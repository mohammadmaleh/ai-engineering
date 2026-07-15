# Architecture Decision Records (ADRs) — Cheat Sheet

> Source of truth: `meddocs/docs/adr/`. This is the recall card — the one sentence per decision.

## What an ADR is (and why)
A record of **one** significant decision: **Context → Decision → Alternatives → Consequences → Revisit-when.**
It exists so the *why* survives, and so a decision is made **once, on purpose**, not re-litigated forever.
**Immutable once accepted** — to change it, write a *new* ADR that supersedes it.

## The interview soundbite for each

- **ADR-001 · Monolith.** Microservices solve an *org / independent-scaling* problem I don't have, and would
  force *distributed transactions* on a workflow that must be atomic. Modular monolith → refactor module
  boundaries cheaply (they're packages, not network contracts). Revisit when one module must scale alone.

- **ADR-002 · Multi-tenancy.** Shared DB, `organization_id NOT NULL` on every tenant row, uniform `WHERE`
  via a base helper, **+ Postgres RLS** as the strong form (DB refuses other tenants even if app forgets).
  uuid PKs so URLs don't leak volume. Rejected DB-per-tenant (ops cost) and app-filter-only (one forgotten
  WHERE = breach).

- **ADR-003 · Auth.** *AuthN* = stateless JWT (server **recomputes** the signature with `SECRET_KEY`, no DB).
  *AuthZ* = RBAC, role on `membership`, **read from the DB per request** → immediate revocation (a token-baked
  role goes stale). Static `ROLE_PERMISSIONS` map, four gates 401→403→404→409. Rejected sessions (stateful)
  and role-in-token (stale).

- **ADR-004 · Feature flags — build.** DB-backed, resolves global→org→user→**% rollout (stable hash)**. Built
  not bought because the real use is trialing a **new AI prompt on a % of orgs, compared in Langfuse**, and
  the scope is too small for LaunchDarkly.

- **ADR-005 · File storage.** Private **object storage** (R2/MinIO, S3 API); DB holds only `storage_key`. API
  runs the gates, **audits the read, then mints a short-lived presigned URL**; browser fetches bytes directly
  but only with an API-authorised capability. Rejected PDFs-in-Postgres, public buckets, long-lived URLs.

## The pattern across all five
Each names **real alternatives** and an **honest downside** — an ADR is not a sales pitch. And each defers
cost with a **"revisit when"** trigger (the senior move: adopt complexity when the need arrives, not before —
same logic as deferring Redis to M6).
