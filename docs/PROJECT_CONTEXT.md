# ClothMate — Project Context
_Last verified: 2026-11-11 (update when things change)_

## Goal
Assignment for a company: an AI-assisted tool that measures clothes from a camera/uploaded
photo (length, chest, shoulder, waist, ...). Users: customers, tailors and staff.
Scope: every garment, men's and women's. Reference object: bank card first; A4 later.
Target: accuracy as close to 100% as possible.

## Product context (from team meeting)
Computer vision has two sub-modes: (1) live video body scan - in development / future;
(2) photo-based scan - current focus. For now photo input = photo of a person OR a
garment laid on a flat base. A frontend prototype ("Clothmate zimutail frontend") has a dashboard
with tabs: AI Measurement / Manual Measurement / Sellers & Brands.
Voice/GenAI = later, not required now.

## Team leader decisions (2026-10-30)
Frontend: Angular first. Backend: Spring Boot. DB: PostgreSQL. REST is fine.
He wants it "working and shown", industry-ready (secure, robust, tested).

## Architecture
Angular (clothmate-web) -> Spring Boot :8080 -> Python FastAPI :8000
                                   |
                                   v
                            PostgreSQL (Docker)
- Photo never leaves the browser; only points + metadata are sent.
- Python: validation, scale + homography, point -> measurement mapping, API-key check,
  request-size limit, safe errors.
- Spring: /api/health, /api/garments, /api/garments/{id}, /api/measure, /api/sessions;
  forwards /measure to Python and saves to tables `measurement`, `measurement_session`.
- Angular: measurement canvas - user clicks 4 card corners, then garment points.

## Method (how a measurement is computed)
1. Click 4 card corners -> homography maps image pixels to a flat real-world plane (cm).
   (Hartley normalization + convex-quad check added.)
2. Click garment points -> convert to cm using that homography.
3. Distances -> garment measurements (chest, length, shoulder, ...) via `specs/*.json`.
4. Garment -> tailor/body measurement via ease defaults (`specs/ease_defaults.json`).

## Specs
16 garment specs (incl. mens_tshirt, womens_kurti, mens_pants, womens_pants).

## Ground truth test: blue polo (tape measure)
Chest 53, length 72, shoulder 48, hem 52 cm.
Latest app result: chest 53.7, length 72.7, shoulder 45.8 (shoulder is ~2.2 cm off -> investigate
how "shoulder" points are defined/clicked).

## Dev machine
Windows + PowerShell, VS Code. Python 3.14.7, Java Temurin 25.0.5, Node 26.7.0, npm 12.2.2,
Git 2.55, Docker 29.9.2. Repo: https://github.com/mohamedshaheemkp/ClothMate.git
Local path: ...\TannMann\CODE\Clothmate
Each service runs in its own VS Code terminal (python, spring, docker, pwsh for commands).

## Team-leader's original 3 tasks
1. Test with many garment types (men + women), report accuracy.
2. Research how tailors measure; map garment <-> tailor/body measurements.
3. Plan integration into a website (Angular + Spring Boot + PostgreSQL), result shown in a window/iframe.
