# Unit — Functional Spec

`build/unit.html` / `build/js/unit.js` / `build/css/unit.css`

## Purpose

Read-only roster table of every doll in `DOLL_MASTER`, showing each owner's (GM/IB/FB)
progression on that doll — vertebra level, helix rank, and signature weapon rank — side
by side, with filtering by movement range, affinity, class, and weapon type.

## Data sources

- `data/master_doll.js` — `DOLL_MASTER` (one row per doll: move, rarity, affinity
  key(s), class emoji, weapon emoji, name), plus the `AFFINITY` / `CLASS` / `WEAPON`
  emoji→name legend arrays. Affinity (index 2) is normally a single emoji string, but
  **may be an array of emoji** for a doll with more than one affinity — e.g. Soppo
  (`["❄","🔥"]`, Feral Form switches its damage type from Freeze to Burn) or OTs-14
  (`["☕","❄","💧","🔥","⚡"]`, its "Resonance" damage type adapts to any element except
  Physical).
- `data/data_doll.js` — `DOLL_DATA`, keyed by doll name, holding `{ owner: [vertebra,
  rank, sig] }` triples. An owner key absent for a doll means that owner does not own it.

This page is **read-only**: it has no save button and does not write back to `data_doll.js`.

## Functional requirements

1. **FR-1 — Build the table on load.** On `DOMContentLoaded`, join `DOLL_MASTER` with
   `DOLL_DATA` (`dollMasterToUnits`) and render one row per doll (`renderUnitsTable`)
   into `#mainDiv`, replacing its placeholder content.
2. **FR-2 — Columns.** Each row shows, in order: Move, Name, Rarity, then for each of
   GM/IB/FB: Vertebra (V), Helix rank (H), Signature rank (R); then Affinity (☯), Class,
   Weapon (⚔).
3. **FR-3 — Missing ownership.** If a doll has no entry for a given owner in `DOLL_DATA`
   (or no entry at all), that owner's V/H/R cells render as `-`.
4. **FR-4 — HTML-escape cell content.** All rendered cell text is escaped (`&`, `<`, `>`)
   before insertion.
5. **FR-5 — Multi-value cells.** Move, Affinity, Class, and Weapon are "filterable"
   columns. Each such cell's underlying value(s) — a scalar for Move/Class/Weapon, or an
   array for a multi-affinity doll — are cached verbatim as a JSON `data-values`
   attribute on the `<td>`; the visible text simply concatenates the value(s) (e.g. a
   dual-affinity doll's Affinity cell shows `❄🔥` with no separator). Filtering and
   filter-button generation read `data-values`, not the rendered text, so a
   multi-affinity doll is discoverable under either of its emoji.
6. **FR-6 — Dynamic filter buttons.** After render, build one filter-button group each
   for Move, Affinity, Class, and Weapon by scanning every rendered row's `data-values`
   for that column's distinct values (not a fixed static list). Move buttons sort
   numerically; Affinity/Class/Weapon buttons sort by their emoji's code point (`Array.
   prototype.sort()` default) with a locale-compare tiebreak. Each button's tooltip shows
   the human-readable name from the legend (Move has no legend entry, so its tooltip
   falls back to the raw number).
7. **FR-7 — Filter semantics.** Within a filter group (e.g. Affinity), multiple selected
   values are OR'd — a row matches if *any* of its values (its full `data-values` list)
   contains any selected value. This means a dual-affinity doll matches if *either* of its
   affinities is selected. Across groups (Move vs Affinity vs Class vs Weapon), the row
   must match *every* group that has an active selection (AND). A group with nothing
   selected passes all rows.
8. **FR-8 — "Hide dash" toggles.** Three additional toggle buttons — GM, IB, FB — each
   hide rows where that owner's Vertebra column equals `-` (i.e. hide dolls that owner
   doesn't have leveled). These combine with AND against the Move/Affinity/Class/Weapon
   filters above.
9. **FR-9 — Clear button.** A "Clear" control resets every active filter (Move/Affinity/
   Class/Weapon filters and hide-dash toggles) and removes the `active` class from all
   filter buttons, then re-renders the full row set.
10. **FR-10 — Live row counter.** `#rowCount` always shows `<visible> / <total>` and
    updates on every filter change.
11. **FR-11 — Hiding, not removing.** Filtering only toggles a `hidden` CSS class on
    non-matching `<tr>` elements; it does not remove or re-fetch rows.

## Acceptance criteria

- **AC-1.** Loading `unit.html` replaces the `#mainDiv` placeholder with a table
  containing exactly one row per `DOLL_MASTER` entry, and `#rowCount` reads `<N> / <N>`
  (N = `DOLL_MASTER.length`) before any filter is applied.
- **AC-2.** For a doll/owner pair absent from `DOLL_DATA`, that owner's V/H/R cells in
  the doll's row all read `-`.
- **AC-3.** Soppo's Affinity cell text contains both `❄` and `🔥`; OTs-14's Affinity cell
  text contains all of `☕`, `❄`, `💧`, `🔥`, `⚡` and does not contain `🦾`.
- **AC-4.** The Affinity filter-button group contains one button per distinct emoji seen
  across all rows' Affinity `data-values` — i.e. Soppo and OTs-14 contribute their emoji
  individually, not as one combined multi-character button.
- **AC-5.** Selecting the `🔥` Affinity filter button shows a row set that includes Soppo
  (dual Freeze/Burn) — a doll never shows only because it is a *single*-affinity Burn
  doll's row is hidden.
- **AC-6.** The Move filter-button group's buttons read in ascending numeric order (e.g.
  `4, 5, 6, 7, 8, 9`), not lexicographic order.
- **AC-7.** Selecting a Move filter value `N` hides every row whose Move column is not
  `N`, and updates `#rowCount` to `<matching count> / <total>`.
- **AC-8.** Selecting two values within the same filter group (e.g. Move `4` and `9`)
  shows rows matching *either* value (OR); combining a Move selection with an Affinity
  selection shows only rows matching both (AND).
- **AC-9.** Toggling a hide-dash button (GM/IB/FB) hides rows where that owner's
  Vertebra cell is `-`, while combining correctly (AND) with any active Move/Affinity/
  Class/Weapon filter.
- **AC-10.** Clicking "Clear" removes the `active` class from every filter button,
  clears all hide-dash state, shows all rows again, and resets `#rowCount` to `<total> /
  <total>`.

## Known gaps / behavior to preserve as-is

- The placeholder text inside `<div id="mainDiv">` ("Something is wrong when u read this
  message") is expected to always be replaced by `render()` on load; if it is ever visible
  to a user, `build/js/unit.js` failed to execute (e.g. JS error, `master_doll.js`/`data_doll.js`
  missing or failed to load) — this is effectively the page's built-in JS-broken indicator
  and should not be treated as normal UI copy.
- `unit.js` is loaded with `defer`; the two data scripts (`master_doll.js`, `data_doll.js`)
  are loaded synchronously before it in `<head>`, so they are guaranteed to be evaluated
  first.
- This page has no `?test` fixture-swap mechanism (unlike remold/affection/task) — it
  always reads the real `data/master_doll.js` and `data/data_doll.js`.
