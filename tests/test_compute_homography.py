import pytest
import numpy as np
from core.homography import compute_homography, apply_homography

CARD_CM = [(0, 0), (8.56, 0), (8.56, 5.40), (0, 5.40)]

# A pretend tilted camera: it turns real table positions into photo pixels.
CAMERA = np.array([[38.0, 6.0, 120.0],
                   [-4.0, 33.0, 80.0],
                   [0.0009, 0.0005, 1.0]])


def to_pixels(cm_point):
    return apply_homography(CAMERA, cm_point)


def test_square_maps_to_square():
    pixels = [(0, 0), (100, 0), (100, 100), (0, 100)]
    cm = [(0, 0), (10, 0), (10, 10), (0, 10)]
    h = compute_homography(pixels, cm)
    assert apply_homography(h, (50, 50)) == pytest.approx((5, 5), abs=1e-6)


def test_corners_map_to_their_targets():
    card_px = [to_pixels(p) for p in CARD_CM]
    h = compute_homography(card_px, CARD_CM)
    for px, cm in zip(card_px, CARD_CM):
        assert apply_homography(h, px) == pytest.approx(cm, abs=1e-6)


def test_tilted_photo_recovers_real_position():
    card_px = [to_pixels(p) for p in CARD_CM]
    h = compute_homography(card_px, CARD_CM)
    photo_point = to_pixels((4.0, 2.0))   # a point we did NOT use to build h
    assert apply_homography(h, photo_point) == pytest.approx((4.0, 2.0), abs=1e-6)


def test_wrong_number_of_points_is_rejected():
    with pytest.raises(ValueError):
        compute_homography([(0, 0)] * 3, [(0, 0)] * 3)