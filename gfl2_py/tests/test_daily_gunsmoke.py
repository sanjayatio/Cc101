"""
tests/test_daily_gunsmoke.py
----------------------------
End-to-end regression tests for the Daily Gunsmoke parser.

Asserts header fields (score, dmg_dealt_total, dmg_taken_total, combat_turns)
and doll count for reference images parsed from single/.

Ground truth for gm_d_20250929 sourced from reference.txt §1.2.

Run with:
    cd gfl2_py
    pytest tests/test_daily_gunsmoke.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
import pytest

from gfl2.patterns.daily_gunsmoke import parse

SINGLE_DIR = Path(__file__).parent.parent / "single"


# ── helpers ───────────────────────────────────────────────────────────────────

@dataclass
class ExpectedPanel:
    score:           str
    dmg_dealt_total: str
    dmg_taken_total: str
    combat_turns:    str
    doll_count:      int = 5


def load_and_parse(filename: str):
    path = SINGLE_DIR / filename
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    img = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"
    return parse(img, filename=path.stem)


def assert_panel(entry, exp: ExpectedPanel, label: str) -> None:
    assert entry.score == exp.score, \
        f"{label}: score {entry.score!r} != {exp.score!r}"
    assert entry.dmg_dealt_total == exp.dmg_dealt_total, \
        f"{label}: dmg_dealt_total {entry.dmg_dealt_total!r} != {exp.dmg_dealt_total!r}"
    assert entry.dmg_taken_total == exp.dmg_taken_total, \
        f"{label}: dmg_taken_total {entry.dmg_taken_total!r} != {exp.dmg_taken_total!r}"
    assert entry.combat_turns == exp.combat_turns, \
        f"{label}: combat_turns {entry.combat_turns!r} != {exp.combat_turns!r}"
    assert len(entry.dolls) == exp.doll_count, \
        f"{label}: doll_count {len(entry.dolls)} != {exp.doll_count}"


# ── gm_d_20250929 ─────────────────────────────────────────────────────────────
# Two-panel image.  Ground truth from reference.txt §1.2 example output.

GM_D_20250929_PANELS = [
    ExpectedPanel(score="4635", dmg_dealt_total="2263K", dmg_taken_total="39170", combat_turns="7"),
    ExpectedPanel(score="3876", dmg_dealt_total="1409K", dmg_taken_total="54070", combat_turns="7"),
]


class TestGmD20250929:
    @pytest.fixture(scope="class")
    def entries(self):
        return load_and_parse("gm_d_20250929.png")

    def test_panel_count(self, entries):
        assert len(entries) == 2

    @pytest.mark.parametrize("i,exp", list(enumerate(GM_D_20250929_PANELS)))
    def test_panel(self, entries, i, exp):
        assert_panel(entries[i], exp, f"gm_d_20250929 panel {i + 1}")
