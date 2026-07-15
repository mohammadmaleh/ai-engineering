# REST / API Conventions — Cheat Sheet

> Source of truth: `meddocs/docs/api-conventions.md`. This is the lookup card.

---

## 1. One error envelope — for the WHOLE API

```json
{ "error": { "code": "illegal_transition", "message": "human text", "details": { } } }
```

- **One shape everywhere** → the client writes error handling **once**.
- **status vs code** (the interview line): the **HTTP status** is the *coarse category* (drives caching/retries/tooling); the **`code`** is the *specific reason*. Many codes share one status — `409` covers `illegal_transition`, `email_taken`, `version_conflict`. **Client branches on `code`, never parses `message`** (message is prose; gets reworded/translated).
- `details` = structured extras (which field failed, allowed_from, …).

### Status codes (map to the four gates)
| Status | When | Gate |
|---|---|---|
| 400 | malformed request schema can't catch | — |
| 401 | not authenticated (bad/expired/forged JWT) | 1 authN |
| 403 | role not allowed | 2 RBAC |
| 404 | doesn't exist **or not in your org** | 3 tenancy |
| 409 | valid request, **wrong state** | 4 guard |
| 422 | valid JSON, **fails validation** (Pydantic) | schema |
| 500 | our bug — never leak internals | — |

- 404 not 403 for cross-tenant → 403 would confirm the row exists elsewhere = leak.
- 409 vs 422 → 422 is about the *request*; 409 is about the *resource's state*.

---

## 2. Pagination

- List endpoints **never** return a bare array — always an envelope:
```json
{ "data": [ … ], "pagination": { "limit": 20, "offset": 0, "total": 137 } }
```
- **offset/limit now** — simple, maps to SQL `LIMIT/OFFSET`, jump-to-page. Defaults limit=20, max 100.
- **Trade-off:** offset **drifts** when rows are inserted between pages (see a row twice / skip one). The fix for the real-time queue is **cursor/keyset** (`?after=<cursor>`) — stable under writes, but no random page access. Deferred to M3 (additive, non-breaking).

---

## 3. Naming & paths

- **Plural nouns:** `/documents`, `/patients`. Specific: `/documents/{id}`.
- **Shallow nesting (≤2):** `/documents/{id}/comments`; deeper → link by id.
- **Tenancy is NEVER in the path** — org comes from the JWT (can't be spoofed in the URL).
- **Transitions = action endpoints:** `POST /documents/{id}/approve`, **not** `PATCH {status}`. A transition is a *guarded operation* (carries the guard, writes `document_events`, returns 409), not a field write.
- **Filter** = `?status=in_review`. **Sort** = `?sort=-created_at` (`-` = desc).
- Method IS the verb — no `/getDocuments`. (Action endpoints are the documented exception.)

---

## 4. Versioning

- **`/api/v1` in the URL** (visible in logs/curl/browser; beats a header for a product API).
- **Additive = safe** (new endpoint, new optional field, new response field — clients ignore unknown fields). No version bump.
- **Breaking** (remove/rename field, change type, optional→required) → stand up **`/api/v2` alongside v1**, deprecation window, sunset date. Never rewrite v1 in place.

---

## 5. Misc rules

- Timestamps ISO-8601 UTC; IDs are UUID; auth = `Authorization: Bearer <jwt>`.
- 201 + `Location` on create; 204 on delete; PATCH = partial (no PUT).
- Never leak internals on 500 (log server-side, generic body).
