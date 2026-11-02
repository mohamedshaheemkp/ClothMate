import json
from pathlib import Path

import pytest

from core.specs import load_spec

SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"


def test_tshirt_spec_loads():
    spec = load_spec(SPECS_DIR / "mens_tshirt.json")
    assert spec["id"] == "mens_tshirt"
    assert len(spec["points"]) == 6


def test_all_existing_specs_are_valid():
    for path in SPECS_DIR.glob("*.json"):
        load_spec(path)


def test_unknown_point_is_rejected(tmp_path):
    bad = {"id": "bad",
           "points": [{"name": "a", "instruction": "x"}],
           "measurements": [{"name": "m", "from": "a", "to": "b", "circumference": False}]}
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError):
        load_spec(path)


def test_duplicate_point_names_are_rejected(tmp_path):
    bad = {"id": "bad",
           "points": [{"name": "a", "instruction": "x"}, {"name": "a", "instruction": "y"}],
           "measurements": []}
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError):
        load_spec(path)