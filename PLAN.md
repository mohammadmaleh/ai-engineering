# MedDocs — Multi-Tenant Clinical Document Workflow Platform

> **v3 — 2026-07-11.** Completes the v2 draft (same day; the WSL session died before it was finished). What v3 adds: the **team-roles lens** (learn every role on a real web team, one project), a **learning layer per milestone** (concepts + interview questions + definition of done), the **defect audit as a first-class section** with file references, **CI moved from M6 to M2**, a **designer track** (wireframes in M1, design system in M5), a **job-hunt track**, a **calendar**, and a session protocol whose first rule exists because WSL just ate a session: *commit and push every session*.
>
> The domain stays medical. The architecture (tenancy, RBAC, state machines, queues) is domain-independent — swapping domains would reset months of merged code and delete the story (German market, DSGVO) that makes this project distinctive. Decided; not revisiting.

---

## 0. How to use this plan

1. **One milestone at a time.** Milestones are listed in order for a reason. No peeking ahead, no "quick detour."
2. **Commit and push at the end of every session — no exceptions.** Plans, notes, and code survive broken WSL installs only if they're on GitHub. This rule exists because v2 of this plan almost didn't.
3. **Every session follows CLAUDE.md's protocol**: briefing → build → notes after each concept → quiz every 2–3 concepts → recap + update "Last Session."
4. **New ideas go to `LATER.md`**, reviewed only at milestone boundaries. Current candidates: fax/email ingestion simulation, DICOM, billing, patient portal, mobile.
5. **If a milestone doubles in duration, cut scope inside it. Never extend it.**
6. Mohamad writes every line of code. Claude explains, reviews, challenges, and quizzes — and in M5 reviews React like a hostile senior.

---

## 1. The product

**MedDocs** is a multi-tenant clinical document workflow platform for German clinics / hospital departments (Praxen, MVZ, diagnostics or internal-medicine departments).

The story: a department receives dozens of documents daily — Überweisungen, Laborbefunde, Arztbriefe, Entlassungsbriefe. Today that's manual sorting in a shared inbox, and urgent findings get buried. MedDocs:

1. **Ingests** documents (upload; later a simulated fax/email inbox) into an org-scoped pipeline
2. **AI-triages** them: classifies type, extracts urgency signals (critical keywords + LLM structured output), suggests routing
3. Places them in **work queues**; staff pick up or get assigned per role
4. Clinician opens a **document workspace**: PDF viewer + plain-language summary + critical-findings panel + citation-grounded Q&A + annotations
5. Document moves through a **review workflow** (state machine with guards, second-opinion path, SLA timers, escalation)
6. Every access and transition lands in an **append-only audit log** (the DSGVO story)
7. Management sees a **department analytics dashboard** (throughput, SLA breaches, urgency mix, reviewer load)
8. Org admins manage **users, roles, invitations, and feature flags** per tenant

The existing RAG chat, citations, summaries, and keyword flags don't get thrown away — they become the AI pipeline's output, embedded in a workflow instead of floating alone.

### Ideas considered and rejected (keep for interviews — rejecting scope is a senior skill)

| Idea | Verdict | Why |
|---|---|---|
| Full hospital system (HIS/EHR) | ❌ | Epic/Cerner-scale scope: 10 modules at 10% depth. Also one of the most common junior CRUD projects on GitHub — breadth reads as *less* senior. |
| Sickness prediction (ML) | ❌ | That's data science, not AI engineering. Unanswerable interview questions: what dataset, how validated, who takes liability? The legitimate version — rule + LLM **urgency triage** — is in scope and honestly named. |
| Generic "practice everything" app | ❌ | Impressive is never the tech list — it's a specific product in a real market with defended decisions. A domain-less demo is the definition of a shallow portfolio piece. |
| One department's document workflow, deep | ✅ | Every senior concern arises naturally: tenancy, RBAC, state machines, audit trails, flags, async pipelines, real-time. Builds on everything already merged. |

### The honesty paragraph (read once, then build)

This is a **4–6 month build** for one person who is also learning Python. That is fine — *if* every milestone ends deployed and demoable, so the project is on your CV and live from month 1, not month 6. What is not fine: disappearing into a 6-month cave, or restarting when the excitement fades (this plan is already restart #3 — it is the last one). Redis/queues stay deferred to M6: adopting infrastructure before the product needs it is a junior tell; adopting it when the need arrives, with an ADR explaining why, is the senior move.

---

## 2. The team-roles lens — "learn every role on a web team"

This project is structured so you rotate through every hat on a real product team. When a milestone says you're wearing a hat, work *as that role would*: produce their artifacts, use their tools, be judged by their standards.

| Role | Their job here | Where you practice it |
|---|---|---|
| **Product manager** | `PRODUCT.md`: personas, user journeys, scope calls, LATER.md discipline | M1; every milestone boundary |
| **Architect** | Architecture doc, ERD, ADRs, API conventions — and defending them under challenge | M1; new ADRs in M3/M6 |
| **Designer** | Lo-fi wireframes → design tokens → component library in Figma → WCAG AA | M1 (wireframes), M5 (design system) |
| **Backend engineer** | Tenancy, RBAC, auth hardening, state machine, queues, storage | M2, M3 |
| **AI engineer** | Pipeline jobs, structured LLM output, scoped RAG, evals, Langfuse, flag-gated prompt rollout | M4 |
| **Frontend engineer** | Next.js app architecture, real-time UI, workspace, dashboard, i18n, a11y | M5 |
| **DevOps / SRE** | Dockerfile + deploy (M2), CI (M2, expanded M6), compose stack, Redis worker, staging, monitoring | M2, M6 |
| **QA engineer** | Test pyramid: unit → API → e2e; the tenancy-isolation test written *first* | M2 onward; Playwright + load test in M6 |
| **Security engineer** | OWASP pass, rate limiting, headers, secrets audit, prompt-injection defense | M6 (+ M4 for AI boundary) |
| **Tech writer** | README, architecture case study, docs that another dev could onboard from | M1, M7 |

**The rule that makes this real:** each role's artifact gets reviewed as if by that role's lead. Your ERD gets challenged like a staff engineer would; your wireframes get critiqued like a design lead would; your PR descriptions like a hostile reviewer would.

---

## 3. System design (first-class phase, not a vibe)

All of this gets written down in `meddocs/docs/` **before** the code — these documents are themselves interview artifacts:

- `docs/architecture.md` — context + container diagram (C4-ish), request/data flow
- `docs/erd.md` — full entity-relationship diagram
- `docs/permissions.md` — the role × permission matrix
- `docs/workflow.md` — document lifecycle state machine diagram
- `docs/api-conventions.md` — versioning (`/api/v1`), pagination, error shape, naming
- `docs/adr/ADR-001..N.md` — Architecture Decision Records, one page each
- `PRODUCT.md` — personas, journeys, product pitch (the PM artifact)

### Architecture

**Deliberate monolith** (ADR-001): one FastAPI app + (from M6) one worker process, one Postgres. Modular internally (`app/modules/{auth,orgs,documents,workflow,ai,flags,audit,notifications,analytics}`). Microservices rejected in writing — arguing *why not* is more senior than having them.

```
Next.js (Vercel) ── REST /api/v1 + WebSocket ──> FastAPI (Render, Docker)
                                                   ├── Postgres (Neon): all state
                                                   ├── Object storage (R2/MinIO): original PDFs
                                                   ├── Pinecone: embeddings
                                                   ├── Groq/OpenAI: LLM + embeddings
                                                   ├── Worker (M6: + Redis queue): AI pipeline, SLA checks
                                                   └── Langfuse + Sentry: observability
```

### Data model (target ERD, evolves via Alembic)

- `organizations` — the tenant. Every domain table carries `org_id`; isolation enforced in the query layer **and proven by tests** (ADR-002: tenant_id columns vs Postgres RLS — decide and document)
- `users`, `memberships` (user↔org, holds `role`), `invitations` (token, expiry, role)
- `patients` — **pseudonymized fake records** (case number, no real PII) so documents group into patient files and lab values trend over time
- `documents` — org_id, patient_id?, storage_key (PDF in object storage — today the PDF isn't even stored, only extracted text!), type, urgency, workflow `status`, flags
- `document_events` — append-only workflow/audit history: who, what transition, when, why
- `assignments`, `comments` (annotation thread per document)
- `chat_sessions`, `chat_messages` (existing; gains org/document scoping)
- `lab_values` — structured extraction target: name, value, unit, reference range, abnormal
- `feature_flags`, `flag_overrides` (global / per-org / per-user / percentage)
- `notifications` — in-app inbox
- `audit_log` — append-only access log for medical-data reads (distinct from workflow events)

### Roles & permissions (RBAC — ADR-003)

Four roles per membership: `org_admin`, `physician`, `assistant` (MFA/nurse), `auditor`. Permissions are the unit of enforcement; roles are bundles of them:

| Permission (sample) | admin | physician | assistant | auditor |
|---|---|---|---|---|
| document.upload | ✅ | ✅ | ✅ | — |
| document.review / .sign | — | ✅ | — | — |
| document.assign | ✅ | ✅ | ✅ | — |
| chat.use | ✅ | ✅ | ✅ | — |
| audit.view | — | — | — | ✅ |
| members.manage / flags.manage | ✅ | — | — | — |

Backend: `require_permission("document.sign")` as a FastAPI dependency. Frontend: permission-aware routing and component gating. Full matrix lives in `docs/permissions.md`.

### Workflow state machine

```
RECEIVED → PROCESSING → TRIAGED → ASSIGNED → IN_REVIEW → APPROVED → ARCHIVED
              ↓                                  ↓    ↘ REJECTED ↗
            FAILED                    NEEDS_SECOND_OPINION → IN_REVIEW
```

- Transitions have **guards** (required permission + valid source state); illegal transitions are 409s, not silent overwrites
- Every transition writes a `document_events` row (actor, from, to, reason)
- **Concurrency handled explicitly**: two assistants grabbing the same queue item → `SELECT … FOR UPDATE SKIP LOCKED` (this one line of SQL is a senior interview in itself)
- SLA: urgent documents get a review deadline; a periodic job escalates breaches (notification + dashboard)

### Feature flags (ADR-004: build vs Unleash/Flagsmith — we build a small one, for learning)

DB-backed service: `evaluate(flag, org, user)` with global default → org override → user override → percentage rollout (stable hash of user id). Admin UI to toggle. Real uses from day one: `ai_triage`, `ai_summaries`, `chat_assistant`, `lab_trends`, and — the genuinely senior use — **gating a new AI prompt/model version to 10% of orgs and comparing in Langfuse before full rollout**. Flags tie the platform story to the AI story.

### AI pipeline v2 (each step = a background job with status + retries + idempotency)

```
PDF stored → extract per-page text → classify (type + urgency, LLM structured output, Pydantic-validated)
→ summarize (plain-language German) → flag keywords/values → chunk PER PAGE → embed → Pinecone
```

- Structured outputs validated with Pydantic = the tool-call-hallucination defense, in production shape
- Prompt-injection defense at the *document content* boundary (uploaded text is untrusted input)
- Langfuse tracing per step; eval suite per step (classification accuracy, retrieval hit-rate, faithfulness) against the fixture set
- RAG Q&A scoped: this document / this patient file / whole org — Pinecone metadata filters

---

## 4. The v1 defect audit (fix in M2 — source of truth, verified against code 2026-07-11)

The current backend is ~565 lines and works as a demo, but has real defects. Fixing them *is* the M2 curriculum — each one teaches a production concept.

| # | Defect | Where | What it teaches |
|---|---|---|---|
| D1 | **Citation page numbers are fake** — computed arithmetically (`i * (CHUNK_SIZE-OVERLAP) // 1000 + 1`) while `extract_text_from_pdf` extracts real page numbers that are then thrown away | `document_processor.py:50` vs `:20-25` | Chunk-per-page design; metadata integrity; why citations must be *grounded* |
| D2 | **No chat history sent to LLM** — every request sends only system prompt + current message; multi-turn is an illusion | `chat_service.py:46-58` | LLMs are stateless; history windows; truncation strategy |
| D3 | **Broken SSE framing** — raw text deltas yielded bare, then one `data: {json}\n\n` event; client can't parse a mixed protocol | `chat_service.py:82-84` | The SSE spec; designing a typed event protocol (`token`, `sources`, `done`, `error`) |
| D4 | **No CORS** — frontend will fail on first fetch | `main.py` | CORS, preflight, why the browser (not the server) enforces it |
| D5 | **No doc-scoped chat** — Pinecone query filters only by `user_id`; "chat with this document" retrieves from all documents | `chat_service.py:31-36` | Metadata filter design; scoping as a security concern |
| D6 | **Blocking upload** — extract/embed/upsert runs inline in the request; also the sync Groq stream blocks the event loop inside an async generator | `documents.py`, `chat_service.py:71-82` | Sync vs async in FastAPI; background work; request lifecycle |
| D7 | **Summary feature missing entirely** | — | Reading your own product spec |
| D8 | **Delete leaves orphan vectors** — DB row deleted, Pinecone vectors stay | `documents.py` | Lifecycle consistency across two datastores |

---

## 5. What "learn the whole of web development" maps to

| Area | Where |
|---|---|
| System design, ERD, ADRs, API design | M1 |
| Product thinking: personas, journeys, scope | M1, M7 |
| UX: wireframes, design systems, tokens, WCAG | M1, M5 |
| AuthN hardening: refresh tokens, invitations, email flows | M2 |
| Multi-tenancy, authorization models, object storage | M2 |
| Docker (Dockerfile), first deploy, DNS/TLS basics, env/secrets | M2 |
| CI: lint + typecheck + tests on every PR | M2 (minimal) → M6 (matrix + e2e) |
| SQL depth: transactions, indexes, EXPLAIN, N+1 | M2, M3 |
| Row locking, state machines, race conditions | M3 |
| WebSockets / real-time, notification patterns | M3 |
| Async pipelines, retries, idempotency, structured LLM output | M4 |
| Evals, LLM observability (Langfuse) | M4 |
| Frontend at scale: React Query, forms + zod, tables, i18n, a11y | M5 |
| Next.js rendering strategies: RSC vs SSR vs CSR, caching | M5 |
| Postgres full-text search vs vector search | M5 |
| Queues/Redis, compose stacks, e2e, security, monitoring | M6 |
| Load testing, backup/restore, health checks, staging | M6 |
| Technical writing: README, case study | M7 |

---

## 6. Milestones

Every milestone block has: **hats** (which team roles), **build**, **learn** (concepts you must be able to explain out loud when the milestone ends — this is the interview currency), **definition of done**. Every milestone from M2 on **ends deployed** (Vercel + Render + Neon; ~free, ~$7/mo Render once it matters).

### M0 — Re-entry (2–3 days)

**Hats:** yourself, back at work after a long break — which is a skill.

**Build:**
- Backend runs locally: venv, `.env`, `alembic upgrade head`, `/docs` smoke test, one full manual pass (register → login → upload a 1-page fixture → chat with it)
- Commit the uncommitted April doc changes + this plan; push everything

**Learn (rust-check — explain out loud, no notes):**
- The RAG pipeline end-to-end; the JWT flow end-to-end
- April shaky list: why keyword flagging runs at upload time; `enumerate()` order; `+=` vs `append` on lists; why `# type: ignore` is sometimes needed with untyped third-party libs

**Done when:** the backend answers a chat question locally; `git status` is clean; both flows explained without notes.

### M1 — System design package (1 week)

**Hats:** architect · product manager · designer (first pass) · tech writer.

**Build:**
- Every doc in §3: `architecture.md`, `erd.md`, `permissions.md`, `workflow.md`, `api-conventions.md`, ADR-001–005 (monolith, tenancy, authz, flags, storage)
- `PRODUCT.md`: personas (MFA doing triage, physician reviewing, org admin, auditor), the 3 core user journeys
- **Designer pass:** lo-fi wireframes in Figma/FigJam for the two core screens — inbox/queues and document workspace. Boxes and flows, not pixels. Claude challenges them from each persona's seat.
- Claude challenges every ADR; you defend it — that's the training

**Learn:** C4 diagrams; ERD notation; what an ADR is and why teams write them; REST API conventions (versioning, pagination, consistent error shape); drawing a state machine before coding it.

**Done when:** `meddocs/docs/` + `PRODUCT.md` + wireframes merged via PR, every ADR survived a challenge round.

### M2 — Foundation (3 weeks) — *the platform floor*

**Hats:** backend engineer · DevOps (first CI, first deploy) · QA (first real tests).

**Build:**
- **Fix D1–D8** (§4) — each fix gets a PR with a description that names the defect and the concept
- `organizations` + `memberships` + tenancy enforcement — and the test proving org A cannot read org B's documents **written first**
- RBAC: `require_permission` dependency, role seeds, matrix implemented
- Auth hardening: refresh-token rotation, invitation flow, password reset (Mailhog for dev SMTP)
- Object storage for original PDFs (MinIO locally, R2 in prod), presigned URLs
- `/api/v1` versioning, consistent error shape, pagination
- Fixtures: fake German medical PDFs (Arztbrief, Laborbefunde ×3 over time, Entlassungsbrief) + faker-based seeder (1 org, 4 role users, docs in every state)
- **CI now, not M6:** GitHub Actions running ruff + black + mypy + pytest on every PR; branch protection on `main`. Senior teams have CI from the first deploy.
- **Deploy the walking skeleton:** Dockerfile for the API, live on Render + Neon (login, upload, list — through the real stack)

**Learn:** sync vs async in FastAPI (D6 makes it concrete); SSE as a protocol (D3); CORS (D4); transactions and when to commit; database indexes + reading `EXPLAIN`; the N+1 problem in SQLAlchemy; pytest fixtures + dependency overrides + test DB; what a Dockerfile actually does; what happens at first deploy (DNS, TLS, env vars, secrets).

**Done when:** deployed skeleton is live with CI green; the tenancy-isolation test exists and passes; all 8 defects closed with PRs.

**→ Job-hunt track starts here (~mid-Aug):** CV updated with the live URL, applications begin at a fixed weekly quota (set the number together at the M2 boundary — then it's non-negotiable). Interview prep from this point uses the project itself: every "learn" list below doubles as interview material.

### M3 — Workflow engine (3–4 weeks) — *the heart*

**Hats:** backend engineer (deep end) · QA.

**Build:**
- State machine with guarded transitions + `document_events` history; illegal transition = 409
- Work queues: unassigned pool per type/urgency, claim with `FOR UPDATE SKIP LOCKED`, manual assignment
- Comments/annotations per document
- Append-only `audit_log` on medical-data reads + auditor-role viewer endpoint
- SLA deadlines + periodic escalation job + `notifications` table
- WebSocket: live inbox/queue updates, urgent-document alerts (authenticate the socket!)
- Second-opinion path (request → second physician → resolve)
- Tests for every guard and every race you can construct

**Learn:** row locking and `FOR UPDATE SKIP LOCKED`; transaction isolation levels (at working depth); race conditions and how to *demonstrate* one in a test; idempotency; WebSocket auth and lifecycle; periodic jobs without a queue (and their limits — foreshadows the M6 ADR).

**Done when:** two concurrent claim requests provably can't grab the same document (there's a test); full workflow walkable via `/docs`; deployed.

### M4 — AI pipeline v2 (3 weeks)

**Hats:** AI engineer.

**Build:**
- Pipeline as background jobs (FastAPI `BackgroundTasks` for now): classify → summarize → flag → embed, per-step status, retries, `FAILED` surfaced
- LLM classification (type + urgency) via structured output, Pydantic-validated (the tool-call-hallucination defense, in production shape)
- Lab-value extraction into `lab_values` (the agent-loop learning goal, landed for real)
- RAG Q&A with **real** page citations (D1's fix matured), scoped to document / patient file / org via Pinecone metadata filters
- Prompt-injection defense at the document-content boundary (uploaded text is untrusted input)
- Langfuse tracing end-to-end; eval scripts per step (classification accuracy, retrieval hit-rate, faithfulness) with results committed
- Feature-flag service + admin endpoints; new prompt version rolled out behind a percentage flag and compared in Langfuse

**Learn:** structured output patterns; retries + idempotency for jobs; how to design an eval and what "good" looks like; prompt injection and layered defenses; what you monitor in production LLM apps; chunking tradeoffs (revisited with per-page chunks).

**Done when:** upload → fully processed document with classification, summary, flags, real citations; evals run green in CI against fixtures (LLM calls mocked in unit tests, real evals as a separate script); deployed.

### M5 — Frontend platform (5–6 weeks) — *your strength; the showcase*

**Hats:** designer (for real, first week) · frontend engineer (the rest).

**Build — design week first:**
- Design system in Figma: tokens (color/type/spacing), core components, the two key screens at real fidelity — *then* code it. Claude supports directly in Figma and critiques like a design lead.
- WCAG AA as a requirement, not a wish; loading/empty/error states specified for every view

**Build — the app:**
- Auth screens + invitation acceptance + org switcher
- **Inbox/queues:** filterable, sortable, real-time updating work queues (TanStack Table + React Query + WebSocket)
- **Document workspace:** split view — PDF viewer (react-pdf) | summary, critical findings, lab values; citation click → page jump + highlight; annotations; workflow action bar driven by permissions + current state; streaming Q&A panel
- **Admin area:** members & roles, invitations, feature-flag toggles
- **Analytics dashboard:** ECharts (throughput, SLA breaches, urgency mix, reviewer load)
- **Lab trends:** values over time per patient with reference bands (your FleetPulse ECharts pattern)
- i18n de/en (next-intl) — the German-market signal
- Forms with react-hook-form + zod mirroring backend Pydantic schemas
- Postgres full-text search (tsvector) with UI — plus the "FTS vs vector search: when each" ADR
- Landing page: product pitch + DSGVO section

**Learn:** Next.js rendering strategies (RSC vs SSR vs CSR — when and why); React Query cache design + optimistic updates; integrating WebSockets with client state; form architecture with shared validation contracts; a11y auditing; i18n mechanics; design tokens as an engineering artifact.

**Done when:** a stranger with demo credentials can complete the full journey — log in, triage, review, approve, ask the document a question — on the live URL, in German or English.

### M6 — Production hardening (3 weeks)

**Hats:** DevOps/SRE · security engineer · QA lead.

**Build:**
- Graduate the pipeline to a real worker + Redis queue (arq or Celery) — **with the ADR saying why now** (BackgroundTasks' limits, observed)
- Docker compose local stack: api, worker, postgres, redis, minio, mailhog — this stack IS the "I can run real infrastructure" proof
- CI grows into the full matrix: backend lint/type/test + frontend lint/typecheck/build + Playwright e2e (login → upload → triage → review → approve); deploy on merge
- Test pyramid complete: unit (chunking, state-machine guards, flag evaluation) · API (tenancy isolation, permission denials, transitions) · e2e
- Security pass: rate limiting, security headers, OWASP top-10 walkthrough against your own app, secrets audit
- Sentry + structured logging + health checks; staging environment
- **Ops drills:** a basic load test (k6/locust) against staging with findings written up; a backup/restore drill (pg_dump → restore → verify)
- DSGVO features: audit export, per-patient data export, deletion job (right to erasure — including the Pinecone vectors, D8's lesson at scale)

**Learn:** why a queue (at-least-once delivery, acking, retries — vs BackgroundTasks); compose networking; what each OWASP item means *in your own code*; rate-limiting strategies; what to log and what never to log (medical data!); reading a load-test result.

**Done when:** `docker compose up` gives a full local stack; CI matrix green including e2e; staging + production both live; drills documented in `docs/ops.md`.

### M7 — Ship (1 week)

**Hats:** tech writer · product manager.

**Build:**
- README: architecture diagrams, screenshots/GIF, live demo credentials, eval results table, Langfuse screenshot
- Written case study: *"Designing a multi-tenant clinical document workflow platform"* — the decisions, the rejected alternatives, the drills. This document is interview gold.
- CV + LinkedIn updated; demo video (2–3 min) recorded

**Done when:** you can hand one URL to a hiring manager and one to an interviewer, and both tell the whole story.

---

## 7. Calendar (targets, not fantasies)

| Milestone | Target window | Ends with |
|---|---|---|
| M0 Re-entry | Jul 11 – Jul 14 | Backend running, repo clean |
| M1 System design | Jul 14 – Jul 21 | docs/ merged |
| M2 Foundation | Jul 21 – Aug 11 | **Live skeleton + CI · applications begin** |
| M3 Workflow engine | Aug 11 – Sep 8 | Workflow live |
| M4 AI pipeline v2 | Sep 8 – Sep 29 | Pipeline + evals live |
| M5 Frontend | Sep 29 – Nov 10 | Full product live |
| M6 Hardening | Nov 10 – Dec 1 | Compose stack, e2e, staging |
| M7 Ship | Dec 1 – Dec 8 | Case study + CV |

Slippage rule (worth repeating): cut scope *inside* the milestone; never move the right-hand column.

---

## 8. Working agreement & standing rules

1. **Ticket discipline:** `ENG-XX` branches, PRs with meaningful descriptions, meaningful commits — the git history is part of the portfolio.
2. **Mohamad writes every line of code.** Claude explains, reviews, challenges, quizzes per CLAUDE.md cadence — and only writes code when explicitly asked.
3. **Commit + push every session.** (See §0. WSL has no mercy.)
4. **Notes per topic** (`notes/`) after every concept block. New files as the plan demands: `notes/system-design.md`, `notes/tenancy-rbac.md`, `notes/websockets.md`, `notes/docker.md`, `notes/testing.md`.
5. **Cost rules hold:** Groq for chat, `text-embedding-3-small` for embeddings, short fixture docs, no API calls in test loops (mock all LLM/vector calls in pytest).
6. **Fake data only, forever** — pseudonymized fixtures; DSGVO is a *designed-for* concern, documented, never tested with real data.
7. **Deployed at every milestone from M2.** A senior project that only runs on localhost is a contradiction.
8. **Scope control:** new ideas → `LATER.md`, reviewed at milestone boundaries only.

## 9. What we deliberately skip (and can defend skipping)

- **LangChain / LlamaIndex** — hides the fundamentals this plan exists to teach
- **Fine-tuning** — GPU budget, low job-hunt ROI
- **Microservices** — ADR-001 argues the monolith; that argument is the asset
- **Kubernetes / IaC** — not expected at mid-level; Render + compose tell the story
- **GraphQL** — REST done properly beats both done shallowly
- **ML model training** — urgency triage stays rule+LLM based and honestly named
- **Redis before M6** — deferred ≠ skipped; the ADR marks the moment it becomes justified
