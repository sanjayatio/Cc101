# UI / Technical Guidance

Generalized conventions across `gfl2_web`'s pages, distilled from `css/_base.css` and the
per-page stylesheets/scripts. Follow these when adding a page or extending an existing
one so the app stays visually and structurally consistent.

## Page architecture

- `index.html` is the shell: a fixed sidebar (`.sidebar`, one link per module) plus an
  `<iframe name="content-frame">` that loads a module page. Sidebar links target the
  iframe by `target="content-frame"` and get an `active` class matching the iframe's
  current `src`, toggled via a small inline script (see `index.html`).
- Every module page (`affection.html`, `remold.html`, `task.html`, `unit.html`) is a
  standalone HTML document that also works when opened directly (not only inside the
  iframe): `<head>` loads `css/_base.css`, then its own `css/<page>.css`, then any
  `data/*.js` scripts it needs (as plain global-scope `<script>` tags, not modules),
  then finally `js/<page>.js` (either at the end of `<body>` or `<head defer>`).
- No build step, no bundler, no framework: plain HTML/CSS/vanilla JS, globals communicate
  between `data/*.js` and `js/*.js` (e.g. `DOLL_MASTER`, `RAW_OWNERSHIP`). Script load
  order matters — data files must be declared before the page's own script unless that
  script is `defer`red past them.

## Layout conventions (`_base.css`)

- Dark theme only, no light-mode variant: page background `#1a1a2e`, body text `#e0e0e0`,
  links `#7979ff`. `* { box-sizing: border-box; margin:0; padding:0 }` reset applies
  globally.
- `.layout` (index shell) is a `flex` row filling `100vh`; `.content` is the flexible
  remainder holding the iframe.
- Every module page follows the same top-to-bottom structure:
  1. `.controls` — a `flex-wrap` toolbar row (row counter, filter groups, save button),
     `gap: 16px`, `margin-bottom: 16px`.
  2. `.table-wrapper` — the scroll container: `overflow: auto` both axes, `max-height:
     85vh`, rounded border (`border-radius: 8px; border: 1px solid #2a2a4e`).
  3. A single `<table>` inside it with a sticky `<thead>` (`position: sticky; top: 0`).
- Reuse `_base.css` classes rather than redefining them per page: `.table-wrapper`,
  `table`/`thead th`/`tbody tr`/`td` base styles, `.row-count` + `.count-badge`,
  `.controls`, `.filter-group`, `.filter-btn`, `.save-btn` (+ `.unsaved`/`.saved`
  states), `#save-status`. Only add page-specific CSS for things `_base.css` doesn't
  cover (e.g. affection's popover, remold's color classes, unit's `#mainDiv`).

## Table conventions

- `table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }` — all data
  tables share this base size; don't override font-size ad hoc.
- Header cells: dark blue-tinted background (`#1e1e3a`), light blue text (`#a0c4ff`),
  sticky, `white-space: nowrap`.
- Body rows: subtle zebra striping (`nth-child(even)` gets `#0a0a1e`), `:hover` highlight
  (`#22223a`), 1px separators (`#2a2a3e`).
- Filtering convention: prefer toggling a `hidden` class (`display: none` via `tr.hidden`)
  over removing/re-adding DOM nodes, so row identity/edit-in-progress state survives a
  filter change. (Affection is the one exception — it fully rebuilds the tbody on every
  filter change; new pages should default to the `hidden`-class approach used by
  Remold/Unit instead.)
- Row counter convention: every filterable/browsable table shows a `#rowCount` badge
  reading `<visible> / <total>`, updated on every filter change and on initial render.
- **Multi-value filterable cells:** when a column's underlying value can be more than one
  item per row (e.g. Unit's Affinity column for a dual-affinity doll), don't rely on
  `textContent` for filter matching/button generation — render the raw value list as a
  JSON `data-values` attribute on the cell (display text can simply concatenate the
  values) and have filtering/button-building read `data-values`, then OR-match against
  it. See `build/js/unit.js`'s `renderUnitsTable`/`filterTable`/`buildFilterButtons` for the
  reference implementation.

## Controls conventions

- **Filter pill buttons** (`.filter-btn`): pill-shaped, `border-radius: 20px`, dim
  (`opacity: 0.55`) until `.active` (`opacity: 1`, white border/text). Group buttons for
  the same filter dimension inside one `.filter-group`, with a `<label>` (`color: #aaa`)
  naming the dimension.
- **Color-coded pill buttons** (`.color-btn`, used by Remold): same pill shape, but text
  color itself carries meaning — red `#ff6b6b`, blue `#74b9ff`, purple `#c57bff`, green
  `#55efc4` — with an `all` variant styled neutral gray/white. Use this pattern (rather
  than `.filter-btn`) specifically when the filter values themselves are colors/categories
  that benefit from being recognizable by color, not just by label.
- **Clear-all button**: give it the `clear-btn` modifier class on top of `.filter-btn`
  (`border-color:#444; color:#666`, turns red on hover) rather than inventing a new
  button style.
- **Save button** (`.save-btn`): green-tinted, pill-ish rounded rect. Always paired with a
  `#save-status` text span next to it. States are class-driven, not inline style:
  - default: static green.
  - `.unsaved`: yellow-green border/text + a 1.5s pulse animation (`@keyframes pulse`) —
    applied the instant any edit changes a value from what it was.
  - `.saved`: dimmer green, applied right after a successful save; `#save-status` shows
    "Saved ✓" and clears itself after 3 seconds via `setTimeout`.
  - Any page with editable cells must wire up this exact unsaved→saved lifecycle rather
    than a bespoke indicator.

## Editable-cell conventions (inline editing pattern)

Remold (doll dropdown), Task (count input) and Affection (level popover) each implement
"click a cell to edit it" — follow the same shape for new editable fields:

1. Clicking the cell swaps its rendered content for an editing control (`<select>`,
   `<input type=number>`, or a small popover anchored to the cell) scoped to just that
   cell/row — never a modal.
2. Re-clicking a cell that's already open is a no-op (guard on whether the control already
   exists).
3. Commit triggers: `change`/click-a-value, `blur`, and `Enter`. `Escape` must revert to
   the pre-edit value and then commit that reverted value (not leave the control open).
4. Only mark the page "unsaved" if the committed value actually differs from the pre-edit
   value — re-selecting/re-typing the same value must not dirty the page.
5. Validate at commit time, not at keystroke time, and silently fall back to the previous
   valid value on invalid input (see Task's count input) rather than blocking commit or
   showing an error state.

## Save-to-file convention

Every editable page implements the same save routine shape (see `build/js/affection.js`,
`build/js/remold.js`, `build/js/task.js`):

1. Serialize in-memory working state back into the exact source-literal text format of
   the original `data/*.js` file (matching constant name, comment header/JSDoc if
   present, and formatting/alignment conventions of the original).
2. Try `window.showSaveFilePicker` first (File System Access API), with `suggestedName`
   matching the real data filename and a `text/javascript`/`.js` file-type filter.
   Treat a thrown `AbortError` (user cancelled the picker) as a silent no-op — don't mark
   saved, don't show an error.
3. If `showSaveFilePicker` isn't available, fall back to a synthetic `<a download>` click
   on a `Blob` URL, then revoke the object URL after 5 seconds.
4. On success (either path), call the shared `markSaved()` pattern.

New editable pages should reuse this exact three-step shape rather than introducing a
different persistence mechanism (e.g. no `fetch`/server calls — this app has no backend).

## Data/JS conventions

- `master_*.js` files are static reference data (never edited by any page's UI).
  `data_*.js` files hold the mutable, per-owner state that pages edit and can save back
  out. Keep this naming/ownership split when adding new data files.
- Pages never mutate the original loaded constant (e.g. `RAW_OWNERSHIP`, `REMOLD_DATA`)
  in place; they copy it into a page-local working structure first (`ownershipMap`,
  `rows`, `dailyRows`/`timedRows`) and read/write/render only through that copy. This
  keeps "unsaved changes" semantics well-defined and keeps the save routine able to diff
  against a known original shape.
- Look-up/legend arrays use the `[[key, value], ...]` tuple-array shape (e.g. `AFFINITY`,
  `CLASS`, `WEAPON`, `AFFILIATIONS`) rather than plain objects, generally so order is
  preserved and can double as either a list or a map depending on use.

## Acceptance criteria (new-page compliance checklist)

A new or modified module page should satisfy all of the following before being
considered consistent with the rest of the app:

- **AC-1.** The page loads `css/_base.css` before its own `css/<page>.css`, and does not
  redefine a class `_base.css` already provides (table/thead/tbody/td, `.row-count` +
  `.count-badge`, `.controls`, `.filter-group`, `.filter-btn`, `.save-btn` + states,
  `#save-status`).
- **AC-2.** Data `<script>` tags are declared before the page's own `js/<page>.js`
  (or the page's script is `defer`red), so globals are guaranteed defined when the
  module script runs.
- **AC-3.** If the page has a browsable/filterable table, it shows a `#rowCount` badge
  reading `<visible> / <total>` that updates on every filter change, and filtering
  toggles a `hidden` class on rows rather than removing/re-adding DOM nodes (unless the
  page has a documented reason to fully rebuild, as Affection does).
  When a filterable column's cell can hold more than one value per row, the page follows
  the multi-value `data-values` convention above rather than parsing rendered text.
- **AC-4.** If the page has editable cells, it follows the click-to-edit /
  commit-on-change-blur-Enter / Escape-reverts-then-commits / dirty-only-on-actual-change
  pattern, and wires the same `.unsaved`/`.saved` Save-button lifecycle (pulsing while
  unsaved, "Saved ✓" for 3s after save) rather than a bespoke indicator.
- **AC-5.** If the page saves data, it follows the three-step save shape (serialize to
  source-literal text → `showSaveFilePicker` with a bare `suggestedName` matching the
  real data filename, `AbortError` treated as a silent no-op → `<a download>` Blob
  fallback with the same bare filename) rather than introducing a different persistence
  mechanism.
