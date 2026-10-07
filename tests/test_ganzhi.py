from datetime import date, datetime, timezone

from saju.ganzhi import day_pillar_of, pillars

SIXTY_STEMS = "甲乙丙丁戊己庚辛壬癸"
SIXTY_BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
SIXTY = [SIXTY_STEMS[i % 10] + SIXTY_BRANCHES[i % 12] for i in range(60)]


def test_known_date():
    assert pillars(datetime(2000, 1, 1, 12, 0)) == {
        "year": "己卯", "month": "丙子", "day": "戊午", "hour": "戊午",
    }


def test_day_cycle_is_60():
    base = date(2000, 1, 1)
    base_idx = SIXTY.index("戊午")
    for delta in (1, 59, 60, 365, 10000):
        d = date.fromordinal(base.toordinal() + delta)
        assert day_pillar_of(d) == SIXTY[(base_idx + delta) % 60]


def test_ipchun_year_boundary():
    # 2024 입춘 = 2월 4일 16:27 KST
    assert pillars(datetime(2024, 2, 4, 16, 0))["year"] == "癸卯"
    assert pillars(datetime(2024, 2, 4, 17, 0))["year"] == "甲辰"


def test_ipchun_month_boundary():
    assert pillars(datetime(2024, 2, 4, 16, 0))["month"] == "乙丑"
    assert pillars(datetime(2024, 2, 4, 17, 0))["month"] == "丙寅"


def test_zi_hour_branch_is_zi_on_both_sides_of_midnight():
    assert pillars(datetime(2024, 3, 10, 23, 30))["hour"][1] == "子"
    assert pillars(datetime(2024, 3, 11, 0, 30))["hour"][1] == "子"


def test_utc_aware_input_converted_to_kst():
    # 07:30 UTC = 16:30 KST, 입춘(16:27) 이후
    assert pillars(datetime(2024, 2, 4, 7, 30, tzinfo=timezone.utc))["year"] == "甲辰"


def test_zi_hour_rule_pinned():
    # 자시 규칙: 23:00~23:59 는 일주를 당일로 유지하고, 시주는 다음 날 기준 子시를 쓴다.
    late = pillars(datetime(2024, 3, 10, 23, 30))
    early = pillars(datetime(2024, 3, 11, 0, 30))
    assert late["day"] == "癸酉" and early["day"] == "甲戌"
    assert late["hour"] == early["hour"] == "甲子"
