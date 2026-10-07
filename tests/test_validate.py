import copy

from saju.validate import validate

GOOD = {
    "date": "2024-03-10",
    "updated_at": "2024-03-10T07:00:00+09:00",
    "ilgin": "癸酉",
    "overall": "전체 운세",
    "slots": {
        s: {"text": "글", "color": {"hex": "#AABBCC", "name": "이름", "reason": "이유"}}
        for s in ("morning", "lunch", "evening")
    },
    "summary": "요약",
}


def test_accepts_good_doc():
    assert validate(GOOD) == []


def test_rejects_bad_hex():
    bad = copy.deepcopy(GOOD)
    bad["slots"]["lunch"]["color"]["hex"] = "red"
    assert any("hex" in e for e in validate(bad))


def test_rejects_missing_slot():
    bad = copy.deepcopy(GOOD)
    del bad["slots"]["evening"]
    assert any("evening" in e for e in validate(bad))


def test_rejects_empty_text_and_naive_timestamp():
    bad = copy.deepcopy(GOOD)
    bad["summary"] = ""
    bad["updated_at"] = "2024-03-10T07:00:00"
    errors = validate(bad)
    assert any("summary" in e for e in errors)
    assert any("updated_at" in e for e in errors)
