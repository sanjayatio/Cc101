# -*- coding: utf-8 -*-
"""
tests/test_stat_ocr_hard_cases.py

Unit tests for _count_inner_blobs (always run).
Integration tests load crops from stat_set/ and check StatOcr.read() output.
Integration tests skip when templates are absent, corrupted, or pre-date inner_blobs.
"""
from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np
import pytest

_ROOT     = Path(__file__).parent.parent
_STAT_SET = _ROOT / "stat_set"
_MANIFEST = _STAT_SET / "manifest.json"


# ── unit tests ────────────────────────────────────────────────────────────────

def test_inner_blobs_zero_holes():
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.full((13, 8), 255, dtype=np.uint8)
    assert _count_inner_blobs(norm) == 0

def test_inner_blobs_empty_image():
    from gfl2.stat_ocr import _count_inner_blobs
    assert _count_inner_blobs(np.zeros((13, 8), dtype=np.uint8)) == 0

def test_inner_blobs_one_hole():
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((13, 8), dtype=np.uint8)
    norm[1:12, 1:7] = 255
    norm[3:10, 2:6] = 0
    assert _count_inner_blobs(norm) == 1

def test_inner_blobs_two_holes():
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((20, 12), dtype=np.uint8)
    norm[1:9,   1:11] = 255;  norm[2:8,   2:10] = 0
    norm[10:19, 1:11] = 255;  norm[11:18, 2:10] = 0
    assert _count_inner_blobs(norm) == 2

def test_inner_blobs_does_not_count_outer():
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((13, 8), dtype=np.uint8)
    norm[2:11, 2:6] = 255
    assert _count_inner_blobs(norm) == 0


# ── fixtures ──────────────────────────────────────────────────────────────────

def _manifest_gt():
    if not _MANIFEST.exists():
        return {}
    items = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    return {Path(it["path"]).stem: {"pct": it["pct"], "val": it["val"]} for it in items}

def _need_rebuild(engine):
    val_t = getattr(engine, "_val", {})
    return bool(val_t) and "inner_blobs" not in next(iter(val_t.values()))

@pytest.fixture(scope="module")
def ocr():
    try:
        from gfl2.stat_ocr import StatOcr
        engine = StatOcr.load()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))
    except Exception as exc:
        if isinstance(exc, (json.JSONDecodeError, ValueError, UnicodeDecodeError)):
            pytest.skip("templates.json unreadable (NTFS truncation?): " + str(exc)[:80])
        raise
    if _need_rebuild(engine):
        pytest.skip(
            "Templates pre-date inner_blobs. "
            "Run: python -m gfl2.stat_ocr --build --images single/"
        )
    return engine

@pytest.fixture(scope="module")
def gt():
    data = _manifest_gt()
    if not data:
        pytest.skip("stat_set/manifest.json not found")
    return data

def _load_crop(name):
    p = _STAT_SET / (name + ".png")
    if not p.exists():
        pytest.skip("stat_set/" + name + ".png not found")
    img = cv2.imread(str(p))
    if img is None:
        pytest.skip("Could not read " + str(p))
    return img

def _check(ocr_engine, gt_map, cell_name, exp_val, fuzzy_val=False):
    crop    = _load_crop(cell_name)
    exp_pct = gt_map.get(cell_name, {}).get("pct")
    got_pct, got_val = ocr_engine.read(crop)
    if exp_pct is not None:
        assert got_pct == exp_pct, cell_name + " pct: exp=" + repr(exp_pct) + " got=" + repr(got_pct)
    if fuzzy_val:
        assert (got_val or "").replace("?", "") == exp_val, (
            cell_name + " val: exp=" + repr(exp_val) + " got=" + repr(got_val))
    else:
        assert got_val == exp_val, cell_name + " val: exp=" + repr(exp_val) + " got=" + repr(got_val)


# ── integration: K-suffix ─────────────────────────────────────────────────────

@pytest.mark.parametrize("cell,exp_val", [
    ("ib_d_20260111_p1_r0_col1", "4246K"),
    ("ib_d_20260111_p1_r1_col1", "3820K"),
    ("ib_d_20260111_p2_r1_col1", "1967K"),
])
def test_k_suffix_correct(ocr, gt, cell, exp_val):
    _check(ocr, gt, cell, exp_val)


# ── integration: zeros ────────────────────────────────────────────────────────

@pytest.mark.parametrize("cell,exp_val", [
    ("ib_d_20260111_p1_r0_col4", "0"),
    ("ib_d_20260111_p1_r1_col4", "0"),
    ("ib_d_20260111_p1_r2_col4", "0"),
    ("ib_d_20260111_p2_r2_col4", "0"),
    ("ib_d_20260111_p2_r2_col2", "440"),
])
def test_zero_cells(ocr, gt, cell, exp_val):
    _check(ocr, gt, cell, exp_val, fuzzy_val=True)


# ── integration: 5 vs 8 ───────────────────────────────────────────────────────

@pytest.mark.parametrize("cell,exp_val", [
    ("ib_d_20260111_p1_r4_col4", "14503"),
])
def test_5_vs_8_confusion(ocr, gt, cell, exp_val):
    _check(ocr, gt, cell, exp_val)


# ── integration: K with interior zeros ───────────────────────────────────────

@pytest.mark.parametrize("cell,exp_val", [
    ("ib_d_20260111_p2_r2_col1", "1001K"),
])
def test_k_with_interior_zeros(ocr, gt, cell, exp_val):
    _check(ocr, gt, cell, exp_val, fuzzy_val=True)
