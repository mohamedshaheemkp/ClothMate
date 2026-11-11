"""ClothMate measurement service.

Run:  uvicorn api.main:app --reload
Dev:  set CLOTHMATE_ENV=dev   (skips the API key check; never use in production)
Prod: set CLOTHMATE_API_KEY and CLOTHMATE_CORS_ORIGINS (comma separated)

The service receives ONLY numbers (clicked pixel positions). Photos never
leave the user's browser, so nothing private is uploaded or stored here.
"""
import hmac
import logging
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.schemas import MeasureRequest, MeasureResponse
from core.mapping import measure_garment
from core.specs import load_all_specs

log = logging.getLogger("clothmate")
logging.basicConfig(level=logging.INFO)

MAX_BODY_BYTES = 100_000
SPEC_DIR = Path(os.environ.get("CLOTHMATE_SPEC_DIR",
                               Path(__file__).resolve().parent.parent / "specs"))
SPECS, EASE_TABLE = load_all_specs(SPEC_DIR)  # fails at start-up if a spec is bad

app = FastAPI(title="ClothMate measurement API", version="0.1.0",
              docs_url=None if os.environ.get("CLOTHMATE_ENV") == "prod" else "/docs")

origins = [o.strip() for o in os.environ.get("CLOTHMATE_CORS_ORIGINS", "").split(",") if o.strip()]
if origins:
    app.add_middleware(CORSMiddleware, allow_origins=origins,
                       allow_methods=["GET", "POST"], allow_headers=["X-API-Key", "Content-Type"])


@app.middleware("http")
async def limit_size_and_add_headers(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
        return JSONResponse({"detail": "Request too large"}, status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


def require_api_key(x_api_key: str | None = Header(default=None)):
    """Swap this for the website's own login (JWT) check when you integrate."""
    expected = os.environ.get("CLOTHMATE_API_KEY")
    if not expected:
        if os.environ.get("CLOTHMATE_ENV") == "dev":
            return
        raise HTTPException(status_code=503, detail="Service not configured")
    if x_api_key is None or not hmac.compare_digest(x_api_key.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    log.exception("Unhandled error")  # details stay in the log, not the response
    return JSONResponse({"detail": "Internal error"}, status_code=500)


@app.get("/health")
def health():
    return {"status": "ok", "garments": len(SPECS)}


@app.get("/v1/garments", dependencies=[Depends(require_api_key)])
def list_garments():
    return [{"id": s["id"], "gender": s["gender"], "category": s["category"],
             "display_name": s["display_name"]} for s in SPECS.values()]


@app.get("/v1/garments/{garment_id}", dependencies=[Depends(require_api_key)])
def get_garment(garment_id: str):
    spec = SPECS.get(garment_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="Unknown garment")
    return {"id": spec["id"], "display_name": spec["display_name"],
            "points": spec["points"],
            "measurements": [m["name"] for m in spec["measurements"]]}


@app.post("/v1/measure", response_model=MeasureResponse,
          dependencies=[Depends(require_api_key)])
def measure(req: MeasureRequest):
    spec = SPECS.get(req.garment_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="Unknown garment")
    c = req.card
    corners = [(p.x, p.y) for p in (c.top_left, c.top_right, c.bottom_right, c.bottom_left)]
    points = {name: (p.x, p.y) for name, p in req.points.items()}
    try:
        result = measure_garment(spec, EASE_TABLE, corners, points,
                                 fit=req.fit, reference=req.reference)
    except ValueError as exc:  # our own messages, safe to show
        raise HTTPException(status_code=422, detail=str(exc))
    result["method"] = "scale"
    log.info("measured garment=%s role=%s", req.garment_id, req.user_role)
    return result
