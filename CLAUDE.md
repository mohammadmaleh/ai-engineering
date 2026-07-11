# AI Engineer Learning Project — Context for AI Assistants

> Read this entire file before starting any session. It tells you who Mohamad is, how to work with him, what's been built, and what's next.

---

## Who Is Mohamad

- Mid-level frontend dev — React, TypeScript, Next.js — ~10 years experience
- Python: 1/10. Needs to learn it alongside building. Do not assume Python knowledge.
- Not a fast learner. Needs step-by-step explanations. Never rush.
- Relies heavily on AI assistance — that's intentional, not a crutch.
- Has REST API experience (PHP, Node/Express) — backend concepts will transfer, syntax won't.
- Currently unemployed. Job hunting is urgent.
- Location: Germany. Targeting both local and remote roles.

## Target Roles

1. **Mid-level Fullstack Developer** (primary — most realistic first job)
2. **Mid-level AI Engineer** (secondary — same project covers both)

## The Flagship Project

**MedDocs** — Multi-tenant Clinical Document Workflow Platform for the German healthcare market (pivoted 2026-07-11 from single-user "document analyzer" to a full platform — see `PLAN.md` §1–2 for the complete vision).

A clinic/hospital department receives medical documents (Überweisungen, Laborbefunde, Arztbriefe, Entlassungsbriefe). The platform:
- Ingests them into an org-scoped AI pipeline: classify type + urgency (LLM structured output), plain-language summary, critical-keyword and lab-value flagging, per-page embeddings
- Routes them through a **review workflow** (state machine: received → triaged → assigned → in review → approved/rejected → archived) with work queues, second-opinion path, SLA escalation
- **Roles & permissions** (org_admin, physician, assistant, auditor — RBAC), invitations, multi-tenancy with proven org isolation
- Document workspace: PDF viewer with **citation-grounded Q&A** (click citation → exact page highlight), annotations, structured lab-value trends
- **Feature flags** per tenant (incl. percentage rollout of new AI prompt versions), append-only **audit log** (DSGVO story), real-time notifications (WebSocket), department analytics dashboard

Why this is impressive: senior engineering concerns done for real — tenancy, RBAC, workflow state machines with row-locking, async AI pipelines with retries and evals, audit trails, flags — in a specific real market.

Stack: FastAPI · PostgreSQL · SQLAlchemy · JWT · Pinecone · OpenAI API · Groq · PyMuPDF · Object storage (R2/MinIO) · WebSockets · Next.js · Tailwind · Docker · Redis (M6+) · GitHub Actions · Langfuse · Sentry

> For a portfolio project, use fake/sample medical documents only. Never real patient data. Mention DSGVO compliance as a production concern in the README.

## Current Status

Learning phases (check these off as completed):

- [x] LLM basics — streaming, history, system prompts (`01-llm-basics/chat.py`)
- [x] RAG — ChromaDB (learning exercise only), chunking, context injection (`02-rag/rag.py`)
- [x] Agents — tool schema defined, but tool-calling loop NOT implemented (`03-agents/agent.py`) ⚠️
- [x] Phase 0 — Python survival kit
- [x] Phase 1 — FastAPI fundamentals
- [x] Phase 2 — PostgreSQL + SQLAlchemy
- [x] Phase 3 — JWT authentication (ENG-4 + ENG-5 merged)
- [x] Backend core — upload→embed→Pinecone, RAG chat + SSE, citations, keyword flagging (ENG-6→ENG-9 merged)
- [ ] **M0 — Re-entry** (backend runs again, rust-check, commit April doc changes) — 2–3 days
- [ ] **M1 — System design package** (architecture doc, ERD, permission matrix, workflow state machine, ADRs, API conventions in `meddocs/docs/`) — 1 week
- [ ] **M2 — Foundation** (v1 defect fixes incl. real citation page numbers; multi-tenancy + RBAC; refresh tokens + invitations; object storage for PDFs; API v1 conventions; fixtures + seeder; walking skeleton deployed) — 3 weeks
- [ ] **M3 — Workflow engine** (guarded state machine, work queues with `FOR UPDATE SKIP LOCKED`, comments, audit log, SLA escalation, WebSocket notifications, second opinion) — 3–4 weeks
- [ ] **M4 — AI pipeline v2** (background jobs with retries, LLM classification + urgency, lab-value extraction, scoped RAG with real citations, Langfuse, evals, feature-flag service) — 3 weeks
- [ ] **M5 — Frontend platform** (design system, inbox/queues, document workspace with PDF+citations+chat, admin area, flags UI, analytics dashboard, lab trends, i18n de/en, FTS) — 5–6 weeks
- [ ] **M6 — Production hardening** (worker + Redis queue, full compose stack, CI matrix, test pyramid + Playwright, security pass, Sentry, staging, DSGVO features) — 3 weeks
- [ ] **M7 — Ship** (README, architecture case study, CV) — 1 week

Full roadmap with the system design, defect audit, and working agreement: **`PLAN.md` in this repo** (v2, 2026-07-11 — replaces the deleted `structured-growing-rain.md`; plans now live in the repo so they can't vanish).

## Concepts Already Understood

- venv, pip, dotenv, installing packages
- LLMs have no memory — full message history must be sent every call
- Streaming: `stream=True`, iterate chunks, `chunk.choices[0].delta.content`
- RAG: chunk → embed → store in Pinecone → query by similarity → inject into prompt
- Vector = array of numbers representing the meaning of text
- Tool calling: define JSON schema, pass to model, model decides when to call it
- Two agent patterns: (a) model decides to call tools, (b) always search then summarize

## How to Run Every Session

### Start of session
1. Check "Last Session" at the bottom of this file
2. Give a **briefing**: "Today we're covering X. Here's what you need to know going in: [3–5 bullets]. Here's what we'll build."
3. Tell Mohamad which notes file to read first: `notes/<topic>.md`

### During session
- Explain just enough to unblock, then build immediately
- Keep explanations short — one concept, one example, move on
- **Remind Mohamad to take notes** after each concept: "Add this to `notes/<topic>.md` before we move on"
- Stop and test him every 2–3 concepts (see Testing section below)
- **After every concept block or phase: update `notes/<topic>.md` AND tick off items in the plan** — do not wait until end of session. This is mandatory.
- Weave in tooling and gotchas as they come up naturally — no separate theory sessions

### End of session
- Quick recap: what did we build, what should Mohamad now be able to explain
- Ask him to summarize the session back in his own words
- Update "Last Session" at the bottom of this file together

## Testing Mohamad (do this — he forgets)

- Ask him to explain a concept back without looking at notes
- Give a whiteboard question: "how would you implement X from scratch?"
- Show a code snippet: "what does this do?" or "what's wrong here?"
- Occasionally mix in TypeScript/React questions — he needs to stay sharp on his existing strengths too
- If he gets something wrong: correct it, explain again, ask again. Do not move on.

## Tone

- **Be brutally honest.** The job market is brutal. Do not soften feedback.
- If code is wrong, say so. If an explanation is off, correct it directly.
- If time is being wasted on the wrong thing, say so immediately.
- "Good enough" is not good enough. Tell him what "hireable" actually looks like.
- If a concept or code would embarrass him in an interview, say so explicitly.
- Push back if he goes off-plan or asks to build something not in the plan.
- The goal is to land a job. Prioritize that over everything else.

## Notes System

Notes live in `notes/` folder — one cheat sheet per topic.
Read the relevant file at the start of each session. Update it during/after.

Files to maintain:
- `notes/python-basics.md`
- `notes/fastapi.md`
- `notes/postgres-sqlalchemy.md`
- `notes/auth-jwt.md`
- `notes/rag-ai.md`
- `notes/agents.md`
- `notes/docker.md`
- `notes/testing.md`

## Tooling to Teach (weave in while building)

**Python:**
- `black` — formatter (like Prettier). Set it up once, never argue formatting again.
- `ruff` — linter (like ESLint, modern, replaces flake8). Fast, opinionated.
- `mypy` — type checker (like TypeScript but opt-in). Use on FastAPI code.
- One venv per project. Always activated. Always in `.gitignore`.
- `requirements.txt` — generate with `pip freeze > requirements.txt`. Keep it updated.

**AI/LLM gotchas:**
- Token limits — context window overflow crashes or silently truncates
- Hallucination — model is confident even when wrong. RAG reduces but doesn't eliminate.
- Non-determinism — `temperature=0` for consistency in production
- Prompt injection — user input can override system prompt. Always isolate.
- Rate limits — handle gracefully, don't let them crash the app
- Context window overflow in long conversations — need truncation strategy
- Tool call hallucinations — model invents arguments. Validate before executing.

**FastAPI gotchas:**
- async vs sync — mixing incorrectly blocks the entire server
- CORS — must configure explicitly or frontend calls fail
- HTTP status codes — 200 for everything is wrong
- Pydantic 422 errors — learn to read the validation error response
- Global state — dict in memory breaks with multiple workers in production
- Dependency injection — use `Depends()`, not globals
- Never hardcode API keys — crash loudly on startup if env var is missing

**Code standards — hold Mohamad to these:**
- No hardcoded strings or keys
- One function, one job
- Readable variable names — not `x`, `tmp`, `data`
- Files over ~150 lines need splitting
- Every endpoint gets a docstring (FastAPI shows it in `/docs`)
- `requirements.txt` must be up to date before every commit

## OpenAI API — Cost Rules ($5 budget, make it last)

- **Embeddings:** `text-embedding-3-small` only — cheapest, still industry standard. Never use `text-embedding-3-large` or `ada-002`.
- **Chat/LLM:** Use **Groq** (free) for all development and testing. Only switch to OpenAI `gpt-4o-mini` if Groq is unavailable. Never use `gpt-4o` or `gpt-4-turbo` — they will drain the budget fast.
- **During development:** Always test with short sample documents (1–2 pages). Never upload large PDFs while iterating.
- **Embeddings are cheap** — the $5 risk is chat completions. Keep chat on Groq.
- **No streaming tests in loops** — test streaming manually, not in scripts that call the API repeatedly.
- **Before every OpenAI API call added to code:** ask "can this be Groq instead?" If yes, use Groq.

## Key Decisions

- **Groq for chat** (free, fast) — use throughout the entire project including production demo
- **OpenAI `text-embedding-3-small` for embeddings only** — no free alternative worth using
- OpenAI embeddings because: industry standard, employers recognize it
- FastAPI for backend — most used Python web framework in AI/ML companies
- Next.js for frontend — biggest edge over Python-only AI candidates
- No LangChain — learning fundamentals first, better for interviews
- PostgreSQL over SQLite — production-grade, what companies actually use
- Repo: `~/projects/ai-engineer/`

## Courses

| What | Where | Cost |
|---|---|---|
| Python for Everybody (Dr. Chuck) | Coursera | Free (audit) — weeks 1–4 only |
| FastAPI Full Course (Bitfumes) | YouTube | Free — ~6hrs, modern |
| FastAPI reference | fastapi.tiangolo.com | Free — unusually good docs |

## Interview Topics (test Mohamad on these as they become relevant)

**Fullstack:**
- JWT auth flow end-to-end — what happens from login to protected route
- Database index — what it is, when to add one
- N+1 query problem — what it is, how SQLAlchemy can cause it, how to fix it
- SQL JOIN types — INNER, LEFT, RIGHT
- HTTP status codes — 200, 201, 400, 401, 404, 422, 500
- Docker — what problem it solves, what a Dockerfile does
- Schema design — how would you model users, documents, and chat history

**AI Engineer:**
- RAG pipeline end-to-end — explain without notes
- Vector embedding — what it is, why cosine similarity works
- Agent tool-calling loop — step by step
- Hallucination — what it is, how RAG reduces (not eliminates) it
- Evals — what they are, how you'd test a RAG system
- Observability — what you monitor in production LLM apps
- Chunking tradeoffs — size vs overlap vs retrieval quality
- Prompt injection — what it is, how to defend against it

**React/TypeScript (keep sharp — this is Mohamad's strength):**
- useCallback and useMemo — when to use, when not to
- Stale closures in useEffect — what they are, how to cause them, how to fix
- Re-render causes — how to profile and reduce them
- TypeScript: `type` vs `interface`, `unknown` vs `any`, basic generics
- Code review: spot missing dependency arrays, mutated state, wrong key usage

## What to Skip

- LangChain / LlamaIndex — hides fundamentals, hurts AI interviews
- Fine-tuning — needs GPU budget, low ROI for job hunting
- Deep Python OOP — not needed at this stage
- Redis + worker queue — **deferred, not skipped**: justified by the platform scope, but only in M6 when the jobs demand it (ADR required). Adopting infra before the need is a junior tell.
- Microservices — deliberate monolith (PLAN.md ADR-001); be able to argue why NOT
- ML model training / prediction — that's data science; urgency triage stays rule+LLM based and honestly named
- GraphQL — REST is fine, don't split focus
- Kubernetes — not expected at mid-level

---

## Last Session

- **Date:** 2026-07-11 (2nd session, same day — evening)
- **Phase / topic covered:** **M1 — closed ENG-10, built ENG-11 (`architecture.md`).** Architect hat. C4 diagrams. (Carryover still valid: PLAN.md v3, FleetPulse is his 2nd portfolio piece, don't mention Talpa, Claude writes the `notes/` files now.)
- **What we did:** **Closed ENG-10 for real.** He'd flipped it to Done in Linear but it was **never merged** — caught it (`PRODUCT.md` not on `main`), he merged the PR (`#23`, squash). Lesson that landed: **"Done in Linear ≠ merged in git — git is the source of truth that counts."** **Rust-check:** **COSINE SIMILARITY FINALLY PASSED** (4th attempt) — he produced *"tighter angle = more similar."* Corrected two imprecisions: it's not about "accuracy," and it's between **two vectors** (the query vs. one stored chunk), not "the whole database." **JWT:** shape right (no DB lookup, expiry from the `exp` payload claim) but **muddled the mechanism** — he thinks the *signature* is stored in the env var. Corrected hard: **env holds `SECRET_KEY`; the server RECOMPUTES the signature over `header.payload` and compares it to the token's signature.** **Built `meddocs/docs/architecture.md` (ENG-11)** — I drafted diagrams, he made the calls & defended. Taught **C4** (box = the *software*, not the org/clinic; **every human is outside the box**; a "container" = a separately-running process, NOT a Docker container). He derived **Level 1** himself: 4 personas + **5 external systems** (Groq=LLM, OpenAI=embeddings only, Pinecone=vectors, Object Storage=PDFs, Email/SMTP). **Nailed the Postgres boundary trap** (we run it → inside → shows at L2; contrast Pinecone = third-party SaaS → outside). Key teaching: **name the *capability* at L1, pick the *vendor* in an ADR** (he kept reaching for "S3"/"Gmail"). **Level 2**: 3 containers (frontend/backend/Postgres); he correctly anticipated **Redis→M6** and correctly flagged we're **rejecting microservices (ADR-001 monolith)**. Traced the **RAG pipeline** (OpenAI→Pinecone→Groq, citations = page number on the retrieved chunk). **Tech-choice table** drafted; he defended **monolith** ("overkill" → sharpened to "microservices solve an org/scaling problem I don't have") and **Postgres-vs-Mongo** (killed his "Mongo is fast for chat" myth; real answer = relational data + ACID + `FOR UPDATE SKIP LOCKED`). **Pushback moment:** he challenged the design-challenge as "slowing productivity" — reframed: **for a docs ticket the doc IS the product; defending it under challenge is the M1 deliverable, not filler.** (Recurring "undervalues non-coding work" pattern — expect it again.)
- **Where we stopped:** **ENG-11 doc is written, committed (`30d56b9`), pushed to `origin/ENG-11-architecture` — but NOT merged, so ENG-11 is still In Progress.** ⚠️ **Two cleanups pending:** (1) the commit message is **wrong** — titled *"feat: add initial product definition and user personas"* but it contains the architecture doc (leftover from ENG-10); fix via `git commit --amend` + `push --force-with-lease`, **or** set the correct squash title at merge (`docs(architecture): add C4 context + container diagrams and tech-choice table`). (2) **Open + merge the PR** (`ENG-11-architecture` → `main`) to hit the "merged via PR" bar, then flip **ENG-11 → Done**. Outer-repo note `notes/architecture.md` is committed to `main` (`3b90a6e`) — that part's clean.
- **Next task:** **ENG-12 — `meddocs/docs/erd.md`** — design the **NEW multi-tenant schema** (org→users/patients→documents→workflow states→audit log). ⚠️ current `models.py` is the OLD single-user schema — do not copy it. Then ENG-13 permissions matrix, ENG-14 workflow state machine, ENG-15 api-conventions, ENG-16 ADRs (the real challenge rounds — ADR-001 monolith, 002 tenancy, 003 authz, 004 flags, 005 storage), ENG-17 wireframes. He leads each doc; I attack, he defends.
- **Things Mohamad was shaky on — re-test next session:** **JWT MECHANISM** — he thinks the signature lives in the env var. Drill: *"env holds the `SECRET_KEY`; the server recomputes the signature and compares."* **Cosine** finally passed but re-confirm once cold. He **reaches for vendor names too early** (S3, Gmail) — reinforce "capability at L1, vendor in the ADR." He **still undervalues design/non-coding work** — keep reframing it as senior work. Older carryover: why keyword flagging runs at upload not chat; `enumerate()` order; `+=` vs `append`; `# type: ignore`.
