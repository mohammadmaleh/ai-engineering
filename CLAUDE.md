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

**MedDocs** — Medical Document Analyzer for the German healthcare market.

Upload medical documents (Arztbriefe, lab reports, discharge summaries). The app:
- Summarizes them in plain language
- Answers questions with exact citations from the document
- Flags critical keywords (dringend, kritisch, abnormal values)
- Stores document + chat history per user account

Why this is impressive: specific real market, citation highlighting is non-trivial, DSGVO awareness, directly relevant to Germany's healthcare digitalization push.

Stack: FastAPI · PostgreSQL · SQLAlchemy · JWT · ChromaDB · OpenAI API · PyMuPDF (PDF parsing) · Next.js · Tailwind · Docker · GitHub Actions · Langfuse

> For a portfolio project, use fake/sample medical documents only. Never real patient data. Mention DSGVO compliance as a production concern in the README.

## Current Status

Learning phases (check these off as completed):

- [x] LLM basics — streaming, history, system prompts (`01-llm-basics/chat.py`)
- [x] RAG — ChromaDB, chunking, context injection (`02-rag/rag.py`)
- [x] Agents — tool schema defined, but tool-calling loop NOT implemented (`03-agents/agent.py`) ⚠️
- [ ] Phase 0 — Python survival kit
- [ ] Phase 1 — FastAPI fundamentals
- [ ] Phase 2 — PostgreSQL + SQLAlchemy
- [ ] Phase 3 — JWT authentication
- [ ] Phase 4 — AI features: agent loop, RAG as API, PDF parsing, citations, evals
- [ ] Phase 5 — Testing with pytest
- [ ] Phase 6 — Docker
- [ ] Phase 7 — Deploy + CI/CD
- [ ] Phase 8 — Observability with Langfuse
- [ ] Phase 9 — READMEs, CV, start applying

Full checklist with every step: `/home/mohamad/.claude/plans/structured-growing-rain.md`

## Concepts Already Understood

- venv, pip, dotenv, installing packages
- LLMs have no memory — full message history must be sent every call
- Streaming: `stream=True`, iterate chunks, `chunk.choices[0].delta.content`
- RAG: chunk → embed → store in ChromaDB → query by similarity → inject into prompt
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

## Key Decisions

- **Groq during learning** (free, fast) → **switch to OpenAI before deployment** (2-line change)
- OpenAI because: industry standard, employers recognize it, Groq is not used in production
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
- Redis, message queues, microservices — premature
- GraphQL — REST is fine, don't split focus
- Kubernetes — not expected at mid-level

---

## Last Session

- **Date:** 2026-04-20
- **Phase / topic covered:** Phase 4 — Agent tool-calling loop
- **What we built:** `05-agents/agent_loop.py` — working Pattern A agent loop with Groq + Tavily search, max iterations limit, fallback summary
- **Where we stopped:** Agent loop working. Notes updated in `notes/agents.md` and `notes/python-basics.md`.
- **Next task:** Phase 4 continued — PDF parsing, RAG as API endpoints, citations
- **Things Mohamad was shaky on — re-test next session:** bcrypt hashing vs encryption distinction, Alembic commands, `while/else` pattern, message roles (user/assistant/system/tool)
