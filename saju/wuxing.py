ELEMENT_ORDER = ("木", "火", "土", "金", "水")

STEM_ELEMENT = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
BRANCH_ELEMENT = {
    "寅": "木", "卯": "木", "巳": "火", "午": "火",
    "辰": "土", "戌": "土", "丑": "土", "未": "土",
    "申": "金", "酉": "金", "亥": "水", "子": "水",
}
CHAR_ELEMENT = {**STEM_ELEMENT, **BRANCH_ELEMENT}


def element_of(char: str) -> str:
    return CHAR_ELEMENT[char]


def count_elements(ganzhi_list: list[str]) -> dict[str, int]:
    counts = {e: 0 for e in ELEMENT_ORDER}
    for gz in ganzhi_list:
        for ch in gz:
            counts[CHAR_ELEMENT[ch]] += 1
    return counts


def needed_element(chart: dict[str, str], ilgin: str) -> str:
    """원국 4기둥 + 일진의 오행 개수가 가장 적은 오행. 동률이면 木火土金水 순서에서 앞선 것."""
    counts = count_elements([chart["year"], chart["month"], chart["day"], chart["hour"], ilgin])
    return min(ELEMENT_ORDER, key=lambda e: (counts[e], ELEMENT_ORDER.index(e)))
