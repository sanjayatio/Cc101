# -*- coding: utf-8 -*-
"""
tests/test_score_pipeline.py

Parametrized integration test for the blob/Hu-moment score pipeline.
Loads crops from tests/inputs/weekly_scores/ and asserts that detect_blob()
returns the expected score string for each entry in manifest.json.

Skip conditions:
  - templates missing  -> pytest.skip (rebuild: python debugs/score_detect.py --build)
  - manifest missing   -> pytest.skip
  - crop PNG missing   -> pytest.skip (per parametrized case)
"""
from __future__ import annotations
import json
from pathlib import Path
import cv2
import pytest

from gfl2.score_ocr import TEMPLATES_F, detect_blob

_ROOT         = Path(__file__).parent.parent
_SCORE_SET    = _ROOT / "tests" / "inputs" / "weekly_scores"
_MANIFEST     = _SCORE_SET / "manifest.json"


def _load_manifest():
    if not _MANIFEST.exists():
        return []
    return json.loads(_MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def templates():
    if not TEMPLATES_F.exists():
        pytest.skip(
            f"Digit templates not found: {TEMPLATES_F}\n"
            "Run: python debugs/score_detect.py --build"
        )
    return json.loads(TEMPLATES_F.read_text(encoding="utf-8"))


_ENTRIES = _load_manifest()


@pytest.mark.parametrize("entry", _ENTRIES, ids=[e["key"] for e in _ENTRIES])
def test_score_blob(templates, entry):
    crop_path = _SCORE_SET / entry["path"]
    if not crop_path.exists():
        pytest.skip(f"crop not found: {entry['path']}")
    crop = cv2.imread(str(crop_path))
    if crop is None:
        pytest.skip(f"could not read: {entry['path']}")

    detected = detect_blob(crop, templates)
    assert detected == entry["expected"], (
        f"{entry['key']}: expected {entry['expected']!r}, got {detected!r}"
    )
