"""만들어질 수 있는 모든 단색 배경화면 PNG 를 docs/colors/<HEX>.png 로 만든다. (표준 라이브러리만 사용)

오행 5 x 시간대 3 x (시주에 필요 오행 있음/없음) 2 = 30가지. 색 규칙(saju/color.py)을 바꾸면 다시 실행한다.
"""
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from saju.color import slot_color  # noqa: E402
from saju.wuxing import CHAR_ELEMENT, ELEMENT_ORDER  # noqa: E402

WIDTH, HEIGHT = 1320, 2868  # 현재 가장 큰 아이폰 해상도. 작은 기종은 자동으로 맞춰진다.
OUT = ROOT / "docs" / "colors"
SLOTS = ("morning", "lunch", "evening")


def _chunk(kind: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def solid_png(rgb: tuple[int, int, int]) -> bytes:
    row = b"\x00" + bytes(rgb) * WIDTH
    raw = row * HEIGHT
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )


def possible_hexes() -> set[str]:
    hexes = set()
    for element in ELEMENT_ORDER:
        with_el = next(c for c, e in CHAR_ELEMENT.items() if e == element) * 2
        other = next(e for e in ELEMENT_ORDER if e != element)
        without_el = next(c for c, e in CHAR_ELEMENT.items() if e == other) * 2
        for slot in SLOTS:
            for hour_pillar in (with_el, without_el):
                hexes.add(slot_color(element, slot, hour_pillar)["hex"])
    return hexes


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for hex_ in sorted(possible_hexes()):
        rgb = tuple(int(hex_[i:i + 2], 16) for i in (1, 3, 5))
        (OUT / f"{hex_.lstrip('#')}.png").write_bytes(solid_png(rgb))
    print(f"{len(possible_hexes())}개 만들었어요: {OUT}")


if __name__ == "__main__":
    main()
