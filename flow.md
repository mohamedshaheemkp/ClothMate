browser → Spring Boot /api/measure → Python /v1/measure → result
                     ↓
          saved in PostgreSQL → result + session id back to the browser





How to set it up

Unzip into your repo root (...\TannMann\CODE\Clothmate), then commit.
In Antigravity, run /start-session once to check it picks everything up. If the slash commands don’t appear, paste the workflow text as a prompt instead.
Fix any command in AGENTS.md that doesn’t match your machine.

The daily habit

Before you hit Claude’s limit, tell me “write my HANDOFF.md now”. Paste it into docs/HANDOFF.md, commit, then continue in Antigravity.
When switching back, run /end-session in Antigravity, commit, and paste HANDOFF.md into Claude using CLAUDE_STARTER.md.