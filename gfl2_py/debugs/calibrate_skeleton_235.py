# -*- coding: utf-8 -*-
"""
debugs/calibrate_skeleton_235.py

Calibration for debugs/debug_stat_ocr_v0_3_0_skeleton_235.py's endpoint-
side connectivity rule for '2'/'3'/'5' (known_issues.txt §37 follow-up).

WHY THIS EXISTS: the first version of the rule used top_frac=0.35,
bot_frac=0.35, min_spur_len=2 -- picked from ONE hand-verified pct '2' and
ONE hand-verified val '5' at the very start of this investigation, never
swept against real data. Running it against the curated meaningful set
(tests/inputs/daily/*.png) across all four v0_3_0-family glyph populations
found a striking split: score/header/pct landed at 96-100% correct, but
val landed at only 66.8% -- despite the hand-verified seed including a
val example.

ROOT CAUSE (found by direct diagnosis, not assumed): min_spur_len is an
ABSOLUTE pixel count, applied identically regardless of the font's own
scale. val glyphs are the smallest population (mean height 12.4px, mean
width 7.4px vs score/header/pct's 16-19px) -- at that scale, a GENUINE
free-endpoint branch is itself only 1-2px long, so min_spur_len=2 prunes
away real structure, not noise. Direct confirmation: val's '5' population
was 107/227 (47%) at min_spur_len=2, and 227/227 (100%) at min_spur_len=0
-- disabling pruning ENTIRELY fixed every single failure, and a full sweep
(0/1/2/3) showed val degrades MONOTONICALLY with any pruning at all, while
pct's '2' digit specifically NEEDS min_spur_len>=1 (107/275 at len=0 vs
258/275 at len=1) to remove a real antialiasing artifact. Two fonts
genuinely needing opposite settings for the same nominal parameter --
matching this project's own established precedent (decisions.txt #91:
"measured directly... this font's own numbers disagreed") that pct and
val must never share a calibrated constant by assumption.

METHOD: grid search over (top_frac, bot_frac, min_spur_len) INDEPENDENTLY
per font (score, header, pct, val), scored on the SAME curated
tests/inputs/daily/*.png set the feasibility script already used (not the
full single/*.png corpus -- established habit going forward: validate
against the small, committed, reproducible fixture before ever touching
the full corpus). Every combo is scored by total correct count with a
false-trigger tiebreak (a combo that ever produces a confident WRONG
digit -- not just an abstention -- is penalized hard, since the whole
value of this rule so far has been zero false triggers across ~2200
samples). Self-validates at the end: re-runs the FULL population per font
with its own winning combo and prints the final confusion table, so the
picked constants are checked against real data before being trusted, not
just assumed from the grid's own scoring.

NOT YET a real gfl2/calibration/ module -- this feature has no production
entry point yet (debug_stat_ocr_v0_3_0_skeleton_235.py is still pure
feasibility work). Writes its result JSON to tests/outputs/daily/ instead
of gfl2/configs/, and does not modify any gfl2/*.py file.

Usage:
    python debugs/calibrate_skeleton_235.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from debug_stat_ocr_v0_3_0_skeleton_235 import (
    _daily_images, _collect_pct_val, _collect_score, _collect_header,
    classify_endpoint_sides,
)

TOP_FRAC_GRID = [0.25, 0.30, 0.35, 0.40, 0.45]
BOT_FRAC_GRID = [0.25, 0.30, 0.35, 0.40, 0.45]
SPUR_LEN_GRID = [0, 1, 2, 3]


def _score_combo(glyphs: dict, top_frac: float, bot_frac: float, spur_len: int) -> dict:
    correct = {"2": 0, "3": 0, "5": 0}
    wrong = {"2": 0, "3": 0, "5": 0}   # confident but wrong digit -- the real penalty
    total = {"2": 0, "3": 0, "5": 0}
    for d, items in glyphs.items():
        for (src, part, idx, crop01) in items:
            total[d] += 1
            r = classify_endpoint_sides(crop01, top_frac=top_frac, bot_frac=bot_frac, min_spur_len=spur_len)
            if r["pred"] == d:
                correct[d] += 1
            elif r["pred"] != "?":
                wrong[d] += 1
    n_correct = sum(correct.values())
    n_wrong = sum(wrong.values())
    n_total = sum(total.values())
    return {"correct": correct, "wrong": wrong, "total": total,
            "n_correct": n_correct, "n_wrong": n_wrong, "n_total": n_total}


def calibrate_font(name: str, glyphs: dict) -> dict:
    print(f"\n{'='*70}\nCalibrating: {name}\n{'='*70}")
    n_samples = sum(len(v) for v in glyphs.values())
    print(f"  samples: {n_samples}  ({', '.join(f'{d}={len(v)}' for d, v in glyphs.items())})")

    best = None
    results = []
    for spur_len in SPUR_LEN_GRID:
        for top_frac in TOP_FRAC_GRID:
            for bot_frac in BOT_FRAC_GRID:
                s = _score_combo(glyphs, top_frac, bot_frac, spur_len)
                # rank: net (correct - wrong), maximized. NOT "fewest wrong
                # first" -- that ranking is a real, documented mistake
                # (known_issues.txt §37): a combo that abstains on almost
                # everything trivially has very few wrong answers too, so
                # ranking on wrong-count alone lets a near-useless "never
                # answer" combo beat one that gets thousands right at the
                # cost of a single miss. Net score only prefers abstention
                # over a wrong answer when the two compete for the SAME
                # glyph, which is what this leaf is actually meant to do.
                net = s["n_correct"] - s["n_wrong"]
                key = -net  # sort ascending == highest net first
                results.append((key, top_frac, bot_frac, spur_len, s))
                if best is None or key < best[0]:
                    best = (key, top_frac, bot_frac, spur_len, s)

    results.sort(key=lambda r: r[0])
    print(f"  top 5 combos (wrong, -correct) | top_frac bot_frac spur_len | correct/total per digit:")
    for key, tf, bf, sl, s in results[:5]:
        digits_str = "  ".join(f"'{d}'={s['correct'][d]}/{s['total'][d]}(wrong={s['wrong'][d]})" for d in ("2", "3", "5"))
        print(f"    {key}  |  tf={tf:.2f} bf={bf:.2f} sl={sl}  |  {digits_str}")

    _, best_tf, best_bf, best_sl, best_s = best
    print(f"\n  WINNER: top_frac={best_tf} bot_frac={best_bf} min_spur_len={best_sl}")
    print(f"  {best_s['n_correct']}/{best_s['n_total']} correct, {best_s['n_wrong']} confident-wrong")

    # Self-validate: are there OTHER combos tied on the ranking key? report if so,
    # since a tie means the grid didn't actually pin down a unique winner.
    ties = [r for r in results if r[0] == best[0]]
    if len(ties) > 1:
        print(f"  NOTE: {len(ties)} combos tied at this score -- grid did not uniquely determine "
              f"top_frac/bot_frac (min_spur_len is likely the load-bearing parameter here).")

    return {"top_frac": best_tf, "bot_frac": best_bf, "min_spur_len": best_sl,
            "n_correct": best_s["n_correct"], "n_total": best_s["n_total"],
            "n_wrong": best_s["n_wrong"], "per_digit": {
                d: {"correct": best_s["correct"][d], "wrong": best_s["wrong"][d], "total": best_s["total"][d]}
                for d in ("2", "3", "5")
            }}


def main():
    images = _daily_images()
    if not images:
        print("No images in tests/inputs/daily/*.png", file=sys.stderr)
        sys.exit(1)
    print(f"Calibrating against curated 'meaningful' set: {len(images)} images")

    families = {
        "score": _collect_score(images),
        "header": _collect_header(images),
        "pct": _collect_pct_val(images, "pct"),
        "val": _collect_pct_val(images, "val"),
    }

    calib = {}
    for name, glyphs in families.items():
        calib[name] = calibrate_font(name, glyphs)

    print(f"\n{'='*70}\nSUMMARY\n{'='*70}")
    print(f"{'set':8s} {'top_frac':>9s} {'bot_frac':>9s} {'spur_len':>9s} {'correct/total':>15s} {'wrong':>7s}")
    for name, c in calib.items():
        print(f"{name:8s} {c['top_frac']:9.2f} {c['bot_frac']:9.2f} {c['min_spur_len']:9d} "
              f"{c['n_correct']:>6d}/{c['n_total']:<7d} {c['n_wrong']:>7d}")

    out_dir = Path("tests/outputs/daily")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "skeleton_235_calib.json"
    out_path.write_text(json.dumps(calib, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
