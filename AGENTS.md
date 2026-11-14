# AGENTS.md — ClothMate (shared rules for Claude, Antigravity, any AI tool)

> Read this file fully at the start of every session. Then read `docs/HANDOFF.md`.

## 1. What this project is
ClothMate measures garments (and later bodies) from a photo. The user clicks
reference points on a photo; a bank card (8.56 x 5.4 cm) in the photo gives the
scale; the system returns real-world measurements (chest, length, shoulder, ...)
and maps them to tailor/body measurements.
It is a company assignment. The team leader wants **industry-ready** work:
secure, robust, tested. It is NOT a college-level demo.

planning to do automatic detection of image , user just need to upload image of the dress , and it detects the type and measure accordingly with accurate results

## 2. Who you are working with (IMPORTANT)
- The user is a B.Tech AI & Data Science student. Beginner coder (basic Python,
  basic Java; new to Docker, SQL, Angular, Spring).
- The user must be able to **explain every line** to the company. Blind
  copy-paste is the failure case.
- Working mode: **small steps -> explain -> user types/runs it -> verify -> next.**
  - Explain WHAT it does, WHY it is needed, and what would break without it.
  - Max ~1 concept per step. No giant code dumps unless the user asks.
  - After a meaningful step, add 1 "explain it back" question.
  - When the user is stuck on time, speed up, but still explain briefly.
- Add every new concept to `docs/LEARNING_LOG.md`.

## 3. Architecture (source of truth: docs/PROJECT_CONTEXT.md)
Angular (clothmate-web) -> Spring Boot (:8080) -> Python FastAPI (:8000) -> PostgreSQL (Docker)
- Photo stays in the browser; only click-points go to the backend.
- Python = math/measurement core. Spring = API gateway + persistence.
- Both services share the env var `CLOTHMATE_API_KEY` (header `X-API-Key`).

## 4. Commands (Windows / PowerShell)
- Python tests:  `python -m pytest`   (pytest.ini has `pythonpath = .`)
- Python API:    run on port 8000, needs `CLOTHMATE_API_KEY` (`CLOTHMATE_ENV=dev` = dev mode)
- Spring:        port 8080, same `CLOTHMATE_API_KEY`
- Database:      `docker compose up -d` (PostgreSQL)
- Angular:       from `clothmate-web/`: `npm install`, then `ng serve`
- Spring endpoints: /api/health, /api/garments, /api/garments/{id}, /api/measure, /api/sessions
> If a command here is wrong, FIX THIS FILE.

## 5. Code standards (industry-ready)
- Validate all input at the API edge. Safe error messages (no stack traces to clients).
- No secrets in git. Use env vars. `.env` is git-ignored.
- Every new behaviour gets a test. Run the full test suite before every commit.
- Small commits, clear messages (`feat:`, `fix:`, `docs:`, `test:`).
- Keep garment definitions in `specs/` (data, not code).
- Don't add dependencies without telling the user why.

## 6. Session protocol (this is how Claude <-> Antigravity handoff works)
**START:** read AGENTS.md -> docs/HANDOFF.md -> docs/PLAN.md. Run `git status`,
`git log --oneline -5`, and the tests. Confirm the HANDOFF matches reality.
**DURING:** work on ONE item from PLAN.md "Now". Log decisions in docs/DECISIONS.md.
**END (or when the user says "I'm hitting my limit"):** update docs/HANDOFF.md
completely, commit it. A good handoff means the next tool needs zero questions.

## 7. Honesty rules
- Report test counts and results exactly as seen. If a number changes unexpectedly
  (e.g. 40 -> 16 tests), investigate and write it in HANDOFF.md.
- Never claim something works without running it.
- Mark guesses as "ASSUMPTION" and record them in docs/DECISIONS.md.

## 8. Do not
- Do not reintroduce Streamlit (removed on purpose).
- Do not rewrite working modules "to be cleaner" without asking.
- Do not commit large photos or secrets.
