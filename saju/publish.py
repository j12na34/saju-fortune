import json
import os
from datetime import datetime
from pathlib import Path

from .ganzhi import KST
from .validate import validate


def _slot_doc(texts: dict, analysis: dict, slot: str) -> dict:
    try:
        t = texts["slots"][slot]
        color = analysis["slots"][slot]["color"]
        return {"text": t["text"], "color": {"hex": color["hex"], "name": color["name"], "reason": t["reason"]}}
    except KeyError as exc:
        raise ValueError(f"{slot} 슬롯 정보가 부족해요: {exc}") from exc


def _topics_doc(texts: dict, analysis: dict) -> dict:
    """점수·근거는 analysis(코드), 글은 texts["topics"][키]["text"] 에서. 글이 없으면 text 를 생략한다."""
    out = {}
    for key, t in analysis["topics"].items():
        entry = {"label": t["label"], "score": t["score"], "facts": t["facts"]}
        text = texts.get("topics", {}).get(key, {}).get("text")
        if text is not None:
            entry["text"] = text
        out[key] = entry
    return out


def publish(texts: dict, analysis: dict, mode: str, path: Path, now: datetime) -> dict:
    """검증을 통과한 문서만 path 에 저장하고 그 문서를 돌려준다. 실패하면 ValueError 이고 파일은 그대로다.

    full: 문서를 새로 만든다. lunch/evening: 오늘 날짜의 기존 문서에서 해당 슬롯(과 선택적 summary)만 바꾼다.
    색의 hex·name 은 analysis(코드 계산 결과)에서, reason 은 texts 에서 가져온다.
    """
    k = now.replace(tzinfo=KST) if now.tzinfo is None else now.astimezone(KST)
    updated_at = k.isoformat(timespec="seconds")
    if mode == "full":
        try:
            doc = {
                "date": analysis["date"],
                "updated_at": updated_at,
                "ilgin": analysis["ilgin"],
                "overall": texts["overall"],
                "slots": {s: _slot_doc(texts, analysis, s) for s in ("morning", "lunch", "evening")},
                "summary": texts["summary"],
                "topics": _topics_doc(texts, analysis),
            }
        except KeyError as exc:
            raise ValueError(f"항목이 부족해요: {exc}") from exc
    elif mode in ("lunch", "evening"):
        if not path.exists():
            raise ValueError("오늘의 fortune.json 이 아직 없어요 (07시 전체 실행이 먼저 필요해요)")
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("date") != analysis["date"]:
            raise ValueError(f"fortune.json 의 날짜({doc.get('date')})가 오늘({analysis['date']})이 아니에요")
        doc["slots"][mode] = _slot_doc(texts, analysis, mode)
        doc["updated_at"] = updated_at
        if "summary" in texts:
            doc["summary"] = texts["summary"]
    else:
        raise ValueError(f"알 수 없는 mode: {mode}")

    errors = validate(doc)
    if errors:
        raise ValueError("; ".join(errors))
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return doc
