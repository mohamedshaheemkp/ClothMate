import pytest
import numpy as np
from pathlib import Path

from core.homography import apply_homography
from core.mapping import CARD_SIZE_CM, measure_garment, to_cm_points
from core.specs import load_spec
from core.mapping import check_card_corners


SPEC = load_spec(Path(__file__).resolve().parent.parent / "specs" / "mens_tshirt.json")

CAMERA = np.array([[38.0, 6.0, 120.0],
                   [-4.0, 33.0, 80.0],
                   [0.0009, 0.0005, 1.0]])
W, H = CARD_SIZE_CM
CARD_CM = [(0, 0), (W, 0), (W, H), (0, H)]

# Where the t-shirt points really are on the table, in cm.
TSHIRT_CM = {
    "shoulder_left": (10, 10), "shoulder_right": (58, 10),
    "neck_shoulder": (34, 8), "hem": (34, 80),
    "chest_left": (14, 25), "chest_right": (54, 25),
}


def photo(cm_point):
    return apply_homography(CAMERA, cm_point)


def test_points_are_converted_back_to_real_cm():
    card_px = [photo(p) for p in CARD_CM]
    points_px = {name: photo(p) for name, p in TSHIRT_CM.items()}
    result = to_cm_points(card_px, points_px)
    assert result["chest_left"] == pytest.approx((14, 25), abs=1e-6)


def test_tshirt_measurements_from_a_tilted_photo():
    card_px = [photo(p) for p in CARD_CM]
    points_px = {name: photo(p) for name, p in TSHIRT_CM.items()}
    rows = {r["name"]: r for r in measure_garment(SPEC, card_px, points_px)}
    assert rows["shoulder"]["flat_cm"] == pytest.approx(48.0, abs=0.1)
    assert rows["length"]["flat_cm"] == pytest.approx(72.0, abs=0.1)
    assert rows["chest_width"]["flat_cm"] == pytest.approx(40.0, abs=0.1)
    assert rows["chest_width"]["garment_circumference_cm"] == pytest.approx(80.0, abs=0.1)
    assert rows["chest_width"]["estimated_body_cm"] == pytest.approx(72.0, abs=0.1)


def test_missing_point_is_rejected():
    card_px = [photo(p) for p in CARD_CM]
    with pytest.raises(ValueError):
        measure_garment(SPEC, card_px, {"chest_left": (100, 100)})



def test_good_card_corners_pass():
    card_px = [photo(p) for p in CARD_CM]
    assert 1.0 < check_card_corners(card_px) < 2.5


def test_card_corners_in_wrong_order_are_rejected():
    card_px = [photo(p) for p in CARD_CM]
    shifted = card_px[1:] + card_px[:1]   # same corners, wrong starting corner
    with pytest.raises(ValueError):
        check_card_corners(shifted)