# Claude Tooling by Department — MedDocs

> Research 2026-07-11. Which Claude Code plugins / MCP servers / skills help each "department" (team-role) from PLAN.md §2 — and **when** to adopt each. The discipline rule (from PLAN.md itself): don't adopt a tool before the milestone needs it. 3–6 MCP servers is the sweet spot; more = context bloat + footguns. Plugins can bundle hooks that run commands — only install from trusted authors and read the bundle first.

## Vocabulary (so the choices make sense)

- **MCP server** — gives Claude live access to an external system (your DB, GitHub, Figma, Sentry). Costs context; pick few.
- **Plugin** — a bundle that may contain skills + slash-commands + hooks + MCP servers. Install via `/plugin`. Read what it bundles.
- **Skill** — a capability Claude loads on demand (e.g. `/code-review`, `/security-review`, `/verify`, `dataviz`). Cheap, already built in.
- Install an MCP server: `claude mcp add <name> ...`. Install a plugin: `/plugin marketplace add <repo>` then `/plugin install <name>@<marketplace>`.

## Already wired into this environment

| Tool | Status | Department |
|---|---|---|
| **Figma MCP** (official) | ✅ connected | Designer, Frontend, Architect (FigJam diagrams) |
| **Gmail MCP** | ✅ connected | Job-hunt / comms |
| **Indeed MCP** | ✅ connected | Job-hunt |
| **Linear** (official connector) | ⚠️ needs auth (/mcp in interactive session) | PM / ticket discipline |
| Google Calendar / Drive | ⚠️ needs auth | PM / misc |
| Built-in skills: `/code-review`, `/security-review`, `/verify`, `/run`, `dataviz`, `artifact-design` | ✅ already here, free | QA, Security, all |

## Per-department map

| Department | Tool | What it gives you | Adopt at | Trust |
|---|---|---|---|---|
| **PM** | Linear (connector) | ENG-XX tickets, PRs linked to issues — the ticket discipline in the working agreement | M1 (optional; GitHub Issues also fine) | Official |
| **Architect** | Figma MCP → FigJam (`generate_diagram`, `get_figjam`) | C4 architecture + ERD + workflow state-machine diagrams for `docs/` | M1 | Official |
| **Architect** | *(none — use Mermaid)* | ERD / state diagrams as Mermaid in markdown need no plugin | M1 | — |
| **Designer** | **Figma MCP** | Wireframes (M1), design tokens + component library + design-to-code (M5). The marquee capability, already connected | M1 + M5 | Official |
| **Backend** | **Postgres MCP Pro** (crystaldba) — **read-only DSN** | Schema inspection, `EXPLAIN` plan analysis, index tuning, N+1 hunting — directly serves M2/M3 "learn" lists | M2 | 3rd-party, reputable, OSS |
| **Backend** | GitHub MCP (github official) | PRs, issues, Actions runs, secret scanning | M2 (when CI + PRs start) | Official |
| **AI engineer** | **Langfuse MCP** (native `/api/public/mcp`) | Query traces, manage prompts, run evals from the terminal — the M4 observability story | M4 | Official |
| **AI engineer** | Context7 (Upstash) | Up-to-date OpenAI/Groq/Pinecone/FastAPI SDK docs → stops hallucinated APIs | M2+ (as SDK surface grows) | Official (Upstash) |
| **Frontend** | Figma MCP + Context7 | Design-to-code; current Next.js App Router / React Query / TanStack docs (these move fast) | M5 | Official |
| **DevOps/SRE** | GitHub MCP | CI workflow runs, build-failure analysis, Dependabot | M2 (CI) → M6 (matrix) | Official |
| **DevOps/SRE** | **Sentry MCP** (getsentry) | Pull errors/traces/logs into the terminal, root-cause + fix — the M6 monitoring story | M6 | Official |
| **QA** | **Playwright MCP** (`@playwright/mcp`) | Drive a real browser, generate e2e specs from plain-language flows — M6 Playwright work | M6 | Official (MS) |
| **QA** | `/verify` skill | Already here — exercise a change end-to-end before committing | now | Built-in |
| **Security** | **Semgrep plugin** (claude.com/plugins/semgrep) | SAST + SCA + secrets scan via post-edit hook | M6 security pass | Official-listed |
| **Security** | `/security-review` skill + [claude-code-security-review](https://github.com/anthropics/claude-code-security-review) GH Action | Semantic vuln review of the diff (auth/authz bypass, injection) — complements Semgrep, doesn't replace it | now (skill) / M6 (Action) | Anthropic |
| **Tech writer** | *(none needed)* | Native Claude + Context7 for accurate API snippets in the README | M7 | — |

## Install-now shortlist (you are at M0→M1)

Only one thing to actually turn on this week: **Figma MCP** (already connected) for M1 wireframes + FigJam architecture/ERD diagrams. Optionally authorize **Linear** if you want tickets there instead of GitHub Issues. **Everything else waits for its milestone** — adopting it early is procrastination disguised as setup.

- M2: Postgres MCP Pro (read-only), GitHub MCP
- M4: Langfuse MCP, Context7
- M6: Playwright MCP, Sentry MCP, Semgrep plugin

## Security learning gem (for the M6 security department)

Giving Claude a GitHub MCP with issue-read access opens a **prompt-injection supply-chain** path: a malicious GitHub issue body can carry instructions the agent then follows. Real, documented (GMO Flatt Security, "Poisoning Claude Code: One GitHub Issue to Break the Supply Chain"). This is exactly the "untrusted input crossing a trust boundary" lesson MedDocs already teaches at the *document-content* boundary (M4) — same defense, different surface. Write it up as an ADR/security note when you reach M6.

## Community SKILLS & marketplaces (the "think like a lawyer" kind)

**The distinction that matters:** an MCP server gives Claude *tool access* (query your DB). A **skill** gives Claude *encoded expertise / a way of thinking* (SKILL.md = instructions + scripts Claude loads on demand — this is the "think like a German lawyer" pack you installed). A **plugin/marketplace** is a bundle that can ship skills + subagents + slash-commands + hooks + MCP servers together. A **subagent** is a specialised persona. You want skills + subagents.

**Open standard:** SKILL.md became an open standard (agentskills.io, Dec 2025), portable across ~40 clients (Claude Code, Copilot, Cursor, Codex, Gemini CLI). A skill is just a folder + `SKILL.md` with YAML frontmatter — **trivial to author yourself.**

### Highest-signal sources (grounded)

| Source | What it is | Stars | Use it for |
|---|---|---|---|
| **anthropics/skills** | Official reference skills (source-available): design, dev, docs, testing web apps, MCP generation | official | Safe starting point; read these to learn the SKILL.md format |
| **wshobson/agents** | Multi-harness marketplace: 92 plugins / 199 agents / 162 skills / 106 commands, organised by exactly our departments (backend, FastAPI/Python, database, frontend, security, testing/QA, API design, ML/RAG) | **37.8k** ✅ verified | **The main one.** Install per-department, per-milestone — never all at once |
| **obra/superpowers** | A dev *methodology* plugin: brainstorm → worktree → plan → TDD → review → finalize | "very popular" (the 252k figure in search is implausible — treat as unverified) | ⚠️ **Anti-learning for you** — see warning below |
| VoltAgent/awesome-agent-skills · hesreallyhim/awesome-claude-code · davila7/claude-code-templates · claudemarketplaces.com | Aggregator directories (1000s of skills, updated from GitHub) | large | Discovery/browsing only |

### Status (2026-07-11): `wshobson/agents` is **registered** as marketplace `claude-code-workflows` — browsable, nothing enabled, zero context cost. Enable specific plugins per milestone: `claude plugin install <plugin>@claude-code-workflows` (e.g. `python-development`, `security`, `database`). **Registered ≠ enabled** — this is the distinction the 16 disabled `klotzkette-german-legal-skills` plugins prove: installing/enabling ahead of need produces dead clutter, not readiness.

### Per-department picks from wshobson/agents (adopt at the milestone, not now)

- **Backend/Architecture:** `backend-architect`, `python-development` (FastAPI), `database` — as *reviewers/challengers*, M2–M3
- **Security:** `security` / security-auditor — M6 (complements Semgrep + `/security-review`)
- **Testing/QA:** test-generation skills — M6
- **AI/RAG:** ML/RAG orchestrators — inspect for M4 ideas, but you're building RAG from fundamentals (no-LangChain rule), so read, don't delegate
- **Frontend:** frontend/React reviewers — M5, as the "hostile senior reviewer" the plan already calls for

### ⚠️ Two warnings that override the hype

1. **A skill is executable instruction; most community skills are unvetted.** Read the SKILL.md (and any bundled hook — hooks run commands on your machine) before installing. You already installed one unofficial pack — going forward, open the folder first. This is itself the M6 security lesson.
2. **The learning trap.** Skills that *review, challenge, or explain* your code fit CLAUDE.md ("Mohamad writes every line"). Skills/methodologies that *write the code for you* (Superpowers' auto-build workflow, full-stack "orchestrator" agents) directly sabotage the practice you're here to get. Great for shipping a startup; poison for getting hired. Use the reviewer half of the ecosystem, refuse the generator half.

### The senior move: author your own skill

Your "think like a lawyer" pack has a MedDocs equivalent you should **build, not download**: a `german-clinical-docs` skill encoding document types (Arztbrief, Laborbefund…), DSGVO constraints, urgency-triage rules, and lab reference ranges. It (a) sharpens the M4 AI pipeline, (b) is a portfolio artifact ("I authored an Agent Skill"), and (c) teaches the SKILL.md standard from the inside. Far more impressive in an interview than a list of installed plugins.

## Sources

- [Discover and install plugins — Claude Code Docs](https://code.claude.com/docs/en/discover-plugins)
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- [Postgres MCP Pro (crystaldba)](https://www.totalum.app/blog/claude-code-postgres-mcp-2026) · [best DB MCP servers](https://dupple.com/learn/best-mcp-servers-databases)
- [Playwright plugin](https://claude.com/plugins/playwright) · [Sentry MCP](https://github.com/getsentry/sentry-mcp) · [Semgrep plugin](https://claude.com/plugins/semgrep)
- [Langfuse for coding agents](https://langfuse.com/agents/agents) · [Context7](https://context7.com/docs/clients/claude-code) · [GitHub MCP](https://github.com/github/github-mcp-server)
- [Poisoning Claude Code: One GitHub Issue (GMO Flatt Security)](https://flatt.tech/research/posts/poisoning-claude-code-one-github-issue-to-break-the-supply-chain/)
