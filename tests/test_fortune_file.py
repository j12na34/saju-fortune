import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOP_KEYS = {"date", "updated_at", "ilgin", "overall", "slots", "summary"}


def test_placeholder_has_required_keys():
    doc = json.loads((ROOT / "docs" / "fortune.json").read_text(encoding="utf-8"))
    assert TOP_KEYS <= set(doc) <= TOP_KEYS | {"topics"}
    assert set(doc["slots"]) == {"morning", "lunch", "evening"}
    for slot in doc["slots"].values():
        assert set(slot) == {"text", "color"}
        assert set(slot["color"]) == {"hex", "name", "reason"}
