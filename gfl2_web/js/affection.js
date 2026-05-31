// ── state ──────────────────────────────────────────────────────────────────
const ALL_OWNERS   = ['GM','IB','FB'];
const AFFIL_ORDER  = AFFILIATIONS.map(a => a[0]);

// In-memory ownership map, initialised from RAW_OWNERSHIP
let ownershipMap = buildOwnershipMap();
let hasUnsaved = false;

function buildOwnershipMap() {
  const map = {};
  for (const [doll, owner, level] of RAW_OWNERSHIP) {
    if (!map[doll]) map[doll] = {};
    map[doll][owner] = level;
  }
  return map;
}

function loadData() {
  return ownershipMap;
}

function recordOverride(doll, owner, level) {
  if (!ownershipMap[doll]) ownershipMap[doll] = {};
  ownershipMap[doll][owner] = level;
  markUnsaved();
}

// ── save ───────────────────────────────────────────────────────────────────
function buildDataFileContent() {
  // Reconstruct RAW_OWNERSHIP from current ownershipMap, preserving original row order
  // then appending any new [doll, owner] pairs not in the original.
  const seen = new Set();
  const merged = RAW_OWNERSHIP.map(([doll, owner]) => {
    seen.add(`${doll}\0${owner}`);
    return [doll, owner, ownershipMap[doll]?.[owner] ?? 0];
  });
  // Append new entries (doll+owner combos added at runtime, not in original data)
  for (const doll of Object.keys(ownershipMap)) {
    for (const owner of Object.keys(ownershipMap[doll])) {
      if (!seen.has(`${doll}\0${owner}`)) {
        merged.push([doll, owner, ownershipMap[doll][owner]]);
      }
    }
  }

  return `// [doll, owner, affection_level]
// Omitting an entry means that owner doesn't have that doll.
const RAW_OWNERSHIP = [
${merged.map(r => '  ' + JSON.stringify(r) + ',').join('\n')}
];
`;
}

async function saveDataFile() {
  const content = buildDataFileContent();
  if (window.showSaveFilePicker) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: 'data_affection.js',
        types: [{ description: 'JavaScript file', accept: { 'text/javascript': ['.js'] } }],
      });
      const writable = await handle.createWritable();
      await writable.write(content);
      await writable.close();
      markSaved();
      return;
    } catch (e) {
      if (e.name === 'AbortError') return;
    }
  }
  // Fallback: download
  const blob = new Blob([content], { type: 'text/javascript' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'data/data_affection.js';
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  markSaved();
}

function markUnsaved() {
  hasUnsaved = true;
  const btn = document.getElementById('save-btn');
  btn.classList.add('unsaved'); btn.classList.remove('saved');
  document.getElementById('save-status').textContent = 'Unsaved changes';
}

function markSaved() {
  hasUnsaved = false;
  const btn = document.getElementById('save-btn');
  btn.classList.remove('unsaved'); btn.classList.add('saved');
  document.getElementById('save-status').textContent = 'Saved ✓';
  setTimeout(() => { document.getElementById('save-status').textContent = ''; }, 3000);
}

// ── render ─────────────────────────────────────────────────────────────────
let activeOwners   = new Set(ALL_OWNERS);
let affiliFilter   = '';
let affectionFilter = -1;

function renderTable() {
  const ownershipData = loadData();
  const visibleOwners = ALL_OWNERS.filter(o => activeOwners.has(o));
  const thead = document.getElementById('table-head');
  const tbody = document.getElementById('table-body');

  // header
  thead.innerHTML = '';
  const hr = document.createElement('tr');
  ['Affiliation','Doll'].forEach(h => {
    const th = document.createElement('th'); th.textContent = h; hr.appendChild(th);
  });
  visibleOwners.forEach(o => {
    const th = document.createElement('th');
    th.textContent = o; th.className = 'owner-col'; hr.appendChild(th);
  });
  thead.appendChild(hr);

  // rows
  tbody.innerHTML = '';
  for (const [doll, affil] of DOLL_AFFIL) {
    if (affiliFilter && affil !== affiliFilter) continue;
    if (affectionFilter >= 0) {
      const ownerMap = ownershipData[doll] || {};
      const ok = visibleOwners.some(o => {
        if (!(o in ownerMap)) return false;
        const lvl = ownerMap[o];
        return affectionFilter === 4 ? lvl === 4 : lvl >= affectionFilter;
      });
      if (!ok) continue;
    }

    const tr = document.createElement('tr');
    const tdA = document.createElement('td'); tdA.className = 'affiliation'; tdA.textContent = affil;
    const tdD = document.createElement('td'); tdD.className = 'doll-name';   tdD.textContent = doll;
    tr.appendChild(tdA); tr.appendChild(tdD);

    const ownerMap = ownershipData[doll] || {};
    visibleOwners.forEach(owner => {
      const td = document.createElement('td');
      td.className = 'owner-cell';
      if (!(owner in ownerMap)) {
        td.classList.add('not-owned'); td.textContent = '—';
      } else {
        const lvl = ownerMap[owner];
        td.classList.add('owned', `affection-${lvl}`);
        td.innerHTML = `<div class="affection-display">
          <span>${lvl}</span>
          <div class="affection-dots">
            ${[0,1,2,3].map(i=>`<div class="dot${i<lvl?' filled':''}"></div>`).join('')}
          </div>
        </div>`;
        td.addEventListener('click', e => openPopover(e, td, doll, owner, lvl));
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  }

  document.getElementById('rowCount').textContent =
    `${tbody.rows.length} / ${DOLL_AFFIL.length}`;
}

// ── popover ────────────────────────────────────────────────────────────────
let currentPopover = null;

function closePopover() {
  if (currentPopover) { currentPopover.remove(); currentPopover = null; }
}

function openPopover(e, td, doll, owner, currentLevel) {
  e.stopPropagation();
  closePopover();
  const pop = document.createElement('div');
  pop.className = 'popover';
  pop.innerHTML = `<label>Affection — <strong>${doll}</strong> / ${owner}</label>
    <div class="popover-options">${[0,1,2,3,4].map(i =>
      `<div class="popt${i===currentLevel?' selected':''}" data-val="${i}">${i}</div>`
    ).join('')}</div>`;
  pop.querySelectorAll('.popt').forEach(btn => {
    btn.addEventListener('click', ev => {
      ev.stopPropagation();
      recordOverride(doll, owner, parseInt(btn.dataset.val));
      closePopover();
      renderTable();
    });
  });
  const rect = td.getBoundingClientRect();
  pop.style.top  = (rect.bottom + 4) + 'px';
  pop.style.left = Math.max(4, rect.left - 20) + 'px';
  document.body.appendChild(pop);
  currentPopover = pop;
}

document.addEventListener('click', closePopover);

// ── controls setup ─────────────────────────────────────────────────────────
const sel = document.getElementById('affil-filter');
sel.innerHTML = '<option value="">All affiliations</option>';
AFFIL_ORDER.forEach(a => {
  const opt = document.createElement('option');
  opt.value = a; opt.textContent = a; sel.appendChild(opt);
});
sel.addEventListener('change', () => { affiliFilter = sel.value; renderTable(); });

const ownerCont = document.getElementById('owner-buttons');
ownerCont.style.cssText = 'display:flex;gap:6px';
ALL_OWNERS.forEach(o => {
  const btn = document.createElement('button');
  btn.className = 'owner-btn active';
  btn.textContent = o;
  btn.addEventListener('click', () => {
    if (activeOwners.has(o)) {
      if (activeOwners.size === 1) return;
      activeOwners.delete(o); btn.classList.remove('active');
    } else {
      activeOwners.add(o); btn.classList.add('active');
    }
    renderTable();
  });
  ownerCont.appendChild(btn);
});

document.getElementById('affection-filter').addEventListener('change', function() {
  affectionFilter = parseInt(this.value); renderTable();
});

renderTable();
