# -*- coding: utf-8 -*-
"""
debugs/compare_stat_ocr_fft_runs.py -- permanent utility to diff two
persisted gfl2.stat_ocr_fft run reports (debugs/persist_run_result.py
JSON files), instead of hand-rolling a fresh ad-hoc comparison script
each time (this exploration's own history is full of those -- see
docs/known_issues.txt §15's many "STANDALONE ABLATION" tables, each a
one-off).  Going forward, generate a report with:

    python -m gfl2.stat_ocr_fft --verify-glyphs --images "single/*.png"

(writes tests/outputs/stat_ocr_fft_glyph_runs/<commit>_<dirty>_<label>.json
via verify_glyphs() + debugs/persist_run_result.py), then diff any two
reports with this script:

    python debugs/compare_stat_ocr_fft_runs.py <before.json> <after.json>
    python debugs/compare_stat_ocr_fft_runs.py --latest 2   # two most
                                                             # recent reports
                                                             # in the default dir

WHAT THIS SHOWS:
  1. The CURRENT (second/"after") run's per-digit table: classified,
     correct, misclassified, unknown, accuracy% -- per digit '0'-'9' plus
     TOTAL.
  2. A per-digit DELTA table (after minus before) for the same four
     counts, with an explicit REGRESSED / IMPROVED / unchanged verdict per
     digit, plus a call-out list of just the regressions and improvements
     (a table alone buries this; a human wants the short list first).
  3. Overall accuracy delta and a timing comparison (mean/stdev/cv,
     %-change, flagged if the change exceeds TIMING_FLAG_PCT).

SCHEMA SUPPORT: primarily targets verify_glyphs()'s report shape
({"per_digit", "totals", "timing", ...}).  Also accepts the older,
aggregate-only cell-level shape used earlier in this exploration (a
top-level "results" dict of {"pair_tiebreak_off"/"pair_tiebreak_on": {...}}
with no per-digit breakdown) -- those reports compare on totals/timing
only, with an explicit note that per-digit comparison isn't available
rather than silently skipping it.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
DEFAULT_DIR = _ROOT / "tests" / "outputs" / "stat_ocr_fft_glyph_runs"

DIGITS = "0123456789"
TIMING_FLAG_PCT = 5.0   # flag a timing change as notable beyond this %


# ── Loading / schema normalization ──────────────────────────────────────────

def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pick_pair_tiebreak_variant(raw: dict) -> dict:
    """Old aggregate-only reports nest results under
    results.pair_tiebreak_off / results.pair_tiebreak_on. Prefer 'off'
    (the default, apples-to-apples with verify_glyphs()'s own default)."""
    results = raw.get("results", {})
    return results.get("pair_tiebreak_off") or results.get("pair_tiebreak_on") or {}


def normalize(raw: dict) -> dict:
    """Return {"per_digit": {...} | None, "totals": {...}, "timing": {...},
    "meta": {...}} regardless of which of the two known schemas `raw` is."""
    if "per_digit" in raw and "totals" in raw:
        return {
            "per_digit": raw["per_digit"],
            "totals": raw["totals"],
            "timing": raw.get("timing", {}),
            "meta": {
                "run_start": raw.get("run_start"),
                "corpus": raw.get("corpus"),
                "feature_set": raw.get("feature_set"),
                "pair_tiebreak": raw.get("pair_tiebreak"),
            },
        }

    # Older, aggregate-only cell-level schema (no per-digit breakdown).
    variant = _pick_pair_tiebreak_variant(raw)
    total = variant.get("pct_total")
    correct = variant.get("pct_correct")
    totals = {
        "classified": total,
        "correct": correct,
        "misclassified": variant.get("misclassified"),
        "unknown": variant.get("no_read"),
        "accuracy_pct": variant.get("pct_accuracy_pct") or variant.get("accuracy_pct"),
    }
    timing = {
        "classify_time_mean_us": variant.get("classify_time_mean_us"),
        "classify_time_stdev_us": variant.get("classify_time_stdev_us"),
        "classify_time_cv": variant.get("classify_time_cv"),
    }
    return {
        "per_digit": None,   # not available in this schema
        "totals": totals,
        "timing": timing,
        "meta": {
            "run_start": None,
            "corpus": raw.get("corpus"),
            "feature_set": raw.get("feature_set"),
            "pair_tiebreak": None,
        },
    }


# ── Rendering ─────────────────────────────────────────────────────────────────

def _fmt(v, spec="") -> str:
    if v is None:
        return "n/a"
    return format(v, spec) if spec else str(v)


def print_meta(label: str, norm: dict) -> None:
    m = norm["meta"]
    print(f"[{label}]")
    if m.get("run_start"):
        print(f"  generated: {m['run_start']}")
    if m.get("corpus"):
        print(f"  corpus:    {m['corpus']}")
    if m.get("feature_set"):
        print(f"  features:  {m['feature_set']}")
    if m.get("pair_tiebreak") is not None:
        print(f"  pair_tiebreak: {'ON' if m['pair_tiebreak'] else 'off'}")


def print_current_per_digit(norm: dict) -> None:
    per_digit = norm["per_digit"]
    if per_digit is None:
        print("\n(no per-digit breakdown in this report -- older aggregate-only "
              "schema; showing totals/timing comparison only)")
        return
    print(f"\nCURRENT run, per digit:")
    print(f"  {'digit':>6} {'classified':>10} {'correct':>8} {'misclassified':>13} "
          f"{'unknown':>8} {'accuracy%':>10}")
    for d in DIGITS:
        b = per_digit.get(d)
        if b is None:
            print(f"  {d:>6}   (missing)")
            continue
        acc = 100 * b["correct"] / b["classified"] if b["classified"] else None
        print(f"  {d:>6} {b['classified']:>10} {b['correct']:>8} "
              f"{b['misclassified']:>13} {b['unknown']:>8} {_fmt(acc, '.2f')}")


def compare_per_digit(before: dict, after: dict) -> None:
    pd_before, pd_after = before["per_digit"], after["per_digit"]
    if pd_before is None or pd_after is None:
        return

    all_digits = sorted(set(pd_before) | set(pd_after), key=lambda d: (d not in DIGITS, d))
    print(f"\nPER-DIGIT DELTA (after - before):")
    print(f"  {'digit':>6} {'Dclassified':>12} {'Dcorrect':>9} {'Dmisclass':>10} "
          f"{'Dunknown':>9}  verdict")

    regressions, improvements = [], []
    for d in all_digits:
        b = pd_before.get(d, {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0})
        a = pd_after.get(d, {"classified": 0, "correct": 0, "misclassified": 0, "unknown": 0})
        d_cls  = a["classified"] - b["classified"]
        d_corr = a["correct"] - b["correct"]
        d_mis  = a["misclassified"] - b["misclassified"]
        d_unk  = a["unknown"] - b["unknown"]

        bad_delta = d_mis + d_unk   # more wrong/unsure answers = worse
        if bad_delta > 0:
            verdict = "REGRESSED"
            regressions.append((d, b, a, d_mis, d_unk))
        elif bad_delta < 0:
            verdict = "IMPROVED"
            improvements.append((d, b, a, d_mis, d_unk))
        else:
            verdict = "unchanged" if d_corr == 0 else ("IMPROVED" if d_corr > 0 else "REGRESSED")
            if verdict == "IMPROVED":
                improvements.append((d, b, a, d_mis, d_unk))
            elif verdict == "REGRESSED":
                regressions.append((d, b, a, d_mis, d_unk))

        print(f"  {d:>6} {d_cls:>+12} {d_corr:>+9} {d_mis:>+10} {d_unk:>+9}  {verdict}")

    print("\nREGRESSIONS:" if regressions else "\nREGRESSIONS: none")
    for d, b, a, d_mis, d_unk in regressions:
        print(f"  '{d}': misclassified {b['misclassified']}->{a['misclassified']} "
              f"({d_mis:+d}), unknown {b['unknown']}->{a['unknown']} ({d_unk:+d})")

    print("\nIMPROVEMENTS:" if improvements else "\nIMPROVEMENTS: none")
    for d, b, a, d_mis, d_unk in improvements:
        print(f"  '{d}': misclassified {b['misclassified']}->{a['misclassified']} "
              f"({d_mis:+d}), unknown {b['unknown']}->{a['unknown']} ({d_unk:+d})")


def compare_totals(before: dict, after: dict) -> None:
    tb, ta = before["totals"], after["totals"]
    print(f"\nTOTALS:")
    print(f"  {'':>14} {'before':>10} {'after':>10} {'delta':>10}")
    for key in ("classified", "correct", "misclassified", "unknown"):
        vb, va = tb.get(key), ta.get(key)
        delta = (va - vb) if (vb is not None and va is not None) else None
        print(f"  {key:>14} {_fmt(vb):>10} {_fmt(va):>10} {_fmt(delta, '+d') if delta is not None else 'n/a':>10}")

    ab, aa = tb.get("accuracy_pct"), ta.get("accuracy_pct")
    if ab is not None and aa is not None:
        print(f"  {'accuracy%':>14} {ab:>10.2f} {aa:>10.2f} {aa - ab:>+10.2f}")
        verdict = "IMPROVEMENT" if aa > ab else ("REGRESSION" if aa < ab else "UNCHANGED")
        print(f"  -> accuracy {verdict} ({aa - ab:+.2f} pts)")


def compare_timing(before: dict, after: dict) -> None:
    tb, ta = before["timing"], after["timing"]
    mb, ma = tb.get("classify_time_mean_us"), ta.get("classify_time_mean_us")
    print(f"\nTIMING:")
    print(f"  {'':>10} {'before':>12} {'after':>12} {'delta':>10}")
    for key, label in (("classify_time_mean_us", "mean_us"),
                        ("classify_time_stdev_us", "stdev_us"),
                        ("classify_time_cv", "cv")):
        vb, va = tb.get(key), ta.get(key)
        delta = (va - vb) if (vb is not None and va is not None) else None
        print(f"  {label:>10} {_fmt(vb, '.3f' if key == 'classify_time_cv' else '.1f') if vb is not None else 'n/a':>12} "
              f"{_fmt(va, '.3f' if key == 'classify_time_cv' else '.1f') if va is not None else 'n/a':>12} "
              f"{_fmt(delta, '+.3f' if key == 'classify_time_cv' else '+.1f') if delta is not None else 'n/a':>10}")

    if mb and ma:
        pct_change = 100 * (ma - mb) / mb
        direction = "slower" if pct_change > 0 else "faster"
        flag = "  <-- NOTABLE" if abs(pct_change) >= TIMING_FLAG_PCT else ""
        print(f"  -> {abs(pct_change):.1f}% {direction} per glyph/cell{flag}")


# ── Report selection ──────────────────────────────────────────────────────────

def _latest_reports(directory: Path, n: int) -> list[Path]:
    files = sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if len(files) < n:
        sys.exit(f"Only {len(files)} report(s) found in {directory}, need {n}. "
                  f"Generate more with: python -m gfl2.stat_ocr_fft --verify-glyphs")
    return files[-n:]


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reports", nargs="*", type=Path,
                     help="Two report JSON paths: <before> <after>. "
                          "Omit and use --latest instead to auto-select.")
    ap.add_argument("--latest", type=int, default=0, metavar="N",
                     help="Ignore `reports`; compare the N=2 most recently "
                          "modified reports in --dir instead.")
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR,
                     help=f"Directory to search for --latest  [default: {DEFAULT_DIR}]")
    args = ap.parse_args(argv)

    if args.latest:
        if args.latest != 2:
            sys.exit("--latest only supports N=2 (a single before/after comparison)")
        before_path, after_path = _latest_reports(args.dir, 2)
    elif len(args.reports) == 2:
        before_path, after_path = args.reports
    else:
        ap.error("pass exactly two report paths, or use --latest 2")
        return

    for p in (before_path, after_path):
        if not p.exists():
            sys.exit(f"Report not found: {p}")

    before = normalize(_load(before_path))
    after = normalize(_load(after_path))

    print("=" * 72)
    print_meta(f"BEFORE: {before_path.name}", before)
    print()
    print_meta(f"AFTER:  {after_path.name}", after)
    if before["meta"].get("feature_set") and after["meta"].get("feature_set") \
            and before["meta"]["feature_set"] != after["meta"]["feature_set"]:
        print("\n*** feature_set DIFFERS between these two reports -- this is not "
              "an apples-to-apples parameter change, the classifier itself changed ***")
    print("=" * 72)

    print_current_per_digit(after)
    compare_per_digit(before, after)
    compare_totals(before, after)
    compare_timing(before, after)
    print("=" * 72)


if __name__ == "__main__":
    main()
