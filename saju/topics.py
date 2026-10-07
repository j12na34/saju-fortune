from .wuxing import ELEMENT_ORDER, count_elements, element_of, needed_element

TOPIC_KEYS = ("love", "money", "work", "health", "people")
LABELS = {"love": "연애운", "money": "재물운", "work": "직장운", "health": "건강운", "people": "대인운"}

_BASE_SCORE = 60
_MIN, _MAX = 30, 95

_STEM_COMBINE = {frozenset(p) for p in ("甲己", "乙庚", "丙辛", "丁壬", "戊癸")}
_BRANCH_COMBINE = {frozenset(p) for p in ("子丑", "寅亥", "卯戌", "辰酉", "巳申", "午未")}
_BRANCH_CLASH = {frozenset(p) for p in ("子午", "丑未", "寅申", "卯酉", "辰戌", "巳亥")}


class _Tally:
    """점수와 근거 문장을 함께 쌓는다."""

    def __init__(self) -> None:
        self.score = _BASE_SCORE
        self.facts: list[str] = []

    def add(self, delta: int, fact: str) -> None:
        self.score += delta
        self.facts.append(fact)

    def result(self, label: str) -> dict:
        score = max(_MIN, min(_MAX, self.score))
        return {"label": label, "score": score, "facts": self.facts or ["오늘은 특별히 두드러지는 관계가 없어요."]}


def _chars(ilgin: str) -> list[str]:
    return [ilgin[0], ilgin[1]]


def _count(ilgin: str, element: str) -> int:
    return sum(1 for ch in _chars(ilgin) if element_of(ch) == element)


def topic_scores(chart: dict[str, str], ilgin: str) -> dict[str, dict]:
    """일간 기준으로 오늘 일진과 원국의 관계에서 주제별 점수·근거를 계산한다(결정적).

    기준: 일간 오행의 재성(극하는 오행)·관성(극받는 오행)·식상(생하는 오행)·인성(생받는 오행).
    """
    day_stem, day_branch = chart["day"][0], chart["day"][1]
    me = element_of(day_stem)
    i = ELEMENT_ORDER.index(me)
    wealth = ELEMENT_ORDER[(i + 2) % 5]  # 내가 극하는 오행
    power = ELEMENT_ORDER[(i - 2) % 5]  # 나를 극하는 오행
    output = ELEMENT_ORDER[(i + 1) % 5]  # 내가 생하는 오행
    resource = ELEMENT_ORDER[(i - 1) % 5]  # 나를 생하는 오행
    today_stem, today_branch = ilgin[0], ilgin[1]
    stem_combines = frozenset((day_stem, today_stem)) in _STEM_COMBINE
    day_branch_pair = frozenset((day_branch, today_branch))

    money, work, love, health, people = (_Tally() for _ in range(5))

    # 재물
    n = _count(ilgin, wealth)
    if n:
        money.add(8 * n, f"재성({wealth}) 기운이 일진에 {n}글자 들어와 재물 흐름에 힘이 실려요.")
    n = _count(ilgin, me)
    if n:
        money.add(-5 * n, f"일간과 같은 {me} 기운이 {n}글자라 지출이 새기 쉬운 날이에요.")

    # 직장
    n = _count(ilgin, power)
    if n:
        work.add(8 * n, f"관성({power}) 기운이 {n}글자 들어와 책임·평가와 맞닿는 날이에요.")
    n = _count(ilgin, resource)
    if n:
        work.add(4 * n, f"인성({resource}) 기운이 {n}글자라 배움과 도움을 받기 좋아요.")
    n = _count(ilgin, output)
    if n:
        work.add(-5 * n, f"식상({output}) 기운이 {n}글자라 관성을 눌러 말과 표현이 앞서기 쉬워요.")

    # 연애
    if day_branch_pair in _BRANCH_COMBINE:
        love.add(15, f"일지 {day_branch}와 오늘 지지 {today_branch}가 육합이라 마음이 잘 맞물려요.")
    elif day_branch_pair in _BRANCH_CLASH:
        love.add(-15, f"일지 {day_branch}와 오늘 지지 {today_branch}가 충이라 감정이 부딪히기 쉬워요.")
    if stem_combines:
        love.add(10, f"일간 {day_stem}과 오늘 천간 {today_stem}이 합이라 끌림이 생기는 날이에요.")
    n = _count(ilgin, "木") + _count(ilgin, "火")
    if n and me not in ("木", "火"):
        love.add(3 * n, f"木·火의 따뜻한 기운이 {n}글자 들어와 분위기가 부드러워요.")

    # 건강
    need = needed_element(chart, ilgin)
    n = _count(ilgin, need)
    if n:
        health.add(10 * n, f"원국에서 가장 적은 {need} 기운을 일진이 {n}글자 채워 줘요.")
    else:
        health.add(0, f"가장 적은 {need} 기운은 오늘 채워지지 않아 컨디션 관리를 가볍게 챙기면 좋아요.")
    counts = count_elements([chart["year"], chart["month"], chart["day"], chart["hour"], ilgin])
    if counts[me] >= 4:
        health.add(-8, f"{me} 기운이 {counts[me]}개로 치우쳐 있어 무리하지 않는 편이 좋아요.")

    # 대인
    if stem_combines:
        people.add(10, f"오늘 천간 {today_stem}이 일간 {day_stem}과 합이라 사람들과 잘 어울려요.")
    for pillar in ("year", "month", "day", "hour"):
        b = chart[pillar][1]
        pair = frozenset((b, today_branch))
        if pair in _BRANCH_COMBINE:
            people.add(6, f"오늘 지지 {today_branch}가 원국 {b}와 육합이라 인연이 닿기 쉬워요.")
        elif pair in _BRANCH_CLASH:
            people.add(-6, f"오늘 지지 {today_branch}가 원국 {b}와 충이라 말투를 조심하면 좋아요.")
    n = _count(ilgin, me)
    if n:
        people.add(4 * n, f"일간과 같은 {me} 기운(비겁)이 {n}글자라 동료·친구의 힘을 얻어요.")

    return {
        "love": love.result(LABELS["love"]),
        "money": money.result(LABELS["money"]),
        "work": work.result(LABELS["work"]),
        "health": health.result(LABELS["health"]),
        "people": people.result(LABELS["people"]),
    }
