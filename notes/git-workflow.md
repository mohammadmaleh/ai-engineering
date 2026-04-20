# Git Workflow — MedDocs Professional Setup

## The Rules
- Never commit directly to `main` — it's protected
- Every feature = a Linear ticket + a branch + a PR
- Squash merge only — one clean commit per feature in main's history
- Branch is auto-deleted after merge

## Branch Naming
Linear generates the branch name for you — open the ticket, press `Ctrl + .` to copy it.

Format: `ENG-123-short-description`

Examples:
- `ENG-1-setup-fastapi`
- `ENG-2-add-pdf-upload`
- `ENG-3-rag-chat-endpoint`

## The Workflow (every single feature)

```
1. Create a Linear ticket for the feature
2. Copy the branch name from Linear (Ctrl + .)
3. git checkout -b ENG-123-feature-name
4. Write code
5. git add <files>
6. git commit -m "feat: add pdf upload endpoint"
7. git push origin ENG-123-feature-name
8. Open a PR on GitHub — link it to the Linear ticket
9. PR gets reviewed (or self-reviewed)
10. Squash merge → branch auto-deleted → Linear ticket auto-closed
```

## Commit Message Format (Conventional Commits)
```
feat: add new feature
fix: fix a bug
refactor: restructure code without changing behavior
chore: tooling, config, dependencies
docs: documentation only
test: add or update tests
```

Examples:
- `feat: add JWT authentication`
- `fix: handle None content in agent response`
- `refactor: move db logic to crud.py`

## Magic Words (link commits to Linear)
Include in your commit or PR description to auto-close the ticket:
- `Fixes ENG-123`
- `Closes ENG-123`
- `Part of ENG-123` (doesn't close, just links)

## PR Description Template
```
## What
Short description of what this PR does.

## Why
The Linear ticket context — what problem this solves.

## How
Key implementation decisions worth noting.

## Test plan
- [ ] Tested endpoint in /docs
- [ ] Edge cases handled
```
