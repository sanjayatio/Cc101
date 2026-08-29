// ── filter state ──────────────────────────────────────────────────────────
// Each set holds the emoji values currently selected for that dimension.
const activeFilters = {
  affinity: new Set(),
  class:    new Set(),
  weapon:   new Set(),
};

// Build a lookup from doll name → DOLL_MASTER row for quick filter access.
// Only include dolls that have an entry in DOLL_INFO.
const masterByName = {};
for (const row of DOLL_MASTER) {
  const name = row[5];
  if (name in DOLL_INFO) masterByName[name] = row;
}

// ── filter buttons ────────────────────────────────────────────────────────

function buildFilterButtons() {
  const legend = Object.fromEntries(
    [...AFFINITY, ...CLASS, ...WEAPON].map(([emoji, name]) => [emoji, name])
  );

  const config = [
    { key: 'affinity', colIdx: 2, containerId: 'affinity-buttons' },
    { key: 'class',    colIdx: 3, containerId: 'class-buttons'    },
    { key: 'weapon',   colIdx: 4, containerId: 'weapon-buttons'   },
  ];

  for (const { key, colIdx, containerId } of config) {
    const values = new Set(Object.values(masterByName).map(row => row[colIdx]));
    const container = document.getElementById(containerId);
    [...values].sort().forEach(emoji => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn';
      btn.textContent = emoji;
      btn.title = legend[emoji] || emoji;
      btn.addEventListener('click', () => {
        if (activeFilters[key].has(emoji)) {
          activeFilters[key].delete(emoji);
          btn.classList.remove('active');
        } else {
          activeFilters[key].add(emoji);
          btn.classList.add('active');
        }
        refreshList();
      });
      container.appendChild(btn);
    });
  }
}

function clearAllFilters() {
  for (const key of ['affinity', 'class', 'weapon']) activeFilters[key].clear();
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  refreshList();
}

// ── doll list ─────────────────────────────────────────────────────────────

function filteredNames() {
  return Object.entries(masterByName)
    .filter(([, row]) => {
      const afOk = activeFilters.affinity.size === 0 || activeFilters.affinity.has(row[2]);
      const clOk = activeFilters.class.size    === 0 || activeFilters.class.has(row[3]);
      const wpOk = activeFilters.weapon.size   === 0 || activeFilters.weapon.has(row[4]);
      return afOk && clOk && wpOk;
    })
    .map(([name]) => name)
    .sort();
}

function refreshList() {
  const sel = document.getElementById('doll-select');
  const current = sel.value;
  const names = filteredNames();

  sel.innerHTML = '';
  for (const name of names) {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    sel.appendChild(opt);
  }

  // Restore previous selection if still visible, else show first.
  if (names.includes(current)) {
    sel.value = current;
  } else if (names.length > 0) {
    sel.value = names[0];
  }

  onDollChange();
}

// ── doll detail ───────────────────────────────────────────────────────────

function onDollChange() {
  const sel   = document.getElementById('doll-select');
  const name  = sel.value;
  const info  = name ? DOLL_INFO[name] : null;

  renderStats(name, info);
  renderActiveTab(info);
}

function renderStats(name, info) {
  const el = document.getElementById('doll-stats');
  if (!info) {
    el.className = 'doll-stats empty';
    el.textContent = 'Select a doll to see details.';
    return;
  }

  const tags = arr =>
    arr.map(t => `<span class="tag">${esc(t)}</span>`).join('');

  el.className = 'doll-stats';
  el.innerHTML = `
    <div class="stat-row">
      <span class="stat-label">Stability Gauge</span>
      <span class="stat-value">${esc(info.stabilityGauge)}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Movement Speed</span>
      <span class="stat-value">${esc(info.movementSpeed)}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Skill Attributes</span>
      <div class="tag-list">${tags(info.skillAttributes || [])}</div>
    </div>
    <div class="stat-row">
      <span class="stat-label">Weaknesses</span>
      <div class="tag-list">${tags(info.weaknesses || [])}</div>
    </div>
  `.trim();
}

// ── tabs ──────────────────────────────────────────────────────────────────

let activeTab = 'helix'; // default to Neural Helix (3rd tab)

function switchTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tab);
  });
  document.querySelectorAll('.tab-content').forEach(p => {
    p.classList.toggle('active', p.dataset.tab === tab);
  });

  const sel  = document.getElementById('doll-select');
  const info = sel.value ? DOLL_INFO[sel.value] : null;
  renderActiveTab(info);
}

function renderActiveTab(info) {
  if (activeTab === 'skills')    renderSkills(info);
  if (activeTab === 'vertebrae') renderVertebrae(info);
  if (activeTab === 'helix')     renderHelix(info);
}

// ── skills ────────────────────────────────────────────────────────────────

function renderSkills(info) {
  const panel = document.querySelector('.tab-content[data-tab="skills"]');
  if (!info || !info.skills || info.skills.length === 0) {
    panel.innerHTML = '<p class="no-data">No skill data available.</p>';
    return;
  }

  panel.innerHTML = info.skills.map(s => {
    const metaTags = [
      s.attribute,
      s.traits && s.traits.join(' · '),
      s.stabilityDamage != null ? `Stab ${s.stabilityDamage}` : null,
      s.cooldown         != null ? `CD ${s.cooldown}`         : null,
      s.confectanceCost  != null ? `Cost ${s.confectanceCost}` : null,
      s.range            != null ? `Range ${s.range}`         : null,
      s.effArea                  ? `Area: ${s.effArea}`       : null,
    ].filter(Boolean).map(t => `<span class="tag">${esc(t)}</span>`).join('');

    const upgrades = (s.upgrades || []).map(u => `
      <div class="upgrade-row">
        <span class="upgrade-label">${esc(u.label || u.type)}</span>${esc(u.effect || '')}
      </div>
    `).join('');

    return `
      <div class="skill-card">
        <div class="skill-name">${esc(s.name)}</div>
        <div class="skill-meta">${metaTags}</div>
        <div class="skill-desc">${esc(s.description || '')}</div>
        ${upgrades ? `<div class="skill-upgrades">${upgrades}</div>` : ''}
      </div>
    `;
  }).join('');
}

// ── vertebrae ─────────────────────────────────────────────────────────────

function renderVertebrae(info) {
  const panel = document.querySelector('.tab-content[data-tab="vertebrae"]');
  if (!info || !info.vertebraeUpgrades || info.vertebraeUpgrades.length === 0) {
    panel.innerHTML = '<p class="no-data">No vertebrae data available.</p>';
    return;
  }

  const rows = info.vertebraeUpgrades.map(v => `
    <tr>
      <td class="vert-upgrade">${esc(v.upgrade)}</td>
      <td class="vert-skill">${esc(v.skill)}</td>
      <td class="vert-level">${esc(v.level)}</td>
      <td>${esc(v.effect)}</td>
    </tr>
  `).join('');

  panel.innerHTML = `
    <table class="vert-table">
      <thead>
        <tr>
          <th>Upgrade</th><th>Skill</th><th>Lv</th><th>Effect</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

// ── neural helix ──────────────────────────────────────────────────────────

function renderHelix(info) {
  const panel = document.querySelector('.tab-content[data-tab="helix"]');
  if (!info || !info.neuralHelixKeys || info.neuralHelixKeys.length === 0) {
    panel.innerHTML = '<p class="no-data">No neural helix data available.</p>';
    return;
  }

  panel.innerHTML = info.neuralHelixKeys.map(h => `
    <div class="helix-card">
      <span class="helix-node">${esc(h.node)}</span>
      <span class="helix-desc">${esc(h.description)}</span>
    </div>
  `).join('');
}

// ── utility ───────────────────────────────────────────────────────────────

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ── init ──────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  buildFilterButtons();

  // Wire up tab buttons.
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Wire up doll select.
  document.getElementById('doll-select').addEventListener('change', onDollChange);

  // Activate default tab (helix).
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === activeTab);
  });
  document.querySelectorAll('.tab-content').forEach(p => {
    p.classList.toggle('active', p.dataset.tab === activeTab);
  });

  // Populate list and show first doll.
  refreshList();
});
