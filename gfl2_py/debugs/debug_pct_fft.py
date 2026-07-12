# -*- coding: utf-8 -*-
"""
debug_pct_fft.py — Explore FFT-based features for pct digit classification.

For each digit 0-9 found in the pct strips of a daily GS image:
  1. Locate blobs using the existing binarise pipeline (position only)
  2. Extract the RAW greyscale glyph crop (no binarisation)
  3. Apply 2D FFT → log-magnitude → normalise to [0, 1]
  4. Bucket into N bins and accumulate histogram per digit class

The last glyph in each pct strip (always '%') is skipped structurally.
'.' blobs are excluded by size.

Outputs (per bin count, under tests/outputs/pct_fft/<N>/):
  hist_<digit>.json    — {digit, n_samples, bins, counts}
  all_digits.png       — all digits overlaid (probability histogram)
  running_total.png    — x = cumulative probability, y = bin index

Usage:
  python debugs/debug_pct_fft.py single/gm_d_20250929.png
  python debugs/debug_pct_fft.py single/gm_d_20250929.png --bins 32,64
  python debugs/debug_pct_fft.py --running-total --bins 32,64
"""
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr_v0_1_0 import (
    PCT_STRIP_Y,
    NORM_W_PCT, NORM_H_PCT,
    DOT_MAX_DIM,
    _binarize, _find_blobs, _filter_y_outliers,
    _find_percent_x_start,
    StatOcrV0_1_0,
)
from gfl2.patterns.daily_gunsmoke import (
    _split_panels, _find_frames, _frame_col_cell,
    COL1_FR, COL2_FR, COL3_FR, COL4_FR,
)

_BASE_OUT = _ROOT / "tests" / "outputs" / "pct_fft"
COLS_FR   = [("col1", COL1_FR), ("col2", COL2_FR),
             ("col3", COL3_FR), ("col4", COL4_FR)]


# ── FFT feature ───────────────────────────────────────────────────────────────

def _fft_magnitudes(gray_crop: np.ndarray) -> np.ndarray:
    """
    Return the flattened log-scaled 2D FFT magnitude spectrum, normalised to [0, 1].
    Values are NOT yet binned — call _make_hist() to bucket at any resolution.
    """
    f32 = gray_crop.astype(np.float32) / 255.0
    mag = np.abs(np.fft.fftshift(np.fft.fft2(f32)))
    mag = np.log1p(mag)
    if mag.max() > 0:
        mag = mag / mag.max()
    return mag.ravel()


def _make_hist(magnitudes: np.ndarray, n_bins: int) -> np.ndarray:
    """Bucket [0,1] magnitudes into n_bins and return a probability histogram."""
    indices = (magnitudes * (n_bins - 1)).astype(np.uint8)
    hist    = np.bincount(indices, minlength=n_bins).astype(np.float64)
    if hist.sum() > 0:
        hist /= hist.sum()
    return hist


# ── Pipeline: collect raw magnitudes ─────────────────────────────────────────

def collect_magnitudes(image_path: Path) -> dict[str, list[np.ndarray]]:
    """
    Run the daily-GS pipeline on image_path and return raw FFT magnitude
    arrays (not yet binned) keyed by digit label.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        sys.exit(f"Cannot read: {image_path}")

    engine = StatOcrV0_1_0.load()
    # digit -> list of flat magnitude arrays (one per glyph instance)
    raw: dict[str, list[np.ndarray]] = defaultdict(list)

    for panel in _split_panels(img):
        for (fx, fy, fw, fh) in _find_frames(panel):
            for _cname, col_fr in COLS_FR:
                cell = _frame_col_cell(panel, fx, fy, fw, fh, col_fr)
                if cell.size == 0:
                    continue

                pct_str, _ = engine.read(cell)
                if not pct_str:
                    continue

                ch        = cell.shape[0]
                pct_strip = cell[: int(ch * PCT_STRIP_Y[1]), :]
                gray      = (cv2.cvtColor(pct_strip, cv2.COLOR_BGR2GRAY)
                             if pct_strip.ndim == 3 else pct_strip)

                thresh = _binarize(pct_strip)
                blobs  = _filter_y_outliers(_find_blobs(thresh), threshold=12)
                if not blobs:
                    continue

                sorted_x    = sorted(blobs, key=lambda b: b[0])
                pct_x       = _find_percent_x_start(sorted_x)
                digit_blobs = [
                    (x, y, w, h) for (x, y, w, h) in sorted_x
                    if (pct_x is None or x < pct_x)
                    and not (w <= DOT_MAX_DIM and h <= DOT_MAX_DIM)
                ]
                expected = [c for c in pct_str if c.isdigit()]
                if len(digit_blobs) != len(expected):
                    continue

                for (x, y, w, h), label in zip(digit_blobs, expected):
                    crop = gray[y: y + h, x: x + w]
                    if crop.size == 0:
                        continue
                    norm = cv2.resize(crop, (NORM_W_PCT, NORM_H_PCT),
                                      interpolation=cv2.INTER_AREA)
                    raw[label].append(_fft_magnitudes(norm))

    n_total = sum(len(v) for v in raw.values())
    print(f"Collected {n_total} digit glyphs from {image_path.name}")
    for d in sorted(raw):
        print(f"  '{d}': {len(raw[d])} samples")
    return raw


# ── Per-resolution output ─────────────────────────────────────────────────────

def generate_for_bins(raw: dict[str, list[np.ndarray]], n_bins: int) -> None:
    """Bucket raw magnitudes at n_bins resolution, save JSONs + all plots."""
    out_dir = _BASE_OUT / str(n_bins)
    out_dir.mkdir(parents=True, exist_ok=True)

    # digit -> (n_samples, n_bins) array of per-sample histograms
    sample_hists: dict[str, np.ndarray] = {
        d: np.array([_make_hist(m, n_bins) for m in raw[d]])
        for d in sorted(raw)
    }
    means = {d: s.mean(axis=0) for d, s in sample_hists.items()}
    stds  = {d: s.std(axis=0)  for d, s in sample_hists.items()}

    _save_json(means, n_bins, out_dir)
    _save_hist_plot(means, n_bins, out_dir)
    _save_running_total_plot(means, n_bins, out_dir)
    _save_variance_plot(means, stds, n_bins, out_dir)
    _save_discriminability_plot(means, stds, n_bins, out_dir)


def _save_json(hists: dict[str, np.ndarray], n_bins: int, out_dir: Path) -> None:
    for digit, avg in hists.items():
        out = out_dir / f"hist_{digit}.json"
        out.write_text(json.dumps({
            "digit":     digit,
            "n_samples": 0,          # filled below if raw counts known
            "bins":      list(range(n_bins)),
            "counts":    [round(v, 6) for v in avg.tolist()],
        }, indent=2), encoding="utf-8")
    print(f"  [{n_bins} bins] JSON -> {out_dir}/hist_*.json")


def _save_hist_plot(hists: dict[str, np.ndarray], n_bins: int, out_dir: Path) -> None:
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
    cmap    = plt.get_cmap("tab10")
    bins    = np.arange(n_bins)
    digits  = sorted(hists.keys())

    fig, ax = plt.subplots(figsize=(11, 5))
    for i, d in enumerate(digits):
        ax.plot(bins, hists[d],
                marker=markers[i % len(markers)], color=cmap(i),
                label=f"'{d}'", linewidth=1.5, markersize=5, alpha=0.85)

    ax.set_xlabel(f"FFT magnitude bin (0 – {n_bins - 1})")
    ax.set_ylabel("probability")
    ax.set_title(f"Pct-digit FFT histograms  ({n_bins} bins)")
    ax.set_xticks(bins[::max(1, n_bins // 16)])
    ax.legend(ncol=2, fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_png = out_dir / "all_digits.png"
    fig.savefig(str(out_png), dpi=110)
    plt.close(fig)
    print(f"  [{n_bins} bins] plot  -> {out_png}")


def _save_variance_plot(means: dict[str, np.ndarray], stds: dict[str, np.ndarray],
                        n_bins: int, out_dir: Path) -> None:
    """Mean ± 1 std shaded band per digit. Tight bands = consistent signal."""
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    cmap   = plt.get_cmap("tab10")
    bins   = np.arange(n_bins)
    digits = sorted(means.keys())

    fig, ax = plt.subplots(figsize=(11, 5))
    for i, d in enumerate(digits):
        mu  = means[d]
        sig = stds[d]
        c   = cmap(i)
        ax.plot(bins, mu, color=c, label=f"'{d}'", linewidth=1.5)
        ax.fill_between(bins, mu - sig, mu + sig, color=c, alpha=0.18)

    ax.set_xlabel(f"bin (0 – {n_bins - 1})")
    ax.set_ylabel("probability  (mean ± 1 std)")
    ax.set_title(f"Pct-digit FFT  mean ± std  ({n_bins} bins)  — tight bands = signal")
    ax.set_xticks(bins[::max(1, n_bins // 16)])
    ax.legend(ncol=2, fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_png = out_dir / "variance.png"
    fig.savefig(str(out_png), dpi=110)
    plt.close(fig)
    print(f"  [{n_bins} bins] var   -> {out_png}")


def _save_discriminability_plot(means: dict[str, np.ndarray], stds: dict[str, np.ndarray],
                                 n_bins: int, out_dir: Path) -> None:
    """
    Per-bin F-ratio: between-digit std / mean within-digit std.
    F > 1 at a bin means digit means are more spread than the within-class noise
    at that bin — i.e. it carries discriminative signal.
    """
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    digits      = sorted(means.keys())
    all_means   = np.array([means[d] for d in digits])   # (10, n_bins)
    all_stds    = np.array([stds[d]  for d in digits])   # (10, n_bins)

    between = all_means.std(axis=0)                       # spread of digit means per bin
    within  = all_stds.mean(axis=0)                       # avg within-digit noise per bin
    f_ratio = between / (within + 1e-9)

    bins = np.arange(n_bins)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]})

    # Top: between vs within
    axes[0].bar(bins, between, width=0.4, align="edge",  color="steelblue",
                alpha=0.8, label="between-digit std")
    axes[0].bar(bins, within,  width=-0.4, align="edge", color="tomato",
                alpha=0.8, label="within-digit std (mean)")
    axes[0].set_ylabel("std")
    axes[0].set_title(f"Pct-digit FFT  discriminability  ({n_bins} bins)")
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3, axis="y")

    # Bottom: F-ratio with threshold line at 1.0
    axes[1].bar(bins, f_ratio, color=np.where(f_ratio >= 1, "steelblue", "lightgray"),
                alpha=0.9)
    axes[1].axhline(1.0, color="black", linewidth=1, linestyle="--",
                    label="F = 1  (signal = noise)")
    axes[1].set_xlabel(f"bin (0 – {n_bins - 1})")
    axes[1].set_ylabel("F-ratio")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3, axis="y")

    axes[1].set_xticks(bins[::max(1, n_bins // 16)])
    fig.tight_layout()

    out_png = out_dir / "discriminability.png"
    fig.savefig(str(out_png), dpi=110)
    plt.close(fig)
    print(f"  [{n_bins} bins] disc  -> {out_png}")


def _save_running_total_plot(hists: dict[str, np.ndarray], n_bins: int,
                              out_dir: Path) -> None:
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
    cmap    = plt.get_cmap("tab10")
    digits  = sorted(hists.keys())

    fig, ax = plt.subplots(figsize=(11, 5))
    for i, d in enumerate(digits):
        cumsum = np.concatenate([[0.0], np.cumsum(hists[d])])
        yvals  = np.arange(len(cumsum))
        ax.step(cumsum, yvals, where="post",
                color=cmap(i), label=f"'{d}'", linewidth=1.8, alpha=0.85)
        ax.plot(cumsum, yvals,
                marker=markers[i % len(markers)], color=cmap(i),
                linestyle="none", markersize=4, alpha=0.7)

    ax.set_xlabel("running total (cumulative probability)")
    ax.set_ylabel(f"bin index (0 – {n_bins - 1})")
    ax.set_title(f"Pct-digit FFT  running total  ({n_bins} bins)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n_bins)
    ax.legend(ncol=2, fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_png = out_dir / "running_total.png"
    fig.savefig(str(out_png), dpi=110)
    plt.close(fig)
    print(f"  [{n_bins} bins] CDF   -> {out_png}")


# ── --running-total from existing JSONs ───────────────────────────────────────

def replot_from_json(n_bins: int) -> None:
    out_dir = _BASE_OUT / str(n_bins)
    hists: dict[str, np.ndarray] = {}
    for f in sorted(out_dir.glob("hist_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        hists[d["digit"]] = np.array(d["counts"])
    if not hists:
        print(f"No hist_*.json files in {out_dir} — run with an image first")
        return
    _save_hist_plot(hists, n_bins, out_dir)
    _save_running_total_plot(hists, n_bins, out_dir)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", help="Daily GS image to process")
    parser.add_argument("--bins", default="16",
                        help="Comma-separated bin counts  [default: 16]")
    parser.add_argument("--running-total", action="store_true",
                        help="Regenerate plots from existing JSON files (no image needed)")
    args = parser.parse_args()

    bin_counts = [int(b.strip()) for b in args.bins.split(",")]

    if args.running_total and args.image is None:
        for n in bin_counts:
            replot_from_json(n)
    elif args.image:
        raw = collect_magnitudes(Path(args.image))
        for n in bin_counts:
            generate_for_bins(raw, n)
    else:
        parser.print_help()
