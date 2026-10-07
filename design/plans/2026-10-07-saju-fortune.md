# 사주 일일 운세 자동화 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 하루 3번 사주 기반 운세·행운 색을 만들어 GitHub Pages의 `fortune.json`으로 공개한다.

**Architecture:** `saju/` 파이썬 패키지가 간지·오행·색을 결정적으로 계산하고, CLI가 분석 JSON을 출력한다. Routines 세션이 그 결과로 글을 쓰고 CLI `publish`가 검증 후 `docs/fortune.json`에 저장·푸시한다. Pages는 main의 `/docs`를 공개한다.

**Tech Stack:** Python 3.11+, `lunar_python`(PyPI), pytest, GitHub Pages, Routines.

**Spec:** `design/2026-10-07-saju-fortune-design.md`

## Global Constraints

- 저장소는 공개. 생년월일·출생시는 어떤 파일·테스트·커밋 메시지에도 넣지 않는다. 간지만 `chart.json`에 둔다.
- 사주 계산은 `lunar_python`만 사용. AI는 계산하지 않는다.
- 시간대 경계: 아침 07~12, 점심 12~18, 저녁 18~다음날 07 (KST, `Asia/Seoul`).
- `fortune.json` 필드: `date, updated_at, ilgin, overall, slots{morning,lunch,evening}{text,color{hex,name,reason}}, summary`. hex는 `#RRGGBB`.
- 검증 실패 시 기존 `docs/fortune.json`을 건드리지 않는다.
- 공개 주소: `https://j12na34.github.io/saju-fortune/fortune.json`.
- 사용자(개발 경험 없음)에게 한 단계씩 쉬운 말로 설명한다.

## Review Focus

- 서버 시계가 UTC여도 한국 날짜·시간대로 계산한다 (Task 2, 5).
- 23:00~23:59(자시)의 일주·시주 처리가 한 가지로 고정되어 있다 (Task 2).
- 절기(입춘 등) 경계 시각 전후로 년주·월주가 바뀐다 (Task 2).
- 부분 갱신(lunch/evening)이 다른 시간대 글·색을 지우지 않는다 (Task 5).
- 오행 개수가 동률일 때 항상 같은 색이 나온다 (Task 3).
- 어제 날짜의 `fortune.json` 위에 lunch/evening만 갱신하려 하면 거부한다 (Task 5).

---

### Task 1: 저장소 구조와 GitHub Pages

**Files:**
- Create: `requirements.txt` (`lunar_python==<설치 시점 최신 안정 버전>`, `pytest`), `docs/fortune.json`, `docs/index.html`(한 줄 안내), `scripts/check_public.py`, `tests/test_fortune_file.py`, `.gitignore`
- Modify: `README.md`

**Interfaces:**
- Produces: `docs/fortune.json`(유효한 자리표시자: date `"1970-01-01"`, 색 `#808080`), `scripts/check_public.py` — 인자 없이 실행하면 공개 주소를 GET하고 JSON 필수 키 존재 여부를 검사, 성공 시 exit 0.

- [ ] **Step 1: 실패하는 테스트** — `tests/test_fortune_file.py::test_placeholder_has_required_keys`: `docs/fortune.json`을 읽어 최상위 키 집합이 스펙의 7개와 같고 slots의 3개 키가 모두 `text, color{hex,name,reason}`를 가진다고 assert.
- [ ] **Step 2: 실행해서 실패 확인** — `python -m pytest tests/test_fortune_file.py -v` → FAIL(파일 없음).
- [ ] **Step 3: 구조 파일 생성**, `pip install -r requirements.txt`.
- [ ] **Step 4: 통과 확인** — 같은 명령 → PASS.
- [ ] **Step 5: 커밋** 후 `claude/stoic-galileo-kt0k3s`에 푸시.
- [ ] **Step 6: Pages 켜기 (사용자 작업, 쉬운 말로 안내)** — Pages는 main 브랜치에서만 공개하므로 작업 브랜치를 main에 합쳐야 한다. 합치기(PR 생성·병합)는 사용자에게 먼저 물어보고 진행. 이후 GitHub 저장소 Settings → Pages → Source "Deploy from a branch", Branch `main`, 폴더 `/docs` → Save. 저장소가 공개(Public)인지도 확인.
- [ ] **Step 7: 공개 주소 확인** — `python scripts/check_public.py` → 1~2분 뒤 exit 0. 안 열리면 Pages 배포 상태(Actions 탭)를 함께 확인.

### Task 2: 간지 계산 엔진

**Files:**
- Create: `saju/__init__.py`, `saju/ganzhi.py`, `tests/test_ganzhi.py`

**Interfaces:**
- Produces: `KST = ZoneInfo("Asia/Seoul")`; `def pillars(dt: datetime) -> dict[str, str]` — 키 `year, month, day, hour`, 값은 한자 간지 두 글자. naive datetime은 KST로 간주, aware는 KST로 변환 후 계산. 내부는 `Solar.fromYmdHms(...).getLunar().getEightChar()`; 자시 처리는 `lunar_python` 기본값(23시는 당일 일주 유지/시주만 子)을 그대로 쓰고 테스트로 고정한다.
- Produces: `def day_pillar_of(date: datetime.date) -> str` (일진).

- [ ] **Step 1: 실패하는 테스트** (`tests/test_ganzhi.py`, 날짜는 모두 공개된 일반 날짜):
  - `test_known_date`: `pillars(datetime(2000,1,1,12,0))` == 년 `己卯`, 월 `丙子`, 일 `戊午`, 시 `戊午`.
  - `test_day_cycle_is_60`: 2000-01-01 기준 임의 날짜 5개(예: +1, +59, +60, +365, +10000일)의 일주가 60갑자 순환 계산(`戊午` 인덱스 + 일수 차 mod 60)과 같다. 계산은 테스트 안에 독립 구현.
  - `test_ipchun_boundary`: 2024-02-04 16:00 → 년 `癸卯`, 17:00 → 년 `甲辰` (입춘 16:27 KST).
  - `test_month_boundary`: 같은 입춘 전후 월주가 `乙丑` → `丙寅`.
  - `test_zi_hour`: 2024-03-10 23:30과 2024-03-11 00:30의 시주 지지가 모두 `子`. 일주 결과는 현재 라이브러리 동작을 확인해 그대로 expected에 고정하고 주석으로 "자시 처리 규칙" 명시.
  - `test_utc_aware_input`: `datetime(2024,2,4,7,30,tzinfo=UTC)`(=KST 16:30)의 년주가 `甲辰`이 아니라 `癸卯`가 아님을 확인 → 실제로는 16:30 > 16:27이므로 `甲辰`.
- [ ] **Step 2: 실패 확인** — `python -m pytest tests/test_ganzhi.py -v` → FAIL(모듈 없음).
- [ ] **Step 3: `pillars`, `day_pillar_of` 구현.**
- [ ] **Step 4: 통과 확인.** 값이 다르면 구현이 아니라 기대값 출처(공개 만세력)부터 다시 확인해 사용자에게 보고.
- [ ] **Step 5: 커밋.**

### Task 3: 오행 분석과 색 선택

**Files:**
- Create: `saju/wuxing.py`, `saju/color.py`, `tests/test_wuxing.py`, `tests/test_color.py`

**Interfaces:**
- Consumes: `pillars`, `day_pillar_of` (Task 2).
- Produces (`wuxing.py`): `STEM_ELEMENT`, `BRANCH_ELEMENT`(천간·지지 → `木火土金水`); `def count_elements(ganzhi_list: list[str]) -> dict[str,int]`(각 간지 두 글자 모두 1점); `def needed_element(chart: dict[str,str], ilgin: str) -> str` — 원국 4기둥 + 일진 1기둥의 개수 합이 가장 적은 오행. 동률은 `木,火,土,金,水` 고정 순서에서 앞선 것.
- Produces (`color.py`): `def slot_color(element: str, slot: str, hour_pillar: str) -> dict` — `{"hex","name"}`. 오행별 고정 색상각(木 135, 火 5, 土 40, 金 210(채도 낮음), 水 225(명도 낮음)), 슬롯별 기본 명도 morning 밝음/lunch 중간/evening 어두움, 시주 오행이 필요 오행과 같으면 채도 +, 아니면 기본. `colorsys`로 hex 변환. 이름은 `"{명도 형용사} {오행 색}"` 형식.

- [ ] **Step 1: 실패하는 테스트**:
  - `test_count_elements`: `["戊午"]` → `{土:1, 火:1, ...나머지 0}`.
  - `test_needed_element_picks_lowest`: 가짜 원국(공개 임의 간지)으로 부족 오행이 선택됨.
  - `test_needed_element_tie_is_deterministic`: 동률 입력에서 고정 순서의 첫 오행, 100번 호출해도 동일.
  - `test_slot_colors_same_family`: 같은 element의 세 슬롯 hex를 HSL로 되돌렸을 때 색상각 차이 ≤ 2°, 명도는 morning > lunch > evening.
  - `test_hex_format`: 모든 오행×슬롯 조합이 `^#[0-9A-F]{6}$`.
- [ ] **Step 2: 실패 확인.**
- [ ] **Step 3: 구현.**
- [ ] **Step 4: 통과 확인.**
- [ ] **Step 5: 커밋.**

### Task 4: 원국 생성과 분석 CLI

**Files:**
- Create: `saju/cli.py`, `saju/analysis.py`, `chart.json`(Step 6에서 생성), `tests/test_cli.py`

**Interfaces:**
- Consumes: Tasks 2–3.
- Produces (`analysis.py`): `def analyze(chart: dict, now: datetime, slots: list[str]) -> dict` — `{"date","ilgin","chart","needed_element","slots":{slot:{"hour_pillar","color":{"hex","name"}}}}`. 슬롯 대표 시각은 07:00 전체 실행 시 morning 09:00, lunch 15:00, evening 21:00, 부분 실행(lunch/evening)은 `now`의 시주를 쓴다.
- Produces (`cli.py`): `python -m saju.cli chart --birth "YYYY-MM-DD HH:MM"` → 입력 시각(이미 진태양시 보정된 시각)의 4기둥을 stdout에 JSON 출력(저장하지 않음). `python -m saju.cli analyze --mode full|lunch|evening` → `analyze` 결과를 stdout에 JSON 출력, 현재 시각은 KST 기준, 차트는 `chart.json`.

- [ ] **Step 1: 실패하는 테스트** — `analyze`가 고정 `now`와 가짜 차트에서 기대 JSON 구조·값을 반환하고 `mode=lunch`면 slots에 lunch만 있다. UTC aware `now`와 같은 KST naive `now`의 결과가 같다.
- [ ] **Step 2: 실패 확인.**
- [ ] **Step 3: 구현.**
- [ ] **Step 4: 통과 확인.**
- [ ] **Step 5: 커밋.**
- [ ] **Step 6: 실제 원국 생성 (대화 중 1회)** — 사용자가 알려준 보정 시각으로 `chart` 명령 실행. 결과가 `己卯 壬申 庚戌 壬午`와 일치하는지 확인하고 간지 4개만 `chart.json`에 저장·커밋. 불일치하면 중단하고 사용자에게 보고. 쉘 기록에 날짜가 남지 않도록 일회성 실행으로 하고 커밋 메시지에도 날짜를 쓰지 않는다.

### Task 5: fortune.json 검증과 발행

**Files:**
- Create: `saju/validate.py`, `saju/publish.py`, `tests/test_validate.py`, `tests/test_publish.py`
- Modify: `saju/cli.py`

**Interfaces:**
- Consumes: `analyze` (Task 4).
- Produces: `def validate(doc: dict) -> list[str]` — 오류 메시지 리스트(빈 리스트면 통과). 검사: 7개 최상위 키, 3개 슬롯, 빈 문자열 금지, hex 형식, `updated_at` ISO8601 + 오프셋.
- Produces: `def publish(texts: dict, analysis: dict, mode: str, path: Path, now: datetime) -> dict` — `texts` 형식 `{"overall","summary","slots":{slot:{"text","reason"}}}`. `mode=full`은 문서 전체 새로 생성. `lunch|evening`은 기존 문서의 `date`가 오늘(KST)일 때만 해당 슬롯의 text/color와 `updated_at`만 갱신하고 나머지는 보존, 날짜가 다르면 `ValueError`. 색 hex·name은 `analysis`에서 가져오고 AI는 `reason`만 쓴다. 검증 실패 시 파일을 쓰지 않고 `ValueError`. 쓰기는 임시 파일 후 교체.
- CLI: `python -m saju.cli publish --mode full|lunch|evening --texts <file.json>` (대상 파일 `docs/fortune.json`).

- [ ] **Step 1: 실패하는 테스트**:
  - `test_validate_rejects_bad_hex`, `test_validate_rejects_missing_slot`, `test_validate_accepts_good_doc`.
  - `test_publish_full_writes_valid_file`.
  - `test_publish_partial_keeps_other_slots`: full 후 lunch 갱신 → morning·evening 동일, lunch 변경, `updated_at` 변경.
  - `test_publish_partial_rejects_stale_date`: 어제 날짜 문서 + lunch → `ValueError`, 파일 불변.
  - `test_invalid_texts_leave_file_untouched`: 빈 `summary` → `ValueError`, 파일 바이트 동일.
- [ ] **Step 2: 실패 확인.**
- [ ] **Step 3: 구현.**
- [ ] **Step 4: 통과 확인** — 전체 `python -m pytest -v`.
- [ ] **Step 5: 커밋.**

### Task 6: Routines 3개 예약

**Files:**
- Create: `routines/daily.md`(실행 지침 하나, 모드는 인자로 구분)
- Modify: `README.md`(운영 방법)

**Interfaces:**
- Consumes: CLI `analyze`, `publish` (Tasks 4–5).
- Produces: 예약 3개 — `CRON_TZ=Asia/Seoul 0 7 * * *`(full), `0 12 * * *`(lunch), `0 18 * * *`(evening). 매번 새 세션 방식.

- [ ] **Step 1: `routines/daily.md` 작성** — 순서: `pip install -r requirements.txt` → `analyze --mode <mode>` → 결과의 간지·오행·색만 근거로 texts.json 작성(계산·추측 금지, 색 hex 변경 금지) → `publish` → 실패 시 파일 변경 없이 종료 → `git pull --rebase` 후 main에 푸시.
- [ ] **Step 2: 수동 시험 실행** — 같은 지침으로 지금 한 번 `full` 모드를 직접 돌려 `docs/fortune.json` 생성, 커밋·푸시, `check_public.py`로 공개 확인.
- [ ] **Step 3: 예약 생성** — 사용자에게 시간·내용을 확인받은 뒤 `create_trigger` 3회. 정각 실행은 서버 사정으로 몇 분 늦을 수 있음을 안내(모드는 시계가 아니라 지침 인자로 정하므로 지연돼도 결과는 맞음).
- [ ] **Step 4: 확인** — `list_triggers`로 3개의 다음 실행 시각이 07:00/12:00/18:00 KST인지 확인. 첫 자동 실행 후 공개 주소의 `updated_at`을 함께 확인.
- [ ] **Step 5: 커밋.**

### Task 7: 아이폰 단축어 안내

**Files:**
- Create: `guide/iphone-shortcut.md`

- [ ] **Step 1: 배경화면 변경 가능 여부 먼저 시험(사용자와 함께)** — 단축어 앱에서 "배경화면 설정" 계열 동작이 있는지, 단색 이미지로 실제 바뀌는지 확인하는 3단계짜리 미니 시험을 쉬운 말로 안내.
- [ ] **Step 2: 결과에 따른 본 안내 작성** — 가능하면: URL 내용 가져오기 → 사전에서 값 가져오기(현재 시간대 판단: 시각 기준 morning/lunch/evening) → hex로 단색 이미지 생성 → 배경화면 설정 → `summary` 알림. 불가능하면 대안(이미지를 사진에 저장 후 수동 지정 또는 알림만)을 안내.
- [ ] **Step 3: 자동화 안내** — 단축어 앱의 "개인용 자동화"로 07:05, 12:05, 18:05 시간에 실행, "실행 전 묻기" 끄기.
- [ ] **Step 4: 실제 기기 확인(사용자)** — 예약 실행 후 배경화면과 알림이 바뀌었는지 확인하도록 안내하고 결과를 받는다.
- [ ] **Step 5: 커밋.**
