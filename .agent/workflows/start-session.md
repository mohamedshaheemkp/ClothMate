---
description: Start a ClothMate session - load context, verify repo state
---
1. Read `AGENTS.md`, `docs/HANDOFF.md`, `docs/PLAN.md`.
2. Run `git status` and `git log --oneline -5`. Compare with HANDOFF.md "Repo state".
3. Run `python -m pytest` and note the exact pass/fail count.
4. Tell the user in 5 lines max: where we are, what is broken (if anything), and the
   proposed single next step from PLAN.md "Now".
5. Wait for the user's OK, then begin in small, explained steps.
