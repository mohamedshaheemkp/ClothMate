import pytest
import numpy as np
from core.homography import apply_homography


def test_zoom_by_two():
    h = np.array([[2, 0, 0],
                  [0, 2, 0],
                  [0, 0, 1]])
    assert apply_homography(h, (3, 4)) == (6, 8)


def test_shift():
    h = np.array([[1, 0, 5],
                  [0, 1, -2],
                  [0, 0, 1]])
    assert apply_homography(h, (3, 4)) == (8, 2)


def test_divide_by_third_number():
    h = np.array([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, 2]])
    assert apply_homography(h, (4, 6)) == (2, 3)


def test_zero_divisor_is_rejected():
    h = np.array([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, 0]])
    with pytest.raises(ValueError):
        apply_homography(h, (1, 1))