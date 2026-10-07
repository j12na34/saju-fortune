from saju.wuxing import ELEMENT_ORDER, count_elements, needed_element

CHART = {"year": "甲子", "month": "乙丑", "day": "丙寅", "hour": "丁卯"}  # 공개 임의 간지


def test_count_elements_single_pillar():
    assert count_elements(["戊午"]) == {"木": 0, "火": 1, "土": 1, "金": 0, "水": 0}


def test_needed_element_picks_lowest_total():
    # 차트: 木 4(甲乙寅卯), 火 2(丙丁), 土 1(丑), 水 1(子), 金 0. 일진 戊午 -> 土 2, 火 3. 金이 가장 적다.
    assert needed_element(CHART, "戊午") == "金"


def test_needed_element_tie_uses_fixed_order():
    # 차트+일진이 모든 오행 동률(각 1)이 되는 입력: 甲(木)午(火) 己(土)酉(金) 壬(水)... 아래 5기둥 10글자는 각 2점
    chart = {"year": "甲午", "month": "己酉", "day": "壬寅", "hour": "丁丑"}
    # 木: 甲 寅 =2, 火: 午 丁 =2, 土: 己 丑 =2, 金: 酉 =1, 水: 壬 =1 -> 일진 庚子(金1,水1)로 전부 2점 동률
    results = {needed_element(chart, "庚子") for _ in range(100)}
    assert results == {ELEMENT_ORDER[0]}  # 木
