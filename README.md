# saju-fortune

사주 기반 일일 운세와 아이폰 배경화면 색을 `fortune.json`으로 공개합니다.

- 공개 주소: https://j12na34.github.io/saju-fortune/fortune.json
- 설계: `design/`
- 생년월일·출생시는 이 저장소에 없습니다. 계산된 간지만 `chart.json`에 있습니다.

## 웹앱
- 주소: https://j12na34.github.io/saju-fortune/ (연애·재물·직장·건강·대인운, 시간대별 색)
- `docs/index.html` + `app.css` + `app.js` 정적 파일. `fortune.json` 을 읽어 보여 줍니다.
- 점수·근거는 `saju/topics.py` 가 계산하고, 글은 매일 Routines 가 `topics` 에 채웁니다. 글이 없으면 근거 문장을 대신 보여 줍니다.
