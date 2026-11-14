from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

CARD_CM = [(0, 0), (8.56, 0), (8.56, 5.40), (0, 5.40)]
TSHIRT_CM = {
    "shoulder_left": (10, 10), "shoulder_right": (58, 10),
    "neck_shoulder": (34, 8), "hem_center": (34, 80),
    "chest_left": (14, 25), "chest_right": (54, 25),
    "hem_left": (14, 80), "hem_right": (54, 80),
}


def straight(p):                       # a photo from directly above: 1 cm = 20 pixels
    return {"x": p[0] * 20 + 100, "y": p[1] * 20 + 50}


def good_request():
    names = ["top_left", "top_right", "bottom_right", "bottom_left"]
    return {
        "garment_id": "mens_tshirt",
        "card": {n: straight(p) for n, p in zip(names, CARD_CM)},
        "points": {n: straight(p) for n, p in TSHIRT_CM.items()},
    }


def test_measure_happy_path():
    response = client.post("/v1/measure", json=good_request())
    assert response.status_code == 200
    rows = {r["name"]: r for r in response.json()["measurements"]}
    assert rows["chest"]["flat_cm"] == 40.0
    assert rows["length"]["flat_cm"] == 72.0
    assert rows["shoulder"]["flat_cm"] == 48.0


def test_unknown_garment_is_404():
    body = good_request()
    body["garment_id"] = "nope"
    assert client.post("/v1/measure", json=body).status_code == 404


def test_missing_point_is_422():
    body = good_request()
    del body["points"]["hem_center"]
    response = client.post("/v1/measure", json=body)
    assert response.status_code == 422
    assert "hem_center" in str(response.json()["detail"])


def test_negative_coordinate_is_422():
    body = good_request()
    body["points"]["hem_center"]["x"] = -5
    response = client.post("/v1/measure", json=body)
    assert response.status_code == 422
    assert "hem_center" in str(response.json()["detail"])


def test_unexpected_field_is_422():
    body = good_request()
    body["hack"] = "x"
    assert client.post("/v1/measure", json=body).status_code == 422


def test_bad_garment_id_characters_are_422():
    body = good_request()
    body["garment_id"] = "../secret"
    assert client.post("/v1/measure", json=body).status_code == 422

def test_response_says_which_method_was_used():
    response = client.post("/v1/measure", json=good_request())
    assert response.json()["method"] == "homography"