# -*- coding: utf-8 -*-
"""
buff_ocr.py - OCR-based buff name recognition.
"""
from __future__ import annotations
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pytesseract

from gfl2.trace import timed

ASSETS_DIR     = Path(__file__).parent.parent / "assets"
OCR_SCALE      = 5
OCR_THRESHOLDS = (190, 200, 210, 220)
OCR_MIN_CONF   = 50
MIN_WORD_LEN   = 4
MIN_THRESHOLDS = 1


def _is_valid_name(name: str) -> bool:
    words = re.findall(r"[A-Za-z]+", name)
    return len(words) >= 2 and all(len(w) >= MIN_WORD_LEN for w in words)


def _is_guid(s: str) -> bool:
    c = s.replace("-", "")
    return len(c) == 32 and all(x in "0123456789abcdefABCDEF" for x in c)


def _known_names() -> list[str]:
    d = ASSETS_DIR / "buff"
    d.mkdir(parents=True, exist_ok=True)
    names = [p.stem.lstrip("_") for p in d.glob("*.png") if not _is_guid(p.stem)]
    return [n for n in names if _is_valid_name(n)]


@timed()
def _words_by_position(cell: np.ndarray) -> list[str]:
    up   = cv2.resize(cell, (0, 0), fx=OCR_SCALE, fy=OCR_SCALE, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY)

    word_ys:     dict[str, list[int]] = defaultdict(list)
    word_thresh: dict[str, set]       = defaultdict(set)

    for t in OCR_THRESHOLDS:
        _, thresh = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
        data = pytesseract.image_to_data(thresh, config="--psm 11 --oem 1",
                                         output_type=pytesseract.Output.DICT)
        for i, word in enumerate(data["text"]):
            clean = re.sub(r"[^A-Za-z]", "", word)
            if clean and len(clean) >= MIN_WORD_LEN and int(data["conf"][i]) >= OCR_MIN_CONF:
                word_ys[clean].append(data["top"][i])
                word_thresh[clean].add(t)

    stable = {w for w, ts in word_thresh.items() if len(ts) >= MIN_THRESHOLDS}
    if not stable:
        return []

    return sorted(stable, key=lambda w: sorted(word_ys[w])[len(word_ys[w]) // 2])


def _save_asset(name: str, cell: np.ndarray) -> None:
    if not _is_valid_name(name):
        return
    d = ASSETS_DIR / "buff"
    for stem in (name, f"_{name}"):
        if list(d.glob(f"{stem}.png")):
            return
    path = d / f"_{name}.png"
    cv2.imwrite(str(path), cell)
    print(f"[buff_ocr] Auto-saved new buff -> {path.name}", file=sys.stderr)


@timed()
def translate(cell: Optional[np.ndarray]) -> Optional[str]:
    if cell is None or cell.size == 0:
        return None

    known = _known_names()
    words = _words_by_position(cell)
    if not words:
        return None

    words_lower = [w.lower() for w in words]
    words_set   = set(words_lower)

    for name in known:
        name_words_lower = re.findall(r"[a-z]+", name.lower())
        name_set = set(name_words_lower)
        if not (name_set and name_set <= words_set):
            continue
        ocr_pos  = {w: j for j, w in enumerate(words_lower)}
        name_pos = [ocr_pos[w] for w in name_words_lower if w in ocr_pos]
        if name_pos == sorted(name_pos):
            return name

    name = " ".join(words)
    if _is_valid_name(name):
        _save_asset(name, cell)
        return name

    return None
