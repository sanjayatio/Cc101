# Remold — Functional Spec

`build/remold.html` / `build/js/remold.js` / `build/css/remold.css`

## Purpose

Editable table of "remold" slots. Each slot belongs to one owner (GM/IB/FB) and a tier
(e.g. F3/F4), has a main pattern and sub pattern (each pattern implies a color), and can
optionally have a doll assigned to it. Supports filtering and inline editing of the doll
assignment, with changes savable back to `data/data_remold.js`.

## Data sources

- `data/master_remold.js` — `REMOLD_MASTER.mainColors` / `.subColors`: color → list of
  pattern names. Inverted at load time into pattern → color lookups (`mainColors`,
  `subColors` in `remold.js`).
- `data/master_doll.js` — `DOLL_MASTER`, used only to build the sorted list of assignable
  doll names (`dollNames`), prefixed with `"__"` (meaning "no doll assigned").
- `data/data_remold.js` — `REMOLD_DATA`: object grouped by owner then tier
  (`{ [owner]: { [tier]: [doll, main, sub][] } }`). Flattened at load time, in
  iteration order (owner, then tier, then array order), into an in-memory working
  copy (`rows`) of `{ owner, tier, doll, main, sub }` objects; this working copy is
  what's rendered, filtered, edited, and saved.

## Functional requirements

1. **FR-1 — Initial render.** On load, render one table row per entry in `REMOLD_DATA`,
   in file order, with columns: Usr (owner), Tier, Doll, Main (pattern), Sub (pattern).
2. **FR-2 — Color coding.** The Main and Sub cells get a CSS class (`red`/`blue`/`purple`/
   `green`) resolved by looking up the pattern name in the inverted `mainColors`/
   `subColors` maps; an unrecognized pattern gets no color class (`unset`).
3. **FR-3 — Empty doll display.** A row whose doll is `"__"` renders the Doll cell with an
   `empty` style (dim/italic) instead of a doll name.
4. **FR-4 — Inline doll editing.** Clicking a Doll cell replaces it with a `<select>`
   populated from `dollNames` (which always includes `"__"` as the first/"none" option),
   pre-selected to the row's current doll. The cell only opens one editor at a time
   (re-clicking while already open is a no-op).
5. **FR-5 — Commit rules for the doll editor.** The edit commits (updates `rows[idx].doll`
   and re-renders the cell as static text) on: `change` (option selected), `blur`
   (clicking away), or `Enter`. `Escape` reverts the select to the value it had when
   opened, then commits that original value — i.e. Escape is a cancel, not a no-op discard
   of the edit UI only.
6. **FR-6 — Unsaved-state tracking.** Committing a doll edit marks the page "unsaved"
   (pulses the Save button, shows "Unsaved changes") only if the committed value differs
   from what it was before the edit opened. Selecting the same doll again does not mark
   unsaved.
7. **FR-7 — Owner filter.** Buttons All/GM/IB/FB filter rows by `owner`; exactly one is
   active at a time (default: All).
8. **FR-8 — Tier filter.** A filter row with an `All` button plus one button per distinct
   `tier` value present in `rows` (built dynamically at load time, sorted descending, e.g.
   F4 before F3) filters rows by `tier`. Exactly one button is active at a time (default:
   All).
9. **FR-9 — Main/Sub color filters.** Two independent filter rows (Main, Sub), each with
   buttons All/Red/Blue/Purple/Green, filter rows by the row's resolved main-color or
   sub-color class respectively. Each group has exactly one active button at a time
   (default: All). All four filter groups (owner, tier, main color, sub color) combine
   with AND.
10. **FR-10 — Filtering is non-destructive.** Filtering toggles a `hidden` class on rows;
    it never removes rows or affects the underlying `rows` array or doll-edit state.
11. **FR-11 — Live row counter.** `#rowCount` shows `<visible> / <total rows>` and updates
    whenever a filter button is clicked.
12. **FR-12 — Save.** The Save button serializes the current `rows` array back into
    `REMOLD_DATA`'s owner→tier→`[doll, main, sub]` grouped form, column-aligned/padded
    for readability, wrapped in a `const REMOLD_DATA = {...}` declaration with a leading
    comment describing the shape. It writes this via
    `window.showSaveFilePicker` (suggested filename `data_remold.js`) where supported,
    falling back to a browser download (filename `data_remold.js`) otherwise. Cancelling
    the native save picker (`AbortError`) leaves state untouched (no "saved" mark).
    Save is available regardless of whether any edit was actually made.
13. **FR-13 — Post-save state.** After a successful save (or fallback download trigger),
    mark the page "saved" (removes pulse/unsaved styling, briefly shows "Saved ✓" for 3s
    then clears the status text).

## Acceptance criteria

- **AC-1.** Loading `remold.html` renders one `<tr>` per `REMOLD_DATA` entry, in the same
  order as the source array, with Usr/Tier/Doll/Main/Sub columns populated from that row.
- **AC-2.** A row whose Main (or Sub) pattern name appears in `REMOLD_MASTER.mainColors`
  (or `.subColors`) gets the corresponding `red`/`blue`/`purple`/`green` class on that
  cell; a pattern name not found in either map gets no color class.
- **AC-3.** A row with `doll === "__"` renders its Doll cell with the `empty` style
  instead of a doll name.
- **AC-4.** Clicking a Doll cell opens a `<select>` pre-selected to that row's current
  doll, offering `"__"` plus every `DOLL_MASTER` name sorted alphabetically; clicking the
  same cell again while the select is open does not open a second select.
- **AC-5.** Choosing a different doll in the select and triggering `change`, `blur`, or
  `Enter` updates the row's doll value, re-renders the cell as static text, and marks the
  page unsaved; re-selecting the *same* doll does not mark it unsaved.
- **AC-6.** Opening the editor then pressing `Escape` leaves the row's doll value
  unchanged and does not mark the page unsaved.
- **AC-7.** With the Usr filter set to `GM` (or `IB`/`FB`), only rows with that `owner`
  are visible; `All` shows every row. Only one Usr filter button is active at a time.
- **AC-8.** With the Tier filter set to a specific tier (e.g. `F4`), only rows with that
  `tier` are visible; `All` shows every row regardless of tier. Only one Tier filter
  button is active at a time, and the set of Tier buttons matches the distinct tiers
  present in `REMOLD_DATA`.
- **AC-9.** Setting the Main color filter to e.g. `Red` combined with the Sub color
  filter set to `Blue` shows only rows matching *both* (AND); `#rowCount` reflects the
  visible count. Combining a Tier filter with owner/color filters narrows by all of them
  together (AND).
- **AC-10.** Clicking Save (with or without any edits made) triggers the save routine and,
  on completion, shows "Saved ✓" and removes the unsaved/pulsing state from the Save
  button.
- **AC-11.** The content produced by the save routine is valid JS that, when
  re-evaluated, yields a `REMOLD_DATA` object with the same total row count (summed
  across all owner/tier groups) and the same `[doll, main, sub]` values as the current
  in-memory `rows` (round-trip fidelity), including any doll reassignment made during
  the session.

## Known gaps / behavior to preserve as-is

- Save does not require `hasUnsaved` to be true — clicking Save with no changes still
  produces/downloads a file and shows "Saved ✓".
- There is no way to change `owner`, `tier`, `main`, or `sub` from the UI — only the
  `doll` field is editable. Adding/removing rows is also not supported from the UI.
