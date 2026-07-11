---
description: Review the pending diff, put it on the right ticket branch, draft a commit message, then STOP for approval before committing and pushing.
argument-hint: "[ENG-NN] [optional message hint]"
---

Help Mohamad commit his current work. Do these steps in order and do not skip the STOP.

## 0. Find the right repository

Mohamad usually runs this from the `ai-engineer` root, but the **MedDocs product lives in the nested
`meddocs/` repo** — its own git repo with its own remote (`MedDocs.git`), separate from the outer
`ai-engineer` repo (`ai-engineering.git`).

- Check for pending changes in **both**: `git -C . status --porcelain` and `git -C meddocs status --porcelain`.
- Set **REPO** to whichever has changes. If **both** have changes, stop and ask Mohamad which one to commit — never mix the two repos in one commit.
- Run **every** git command below with `git -C <REPO> …` so it works no matter which directory he launched from.

## 1. Determine the ticket

MedDocs branches are Linear-linked by ticket ID. Find the ticket in this priority order:

1. If `$ARGUMENTS` contains an `ENG-<number>`, use that.
2. Else if the current branch (`git -C <REPO> branch --show-current`) already matches `ENG-<number>-…`, use that ticket — we're already on it.
3. Else ask Mohamad which ticket this is. If the Linear MCP is connected, first list the MedDocs project's **In Progress** issues to offer him the likely one; if it isn't connected, just ask for the `ENG-NN`.

Docs/notes work in the **outer `ai-engineer` repo** is not ticket-tracked — skip the ticket/branch steps for that repo and commit on `main`. The ticket/branch flow applies to the **MedDocs repo**.

## 2. Make sure we're on the matching branch (MedDocs repo only)

Linear only links the branch if its name carries the ticket ID.

- If the current branch already matches `ENG-<number>-…` for this ticket, stay on it.
- If we're on `main` (or a non-matching branch), create the ticket branch **from an up-to-date main**,
  following Mohamad's convention **`ENG-<n>-<short-kebab-slug>`** (e.g. `ENG-10-product-definition` —
  short, like `ENG-6-document-upload`, not Linear's long auto-slug). Propose the slug and let him adjust.
  Uncommitted working-tree changes carry over to the new branch automatically, so create it before committing:
  `git -C <REPO> checkout -b ENG-<n>-<slug>`.

## 3. Review the diff

- Run `git -C <REPO> status` and `git -C <REPO> diff HEAD` to see every pending change.
- Invoke the `/code-review` skill on the diff. Summarize findings as a short flagged list, most-severe first. If there's a real correctness bug, say so plainly and recommend fixing before committing.

## 4. Safety sweep

Look for things that must never be committed: secrets / API keys / `.env` values, debug prints, large or accidental files, commented-out junk, unrelated changes that snuck in (e.g. a stray edit to a file you weren't working on). Raise anything found loudly.

## 5. Draft the message

Propose ONE meaningful commit message in Conventional Commits form: `type(scope): summary`. The git
history is part of Mohamad's portfolio — make it accurate and specific, not generic. Reference the
ticket in the body (e.g. `Refs ENG-10`). If `$ARGUMENTS` included a message hint, use it for the summary.

## 6. STOP

Show Mohamad: (a) the flagged issues, (b) the branch that will be used (and whether it was newly created),
(c) the exact files that will be committed, (d) the proposed message. Do **NOT** run commit or push yet.
Ask him to confirm, edit the message, or fix flags first.

## 7. Commit & push (only after explicit confirmation)

- `git -C <REPO> add -A`
- commit with the approved message
- `git -C <REPO> push -u origin <branch>`
- Then offer to open a PR with `gh` (`gh pr create` run against REPO) so Linear picks up the branch/PR and
  the M1 "merged via PR" bar is met — but only if he wants it.

## Rules

- Never commit secrets. Never push without explicit confirmation.
- Never mix the `ai-engineer` and `meddocs` repos in one commit.
- If `/code-review` surfaces a serious bug, recommend fixing before committing rather than committing anyway.
