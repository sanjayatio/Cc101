# -*- coding: utf-8 -*-
"""
tests/test_stat_ocr_hard_cases.py

Unit tests for _count_inner_blobs (always run).
Integration tests load crops from tests/inputs/daily/ and assert that
StatOcr.read() matches the ground-truth (pct, val) stored in stat.json.

Ground truth is produced by running the full pipeline (blob where possible,
Tesseract fallback otherwise) on the N worst-performing images from single/.
Regenerate test inputs with: python tests/generate_stat_inputs.py

After the session, tests/outputs/daily/stat.json is written with entries
where the blob pipeline diverged from GT (i.e., would have fallen back to
Tesseract in production).  Failing crop PNGs are also copied there unless
--no-save-failing-crops is passed.

Skip conditions:
  - templates missing         -> pytest.skip (rebuild: python -m gfl2.stat_ocr --build ...)
  - templates pre-date inner_blobs -> pytest.skip (rebuild required)
  - stat.json missing         -> pytest.skip (regenerate: python tests/generate_stat_inputs.py)
  - crop PNG missing          -> pytest.skip (per parametrized case)
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import cv2
import pytest

_ROOT     = Path(__file__).parent.parent
_DAILY    = _ROOT / "tests" / "inputs" / "daily"
_MANIFEST = _DAILY / "stat.json"

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
    """
    Return flat list of (source_img, part, pct, val) from stat.json.
    Handles both the current grouped format and the legacy flat-list format.
    """
    if not _MANIFEST.exists():
        return []
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    crops = data.get("crops", {})

    if isinstance(crops, list):
        rows = []
        for entry in crops:
            stem = Path(entry["path"]).stem
            m = _PART_RE.search(stem)
            if m:
                source = stem[:m.start()] + ".png"
                rows.append((source, m.group(1), entry["pct"], entry["val"]))
        return rows

    rows = []
    for source_img, parts in crops.items():
        for entry in parts:
            rows.append((source_img, entry["part"], entry["pct"], entry["val"]))
    return rows


_CROPS = _load_manifest()


# ── integration: parametrized over all crops in stat.json ────────────────────

@pytest.mark.parametrize(
    "source,part,exp_pct,exp_val",
    _CROPS,
    ids=[f"{s}::{p}" for s, p, _, _ in _CROPS],
)
def test_stat_cell(ocr, stat_fallback_collector, source, part, exp_pct, exp_val):
    crop_name = f"{Path(source).stem}_{part}.png"
    crop_path = _DAILY / crop_name
    if not crop_path.exists():
        pytest.skip(f"crop not found: {crop_name}")
    img = cv2.imread(str(crop_path))
    if img is None:
        pytest.skip(f"could not read: {crop_name}")

    got_pct, got_val = ocr.read(img)

    pct_ok = (not exp_pct) or (got_pct == exp_pct)
    val_ok = (not exp_val) or (got_val == exp_val)

    if not pct_ok or not val_ok:
        stat_fallback_collector["items"].append({
            "source":   source,
            "part":     part,
            "exp_pct":  exp_pct,  "got_pct": got_pct,
            "exp_val":  exp_val,  "got_val": got_val,
            "crop_path": str(crop_path),
        })

    if exp_pct:
        assert pct_ok, f"{source}::{part} pct: expected {exp_pct!r}, got {got_pct!r}"
    if exp_val:
        assert val_ok, f"{source}::{part} val: expected {exp_val!r}, got {got_val!r}"
