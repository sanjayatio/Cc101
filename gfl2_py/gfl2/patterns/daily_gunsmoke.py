# -*- coding: utf-8 -*-
"""
daily_gunsmoke.py - Daily Gunsmoke (Challenge Points) report parser.

Output format: JavaScript constant accumulated into daily_gunsmoke.js.

    const DAILY_GUNSMOKE = [
      ["gm_d_20250929",1,4635,"2263K",39170,7,[
        ["Qiongjiu",   38.97,882107,24.22,186,14.58, 5716, 0,    0],
        ...
      ]],
      ...
    ];

Usage (folder mode, recommended):
    python main.py gm/ --pattern daily_gunsmoke

Usage (single file):
    python main.py gm/gm_d_20250929.png --pattern daily_gunsmoke
"""
from __future__ import annotations
import re
import json
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
import pytesseract

# ── Timing accumulator ────────────────────────────────────────────────────────

_T: dict[str, list[float]] = defaultdict(list)

def _record(label: str, elapsed: float) -> None:
    _T[label].append(elapsed)

def print_timing_summary(n_images: int, wall: float) -> None:
    """Print accumulated OCR timing for the daily_gunsmoke pipeline."""
    order = [
        "extract_header",
        "score/bright",
        "stats_row",
        "extract_doll_rows",
        "name",
        "stat_cell/psm6",
        "stat_cell/psm4",
    ]
    labels = order + [k for k in sorted(_T) if k not in order]
    print(f"\n{'─'*56}")
    print(f"daily_gunsmoke OCR timing  ({n_images} image{'s' if n_images != 1 else ''},"
          f" {wall:.2f}s wall)")
    for label in labels:
        if label not in _T:
            continue
        times  = _T[label]
        total  = sum(times)
        avg_ms = total / len(times) * 1000
        print(f"  {label:<24}  {total:6.2f}s  {len(times):5d}×  avg {avg_ms:6.1f}ms")
    print(f"{'─'*56}")

# ── Layout (proportions of panel width / image height) ───────────────────────
HEADER_BAR_Y0  = 0.010
HEADER_BAR_Y1  = 0.082
STATS_ROW_Y0   = 0.082
STATS_ROW_Y1   = 0.170
DOLL_ROWS_Y0   = 0.234
N_DOLL_ROWS    = 5

NAME_X0, NAME_X1   = 0.083, 0.220
COL1_X0, COL1_X1   = 0.192, 0.384   # Damage dealt
COL2_X0, COL2_X1   = 0.376, 0.575   # Stability broken
COL3_X0, COL3_X1   = 0.575, 0.767   # Damage taken
COL4_X0, COL4_X1   = 0.767, 1.000   # Healed
SCORE_X0, SCORE_X1 = 0.820, 1.000

CELL_BOTTOM_TRIM = 0.15


# ── Data model ────────────────────────────────────────────────────────────────

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
        rows   = ",\n".join(d.to_js(indent) for d in self.dolls)
        return f"{header}{rows}]]"


# ── JS file I/O ───────────────────────────────────────────────────────────────

JS_VAR = "DAILY_GUNSMOKE"

def _load_js(path: Path) -> list[ReportEntry]:
    """Parse existing JS file; return list of ReportEntry for dedup."""
    if not path.exists():
        return []
    # We don't full-parse the JS; just extract (filename, report_idx) keys
    content = path.read_text(encoding="utf-8")
    keys = re.findall(r'\["([^"]+)",\s*(\d+),', content)
    return [(k[0], int(k[1])) for k in keys]   # type: ignore


def save_js(entries: list[ReportEntry], path: Path) -> None:
    """Write / update the JS constant file with new entries."""
    existing_keys = set(_load_js(path))
    new_entries   = [e for e in entries if e.key not in existing_keys]

    if not new_entries:
        return 0  # nothing to add

    if path.exists():
        # Append before the closing "];":
        content = path.read_text(encoding="utf-8").rstrip()
        # Remove trailing "];" then re-add with new entries
        if content.endswith("];"):
            content = content[:-2].rstrip()
            # If there are existing entries, add a comma
            if content.rstrip().endswith("]"):
                content += ","
            new_block = ",\n".join(e.to_js() for e in new_entries)
            content   = f"{content}\n{new_block}\n];"
        else:
            # Malformed — overwrite
            content = _build_js(entries)
    else:
        content = _build_js(new_entries)

    path.write_text(content + "\n", encoding="utf-8")
    return len(new_entries)


def _build_js(entries: list[ReportEntry]) -> str:
    body = ",\n".join(e.to_js() for e in entries)
    return f"const {JS_VAR} = [\n{body}\n];"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _crop(img, x0f, x1f, y0f=0.0, y1f=1.0):
    h, w = img.shape[:2]
    return img[int(h*y0f):int(h*y1f), int(w*x0f):int(w*x1f)]


def _ocr_raw(region, cfg="--psm 6"):
    if region.size == 0:
        return ""
    up   = cv2.resize(region, (0, 0), fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY) if up.ndim == 3 else up
    return pytesseract.image_to_string(gray, config=cfg).strip()


def _ocr_bright(region, threshold=170, cfg="--psm 7"):
    if region.size == 0:
        return ""
    up   = cv2.resize(region, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY) if up.ndim == 3 else up
    _, t = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return pytesseract.image_to_string(255 - t, config=cfg).strip()


def _parse_pct_val(txt: str):
    m   = re.search(r"([\d.]+)\s*%", txt)
    pct = m.group(1) if m else None
    nums = re.findall(r"\d+", txt)
    if not nums:
        return pct, None
    pct_digits = pct.replace(".", "") if pct else ""
    joined     = "".join(nums)
    after      = joined[len(pct_digits):]
    val_m      = re.search(r"\d+", after)
    # Only fall back to nums[-1] when there ARE leftover digits after the pct
    # fragment — otherwise every digit came from the percentage itself and
    # nums[-1] would be a spurious fragment (e.g. "33" from "13.33%").
    val        = val_m.group(0) if val_m else (nums[-1] if (after and nums) else None)
    return pct, val


# ── Stat-cell blob OCR engine (lazy-loaded) ───────────────────────────────────

_STAT_OCR = None   # StatOcr instance, or False if templates not available

def _get_stat_ocr():
    global _STAT_OCR
    if _STAT_OCR is None:
        try:
            from gfl2.stat_ocr import StatOcr
            _STAT_OCR = StatOcr.load()
        except Exception:
            _STAT_OCR = False   # disable blob pipeline
    return _STAT_OCR if _STAT_OCR is not False else None


def _extract_stat_cell(cell: np.ndarray):
    h    = cell.shape[0]
    crop = cell[:int(h * (1 - CELL_BOTTOM_TRIM)), :]

    # ── Pass 0: blob pipeline (fast, Tesseract-free) ─────────────────────
    engine = _get_stat_ocr()
    if engine is not None:
        t0 = time.perf_counter()
        pct, val = engine.read(crop)
        _record("stat_cell/blob", time.perf_counter() - t0)
        if pct is not None and val is not None:
            return pct, val
        # Partial result: keep what the blob pipeline gave, fill gaps via OCR

    # ── Pass 1: Tesseract PSM 6 fallback ─────────────────────────────────
    t0 = time.perf_counter(); txt = _ocr_raw(crop, "--psm 6"); _record("stat_cell/psm6", time.perf_counter() - t0)
    pct, val = _parse_pct_val(txt)
    if val is None or len(val) <= 2:
        t0 = time.perf_counter(); txt2 = _ocr_raw(crop, "--psm 4"); _record("stat_cell/psm4", time.perf_counter() - t0)
        pct2, val2 = _parse_pct_val(txt2)
        if val2 and (val is None or len(val2) > len(val)):
            val = val2
    return pct, val


def _extract_name(cell: np.ndarray) -> Optional[str]:
    t0 = time.perf_counter(); txt = _ocr_raw(cell, "--psm 7"); _record("name", time.perf_counter() - t0)
    clean = re.sub(r"[^A-Za-z0-9_\-\. ]", "", txt).strip()
    words = clean.split()
    while words and len(words[0]) <= 2 and not words[0][0].isupper():
        words.pop(0)
    return " ".join(words) or None


# ── Panel detection ───────────────────────────────────────────────────────────

def _split_panels(image: np.ndarray) -> list[np.ndarray]:
    """Split a 2-panel image at the bright column between the two panels.

    Only splits if the brightest column in the middle third of the top bar
    lands between 40% and 60% of the image width — a genuine 2-panel layout
    always produces two roughly equal-width panels.  A bright UI separator
    inside a single panel (e.g. at 33%) is ignored and the full image is
    returned as one panel.
    """
    h, w  = image.shape[:2]
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bar   = gray[:int(h * 0.10), :]
    third = w // 3
    mid   = third + int(np.argmax(bar.mean(axis=0)[third: 2*third]))
    if mid < w * 0.40 or mid > w * 0.60:
        return [image]
    return [image[:, :mid], image[:, mid:]]


# ── Header & row extraction ───────────────────────────────────────────────────

def _extract_header(panel: np.ndarray) -> dict:
    hdr_t0 = time.perf_counter()
    # Score: white text on dark teal — try multiple thresholds to handle
    # varying image brightness across different captures.
    sc  = _crop(panel, SCORE_X0, SCORE_X1, HEADER_BAR_Y0, HEADER_BAR_Y1)
    sm  = None
    for thresh in (150, 160, 170, 180, 190):
        t0 = time.perf_counter(); stxt = _ocr_bright(sc, thresh, "--psm 7 -c tessedit_char_whitelist=0123456789"); _record("score/bright", time.perf_counter() - t0)
        sm = re.search(r"\d{3,}", stxt)
        if sm:
            break

    st  = _crop(panel, 0.0, 1.0, STATS_ROW_Y0, STATS_ROW_Y1)
    t0 = time.perf_counter(); txt = _ocr_raw(st, "--psm 6"); _record("stats_row", time.perf_counter() - t0)

    def find(pat):
        m = re.search(pat, txt, re.IGNORECASE)
        return m.group(1).replace(",", "") if m else None

    _record("extract_header", time.perf_counter() - hdr_t0)
    return {
        "score":           sm.group(0) if sm else None,
        "dmg_dealt_total": find(r"[Dd]amage\s*[Dd]ealt\s+([\d,.KMkm]+)"),
        "dmg_taken_total": find(r"[Dd]amage\s*[Tt]aken\s+([\d,.]+)"),
        "combat_turns":    find(r"[Cc]ombat\s*[Tt]urns?\s*(\d+)"),
    }


def _extract_doll_rows(panel: np.ndarray) -> list[DollRow]:
    rows_t0 = time.perf_counter()
    h, w    = panel.shape[:2]
    y0      = int(h * DOLL_ROWS_Y0)
    row_h   = (h - y0) // N_DOLL_ROWS
    rows    = []
    for i in range(N_DOLL_ROWS):
        row        = panel[y0 + i*row_h : y0 + (i+1)*row_h, :]
        name       = _extract_name(_crop(row, NAME_X0, NAME_X1))
        dp, dv     = _extract_stat_cell(_crop(row, COL1_X0, COL1_X1))
        sp, sv     = _extract_stat_cell(_crop(row, COL2_X0, COL2_X1))
        tp, tv     = _extract_stat_cell(_crop(row, COL3_X0, COL3_X1))
        hp, hv     = _extract_stat_cell(_crop(row, COL4_X0, COL4_X1))
        rows.append(DollRow(name, dp, dv, sp, sv, tp, tv, hp, hv))
    _record("extract_doll_rows", time.perf_counter() - rows_t0)
    return rows


# ── Public API ────────────────────────────────────────────────────────────────

def parse(image: np.ndarray, filename: str = "unknown", **_) -> list[ReportEntry]:
    """Return a list of ReportEntry objects (one per panel)."""
    panels  = _split_panels(image)
    entries = []
    for idx, panel in enumerate(panels):
        hdr = _extract_header(panel)
        entries.append(ReportEntry(
            filename        = filename,
            report_idx      = idx + 1,
            score           = hdr.get("score"),
            dmg_dealt_total = hdr.get("dmg_dealt_total"),
            dmg_taken_total = hdr.get("dmg_taken_total"),
            combat_turns    = hdr.get("combat_turns"),
            dolls           = _extract_doll_rows(panel),
        ))
    return entries
