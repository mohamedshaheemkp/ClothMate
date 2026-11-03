from core.geometry import distance
from core.homography import apply_homography, compute_homography
from core.units import body_from_garment, circumference_from_flat

CARD_SIZE_CM = (8.56, 5.40)


def to_cm_points(card_corners_px, points_px):
    """Convert clicked photo points into real centimetres on the table."""
    width, height = CARD_SIZE_CM
    card_cm = [(0, 0), (width, 0), (width, height), (0, height)]
    h = compute_homography(card_corners_px, card_cm)
    return {name: apply_homography(h, xy) for name, xy in points_px.items()}


def measure_garment(spec, card_corners_px, points_px, fit="regular"):
    """Return one result row per measurement defined in the garment spec."""
    needed = [p["name"] for p in spec["points"]]
    missing = [name for name in needed if name not in points_px]
    if missing:
        raise ValueError(f"Missing points for {spec['id']}: {missing}")

    cm_points = to_cm_points(card_corners_px, points_px)

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