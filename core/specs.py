import json


def load_spec(path):
    """Read one garment spec file and check that it makes sense."""
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)

    point_names = [p["name"] for p in spec["points"]]

    if len(point_names) != len(set(point_names)):
        raise ValueError(f"{spec['id']}: duplicate point names")

    for m in spec["measurements"]:
        if m["from"] not in point_names or m["to"] not in point_names:
            raise ValueError(
                f"{spec['id']}: measurement '{m['name']}' uses an unknown point"
            )

    return spec