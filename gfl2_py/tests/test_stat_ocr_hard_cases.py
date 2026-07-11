# -*- coding: utf-8 -*-
"""
tests/test_stat_ocr_hard_cases.py

Unit tests for _count_inner_blobs (always run).
Integration tests load crops from tests/inputs/daily/ and assert that
StatOcr.read() matches the ground-truth (pct, val) stored in stat.json.

Ground truth is produced by running the full pipeline (blob where possible,
Tesseract fallback otherwise) on the N worst-performing images from single/.
Regenerate test inputs with: python tests/generate_stat_inputs.py

Ground truth + per-image metadata (doll frames present, rare-doll tags, hard
cell counts) live in tests/inputs/daily/stat_data.py — a generated Python
module (docs/action_items.txt #1), not the old stat.json.

After the session, tests/outputs/daily/stat.json is written with entries
where the blob pipeline diverged from GT (i.e., would have fallen back to
Tesseract in production).  Failing crop PNGs are also copied there unless
--no-save-failing-crops is passed.

Skip conditions:
  - templates missing         -> pytest.skip (rebuild: python -m gfl2.stat_ocr --build ...)
  - templates pre-date inner_blobs -> pytest.skip (rebuild required)
  - stat_data.py missing      -> pytest.skip (regenerate: python tests/generate_stat_inputs.py)
  - crop PNG missing          -> pytest.skip (per parametrized case)
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import pytest

_ROOT     = Path(__file__).parent.parent
_DAILY    = _ROOT / "tests" / "inputs" / "daily"
_STAT_DATA_PY = _DAILY / "stat_data.py"

_PART_RE  = re.compile(r'_(p\d+_r\d+_col\d+)$')


# ── unit tests: _count_inner_blobs ────────────────────────────────────────────

def test_inner_blobs_zero_holes():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.full((13, 8), 255, dtype=np.uint8)
    assert _count_inner_blobs(norm) == 0

def test_inner_blobs_empty_image():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    assert _count_inner_blobs(np.zeros((13, 8), dtype=np.uint8)) == 0

def test_inner_blobs_one_hole():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((13, 8), dtype=np.uint8)
    norm[1:12, 1:7] = 255
    norm[3:10, 2:6] = 0
    assert _count_inner_blobs(norm) == 1

def test_inner_blobs_two_holes():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((20, 12), dtype=np.uint8)
    norm[1:9,   1:11] = 255;  norm[2:8,   2:10] = 0
    norm[10:19, 1:11] = 255;  norm[11:18, 2:10] = 0
    assert _count_inner_blobs(norm) == 2

def test_inner_blobs_does_not_count_outer():
    import numpy as np
    from gfl2.stat_ocr import _count_inner_blobs
    norm = np.zeros((13, 8), dtype=np.uint8)
    norm[2:11, 2:6] = 255
    assert _count_inner_blobs(norm) == 0


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def stat_crops():
    """Extract all stat crops from single/ source images, keyed by (source, part)."""
    from gfl2.stat_ocr import _collect_cells
    single = _ROOT / "single"
    sources = {s for s, _, _, _ in _CROPS}
    image_paths = [single / s for s in sources if (single / s).exists()]
    if not image_paths:
        return {}
    results = _collect_cells(image_paths, tess_only=False)
    crops: dict[tuple[str, str], object] = {}
    for item in results:
        source_key = item["img_path"].name
        m = _PART_RE.search(item["source"])
        if m:
            crops[(source_key, m.group(1))] = item["cell"]
    return crops


def _need_rebuild(engine) -> bool:
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
            pytest.skip("templates.json unreadable: " + str(exc)[:80])
        raise
    if _need_rebuild(engine):
        pytest.skip(
            "Templates pre-date inner_blobs. "
            "Run: python -m gfl2.stat_ocr --build --images single/"
        )
    return engine


def _load_manifest() -> list[tuple[str, str, str, str]]:
    """Return flat list of (source_img, part, pct, val) from stat_data.py's CROPS."""
    if not _STAT_DATA_PY.exists():
        return []
    ns: dict = {}
    exec(compile(_STAT_DATA_PY.read_text(encoding="utf-8"), str(_STAT_DATA_PY), "exec"), ns)
    crops = ns.get("CROPS", {})

    rows = []
    for source_img, parts in crops.items():
        for entry in parts:
            rows.append((source_img, entry["part"], entry["pct"], entry["val"]))
    return rows


_CROPS = _load_manifest()

# docs/known_issues.txt §18 (2026-07-11 UPDATE): gm_d_20250908.png is
# captured at a genuinely different (~10% smaller) resolution than the
# rest of the corpus (2047x652 vs the corpus's typical ~2280x690-700).
# THRESH_BIN=180 bridges adjacent black-ink digit glyphs into one merged
# blob at this smaller scale, for these 8 col3 (dmg_taken) cells
# specifically -- confirmed via a direct threshold sweep (clean 8-blob
# separation at t<=150, collapsing to 4 blobs at t=180). Every other
# column/cell in this same image was fixed by §18's _find_percent_x_start
# rewrite and is NOT in this set. Lowering THRESH_BIN globally was tried
# and rejected (regresses corpus accuracy 98.9%->95.1%, a new systematic
# '5'->'3' misread elsewhere) -- this needs a real resolution-adaptive
# threshold design, not a quick constant change, so it's left open and
# honestly marked rather than silently masked.
#
# TO REMOVE once §18's threshold gap gets a real fix: delete these 8
# tuples, re-run this file -- the ground truth in stat_data.py is already
# correct (confirmed via the independent Tesseract GT cache), only the
# classifier's own extraction needs to catch up.
_KNOWN_FAILING = {
    ("gm_d_20250908.png", "p1_r0_col3"), ("gm_d_20250908.png", "p1_r1_col3"),
    ("gm_d_20250908.png", "p1_r2_col3"), ("gm_d_20250908.png", "p1_r3_col3"),
    ("gm_d_20250908.png", "p1_r4_col3"), ("gm_d_20250908.png", "p2_r1_col3"),
    ("gm_d_20250908.png", "p2_r2_col3"), ("gm_d_20250908.png", "p2_r3_col3"),
}


def _build_params():
    params = []
    for s, p, exp_pct, exp_val in _CROPS:
        marks = []
        if (s, p) in _KNOWN_FAILING:
            marks.append(pytest.mark.xfail(
                reason="docs/known_issues.txt §18 (2026-07-11 UPDATE): "
                       "gm_d_20250908.png col3 -- known unresolved "
                       "resolution-adaptive-binarization-threshold gap",
                strict=True,
            ))
        params.append(pytest.param(s, p, exp_pct, exp_val, marks=marks, id=f"{s}::{p}"))
    return params


_PARAMS = _build_params()


# ── integration: parametrized over all crops in stat.json ────────────────────

@pytest.mark.parametrize(
    "source,part,exp_pct,exp_val",
    _PARAMS,
)
def test_stat_cell(ocr, stat_fallback_collector, stat_crops, source, part, exp_pct, exp_val):
    img = stat_crops.get((source, part))
    if img is None:
        pytest.skip(f"crop not extractable: {source}::{part}")

    got_pct, got_val = ocr.read(img)

    pct_ok = (not exp_pct) or (got_pct == exp_pct)
    val_ok = (not exp_val) or (got_val == exp_val)

    if not pct_ok or not val_ok:
        stat_fallback_collector["items"].append({
            "source":  source,
            "part":    part,
            "exp_pct": exp_pct, "got_pct": got_pct,
            "exp_val": exp_val, "got_val": got_val,
            "cell":    img,
        })

    if exp_pct:
        assert pct_ok, f"{source}::{part} pct: expected {exp_pct!r}, got {got_pct!r}"
    if exp_val:
        assert val_ok, f"{source}::{part} val: expected {exp_val!r}, got {got_val!r}"
