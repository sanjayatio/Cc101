# -*- coding: utf-8 -*-
"""
doll_name_ocr.py — Projection-based doll name classifier (no Tesseract).

Pipeline per name crop:
  1. Grayscale + high-threshold binary → isolate bright white text pixels.
  2. Find tight bounding box of foreground text pixels.
  3. Split bounding box into top / bottom halves.
  4. Normalise each half to SIG_WIDTH columns; compute column-wise mean.
  5. Concatenate → feature vector of 2 × SIG_WIDTH floats in [0, 1].
  6. L2-nearest-neighbour against stored templates; return name when dist < threshold.

Template file  (assets/doll_names/templates.json):
    {"DollName": [<2*SIG_WIDTH floats>], ...}

Build (or re-build) templates from daily-gunsmoke images:
    python -m gfl2.doll_name_ocr --build <image.png> [<image2.png> ...]
    python -m gfl2.doll_name_ocr --build gm_folder/   # all *.png in folder

The build pipeline runs the full daily-gunsmoke OCR + fuzzy-correction on each
image and collects (name_crop, corrected_name) pairs for every doll row where
OCR produced a known doll name.  Templates are averaged across all examples.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

SIG_WIDTH       = 64     # columns per half after normalisation
TEXT_THRESHOLD  = 200    # brightness cut-off to isolate white name text
MATCH_THRESHOLD = 1.8    # L2 distance below which = confident match

_TEMPLATES_PATH = Path(__file__).parent.parent / "assets" / "doll_names" / "templates.json"


# ── Feature extraction ────────────────────────────────────────────────────────

def _col_mean(region: np.ndarray) -> np.ndarray:
    """Resize region to SIG_WIDTH columns, return column-wise mean in [0, 1]."""
    if region.size == 0:
        return np.zeros(SIG_WIDTH, dtype=np.float32)
    rh = max(1, region.shape[0])
    scaled = cv2.resize(region.astype(np.float32),
                        (SIG_WIDTH, rh),
                        interpolation=cv2.INTER_AREA)
    return (scaled.mean(axis=0) / 255.0).astype(np.float32)


def feature(cell: np.ndarray,
            thresh: int = TEXT_THRESHOLD) -> Optional[np.ndarray]:
    """Compute the 2*SIG_WIDTH projection feature vector for a name-column crop.

    Uses a fixed brightness threshold (default TEXT_THRESHOLD) to isolate the
    bright white doll-name text from the darker game-UI background, then finds
    the tight bounding box of the resulting foreground pixels.

    Returns a float32 array of shape (2*SIG_WIDTH,), or None when the cell is
    blank (no foreground pixels found after thresholding).
    """
    if cell is None or cell.size == 0:
        return None

    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if cell.ndim == 3 else cell
    _, binary = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)

    ys, xs = np.where(binary > 0)
    if len(ys) == 0:
        return None

    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    text = binary[y0:y1, x0:x1]

    h = text.shape[0]
    mid = max(1, h // 2)
    top = text[:mid, :]
    bot = text[mid:, :]

    return np.concatenate([_col_mean(top), _col_mean(bot)])


# ── Classifier ────────────────────────────────────────────────────────────────

class DollNameOcr:
    """Projection-based nearest-neighbour classifier for doll names."""

    def __init__(self, templates: dict[str, np.ndarray],
                 threshold: float = MATCH_THRESHOLD) -> None:
        self._templates  = templates   # {name: feature_vec}
        self.threshold   = threshold

    # ── loading ───────────────────────────────────────────────────────────────

    @classmethod
    def load(cls, path: Optional[Path] = None) -> Optional["DollNameOcr"]:
        """Load templates from JSON.  Returns None when file is absent."""
        p = path or _TEMPLATES_PATH
        if not p.exists():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        templates = {name: np.array(v, dtype=np.float32) for name, v in data.items()}
        return cls(templates)

    # ── building ──────────────────────────────────────────────────────────────

    @classmethod
    def build(cls, labeled_crops: list[tuple[np.ndarray, str]],
              out_path: Optional[Path] = None) -> "DollNameOcr":
        """Build and save templates from (crop_bgr, name) pairs.

        Multiple crops of the same doll are averaged so each lookup entry is
        the centroid of all observed examples.
        """
        accum: dict[str, list[np.ndarray]] = {}
        for cell, name in labeled_crops:
            vec = feature(cell)
            if vec is not None:
                accum.setdefault(name, []).append(vec)

        templates: dict[str, np.ndarray] = {
            name: np.mean(vecs, axis=0).astype(np.float32)
            for name, vecs in accum.items()
        }

        p = out_path or _TEMPLATES_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps({n: v.tolist() for n, v in templates.items()}, indent=2),
            encoding="utf-8",
        )
        return cls(templates)

    def update(self, labeled_crops: list[tuple[np.ndarray, str]],
               alpha: float = 0.3,
               out_path: Optional[Path] = None) -> None:
        """Incrementally update templates with new (crop, name) pairs.

        Uses an exponential moving average so existing templates shift toward
        new examples rather than being replaced.  Saves the updated templates.
        """
        new_accum: dict[str, list[np.ndarray]] = {}
        for cell, name in labeled_crops:
            vec = feature(cell)
            if vec is not None:
                new_accum.setdefault(name, []).append(vec)

        for name, vecs in new_accum.items():
            incoming = np.mean(vecs, axis=0).astype(np.float32)
            if name in self._templates:
                self._templates[name] = (alpha * incoming
                                         + (1.0 - alpha) * self._templates[name])
            else:
                self._templates[name] = incoming

        p = out_path or _TEMPLATES_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps({n: v.tolist() for n, v in self._templates.items()}, indent=2),
            encoding="utf-8",
        )

    # ── inference ─────────────────────────────────────────────────────────────

    def classify(self, cell: np.ndarray) -> Optional[str]:
        """Return the nearest doll name or None when confidence is too low."""
        vec = feature(cell)
        if vec is None or not self._templates:
            return None
        best_name, best_dist = None, float("inf")
        for name, tmpl in self._templates.items():
            d = float(np.linalg.norm(vec - tmpl))
            if d < best_dist:
                best_dist, best_name = d, name
        return best_name if best_dist < self.threshold else None

    def distances(self, cell: np.ndarray) -> list[tuple[str, float]]:
        """Return all (name, dist) pairs sorted nearest-first (for debugging)."""
        vec = feature(cell)
        if vec is None:
            return []
        result = [(n, float(np.linalg.norm(vec - t)))
                  for n, t in self._templates.items()]
        return sorted(result, key=lambda x: x[1])


# ── Build CLI ─────────────────────────────────────────────────────────────────

def _build_from_daily_images(image_paths: list[Path], show: bool = False) -> "DollNameOcr":
    """Process daily-gunsmoke images with OCR, collect labeled name crops, build templates.

    For each doll row where OCR + fuzzy-correction produces a non-empty name,
    the name-column crop is saved as a labeled example.  The known-doll filter
    is skipped when assets/dolls/ is empty so templates can be bootstrapped.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from gfl2.patterns.daily_gunsmoke import (
        _split_panels, _find_frames, NAME_W_FRAC,
        _extract_name, _fuzzy_correct, _known_doll_names,
    )
    known = set(_known_doll_names())
    use_known_filter = len(known) > 0

    labeled: list[tuple[np.ndarray, str]] = []
    n_images = n_panels = n_frames = n_ok = n_empty = 0

    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            print("  [skip]", img_path.name, "(unreadable)")
            continue
        n_images += 1
        n_before = len(labeled)
        for panel in _split_panels(img):
            n_panels += 1
            ph, pw = panel.shape[:2]
            frames = _find_frames(panel)
            if not frames:
                print("   ", img_path.name, ": no frames in panel", n_panels)
                continue
            n_frames += len(frames)
            ax, ay, aw, ah = frames[0]
            name_x0 = ax + aw + 2
            name_x1 = name_x0 + round(pw * NAME_W_FRAC)
            for fx, fy, fw, fh in frames:
                name_cell = panel[fy:fy + fh, name_x0:name_x1]
                raw = _extract_name(name_cell)
                if not raw:
                    n_empty += 1
                    continue
                n_ok += 1
                name = _fuzzy_correct(raw)
                if use_known_filter and name not in known:
                    continue
                labeled.append((name_cell.copy(), name))
        added = len(labeled) - n_before
        print(" ", img_path.name + ":", added, "labeled crops")

    print()
    print("  images=" + str(n_images), " panels=" + str(n_panels),
          " frames=" + str(n_frames), " ocr_ok=" + str(n_ok),
          " ocr_empty=" + str(n_empty), " collected=" + str(len(labeled)))
    if use_known_filter:
        print("  known filter: ON (" + str(len(known)) + " names from assets/dolls/)")
    else:
        print("  known filter: OFF (assets/dolls/ is empty — accepting all OCR results)")

    if not labeled:
        print()
        print("  *** 0 crops collected. Possible causes: ***")
        print("    1. Images are weekly format, not daily-gunsmoke format")
        print("    2. Frame detection found nothing (wrong image layout)")
        print("    3. OCR returned empty for all " + str(n_empty) + " name cells")
        if use_known_filter and n_ok > 0:
            print("    4. OCR produced names not in known list — try again without portraits")
        return DollNameOcr({})

    print("Building templates from", len(labeled), "crops ...")
    ocr = DollNameOcr.build(labeled)
    print("Saved", len(ocr._templates), "templates ->", str(_TEMPLATES_PATH))

    if show:
        from collections import Counter
        counts = Counter(name for _, name in labeled)
        print()
        print("  {:<20}  {:>8}".format("name", "n crops"))
        print("  {:<20}  {:>8}".format("-"*20, "-"*8))
        for name in sorted(ocr._templates):
            print("  {:<20}  {:>8d}".format(name, counts.get(name, 0)))

    return ocr


if __name__ == "__main__":
    import sys
    from pathlib import Path

    args = sys.argv[1:]
    show   = "--show"  in args; args = [a for a in args if a != "--show"]
    build  = "--build" in args; args = [a for a in args if a != "--build"]

    if not build or not args:
        print(__doc__)
        sys.exit(0 if not build else 1)

    # Expand folder args to *.png globs
    paths: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            paths.extend(sorted(p.glob("*.png")))
        elif p.exists():
            paths.append(p)
        else:
            print(f"  [skip] {p} (not found)")

    if not paths:
        print("No .png files found.", file=sys.stderr)
        sys.exit(1)

    _build_from_daily_images(paths, show=show)
