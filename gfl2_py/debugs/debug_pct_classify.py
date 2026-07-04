# -*- coding: utf-8 -*-
"""
debug_pct_classify.py — Pct digit feature explorer: 64-bin FFT histogram + Gabor filters + wedge.

Feature vector per glyph (N_BINS + N_ORIENT + N_WEDGES = 76 dimensions):
  [0:64]   64-bin FFT log-magnitude histogram (sum=1)
  [64:68]  Gabor orientation fractions at θ=0°, 45°, 90°, 135° (sum=1)
           λ=4, σ=2, γ=1 (circular) — best from parameter sweep.
  [68:76]  8-wedge angular-sector energy fractions of the FFT magnitude
           spectrum (sum=1), folded to [0°,180°) — the classic Fourier
           "ring/wedge" texture feature, tried against the '6'/'9'
           collision left unresolved by Gabor (known_issues.txt §15).

Goal: use FFT+Gabor(+wedge) to segregate digits into groups, not as a final
      classifier.  KNN is retained only as an internal proxy metric for
      the Gabor parameter sweep (--tune).

Usage:
  python debugs/debug_pct_classify.py single/gm_d_20250929.png
  python debugs/debug_pct_classify.py single/gm_d_20250929.png --tune
"""
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import (
    PCT_STRIP_Y, NORM_W_PCT, NORM_H_PCT, DOT_MAX_DIM,
    _binarize, _find_blobs, _filter_y_outliers,
    _find_percent_x_start, StatOcr,
)
from gfl2.stat_ocr_padded import _normalize_glyph
from gfl2.patterns.daily_gunsmoke import (
    _split_panels, _find_frames, _frame_col_cell,
    COL1_FR, COL2_FR, COL3_FR, COL4_FR,
)

OUT_DIR   = _ROOT / "tests" / "outputs" / "pct_classify"
COLS_FR   = [("col1", COL1_FR), ("col2", COL2_FR),
             ("col3", COL3_FR), ("col4", COL4_FR)]
N_BINS    = 64
N_ORIENT  = 4            # best from sweep: λ=4, σ=2, γ=1, 4 orientations
N_WEDGES  = 8            # angular sectors over [0°,180°) of the FFT magnitude
N_FEAT    = N_BINS + N_ORIENT + N_WEDGES


# ── FFT helpers (inlined from debug_pct_fft) ──────────────────────────────────

def _fft_magnitudes(gray: np.ndarray) -> np.ndarray:
    f32 = gray.astype(np.float32) / 255.0
    mag = np.abs(np.fft.fftshift(np.fft.fft2(f32)))
    mag = np.log1p(mag)
    if mag.max() > 0:
        mag = mag / mag.max()
    return mag.ravel()

def _make_hist(mags: np.ndarray, n_bins: int) -> np.ndarray:
    idx  = (mags * (n_bins - 1)).astype(np.uint8)
    hist = np.bincount(idx, minlength=n_bins).astype(np.float64)
    if hist.sum() > 0:
        hist /= hist.sum()
    return hist


# ── Gabor kernels ──────────────────────────────────────────────────────────────
# Best config from sweep: λ=4, σ=2, γ=1 (circular), 4 orientations.
# γ=1 (circular) beats elongated filters on this small 12×20 glyph —
# strokes are too short for orientation-selective elongated kernels.
# 4 orientations (0°, 45°, 90°, 135°) capture diagonal strokes in '7'/'4'
# that 2-orientation h/v misses.

_GABOR_KERNELS = [
    cv2.getGaborKernel((7, 7), 2.0, i * np.pi / N_ORIENT, 4.0, 1.0, 0.0, cv2.CV_32F)
    for i in range(N_ORIENT)
]


# ── Wedge filter (Fourier ring/wedge angular-sector energy) ──────────────────
# Classic optical/Fourier texture feature: instead of Gabor's spatial
# convolution, sum the 2D FFT magnitude spectrum within angular sectors
# ("wedges") radiating from the DC term.  Tried as a second attempt at the
# '6'/'9' Gabor orientation collision (known_issues.txt §15) after
# aspect-preserving padding left it unchanged.
#
# CAVEAT (checked before trusting this feature): for any real-valued image
# f, its exact 180°-rotation g(x,y)=f(-x,-y) has FFT G(u,v)=F(-u,-v), and by
# the Hermitian symmetry of real signals F(-u,-v)=conj(F(u,v)), so
# |G(u,v)|==|F(u,v)| at every frequency bin — the magnitude spectrum of a
# 180°-rotated image is IDENTICAL to the original's, not just similar.  If
# '9' renders as an exact 180° rotation of '6' in this font (plausible —
# many fonts construct them that way), no feature built purely from FFT
# magnitude, wedge-binned or not, can distinguish them even in principle.
# The existing 64-bin FFT histogram feature is subject to the same limit.

_WEDGE_BIN_CACHE: dict[tuple[int, int], np.ndarray] = {}


def _wedge_bin_map(h: int, w: int, n_wedges: int) -> np.ndarray:
    """Angular-sector index per FFT pixel, folded to [0°,180°) — a real
    image's magnitude spectrum is centrosymmetric (|F(u,v)|==|F(-u,-v)|), so
    sectors spanning the full circle would just duplicate each other."""
    key = (h, w)
    cached = _WEDGE_BIN_CACHE.get(key)
    if cached is not None:
        return cached
    cy, cx = h // 2, w // 2
    ys, xs = np.indices((h, w))
    angles = np.degrees(np.arctan2(ys - cy, xs - cx)) % 180
    bins = np.minimum((angles / 180 * n_wedges).astype(int), n_wedges - 1)
    _WEDGE_BIN_CACHE[key] = bins
    return bins


def _wedge_energies(gray_norm: np.ndarray, n_wedges: int = N_WEDGES) -> np.ndarray:
    """Fraction of FFT magnitude energy in each angular sector (DC excluded
    — it dominates the total and carries no orientation information)."""
    f32 = gray_norm.astype(np.float32) / 255.0
    mag = np.abs(np.fft.fftshift(np.fft.fft2(f32)))
    h, w = mag.shape
    mag[h // 2, w // 2] = 0.0
    bins = _wedge_bin_map(h, w, n_wedges)
    energies = np.array([mag[bins == i].sum() for i in range(n_wedges)])
    total = energies.sum() + 1e-9
    return energies / total


# ── Feature extraction ────────────────────────────────────────────────────────

def compute_features(gray_norm: np.ndarray) -> np.ndarray:
    """
    Return a (N_BINS + N_ORIENT + N_WEDGES)-element feature vector for a
    12×20 glyph:
      [0:N_BINS]                    64-bin FFT magnitude histogram (sum=1)
      [N_BINS:N_BINS+N_OR]          Gabor orientation fractions (sum=1) at
                                     θ = 0°, 45°, 90°, 135°
      [N_BINS+N_OR:N_BINS+N_OR+N_W] wedge angular-sector energy fractions
                                     (sum=1) over [0°,180°)
    """
    fft_hist = _make_hist(_fft_magnitudes(gray_norm), N_BINS)
    f32      = gray_norm.astype(np.float32)
    resps    = [float(np.abs(cv2.filter2D(f32, -1, k)).mean())
                for k in _GABOR_KERNELS]
    tot      = sum(resps) + 1e-9
    gabor    = [r / tot for r in resps]
    wedge    = _wedge_energies(gray_norm)
    return np.concatenate([fft_hist, gabor, wedge])


# ── Glyph collection ──────────────────────────────────────────────────────────

def collect_glyphs(image_path: Path) -> list[tuple[np.ndarray, np.ndarray, str]]:
    """
    Run the daily-GS pipeline on image_path.
    Returns list of (gray_norm_12x20, feature_vec, label).
    """
    img = cv2.imread(str(image_path))
    if img is None:
        sys.exit(f"Cannot read: {image_path}")

    engine = StatOcr.load()
    data: list[tuple[np.ndarray, np.ndarray, str]] = []

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
                thresh    = _binarize(pct_strip)
                blobs     = _filter_y_outliers(_find_blobs(thresh), threshold=12)
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
                    # Use thresh (binarized) — matches what _extract_pct_glyphs
                    # passes to _classify at runtime.
                    crop = thresh[y: y + h, x: x + w]
                    if crop.size == 0:
                        continue
                    # Aspect-preserving pad instead of direct stretch (§15) —
                    # 2D features (FFT/Gabor) are distortion-sensitive in a way
                    # the 1D projection classifier isn't.
                    norm = _normalize_glyph(crop, NORM_W_PCT, NORM_H_PCT)
                    data.append((norm, compute_features(norm), label))

    return data


# ── Nearest-centroid classifier ───────────────────────────────────────────────

def build_templates(data: list) -> dict[str, np.ndarray]:
    """Average feature vector per digit from a labeled dataset."""
    buckets: dict[str, list] = defaultdict(list)
    for _gray, feat, label in data:
        buckets[label].append(feat)
    return {d: np.mean(fv, axis=0) for d, fv in buckets.items()}


def predict_knn(feat: np.ndarray, templates: dict[str, np.ndarray]) -> str:
    """Nearest centroid by L2 distance on the full feature vector."""
    dists = {d: float(np.linalg.norm(feat - t)) for d, t in templates.items()}
    return min(dists, key=dists.get)


# ── Leave-one-out evaluation (sweep-internal) ─────────────────────────────────

def evaluate_loo(
    data: list, predict_fn
) -> tuple[float, dict[str, dict[str, int]]]:
    """
    Leave-one-out evaluation.
    Returns (overall_accuracy, confusion_matrix).
    confusion[true][pred] = count
    """
    confusion: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    correct = 0

    for i, (_gray, feat_i, label_i) in enumerate(data):
        rest = [d for j, d in enumerate(data) if j != i]
        tmpl = build_templates(rest)
        pred = predict_fn(feat_i, tmpl)
        confusion[label_i][pred] += 1
        if pred == label_i:
            correct += 1

    return correct / len(data), confusion


# ── Output ────────────────────────────────────────────────────────────────────

def save_feature_importance(data: list) -> None:
    """
    Per-feature F-ratio: between-digit std / mean within-digit std.
    Saved as discriminability.png in OUT_DIR.
    """
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    buckets: dict[str, list] = defaultdict(list)
    for _g, feat, label in data:
        buckets[label].append(feat)

    all_feats = np.array([d[1] for d in data])
    labels    = [d[2] for d in data]
    digits    = sorted(buckets)

    mat_mean = np.array([np.mean(buckets[d], axis=0) for d in digits])
    mat_std  = np.array([np.std( buckets[d], axis=0) for d in digits])
    between  = mat_mean.std(axis=0)
    within   = mat_std.mean(axis=0)
    f_ratio  = between / (within + 1e-9)

    orient_names = [f"g{int(i*180/N_ORIENT)}°" for i in range(N_ORIENT)]
    wedge_names  = [f"w{int(i*180/N_WEDGES)}°" for i in range(N_WEDGES)]
    gab_colors   = ["tomato", "seagreen", "darkorange", "mediumpurple"]
    wedge_color  = "goldenrod"
    x      = np.arange(N_FEAT)
    colors = (["steelblue"] * N_BINS + [gab_colors[i] for i in range(N_ORIENT)]
              + [wedge_color] * N_WEDGES)
    labels_x = ([str(i) if i % 8 == 0 else "" for i in range(N_BINS)]
                + orient_names + wedge_names)

    fig, axes = plt.subplots(2, 1, figsize=(14, 7), sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]})

    axes[0].bar(x, between, color=colors, alpha=0.8, label="between-digit std")
    axes[0].bar(x, within,  color=colors, alpha=0.35, label="within-digit std")
    axes[0].set_ylabel("std")
    axes[0].set_title(f"Feature discriminability  ({N_BINS}-bin FFT + {N_ORIENT}-orientation Gabor + {N_WEDGES}-wedge)")
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3, axis="y")

    bar_colors = (["steelblue" if f >= 1 else "lightgray" for f in f_ratio[:N_BINS]]
                  + [gab_colors[i] if f_ratio[N_BINS + i] >= 1 else "lightgray"
                     for i in range(N_ORIENT)]
                  + [wedge_color if f_ratio[N_BINS + N_ORIENT + i] >= 1 else "lightgray"
                     for i in range(N_WEDGES)])
    axes[1].bar(x, f_ratio, color=bar_colors, alpha=0.9)
    axes[1].axhline(1.0, color="black", linewidth=1, ls="--")
    axes[1].set_ylabel("F-ratio")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels_x, fontsize=7)
    axes[1].grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    out = OUT_DIR / "feature_importance.png"
    fig.savefig(str(out), dpi=110)
    plt.close(fig)
    print(f"  -> {out}")


def save_pca_plot(data: list) -> None:
    """
    2D PCA of the full feature space.  Each point is one glyph, coloured by
    digit label.  Cluster separation shows whether current parameters give
    useful groupings and which digits are confused.
    """
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    X      = np.array([feat for _, feat, _ in data])
    labels = [label for _, _, label in data]
    digits = sorted(set(labels))
    cmap   = plt.get_cmap("tab10")

    # PCA via SVD (no sklearn needed)
    Xc  = X - X.mean(axis=0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    X2  = Xc @ Vt[:2].T          # project onto top-2 principal components

    # Variance explained
    cov_diag = (Xc ** 2).sum(axis=0)
    total_var = cov_diag.sum()
    # Approximate explained variance via projection residual
    var_pc1 = float(((Xc @ Vt[0]) ** 2).sum() / total_var * 100)
    var_pc2 = float(((Xc @ Vt[1]) ** 2).sum() / total_var * 100)

    fig, ax = plt.subplots(figsize=(9, 7))
    for i, d in enumerate(digits):
        idx = [j for j, l in enumerate(labels) if l == d]
        xs  = X2[idx, 0]
        ys  = X2[idx, 1]
        ax.scatter(xs, ys, color=cmap(i), label=f"'{d}'",
                   s=55, alpha=0.75, edgecolors="none")
        # centroid label
        ax.text(xs.mean(), ys.mean(), d, fontsize=11, fontweight="bold",
                color=cmap(i), ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.6, ec="none"))

    ax.set_xlabel(f"PC1  ({var_pc1:.1f}% var)")
    ax.set_ylabel(f"PC2  ({var_pc2:.1f}% var)")
    ax.set_title(f"PCA of FFT+Gabor features  ({N_BINS}-bin + {N_ORIENT}-orient)  —  {len(data)} glyphs")
    ax.legend(ncol=2, fontsize=9, loc="best")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()

    out = OUT_DIR / "pca.png"
    fig.savefig(str(out), dpi=120)
    plt.close(fig)
    print(f"  -> {out}")


# ── Gabor parameter sweep ─────────────────────────────────────────────────────

def gabor_sweep(data: list, ksize: int = 7) -> tuple[float, list]:
    """
    Sweep (lambd, sigma, gamma, n_orientations) and evaluate LOO KNN accuracy
    for FFT+Gabor features.  Also returns FFT-only baseline for comparison.

    Gabor responses are normalised so they sum to 1 across orientations —
    this gives orientation fractions rather than absolute response magnitudes,
    which makes them scale-invariant across different glyph intensities.
    """
    grays  = [g              for g, _, _ in data]
    labels = [label          for _, _, label in data]
    # Precompute FFT histograms once — constant across Gabor configs.
    fft_hists = np.array([_make_hist(_fft_magnitudes(g), N_BINS) for g in grays])

    # FFT-only baseline
    fft_only = [(None, fft_hists[i], labels[i]) for i in range(len(labels))]
    acc_baseline, _ = evaluate_loo(fft_only, predict_knn)

    param_grid = [
        (lambd, sigma, gamma, n_or)
        for lambd in [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
        for sigma in [1.0, 1.5, 2.0]
        for gamma in [0.25, 0.5, 1.0]
        for n_or  in [2, 4, 8]
    ]
    print(f"  Sweep: {len(param_grid)} configs × {len(data)} LOO steps ...")

    results = []
    for idx, (lambd, sigma, gamma, n_or) in enumerate(param_grid):
        if idx % 40 == 0:
            print(f"    {idx}/{len(param_grid)}")

        thetas  = [i * np.pi / n_or for i in range(n_or)]
        kernels = [
            cv2.getGaborKernel((ksize, ksize), sigma, t, lambd, gamma, 0.0, cv2.CV_32F)
            for t in thetas
        ]

        gabor_rows = []
        for g in grays:
            f32   = g.astype(np.float32)
            resps = [float(np.abs(cv2.filter2D(f32, -1, k)).mean()) for k in kernels]
            tot   = sum(resps) + 1e-9
            gabor_rows.append([r / tot for r in resps])
        gabor_mat = np.array(gabor_rows)

        feat_mat = np.hstack([fft_hists, gabor_mat])
        labeled  = [(None, feat_mat[i], labels[i]) for i in range(len(labels))]
        acc, _   = evaluate_loo(labeled, predict_knn)
        results.append((acc, {"lambd": lambd, "sigma": sigma,
                               "gamma": gamma, "n_or": n_or}))

    results.sort(key=lambda x: x[0], reverse=True)
    return acc_baseline, results


def save_sweep_summary(results: list, baseline: float, out_dir: Path) -> None:
    """Box plots showing accuracy distribution per parameter value."""
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    params = ["lambd", "sigma", "gamma", "n_or"]
    fig, axes = plt.subplots(1, len(params), figsize=(14, 4))

    for ax, p in zip(axes, params):
        vals = sorted({cfg[p] for _, cfg in results})
        groups = [[acc for acc, cfg in results if cfg[p] == v] for v in vals]
        ax.boxplot(groups, tick_labels=[str(v) for v in vals])
        ax.axhline(baseline, color="tomato", ls="--", lw=1.2,
                   label=f"FFT-only {baseline*100:.1f}%")
        ax.set_title(p); ax.set_ylabel("LOO acc"); ax.set_ylim(0, 1)
        ax.legend(fontsize=8)

    fig.suptitle("Gabor parameter sweep  —  LOO KNN accuracy distributions")
    fig.tight_layout()
    out = out_dir / "gabor_sweep_summary.png"
    fig.savefig(str(out), dpi=110); plt.close(fig)
    print(f"  -> {out}")


def save_response_grid(data: list, cfg: dict, out_dir: Path) -> None:
    """
    For one sample of each digit, show the raw glyph alongside the Gabor
    response maps at each orientation in cfg.
    """
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    # One sample per digit
    seen: dict[str, np.ndarray] = {}
    for g, _, label in data:
        if label not in seen:
            seen[label] = g
    digits  = sorted(seen)
    n_or    = cfg["n_or"]
    thetas  = [i * np.pi / n_or for i in range(n_or)]
    kernels = [
        cv2.getGaborKernel((7, 7), cfg["sigma"], t, cfg["lambd"],
                           cfg["gamma"], 0.0, cv2.CV_32F)
        for t in thetas
    ]

    n_cols = 1 + n_or   # raw + one per orientation
    fig, axes = plt.subplots(len(digits), n_cols,
                              figsize=(n_cols * 1.6, len(digits) * 2.0))
    axes = np.array(axes)

    theta_labels = [f"θ={t:.2f}" for t in thetas]
    for col, lbl in enumerate(["raw"] + theta_labels):
        axes[0, col].set_title(lbl, fontsize=8)

    for row, d in enumerate(digits):
        g   = seen[d]
        f32 = g.astype(np.float32)
        axes[row, 0].imshow(g, cmap="gray", vmin=0, vmax=255)
        axes[row, 0].set_ylabel(f"'{d}'", fontsize=9, rotation=0, labelpad=14)
        for col, k in enumerate(kernels, start=1):
            resp = np.abs(cv2.filter2D(f32, -1, k))
            axes[row, col].imshow(resp, cmap="hot")
        for ax in axes[row]:
            ax.set_xticks([]); ax.set_yticks([])

    fig.suptitle(
        f"Gabor responses  λ={cfg['lambd']} σ={cfg['sigma']} "
        f"γ={cfg['gamma']} n_or={cfg['n_or']}",
        fontsize=10)
    fig.tight_layout()
    out = out_dir / "gabor_responses_best.png"
    fig.savefig(str(out), dpi=110); plt.close(fig)
    print(f"  -> {out}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Daily GS image to process")
    parser.add_argument("--tune", action="store_true",
                        help="Sweep Gabor parameters and report best configs")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image_path = Path(args.image)

    print(f"Collecting glyphs from {image_path.name} ...")
    data   = collect_glyphs(image_path)
    digits = sorted({label for *_, label in data})
    print(f"  {len(data)} glyphs  digits: {digits}")

    if args.tune:
        print("\nGabor parameter sweep ...")
        acc_base, sweep = gabor_sweep(data)
        print(f"\nFFT-only baseline: {acc_base*100:.1f}%")
        print(f"\nTop-15 Gabor configs:")
        print(f"  {'acc':>6}  {'lambd':>6}  {'sigma':>6}  {'gamma':>6}  {'n_or':>5}")
        for acc, cfg in sweep[:15]:
            print(f"  {acc*100:5.1f}%  {cfg['lambd']:6.1f}  {cfg['sigma']:6.2f}"
                  f"  {cfg['gamma']:6.3f}  {cfg['n_or']:5d}")

        (OUT_DIR / "gabor_sweep.json").write_text(
            json.dumps([{"acc": acc, **cfg} for acc, cfg in sweep], indent=2),
            encoding="utf-8")

        save_sweep_summary(sweep, acc_base, OUT_DIR)
        if sweep:
            save_response_grid(data, sweep[0][1], OUT_DIR)
    else:
        # Gabor orientation fractions per digit (θ = 0°, 45°, 90°, 135°)
        orient_labels = [f"{int(i*180/N_ORIENT):3d}°" for i in range(N_ORIENT)]
        print("\nGabor orientation fractions per digit  (" +
              "  ".join(orient_labels) + "):")
        buckets: dict[str, list] = defaultdict(list)
        for _g, feat, label in data:
            buckets[label].append(feat[N_BINS:N_BINS + N_ORIENT])
        for d in digits:
            arr  = np.array(buckets[d])
            vals = "  ".join(f"{arr[:,i].mean():.3f}" for i in range(N_ORIENT))
            print(f"  '{d}':  {vals}")

        # Wedge angular-sector fractions per digit (0°..180°, N_WEDGES bins)
        wedge_labels = [f"{int(i*180/N_WEDGES):3d}°" for i in range(N_WEDGES)]
        print("\nWedge angular-sector fractions per digit  (" +
              "  ".join(wedge_labels) + "):")
        wedge_buckets: dict[str, list] = defaultdict(list)
        for _g, feat, label in data:
            wedge_buckets[label].append(feat[N_BINS + N_ORIENT:])
        for d in digits:
            arr  = np.array(wedge_buckets[d])
            vals = "  ".join(f"{arr[:,i].mean():.3f}" for i in range(N_WEDGES))
            print(f"  '{d}':  {vals}")

        save_feature_importance(data)
        save_pca_plot(data)

        # ── Timing benchmark ──────────────────────────────────────────────────
        import time as _time
        sample_gray = data[0][0]
        N_WARM, N_ITER = 50, 2000

        for _ in range(N_WARM):
            compute_features(sample_gray)
        _t0 = _time.perf_counter()
        for _ in range(N_ITER):
            compute_features(sample_gray)
        feat_us = (_time.perf_counter() - _t0) / N_ITER * 1e6

        n_digits_per_cell = 5
        cell_ms = feat_us * n_digits_per_cell / 1e3

        print()
        print("── Timing (single glyph, 12×20 px) ───────────────────────────")
        print(f"  compute_features (FFT + Gabor) : {feat_us:6.1f} µs")
        print(f"  estimated per cell (~{n_digits_per_cell} glyphs) : {cell_ms:6.2f} ms")
