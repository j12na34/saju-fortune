"""공개 주소의 fortune.json 이 열리고 필수 키가 있는지 확인한다. 성공하면 종료 코드 0."""
import json
import sys
import urllib.request

URL = "https://j12na34.github.io/saju-fortune/fortune.json"
REQUIRED = {"date", "updated_at", "ilgin", "overall", "slots", "summary"}


def main() -> int:
    try:
        with urllib.request.urlopen(URL, timeout=20) as resp:
            doc = json.load(resp)
    except Exception as exc:  # noqa: BLE001 - 사용자에게 이유를 그대로 보여준다
        print(f"실패: {URL} 를 열 수 없어요 ({exc})")
        return 1
    missing = REQUIRED - set(doc)
    if missing:
        print(f"실패: 빠진 항목 {sorted(missing)}")
        return 1
    print(f"성공: {URL} (date={doc['date']}, updated_at={doc['updated_at']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
