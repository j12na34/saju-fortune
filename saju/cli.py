import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .analysis import ALL_SLOTS, analyze
from .publish import publish
from .ganzhi import KST, pillars

ROOT = Path(__file__).resolve().parent.parent
CHART_PATH = ROOT / "chart.json"
OUT_PATH = ROOT / "docs" / "fortune.json"
MODE_SLOTS = {"full": ALL_SLOTS, "lunch": ["lunch"], "evening": ["evening"]}


def _dump(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="saju")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("chart", help="입력 시각의 4기둥을 출력(저장 안 함)")
    c.add_argument("--birth", required=True, help='"YYYY-MM-DD HH:MM" (진태양시 보정이 끝난 시각)')

    a = sub.add_parser("analyze", help="오늘 분석 결과를 JSON 으로 출력")
    a.add_argument("--mode", choices=sorted(MODE_SLOTS), required=True)

    u = sub.add_parser("publish", help="글 파일을 검증하고 docs/fortune.json 에 저장")
    u.add_argument("--mode", choices=sorted(MODE_SLOTS), required=True)
    u.add_argument("--texts", required=True, help="overall, summary, slots{슬롯:{text,reason}} 가 든 JSON 파일")
    u.add_argument("--chart", default=str(CHART_PATH))
    u.add_argument("--out", default=str(OUT_PATH))

    args = p.parse_args(argv)
    if args.cmd == "chart":
        _dump(pillars(datetime.strptime(args.birth, "%Y-%m-%d %H:%M")))
    elif args.cmd == "analyze":
        chart = json.loads(CHART_PATH.read_text(encoding="utf-8"))
        _dump(analyze(chart, datetime.now(KST), MODE_SLOTS[args.mode]))
    elif args.cmd == "publish":
        now = datetime.now(KST)
        chart = json.loads(Path(args.chart).read_text(encoding="utf-8"))
        texts = json.loads(Path(args.texts).read_text(encoding="utf-8"))
        try:
            publish(texts, analyze(chart, now, MODE_SLOTS[args.mode]), args.mode, Path(args.out), now)
        except ValueError as exc:
            print(f"publish 실패: {exc}", file=sys.stderr)
            return 1
        print("publish 성공")
    return 0


if __name__ == "__main__":
    sys.exit(main())
