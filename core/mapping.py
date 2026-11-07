from core.geometry import distance
from core.homography import apply_homography, compute_homography
from core.units import body_from_garment, circumference_from_flat

CARD_SIZE_CM = (8.56, 5.40)  # width (long edge) and height of a bank card


def check_card_corners(card_corners_px):
    """Raise ValueError if the 4 clicked card corners cannot be a bank card."""
    tl, tr, br, bl = card_corners_px
    top, bottom = distance(tl, tr), distance(bl, br)
    left, right = distance(tl, bl), distance(tr, br)
    if min(top, bottom, left, right) < 20:
        raise ValueError("Card corners are too close together")
    seen_ratio = ((top + bottom) / 2) / ((left + right) / 2)
    expected_ratio = CARD_SIZE_CM[0] / CARD_SIZE_CM[1]
    if not (0.6 * expected_ratio <= seen_ratio <= 1.6 * expected_ratio):
        raise ValueError(
            f"The card corners do not look like a bank card (long/short edge ratio "
            f"{seen_ratio:.2f}, expected about {expected_ratio:.2f}). Click the corners "
            f"in the order top-left, top-right, bottom-right, bottom-left, with the "
            f"long edge as the top."
        )
    return seen_ratio


def to_cm_points(card_corners_px, points_px, method="scale"):
    """Convert clicked photo points into real centimetres on the table.

    card_corners_px: [top_left, top_right, bottom_right, bottom_left] in photo pixels
    points_px: {"point_name": (x, y), ...} in photo pixels
    method: "scale"      one number (pixels per cm); best for photos taken from above
            "homography" also corrects camera tilt; needs a LARGE reference object
    """
    width, height = CARD_SIZE_CM
    tl, tr, br, bl = card_corners_px

    if method == "scale":
        scale = (distance(tl, tr) / width + distance(bl, br) / width
                 + distance(tl, bl) / height + distance(tr, br) / height) / 4
        return {name: (x / scale, y / scale) for name, (x, y) in points_px.items()}

    if method == "homography":
        card_cm = [(0, 0), (width, 0), (width, height), (0, height)]
        h = compute_homography(card_corners_px, card_cm)
        return {name: apply_homography(h, xy) for name, xy in points_px.items()}

    raise ValueError(f"Unknown method: {method}")


def measure_garment(spec, card_corners_px, points_px, fit="regular", method="scale"):
    """Return one result row per measurement defined in the garment spec."""
    needed = [p["name"] for p in spec["points"]]
    missing = [name for name in needed if name not in points_px]
    if missing:
        raise ValueError(f"Missing points for {spec['id']}: {missing}")

    check_card_corners(card_corners_px)

    cm_points = to_cm_points(card_corners_px, points_px, method)

    results = []
    for m in spec["measurements"]:
        flat = distance(cm_points[m["from"]], cm_points[m["to"]])
        row = {"name": m["name"], "flat_cm": round(flat, 1)}
        if m["circumference"]:
            circ = circumference_from_flat(flat)
            row["garment_circumference_cm"] = round(circ, 1)
            ease = m.get("ease_cm", {}).get(fit)
            if ease is not None:
                row["estimated_body_cm"] = round(body_from_garment(circ, ease), 1)
        results.append(row)
    return results