"""Load and validate garment specs (specs/*.json) and the ease table."""
import json
import re
from pathlib import Path

VALID_KINDS = {"straight", "flat_circumference"}
VALID_FITS = ("slim", "regular", "loose")
NAME_PATTERN = re.compile(r"^[a-z0-9_]{1,60}$")
EASE_FILE = "ease_defaults.json"


class SpecError(ValueError):
    """A spec file is invalid."""


def validate_spec(spec, ease_profiles):
    for key in ("id", "gender", "category", "display_name", "ease_profile",
                "points", "measurements"):
        if key not in spec:
            raise SpecError(f"Spec is missing '{key}'")
    if not NAME_PATTERN.match(spec["id"]):
        raise SpecError(f"Bad spec id: {spec['id']!r}")
    if spec["gender"] not in ("men", "women", "unisex"):
        raise SpecError(f"{spec['id']}: bad gender")
    if spec["ease_profile"] not in ease_profiles:
        raise SpecError(f"{spec['id']}: unknown ease_profile")

    names = [p["name"] for p in spec["points"]]
    if len(names) != len(set(names)):
        raise SpecError(f"{spec['id']}: duplicate point names")
    for p in spec["points"]:
        if not NAME_PATTERN.match(p["name"]) or not p.get("instruction"):
            raise SpecError(f"{spec['id']}: bad point {p!r}")

    seen = set()
    profile = ease_profiles[spec["ease_profile"]]
    for m in spec["measurements"]:
        if m["name"] in seen:
            raise SpecError(f"{spec['id']}: duplicate measurement {m['name']}")
        seen.add(m["name"])
        if m["kind"] not in VALID_KINDS:
            raise SpecError(f"{spec['id']}: bad kind in {m['name']}")
        if m["from"] not in names or m["to"] not in names:
            raise SpecError(f"{spec['id']}: {m['name']} uses an unknown point")
        if m.get("ease_key"):
            if m["kind"] != "flat_circumference":
                raise SpecError(f"{spec['id']}: only circumferences have ease")
            for fit in VALID_FITS:
                if m["ease_key"] not in profile.get(fit, {}):
                    raise SpecError(
                        f"{spec['id']}: ease '{m['ease_key']}' missing for {fit}")
    return spec


def load_all_specs(specs_dir):
    """Return (dict of specs by id, ease table dict)."""
    specs_dir = Path(specs_dir)
    ease_table = json.loads((specs_dir / EASE_FILE).read_text(encoding="utf-8"))
    profiles = ease_table["profiles"]

    specs = {}
    for path in sorted(specs_dir.glob("*.json")):
        if path.name == EASE_FILE:
            continue
        spec = validate_spec(json.loads(path.read_text(encoding="utf-8")), profiles)
        if spec["id"] in specs:
            raise SpecError(f"Duplicate spec id {spec['id']}")
        specs[spec["id"]] = spec
    return specs, ease_table
