#!/usr/bin/env python3
"""
render_debug.py - Render a parsed CSV back as a compact debug image.

Layout per row:
  [date (small, above buff when it changes)]
  [buff icon+name] [doll1..5 icons+names] [owner / score]

Date is printed above the buff icon only when it changes — no full-width
banner row, so the image is both narrower and shorter than before.
Owner name and score share the rightmost column.

Usage: python render_debug.py <csv_path>
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import shutil as _shutil, pathlib as _pathlib
for _d in _pathlib.Path(__file__).parent.rglob("__pycache__"):
    _shutil.rmtree(_d, ignore_errors=True)
import csv
from pathlib import Path
import cv2, numpy as np

ICON_SIZE  = 56
GAP        = 4
PAD        = 8
DATE_H     = 14          # height of date label strip above buff when date changes
LABEL_H    = 16          # height of name label below each icon
ROW_H      = ICON_SIZE + LABEL_H + GAP

W_BUFF     = ICON_SIZE + GAP
W_DOLL     = ICON_SIZE + GAP
W_RIGHT    = 100         # owner + score column
N_DOLLS    = 5
TOTAL_W    = PAD + W_BUFF + GAP + N_DOLLS * W_DOLL + GAP + W_RIGHT + PAD

C_BG       = (45, 45, 45)
C_DATE_BG  = (55, 50, 35)
C_DATE_TXT = (160, 185, 230)
C_ROW_A    = (55, 55, 55)
C_ROW_B    = (62, 62, 62)
C_TXT      = (220, 220, 220)
C_DIM      = (110, 110, 110)
C_SCORE    = (160, 185, 230)
C_UNKNOWN  = (70, 70, 70)
C_BORDER   = (90, 90, 90)

FONT    = cv2.FONT_HERSHEY_SIMPLEX
F_TINY  = 0.28
F_SM    = 0.32
F_MD    = 0.38
F_LG    = 0.42

ASSETS_DIR = Path(__file__).parent / "assets"


def _load_icon(category, name):
    if not name:
        return None
    d = ASSETS_DIR / category
    for stem in (name, f"_{name}"):
        hits = list(d.glob(f"{stem}.png"))
        if hits:
            img = cv2.imread(str(hits[0]))
            if img is not None:
                return cv2.resize(img, (ICON_SIZE, ICON_SIZE), interpolation=cv2.INTER_AREA)
    return None


def _placeholder():
    ph = np.full((ICON_SIZE, ICON_SIZE, 3), C_UNKNOWN, dtype=np.uint8)
    cv2.rectangle(ph, (0, 0), (ICON_SIZE-1, ICON_SIZE-1), C_BORDER, 1)
    cv2.line(ph, (4, 4), (ICON_SIZE-5, ICON_SIZE-5), C_BORDER, 1)
    cv2.line(ph, (ICON_SIZE-5, 4), (4, ICON_SIZE-5), C_BORDER, 1)
    return ph


def _put(c, text, x, y, color=None, scale=F_MD, th=1):
    cv2.putText(c, text, (x, y), FONT, scale, color or C_TXT, th, cv2.LINE_AA)


def _draw_icon(canvas, icon, label, x, y):
    canvas[y:y+ICON_SIZE, x:x+ICON_SIZE] = icon if icon is not None else _placeholder()
    short = (label or "?")[:10]
    (tw, _), _ = cv2.getTextSize(short, FONT, F_SM, 1)
    tx = x + max(0, (ICON_SIZE - tw) // 2)
    _put(canvas, short, tx, y + ICON_SIZE + 12, C_DIM if not label else C_TXT, F_SM)


def render(rows: list[dict]) -> np.ndarray:
    # Calculate total height (add DATE_H when date changes)
    total_h = PAD
    prev_date = None
    for r in rows:
        d = (r.get("date") or "").strip() or None
        if d != prev_date:
            total_h += DATE_H
            prev_date = d
        total_h += ROW_H + GAP
    total_h += PAD

    canvas = np.full((total_h, TOTAL_W, 3), C_BG, dtype=np.uint8)
    y = PAD
    prev_date = None

    for ri, row in enumerate(rows):
        date  = (row.get("date") or "").strip() or None
        buff  = (row.get("buffName") or "").strip()
        owner = (row.get("ownerName") or "?").strip()[:14]
        score = (row.get("score") or "").strip()

        # Date strip above buff icon (only when date changes)
        if date != prev_date:
            cv2.rectangle(canvas, (PAD, y), (PAD + W_BUFF, y + DATE_H - 2), C_DATE_BG, -1)
            _put(canvas, date or "—", PAD + 3, y + DATE_H - 4, C_DATE_TXT, F_TINY)
            y += DATE_H
            prev_date = date

        # Row background (alternating)
        cv2.rectangle(canvas, (PAD, y), (TOTAL_W - PAD, y + ROW_H),
                      C_ROW_A if ri % 2 == 0 else C_ROW_B, -1)

        x = PAD

        # Buff
        _draw_icon(canvas, _load_icon("buff", buff), buff, x, y)
        x += W_BUFF + GAP

        # Dolls
        for i in range(1, 6):
            n = (row.get(f"doll{i}") or "").strip()
            _draw_icon(canvas, _load_icon("dolls", n), n, x, y)
            x += W_DOLL

        # Rightmost: owner (top) + score (bottom)
        x += GAP
        _put(canvas, owner, x, y + 20, C_TXT, F_MD)
        if score:
            _put(canvas, score, x, y + 20 + 22, C_SCORE, F_LG, 1)

        y += ROW_H + GAP

    return canvas


def main():
    if len(sys.argv) < 2:
        print("Usage: python render_debug.py <csv_path>")
        sys.exit(1)
    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: {csv_path} not found", file=sys.stderr)
        sys.exit(1)
    rows   = list(csv.DictReader(open(csv_path, newline="", encoding="utf-8")))
    canvas = render(rows)
    out    = csv_path.with_name(csv_path.stem + "_debug.png")
    cv2.imwrite(str(out), canvas)
    print(f"Saved -> {out}  ({canvas.shape[1]}x{canvas.shape[0]}px)")


if __name__ == "__main__":
    main()
