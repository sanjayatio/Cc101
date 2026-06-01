// Column indices (0-based) for the last 3 columns
const COL_AFFINITY = 12;
const COL_CLASS    = 13;
const COL_WEAPON   = 14;

// Active filter state: a Set of selected values per column
const activeFilters = {
  [COL_AFFINITY]: new Set(),
  [COL_CLASS]:    new Set(),
  [COL_WEAPON]:   new Set(),
};

// Column indices (0-based) for the V (vertebra) columns in each tier
const COL_V_GM = 3;
const COL_V_IB = 6;
const COL_V_FB = 9;

// Hide-dash filter state: when true, rows where that column = '-' are hidden
const hideDash = {
  [COL_V_GM]: false,
  [COL_V_IB]: false,
  [COL_V_FB]: false,
};

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

  document.getElementById('rowCount').textContent =
    `${visibleCount} / ${rows.length}`;
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
  // Build emoji → name lookup from the legend arrays in master_doll.js
  const legend = Object.fromEntries(
    [...AFFINITY, ...CLASS, ...WEAPON].map(([emoji, name]) => [emoji, name])
  );

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
      btn.title = legend[value] || value;
      btn.addEventListener('click', () => toggleFilter(colIdx, value, btn));
      container.appendChild(btn);
    });
  });
}

/**
 * Builds a lookup map from DOLL_DATA: { dollName: { GM: {v,rank,sig}, IB: ..., FB: ... } }
 * Missing entries (owner doesn't own that doll) default to {v:'-', rank:'-', sig:'-'}.
 */
function buildDollDataMap() {
  const map = {};
  for (const d of DOLL_MASTER) {
    map[d[5]] = {
      GM: { v: '-', rank: '-', sig: '-' },
      IB: { v: '-', rank: '-', sig: '-' },
      FB: { v: '-', rank: '-', sig: '-' },
    };
  }
  for (const [doll, owners] of Object.entries(DOLL_DATA)) {
    if (map[doll]) {
      for (const [owner, [v, rank, sig]] of Object.entries(owners)) {
        map[doll][owner] = { v, rank, sig };
      }
    }
  }
  return map;
}

/**
 * Maps DOLL_MASTER records into the unit object shape expected by renderUnitsTable(),
 * joining owner data from DOLL_DATA.
 *
 * @param {Array<Object>} dolls - DOLL_MASTER array
 * @returns {Array<Object>} unit records
 */
function dollMasterToUnits(dolls) {
  const ownerData = buildDollDataMap();
  return dolls.map(d => {
    const own = ownerData[d[5]];
    return {
      move:      d[0],
      name:      d[5],
      rarity:    d[1],
      vertebra1: own.GM.v,
      helix1:    own.GM.rank,
      sig1:      own.GM.sig,
      vertebra2: own.IB.v,
      helix2:    own.IB.rank,
      sig2:      own.IB.sig,
      vertebra3: own.FB.v,
      helix3:    own.FB.rank,
      sig3:      own.FB.sig,
      element:   d[2],
      class:     d[3],
      weapon:    d[4],
    };
  });
}

/**
 * Renders an array of unit objects into an HTML table string.
 *
 * @param {Array<Object>} units - Output of dollMasterToUnits()
 * @returns {string} HTML string for the table
 */
function renderUnitsTable(units) {
  const COLUMNS = [
    { key: 'move',      label: 'Move'   },
    { key: 'name',      label: 'Name'   },
    { key: 'rarity',    label: 'Rarity' },
    { key: 'vertebra1', label: 'V GM'   },
    { key: 'helix1',    label: 'H GM'   },
    { key: 'sig1',      label: 'R GM'   },
    { key: 'vertebra2', label: 'V IB'   },
    { key: 'helix2',    label: 'H IB'   },
    { key: 'sig2',      label: 'R IB'   },
    { key: 'vertebra3', label: 'V FB'   },
    { key: 'helix3',    label: 'H FB'   },
    { key: 'sig3',      label: 'R FB'   },
    { key: 'element',   label: '☯'     },
    { key: 'class',     label: 'Class'  },
    { key: 'weapon',    label: '⚔'     },
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

function render() {
  const html = renderUnitsTable(dollMasterToUnits(DOLL_MASTER));
  document.getElementById('mainDiv').innerHTML = html;
  buildFilterButtons();
  filterTable();
}

document.addEventListener('DOMContentLoaded', render);
