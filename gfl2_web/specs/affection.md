# Affection — Functional Spec

`build/affection.html` / `build/js/affection.js` / `build/css/affection.css`

## Purpose

Editable matrix of doll affection levels (0–4) per owner (GM/IB/FB), grouped by
affiliation, with a click-to-edit popover, filtering, and save-back to
`data/data_affection.js`.

## Data sources

- `data/master_affection.js` — `AFFILIATIONS` (ordered list of `[name, gift]` pairs,
  defines affiliation display order via `AFFIL_ORDER`) and `DOLL_AFFIL` (affiliation →
  array of doll names, defines row order within a group).
- `data/data_affection.js` — `RAW_OWNERSHIP`: `{ doll: { owner: level } }`. An owner key
  absent for a doll means that owner does not own it. Loaded into an in-memory working
  copy (`ownershipMap`) via `buildOwnershipMap()`; all reads/writes during the session go
  through this copy, not the original constant.

## Functional requirements

1. **FR-1 — Initial render.** On load, render one row per doll, grouped and ordered by
   `DOLL_AFFIL`/`AFFIL_ORDER` (i.e. by affiliation, then by the doll's position within
   that affiliation's list). Columns: Affiliation, Doll, then one column per active owner.
2. **FR-2 — Owner columns are togglable.** All three owners (GM/IB/FB) are shown by
   default. Clicking an owner's toggle button removes/re-adds that owner's column from
   both the header and every row. At least one owner must remain active — clicking the
   last active owner's button is a no-op.
3. **FR-3 — Not-owned cells.** If a doll has no entry for a visible owner in
   `ownershipMap`, that owner's cell renders as `—` with a distinct "not-owned" style and
   is not clickable.
4. **FR-4 — Owned cell display.** If owned, the cell shows the numeric level (0–4) plus a
   4-dot indicator where `level` dots are filled; the cell's color/weight is styled per
   level (0 dim, 4 bold/highlighted). Owned cells are clickable.
5. **FR-5 — Edit via popover.** Clicking an owned cell opens a popover anchored below/near
   the cell, offering levels 0–4 as buttons with the current level pre-highlighted.
   Clicking a level: records it into `ownershipMap` for that `(doll, owner)`, marks the
   page unsaved, closes the popover, and re-renders the table (so the clicked cell — and
   the filtered row set, if a filter now excludes/includes it — reflects the new value
   immediately).
6. **FR-6 — Popover dismissal.** Only one popover is open at a time (opening a new one
   closes any existing one). Clicking anywhere outside a popover option closes it without
   changing the value.
7. **FR-7 — Affiliation filter.** A dropdown (default "All affiliations") restricts rows
   to a single affiliation when set.
8. **FR-8 — Minimum-affection filter.** A dropdown offers: Any, 0+, 1+, 2+, 3+, "4 only".
   With a threshold `N < 4` selected, a doll row is shown if *any currently visible owner*
   who owns that doll has level ≥ N. With "4 only" selected, a doll row is shown if any
   currently visible owner has exactly level 4. Owners the doll isn't owned by don't count
   toward this filter.
9. **FR-9 — Filters combine.** Affiliation filter, affection filter, and the set of active
   owner columns all apply together (a row must pass all three) when deciding row
   visibility.
10. **FR-10 — Filtering re-renders.** Unlike Remold/Unit, filtering here is implemented by
    fully rebuilding `<thead>`/`<tbody>` on every change (not by toggling a `hidden`
    class) — the effect is equivalent, but rows/cells are recreated each time.
11. **FR-11 — Live row counter.** `#rowCount` shows `<rows currently rendered> / <total
    dolls across all affiliations>` (the denominator is the full roster count, independent
    of owner-column visibility).
12. **FR-12 — Save.** Serializes `ownershipMap` back into `RAW_OWNERSHIP` object-literal
    form, preserving the original doll key order from `RAW_OWNERSHIP` first, then
    appending any dolls that exist only in the runtime map but not in the original data
    (i.e. newly-added dolls, if any were ever added programmatically) at the end. Writes
    via `window.showSaveFilePicker` (suggested filename `data_affection.js`) where
    supported, falling back to a browser download (path `data/data_affection.js`)
    otherwise. Cancelling the native picker leaves state untouched.
13. **FR-13 — Post-save state.** Same unsaved/saved indicator behavior as Remold (pulse
    while unsaved, "Saved ✓" for 3s after a successful save).

## Acceptance criteria

- **AC-1.** Loading `affection.html` renders one row per doll across all affiliations,
  grouped/ordered by `DOLL_AFFIL`/`AFFIL_ORDER`, with a column per active owner (GM/IB/FB
  all active by default); `#rowCount` reads `<N> / <N>` where N is the total doll count
  across all affiliations.
- **AC-2.** Clicking an owner's toggle button removes that owner's column from the
  header and every row; clicking it again restores it. Clicking the toggle for the last
  remaining active owner is a no-op (its column stays visible).
- **AC-3.** A doll not owned by a given visible owner renders that owner's cell as `—`
  with the not-owned style, and clicking it does not open a popover.
- **AC-4.** A doll owned by a given owner renders that owner's cell with the numeric
  level and a dot indicator with exactly `level` dots filled; clicking it opens a
  popover with levels 0–4, the current level pre-highlighted.
- **AC-5.** Clicking a level in the popover updates that `(doll, owner)`'s level, marks
  the page unsaved, closes the popover, and re-renders the table so the new level is
  visible immediately. Opening a second popover elsewhere closes the first.
- **AC-6.** Setting the Affiliation filter to a specific affiliation shows only that
  affiliation's rows; resetting to "All affiliations" restores every row.
- **AC-7.** Setting the affection-threshold filter to `N` (0–3) shows a doll row only if
  at least one currently *visible* owner who owns that doll has level ≥ N; setting it to
  "4 only" shows a doll row only if at least one visible owner has exactly level 4.
  Owners who don't own the doll never count toward this filter.
- **AC-8.** Affiliation filter, affection filter, and active-owner columns combine with
  AND — a row is visible only if it passes all three simultaneously.
- **AC-9.** Clicking Save triggers the save routine and, on success, shows "Saved ✓" and
  clears the unsaved/pulsing state.
- **AC-10.** The content produced by the save routine is valid JS that, when
  re-evaluated, yields a `RAW_OWNERSHIP` object whose keys start with every doll key from
  the original data file (in original order) and reflect any level changes made during
  the session.

## Known gaps / behavior to preserve as-is

- There is no UI path to add a brand-new doll or affiliation — FR-12's "append new dolls"
  logic exists for forward-compatibility but nothing in the current UI creates a doll key
  that isn't already in `RAW_OWNERSHIP`/`DOLL_AFFIL`.
- Save does not require `hasUnsaved` to be true.
