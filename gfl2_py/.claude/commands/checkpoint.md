# Checkpoint this session for gfl2_py (draft only — no doc edits, no commit)

Use this to end a session that ISN'T ready for `/land` — the normal case.
Concluding without finalizing is expected; what's NOT okay is leaving that
work as an anonymous, uncommitted mutation of a permanent doc file, where a
later session can't tell if it's reviewed, half-done, or safe to bundle into
an unrelated commit (this happened for real: a prior session's addendum to
`docs/decisions.txt` sat uncommitted and got swept into a later commit with
no one having deliberately reviewed it as its own thing).

This skill NEVER edits `docs/known_issues.txt`, `docs/decisions.txt`,
`docs/takeaways.txt`, `docs/action_items.txt`, `docs/technical_design.txt`,
or `reference.txt`. It writes everything to one new, gitignored, disposable
file instead — the permanent docs stay untouched and the working tree stays
clean until a human deliberately runs `/land`.

1. Infer what happened this session: takeaways (generalizable lessons),
   action items (opened/closed/still-open follow-ups), issues found (bugs,
   regressions, resolved/mitigated/open — with SCOPE: MAIN/EXPLORE/MIXED
   per known_issues.txt's own key), and any design decisions made — same
   inference `/land` already does, just not written to the same place.

2. Create `docs/drafts/` if it doesn't exist, then write ONE file:
   `docs/drafts/<UTC timestamp, e.g. 20260710-0915>_draft.md` (get the
   timestamp via `date -u +%Y%m%d-%H%M`, don't guess it). Structure:

   ```
   # Session draft — <one-line topic>

   ## Context
   <one paragraph: what was being worked on and why>

   ## Proposed known_issues.txt entries
   <full entry text, ready to paste in, each tagged with its SCOPE key —
    or "none" if nothing rises to that bar>

   ## Proposed decisions.txt entries
   <full entry text, or "none">

   ## Proposed takeaways.txt entries
   <full entry text, or "none">

   ## Proposed action_items.txt changes
   <mark-as-DONE / new-item text, or "none">

   ## Draft commit message
   <in this repo's existing style — see recent `git log`>

   ## Files touched this session
   <from `git status` / `git diff --stat` — so a future session doesn't
    have to re-derive it>

   ## Staleness note
   <one line: what would make this draft wrong or out of date — e.g.
    "invalid if gfl2/stat_ocr_fft.py's hierarchical branch changes again
    before this lands". The user judges staleness, not a future session
    automatically acting on this file.>
   ```

3. Run `python compile_gfl2.py` then `pytest tests/ -q --no-header --tb=no`
   and record the result under Context or its own line — this is a
   snapshot for the draft, not a repair step; don't fix failures here.

4. Print the draft's file path and a one-line summary. Do NOT run
   `git add`/`git commit`, and do NOT edit any tracked doc file — if you
   find yourself about to Edit `docs/known_issues.txt` etc., stop, that
   content belongs in the draft file instead.

To pick a draft back up later (same session or a future one): read it,
judge whether it's still accurate, then either fold its proposed entries
into the real docs yourself and run `/land`, or delete the draft file if
it's gone stale. Nothing here is ever applied automatically.
