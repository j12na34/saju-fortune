from saju.topics import TOPIC_KEYS, topic_scores

CHART = {"year": "己卯", "month": "壬申", "day": "庚戌", "hour": "壬午"}


def test_keys_and_range_for_every_ganzhi():
    stems, branches = "甲乙丙丁戊己庚辛壬癸", "子丑寅卯辰巳午未申酉戌亥"
    for i in range(60):
        r = topic_scores(CHART, stems[i % 10] + branches[i % 12])
        assert tuple(r) == TOPIC_KEYS
        for t in r.values():
            assert 30 <= t["score"] <= 95 and t["facts"] and t["label"]


def test_deterministic():
    assert topic_scores(CHART, "乙卯") == topic_scores(CHART, "乙卯")


def test_yi_mao_day_is_good_for_love_and_money():
    r = topic_scores(CHART, "乙卯")  # 乙庚합, 卯戌합, 木 두 글자
    assert r["love"]["score"] == 60 + 15 + 10 + 6 and r["love"]["score"] > 80
    assert r["money"]["score"] == 60 + 16
    assert r["people"]["score"] > 70


def test_clash_lowers_love():
    r = topic_scores(CHART, "甲辰")  # 辰戌충
    assert r["love"]["score"] < 60
    assert any("충" in f for f in r["love"]["facts"])
