# State Machines & Guarded Transitions — Cheat Sheet

> Source of truth for the real design: `meddocs/docs/workflow.md`.
> This is the lookup card. Reading it is not learning — being *tested* on it is.

---

## 0. The one that costs offers: four gates → four codes

Every protected request passes four gates, **in order**. Passing one is not passing another.

| Gate | Fails when… | HTTP |
|---|---|---|
| 1 · **authN** | not logged in / bad JWT | **401** Unauthorized |
| 2 · **RBAC** (permission) | your **role** can't do this action | **403** Forbidden |
| 3 · **tenancy** | the row isn't in **your org** | **404** Not Found |
| 4 · **guard** | the object is in the **wrong state** | **409** Conflict |

- **404 for tenancy, not 403** — a `403` would *confirm the row exists* in another org = cross-tenant leak. To an outsider, it does not exist.
- **409 for a bad state, not 422** — `422` = the *request* is malformed (bad body/types). `POST /documents/999/approve` is a perfectly valid request; the problem is the **state of the target**. That's the textbook meaning of `409 Conflict`.
- Traps: `402` = *Payment Required* (not "forbidden"). `403` = Forbidden.

---

## 1. Permission vs. guard

| | Question | About | Static/dynamic | Gate → code |
|---|---|---|---|---|
| **Permission** (RBAC) | may this **role** *ever* do this action? | the role | **static** fact | gate 2 → **403** |
| **Guard** (precondition) | is this **object** in a legal state *right now*? | the row | **dynamic** fact | gate 4 → **409** |

Both must pass. RBAC answers **who**; the guard answers **when**.

> Example — `approve`: RBAC says "physicians may approve." The guard says "…but only a doc whose `status = in_review`, assigned to *you*." A physician approving a `received` doc → 409.

---

## 2. Why model a workflow as a state machine at all

A document doesn't move through arbitrary states in arbitrary order. Encoding the legal moves turns bugs into impossibilities:
- **Illegal transitions rejected structurally** (409), not by scattered `if`s someone forgets.
- **History is a by-product**: every transition writes one `document_events` row — you don't *remember* to log.
- **Queues + SLA read the state**, so the state must be honest about what's actually happening.

**The rule:** a transition not in the table is illegal → **409**.

---

## 3. MedDocs document lifecycle

States (this is `documents.status`):

```
received → triaged → assigned → in_review → approved  → archived
                                     ↕                 ↘ rejected → archived
                          awaiting_second_opinion
```

What each **asserts**:
- `received` — file exists, nothing trusted yet.
- `triaged` — type + urgency settled (AI classifies; human confirms anything above `routine`).
- `assigned` — a specific physician is responsible. *(on someone's desk)*
- `in_review` — that physician has actually opened it. *(the gap `assigned→in_review` is what the SLA measures)*
- `awaiting_second_opinion` — reviewer is blocked on a colleague's consult.
- `approved` / `rejected` — clinical outcomes. **Terminal-ish** → both go to `archived`.
- `archived` — terminal. Retained, never hard-deleted.

---

## 4. Guards worth remembering

- **The clinical acts are locked to the assignee:** `start_review`, `approve`, `reject` all require `assigned_user_id = caller`. Reason: *approve asserts "I reviewed this"* — a different doctor can't sign for it (separation of duties / liability).
- **Continuity = reassignment, never bypass.** Doctor on vacation? An admin **reassigns** (`assigned_user_id` changes) — the only way that column moves. The new doctor reviews *and* approves. Never let a non-assignee "just review it."
- **`reject` always carries a reason** (written to `document_events.note`) — a reject with no reason is useless for audit.
- **Terminal is terminal.** You never drag a doc backwards — that would rewrite its history into a lie. A redo is a **brand-new document entity** with its own lifecycle (optionally linked via `replaces_document_id`).

---

## 5. Second opinion — why it's its own state

Dr. A wants Dr. B to weigh in *before* committing.
- **Dr. B is a consultant, not the reviewer** — `assigned_user_id` never changes; only Dr. A can `approve`. Dr. B just adds a comment (physicians already have `document:comment`).
- **It's a first-class state, not a boolean inside `in_review`.** Principle: *if a state has a different responsible party or different SLA behaviour, it deserves to be its own state.* Otherwise the SLA can't tell "Dr. A is slow" from "Dr. A is blocked on Dr. B" → it escalates the wrong person.

---

## 6. The actor on an automatic transition — service account

The AI triage has no human behind it, but `document_events` still needs an `actor_user_id`.
- **Service account** — a reserved non-human principal in `users` (`ai_classifier`, `sla_escalator`), well-known UUID, no password. Auto-transitions are attributed to it.
- **Not `null`** — `null` can't tell "the classifier did it" from "a bug left it blank."
- **Not impersonation** — impersonation is *a human acting as another human*; using it here would pin the machine's work on a real person = the accountability lie we avoid. A service account *is itself*.

---

## 7. Two concurrency + integrity notes (foreshadow M3)

- **Two reviewers racing the same transition** → lock the row first: `SELECT … FOR UPDATE` before checking the guard.
- **`document_events` vs `audit_log`** — *this document's* state timeline (read by the physician) vs the *org-wide who-touched-what including reads* (read by the auditor). Two trails, two audiences.
