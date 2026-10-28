import math


def distance(p1, p2):
    """Straight-line distance between two points, each given as (x, y)."""
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def pixels_per_cm(corners, card_w_cm=8.56, card_h_cm=5.40):
    """
    Work out how many image pixels equal 1 cm, using the 4 card corners.
    corners = [top_left, top_right, bottom_left, bottom_right], each (x, y).
    """
    if len(corners) != 4:
        raise ValueError("Need exactly 4 card corners")

    top_left, top_right, bottom_left, bottom_right = corners

    width_px = distance(top_left, top_right)
    height_px = distance(top_left, bottom_left)

    if width_px == 0 or height_px == 0:
        raise ValueError("Card corners must be different points")

    scale_from_width = width_px / card_w_cm
    scale_from_height = height_px / card_h_cm

    return (scale_from_width + scale_from_height) / 2