#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
populate_doll_assets.py
-----------------------
Extracts doll portrait crops from Daily Gunsmoke (Challenge Points) images
and saves them to assets/dolls/.  No manual renaming required.

Detection pipeline:
  1. Split image into panels (1 or 2 side-by-side reports).
  2. Find up to 5 doll-frame bounding boxes per panel by scanning the left
     ~15% for large, roughly-square dark blobs (the portrait squares).
  3. Use the FIRST frame as the anchor to derive the name-column position.
  4. Crop each portrait by removing the uniform background, then taking the
     tight bounding box of the remaining content.

Asset management:
  - New doll:  saved as _Name.png.
  - Stored asset has borrowed indicator but new frame does NOT:
      replace with the cleaner version.
  - Same name, visually different appearance (pHash distance > VARIANT_THRESH):
      saved as _Name (1).png, _Name (2).png, …  (only if not a duplicate of
      any existing variant).
  - Already have this exact appearance: skip.

Usage:
    python populate_doll_assets.py <folder>       # all *.png files
    python populate_doll_assets.py image.png      # single image
"""
from __future__ import annotations
import sys, re
sys.dont_write_bytecode = True

from pathlib import Path
import cv2
import numpy as np
import pytesseract
import shutil

if not shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from gfl2.patterns.daily_gunsmoke import _split_panels

ASSETS_DOLLS    = Path(__file__).parent / "assets" / "dolls"
PORTRAIT_NORM   = 128       # output size (px)
SEARCH_X1       = 0.25      # left fraction to search for frames
BG_DELTA        = 30        # brightness delta from background = content
FRAME_MIN_DIM   = 40        # minimum frame width/height
FRAME_MIN_SQ    = 0.70      # minimum squareness (min/max side ratio)
VARIANT_THRESH  = 32        # pHash distance above which = new variant
NAME_W_FRAC     = 0.14      # name column width as fraction of panel width

_VALID_RE = re.compile(r"^[A-Z][A-Za-z0-9 \-_\.]{2,}$")


def _is_valid(name: str) -> bool:
    return bool(name and _VALID_RE.match(name) and len(name) >= 3)


def _levenshtein(a: str, b: str) -> int:
    """Simple edit distance."""
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            prev, dp[j] = dp[j], prev if a[i-1]==b[j-1] else 1 + min(prev, dp[j], dp[j-1])
    return dp[n]


def _known_names() -> list[str]:
    """Return all doll names currently in assets/dolls/."""
    names = []
    for p in ASSETS_DOLLS.glob("_[A-Z]*.png"):
        if "(" not in p.stem:   # skip variants
            names.append(p.stem.lstrip("_"))
    return names


def _fuzzy_correct(name: str, max_dist: int = 2) -> str:
    """
    If `name` is within `max_dist` edits of a known doll name, return the
    known name.  This corrects OCR errors like 'Sharkty' → 'Sharkry'.
    """
    known = _known_names()
    for kn in known:
        if _levenshtein(name.lower(), kn.lower()) <= max_dist:
            return kn
    return name


# ── pHash ─────────────────────────────────────────────────────────────────────

def _phash(img: np.ndarray) -> int:
    gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    dct     = cv2.dct(np.float32(resized))
    dct_low = dct[:8, :8]
    bits    = (dct_low >= np.median(dct_low)).flatten()
    h = 0
    for b in bits:
        h = (h << 1) | int(b)
    return h


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


# ── Borrowed indicator ────────────────────────────────────────────────────────

def _has_borrowed(portrait: np.ndarray) -> bool:
    h, w   = portrait.shape[:2]
    region = portrait[:int(h * 0.30), int(w * 0.55):]
    hsv    = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    yellow = ((hsv[:,:,0] >= 20) & (hsv[:,:,0] <= 35) &
              (hsv[:,:,1] > 100) & (hsv[:,:,2] > 80))
    return yellow.sum() > 20


# ── Frame detection ───────────────────────────────────────────────────────────

def _find_frames(panel: np.ndarray,
                 debug_path: str | None = None) -> list[tuple[int,int,int,int]]:
    """
    Find up to 5 doll-frame bounding boxes in the left SEARCH_X1 of the panel.
    Returns list of (x, y, w, h) sorted by y (top to bottom).
    If debug_path is set, saves an annotated image there.
    """
    h, w    = panel.shape[:2]
    region  = panel[:, :int(w * SEARCH_X1)]
    gray    = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    bg      = int(np.argmax(np.bincount(gray.flatten())))
    mask    = (np.abs(gray.astype(int) - bg) > BG_DELTA).astype(np.uint8) * 255

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    all_sq  = []
    frames  = []
    for c in cnts:
        x, y, cw, ch = cv2.boundingRect(c)
        if cw < FRAME_MIN_DIM or ch < FRAME_MIN_DIM:
            continue
        sq = min(cw, ch) / max(cw, ch)
        all_sq.append((x, y, cw, ch, sq))
        if sq < FRAME_MIN_SQ:
            continue
        frames.append((x, y, cw, ch))

    frames.sort(key=lambda b: b[1])
    frames = frames[:5]

    if debug_path:
        vis = panel.copy()
        # Draw all square-like candidates (yellow) and accepted frames (green)
        for x, y, cw, ch, sq in all_sq:
            color = (0, 255, 0) if (min(cw,ch)/max(cw,ch) >= FRAME_MIN_SQ) else (0, 200, 255)
            cv2.rectangle(vis, (x, y), (x+cw, y+ch), color, 2)
        for i, (x, y, cw, ch) in enumerate(frames):
            cv2.putText(vis, str(i), (x+2, y+14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imwrite(debug_path, vis)
        print(f"  [debug] panel {w}x{h}  bg={bg}  candidates={len(all_sq)}  "
              f"frames={len(frames)} → {debug_path}")

    return frames


# ── Portrait crop ─────────────────────────────────────────────────────────────

def _crop_portrait(panel: np.ndarray,
                   fx: int, fy: int, fw: int, fh: int) -> np.ndarray:
    """
    Return the portrait crop for the frame at (fx, fy, fw, fh).

    Strategy: take the frame region from the panel, then remove the uniform
    background colour to find the tight bounding box of the actual portrait
    content.  Normalise to PORTRAIT_NORM × PORTRAIT_NORM with LANCZOS.
    """
    ph, pw = panel.shape[:2]
    # Slightly enlarge the search area to catch any clipped edges
    pad  = 3
    x0   = max(0, fx - pad); x1 = min(pw, fx + fw + pad)
    y0   = max(0, fy - pad); y1 = min(ph, fy + fh + pad)
    crop = panel[y0:y1, x0:x1]

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    bg   = int(np.argmax(np.bincount(gray.flatten())))
    fmask = (np.abs(gray.astype(int) - bg) > BG_DELTA)

    if not fmask.any():
        return cv2.resize(crop, (PORTRAIT_NORM, PORTRAIT_NORM),
                          interpolation=cv2.INTER_LANCZOS4)

    # Tight bounding box of content
    rows = fmask.any(axis=1)
    cols = fmask.any(axis=0)
    ry0  = rows.argmax()
    ry1  = len(rows) - rows[::-1].argmax()
    cx0  = cols.argmax()
    cx1  = len(cols) - cols[::-1].argmax()

    tight = crop[ry0:ry1, cx0:cx1]
    if tight.size == 0:
        tight = crop

    return cv2.resize(tight, (PORTRAIT_NORM, PORTRAIT_NORM),
                      interpolation=cv2.INTER_LANCZOS4)


# ── Name OCR ──────────────────────────────────────────────────────────────────

def _ocr_name_at(panel: np.ndarray,
                 name_x0: int, name_x1: int,
                 row_y0: int,  row_y1: int) -> str | None:
    """OCR the doll name from the cell to the right of its portrait."""
    cell  = panel[row_y0:row_y1, name_x0:name_x1]
    up    = cv2.resize(cell, (0, 0), fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
    gray  = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY)
    txt   = pytesseract.image_to_string(gray, config="--psm 7").strip()
    clean = re.sub(r"[^A-Za-z0-9_\-\. ]", "", txt).strip()
    words = clean.split()
    # Drop leading noise: short token not starting with uppercase (e.g. "s Nikketa")
    while words and len(words[0]) <= 2 and not words[0][0].isupper():
        words.pop(0)
    # Drop trailing noise: short token or badge pattern like "w5", "s3", "Lv"
    _BADGE = re.compile(r"^[A-Za-z]{1,2}\d*$")
    while words and len(words[-1]) <= 3 and _BADGE.match(words[-1]):
        words.pop()
    return " ".join(words) or None


# ── Asset management ──────────────────────────────────────────────────────────

def _existing_hashes(base_name: str) -> list[int]:
    hashes = []
    for p in ASSETS_DOLLS.glob(f"_{base_name}*.png"):
        img = cv2.imread(str(p))
        if img is not None:
            hashes.append(_phash(img))
    return hashes


def _next_variant_path(base_name: str) -> Path:
    n = 1
    while True:
        p = ASSETS_DOLLS / f"_{base_name} ({n}).png"
        if not p.exists():
            return p
        n += 1


def _save_portrait(name: str, portrait: np.ndarray) -> str:
    ASSETS_DOLLS.mkdir(parents=True, exist_ok=True)
    base_path = ASSETS_DOLLS / f"_{name}.png"
    new_hash  = _phash(portrait)

    if not base_path.exists():
        cv2.imwrite(str(base_path), portrait)
        return f"new → {base_path.name}"

    stored = cv2.imread(str(base_path))
    if stored is not None and _has_borrowed(stored) and not _has_borrowed(portrait):
        cv2.imwrite(str(base_path), portrait)
        return f"upgraded (removed borrowed) → {base_path.name}"

    existing = _existing_hashes(name)
    if all(_hamming(new_hash, eh) > VARIANT_THRESH for eh in existing):
        dest = _next_variant_path(name)
        cv2.imwrite(str(dest), portrait)
        return f"variant → {dest.name}"

    return "skip"


# ── Per-panel processing ──────────────────────────────────────────────────────

def _process_panel(panel: np.ndarray,
                   debug_prefix: str | None = None) -> list[tuple[str, str]]:
    """Return [(name, action), ...] for each doll found in the panel."""
    h, w  = panel.shape[:2]
    frames = _find_frames(panel, debug_path=debug_prefix)
    if not frames:
        return []

    # Anchor = first frame; derive name column from it
    ax, ay, aw, ah = frames[0]
    name_x0 = ax + aw + 2                         # just right of frame
    name_x1 = name_x0 + round(w * NAME_W_FRAC)   # ~14% of panel width

    results = []
    for i, (fx, fy, fw, fh) in enumerate(frames):
        # Row boundaries: from frame top to frame bottom
        # Use adjacent frames to estimate row span
        if i + 1 < len(frames):
            next_fy = frames[i + 1][1]
            row_y0  = fy
            row_y1  = next_fy
        else:
            # Last row: use same height as previous gap
            if i > 0:
                gap = frames[i][1] - frames[i-1][1]
            else:
                gap = fh + 2
            row_y0 = fy
            row_y1 = min(h, fy + gap)

        name     = _ocr_name_at(panel, name_x0, name_x1, row_y0, row_y1)
        portrait = _crop_portrait(panel, fx, fy, fw, fh)

        if name and _is_valid(name) and portrait is not None:
            # Correct OCR typos against known doll names (e.g. Sharkty → Sharkry)
            name = _fuzzy_correct(name)
            action = _save_portrait(name, portrait)
            results.append((name, action))

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def process(image_path: Path, debug: bool = False) -> dict[str, str]:
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"  [error] cannot read {image_path}")
        return {}
    panels = _split_panels(image)
    if not panels:
        print(f"  [error] no panels found in {image_path.name}")
        return {}
    actions = {}
    for pi, panel in enumerate(panels):
        dbg = (str(image_path.with_suffix(f".debug_p{pi}.png"))
               if debug else None)
        for name, action in _process_panel(panel, debug_prefix=dbg):
            if name not in actions or "skip" in actions.get(name, ""):
                actions[name] = action
    return actions


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    debug  = "--debug" in sys.argv
    args   = [a for a in sys.argv[1:] if not a.startswith("-")]
    target = Path(args[0])
    images = sorted(target.glob("*.png")) if target.is_dir() else [target]

    if not images:
        print(f"No *.png files found in {target}")
        sys.exit(1)

    total = 0
    for img_path in images:
        print(f"\n{img_path.name}:")
        for name, action in sorted(process(img_path, debug=debug).items()):
            marker = "+" if "skip" not in action else " "
            print(f"  {marker} {name:<22} {action}")
            if marker == "+":
                total += 1

    print(f"\nDone. {total} asset(s) written to {ASSETS_DOLLS}")


if __name__ == "__main__":
    main()
