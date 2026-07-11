# Architecture & C4 — Cheat Sheet

Notes for the system-design docs (ENG-11+). Keep answers interview-ready.

## The C4 model

C4 = four zoom levels of an architecture diagram. You usually only draw the top two.

1. **Context** — the system as ONE box, plus the people and external systems around it. *Who/what touches it?*
2. **Container** — open the box: the separately-running pieces (app, DB, frontend) and how they talk.
3. **Component** — inside one container: its internal modules. (Rarely drawn.)
4. **Code** — classes/functions. (Almost never drawn — that's what the code is for.)

> "Container" ≠ Docker container. It means a **separately deployable/running thing** (a process, a database, an SPA).

## The one skill: where is the boundary?

The hard part isn't drawing — it's deciding **what's inside the box vs. outside**.

- **The box = the software you build and run** (NOT the company/clinic).
- **Every human is OUTSIDE the box.** A person is never inside software. All personas = users around it.
- **Inside vs outside for services — the test is who RUNS it:**
  - We run it ourselves → **inside** (e.g. PostgreSQL — even on its own server, it's ours).
  - A third party runs it, we call their API → **outside / external** (Groq, OpenAI, Pinecone, Object Storage, Email).
- **Name the capability, not the vendor, at Level 1.** "Object Storage", not "AWS S3". The vendor is an ADR decision — never block the architecture on picking a brand.

## Arrows

- Every arrow is **labelled** with *what flows across it* (data), not just "connects to".
- Arrow **direction = who initiates the call**. People call into MedDocs; MedDocs calls out to external systems.
- An unlabelled arrow is a bug.

## MedDocs Level 1 (memorise the inventory)

- **Box:** MedDocs.
- **People (4):** Assistant/MFA · Physician · Org Admin · Auditor.
- **External systems (5):** Groq (LLM) · OpenAI (embeddings only) · Pinecone (vectors) · Object Storage (PDF files) · Email/SMTP (invites + notifications).
- **Not shown (inside the box):** PostgreSQL — we run it → Level 2.

Two AI vendors, two jobs: **Groq = the LLM brain**, **OpenAI = embeddings only** (cost rule).
