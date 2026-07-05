# Land this work: update docs, then propose a commit for gfl2_py

1. Infer what changed this session from the conversation (code, exploration
   results, design decisions, resolved/opened issues).
2. Update whichever of these are relevant (never delete history — add or
   amend entries instead):
   - `docs/known_issues.txt` — add/update issues. Tag each with
     `SCOPE: MAIN` (shipped, selectable pipeline), `SCOPE: EXPLORE`
     (gfl2/stat_ocr_fft.py or debugs/*.py only), or `SCOPE: MIXED`
     (spans both — say which part is which), per the file's own SCOPE KEY.
   - `reference.txt` §6 open issues summary — keep in sync with
     known_issues.txt; prefix each line `[MAIN]` or `[EXPLORE]` to match.
   - `docs/decisions.txt` — new numbered entry per significant design decision.
   - `docs/takeaways.txt` — new numbered entry per generalizable lesson.
   - `docs/action_items.txt` — mark items DONE, or file new follow-ups.
   - `docs/technical_design.txt` — new modules or changed responsibilities.
3. Run `python compile_gfl2.py` then `pytest tests/ -q --no-header --tb=short`.
   Fix or report any failure before continuing.
4. Run `git status` and `git diff` to see everything that would be staged.
   Draft a commit message (1-2 sentences, why not just what) in this
   repo's existing style.
5. Show the user the exact files you'd `git add` and the exact commit
   message, then STOP and ask for explicit approval. Do not run
   `git add`/`git commit` until they say yes — invoking this skill
   authorizes drafting the commit, not making it.
