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

import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
import pytest

from gfl2.patterns.daily_gunsmoke import parse

SINGLE_DIR = Path(__file__).parent.parent / "single"

sys.path.insert(0, str(Path(__file__).parent.parent))
import main  # noqa: E402  (path must be set up before this import)


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


def test_stat_ocr_v0_1_1_engine_runs_end_to_end():
    """The promoted gfl2.stat_ocr_v0_1_1.StatOcrV0_1_1 engine, injected the
    same way main.py's --stat-ocr-engine v0_1_1 does, must parse a real
    fixture end-to-end and produce structurally valid rows — proving it's
    actually wired correctly through the real call path, not just
    duck-type-compatible in theory."""
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    try:
        from gfl2.stat_ocr_v0_1_1 import StatOcrV0_1_1
        engine = StatOcrV0_1_1.load()
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


def test_stat_ocr_v0_3_0_engine_runs_end_to_end():
    """The gfl2.stat_ocr_v0_3_0.StatOcrV0_3_0 engine, injected the same way main.py's
    --stat-ocr-engine v0_3_0 does, must parse a real fixture end-to-end and
    produce structurally valid rows for both pct AND val (the val-line
    classify_val() tree, docs/known_issues.txt §31's VAL-LINE TREE) --
    with tess_fallback=True (this test), val comes from the same real v0_3_0
    classifier as pct; the existing Tesseract fallback is only a backstop
    for cells the classifier itself leaves as None. This test is slow
    (real Tesseract calls are still possible for any residual miss) by
    necessity, not oversight."""
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    from gfl2.stat_ocr_v0_3_0 import StatOcrV0_3_0
    engine = StatOcrV0_3_0.load()
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
            assert doll.dmg_dealt_val is not None
            assert doll.stab_val is not None
            assert doll.dmg_taken_val is not None
            assert doll.healed_val is not None

    # First entry's first doll is a known-correct fixture value (reference.txt
    # §1.2's own worked example) -- confirms the val classifier reads the
    # real val-line digits, not just "some string".
    first_doll = entries[0].dolls[0]
    assert first_doll.name == "QiongJiu"
    assert first_doll.dmg_dealt_val == "882107"
    assert first_doll.stab_val == "186"
    assert first_doll.dmg_taken_val == "5716"


def test_stat_ocr_v0_3_0_engine_tess_fallback_off_val_from_classifier():
    """main.py's --stat-tess-fallback defaults to OFF: with
    tess_fallback=False (the CLI's default), _extract_stat_cell must NOT
    call Tesseract at all -- pct AND val must both come directly from
    StatOcrV0_3_0's own classify()/classify_val() trees, with no external
    fallback involved. This is the fast path; test_stat_ocr_v0_3_0_engine_runs_
    end_to_end above additionally allows the (slow, Tesseract-backed)
    fallback for any residual miss."""
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    from gfl2.stat_ocr_v0_3_0 import StatOcrV0_3_0
    engine = StatOcrV0_3_0.load()
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
            assert doll.dmg_dealt_val is not None
            assert doll.stab_val is not None
            assert doll.dmg_taken_val is not None
            assert doll.healed_val is not None

    first_doll = entries[0].dolls[0]
    assert first_doll.name == "QiongJiu"
    assert first_doll.dmg_dealt_val == "882107"
    assert first_doll.stab_val == "186"
    assert first_doll.dmg_taken_val == "5716"


def test_score_ocr_v0_3_0_fixes_adjacent_digit_merge():
    """Regression test for docs/known_issues.txt §33: the default score
    pipeline (score_ocr=None, unchanged for every engine but v0_3_0) silently
    DROPS an adjacent-digit merge -- fb_d_20251019.png panel 2's real
    score '4407' reads back as '07' with no '?' marker, confirmed via a
    direct parse() call. gfl2.score_ocr_v0_3_0.ScoreOcrV0_3_0 (selected alongside
    stat_ocr='v0_3_0' via main.py --stat-ocr-engine v0_3_0) is a SEGMENTATION-ONLY
    scaffold whose read_score() always returns None -- this routes score
    through the existing unconditional Tesseract fallback instead, which
    reads this specific case correctly. This does not validate the
    adaptive-threshold segmentation logic itself (that was corpus-
    validated separately, see §33) -- it validates the WIRING: that
    injecting score_ocr actually changes daily_gunsmoke.py's behavior for
    this real, previously-broken case."""
    path = SINGLE_DIR / "fb_d_20251019.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    from gfl2.score_ocr_v0_3_0 import ScoreOcrV0_3_0
    engine = ScoreOcrV0_3_0.load()
    img = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"

    entries = parse(img, filename=path.stem, score_ocr=engine, tess_fallback=True)

    assert len(entries) == 2
    by_idx = {e.report_idx: e for e in entries}
    assert by_idx[1].score == "4180"
    assert by_idx[2].score == "4407"


def test_header_ocr_v0_3_0_engine_runs_end_to_end():
    """gfl2.header_ocr_v0_3_0.HeaderOcrV0_3_0, injected the same way main.py's
    --stat-ocr-engine v0_3_0 does, must parse a real fixture end-to-end and
    read the header stats row (dealt/taken/turns) correctly. Unlike
    gfl2.score_ocr_v0_3_0.ScoreOcrV0_3_0 (a segmentation-only scaffold at the time
    of writing), this engine's classify_header() is a real v0_3_0-family
    classify tree over 0-9/K/M built from assets/fonts/
    glyph_daily_header.png -- corpus-validated at 100.0% glyph-level
    accuracy (gfl2/calibration/calibrate_header_v0_3_0.py). Expected values
    match reference.txt's own documented gm_d_20250929 example exactly."""
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    from gfl2.header_ocr_v0_3_0 import HeaderOcrV0_3_0
    engine = HeaderOcrV0_3_0.load()
    img = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"

    entries = parse(img, filename=path.stem, header_ocr=engine)

    assert len(entries) == 2
    by_idx = {e.report_idx: e for e in entries}
    assert by_idx[1].dmg_dealt_total == "2263K"
    assert by_idx[1].dmg_taken_total == "39170"
    assert by_idx[1].combat_turns == "7"
    assert by_idx[2].dmg_dealt_total == "1409K"
    assert by_idx[2].dmg_taken_total == "54070"
    assert by_idx[2].combat_turns == "7"


# ── timer-span completeness vs wall_clock_s ─────────────────────────────────
# known_issues.txt §35: real per-image work (cv2.imread,
# panel/frame detection, save_js) once ran completely outside any
# `timer.timed(...)` span -- invisible to gfl2/report.py's SECTIONS and to
# the console's pipeline_summary() tree alike -- and was only found by a user
# manually summing a generated report's numbers by hand against its own
# META.wall_clock_s. These tests assert the invariant that fix established:
# every processed image's Span.root.ms must, in total, account for main.py's
# own independently-measured wall_clock_s within a small tolerance -- so a
# FUTURE untimed code path shows up as a test failure instead of requiring
# another manual reconciliation.
#
# Exercises the real main._process_daily_single/_process_daily_folder
# functions directly (not a re-implementation of their instrumentation), so a
# regression in main.py's own span wiring is actually caught -- the bug this
# guards against lived in main.py itself (image_load/save_js spans), not in
# gfl2.patterns.daily_gunsmoke.parse(). generate_report, the tess-fallback-log
# flush, and the name-template flush are monkeypatched to no-ops purely to
# keep the test from overwriting real, version-controlled/generated project
# state (tests/outputs/daily/stat_tess_fallbacks.json,
# assets/doll_names/templates.json, tests/outputs/daily/reports/) -- none of
# that touches the timer/wall-clock instrumentation itself.

_TIMER_GAP_TOLERANCE_MS = 100.0  # measured real gap on this fixture set is
                                 # sub-millisecond (<0.1ms) once lazy
                                 # singletons are warmed up; 100ms leaves
                                 # generous room for test-environment print/
                                 # flush jitter while still catching the
                                 # original bug's class of regression (tens
                                 # of ms/image of untimed work, known_issues.txt §35).


def _neutralize_main_side_effects(monkeypatch) -> dict:
    """Prevent main.py's flush/report helpers from touching real,
    version-controlled/generated project files during this test -- see this
    section's own header comment. Returns the dict that generate_report's
    real kwargs get captured into (roots, wall_clock_s, ...)."""
    captured: dict = {}

    def _fake_generate_report(**kwargs):
        captured.update(kwargs)
        return Path("unused-in-test-report.py")

    monkeypatch.setattr(main, "generate_report", _fake_generate_report)
    monkeypatch.setattr(main, "_flush_tess", lambda: 0)
    monkeypatch.setattr(main, "_flush_names", lambda: None)
    main._set_save_tess_crops(False)
    return captured


def _assert_spans_account_for_wall_clock(roots, wall_clock_s: float, label: str) -> None:
    total_span_ms = sum(r.ms for r in roots)
    wall_clock_ms = wall_clock_s * 1000
    gap_ms = abs(wall_clock_ms - total_span_ms)
    assert gap_ms <= _TIMER_GAP_TOLERANCE_MS, (
        f"{label}: timer spans ({total_span_ms:.1f}ms total) drifted from "
        f"main.py's own wall_clock_s ({wall_clock_ms:.1f}ms) by {gap_ms:.1f}ms "
        f"-- a code path is running outside any timer.timed(...) span "
        f"(known_issues.txt §35)"
    )


def test_timer_spans_account_for_wall_clock_single_image(tmp_path, monkeypatch):
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")

    captured = _neutralize_main_side_effects(monkeypatch)

    def _run(out_name: str):
        args = main.build_arg_parser().parse_args([
            str(path), "--pattern", "daily_gunsmoke",
            "--output", str(tmp_path / out_name),
            "--no-save-tess-crops",
        ])
        main._process_daily_single(path, args)

    _run("warmup.js")   # absorb lazy-singleton first-call cost (stat engine
                        # templates, doll-name OCR, asset-mapper caches) so it
                        # isn't mistaken for a genuine untimed gap below.
    _run("out.js")

    assert captured, "generate_report was never called"
    _assert_spans_account_for_wall_clock(
        captured["roots"], captured["wall_clock_s"], "single-image path"
    )


def test_timer_spans_account_for_wall_clock_folder(tmp_path, monkeypatch):
    names = ["gm_d_20250929.png", "fb_d_20251019.png"]
    missing = [n for n in names if not (SINGLE_DIR / n).exists()]
    if missing:
        pytest.skip(f"Test image(s) not found: {missing}")

    folder = tmp_path / "images"
    folder.mkdir()
    for n in names:
        shutil.copy(SINGLE_DIR / n, folder / n)

    captured = _neutralize_main_side_effects(monkeypatch)

    def _run(out_name: str):
        args = main.build_arg_parser().parse_args([
            str(folder), "--pattern", "daily_gunsmoke",
            "--output", str(tmp_path / out_name),
            "--no-save-tess-crops",
        ])
        main._process_daily_folder(folder, args)

    _run("warmup.js")   # absorb lazy-singleton first-call cost
    _run("out.js")

    assert captured, "generate_report was never called"
    _assert_spans_account_for_wall_clock(
        captured["roots"], captured["wall_clock_s"], "folder path"
    )
