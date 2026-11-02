import numpy as np


def apply_homography(h, point):
    """Convert one (x, y) point using the 3x3 matrix h."""
    x, y = point
    vec = h @ np.array([x, y, 1.0])
    if abs(vec[2]) < 1e-12:
        raise ValueError("Point cannot be converted (degenerate position)")
    return (float(vec[0] / vec[2]), float(vec[1] / vec[2]))

def compute_homography(src, dst):
    """Find the 3x3 matrix that maps each src point (x, y) to its dst point (u, v)."""
    if len(src) != 4 or len(dst) != 4:
        raise ValueError("Need exactly 4 source and 4 destination points")

    rows = []
    for (x, y), (u, v) in zip(src, dst):
        rows.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        rows.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])

    a = np.array(rows, dtype=float)
    _, _, vt = np.linalg.svd(a)
    h = vt[-1].reshape(3, 3)

    if abs(h[2, 2]) < 1e-12:
        raise ValueError("Corners do not form a usable shape")
    return h / h[2, 2]