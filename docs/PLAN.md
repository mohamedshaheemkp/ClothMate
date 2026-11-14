# ClothMate — Plan
_Update checkboxes at the end of every session._

## Done (as of 2026-11-11)
- [x] Phase 0: geometry core + tests
- [x] Python API: validation, scale, homography, API-key, size limit, safe errors
- [x] Photo-points -> garment/body measurement mapping
- [x] Spring Boot skeleton + DB health + /measure forwarding + save to PostgreSQL
- [x] docker compose for PostgreSQL
- [x] Angular measurement canvas working through Spring proxy
- [x] 16 garment specs + ease defaults
- [x] Homography hardening (Hartley normalization, convex check)

## NOW (do in this order — one at a time)
- [ ] N1. Reconcile repo: is `clothmate-web/` committed? run all tests; explain 40 vs 16 test count
- [ ] N2. Fix/understand shoulder error (45.8 vs 48): define shoulder points clearly in UI + spec
- [ ] N3. Accuracy test protocol: 10+ garments (men + women), tape vs app, results table (CSV) 

## NEXT
- [ ] X1. Angular UI to match prototype: dashboard + AI Measurement / Manual Measurement tabs
- [ ] X2. Show history of sessions (Spring /api/sessions -> Angular list)
- [ ] X3. Tailor measurement research doc: garment -> body mapping table
- [ ] X4. Integration plan doc: embed in website (iframe/window), CORS, auth
- [ ] X5. Dockerize Python + Spring + Angular (one `docker compose up`)

## LATER
- [ ] L1. Security pass: auth (login/roles: customer/tailor/staff), rate limiting, input fuzzing
- [ ] L2. Tester-ready: Spring tests, Angular tests, an end-to-end test, CI (GitHub Actions)
- [ ] L3. A4 sheet as second reference object
- [ ] L4. Automatic point detection (replace manual clicks) / photo-of-person mode
- [ ] L5. Live video body scan (future, per meeting)

## Deliverables for the team leader
- [ ] Accuracy report (N3)
- [ ] Tailor mapping doc (X3)
- [ ] Integration plan + time estimate (X4)
- [ ] Working demo ("make it work and show")
- [ ] Progress update note: `docs/leader_update.md`
