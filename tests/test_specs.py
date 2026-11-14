from pathlib import Path

import pytest

from core.specs import SpecError, load_all_specs, validate_spec

SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
SPECS, EASE = load_all_specs(SPECS_DIR)   # fails right here if any spec file is bad
PROFILES = EASE["profiles"]


def good_spec():
    """A tiny valid spec that each test below breaks in exactly one way."""
    return {
        "id": "test_top", "gender": "men", "category": "top",
        "display_name": "Test top", "ease_profile": "knit_top",
        "points": [{"name": "a", "instruction": "x"},
                   {"name": "b", "instruction": "y"}],
        "measurements": [{"name": "m", "from": "a", "to": "b", "kind": "straight"}],
    }


def test_tshirt_spec_loads():
    spec = SPECS["mens_tshirt"]
    required = [p for p in spec["points"] if p.get("required", True)]
    assert len(required) == 8


def test_enough_garments_are_loaded():
    assert len(SPECS) >= 14


def test_good_spec_passes():
    assert validate_spec(good_spec(), PROFILES)["id"] == "test_top"


def test_unknown_point_is_rejected():
    spec = good_spec()
    spec["measurements"][0]["to"] = "zzz"
    with pytest.raises(SpecError):
        validate_spec(spec, PROFILES)


def test_duplicate_point_names_are_rejected():
    spec = good_spec()
    spec["points"].append({"name": "a", "instruction": "again"})
    with pytest.raises(SpecError):
        validate_spec(spec, PROFILES)


def test_unknown_ease_profile_is_rejected():
    spec = good_spec()
    spec["ease_profile"] = "no_such_profile"
    with pytest.raises(SpecError):
        validate_spec(spec, PROFILES)


def test_ease_key_must_exist_in_profile():
    spec = good_spec()
    spec["measurements"] = [{"name": "m", "from": "a", "to": "b",
                             "kind": "flat_circumference", "ease_key": "nope"}]
    with pytest.raises(SpecError):
        validate_spec(spec, PROFILES)