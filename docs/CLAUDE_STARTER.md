# Paste this into Claude when you start (or resume) a session

I'm continuing the ClothMate project. Rules: AGENTS.md (teaching mode: small steps,
explain, I type, I must be able to explain every line).

Here is my current docs/HANDOFF.md:
<paste HANDOFF.md>

Here is `git log --oneline -5` and my last pytest result:
<paste>

Today I want to: <one goal from PLAN.md "NOW">
Do NOT start coding until you've told me in 5 lines where we are and what the first step is.

---
# When Claude hits its limit
Ask Claude (before limit): "Write my HANDOFF.md now." Copy it into docs/HANDOFF.md, commit,
then open Antigravity and run /start-session.

# When Antigravity hits ITS limit (switching back)
In Antigravity run /end-session, commit, then paste HANDOFF.md into Claude using the template above.
