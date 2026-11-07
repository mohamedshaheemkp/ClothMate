from pathlib import Path

from fastapi import FastAPI, HTTPException

from api.schemas import MeasureRequest
from core.mapping import measure_garment
from core.specs import load_spec

SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"

app = FastAPI(title="ClothMate measurement API")


def load_all_specs():
    specs = {}
    for path in sorted(SPECS_DIR.glob("*.json")):
        spec = load_spec(path)
        specs[spec["id"]] = spec
    return specs


SPECS = load_all_specs()


@app.get("/")
def home():
    return {"service": "ClothMate measurement API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "garments": len(SPECS)}


@app.get("/v1/garments")
def list_garments():
    return [{"id": s["id"], "gender": s.get("gender"), "category": s.get("category")}
            for s in SPECS.values()]


@app.get("/v1/garments/{garment_id}")
def get_garment(garment_id: str):
    spec = SPECS.get(garment_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="Unknown garment")
    return {"id": spec["id"],
            "points": spec["points"],
            "measurements": [m["name"] for m in spec["measurements"]]}


@app.post("/v1/measure")
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