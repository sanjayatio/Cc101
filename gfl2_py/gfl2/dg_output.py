# -*- coding: utf-8 -*-
"""
gfl2/dg_output.py — Shared output utilities for Daily Gunsmoke parsers.

Provides:
  - JS data model  (DollRow, ReportEntry) and JS file I/O (save_js)
  - Portrait asset saving  (_save_doll_portrait, _crop_portrait)

Used by daily_gunsmoke.py.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from gfl2.asset_mapper import ASSETS_DIR, _phash, _hamming


# ── JS data model ─────────────────────────────────────────────────────────────

JS_VAR = "DAILY_GUNSMOKE"


@dataclass
class DollRow:
    name:          Optional[str]
    dmg_dealt_pct: Optional[str]
    dmg_dealt_val: Optional[str]
    stab_pct:      Optional[str]
    stab_val:      Optional[str]
    dmg_taken_pct: Optional[str]
    dmg_taken_val: Optional[str]
    healed_pct:    Optional[str]
    healed_val:    Optional[str]

    def to_js(self, indent: str = "    ") -> str:
        def _n(v): return v if v is not None else ""
        def _v(v):
            if v is None or v == "":
                return "null"
            # Values containing '?' are low-confidence partial reads — skip them
            if '?' in v:
                return "null"
            # K/M multiplier suffix (e.g. "4246K" → 4246000)
            km = re.fullmatch(r'(\d+)([KkMm])', v)
            if km:
                mult = 1_000 if km.group(2).upper() == 'K' else 1_000_000
                return str(int(km.group(1)) * mult)
            try:
                f = float(v.replace(",", ""))
                return str(int(f)) if f == int(f) else str(f)
            except ValueError:
                return f'"{v}"'
        fields = [f'"{_n(self.name)}"',
                  _v(self.dmg_dealt_pct), _v(self.dmg_dealt_val),
                  _v(self.stab_pct),      _v(self.stab_val),
                  _v(self.dmg_taken_pct), _v(self.dmg_taken_val),
                  _v(self.healed_pct),    _v(self.healed_val)]
        return f"{indent}  [{', '.join(fields)}]"


@dataclass
class ReportEntry:
    filename:        str       # image stem, e.g. "gm_d_20250929"
    report_idx:      int       # 1 or 2
    score:           Optional[str]
    dmg_dealt_total: Optional[str]
    dmg_taken_total: Optional[str]
    combat_turns:    Optional[str]
    dolls:           list[DollRow]

    @property
    def key(self) -> tuple[str, int]:
        return (self.filename, self.report_idx)

    def to_js(self, indent: str = "  ") -> str:
        def _s(v): return f'"{v}"' if v else "null"
        def _n(v):
            if v is None: return "null"
            try:
                f = float(v.replace(",", ""))
                return str(int(f)) if f == int(f) else str(f)
            except ValueError:
                return f'"{v}"'
        header = (f'{indent}["{self.filename}",{self.report_idx},'
                  f'{_n(self.score)},{_s(self.dmg_dealt_total)},'
                  f'{_n(self.dmg_taken_total)},{_n(self.combat_turns)},[\n')
        rows = ",\n".join(d.to_js(indent) for d in self.dolls)
        return f"{header}{rows}]]"


# ── JS file I/O ───────────────────────────────────────────────────────────────

def _load_js(path: Path) -> list[tuple[str, int]]:
    """Parse existing JS file; return list of (filename, report_idx) keys for dedup."""
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    keys = re.findall(r'\["([^"]+)",\s*(\d+),', content)
    return [(k[0], int(k[1])) for k in keys]


def _build_js(entries: list[ReportEntry]) -> str:
    body = ",\n".join(e.to_js() for e in entries)
    return f"const {JS_VAR} = [\n{body}\n];"


def save_js(entries: list[ReportEntry], path: Path) -> int:
    """Write / append new entries to the JS constant file.  Returns count added."""
    existing_keys = set(_load_js(path))
    new_entries   = [e for e in entries if e.key not in existing_keys]
    if not new_entries:
        return 0
    if path.exists():
        content = path.read_text(encoding="utf-8").rstrip()
        if content.endswith("];"):
            content = content[:-2].rstrip()
            if content.rstrip().endswith("]"):
                content += ","
            new_block = ",\n".join(e.to_js() for e in new_entries)
            content   = f"{content}\n{new_block}\n];"
        else:
            content = _build_js(new_entries)
    else:
        content = _build_js(new_entries)
    path.write_text(content + "\n", encoding="utf-8")
    return len(new_entries)


# ── Portrait save utilities ───────────────────────────────────────────────────

PORTRAIT_NORM  = 128   # normalised portrait output size in pixels
FRAME_BG_DELTA = 30    # brightness delta to separate content from background

# Borrow indicator: yellow icon in the top-right corner of the portrait.
BORROW_H_FRAC  = 0.35
BORROW_X_FRAC  = 0.55

# pHash distance above which a frame is treated as a new visual variant.
VARIANT_THRESH = 32

# In-memory pHash cache: { stem: [hash, ...] } — populated lazily per name.
_HASH_CACHE: dict[str, list[int]] = {}

# Per-image portrait action log: list of (name, status) tuples.
# Populated by _save_doll_portrait; cleared by flush_portrait_log().
_PORTRAIT_LOG: list[tuple[str, str]] = []


def flush_portrait_log() -> list[tuple[str, str]]:
    """Return and clear the portrait action log accumulated since the last flush."""
    result = list(_PORTRAIT_LOG)
    _PORTRAIT_LOG.clear()
    return result


def _has_borrow_indicator(portrait: np.ndarray) -> bool:
    """Return True when the yellow 'borrowed doll' icon is visible in the top-right."""
    h, w   = portrait.shape[:2]
    region = portrait[:int(h * BORROW_H_FRAC), int(w * BORROW_X_FRAC):]
    if region.size == 0:
        return False
    hsv    = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    yellow = ((hsv[:, :, 0] >= 20) & (hsv[:, :, 0] <= 35) &
              (hsv[:, :, 1] >  100) & (hsv[:, :, 2] >  80))
    return int(yellow.sum()) > 20


def _cache_for(dolls_dir: Path, stem: str) -> list[int]:
    """Return (lazily populated) cached pHashes for all variants of stem."""
    if stem not in _HASH_CACHE:
        hashes = []
        for p in sorted(dolls_dir.glob(f"_{stem}*.png")):
            img = cv2.imread(str(p))
            if img is not None:
                hashes.append(_phash(img))
        _HASH_CACHE[stem] = hashes
    return _HASH_CACHE[stem]


def _next_variant_path(dolls_dir: Path, stem: str) -> Path:
    n = 1
    while True:
        p = dolls_dir / f"_{stem} ({n}).png"
        if not p.exists():
            return p
        n += 1


def normalize_portrait(cell: Optional[np.ndarray]) -> Optional[np.ndarray]:
    """Normalize a weekly doll column crop to PORTRAIT_NORM × PORTRAIT_NORM.

    The weekly pipeline yields a column slice whose width equals the portrait
    size (the portrait is square) but whose height is the full row height.
    We extract a fw×fw square centred vertically, then resize to PORTRAIT_NORM.
    Used by weekly_gunsmoke so both pipelines share the same asset library.
    """
    if cell is None or cell.size == 0:
        return None
    h, w = cell.shape[:2]
    fw = w                        # portrait fills the full column width
    y0 = max(0, (h - fw) // 2)   # centre vertically in the row crop
    square = cell[y0:y0 + fw, 0:fw]
    if square.size == 0:
        square = cell
    return cv2.resize(square, (PORTRAIT_NORM, PORTRAIT_NORM),
                      interpolation=cv2.INTER_LANCZOS4)


def _crop_portrait(panel: np.ndarray,
                   fx: int, fy: int, fw: int, fh: int) -> np.ndarray:
    """Tight-crop the portrait at (fx, fy, fw, fh) and normalise to PORTRAIT_NORM.

    Pads slightly, removes uniform background to find content bbox, then
    resizes to PORTRAIT_NORM × PORTRAIT_NORM with LANCZOS.
    """
    ph, pw = panel.shape[:2]
    pad = 3
    x0 = max(0, fx - pad);  x1 = min(pw, fx + fw + pad)
    y0 = max(0, fy - pad);  y1 = min(ph, fy + fh + pad)
    crop = panel[y0:y1, x0:x1]

    gray  = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    bg    = int(np.argmax(np.bincount(gray.flatten())))
    fmask = np.abs(gray.astype(int) - bg) > FRAME_BG_DELTA

    if fmask.any():
        rows = fmask.any(axis=1)
        cols = fmask.any(axis=0)
        ry0  = rows.argmax()
        ry1  = len(rows) - rows[::-1].argmax()
        cx0  = cols.argmax()
        cx1  = len(cols) - cols[::-1].argmax()
        tight = crop[ry0:ry1, cx0:cx1]
        if tight.size > 0:
            crop = tight

    return cv2.resize(crop, (PORTRAIT_NORM, PORTRAIT_NORM),
                      interpolation=cv2.INTER_LANCZOS4)


def _save_doll_portrait(name: str, portrait: np.ndarray) -> str:
    """Save / upgrade / extend the doll asset library from a portrait crop.

    Naming convention (all in assets/dolls/):
        _Name.png          primary reference (clean preferred)
        _Name (1).png      alternate visual variant
        _Name (2).png      ...

    Rules:
    - If any existing variant is within VARIANT_THRESH pHash distance:
        Replace only when stored has borrow indicator and new frame does not.
        Otherwise skip.
    - If no close match exists, save as a new variant:
        Use _Name.png when free, else _Name (N).png auto-increment.

    Returns a status string: "new", "upgraded", "variant", or "skip".
    """
    stem = re.sub(r'[\\/:*?"<>|]', "", name).strip()
    if not stem:
        return "skip"

    dolls_dir = ASSETS_DIR / "dolls"
    dolls_dir.mkdir(parents=True, exist_ok=True)

    new_hash  = _phash(portrait)
    base_path = dolls_dir / f"_{stem}.png"

    if not base_path.exists():
        cv2.imwrite(str(base_path), portrait)
        _cache_for(dolls_dir, stem).append(new_hash)
        print(f"[dg] Saved new doll asset: _{stem}.png", file=sys.stderr)
        _PORTRAIT_LOG.append((name, "new"))
        return "new"

    existing = _cache_for(dolls_dir, stem)
    if any(_hamming(new_hash, eh) <= VARIANT_THRESH for eh in existing):
        stored = cv2.imread(str(base_path))
        if stored is not None:
            if _has_borrow_indicator(stored) and not _has_borrow_indicator(portrait):
                cv2.imwrite(str(base_path), portrait)
                print(f"[dg] Upgraded _{stem}.png (removed borrow indicator)",
                      file=sys.stderr)
                _PORTRAIT_LOG.append((name, "upgraded"))
                return "upgraded"
        _PORTRAIT_LOG.append((name, "skip"))
        return "skip"

    dest = _next_variant_path(dolls_dir, stem)
    cv2.imwrite(str(dest), portrait)
    existing.append(new_hash)
    print(f"[dg] Saved new variant: {dest.name}", file=sys.stderr)
    _PORTRAIT_LOG.append((name, "variant"))
    return "variant"

# ── Doll name OCR utilities ───────────────────────────────────────────────────

from gfl2.asset_mapper import ASSETS_DIR as _ASSETS_DIR_NAME   # already imported above

_DOLL_NAME_OCR = None   # DollNameOcr instance, False if absent, None = not tried

# Accumulator for (name_cell, name) pairs collected during OCR slow-path runs.
_NEW_CROPS: list = []   # list[tuple[np.ndarray, str]]


def _get_doll_name_ocr():
    global _DOLL_NAME_OCR
    if _DOLL_NAME_OCR is None:
        try:
            from gfl2.doll_name_ocr import DollNameOcr
            loaded = DollNameOcr.load()
            _DOLL_NAME_OCR = loaded if loaded is not None else False
        except Exception:
            _DOLL_NAME_OCR = False
    return _DOLL_NAME_OCR if _DOLL_NAME_OCR is not False else None


def flush_name_templates() -> None:
    """Persist projection templates updated from OCR-confirmed name crops."""
    global _DOLL_NAME_OCR, _NEW_CROPS
    if not _NEW_CROPS:
        return
    ocr = _get_doll_name_ocr()
    crops, _NEW_CROPS = _NEW_CROPS, []
    if ocr is not None:
        ocr.update(crops)
    else:
        from gfl2.doll_name_ocr import DollNameOcr
        DollNameOcr.build(crops)
        _DOLL_NAME_OCR = None   # force reload on next call


def _known_doll_names() -> list:
    """Return all known doll names from assets/dolls/ (_-prefixed, no variants)."""
    dolls_dir = ASSETS_DIR / "dolls"
    names = []
    for p in dolls_dir.glob("_[A-Z]*.png"):
        if "(" not in p.stem:
            names.append(p.stem.lstrip("_"))
    return names


def _levenshtein(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            prev, dp[j] = dp[j], prev if a[i-1] == b[j-1] else 1 + min(prev, dp[j], dp[j-1])
    return dp[n]


def _fuzzy_correct(name: str) -> str:
    """Snap an OCR name to the nearest known doll name when within edit distance."""
    max_dist = 3 if len(name) >= 7 else 2
    known    = _known_doll_names()
    for kn in known:
        if _levenshtein(name.lower(), kn.lower()) <= max_dist:
            return kn
    return name
