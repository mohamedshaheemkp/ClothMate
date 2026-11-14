import math
from pathlib import Path

import numpy as np
import pytest

from core.homography import apply_homography
from core.mapping import REFERENCE_OBJECTS, check_reference_corners, measure_garment
from core.specs import load_all_specs

SPECS, EASE = load_all_specs(Path(__file__).resolve().parent.parent / "specs")
SPEC = SPECS["mens_tshirt"]

# A fake tilted camera: real table position (cm) -> photo pixel.
CAMERA = np.array([[38.0, 6.0, 120.0],
                   [-4.0, 33.0, 80.0],
                   [0.0009, 0.0005, 1.0]])
W, H = REFERENCE_OBJECTS["card"]
CARD_CM = [(0, 0), (W, 0), (W, H), (0, H)]

# Where the t-shirt points really are on the table, in cm.
TSHIRT_CM = {
    "shoulder_left": (10, 10), "shoulder_right": (58, 10),
    "neck_shoulder": (34, 8), "hem_center": (34, 80),
    "chest_left": (14, 25), "chest_right": (54, 25),
    "hem_left": (14, 80), "hem_right": (54, 80),
}


def photo(cm_point):
    return apply_homography(CAMERA, cm_point)


def straight(cm_point, px_per_cm):    # photo from directly above
    return (cm_point[0] * px_per_cm + 100, cm_point[1] * px_per_cm + 50)


CARD_PX = [photo(p) for p in CARD_CM]
POINTS_PX = {name: photo(p) for name, p in TSHIRT_CM.items()}


def rows_for(fit="regular", points=POINTS_PX):
    result = measure_garment(SPEC, EASE, CARD_PX, points, fit=fit)
    return {r["name"]: r for r in result["measurements"]}


def test_tilted_photo_gives_correct_cm():
    rows = rows_for()
    assert rows["shoulder"]["flat_cm"] == pytest.approx(48.0, abs=0.1)
    assert rows["length"]["flat_cm"] == pytest.approx(72.0, abs=0.1)
    assert rows["chest"]["flat_cm"] == pytest.approx(40.0, abs=0.1)


def test_chest_circumference_and_body_estimate():
    chest = rows_for()["chest"]
    assert chest["garment_circumference_cm"] == pytest.approx(80.0, abs=0.2)
    assert chest["ease_cm"] == 8                      # knit_top, regular
    assert chest["estimated_body_cm"] == pytest.approx(72.0, abs=0.2)


def test_fit_changes_the_body_estimate():
    slim = rows_for("slim")["chest"]
    loose = rows_for("loose")["chest"]
    assert slim["ease_cm"] == 4
    assert loose["ease_cm"] == 14
    assert slim["estimated_body_cm"] > loose["estimated_body_cm"]


def test_unknown_fit_is_rejected():
    with pytest.raises(ValueError):
        measure_garment(SPEC, EASE, CARD_PX, POINTS_PX, fit="tight")


def test_unknown_reference_is_rejected():
    with pytest.raises(ValueError):
        measure_garment(SPEC, EASE, CARD_PX, POINTS_PX, reference="coin")


def test_optional_sleeve_point_adds_sleeve_length():
    assert "sleeve_length" not in rows_for()
    with_sleeve = dict(POINTS_PX, sleeve_end=photo((2, 30)))
    rows = rows_for(points=with_sleeve)
    assert rows["sleeve_length"]["flat_cm"] == pytest.approx(
        math.dist((10, 10), (2, 30)), abs=0.2)


def test_good_card_corners_return_side_lengths():
    top, bottom, left, right = check_reference_corners(CARD_PX, W, H)
    assert top > left and bottom > right      # the long edge is the top edge


def test_card_corners_with_wrong_starting_corner_are_rejected():
    shifted = CARD_PX[1:] + CARD_PX[:1]       # same corners, wrong starting corner
    with pytest.raises(ValueError):
        check_reference_corners(shifted, W, H)


def test_low_resolution_adds_a_warning():
    card = [straight(p, 5) for p in CARD_CM]  # only 5 pixels per cm
    points = {n: straight(p, 5) for n, p in TSHIRT_CM.items()}
    result = measure_garment(SPEC, EASE, card, points)
    assert any("Low resolution" in w for w in result["warnings"])


def test_large_garment_with_a_card_adds_a_warning():
    result = measure_garment(SPEC, EASE, CARD_PX, POINTS_PX)
    assert any("Large garment" in w for w in result["warnings"])
    