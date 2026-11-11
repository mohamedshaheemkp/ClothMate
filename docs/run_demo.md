# Run the full demo (4 parts)

You need: Docker Desktop (or a local PostgreSQL), Python 3.12+, Java 17+ with Maven, Node 20+ with Angular CLI.

## 1. Database + measurement service (Docker)
From the repo root:
    docker compose up -d --build
Check: http://localhost:8000/health shows {"status":"ok",...}
(No Docker? Install PostgreSQL, create DB/user "clothmate", run db/schema.sql, then start the Python
service manually: PowerShell `$env:CLOTHMATE_ENV="dev"; uvicorn api.main:app --port 8000`.)

## 2. Spring Boot backend
    cd backend-springboot
    mvn spring-boot:run
Check: http://localhost:8080/api/garments lists 14 garments.

## 3. Angular frontend
Create the app once:
    ng new clothmate-web --routing=false --style=css --ssr=false
    cd clothmate-web
Copy from ../frontend-angular into clothmate-web/src/app/:
    measure.component.ts, app.component.ts (replace), app.config.ts (replace)
Copy proxy.conf.json into clothmate-web/ (next to package.json). If your generated app has
src/app/app.ts instead of app.component.ts, keep that file name and just import MeasureComponent there.
Run:
    ng serve --proxy-config proxy.conf.json
Open http://localhost:4200

## 4. Demo flow
Choose a garment -> choose the photo -> click the 4 card corners (top-left, top-right, bottom-right,
bottom-left; the LONG edge is "top") -> click each garment point -> Calculate.
The result appears and is saved: http://localhost:8080/api/sessions shows the saved sessions.

## Photo tips for a good demo
Garment flat on a plain contrasting surface, card next to it (not on it), camera straight above,
whole garment and card visible, high resolution.

## If something fails
- "Cannot reach the backend": Spring Boot is not running, or you forgot --proxy-config.
- 502 "not reachable": the Python service is down. 502 "misconfigured": API key mismatch.
- Spring Boot cannot connect to DB: check docker compose is up and port 5432 is free.
- 422 messages from the service are readable (wrong corner order, points too close, etc.).
