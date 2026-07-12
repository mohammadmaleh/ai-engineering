# ERD & Schema Design — Cheat Sheet

For designing relational schemas (ENG-12+). Database design was my weakest point — this is the muscle.

## ERD notation

- **Entity** = a table (a box). Lists columns; marks **PK** (primary key) and **FK** (foreign key → points at another table).
- **Relationship** = a line between boxes.
- **Cardinality** = the shape of the line: **1:N** (one org → many users) or **N:M** (many-to-many).
- Draw it in Mermaid `erDiagram`. `||--o{` = one-to-(zero-or-)many.

## Multi-tenancy at the schema level

- Every table holding tenant data has an **`organization_id`** column. That column is what isolates org A from org B.
- **Exception: `users`** has no `organization_id` — a user is a **global identity** (one login), tied to orgs via `memberships`.

## Many-to-many → join table (the big one)

- When both sides can have many of the other (users ↔ organizations), you can't put a foreign key on either side.
- Resolve it with a **join table** (junction/link table): `memberships (user_id, organization_id, role)`.
- **Data about the relationship lives on the join table.** Role is about the *link* (this user, in this org), so `role` goes on `memberships`, NOT on `users`.
- Why it matters: one person can be `physician` at Clinic A and `auditor` at Clinic B. Impossible with `role` on `users`.
- **Interview line:** *"users-to-orgs is many-to-many, so it needs a join table; the role is an attribute of the membership, not of the user."*

## Two trails — don't merge them

- `document_events` = **what happened to the document** — one row per state change (`from_status → to_status`). The timeline.
- `audit_log` = **who touched what, everywhere** — one row per sensitive action, **including reads**. Append-only, for the auditor (DSGVO).
- Proof they differ: a physician **reading** a doc changes no state → nothing in `document_events` → but it MUST be in `audit_log`.
- Both written **at event time** ("record it when it happens") — same pattern as keyword-flagging at upload.

## Where indexes go

- Index the columns you **filter or join on a lot**. Examples here:
  - `documents(organization_id, status)` — the work-queue lookup.
  - `audit_log(organization_id, created_at)` — the auditor's time-range filter.
- Rule: an index speeds reads on that column but costs a little on writes. Add them where the hot queries are.

## Constraints belong in the database (not just app code)

- An **ERD shows *shape*** (tables, columns, PK/FK, cardinality). It does **NOT** show `UNIQUE`, `CHECK`, enums, `NOT NULL`, defaults, or indexes — those are written as notes / live in the migration DDL.
- Mermaid can mark a **single-column** unique (`email UK`) but **not a composite** one — `UNIQUE(user_id, organization_id)` has to be a written note.
- **Put invariants in the DB as constraints.** A constraint can *never* be violated; app-level checks get forgotten, bypassed by another code path, or lost in a race. Make correctness *structural*.
- Concrete ones for MedDocs:
  - `UNIQUE(user_id, organization_id)` on `memberships` → one role per user per org (else separation of duties breaks + ambiguous role).
  - `CHECK`/enum on `role`, `status`, `doc_type`, `urgency` → a typo can't become a silent bug.
  - **`timestamptz`, never naive `timestamp`** — timezone-aware, stored UTC.
  - `audit_log` / `document_events` = **append-only** (insert only) → trustworthy trail.
- **Interview line:** *"I enforce business invariants with database constraints — e.g. a unique constraint on (user, org) guarantees one role per user per org no matter what the app code does."*
