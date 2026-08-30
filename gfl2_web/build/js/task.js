// ── state ──────────────────────────────────────────────────────────────────
const owners = DATA_OWNER.map(([id, tag, startDate]) => ({ id, tag, startDate }));

// Working copies — deep-cloned from data
let dailyRows = DATA_TASK_DAILY.map(([name, counts]) => ({
  name,
  counts: Object.assign({}, counts),
}));
let timedRows = DATA_TASK_TIMED.map(([name, dueDate, counts]) => ({
  name,
  dueDate,
  counts: Object.assign({}, counts),
}));

let hasUnsaved = false;

// ── save ───────────────────────────────────────────────────────────────────
function buildDataFileContent() {
  const ownerLines = owners.map(o => `  [${o.id}, "${o.tag}", "${o.startDate}"]`).join(',\n');

  const dailyLines = dailyRows.map(r => {
    const inner = owners.map(o => `${o.id}:${r.counts[o.id] ?? 0}`).join(', ');
    return `  [${JSON.stringify(r.name)}, {${inner}}]`;
  }).join(',\n');

  const timedLines = timedRows.map(r => {
    const inner = owners.map(o => `${o.id}:${r.counts[o.id] ?? 0}`).join(', ');
    return `  [${JSON.stringify(r.name)}, ${JSON.stringify(r.dueDate)}, {${inner}}]`;
  }).join(',\n');

  return `/**
 * Owner definitions.
 * @type {[ownerId: number, ownerTag: string, startDate: string][]}
 */
const DATA_OWNER = [
${ownerLines},
];

/**
 * Daily task execution counts per owner.
 * @type {[taskName: string, counts: { [ownerId: number]: number }][]}
 */
const DATA_TASK_DAILY = [
${dailyLines},
];

/**
 * Timed task execution counts per owner.
 * @type {[taskName: string, dueDate: string, counts: { [ownerId: number]: number }][]}
 */
const DATA_TASK_TIMED = [
${timedLines},
];
`;
}

async function saveDataFile() {
  const content = buildDataFileContent();
  if (window.showSaveFilePicker) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: 'data_owner.js',
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
  const blob = new Blob([content], { type: 'text/javascript' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'data_owner.js';
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
function renderTable() {
  const thead = document.getElementById('table-head');
  const tbody = document.getElementById('table-body');

  // Header
  thead.innerHTML = '';
  const hr = document.createElement('tr');
  ['Task', 'Due Date', ...owners.map(o => o.tag)].forEach(h => {
    const th = document.createElement('th');
    th.textContent = h;
    hr.appendChild(th);
  });
  thead.appendChild(hr);

  tbody.innerHTML = '';

  // Section header helper
  function sectionRow(label) {
    const tr = document.createElement('tr');
    tr.className = 'section-header';
    const td = document.createElement('td');
    td.colSpan = 2 + owners.length;
    td.textContent = label;
    tr.appendChild(td);
    tbody.appendChild(tr);
  }

  // Row helper
  function dataRow(name, dueDate, countsObj, rowRef) {
    const tr = document.createElement('tr');

    const tdName = document.createElement('td');
    tdName.className = 'task-name';
    tdName.textContent = name;
    tr.appendChild(tdName);

    const tdDate = document.createElement('td');
    tdDate.className = 'due-date';
    tdDate.textContent = dueDate || '—';
    tr.appendChild(tdDate);

    owners.forEach(o => {
      const td = document.createElement('td');
      td.className = 'count-cell';
      td.textContent = countsObj[o.id] ?? 0;
      td.addEventListener('click', () => openEditor(td, o.id, rowRef));
      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  }

  sectionRow('Daily');
  dailyRows.forEach(r => dataRow(r.name, null, r.counts, r));

  sectionRow('Timed');
  timedRows.forEach(r => dataRow(r.name, r.dueDate, r.counts, r));
}

// ── inline editor ──────────────────────────────────────────────────────────
function openEditor(td, ownerId, rowRef) {
  if (td.querySelector('input')) return;
  const current = rowRef.counts[ownerId] ?? 0;

  const input = document.createElement('input');
  input.type = 'number';
  input.min = '0';
  input.value = current;
  input.className = 'count-input';

  td.textContent = '';
  td.appendChild(input);
  input.focus();
  input.select();

  function commit() {
    const val = parseInt(input.value);
    const newVal = isNaN(val) || val < 0 ? current : val;
    rowRef.counts[ownerId] = newVal;
    td.textContent = newVal;
    if (newVal !== current) markUnsaved();
  }

  input.addEventListener('blur', commit);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter')  { e.preventDefault(); input.blur(); }
    if (e.key === 'Escape') { input.value = current; input.blur(); }
  });
}

// ── init ───────────────────────────────────────────────────────────────────
renderTable();
