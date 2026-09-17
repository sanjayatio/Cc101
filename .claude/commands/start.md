# Session warm-up for gfl2_py

Read `gfl2_py/reference.txt` in full, then read `gfl2_py/docs/known_issues.txt` and skip any
issue whose STATUS line contains RESOLVED or ACCEPTED. Also read
`gfl2_py/docs/action_items.txt` and skip any item whose STATUS line is DONE.

Check for pending checkpoint drafts: list `gfl2_py/docs/drafts/*.md` if the
directory exists. These are gitignored, undecided notes from a session that
ended via `/checkpoint` instead of `/land` — surface them so they don't get
silently forgotten (see `.claude/commands/checkpoint.md`).

Run `python gfl2_py/compile_gfl2.py` and `pytest gfl2_py/tests/ -q --no-header --tb=no`.

Print a concise briefing:
- Open/mitigated issues (one line each)
- Open/in-progress action items (one line each)
- Pending checkpoint drafts, if any (filename + one-line topic from each) —
  omit this section entirely if `gfl2_py/docs/drafts/` is empty or absent
- Compile result
- Test pass/fail count
- Key CLI commands (from gfl2_py/reference.txt §5)

End with: "Ready. What would you like to work on?"
