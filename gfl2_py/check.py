#!/usr/bin/env python3
"""check.py — compile + test in one step.

Usage:
    python check.py              # compile then run all tests
    python check.py tests/test_weekly_gunsmoke.py   # compile then run one file
    python check.py -k score     # compile then pytest -k filter
"""
import sys
import subprocess

compile_result = subprocess.run([sys.executable, "compile_gfl2.py"])
if compile_result.returncode != 0:
    sys.exit(compile_result.returncode)

pytest_args = [sys.executable, "-m", "pytest", "-q", "--no-header", "--tb=short"]
pytest_args += sys.argv[1:] if len(sys.argv) > 1 else ["tests/"]
sys.exit(subprocess.run(pytest_args).returncode)
