import struct
import zlib
from pathlib import Path

import pytest

from saju.color import slot_color
from saju.wuxing import ELEMENT_ORDER, CHAR_ELEMENT

ROOT = Path(__file__).resolve().parent.parent
COLORS_DIR = ROOT / "docs" / "colors"
SLOTS = ("morning", "lunch", "evening")


def _all_possible_hexes() -> set[str]:
    """시주에 필요 오행이 있을 때/없을 때 두 경우를 모두 포함한, 만들어질 수 있는 모든 색."""
    hexes = set()
    for element in ELEMENT_ORDER:
        match = next(ch for ch, el in CHAR_ELEMENT.items() if el == element) + "子"
        other_el = next(e for e in ELEMENT_ORDER if e != element and e != "水")
        no_match = next(ch for ch, el in CHAR_ELEMENT.items() if el == other_el) * 1 + next(
            ch for ch, el in CHAR_ELEMENT.items() if el == other_el
        )
        for slot in SLOTS:
            for hp in (match, no_match):
                hexes.add(slot_color(element, slot, hp)["hex"])
    return hexes


def _read_png(path: Path):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, ihdr, idat = 8, None, b""
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    return ihdr, zlib.decompress(idat)


@pytest.mark.parametrize("hex_", sorted(_all_possible_hexes()))
def test_every_possible_color_has_a_png(hex_):
    path = COLORS_DIR / f"{hex_.lstrip('#')}.png"
    assert path.exists(), f"{path.name} 이 없어요"
    (width, height, depth, ctype, *_), raw = _read_png(path)
    assert (width, height) == (1320, 2868)
    assert depth == 8 and ctype == 2  # 8비트 RGB
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    assert raw[0] == 0  # 첫 줄 필터 없음
    assert tuple(raw[1:4]) == (r, g, b)
    assert tuple(raw[-3:]) == (r, g, b)  # 마지막 픽셀도 같은 색
