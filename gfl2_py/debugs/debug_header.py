#!/usr/bin/env python3
"""
debug_header.py  —  visualise header/stats-row crop regions.

Usage:
    python debug_header.py <image.png>

Saves  <image>_header_debug.png  alongside the source image showing:
  - green  : score crop (SCORE_X0/X1 × HEADER_BAR_Y0/Y1)
  - blue   : stats row full band (frame-relative Y from doll frame)
  - yellow : STATS_DEALT_FR crop
  - cyan   : STATS_TAKEN_FR crop
  - magenta: STATS_TURNS_FR crop
  - white  : first detected doll frame (anchor for FR offsets)
"""
from __future__ import annotations
import sys
from pathlib import Path

import cv2
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # project root

# ── load the module constants without importing the full gfl2 package ──────────
from gfl2.patterns.daily_gunsmoke import (
    HEADER_BAR_Y0, HEADER_BAR_Y1,
    STATS_ROW_Y0, STATS_ROW_Y1,
    STATS_ROW_Y0_FR, STATS_ROW_Y1_FR,
    SCORE_X0, SCORE_X1,
    STATS_DEALT_FR, STATS_TAKEN_FR, STATS_TURNS_FR,
    _split_panels, _find_frames,
)


def _rect(img, x0, y0, x1, y1, color, label=""):
    cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)
    if label:
        cv2.putText(img, label, (x0 + 3, max(y0 + 14, 14)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)


def annotate_panel(panel: np.ndarray) -> np.ndarray:
    out = panel.copy()
    ph, pw = panel.shape[:2]

    # Score crop (green)
    _rect(out,
          int(pw * SCORE_X0), int(ph * HEADER_BAR_Y0),
          int(pw * SCORE_X1), int(ph * HEADER_BAR_Y1),
          (0, 220, 0), "score")

    # First doll frame (white) — detect early; all Y coords are frame-relative
    frames = _find_frames(panel)

    if frames:
        _fx, _fy, _fw, _fh = frames[0]
        sy0 = _fy - int(_fh * STATS_ROW_Y0_FR)
        sy1 = _fy - int(_fh * STATS_ROW_Y1_FR)
    else:
        sy0 = int(ph * STATS_ROW_Y0)
        sy1 = int(ph * STATS_ROW_Y1)

    # Stats row full band (blue, thin)
    cv2.rectangle(out, (0, sy0), (pw - 1, sy1), (200, 100, 0), 1)

    if frames:
        fx, fy, fw, fh = frames[0]
        _rect(out, fx, fy, fx + fw, fy + fh, (255, 255, 255), "frame[0]")
        fr = fx + fw

        def stats_crop_rect(fr_range):
            x0 = max(0, fr + int(fw * fr_range[0]))
            x1 = min(pw, fr + int(fw * fr_range[1]))
            return x0, sy0, x1, sy1

        _rect(out, *stats_crop_rect(STATS_DEALT_FR), (0, 220, 220), "dealt")
        _rect(out, *stats_crop_rect(STATS_TAKEN_FR), (220, 220, 0), "taken")
        _rect(out, *stats_crop_rect(STATS_TURNS_FR), (220, 0, 220), "turns")
    else:
        cv2.putText(out, "NO FRAME DETECTED", (10, sy0 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return out


def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_header.py <image.png>")
        sys.exit(1)

    src = Path(sys.argv[1])
    img = cv2.imread(str(src))
    if img is None:
        print(f"Cannot read: {src}")
        sys.exit(1)

    panels = _split_panels(img)
    annotated = [annotate_panel(p) for p in panels]
    out_img = np.hstack(annotated) if len(annotated) > 1 else annotated[0]

    out_path = src.with_name(src.stem + "_header_debug.png")
    cv2.imwrite(str(out_path), out_img)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
