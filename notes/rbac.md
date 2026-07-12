# RBAC / Permissions — Cheat Sheet

> Written during ENG-13 (`meddocs/docs/permissions.md`). Read before any auth/permissions work.

---

## 0. THE RULE I KEEP BREAKING (read this first, every time)

> **A comparison has TWO sides. If I cannot name both sides, I do not know the mechanism —
> I only know its title.**

I keep giving one-sided answers. "We check the signature." "The tenancy gate." "Against the key."
An interviewer hears that as *"has read about it, has not understood it."*

**Say both sides, in this exact shape:**

- **JWT:** the server compares **the signature carried in the token** against **a signature it recomputes
  itself** from the incoming `header.payload` using the `SECRET_KEY`.
- **Tenancy:** the server compares **the document's `organization_id`** against **the caller's
  `organization_id`**.

---

## 1. AuthN vs AuthZ

| | Authentication | Authorization |
|---|---|---|
| Question | *Are you who you say you are?* | *What may you do?* |
| Mechanism | JWT signature | permission matrix (RBAC) |
| Output | a trusted `user_id` | allow / deny |
| Failure code | **`401`** — "I don't know who you are" | **`403`** — "I know exactly who you are, and no" |

Being allowed to **log in at all** is still authN. AuthZ only starts **after** we know who you are.

## 2. How the JWT check REALLY works

A token is three base64 chunks: `header.payload.signature`.

```
signature = HMAC_SHA256( base64(header) + "." + base64(payload),  SECRET_KEY )
```

**On every request the server:**
1. takes the **incoming** header + payload,
2. **recomputes** a signature over them with its `SECRET_KEY`,
3. **compares its fresh signature against the token's signature.**
   - match → genuine + untampered ✅
   - mismatch → forged/tampered → reject ❌
4. separately checks the **`exp`** claim (expiry).

**No database. Ever.** The token proves itself — that's what "stateless" means.

- **`SECRET_KEY` is an INGREDIENT, not a side of the comparison.** Flour, not cake. You bake a *second
  cake* with the same flour and compare **cake to cake**.
- **Wax-seal model:** the payload is a letter *anyone can read* (base64 is **encoding, not encryption** —
  never put secrets in a JWT). The signature is a seal stamped with a die only we own. When the letter
  comes back we press a **fresh seal** and compare **impression to impression**. You never hold the
  letter against the stamp.
- Attacker edits `role: physician` → `role: org_admin`: the payload bytes change, so the recomputed
  signature no longer matches the one in the token → **rejected at the signature check**, before the
  role is ever read, without touching the DB. They can't re-sign — they don't have the key.
- The signature gives **integrity** (tamper-proof), **not confidentiality** (not hidden).

## 3. RBAC basics

- **Permissions attach to ROLES, never to individual users.** No per-user grants — that's how RBAC rots.
- **The role lives on the `membership` row**, not on `users`: `memberships(user_id, organization_id, role)`.
  A person can be `physician` in Clinic A and `org_admin` in Clinic B. The role is a property of the
  **link**, not of the person.
- `UNIQUE(user_id, organization_id)` → **one role per user per org.**

**Where does authz get the role from — the token or the DB?** A real design choice:

| | role baked **in the token** | role looked up **in the DB** ← *MedDocs* |
|---|---|---|
| DB hit per request | no | yes (one indexed query) |
| **Revocation** | **stale** — demote someone, their token still says admin until it expires | **immediate** — next request sees it |

MedDocs uses the DB: JWT proves *who* (no DB), then we load the membership to get the **current** role.

## 4. THE FOUR GATES (the whole model in one frame)

| # | Gate | Question | Enforced by | Fails with |
|---|---|---|---|---|
| 1 | **AuthN** | who are you? | JWT signature recompute+compare | `401` |
| 2 | **RBAC** | may your **role** do this action? | permission string vs. matrix | `403` |
| 3 | **Tenancy** | does this **row** belong to your org? | `WHERE organization_id = me` | `404` |
| 4 | **Guard** | is the object in a legal **state**? | workflow preconditions | `409` |

**Passing one gate is not passing another.**

**Gate 3 returns `404`, not `403`** — a `403` would *confirm the document exists* in someone else's
clinic. Leak nothing; pretend it isn't there.

## 5. Permission strings — and why scope is NOT in them

Convention: **`resource:action`** → `document:approve`, `audit_log:read`, `member:manage`.

**There is no `document:approve:own_org`.** The failure it would cause:

> Dr. Schmidt, `physician` at **Clinic A**, legitimately holds `document:approve`.
> He calls approve on document 999, which belongs to **Clinic B**.
> RBAC asks: *does `physician` have `document:approve`?* → **YES** → allowed.
> **He just approved another clinic's patient record. Cross-tenant breach.** 🔥

**Why the string can never save you:**
- `document:approve` is a **static fact about a role** — the same string on every request, forever.
- *"Is document 999 mine?"* is a **dynamic fact about one row** — a different answer every request.
- **A static string cannot answer a question about a specific row.** Someone has to go *look at the row*
  and compare its `organization_id` to mine. That comparison **is** the `WHERE` filter.
- (A string *per org* explodes combinatorially — and you'd still have to look up who owns doc 999 to pick
  the right string. You did the query anyway, with extra steps.)

**Two independent gates, both must pass:** RBAC = *may my role?* · Tenancy = *is this row mine?*

**Make tenancy structural, not disciplinary** — humans forget a `WHERE` clause exactly once:
`organization_id` on every table → a base query helper that always applies it → **Postgres Row-Level
Security (RLS)** is the strong form (the DB refuses other tenants' rows even if the app forgets).

## 6. Permission ≠ Guard

| | Question | Lives in |
|---|---|---|
| **Permission (RBAC)** | may this **role** *ever* do this? | `permissions.md` |
| **Guard (precondition)** | is the **object** in a state where it's legal *now*? | `workflow.md` |

`assistant` **holds** `document:delete` — but it's only legal while
`status='received' AND assignee IS NULL AND no comments`. **RBAC = who. Guards = when.**

## 7. Backend vs frontend

`GET /me` → `{ role, permissions: ["document:approve", ...] }` → the UI hides buttons.
**Same strings on both sides — that's the point of the convention.**

> **The frontend hiding a button is a courtesy. It is NOT a security control.**
> **`curl` exists.** Every hidden button is one HTTP request away. The server re-checks every request
> **as if the frontend does not exist.** The `permissions[]` array is a read-only gift to the UI —
> **never** an input to a decision. A client sending permissions in a body → ignored, recomputed server-side.

## 8. Separation of duties — the design principles

1. **"Admin can do everything" is an ANTI-PATTERN, not a feature.** In a compliance domain the admin
   should have the **least** clinical reach, not the most.
2. **Administrative power ≠ clinical authority.** An `org_admin` is often the office manager, possibly
   with no medical licence. *Approve* asserts "this is medically correct." They cannot say that.
3. **A permission denial must be able to state its reason out loud** — a missing qualification, or a
   conflict of interest. **Deny for a reason, never by habit.** (A physician *can* triage — they're the
   most qualified person in the building. Denying it protects nothing and just creates friction.)
4. **The oversight role writes nothing.** An auditor who can write into the system they audit is not
   independent. They raise concerns **out of band** (report/export), never inside the workflow.
5. **Who audits the admin?** The admin is a *subject* of the audit. So `audit_log:read` is the
   **auditor's alone** — that sole-holder access is the only thing that makes the role meaningful.
6. **Continuity does not require god-mode.** Dead/absent doctor with a stuck document? The admin needs to
   **re-assign** it (administrative), not **approve** it (clinical). *Routing work ≠ judging content.*
7. **Break-glass:** true emergency override is explicit, time-limited, alarmed, reviewed after the fact.
   **Emergency access is an EVENT, not a role.**
8. **Metadata vs content.** The admin can see *that* a document exists (type, urgency, status, assignee)
   so they can re-route it — but **not the patient's diagnosis**. Data minimisation / need-to-know (DSGVO).

## 9. Two trails, two audiences (recurring — I keep conflating these)

| Table | Holds | Audience |
|---|---|---|
| **`document_events`** | state history of **ONE document** (triaged by X, assigned to Y, approved by Z) | **physician** — clinical context ✅ |
| **`audit_log`** | **org-wide, append-only** trail of *everything*, **including reads**, logins, role changes | **auditor** — compliance instrument 🔒 |

A doctor wanting "who touched this document?" wants **`document_events`**, *not* the audit log.

## 10. No hard delete (German healthcare)

- **Aufbewahrungspflicht** — patient records must be retained **~10 years**. Deleting them is **illegal**,
  and this **overrides DSGVO's right-to-erasure** for medical records. *(Great interview nuance.)*
- The trails are **append-only** — a hard delete leaves them pointing at a record that doesn't exist.
- ⇒ **soft delete only**, for one purpose: **correcting a mis-upload**. Reversible, audited, guarded.
- **Storage pressure is NOT a reason to delete.** Capacity = retention policies + cheap archival tiers,
  an automated system process — **not a button a human clicks.**
- **You may not destroy what you are not permitted to look at** (why `org_admin` can't delete: they
  can't read content, so they can't judge which doc is a mistake).

## 11. Interview one-liners

- *"AuthN is who you are; authZ is what you may do. 401 vs 403."*
- *"The server recomputes the signature and compares it to the token's — the secret key is an ingredient,
  not a side of the comparison. No DB."*
- *"RBAC answers **who**; the tenancy filter answers **which rows**; guards answer **when**. Three
  different questions — you need all three."*
- *"Scope never goes in the permission string: a static string can't answer a question about a specific row."*
- *"The frontend check is UX. The backend check is security. curl exists."*
- *"'Admin can do everything' is an anti-pattern — who audits the admin?"*
