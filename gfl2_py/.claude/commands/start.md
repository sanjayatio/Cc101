# Session warm-up for gfl2_py

Read `reference.txt` in full, then read `docs/known_issues.txt` and skip any
issue whose STATUS line contains RESOLVED or ACCEPTED. Also read
`docs/action_items.txt` and skip any item whose STATUS line is DONE.

Run `python compile_gfl2.py` and `pytest tests/ -q --no-header --tb=no`.

Print a concise briefing:
- Open/mitigated issues (one line each)
- Open/in-progress action items (one line each)
- Compile result
- Test pass/fail count
- Key CLI commands (from reference.txt §5)

End with: "Ready. What would you like to work on?"
