# Task — Functional Spec

`build/task.html` / `build/js/task.js` / `build/css/task.css`

## Purpose

Editable table of per-owner task completion counts, split into two sections — "Daily"
(no due date) and "Timed" (has a due date) — with inline count editing and save-back to
`data/data_owner.js`.

## Data sources

`data/data_owner.js`, all consumed as-is at load then deep-copied into working state:

- `DATA_OWNER` — `[ownerId, ownerTag, startDate][]`. Defines the set and left-to-right
  order of owner columns (currently GM/IB/FB). `startDate` is loaded but not currently
  displayed anywhere on this page.
- `DATA_TASK_DAILY` — `[taskName, { ownerId: count }][]`, copied into working state
  `dailyRows`.
- `DATA_TASK_TIMED` — `[taskName, dueDate, { ownerId: count }][]`, copied into working
  state `timedRows`.
- `DATA_RESOURCES` — `[resourceName, { ownerId: count }][]`. **Present in the data file but
  not currently read or rendered by `task.js`** (see Known gaps).

## Functional requirements

1. **FR-1 — Header.** Table header is built from owner data: `Task`, `Due Date`, then one
   column per entry in `DATA_OWNER` labeled with that owner's tag.
2. **FR-2 — Section grouping.** Body renders a "Daily" section header row (full-width
   label, uppercase styling) followed by all `dailyRows`, then a "Timed" section header
   row followed by all `timedRows`. Section order and row order within each section match
   the source arrays.
3. **FR-3 — Row content.** Each data row shows the task name, its due date (Timed rows) or
   `—` (Daily rows, which have no due date), and one count cell per owner. A count
   defaults to `0` if that owner has no entry for that task.
4. **FR-4 — Inline count editing.** Clicking a count cell replaces it with a `number`
   input (min 0) pre-filled with the current value and focused/selected. Only one editor
   opens per cell at a time (re-click while open is a no-op).
5. **FR-5 — Commit rules.** `Enter` or losing focus (`blur`) commits the value. `Escape`
   resets the input to the pre-edit value, then blurs (commits that original value). An
   invalid or negative entry (`NaN` or `< 0`) is rejected and the pre-edit value is kept
   instead.
6. **FR-6 — Unsaved-state tracking.** Committing marks the page "unsaved" only if the
   final committed value differs from the value before the edit opened.
7. **FR-7 — Save.** Serializes `owners` (from `DATA_OWNER`, unchanged), `dailyRows`, and
   `timedRows` back into the original three `const` declarations (with their original
   JSDoc-style comments) as the full new contents of `data_owner.js`. Writes via
   `window.showSaveFilePicker` (suggested filename `data_owner.js`) where supported,
   falling back to a browser download (filename `data_owner.js`) otherwise. Cancelling the
   native picker leaves state untouched.
8. **FR-8 — Post-save state.** Same unsaved/saved indicator behavior as Remold/Affection.

## Acceptance criteria

- **AC-1.** Loading `task.html` renders a header row of `Task`, `Due Date`, then one
  column per `DATA_OWNER` entry (labeled by tag), followed by a "Daily" section header,
  every `dailyRows` entry, a "Timed" section header, then every `timedRows` entry — in
  each case in the same order as the source arrays.
- **AC-2.** A Daily row's due-date cell reads `—`; a Timed row's due-date cell shows its
  `dueDate` value. A count cell for an owner with no entry for that task reads `0`.
- **AC-3.** Clicking a count cell opens a focused, pre-filled `number` input; clicking
  the same cell again while the input is open does not open a second input.
- **AC-4.** Committing a valid non-negative number via `Enter` or `blur` updates the
  cell and, only if the value differs from before the edit, marks the page unsaved.
- **AC-5.** Entering an invalid value (empty/non-numeric or negative) and committing
  keeps the pre-edit value and does not mark the page unsaved.
- **AC-6.** Pressing `Escape` while editing reverts the input to the pre-edit value and
  commits that reverted value (no dirty state, editor closes).
- **AC-7.** Clicking Save triggers the save routine and, on success, shows "Saved ✓" and
  clears the unsaved/pulsing state.
- **AC-8.** The content produced by the save routine is valid JS that, when
  re-evaluated, yields `DATA_OWNER`, `DATA_TASK_DAILY`, and `DATA_TASK_TIMED` with the
  same lengths and values as current working state, including any count edits made
  during the session — and does **not** re-emit a `DATA_RESOURCES` declaration (per the
  known data-loss gap below).

## Known gaps / behavior to preserve as-is

- **`DATA_RESOURCES` is not rendered.** The data file defines a resources table (Tickets,
  Collapse Pieces, Dorittos per owner) that this page loads no reference to at all —
  there is no third section, no UI for it, and saving from this page does **not**
  preserve it (`buildDataFileContent()` only re-emits `DATA_OWNER`, `DATA_TASK_DAILY`,
  `DATA_TASK_TIMED`). **Saving from the Task page today will silently drop any
  `DATA_RESOURCES` content from `data_owner.js`.** Treat this as a known data-loss risk,
  not an intentional omission, when working on this page.
- There is no filtering or search on this page (unlike Unit/Remold/Affection).
- There is no UI to add/remove a task row or an owner — only existing counts are editable.
