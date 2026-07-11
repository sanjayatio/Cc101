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


# ── stat_ocr engine injection ───────────────────────────────────────────────
# Regression coverage for parse()'s stat_ocr parameter: docs/known_issues.txt
# §16 found that main.py's CLI wiring of an alternate pipeline (score_fn via
# make_score_fn()) had ZERO test coverage even though weekly_gunsmoke.parse()
# itself was tested — the wiring, not the pipeline, was the untested part.
# These tests close the equivalent gap for stat_ocr: they call parse()
# directly with an injected engine (main.py's actual mechanism), instead of
# only exercising the default _get_stat_ocr() lazy-singleton path.

class _StubStatOcr:
    """Fake stat-cell OCR engine returning a fixed, unmistakable sentinel —
    used to prove injection actually overrides the default engine rather
    than being silently ignored (a real engine's output would never be this
    same fixed pair across every single cell)."""

    SENTINEL_PCT = "11.11"
    SENTINEL_VAL = "999999"

    def read(self, cell, timer=None):
        return (self.SENTINEL_PCT, self.SENTINEL_VAL)


def test_stat_ocr_injection_overrides_default():
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    img = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"

    entries = parse(img, filename=path.stem, stat_ocr=_StubStatOcr())

    assert entries, "expected at least one report entry"
    for entry in entries:
        for doll in entry.dolls:
            for pct, val in (
                (doll.dmg_dealt_pct, doll.dmg_dealt_val),
                (doll.stab_pct,      doll.stab_val),
                (doll.dmg_taken_pct, doll.dmg_taken_val),
                (doll.healed_pct,    doll.healed_val),
            ):
                assert pct == _StubStatOcr.SENTINEL_PCT, \
                    f"injected stub engine was not used: got pct={pct!r}"
                assert val == _StubStatOcr.SENTINEL_VAL, \
                    f"injected stub engine was not used: got val={val!r}"


def test_stat_ocr_padded_engine_runs_end_to_end():
    """The promoted gfl2.stat_ocr_padded.StatOcrPadded engine, injected the
    same way main.py's --stat-ocr-engine padded does, must parse a real
    fixture end-to-end and produce structurally valid rows — proving it's
    actually wired correctly through the real call path, not just
    duck-type-compatible in theory."""
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    try:
        from gfl2.stat_ocr_padded import StatOcrPadded
        engine = StatOcrPadded.load()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))
    img = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"

    entries = parse(img, filename=path.stem, stat_ocr=engine)

    assert len(entries) == 2
    for entry in entries:
        assert len(entry.dolls) == 5
        for doll in entry.dolls:
            assert doll.name is not None


def test_stat_ocr_dp_engine_runs_end_to_end():
    """The exploratory gfl2.stat_ocr_dp.StatOcrDp engine, injected the same
    way main.py's --stat-ocr-engine dp does, must parse a real fixture
    end-to-end and produce structurally valid rows. Unlike the padded
    engine, StatOcrDp's val-line is a real no-op stub (always returns
    None) -- every cell's val is expected to come from the existing
    Tesseract psm6/psm4 fallback in _extract_stat_cell, not from StatOcrDp
    itself. This test is slow (real Tesseract calls on every cell) by
    necessity, not oversight -- it's what actually exercises the "dp
    engine's None val correctly triggers the existing fallback" path,
    not just duck-type compatibility in theory."""
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    from gfl2.stat_ocr_dp import StatOcrDp
    engine = StatOcrDp.load()
    img = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"

    entries = parse(img, filename=path.stem, stat_ocr=engine)

    assert len(entries) == 2
    for entry in entries:
        assert len(entry.dolls) == 5
        for doll in entry.dolls:
            assert doll.name is not None
            assert doll.dmg_dealt_pct is not None
            assert doll.stab_pct is not None
            assert doll.dmg_taken_pct is not None
            assert doll.healed_pct is not None


def test_stat_ocr_dp_engine_tess_fallback_off_leaves_val_none():
    """main.py's --stat-tess-fallback defaults to OFF specifically because
    of this engine: with tess_fallback=False (the CLI's new default),
    _extract_stat_cell must NOT call Tesseract at all when StatOcrDp
    leaves val as None -- val should pass straight through as None (JS
    `null` downstream), and pct must still come from the real dp
    classifier. This is the fast path; test_stat_ocr_dp_engine_runs_end_to_end
    above is the (slow, Tesseract-backed) opt-in path."""
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    from gfl2.stat_ocr_dp import StatOcrDp
    engine = StatOcrDp.load()
    img = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"

    entries = parse(img, filename=path.stem, stat_ocr=engine, tess_fallback=False)

    assert len(entries) == 2
    for entry in entries:
        assert len(entry.dolls) == 5
        for doll in entry.dolls:
            assert doll.name is not None
            assert doll.dmg_dealt_pct is not None
            assert doll.stab_pct is not None
            assert doll.dmg_taken_pct is not None
            assert doll.healed_pct is not None
            assert doll.dmg_dealt_val is None
            assert doll.stab_val is None
            assert doll.dmg_taken_val is None
            assert doll.healed_val is None
