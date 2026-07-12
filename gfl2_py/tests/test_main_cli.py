"""
tests/test_main_cli.py
----------------------
Tests main.py's own argparse layer directly (main.build_arg_parser()), not
gfl2.patterns.daily_gunsmoke.parse() -- the two are different layers and a
default at one doesn't guarantee the other. Filed specifically to close a
real gap: tests/test_daily_gunsmoke.py's v0_3_0-engine tests call parse()
directly with tess_fallback passed explicitly, so they validate the
mechanism but say nothing about main.py's actual --stat-tess-fallback
default. Nothing else in the suite ever imports main or constructs its
parser (docs/decisions.txt #78's own landing found this gap by direct
question, not by discovery during implementation).

No subprocess needed: main.build_arg_parser() returns the real parser
main() itself uses, so parser.parse_args([...]) exercises the exact same
defaults/choices without any image-processing side effects.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import main


def _parse(*extra_args):
    return main.build_arg_parser().parse_args(["dummy.png", *extra_args])


def test_stat_tess_fallback_defaults_off():
    """decisions.txt #78: --stat-tess-fallback must default to False --
    this is the exact default a future accidental flip back to True would
    silently re-introduce the always-on-Tesseract cost this decision was
    about (known_issues.txt §31's 15-19s/image figure for --stat-ocr-engine
    v0_3_0)."""
    args = _parse()
    assert args.stat_tess_fallback is False


def test_stat_tess_fallback_can_be_enabled():
    args = _parse("--stat-tess-fallback")
    assert args.stat_tess_fallback is True


def test_stat_tess_fallback_explicit_off():
    args = _parse("--no-stat-tess-fallback")
    assert args.stat_tess_fallback is False


def test_stat_ocr_engine_default_is_v0_1_0():
    args = _parse()
    assert args.stat_ocr_engine == "v0_1_0"


def test_stat_ocr_engine_accepts_v0_3_0():
    """decisions.txt #78: "dp" (now "v0_3_0") must be a valid --stat-ocr-engine
    choice -- this is the actual CLI surface known_issues.txt §31's SCOPE
    change (EXPLORE -> MIXED) refers to."""
    args = _parse("--stat-ocr-engine", "v0_3_0")
    assert args.stat_ocr_engine == "v0_3_0"


def test_stat_ocr_engine_rejects_unknown_choice():
    with pytest.raises(SystemExit):
        _parse("--stat-ocr-engine", "not-a-real-engine")
