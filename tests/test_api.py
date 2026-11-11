import os

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
os.environ["CLOTHMATE_ENV"] = "dev"
os.environ.pop("CLOTHMATE_API_KEY", None)

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402

client = TestClient(app)
CARD = {"top_left": {"x": 100, "y": 100}, "top_right": {"x": 400, "y": 100},
        "bottom_right": {"x": 400, "y": 289}, "bottom_left": {"x": 100, "y": 289}}


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_list_and_get_garments():
    assert len(client.get("/v1/garments").json()) >= 14
    assert client.get("/v1/garments/mens_tshirt").status_code == 200
    assert client.get("/v1/garments/nope").status_code == 404


def test_measure_happy_path():
    pts = {"shoulder_left": {"x": 500, "y": 300}, "shoulder_right": {"x": 1200, "y": 300},
           "neck_shoulder": {"x": 850, "y": 280}, "hem_center": {"x": 850, "y": 1500},
           "chest_left": {"x": 540, "y": 600}, "chest_right": {"x": 1160, "y": 600},
           "hem_left": {"x": 540, "y": 1500}, "hem_right": {"x": 1160, "y": 1500}}
    r = client.post("/v1/measure", json={"garment_id": "mens_tshirt", "card": CARD, "points": pts})
    assert r.status_code == 200, r.text
    assert r.json()["measurements"]


def test_bad_input_rejected():
    assert client.post("/v1/measure", json={"garment_id": "mens_tshirt"}).status_code == 422
    r = client.post("/v1/measure", json={"garment_id": "../etc", "card": CARD, "points": {}})
    assert r.status_code == 422
    bad = dict(CARD, top_left={"x": -5, "y": 0})
    assert client.post("/v1/measure", json={"garment_id": "mens_tshirt", "card": bad, "points": {}}).status_code == 422
