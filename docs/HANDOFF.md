# HANDOFF — the baton between Claude and Antigravity
_Rewrite this ENTIRE file at the end of every session._

**Last session:** 2026-11-14 by Antigravity
**Last known good state:** 2026-11-14

## Repo state
- Branch: main
- Last commit: 7eb7be5 ("Report homography as the measurement method")
- Uncommitted files: prompt.md
- Tests: 59 passed (venv: `.\venv\Scripts\python -m pytest`) [Note: 59 tests verified after restoring and expanding spec/mapping test suites]

## Done this session
- Initialized session verification: verified git status, commit history, and test suite.
- Analyzed project scope, goals, and architectural roadmap.
- Formulated master architectural plan and visual blueprint spanning manual clicking to automatic CV detection.

## Half-finished (exact place I stopped)
- Reviewing accuracy & roadmap alignment with the user.

## NEXT STEP (one thing, concrete)
- Review the master plan with the user, then address N1/N2 from docs/PLAN.md (Shoulder point calibration & 10-garment accuracy protocol).

## How to resume (commands)
1. `docker compose up -d`
2. Set `CLOTHMATE_API_KEY`, start Python API (:8000), then Spring (:8080), then `ng serve`
3. Run tests: `.\venv\Scripts\python -m pytest`

## Open questions / blockers
- Shoulder measurement currently has ~2.2 cm variance on blue polo ground truth test; needs clearer landmark definition in spec.

## New concepts the user met (also add to LEARNING_LOG.md)
- Projective Homography vs. Direct Linear Transformation (DLT)
- Ground Truth validation before deep learning automation
