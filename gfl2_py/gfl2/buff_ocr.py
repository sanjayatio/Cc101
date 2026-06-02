# -*- coding: utf-8 -*-
"""
buff_ocr.py - Buff name recognition.

Pipeline (in order):
  1. Projection match (primary, Tesseract-free, ~0.5ms/buff):
     Compare 1D vertical + horizontal projections of the buff crop against
     stored reference projections from assets/buff/.
     If nearest-neighbour distance < PROJ_THRESHOLD → return name.

     Feasibility (tested on 24 crops across 3 screenshots):
       Same-buff distance:      0.000 – 0.023
       Min different-buff dist: 0.034
       Threshold set to 0.030 leaves a comfortable ~0.010 safety margin.

  2. OCR fallback (Tesseract, ~650ms/buff):
     Runs only when projection fails — i.e. when the buff is new (not yet
     in assets) or its projection distance exceeds the threshold.
     Multi-threshold brightness OCR + Y-sorted CamelCase extraction.
     Known names matched order-independently; new names auto-saved.

See docs/decisions.txt §9, §14 and docs/takeaways.txt §9.
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

ASSETS_DIR     = Path(__file__).parent.parent / "assets"
PROJ_SIZE      = 64      # normalise buff crops to this square before projecting
PROJ_THRESHOLD = 0.030   # max projection distance to accept a match
OCR_SCALE      = 5
OCR_THRESHOLDS = (190, 200, 210, 220)
OCR_MIN_CONF   = 50
MIN_WORD_LEN   = 4
MIN_THRESHOLDS = 1


# ── helpers ───────────────────────────────────────────────────────────────────

def _is_guid(s: str) -> bool:
    c = s.replace("-", "")
    return len(c) == 32 and all(x in "0123456789abcdefABCDEF" for x in c)


def _is_valid_name(name: str) -> bool:
    words = re.findall(r"[A-Za-z]+", name)
    return len(words) >= 2 and all(len(w) >= MIN_WORD_LEN for w in words)


def _proj_pair(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(v_projection, h_projection) of img normalised to PROJ_SIZE×PROJ_SIZE."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    norm = cv2.resize(gray, (PROJ_SIZE, PROJ_SIZE),
                      interpolation=cv2.INTER_AREA).astype(float)
    vp = norm.mean(axis=1); vp /= (vp.max() + 1e-8)
    hp = norm.mean(axis=0); hp /= (hp.max() + 1e-8)
    return vp, hp


def _proj_dist(a: tuple, b: tuple) -> float:
    return float((np.mean(np.abs(a[0] - b[0])) + np.mean(np.abs(a[1] - b[1]))) / 2)


def _load_assets() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    d = ASSETS_DIR / "buff"
    d.mkdir(parents=True, exist_ok=True)
    out = {}
    for p in sorted(d.glob("*.png")):
        if _is_guid(p.stem):
            continue
        img = cv2.imread(str(p))
        if img is not None:
            out[p.stem.lstrip("_")] = _proj_pair(img)
    return out


# ── Pipeline 1: projection ────────────────────────────────────────────────────

def _match_projection(cell: np.ndarray) -> Optional[str]:
    assets = _load_assets()
    if not assets:
        return None
    qp    = _proj_pair(cell)
    dists = {name: _proj_dist(qp, ap) for name, ap in assets.items()}
    best  = min(dists, key=dists.get)
    return best if dists[best] < PROJ_THRESHOLD else None


# ── Pipeline 2: OCR ───────────────────────────────────────────────────────────

def _words_by_position(cell: np.ndarray) -> list[str]:
    up   = cv2.resize(cell, (0, 0), fx=OCR_SCALE, fy=OCR_SCALE,
                      interpolation=cv2.INTER_CUBIC)
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


def _majority_suffix(word_lists: list[list[str]]) -> list[str]:
    wls = [wl for wl in word_lists if wl]
    if not wls:
        return []
    min_agree = (len(wls) + 1) // 2
    for n in range(max(len(wl) for wl in wls), 0, -1):
        counts: dict = {}
        for wl in wls:
            if len(wl) >= n:
                key = tuple(wl[-n:])
                counts[key] = counts.get(key, 0) + 1
        if counts:
            best, cnt = max(counts.items(), key=lambda x: x[1])
            if cnt >= min_agree:
                return list(best)
    return []


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


def _match_ocr(cell: np.ndarray) -> Optional[str]:
    """OCR fallback: matches known buffs by word set, auto-saves new ones."""
    known_names = list(_load_assets().keys())

    # Collect alpha strings at each threshold
    up   = cv2.resize(cell, (0, 0), fx=OCR_SCALE, fy=OCR_SCALE,
                      interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY)
    alphas = []
    for t in OCR_THRESHOLDS:
        _, thresh = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
        txt = pytesseract.image_to_data(thresh, config="--psm 11 --oem 1",
                                        output_type=pytesseract.Output.DICT)
        alpha = "".join(
            re.sub(r"[^A-Za-z]", "", txt["text"][i])
            for i in range(len(txt["text"]))
            if re.sub(r"[^A-Za-z]", "", txt["text"][i])
            and len(re.sub(r"[^A-Za-z]", "", txt["text"][i])) >= MIN_WORD_LEN
            and int(txt["conf"][i]) >= OCR_MIN_CONF
        )
        alphas.append(alpha)

    # Pass 1: match known name — words present (order-independent)
    for alpha in alphas:
        spaced       = re.sub(r"([A-Z])", r" \1", alpha).lower()
        words_in_ocr = set(re.findall(r"[a-z]+", spaced))
        for name in known_names:
            name_words = set(re.findall(r"[a-z]+", name.lower()))
            if name_words and name_words <= words_in_ocr:
                return name

    # Pass 2: new buff — Y-position word extraction + majority suffix
    words  = _words_by_position(cell)
    suffix = _majority_suffix([words])
    if suffix:
        name = " ".join(suffix)
        if _is_valid_name(name):
            _save_asset(name, cell)
            return name

    return None


# ── Public API ────────────────────────────────────────────────────────────────

def translate(cell: Optional[np.ndarray]) -> Optional[str]:
    """
    Identify a buff crop.

    Pipeline:
      1. Projection match  — Tesseract-free, ~0.5ms
      2. OCR fallback      — Tesseract, ~650ms (only for new/unknown buffs)
    """
    if cell is None or cell.size == 0:
        return None
    result = _match_projection(cell)
    if result is not None:
        return result
    return _match_ocr(cell)
