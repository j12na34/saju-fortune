from datetime import datetime

from .color import slot_color
from .ganzhi import KST, day_pillar_of, pillars
from .wuxing import needed_element

ALL_SLOTS = ["morning", "lunch", "evening"]
# 전체(07:00) 실행에서 각 시간대의 시주를 구할 대표 시각
_REPRESENTATIVE_HOUR = {"morning": 9, "lunch": 15, "evening": 21}


def analyze(chart: dict[str, str], now: datetime, slots: list[str]) -> dict:
    """일진·필요 오행·시간대별 색을 계산한다.

    slots 가 세 시간대 전부면 대표 시각(09/15/21시)의 시주를, 일부면 now 의 시주를 쓴다.
    """
    k = now.replace(tzinfo=KST) if now.tzinfo is None else now.astimezone(KST)
    ilgin = day_pillar_of(k.date())
    element = needed_element(chart, ilgin)
    full = set(slots) == set(ALL_SLOTS)
    result_slots = {}
    for slot in slots:
        when = k.replace(hour=_REPRESENTATIVE_HOUR[slot], minute=0, second=0, microsecond=0) if full else k
        hour_pillar = pillars(when)["hour"]
        result_slots[slot] = {"hour_pillar": hour_pillar, "color": slot_color(element, slot, hour_pillar)}
    return {
        "date": k.date().isoformat(),
        "ilgin": ilgin,
        "chart": chart,
        "needed_element": element,
        "slots": result_slots,
    }
