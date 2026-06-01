#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compile_gfl2.py - Force a clean recompilation of the gfl2 package.

Run this once after pulling updates or whenever source files change.
After running, main.py can be invoked repeatedly without any runtime
cache-invalidation overhead.

Uses CHECKED_HASH invalidation mode: Python validates .pyc files by
hashing the source at import time, not by comparing timestamps. This
is immune to the cross-platform mtime issue where edits from a Linux
sandbox do not update the file's mtime as seen by Windows Python.

Usage:
    python compile_gfl2.py
"""
import py_compile
import shutil
import sys
from pathlib import Path

ROOT   = Path(__file__).parent
GFL2   = ROOT / "gfl2"
MODE   = py_compile.PycInvalidationMode.CHECKED_HASH


def main() -> None:
    sources = sorted(GFL2.rglob("*.py"))

    # Step 1: wipe all existing .pyc / __pycache__ dirs
    removed = 0
    for d in GFL2.rglob("__pycache__"):
        try:
            shutil.rmtree(d)
            removed += 1
        except Exception as e:
            # Locked files — overwrite magic bytes so Python treats them invalid
            for pyc in d.glob("*.pyc"):
                try:
                    data = pyc.read_bytes()
                    pyc.write_bytes(b"\x00\x00\x00\x00" + data[4:])
                except Exception:
                    pass
    print(f"Wiped {removed} __pycache__ director{'y' if removed == 1 else 'ies'}")

    # Step 2: recompile every .py with CHECKED_HASH mode
    ok = failed = 0
    for src in sources:
        try:
            py_compile.compile(str(src), doraise=True,
                               invalidation_mode=MODE)
            ok += 1
        except py_compile.PyCompileError as e:
            print(f"  FAIL: {src.relative_to(ROOT)}: {e}", file=sys.stderr)
            failed += 1

    print(f"Compiled {ok} file(s)" + (f", {failed} error(s)" if failed else "") + ".")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
