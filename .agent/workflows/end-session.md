---
description: End a ClothMate session - write the handoff so any tool can continue
---
1. Run `python -m pytest` and `git status`.
2. Rewrite `docs/HANDOFF.md` completely (use its template): what was done, exact
   test result, what is half-finished, the exact next step, commands to resume,
   open questions, new concepts learned.
3. Add any new decisions to `docs/DECISIONS.md` and concepts to `docs/LEARNING_LOG.md`.
4. Update checkboxes in `docs/PLAN.md`.
5. Commit: `git add -A && git commit -m "docs: handoff <date>"` (ask the user before pushing).
6. Tell the user: "Handoff saved. Open the other tool and run its start step."
