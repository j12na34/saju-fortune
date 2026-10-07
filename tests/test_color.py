import colorsys
import re

import pytest

from saju.color import slot_color
from saju.wuxing import ELEMENT_ORDER

SLOTS = ("morning", "lunch", "evening")


def _hls(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, l, s


@pytest.mark.parametrize("element", ELEMENT_ORDER)
def test_hex_format_and_name(element):
    for slot in SLOTS:
        c = slot_color(element, slot, "甲子")
        assert re.fullmatch(r"#[0-9A-F]{6}", c["hex"])
        assert c["name"]


@pytest.mark.parametrize("element", ELEMENT_ORDER)
def test_slots_share_hue_and_get_darker(element):
    cs = [_hls(slot_color(element, s, "甲子")["hex"]) for s in SLOTS]
    hues = [c[0] for c in cs]
    assert max(hues) - min(hues) <= 6
    assert cs[0][1] > cs[1][1] > cs[2][1]


def test_matching_hour_element_raises_saturation():
    plain = _hls(slot_color("木", "lunch", "丙午")["hex"])      # 火 -> 불일치
    boosted = _hls(slot_color("木", "lunch", "甲寅")["hex"])    # 木 -> 일치
    assert boosted[2] > plain[2]
