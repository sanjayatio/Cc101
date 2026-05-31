// ── state ──────────────────────────────────────────────────────────────────
// Data is injected by master_remold.js, master_doll.js, data_remold.js
let rows      = REMOLD_DATA.map(r => Object.assign({}, r)); // mutable working copy
let mainColors = REMOLD_MASTER.mainColors;
let subColors  = REMOLD_MASTER.subColors;
let dollNames  = ["__", ...DOLL_MASTER.map(d => d.name).sort()];
let hasUnsaved = false;

const activeFilter = { usr: "all", main: "all", sub: "all" };
const tbody = document.getElementById("tableBody");

// ── save ───────────────────────────────────────────────────────────────────
async function saveDataFile() {
  const content = "const REMOLD_DATA = " + JSON.stringify(rows, null, 2) + ";";
  if (window.showSaveFilePicker) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: "data_remold.js",
        types: [{ description: "JavaScript file", accept: { "text/javascript": [".js"] } }],
      });
      const writable = await handle.createWritable();
      await writable.write(content);
      await writable.close();
    } catch (e) {
      if (e.name === "AbortError") return;
    }
  } else {
    const blob = new Blob([content], { type: "text/javascript" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "data_remold.js";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  }
  markSaved();
}

function markUnsaved() {
  hasUnsaved = true;
  const btn = document.getElementById("save-btn");
  btn.classList.add("unsaved"); btn.classList.remove("saved");
  document.getElementById("save-status").textContent = "Unsaved changes";
}

function markSaved() {
  hasUnsaved = false;
  const btn = document.getElementById("save-btn");
  btn.classList.remove("unsaved"); btn.classList.add("saved");
  document.getElementById("save-status").textContent = "Saved ✓";
  setTimeout(() => { document.getElementById("save-status").textContent = ""; }, 3000);
}

// ── render ─────────────────────────────────────────────────────────────────
function renderTable() {
  tbody.innerHTML = "";
  rows.forEach((row, idx) => {
    const mc = mainColors[row.main] || "unset";
    const sc = subColors[row.sub]  || "unset";
    const tr = document.createElement("tr");
    tr.dataset.usr       = row.owner;
    tr.dataset.mainColor = mc;
    tr.dataset.subColor  = sc;
    tr.dataset.idx       = idx;

    const dollClass = row.doll === "__" ? "doll empty" : "doll";

    tr.innerHTML = `
      <td class="user">${row.owner}</td>
      <td class="tier">${row.tier}</td>
      <td class="${dollClass}" data-idx="${idx}">${row.doll}</td>
      <td class="${mc}">${row.main}</td>
      <td class="${sc}">${row.sub}</td>
    `;
    tbody.appendChild(tr);
  });

  // doll cell click → inline select
  tbody.querySelectorAll("td.doll").forEach(td => {
    td.addEventListener("click", () => openDollEditor(td));
  });
}

function openDollEditor(td) {
  if (td.querySelector("select")) return; // already open
  const idx = parseInt(td.dataset.idx);
  const current = rows[idx].doll;

  const sel = document.createElement("select");
  sel.className = "doll-select";
  dollNames.forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    if (name === current) opt.selected = true;
    sel.appendChild(opt);
  });

  td.textContent = "";
  td.classList.remove("empty");
  td.appendChild(sel);
  sel.focus();

  function commit() {
    const chosen = sel.value;
    rows[idx].doll = chosen;
    td.removeEventListener("blur", onBlur, true);
    td.innerHTML = chosen;
    td.className = chosen === "__" ? "doll empty" : "doll";
    td.dataset.idx = idx;
    td.addEventListener("click", () => openDollEditor(td));
    if (chosen !== current) markUnsaved();
  }

  function onBlur() { commit(); }
  sel.addEventListener("change", commit);
  sel.addEventListener("blur", onBlur, true);
  sel.addEventListener("keydown", e => {
    if (e.key === "Enter")  { e.preventDefault(); commit(); }
    if (e.key === "Escape") { sel.value = current; commit(); }
  });
}

// ── filters ────────────────────────────────────────────────────────────────
function applyFilters() {
  const allRows = tbody.querySelectorAll("tr");
  let visible = 0;
  allRows.forEach(tr => {
    const usrMatch  = activeFilter.usr  === "all" || tr.dataset.usr       === activeFilter.usr;
    const mainMatch = activeFilter.main === "all" || tr.dataset.mainColor === activeFilter.main;
    const subMatch  = activeFilter.sub  === "all" || tr.dataset.subColor  === activeFilter.sub;
    const show = usrMatch && mainMatch && subMatch;
    tr.classList.toggle("hidden", !show);
    if (show) visible++;
  });
  document.getElementById("rowCount").textContent = `${visible} / ${rows.length}`;
}

document.querySelectorAll(".user-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    activeFilter.usr = btn.dataset.user;
    document.querySelectorAll(".user-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    applyFilters();
  });
});

document.querySelectorAll(".color-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const col = btn.dataset.col;
    activeFilter[col] = btn.dataset.color;
    document.querySelectorAll(`.color-btn[data-col="${col}"]`).forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    applyFilters();
  });
});

// ── init ───────────────────────────────────────────────────────────────────
renderTable();
applyFilters();
