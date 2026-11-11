"""Tilt correction.

The reference object (card or A4 sheet) lies on the same flat surface as the
garment. Its 4 corners are known in the photo (pixels) and in real life (cm).
From those 4 pairs we compute a "homography": a 3x3 matrix that converts any
photo pixel on that surface into real-world centimetres. This also corrects
for a camera that is not perfectly overhead.
"""
import math

import numpy as np


def _normalization_matrix(points):
    """Shift/scale points so the maths is numerically stable."""
    pts = np.asarray(points, dtype=float)
    centroid = pts.mean(axis=0)
    mean_dist = np.mean(np.linalg.norm(pts - centroid, axis=1))
    if mean_dist < 1e-12:
        raise ValueError("Reference corners are all the same point")
    s = math.sqrt(2) / mean_dist
    return np.array([[s, 0, -s * centroid[0]],
                     [0, s, -s * centroid[1]],
                     [0, 0, 1.0]])


def compute_homography(src, dst):
    """Matrix H that maps each src point (x, y) to its dst point (u, v)."""
    if len(src) != 4 or len(dst) != 4:
        raise ValueError("Need exactly 4 source and 4 destination points")

    t_src = _normalization_matrix(src)
    t_dst = _normalization_matrix(dst)

    rows = []
    for (x, y), (u, v) in zip(src, dst):
        xs, ys, _ = t_src @ np.array([x, y, 1.0])
        us, vs, _ = t_dst @ np.array([u, v, 1.0])
        rows.append([-xs, -ys, -1, 0, 0, 0, us * xs, us * ys, us])
        rows.append([0, 0, 0, -xs, -ys, -1, vs * xs, vs * ys, vs])

    # The best solution is the last row of V^T from the SVD (the null space).
    _, _, vt = np.linalg.svd(np.array(rows))
    h_norm = vt[-1].reshape(3, 3)
    h = np.linalg.inv(t_dst) @ h_norm @ t_src

    if abs(h[2, 2]) < 1e-12:
        raise ValueError("Reference corners do not form a usable shape")
    return h / h[2, 2]


def apply_homography(h, point):
    """Convert one (x, y) point using matrix h."""
    x, y = point
    vec = h @ np.array([x, y, 1.0])
    if abs(vec[2]) < 1e-12:
        raise ValueError("Point cannot be converted (degenerate position)")
    return (float(vec[0] / vec[2]), float(vec[1] / vec[2]))
