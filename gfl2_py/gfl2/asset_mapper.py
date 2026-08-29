# -*- coding: utf-8 -*-
"""
asset_mapper.py - Translates a cropped doll/buff frame to a named asset string.

Asset naming convention
-----------------------
  Known (user-confirmed) assets  ->  prefix with '_', e.g. _QiongJiu.png
  Unknown (auto-saved) crops     ->  caller-supplied name, no underscore prefix
                                      e.g. gm_250801-row01-doll3.png

To promote an unknown to a matchable asset, rename the file to _Name.png.
"""
from __future__ import annotations
import sys
import uuid
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from gfl2.trace import timed

PHASH_THRESHOLD = 6
HIST_THRESHOLD  = 0.88
PHASH_SIZE      = 8

ELEM_X1   = 0.25
ARROW_Y0  = 0.20
ARROW_Y1  = 0.58
BORROW_X0 = 0.48
BORROW_Y1 = 0.26
BADGE_Y0  = 0.75

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def _phash(img_bgr: np.ndarray) -> int:
    gray    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (PHASH_SIZE*4, PHASH_SIZE*4), interpolation=cv2.INTER_AREA)
    dct     = cv2.dct(np.float32(resized))
    dct_low = dct[:PHASH_SIZE, :PHASH_SIZE]
    bits    = (dct_low >= np.median(dct_low)).flatten()
    h = 0
    for b in bits:
        h = (h << 1) | int(b)
    return h


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def _make_mask(h: int, w: int) -> np.ndarray:
    mask = np.ones((h, w), dtype=np.uint8) * 255
    mask[int(h*ARROW_Y0):int(h*ARROW_Y1), :int(w*ELEM_X1)] = 0
    mask[:int(h*BORROW_Y1), int(w*BORROW_X0):]             = 0
    mask[int(h*BADGE_Y0):, :]                               = 0
    return mask


@timed()
def _hist_corr(frame: np.ndarray, asset: np.ndarray) -> float:
    ref  = cv2.resize(asset, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_AREA)
    h, w = frame.shape[:2]
    mask = _make_mask(h, w)
    def hist(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hst = cv2.calcHist([hsv], [0, 1], mask, [30, 32], [0, 180, 0, 256])
        cv2.normalize(hst, hst)
        return hst
    return float(cv2.compareHist(hist(frame), hist(ref), cv2.HISTCMP_CORREL))


class AssetMapper:
    def __init__(self, category: str) -> None:
        self.category  = category
        self.asset_dir = ASSETS_DIR / category
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        # Only user-confirmed assets (stem starts with '_') are used for matching.
        self._named: list[tuple[str, np.ndarray, int]] = []
        self._rebuild_index()

    @timed()
    def translate(self, frame: Optional[np.ndarray],
                  save_name: Optional[str] = None) -> Optional[str]:
        """
        Match frame against known assets.

        Returns the asset stem (e.g. '_QiongJiu') on a match, None otherwise.
        On no match, saves the frame to assets/{category}/{save_name}.png if
        the file does not already exist.  Falls back to a UUID name when
        save_name is not provided.
        """
        if frame is None or frame.size == 0:
            return None
        self._rebuild_index()
        fh = _phash(frame)

        if self._named:
            best_name, best_dist = self._phash_best(fh)
            if best_dist <= PHASH_THRESHOLD:
                return best_name
            best_name, best_score = self._hist_best(frame)
            if best_score >= HIST_THRESHOLD:
                return best_name

        # No match found -- save the crop for manual labelling
        self._save_unknown(frame, save_name)
        return None

    def reload(self) -> None:
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Load only _-prefixed PNGs as matchable assets.

        Scans the top-level asset directory AND any immediate subdirectories
        (e.g. weekly_seeds/, daily/) so test-fixture seeds and live assets can
        live side-by-side without phantom-file conflicts on NTFS mounts.
        """
        named = []
        for png in sorted(self.asset_dir.rglob("_*.png")):
            img = cv2.imread(str(png))
            if img is None:
                continue
            named.append((png.stem, img, _phash(img)))
        self._named = named

    def _phash_best(self, fh: int) -> tuple[str, int]:
        best_name, best_dist = "", 64
        for name, _, ah in self._named:
            d = _hamming(fh, ah)
            if d < best_dist:
                best_dist, best_name = d, name
        return best_name, best_dist

    def _hist_best(self, frame: np.ndarray) -> tuple[str, float]:
        best_name, best_score = "", 0.0
        for name, asset_img, _ in self._named:
            s = _hist_corr(frame, asset_img)
            if s > best_score:
                best_score, best_name = s, name
        return best_name, best_score

    def _save_unknown(self, frame: np.ndarray,
                      name: Optional[str] = None) -> Optional[Path]:
        stem = name if name else str(uuid.uuid4())
        path = self.asset_dir / f"{stem}.png"
        if path.exists():
            return path   # already saved in a previous run -- don't overwrite
        cv2.imwrite(str(path), frame)
        print(f"[asset_mapper] Unknown {self.category} saved -> {path.name}",
              file=sys.stderr)
        return path
