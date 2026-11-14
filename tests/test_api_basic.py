from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_garments_includes_tshirt():
    ids = [g["id"] for g in client.get("/v1/garments").json()]
    assert "mens_tshirt" in ids


def test_unknown_garment_is_404():
    response = client.get("/v1/garments/nope")
    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown garment"