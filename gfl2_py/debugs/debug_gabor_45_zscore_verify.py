# -*- coding: utf-8 -*-
"""
debugs/debug_gabor_45_zscore_verify.py -- §24 follow-up: fix gabor_45's
degenerate self-fraction normalization, then measure whether the corrected
feature can serve as a PASS-THROUGH GATE for {4,7} (or the broader
line-dominant {1,4,7} group) vs the rest -- NOT as a 4-vs-7 discriminator.
That distinction matters and is the whole point of this script's second
half: a feature can be structurally incapable of telling two classes apart
from each other while still being an excellent binary gate for "is this
glyph in {that pair} or not" -- those are different questions with
different answers here.

BACKGROUND (docs/known_issues.txt §24): gfl2/stat_ocr_fft.py's compute_features()
reports Gabor as a self-fraction, resp/(sum(resps)+eps) -- meaningful when 2+
orientations shared the denominator, degenerate once N_ORIENT dropped to 1
(only 45deg survives): the fraction of ONE value against its own sum is
always ~1.0 regardless of digit. Confirmed on the shipped templates: every
digit's gabor_45 centroid is exactly 1.0000000000 (variance 3.6e-26) -- 0.0%
contribution to any real classification decision, whether used to
discriminate OR to gate.

FIX: use the raw Gabor response magnitude instead of the self-fraction (see
_raw_gabor45 below -- identical math to compute_features()'s gabor block,
minus the degenerate division). NOTE: this fix does NOT need to be wired
into gfl2/stat_ocr_fft.py's Agent A z-scored L2 distance to be useful as a
gate -- a plain 1D threshold interval on the raw value is a completely
separate, much simpler consumer that was never tried before this script.
(A z-scored version WAS tried, wired into Agent A directly, and reverted
after it regressed glyph accuracy 100.0%->87.12% -- see the git history /
known_issues.txt §24 for that dead end. This script does not repeat it.)

PART 1 -- PAIRWISE '4' vs '7' DISCRIMINATION (the ORIGINAL framing):
measures whether gabor_45 alone can decide WHICH of '4'/'7' a glyph is.
Answer: NO -- d'=0.213, forced-choice accuracy 42.4% (worse than the 56.6%
majority-class baseline). '4' and '7' share both the top bar and diagonal
descender by construction, so 45deg-oriented energy content is nearly
identical between them.

PART 2 -- PASS-THROUGH GATE (the CORRECTED framing, per direct feedback):
measures whether gabor_45 can PASS {4,7} (or {1,4,7}) through while
REJECTING the other digits, i.e. a binary accept/reject gate ahead of an
expensive downstream feature (vstroke/hbar, known_issues.txt §19 -- ~81%
of feature-extraction time), not a discriminator within the accepted set.
This is a fundamentally different, much easier question, and the answer
here is a clear YES for the broader {1,4,7} line-dominant group ('1' is
the digit vstroke already targets alongside '4'/'7' -- known_issues.txt
§19's vstroke docstring: "targets '1'/'4' vs '7'"), and a weaker but still
strong yes for {4,7} alone (contaminated only by digit '1' overlapping the
low end of the range).

Usage:
    python debugs/debug_gabor_45_zscore_verify.py
    python debugs/debug_gabor_45_zscore_verify.py --images "single/*.png"
"""
from __future__ import annotations
import sys, glob as _glob
from pathlib import Path
import numpy as np
import cv2
import json

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from gfl2.stat_ocr import _collect_cells, _load_tess_gt_cache
from gfl2.stat_ocr_fft import _extract_pct_digit_glyphs, _GABOR_KERNELS


def _raw_gabor45(gray_norm: np.ndarray) -> float:
    """The FIXED feature: raw Gabor response magnitude, not the degenerate
    self-fraction (see module docstring). Identical math to
    gfl2.stat_ocr_fft.compute_features()'s gabor block, minus the
    resp/(sum(resps)+eps) division that collapses to ~1.0 at N_ORIENT=1."""
    f32 = gray_norm.astype(np.float32)
    return float(np.abs(cv2.filter2D(f32, -1, _GABOR_KERNELS[0])).mean())


def collect_glyphs(image_paths):
    gt_cache = _load_tess_gt_cache() or {}
    samples = _collect_cells(image_paths, tess_only=True, gt_cache=gt_cache)
    gt_file = Path("stat_gt_overrides.json")
    if gt_file.exists():
        gt_overrides = json.loads(gt_file.read_text(encoding="utf-8"))
        for item in samples:
            ov = gt_overrides.get(item["source"])
            if ov and "pct" in ov:
                item["pct"] = ov["pct"]

    buckets: dict[str, list[float]] = {d: [] for d in "0123456789"}
    for item in samples:
        glyphs = _extract_pct_digit_glyphs(item["cell"], item.get("pct") or "")
        if glyphs is None:
            continue
        for norm, label in glyphs:
            buckets.setdefault(label, []).append(_raw_gabor45(norm))
    return buckets


def _best_gate(pos: np.ndarray, neg: np.ndarray, step: float = 5.0):
    """Sweep [lo, hi] to maximize Youden's J (recall - false_trigger_rate).
    Coarse grid search, not gradient-based -- the value range here (a few
    hundred, ~1753+8574 samples) makes an exhaustive sweep cheap and exact
    enough; no need for anything fancier."""
    best = None
    for lo in np.arange(pos.min() - 30, pos.mean(), step):
        for hi in np.arange(pos.mean(), pos.max() + 30, step):
            recall = float(np.mean((pos >= lo) & (pos <= hi)))
            false_trigger = float(np.mean((neg >= lo) & (neg <= hi)))
            j = recall - false_trigger
            if best is None or j > best[0]:
                best = (j, lo, hi, recall, false_trigger)
    return best


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default="single/*.png")
    args = ap.parse_args(argv)

    image_paths = sorted(Path(p) for p in _glob.glob(args.images)
                         if "debug" not in Path(p).stem)
    if not image_paths:
        sys.exit(f"No images matched: {args.images}")

    print(f"Collecting glyphs from {len(image_paths)} image(s) ...")
    buckets = collect_glyphs(image_paths)

    print(f"\n{'digit':>6} {'n':>6} {'mean':>10} {'std':>8}")
    for d in "0123456789":
        v = np.array(buckets[d])
        print(f"{d:>6} {len(v):>6} {v.mean():>10.2f} {v.std():>8.2f}")

    # ── PART 1: pairwise 4-vs-7 discrimination (in-sample corpus, same
    # convention as this project's other stat_ocr_fft explorations) ─────────
    v4, v7 = np.array(buckets["4"]), np.array(buckets["7"])
    mean4, mean7 = v4.mean(), v7.mean()
    std4, std7 = v4.std(), v7.std()
    pooled_std = np.sqrt((std4 ** 2 + std7 ** 2) / 2)
    d_prime = (mean4 - mean7) / pooled_std if pooled_std > 0 else float("nan")
    correct = int(np.sum(np.abs(v4 - mean4) < np.abs(v4 - mean7))) + \
              int(np.sum(np.abs(v7 - mean7) < np.abs(v7 - mean4)))
    total = len(v4) + len(v7)

    print(f"\n{'='*68}")
    print("PART 1 -- pairwise '4' vs '7' discrimination (WHICH one is it?)")
    print(f"{'='*68}")
    print(f"  mean4={mean4:.2f}  std4={std4:.2f}  (n={len(v4)})")
    print(f"  mean7={mean7:.2f}  std7={std7:.2f}  (n={len(v7)})")
    print(f"  d'  = {d_prime:.3f}")
    print(f"  standalone forced-choice accuracy: {correct}/{total} ({100*correct/total:.1f}%)"
          f"  (majority-class baseline: {100*max(len(v4),len(v7))/total:.1f}%)")
    print("  Verdict: NO -- near-total overlap; cannot decide which of the pair a glyph is.")

    # ── PART 2: pass-through gate ({4,7} or {1,4,7}) vs the rest ─────────────
    print(f"\n{'='*68}")
    print("PART 2 -- pass-through gate (IS this glyph in the target group?)")
    print(f"{'='*68}")

    for label, target_digits in (("{4,7}", ("4", "7")), ("{1,4,7}", ("1", "4", "7"))):
        pos = np.concatenate([buckets[d] for d in target_digits])
        neg_digits = [d for d in "0123456789" if d not in target_digits]
        neg = np.concatenate([buckets[d] for d in neg_digits])
        j, lo, hi, recall, false_trigger = _best_gate(pos, neg)
        print(f"\n  Target group {label}  (n_pos={len(pos)}, n_neg={len(neg)})")
        print(f"    best gate interval = [{lo:.1f}, {hi:.1f}]")
        print(f"    recall             = {100*recall:.1f}%  (fraction of {label} correctly passed)")
        print(f"    false_trigger_rate = {100*false_trigger:.2f}%  (fraction of the OTHER "
              f"{len(neg_digits)} digits incorrectly passed)")
        print(f"    per-digit pass-rate at this interval:")
        for d in "0123456789":
            v = np.array(buckets[d])
            passed = 100 * np.mean((v >= lo) & (v <= hi))
            tag = " <- TARGET" if d in target_digits else (" <- false trigger" if passed > 1 else "")
            print(f"      {d}: {passed:5.1f}%{tag}")

    print(f"\n{'='*68}")
    print("CONCLUSION")
    print(f"{'='*68}")
    print("""  gabor_45 cannot tell '4' from '7' apart (Part 1: NO). But that was
  never what a GATE needs to do -- a gate only needs to accept the target
  group and reject everything else, then hand the accepted glyphs to a
  downstream feature (vstroke/hbar) that CAN discriminate within the group.

  As a {1,4,7} pass-through gate (Part 2), gabor_45 is close to perfect:
  the line-dominant group ('1'/'4'/'7' -- exactly the group vstroke already
  targets, known_issues.txt §19) separates cleanly from the arc/loop-
  dominant rest ('0','2','3','5','6','8','9'). As a {4,7}-only gate
  (excluding '1'), recall stays high but false-trigger rises because a
  fraction of '1' glyphs fall inside the same raw-response range as '4'/'7'.

  IMPLICATION: gabor_45 (fixed, raw -- NOT the z-scored version that
  regressed when wired into Agent A) is a genuine candidate for a cheap
  PRE-FILTER ahead of vstroke/hbar's expensive 2D-sliding search (~81% of
  feature-extraction time per known_issues.txt §19) -- run the full
  vstroke+hbar computation only for glyphs the gate accepts into
  {1,4,7}, and use a cheap fallback (or skip straight to Agent B/hist) for
  the rest. This is NOT wired into production by this script -- it is a
  measurement, matching this project's convention of validating an idea
  standalone before touching the shipped classify path (see
  docs/known_issues.txt §24's ring+paren cheap-first-pass precedent, which
  reached a similar but not-yet-implemented state for the loop group).
  In-sample corpus only (same convention as this project's other
  stat_ocr_fft --build/--verify measurements) -- not held-out validated.""")


if __name__ == "__main__":
    main()
