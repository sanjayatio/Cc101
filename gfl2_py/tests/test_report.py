# -*- coding: utf-8 -*-
"""
tests/test_report.py
---------------------
Regression coverage for gfl2/report.py's generate_report() and the
per-section stats machinery (_record_field/flush_section_stats) in
gfl2/patterns/daily_gunsmoke.py that feeds it -- closing action_items.txt
#35 (neither had any automated test before this; both were only manually
verified against a real 87-image folder run inspected by hand).

Two layers, per that item's own ACTION:
  - _record_field/flush_section_stats: direct unit tests against synthetic
    (raw, final) pairs, covering the "ok" / "failed" / unknown_glyphs-only
    contract documented in _record_field's own docstring, plus an
    end-to-end run of parse() on a real fixture whose counts are exactly
    known (2 panels x 5 dolls x 4 stat pairs = 40 pct/val cells; 2 panels
    x (1 score + 3 stats-row) fields).
  - generate_report(): a synthetic Span tree + section_stats dict (no
    image I/O, so the pipeline-row arithmetic is exact and immune to
    engine/timing variance), asserting the written report's META and
    SECTIONS match expected values -- including that pct/val share the
    same stat_cell/blob pipeline row by construction (decisions.txt #57).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import cv2
import pytest

from gfl2 import report
from gfl2.patterns.daily_gunsmoke import _record_field, flush_section_stats, parse
from gfl2.report import generate_report
from gfl2.timing import Span

SINGLE_DIR = Path(__file__).parent.parent / "single"


@pytest.fixture(autouse=True)
def _clean_section_stats():
    """_SECTION_STATS is module-global state shared with every other test
    module that calls parse() in the same pytest process (e.g.
    tests/test_daily_gunsmoke.py, which does not flush it) -- flush before
    and after each test here so the counts asserted below can never be
    polluted by another test file's parse() calls, and this file never
    leaves stale counts behind for anyone else either."""
    flush_section_stats()
    yield
    flush_section_stats()


# ── _record_field / flush_section_stats ─────────────────────────────────────

def test_record_field_ok_when_raw_clean_and_matches_final():
    _record_field("pct", "12.34", "12.34")
    snap = flush_section_stats()
    assert snap["pct"] == {"processed": 1, "ok": 1, "failed": 0, "unknown_glyphs": 0}


def test_record_field_failed_when_final_is_none():
    _record_field("val", None, None)
    snap = flush_section_stats()
    assert snap["val"] == {"processed": 1, "ok": 0, "failed": 1, "unknown_glyphs": 0}


def test_record_field_unknown_glyphs_counted_without_ok_or_failed():
    # raw carries two '?' glyphs but a fallback still resolved a final
    # value -- not "ok" (raw wasn't clean), not "failed" (final resolved).
    _record_field("val", "1??4", "123456")
    snap = flush_section_stats()
    assert snap["val"] == {"processed": 1, "ok": 0, "failed": 0, "unknown_glyphs": 2}


def test_record_field_fallback_recovery_from_raw_none_is_not_ok():
    # raw is None (blob path produced nothing) but a fallback recovered a
    # value -- still not "ok" (raw wasn't clean to begin with).
    _record_field("header", None, "39170")
    snap = flush_section_stats()
    assert snap["header"] == {"processed": 1, "ok": 0, "failed": 0, "unknown_glyphs": 0}


def test_flush_section_stats_resets_counters():
    _record_field("score", "4635", "4635")
    first = flush_section_stats()
    assert first["score"]["processed"] == 1
    second = flush_section_stats()
    assert second["score"] == {"processed": 0, "ok": 0, "failed": 0, "unknown_glyphs": 0}


def test_flush_section_stats_accumulates_across_multiple_records():
    _record_field("pct", "1.23", "1.23")
    _record_field("pct", None, None)
    _record_field("pct", "4?6", "456")
    snap = flush_section_stats()
    assert snap["pct"] == {"processed": 3, "ok": 1, "failed": 1, "unknown_glyphs": 1}


# ── end-to-end: parse() + flush_section_stats() on a real fixture ──────────
# Exercises the real call path (_extract_header's / _extract_stat_cell's own
# _record_field calls), not a re-implementation of their logic.

def test_flush_section_stats_counts_gm_d_20250929():
    path = SINGLE_DIR / "gm_d_20250929.png"
    if not path.exists():
        pytest.skip(f"Test image not found: {path}")
    img = cv2.imread(str(path))
    assert img is not None, f"Could not read {path}"

    entries = parse(img, filename=path.stem)
    snap = flush_section_stats()

    assert len(entries) == 2
    # 2 panels x 5 dolls x 4 stat pairs (dealt/stab/taken/healed) = 40 cells.
    # The default engine reads this fixture cleanly (test_daily_gunsmoke.py's
    # own TestGmD20250929 asserts every field's final value) -- counts below
    # confirm it also reads cleanly with no '?' and no fallback needed.
    assert snap["pct"] == {"processed": 40, "ok": 40, "failed": 0, "unknown_glyphs": 0}
    assert snap["val"] == {"processed": 40, "ok": 40, "failed": 0, "unknown_glyphs": 0}
    # 2 panels x 1 score field each.
    assert snap["score"] == {"processed": 2, "ok": 2, "failed": 0, "unknown_glyphs": 0}
    # 2 panels x 3 stats-row fields (dealt/taken/turns) each.
    assert snap["header"] == {"processed": 6, "ok": 6, "failed": 0, "unknown_glyphs": 0}


# ── generate_report() ────────────────────────────────────────────────────────

def _leaf(name: str, elapsed_s: float) -> Span:
    return Span(name=name, elapsed=elapsed_s)


def test_generate_report_meta_and_sections(tmp_path, monkeypatch):
    """Synthetic Span tree, no image I/O -- the pipeline-row arithmetic is
    exact by construction, so this test is immune to real classifier/timing
    variance. Values chosen to also confirm pct and val share the identical
    stat_cell/blob pipeline row (decisions.txt #57), not a bug."""
    monkeypatch.setattr(report, "_REPORT_DIR", tmp_path)

    root1 = Span(name="img1.png", elapsed=0.0, children=[
        _leaf("score/blob", 0.010),
        _leaf("stats_row/blob", 0.020),
        _leaf("stat_cell/blob", 0.005),
        _leaf("stat_cell/blob", 0.005),
        _leaf("stat_cell/blob", 0.005),
    ])
    root2 = Span(name="img2.png", elapsed=0.0, children=[
        _leaf("score/blob", 0.030),
        _leaf("stat_cell/blob", 0.007),
        _leaf("stat_cell/blob", 0.007),
    ])

    section_stats = {
        "score":  {"processed": 2,  "ok": 2,  "failed": 0, "unknown_glyphs": 0},
        "header": {"processed": 6,  "ok": 5,  "failed": 1, "unknown_glyphs": 2},
        "pct":    {"processed": 40, "ok": 38, "failed": 0, "unknown_glyphs": 3},
        "val":    {"processed": 40, "ok": 37, "failed": 1, "unknown_glyphs": 5},
    }
    started_at = datetime(2026, 7, 19, 12, 0, 0, tzinfo=timezone.utc)

    out_path = generate_report(
        image_names=["img1.png", "img2.png"],
        roots=[root1, root2],
        section_stats=section_stats,
        wall_clock_s=1.234,
        started_at=started_at,
        stat_ocr_engine="v0_3_0",
    )

    assert out_path.parent == tmp_path
    assert out_path.name.startswith("report_") and out_path.name.endswith(".py")

    ns: dict = {}
    exec(compile(out_path.read_text(encoding="utf-8"), str(out_path), "exec"), ns)
    meta, sections = ns["META"], ns["SECTIONS"]

    assert meta["stat_ocr_engine"] == "v0_3_0"
    assert meta["images_processed"] == 2
    assert meta["image_names"] == ["img1.png", "img2.png"]
    assert meta["wall_clock_s"] == 1.234
    assert meta["generated_at"] == started_at.isoformat()
    assert isinstance(meta["commit"], str) and meta["commit"]
    assert isinstance(meta["dirty_lines"], int)

    assert sections["score"]["summary"] == section_stats["score"]
    assert sections["header"]["summary"] == section_stats["header"]
    assert sections["pct"]["summary"] == section_stats["pct"]
    assert sections["val"]["summary"] == section_stats["val"]

    assert sections["score"]["pipeline"] == [
        {"stage": "score/blob", "total_s": 0.04, "hits": 2, "avg_ms": 20.0},
    ]
    assert sections["header"]["pipeline"] == [
        {"stage": "stats_row/blob", "total_s": 0.02, "hits": 1, "avg_ms": 20.0},
    ]
    expected_stat_cell_row = {
        "stage": "stat_cell/blob", "total_s": 0.029, "hits": 5, "avg_ms": 5.8,
    }
    assert sections["pct"]["pipeline"] == [expected_stat_cell_row]
    assert sections["val"]["pipeline"] == [expected_stat_cell_row]


def test_generate_report_empty_section_uses_zeroed_summary(tmp_path, monkeypatch):
    """A section missing from section_stats (e.g. a caller that never
    touched "header") must fall back to _EMPTY_SUMMARY, not raise a
    KeyError -- generate_report()'s own contract via section_stats.get()."""
    monkeypatch.setattr(report, "_REPORT_DIR", tmp_path)

    root = Span(name="img1.png", elapsed=0.0, children=[_leaf("score/blob", 0.010)])
    started_at = datetime(2026, 7, 19, 12, 0, 0, tzinfo=timezone.utc)

    out_path = generate_report(
        image_names=["img1.png"],
        roots=[root],
        section_stats={"score": {"processed": 1, "ok": 1, "failed": 0, "unknown_glyphs": 0}},
        wall_clock_s=0.5,
        started_at=started_at,
        stat_ocr_engine="v0_1_0",
    )

    ns: dict = {}
    exec(compile(out_path.read_text(encoding="utf-8"), str(out_path), "exec"), ns)
    sections = ns["SECTIONS"]

    assert sections["header"]["summary"] == {
        "processed": 0, "ok": 0, "failed": 0, "unknown_glyphs": 0,
    }
    assert sections["header"]["pipeline"] == []
