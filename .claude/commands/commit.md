---
description: Review the pending diff, raise flags, draft a commit message, then STOP for approval before committing and pushing.
argument-hint: "[optional message hint]"
---

Help Mohamad commit his current work. Do these steps in order and do not skip the stop:

1. Run `git status` and `git diff HEAD` to see every pending change.
2. Invoke the `/code-review` skill on the diff. Summarize its findings as a short flagged list, most-severe first. If there is a real correctness bug, say so plainly and recommend fixing before committing.
3. Do a safety sweep for things that must never be committed: secrets / API keys / `.env` values, debug prints, large or accidental files, commented-out junk. Raise anything found loudly.
4. Consider the branch: if this is product code (not just docs/notes) and the current branch is `main`, suggest creating an `ENG-XX` feature branch first, per Mohamad's working agreement. Docs/notes on `main` are fine.
5. Propose ONE meaningful commit message in Conventional Commits form: `type(scope): summary`. The git history is part of Mohamad's portfolio — make it accurate and specific, not generic. If arguments were passed ($ARGUMENTS), use them as a hint for the scope/summary.
6. STOP HERE. Show Mohamad: (a) the flagged issues, (b) the exact files that will be committed, (c) the proposed message. Do NOT run commit or push yet. Ask him to confirm, edit the message, or fix flags first.
7. Only after he explicitly confirms: `git add -A`, commit with the approved message, then `git push`.

Rules: never commit secrets; never push without explicit confirmation; if `/code-review` surfaces a serious bug, recommend fixing before committing rather than committing anyway.
