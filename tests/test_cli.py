import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from saju.analysis import analyze
from saju.color import slot_color
from saju.ganzhi import KST, pillars
from saju.wuxing import needed_element

CHART = {"year": "甲子", "month": "乙丑", "day": "丙寅", "hour": "丁卯"}
ALL = ["morning", "lunch", "evening"]
ROOT = Path(__file__).resolve().parent.parent


def test_full_analysis_structure_and_values():
    now = datetime(2024, 3, 10, 7, 0, tzinfo=KST)
    a = analyze(CHART, now, ALL)
    assert a["date"] == "2024-03-10"
    assert a["ilgin"] == "癸酉"
    assert a["chart"] == CHART
    el = needed_element(CHART, "癸酉")
    assert a["needed_element"] == el
    assert set(a["slots"]) == set(ALL)
    # 전체 실행은 대표 시각 09:00 / 15:00 / 21:00 의 시주를 쓴다
    for slot, hour in (("morning", 9), ("lunch", 15), ("evening", 21)):
        hp = pillars(datetime(2024, 3, 10, hour, 0))["hour"]
        assert a["slots"][slot]["hour_pillar"] == hp
        assert a["slots"][slot]["color"] == slot_color(el, slot, hp)


def test_partial_analysis_uses_now_hour_pillar_and_only_that_slot():
    now = datetime(2024, 3, 10, 12, 0, tzinfo=KST)
    a = analyze(CHART, now, ["lunch"])
    assert set(a["slots"]) == {"lunch"}
    assert a["slots"]["lunch"]["hour_pillar"] == pillars(now)["hour"]


def test_utc_now_same_as_kst_now():
    kst = datetime(2024, 3, 10, 12, 0, tzinfo=KST)
    utc = datetime(2024, 3, 10, 3, 0, tzinfo=timezone.utc)
    assert analyze(CHART, kst, ["lunch"]) == analyze(CHART, utc, ["lunch"])


def test_cli_chart_prints_four_pillars_without_writing_files():
    out = subprocess.run(
        [sys.executable, "-m", "saju.cli", "chart", "--birth", "2000-01-01 12:00"],
        capture_output=True, text=True, cwd=ROOT, check=True,
    ).stdout
    assert json.loads(out) == {"year": "己卯", "month": "丙子", "day": "戊午", "hour": "戊午"}


def test_cli_publish_full_writes_valid_file(tmp_path):
    texts = {
        "overall": "전체",
        "summary": "요약",
        "slots": {s: {"text": f"{s} 글", "reason": f"{s} 이유"} for s in ALL},
    }
    tf = tmp_path / "texts.json"
    tf.write_text(json.dumps(texts, ensure_ascii=False), encoding="utf-8")
    chart = tmp_path / "chart.json"
    chart.write_text(json.dumps(CHART), encoding="utf-8")
    out = tmp_path / "fortune.json"
    subprocess.run(
        [sys.executable, "-m", "saju.cli", "publish", "--mode", "full", "--texts", str(tf),
         "--chart", str(chart), "--out", str(out)],
        check=True, cwd=ROOT,
    )
    from saju.validate import validate
    assert validate(json.loads(out.read_text(encoding="utf-8"))) == []


def test_cli_publish_invalid_exits_nonzero_and_keeps_file(tmp_path):
    tf = tmp_path / "texts.json"
    tf.write_text(json.dumps({"overall": "", "summary": "", "slots": {}}), encoding="utf-8")
    chart = tmp_path / "chart.json"
    chart.write_text(json.dumps(CHART), encoding="utf-8")
    out = tmp_path / "fortune.json"
    out.write_text("{}", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-m", "saju.cli", "publish", "--mode", "full", "--texts", str(tf),
         "--chart", str(chart), "--out", str(out)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert r.returncode != 0
    assert "publish 실패" in r.stderr
    assert out.read_text(encoding="utf-8") == "{}"
