/**
 * Filter the table rows based on the current activeFilters state.
 * A row is shown only if it matches ALL active filter groups.
 * Within a group, any selected value is accepted (OR logic).
 * Across groups, all groups must pass (AND logic).
 */
function filterTable() {
  const rows = document.querySelectorAll('.units-table tbody tr');
  let visibleCount = 0;

  rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    const match =
      [COL_AFFINITY, COL_CLASS, COL_WEAPON].every(colIdx => {
        const selected = activeFilters[colIdx];
        if (selected.size === 0) return true; // no filter active for this column
        return selected.has(cells[colIdx].textContent.trim());
      }) &&
      [COL_V_GM, COL_V_IB, COL_V_FB].every(colIdx => {
        if (!hideDash[colIdx]) return true; // hide-dash not active for this column
        return cells[colIdx].textContent.trim() !== '-';
      });

    row.classList.toggle('hidden', !match);
    if (match) visibleCount++;
  });

  document.getElementById('no-results').style.display =
    visibleCount === 0 ? 'block' : 'none';
}

/** Toggle a value in a filter group and re-run the filter. */
function toggleFilter(colIdx, value, btn) {
  if (activeFilters[colIdx].has(value)) {
    activeFilters[colIdx].delete(value);
    btn.classList.remove('active');
  } else {
    activeFilters[colIdx].add(value);
    btn.classList.add('active');
  }
  filterTable();
}

/** Toggle a hide-dash filter for a column and re-run the filter. */
function toggleHideDash(colIdx, btn) {
  hideDash[colIdx] = !hideDash[colIdx];
  btn.classList.toggle('active', hideDash[colIdx]);
  filterTable();
}

/** Clear all active filters and reset button states. */
function clearAllFilters() {
  [COL_AFFINITY, COL_CLASS, COL_WEAPON].forEach(colIdx => {
    activeFilters[colIdx].clear();
  });
  [COL_V_GM, COL_V_IB, COL_V_FB].forEach(colIdx => {
    hideDash[colIdx] = false;
  });
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  filterTable();
}

/** Build filter buttons by reading unique values from the table. */
function buildFilterButtons() {
  const config = [
    { colIdx: COL_AFFINITY, containerId: 'affinity-buttons' },
    { colIdx: COL_CLASS,    containerId: 'class-buttons'    },
    { colIdx: COL_WEAPON,   containerId: 'weapon-buttons'   },
  ];

  config.forEach(({ colIdx, containerId }) => {
    const values = new Set();
    document.querySelectorAll('.units-table tbody tr').forEach(row => {
      const text = row.querySelectorAll('td')[colIdx].textContent.trim();
      values.add(text);
    });

    const container = document.getElementById(containerId);
    [...values].sort().forEach(value => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn';
      btn.textContent = value;
      btn.title = value;
      btn.addEventListener('click', () => toggleFilter(colIdx, value, btn));
      container.appendChild(btn);
    });
  });
}

/**
 * Parses a units.txt string into an array of unit objects.
 *
 * The file uses fixed display-width columns (each emoji counts as 2 display
 * columns, ASCII chars as 1). 
 *
 * Array.from() is used throughout so that non-BMP emoji (e.g. 💧 U+1F4A7,
 * 🔥 U+1F525) which are surrogate pairs in UTF-16 are treated as one unit,
 * matching the file's codepoint-indexed column positions.
 *
 * @param {string} text - Raw content of units.txt
 * @returns {Array<Object>} Parsed unit records
 */
function parseUnits(text) {
  const units = [];

  for (const rawLine of text.split('\n')) {
    const line = rawLine.trimEnd();
    if (!line) continue;

    // Work in Unicode codepoints (not UTF-16 code units) so surrogate-pair
    // emoji don't shift every subsequent index.
    const cp = Array.from(line);
    if (cp.length < 25) continue;

    const move         = cp[0];
    const name         = cp.slice(3, 17).join('').trim();
    const rarity       = cp[17];
    const vertebra1    = cp[20];
    const helix1       = cp[22];
    const weaponlevel1 = cp[24];
    const vertebra2    = cp[27];
    const helix2       = cp[29];
    const weaponlevel2 = cp[31];
    const vertebra3    = cp[34];
    const helix3       = cp[36];
    const weaponlevel3 = cp[38];
    const element      = cp[41];
    const cls          = cp[44];
    const weapontype   = cp[47];

    units.push({ move, name, rarity, vertebra1, helix1, weaponlevel1
	  , vertebra2, helix2, weaponlevel2, vertebra3, helix3, weaponlevel3
	  , element, class: cls, weapontype });
  }

  return units;
}

/**
 * Renders an array of unit objects (from parseUnits) into an HTML table string.
 *
 * @param {Array<Object>} units - Output of parseUnits()
 * @returns {string} HTML string for the table
 */
function renderUnitsTable(units) {
  const COLUMNS = [
    { key: 'move',         label: 'Move'   },
    { key: 'name',         label: 'Name'   },
    { key: 'rarity',       label: 'Rarity' },
    { key: 'vertebra1',    label: 'V GM'   },
    { key: 'helix1',       label: 'H GM'   },
    { key: 'weaponlevel1', label: 'R GM'   },
    { key: 'vertebra2',    label: 'V IB '  },
    { key: 'helix2',       label: 'H IB '  },
    { key: 'weaponlevel2', label: 'R IB '  },
    { key: 'vertebra3',    label: 'V FB'   },
    { key: 'helix3',       label: 'H FB'   },
    { key: 'weaponlevel3', label: 'R FB'   },
    { key: 'element',      label: '☯'     },
    { key: 'class',        label: 'Class'  },
    { key: 'weapontype',   label: '⚔'     },
  ];

  const esc = (str) =>
    String(str ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

  const headerCells = COLUMNS
    .map(({ label }) => `<th>${esc(label)}</th>`)
    .join('');

  const rows = units.map((unit) => {
    const cells = COLUMNS
      .map(({ key }) => `<td>${esc(unit[key])}</td>`)
      .join('');
    return `<tr>${cells}</tr>`;
  });

  return `
<table class="units-table">
  <thead>
    <tr>${headerCells}</tr>
  </thead>
  <tbody>
    ${rows.join('\n    ')}
  </tbody>
</table>`.trimStart();
}

/**
 * Convenience: parse raw text and return the rendered HTML table string.
 *
 * @param {string} text - Raw content of units.txt
 * @returns {string} HTML table string
 */
function unitsTextToTable(text) {
  return renderUnitsTable(parseUnits(text));
}

/**
 * Required some hacks if we want to load the source from file
 *    invoke: .\chrome.exe --allow-file-access-from-files
 * async function render() {
 *    const response = await fetch('units.txt', {mode: 'cors'});
 *    const rawText = await response.text();
 */
function render() {
   const html = unitsTextToTable(UNITS_DATA);
   document.getElementById('mainDiv').innerHTML = html;
   buildFilterButtons();
}

document.addEventListener('DOMContentLoaded', render);

// ─── Node.js usage ───────────────────────────────────────────────────────────
// (uncomment if running directly with Node)
//
// const fs = require('fs');
// const raw = fs.readFileSync('units.txt', 'utf8');
// console.log(unitsTextToTable(raw));

// Export for CommonJS / ES module environments
// if (typeof module !== 'undefined') {
//   module.exports = { parseUnits, renderUnitsTable, unitsTextToTable };
// }