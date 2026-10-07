import re
from datetime import datetime

TOP_KEYS = ("date", "updated_at", "ilgin", "overall", "slots", "summary")
SLOTS = ("morning", "lunch", "evening")
TOPICS = ("love", "money", "work", "health", "people")
_HEX = re.compile(r"#[0-9A-Fa-f]{6}")


def _blank(v) -> bool:
    return not isinstance(v, str) or not v.strip()


def _validate_topics(topics) -> list[str]:
    if not isinstance(topics, dict):
        return ["topics 형식이 잘못됐어요"]
    errors = []
    for key in TOPICS:
        t = topics.get(key)
        if not isinstance(t, dict):
            errors.append(f"topics.{key} 가 없어요")
            continue
        if _blank(t.get("label")):
            errors.append(f"topics.{key}.label 이 비어 있어요")
        score = t.get("score")
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
            errors.append(f"topics.{key}.score 는 0~100 정수여야 해요")
        facts = t.get("facts")
        if not isinstance(facts, list) or not facts or any(_blank(f) for f in facts):
            errors.append(f"topics.{key}.facts 가 비어 있어요")
        if "text" in t and _blank(t["text"]):
            errors.append(f"topics.{key}.text 가 비어 있어요")
    return errors


def validate(doc: dict) -> list[str]:
    """fortune.json 형식 검사. 오류 메시지 목록(빈 목록이면 통과)."""
    errors: list[str] = []
    for key in TOP_KEYS:
        if key not in doc:
            errors.append(f"{key} 항목이 없어요")
    for key in ("date", "ilgin", "overall", "summary"):
        if key in doc and _blank(doc[key]):
            errors.append(f"{key} 가 비어 있어요")
    if "updated_at" in doc:
        try:
            if datetime.fromisoformat(doc["updated_at"]).utcoffset() is None:
                errors.append("updated_at 에 시간대(+09:00)가 없어요")
        except (TypeError, ValueError):
            errors.append("updated_at 형식이 잘못됐어요")
    if "topics" in doc:
        errors.extend(_validate_topics(doc["topics"]))
    slots = doc.get("slots")
    if not isinstance(slots, dict):
        return errors
    for slot in SLOTS:
        s = slots.get(slot)
        if not isinstance(s, dict):
            errors.append(f"슬롯 {slot} 이 없어요")
            continue
        if _blank(s.get("text")):
            errors.append(f"{slot}.text 가 비어 있어요")
        color = s.get("color")
        if not isinstance(color, dict):
            errors.append(f"{slot}.color 가 없어요")
            continue
        if not isinstance(color.get("hex"), str) or not _HEX.fullmatch(color["hex"]):
            errors.append(f"{slot}.color.hex 형식이 #RRGGBB 가 아니에요")
        for k in ("name", "reason"):
            if _blank(color.get(k)):
                errors.append(f"{slot}.color.{k} 가 비어 있어요")
    return errors
