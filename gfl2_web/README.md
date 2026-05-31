# GFL2 Web

A static single-page app for tracking Girls Frontline 2 doll data across three owners: **GM**, **IB**, and **FB**.

## Structure

```
index.html          # Shell layout with sidebar nav and iframe content area
affection.html      # Affection module
remold.html         # Remold module
unit.html           # Unit module
css/
  _base.css         # Shared base styles
  index.css         # Shell/sidebar styles
  affection.css
  remold.css
  unit.css
js/
  affection.js      # Affection module logic
  remold.js         # Remold module logic
  unit.js           # Unit module logic
data/
  master_doll.js    # Static doll definitions (name, rarity, move, element, class, weapon)
  master_affection.js  # Affiliations and doll→affiliation mapping
  master_remold.js  # Remold pattern definitions (main/sub color categories)
  data_affection.js # Per-owner affection levels (editable, saveable)
  data_doll.js      # Per-owner doll data: vertebra, helix rank, signature weapon
  data_remold.js    # Per-owner remold slot assignments (editable, saveable)
```

## Modules

### Unit (`unit.html`)
Table of all dolls with per-owner columns for vertebra level (V), helix rank (H), and signature weapon (R). Filterable by affinity, class, and weapon type. Owner columns show `–` when a doll isn't owned.

### Remold (`remold.html`)
Table of remold slots per owner, each with a tier, assigned doll, main pattern, and sub pattern. The doll assignment is editable inline via a dropdown. Changes can be saved back to `data_remold.js` via the File System Access API (or downloaded as a fallback).

### Affection (`affection.html`)
Table of doll affection levels (0–4) per owner, grouped by affiliation. Cells are clickable to update the level via a popover. Filterable by affiliation and minimum affection level. Changes can be saved back to `data_affection.js`.

## Data files

`master_*.js` files are static reference data. `data_*.js` files hold mutable per-owner state and are the files you replace when saving edits from the UI.
