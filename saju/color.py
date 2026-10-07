import colorsys

from .wuxing import element_of

# 오행별 (색상각, 기본 채도, 색 이름)
_BASE = {
    "木": (135, 0.50, "초록"),
    "火": (5, 0.70, "빨강"),
    "土": (40, 0.50, "황토"),
    "金": (210, 0.20, "은회색"),
    "水": (225, 0.55, "남색"),
}
# 시간대별 (명도, 이름 앞에 붙는 말)
_SLOT = {
    "morning": (0.72, "연한 "),
    "lunch": (0.55, ""),
    "evening": (0.38, "짙은 "),
}
_MATCH_BOOST = 0.10


def slot_color(element: str, slot: str, hour_pillar: str) -> dict:
    """같은 오행 계열에서 시간대별 명도를 달리한 색. 시주에 필요한 오행이 있으면 채도를 높인다."""
    hue, sat, name = _BASE[element]
    light, prefix = _SLOT[slot]
    if any(element_of(ch) == element for ch in hour_pillar):
        sat = min(1.0, sat + _MATCH_BOOST)
    r, g, b = colorsys.hls_to_rgb(hue / 360, light, sat)
    hex_ = "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))
    return {"hex": hex_, "name": f"{prefix}{name}"}
