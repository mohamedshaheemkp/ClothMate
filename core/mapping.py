"""Turn clicked points into garment and tailor (body) measurements."""
import math

from core.homography import apply_homography, compute_homography

# Real size in cm of the reference object. The "top" edge (top_left ->
# top_right) is always the LONG edge.
REFERENCE_OBJECTS = {
    "card": (8.56, 5.40),   # ISO bank card
    "a4": (29.7, 21.0),     # A4 sheet, landscape
}

MIN_SIDE_PX = 20          # reference corners closer than this are rejected
MIN_VALUE_CM = 0.5        # two points almost on top of each other
MAX_VALUE_CM = 300.0
LOW_RES_CM_PER_PX = 0.08  # coarser than this: a 3 px click error ~ 0.24 cm
TILT_WARN_RATIO = 1.15
LARGE_GARMENT_CM = 70.0


def _dist(a, b):
    return math.dist(a, b)


def check_reference_corners(corners, ref_w_cm, ref_h_cm):
    """corners: [top_left, top_right, bottom_right, bottom_left] in pixels.
    Raises ValueError if they cannot be the 4 corners of the reference.
    Returns (top, bottom, left, right) side lengths in pixels."""
    if len(corners) != 4:
        raise ValueError("Exactly 4 reference corners are required")
    for x, y in corners:
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError("Reference corners must be finite numbers")

    tl, tr, br, bl = corners
    top, bottom = _dist(tl, tr), _dist(bl, br)
    left, right = _dist(tl, bl), _dist(tr, br)
    if min(top, bottom, left, right) < MIN_SIDE_PX:
        raise ValueError("Reference corners are too close together")

    # Convex quadrilateral: cross products of consecutive edges share a sign.
    signs = []
    ring = [tl, tr, br, bl]
    for i in range(4):
        a, b, c = ring[i], ring[(i + 1) % 4], ring[(i + 2) % 4]
        cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        signs.append(cross)
    if not (all(s > 0 for s in signs) or all(s < 0 for s in signs)):
        raise ValueError(
            "Reference corners are in the wrong order. Click: top-left, "
            "top-right, bottom-right, bottom-left")

    expected = ref_w_cm / ref_h_cm
    seen = ((top + bottom) / 2) / ((left + right) / 2)
    if not (expected * 0.6 <= seen <= expected * 1.6):
        raise ValueError(
            "Reference corners do not match the reference shape. Check the "
            "click order and that the long edge is the 'top' edge")
    return top, bottom, left, right


def measure_garment(spec, ease_table, card_corners_px, points_px,
                    fit="regular", reference="card"):
    """
    spec:            one garment spec (dict from specs/*.json)
    card_corners_px: [top_left, top_right, bottom_right, bottom_left] (x, y)
    points_px:       {point_name: (x, y)} in the same pixel coordinates
    Returns a dict with measurements, warnings and the scale.
    """
    if reference not in REFERENCE_OBJECTS:
        raise ValueError("Unknown reference object")
    if fit not in ("slim", "regular", "loose"):
        raise ValueError("Unknown fit")
    ref_w, ref_h = REFERENCE_OBJECTS[reference]

    # --- check the points match the spec -------------------------------
    known = {p["name"]: p for p in spec["points"]}
    unknown = sorted(set(points_px) - set(known))
    if unknown:
        raise ValueError(f"Unknown points for {spec['id']}: {unknown}")
    missing = sorted(n for n, p in known.items()
                     if p.get("required", True) and n not in points_px)
    if missing:
        raise ValueError(f"Missing points for {spec['id']}: {missing}")

    top, bottom, left, right = check_reference_corners(card_corners_px, ref_w, ref_h)

    # --- pixels -> centimetres on the table surface ----------------------
    plane_corners = [(0.0, 0.0), (ref_w, 0.0), (ref_w, ref_h), (0.0, ref_h)]
    h = compute_homography(card_corners_px, plane_corners)
    cm_points = {name: apply_homography(h, xy) for name, xy in points_px.items()}

    warnings = []
    cm_per_px = ref_w / max(top, bottom)
    if cm_per_px > LOW_RES_CM_PER_PX:
        warnings.append(
            f"Low resolution: 1 pixel is about {cm_per_px:.2f} cm. Move the "
            "camera closer or use a higher-resolution photo.")
    tilt = max(max(top, bottom) / min(top, bottom),
               max(left, right) / min(left, right))
    if tilt > TILT_WARN_RATIO:
        warnings.append(
            "The camera looks tilted. It was corrected, but a photo taken "
            "from directly above is more accurate.")
    if len(cm_points) >= 2:
        extent = max(_dist(a, b) for a in cm_points.values()
                     for b in cm_points.values())
        if reference == "card" and extent > LARGE_GARMENT_CM:
            warnings.append(
                "Large garment with a small reference object: accuracy "
                "drops. Use an A4 sheet as the reference.")

    # --- measurements -----------------------------------------------------
    profile = ease_table["profiles"][spec["ease_profile"]][fit]
    results = []
    for m in spec["measurements"]:
        if m["from"] not in cm_points or m["to"] not in cm_points:
            continue  # uses an optional point that was not given
        flat = _dist(cm_points[m["from"]], cm_points[m["to"]])
        if flat < MIN_VALUE_CM or flat > MAX_VALUE_CM:
            raise ValueError(
                f"'{m['name']}' came out as {flat:.1f} cm, which is not "
                "plausible. Check the clicked points")
        row = {
            "name": m["name"],
            "tailor_measure": m["tailor_measure"],
            "flat_cm": round(flat, 1),
            "garment_circumference_cm": None,
            "ease_cm": None,
            "estimated_body_cm": None,
        }
        if m["kind"] == "flat_circumference":
            circ = flat * 2
            row["garment_circumference_cm"] = round(circ, 1)
            if m.get("ease_key"):
                ease = profile[m["ease_key"]]
                row["ease_cm"] = ease
                row["estimated_body_cm"] = round(circ - ease, 1)
        results.append(row)

    return {
        "garment_id": spec["id"],
        "fit": fit,
        "reference": reference,
        "cm_per_pixel_at_reference": round(cm_per_px, 4),
        "measurements": results,
        "warnings": warnings,
        "ease_status": ease_table.get("_status", ""),
    }
