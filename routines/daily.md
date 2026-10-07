# 매일 운세 갱신 지침 (Routines 가 읽는 문서)

실행 모드는 이 지침을 부른 메시지가 정한다: `full`(07:00), `lunch`(12:00), `evening`(18:00).
시계가 아니라 **모드**로 어떤 시간대를 갱신할지 정하므로, 실행이 조금 늦어도 결과는 같다.

## 순서

1. `git checkout main && git pull origin main`
2. `bash scripts/setup.sh` (실패하면 여기서 멈추고 아무것도 바꾸지 않는다)
3. `. .venv/bin/activate && python -m saju.cli analyze --mode <모드>` 로 분석 결과를 얻는다.
4. 분석 결과(일진, 시주, 필요 오행, 색)만 근거로 `texts.json`(저장소 밖 임시 위치)을 쓴다.
   - 간지·오행·색을 직접 계산하거나 바꾸지 않는다. 색 hex·name 은 코드가 정한 값을 그대로 쓴다.
   - 쉬운 한국어, 따뜻하지만 단정하지 않는 어조. 건강·재물 등을 단정적으로 예언하지 않는다.
   - `reason` 은 "필요 오행이 ○이고 이 시간대 시주가 ○이라서 ○색 계열" 처럼 분석 결과의 사실로 설명한다.
   - 형식 (`full`):
     `{"overall": "...", "summary": "알림용 한두 줄", "slots": {"morning": {"text": "...", "reason": "..."}, "lunch": {...}, "evening": {...}}}`
   - `full` 일 때는 `topics` 도 쓴다: `"topics": {"love": {"text": "..."}, "money": {...}, "work": {...}, "health": {...}, "people": {...}}`.
     분석 결과의 `topics.<키>.facts` 와 `score` 만 근거로 2~3문장. 점수·근거를 바꾸지 않고, 건강·재물·연애를 단정하지 않는다.
   - 형식 (`lunch`/`evening`): `slots` 에 해당 시간대만. `summary` 는 바꿀 때만 넣는다.
5. `python -m saju.cli publish --mode <모드> --texts <texts.json>`
   - 실패 메시지가 나오면 파일은 그대로다. texts 를 고쳐서 한 번만 다시 시도하고, 그래도 실패하면 종료한다.
6. 성공하면 `git add docs/fortune.json && git commit -m "fortune: <날짜> <모드>" && git pull --rebase origin main && git push origin main`
7. 마지막에 `python scripts/check_public.py` 는 배포 지연이 있으니 실패해도 오류로 보지 않는다.
