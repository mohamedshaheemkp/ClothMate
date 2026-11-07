import hmac
import logging
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from api.schemas import MeasureRequest
from core.mapping import measure_garment
from core.specs import load_spec

log = logging.getLogger("clothmate")
logging.basicConfig(level=logging.INFO)

MAX_BODY_BYTES = 100_000  # a real request is a few KB; anything bigger is refused
SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"

app = FastAPI(title="ClothMate measurement API")


def load_all_specs():
    specs = {}
    for path in sorted(SPECS_DIR.glob("*.json")):
        spec = load_spec(path)
        specs[spec["id"]] = spec
    return specs


SPECS = load_all_specs()


def require_api_key(x_api_key: str | None = Header(default=None)):
    """Only callers that know the secret key may use the /v1 endpoints."""
    expected = os.environ.get("CLOTHMATE_API_KEY")
    if not expected:
        if os.environ.get("CLOTHMATE_ENV") == "dev":
            return  # development convenience only
        raise HTTPException(status_code=503, detail="Service not configured")
    if x_api_key is None or not hmac.compare_digest(x_api_key.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.middleware("http")
async def limit_size_and_add_headers(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
        return JSONResponse({"detail": "Request too large"}, status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    log.exception("Unhandled error")  # the details stay in our log, not in the reply
    return JSONResponse({"detail": "Internal error"}, status_code=500)


@app.get("/")
def home():
    return {"service": "ClothMate measurement API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "garments": len(SPECS)}


@app.get("/v1/garments", dependencies=[Depends(require_api_key)])
def list_garments():
    return [{"id": s["id"], "gender": s.get("gender"), "category": s.get("category")}
            for s in SPECS.values()]


@app.get("/v1/garments/{garment_id}", dependencies=[Depends(require_api_key)])
def get_garment(garment_id: str):
    spec = SPECS.get(garment_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="Unknown garment")
    return {"id": spec["id"],
            "points": spec["points"],
            "measurements": [m["name"] for m in spec["measurements"]]}


@app.post("/v1/measure", dependencies=[Depends(require_api_key)])
def measure(req: MeasureRequest):
    spec = SPECS.get(req.garment_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="Unknown garment")

    c = req.card
    corners = [(p.x, p.y) for p in (c.top_left, c.top_right, c.bottom_right, c.bottom_left)]
    points = {name: (p.x, p.y) for name, p in req.points.items()}

    try:
        rows = measure_garment(spec, corners, points, fit=req.fit, method=req.method)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))

    return {"garment_id": spec["id"], "fit": req.fit, "method": req.method,
            "measurements": rows}