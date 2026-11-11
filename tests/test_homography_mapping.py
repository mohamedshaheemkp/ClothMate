import math
from pathlib import Path

import pytest

from core.homography import apply_homography, compute_homography
from core.mapping import measure_garment
from core.specs import load_all_specs

SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
SPECS, EASE = load_all_specs(SPECS_DIR)

# A fake camera: converts real table positions (cm) into photo pixels.
# Values are chosen so the photo looks tilted (perspective), not just scaled.
CAMERA = [[38.0, 6.0, 120.0],
          [-4.0, 33.0, 80.0],
          [0.0009, 0.0005, 1.0]]


def to_pixels(cm_point):
    import numpy as np
    return apply_homography(np.array(CAMERA), cm_point)


CARD_CM = [(0, 0), (8.56, 0), (8.56, 5.40), (0, 5.40)]
CARD_PX = [to_pixels(p) for p in CARD_CM]


def test_homography_recovers_known_mapping():
    import numpy as np
    h = compute_homography(CARD_PX, CARD_CM)
    # a point NOT used to build the matrix
    px = to_pixels((4.0, 2.0))
    x, y = apply_homography(h, px)
    assert (x, y) == pytest.approx((4.0, 2.0), abs=1e-6)


def test_tshirt_numbers_survive_tilt():
    """Garment drawn on the table in cm, photographed with a tilted camera."""
    cm = {  # real positions in cm (card is at the origin, garment beside it)
        "shoulder_left": (10, 10), "shoulder_right": (58, 10),
        "neck_shoulder": (30, 8), "hem_center": (34, 80),
        "chest_left": (14, 25), "chest_right": (54, 25),
        "hem_left": (14, 80), "hem_right": (54, 80),
    }
    pts = {k: to_pixels(v) for k, v in cm.items()}
    out = measure_garment(SPECS["mens_tshirt"], EASE, CARD_PX, pts, fit="regular")
    by_name = {m["name"]: m for m in out["measurements"]}
    assert by_name["shoulder"]["flat_cm"] == pytest.approx(48.0, abs=0.2)
    assert by_name["chest"]["flat_cm"] == pytest.approx(40.0, abs=0.2)
    assert by_name["chest"]["garment_circumference_cm"] == pytest.approx(80.0, abs=0.4)
    # regular knit-top chest ease is 8 cm in the draft table
    assert by_name["chest"]["estimated_body_cm"] == pytest.approx(72.0, abs=0.4)
    assert by_name["length"]["flat_cm"] == pytest.approx(math.dist((30, 8), (34, 80)), abs=0.2)
    assert "sleeve_length" not in by_name  # optional sleeve point not given


def test_wrong_corner_order_is_rejected():
    bad = [CARD_PX[0], CARD_PX[2], CARD_PX[1], CARD_PX[3]]
    pts = {p["name"]: (500, 500) for p in SPECS["mens_tshirt"]["points"]}
    with pytest.raises(ValueError):
        measure_garment(SPECS["mens_tshirt"], EASE, bad, pts)


def test_missing_required_point_is_rejected():
    with pytest.raises(ValueError):
        measure_garment(SPECS["mens_tshirt"], EASE, CARD_PX, {})


def test_unknown_point_is_rejected():
    pts = {"not_a_point": (1, 1)}
    with pytest.raises(ValueError):
        measure_garment(SPECS["mens_tshirt"], EASE, CARD_PX, pts)


def test_two_points_on_top_of_each_other_are_rejected():
    pts = {p["name"]: (1000, 1000) for p in SPECS["mens_tshirt"]["points"] if p["required"]}
    with pytest.raises(ValueError):
        measure_garment(SPECS["mens_tshirt"], EASE, CARD_PX, pts)


def test_tiny_reference_is_rejected():
    tiny = [(0, 0), (5, 0), (5, 3), (0, 3)]
    pts = {p["name"]: (100, 100) for p in SPECS["mens_tshirt"]["points"] if p["required"]}
    with pytest.raises(ValueError):
        measure_garment(SPECS["mens_tshirt"], EASE, tiny, pts)


def test_every_spec_loads_and_names_are_consistent():
    assert len(SPECS) >= 14
    for spec in SPECS.values():
        names = {p["name"] for p in spec["points"]}
        for m in spec["measurements"]:
            assert m["from"] in names and m["to"] in names
