# -*- coding: utf-8 -*-
"""
debugs/persist_run_result.py -- persist an exploration run's results (e.g.
gfl2.stat_ocr_fft.verify() output) to a JSON file named after the code state
that produced it, so results survive across sessions without relying on
memory or scrollback.

Filename convention: tests/outputs/<subdir>/<commit>_<dirty>.json
  commit -- short hash of HEAD (`git rev-parse --short HEAD`)
  dirty  -- total changed lines (insertions+deletions) in tracked files vs
            HEAD (`git diff --numstat HEAD`), 0 if the working tree is clean.
            Since exploration work usually runs against an uncommitted tree,
            this distinguishes "same commit, different in-progress edit" runs
            that would otherwise silently overwrite each other.

This is a library function, not a CLI -- import save_run_result() from a
one-off script the way debugs/persist_fft_run_example.py (if one exists) or
an ad-hoc scratch script would.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

_ROOT = Path(__file__).parent.parent


def _git(args: list[str]) -> str:
    return subprocess.run(
        ["git"] + args, cwd=_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def commit_dirty_tag() -> str:
    """'<short-commit>_<dirty-line-count>', e.g. 'eb187e2_263' or 'eb187e2_0'
    for a clean tree. dirty counts only TRACKED file changes (git diff
    --numstat) -- untracked scratch files don't affect the tag."""
    commit = _git(["rev-parse", "--short", "HEAD"])
    numstat = _git(["diff", "--numstat", "HEAD", "--", "."])
    dirty = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            dirty += int(parts[0]) + int(parts[1])
    return f"{commit}_{dirty}"


def save_run_result(data: dict, subdir: str = "stat_ocr_fft_runs", label: str = "") -> Path:
    """Write `data` (must be JSON-serializable) to
    tests/outputs/<subdir>/<commit>_<dirty>[_<label>].json and return the path."""
    tag = commit_dirty_tag()
    name = f"{tag}_{label}.json" if label else f"{tag}.json"
    out_dir = _ROOT / "tests" / "outputs" / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / name
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return out_path
