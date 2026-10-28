import pytest
from core.geometry import distance, pixels_per_cm


def test_distance_345_triangle():
    assert distance((0, 0), (3, 4)) == 5


def test_distance_same_point_is_zero():
    assert distance((7, 7), (7, 7)) == 0


def test_pixels_per_cm_exact_card():
    # A card drawn at exactly 10 pixels per cm
    corners = [(0, 0), (85.6, 0), (0, 54.0), (85.6, 54.0)]
    assert pixels_per_cm(corners) == pytest.approx(10)


def test_pixels_per_cm_rejects_wrong_corner_count():
    with pytest.raises(ValueError):
        pixels_per_cm([(0, 0), (1, 1)])