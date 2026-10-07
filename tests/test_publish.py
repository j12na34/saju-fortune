import json
from datetime import datetime

import pytest

from saju.analysis import ALL_SLOTS, analyze
from saju.ganzhi import KST
from saju.publish import publish
from saju.validate import validate

CHART = {"year": "甲子", "month": "乙丑", "day": "丙寅", "hour": "丁卯"}


def _texts(slots, summary="요약"):
    return {
        "overall": "전체",
        "summary": summary,
        "slots": {s: {"text": f"{s} 글", "reason": f"{s} 이유"} for s in slots},
    }


def _full(path, day=10):
    now = datetime(2024, 3, day, 7, 0, tzinfo=KST)
    return publish(_texts(ALL_SLOTS), analyze(CHART, now, ALL_SLOTS), "full", path, now)


def test_publish_full_writes_valid_file(tmp_path):
    path = tmp_path / "fortune.json"
    _full(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert validate(doc) == []
    assert doc["date"] == "2024-03-10" and doc["ilgin"] == "癸酉"


def test_publish_partial_keeps_other_slots(tmp_path):
    path = tmp_path / "fortune.json"
    before = _full(path)
    now = datetime(2024, 3, 10, 12, 0, tzinfo=KST)
    t = _texts(["lunch"], summary="새 요약")
    after = publish(t, analyze(CHART, now, ["lunch"]), "lunch", path, now)
    assert after["slots"]["morning"] == before["slots"]["morning"]
    assert after["slots"]["evening"] == before["slots"]["evening"]
    assert after["slots"]["lunch"]["text"] == "lunch 글"
    assert after["updated_at"] != before["updated_at"]
    assert after["summary"] == "새 요약"
    assert json.loads(path.read_text(encoding="utf-8")) == after


def test_publish_partial_rejects_stale_date(tmp_path):
    path = tmp_path / "fortune.json"
    _full(path, day=9)
    original = path.read_bytes()
    now = datetime(2024, 3, 10, 12, 0, tzinfo=KST)
    with pytest.raises(ValueError):
        publish(_texts(["lunch"]), analyze(CHART, now, ["lunch"]), "lunch", path, now)
    assert path.read_bytes() == original


def test_publish_partial_without_existing_file_rejected(tmp_path):
    now = datetime(2024, 3, 10, 12, 0, tzinfo=KST)
    with pytest.raises(ValueError):
        publish(_texts(["lunch"]), analyze(CHART, now, ["lunch"]), "lunch", tmp_path / "none.json", now)


def test_invalid_texts_leave_file_untouched(tmp_path):
    path = tmp_path / "fortune.json"
    _full(path)
    original = path.read_bytes()
    now = datetime(2024, 3, 10, 18, 0, tzinfo=KST)
    with pytest.raises(ValueError):
        publish(_texts(ALL_SLOTS, summary=""), analyze(CHART, now, ALL_SLOTS), "full", path, now)
    assert path.read_bytes() == original
