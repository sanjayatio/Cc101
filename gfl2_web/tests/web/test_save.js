/**
 * Automated tests for the save features of remold, affection, and task modules.
 *
 * What is tested:
 *   1. buildDataFileContent() round-trip: serialise → re-execute → data matches original
 *   2. Mutation propagation: in-memory change is reflected in serialised output
 *   3. Re-parseable output: the generated JS is syntactically valid and re-loadable
 *   4. saveDataFile() fallback path: when showSaveFilePicker is absent the content
 *      gets written correctly (captured via a mock <a> element)
 *
 * Run with:
 *   node tests/web/test_save.js
 *
 * Technique note:
 *   Module files use `let` for mutable state, which vm.runInContext does not expose
 *   on the context object. To bridge this, we append a small test-harness snippet
 *   (using `var`) to each combined source string so state is readable/mutable from
 *   outside the vm execution while staying in the same script scope.
 */

'use strict';

const fs   = require('fs');
const path = require('path');
const vm   = require('vm');

// ── helpers ──────────────────────────────────────────────────────────────────

const ROOT = path.resolve(__dirname, '../..');

function readFile(rel) {
  return fs.readFileSync(path.join(ROOT, rel), 'utf8');
}

/**
 * Execute a combined JS source string in an isolated vm context.
 * Returns the context so callers can invoke function declarations on it.
 */
function execInContext(combinedSrc, extraGlobals = {}) {
  const ctx = vm.createContext({ ...extraGlobals });
  vm.runInContext(combinedSrc, ctx);
  return ctx;
}

/**
 * Re-execute a serialised data file for assertion purposes.
 * Data files use `const` which vm doesn't expose on the context; we replace
 * `const ` with `var ` at the top level so declared names land on the context.
 * This is fine for read-only inspection — we never write back via these contexts.
 */
function execDataFile(src, extraGlobals = {}) {
  // Only replace standalone `const ` declarations (not `const` inside strings/comments).
  // A line-start replacement is sufficient since all data files declare at column 0.
  const patched = src.replace(/^const /gm, 'var ');
  return execInContext(patched, extraGlobals);
}

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log('  ✓', label);
    passed++;
  } else {
    console.error('  ✗', label);
    failed++;
  }
}

function assertEqual(a, b, label) {
  const ok = JSON.stringify(a) === JSON.stringify(b);
  if (ok) {
    console.log('  ✓', label);
    passed++;
  } else {
    console.error('  ✗', label);
    console.error('    expected:', JSON.stringify(b));
    console.error('    got:     ', JSON.stringify(a));
    failed++;
  }
}

// ── DOM stub ─────────────────────────────────────────────────────────────────
// Minimal stubs so module files don't throw when they access document/window.

function makeEl() {
  const el = {
    innerHTML: '', textContent: '', style: {}, href: '', download: '',
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    querySelectorAll: () => ({ forEach: () => {} }),
    querySelector:   () => null,
    appendChild:     () => {},
    addEventListener:() => {},
    removeEventListener: () => {},
    dataset: {}, rows: { length: 0 }, colSpan: 0,
    click() { this._clicked = true; },
  };
  return el;
}

function makeDomStub(overrides = {}) {
  const el = makeEl();
  return {
    document: {
      getElementById:   () => el,
      querySelector:    () => el,
      querySelectorAll: () => ({ forEach: () => {} }),
      createElement:    () => el,
      addEventListener: () => {},
      body:             { appendChild: () => {} },
      ...overrides.document,
    },
    window: {
      // No showSaveFilePicker by default → exercises the fallback path
      ...overrides.window,
    },
  };
}

// ── capture stub ──────────────────────────────────────────────────────────────
// Returns globals that intercept Blob + <a download> and expose what was written.

function makeSaveCapture() {
  const capture = { filename: null, content: null };
  const el = makeEl();
  el.click = function () { capture.filename = this.download; };
  // URL is accessed as a bare global (not window.URL) in the module code.
  const urlStub = { createObjectURL: () => 'blob:mock', revokeObjectURL: () => {} };
  return {
    capture,
    globals: {
      Blob: class MockBlob {
        constructor(parts) { capture.content = parts.join(''); }
      },
      URL: urlStub,               // bare global — modules access URL directly
      setTimeout: () => {},
      window: { URL: urlStub },   // also under window for completeness
      document: {
        getElementById:   () => el,
        querySelector:    () => el,
        querySelectorAll: () => ({ forEach: () => {} }),
        createElement:    () => el,
        addEventListener: () => {},
        body:             { appendChild: () => {} },
      },
    },
  };
}

// ── REMOLD ───────────────────────────────────────────────────────────────────

console.log('\n── remold ──────────────────────────────────────────────────────────');

{
  const masterRemold = readFile('data/master_remold.js');
  const masterDoll   = readFile('data/master_doll.js');
  const testData     = readFile('tests/web/data_remold.js');
  const moduleSrc    = readFile('js/remold.js');

  // Test bridge: var declarations are accessible on the vm context; they can
  // also read/write the module's let-declared `rows` because they live in the
  // same concatenated script scope.
  const testBridge = `
    var __getRows        = () => rows;
    var __setRowDoll     = (i, v) => { rows[i].doll = v; };
    var __buildContent   = () => {
      const tuples = rows.map(r => [r.owner, r.tier, r.doll, r.main, r.sub]);
      const pad = (s, n) => s + ' '.repeat(Math.max(0, n - s.length));
      const lines = tuples.map(([o, t, d, m, s]) =>
        '  [' + JSON.stringify(o) + ',' + JSON.stringify(t) + ',' +
        pad(JSON.stringify(d)+',', 16) + ' ' +
        pad(JSON.stringify(m)+',', 30) + ' ' +
        JSON.stringify(s) + ']'
      );
      return '// [owner, tier, doll, main, sub]\\nconst REMOLD_DATA = [\\n' +
        lines.join(',\\n') + ',\\n];';
    };
  `;

  const stub = makeDomStub();
  const combined = [masterRemold, masterDoll, testData, moduleSrc, testBridge].join('\n');
  const ctx = execInContext(combined, { document: stub.document, window: stub.window });

  // 1. Round-trip fidelity
  const serialised = ctx.__buildContent();
  assert(typeof serialised === 'string' && serialised.length > 0,
    'serialised output is a non-empty string');
  assert(serialised.includes('const REMOLD_DATA'),
    'output contains REMOLD_DATA declaration');

  const ctx2 = execDataFile(serialised);
  assertEqual(ctx2.REMOLD_DATA.length, 5,
    'round-trip preserves row count (5)');
  assertEqual(ctx2.REMOLD_DATA[0],
    ['GM','F3','Suomi','Attack Boost','Corrosive Smite'],
    'round-trip preserves first row values');
  assertEqual(ctx2.REMOLD_DATA[1][2], '__',
    'round-trip preserves unassigned slot');

  // 2. Mutation propagation
  ctx.__setRowDoll(1, 'Groza');
  const serialised2 = ctx.__buildContent();
  const ctx3 = execDataFile(serialised2);
  assertEqual(ctx3.REMOLD_DATA[1][2], 'Groza',
    'doll assignment change is reflected in re-serialised output');

  // 3. Fallback save path
  const { capture, globals } = makeSaveCapture();
  const ctxSave = execInContext(
    [masterRemold, masterDoll, testData, moduleSrc].join('\n'),
    globals
  );
  ctxSave.saveDataFile(); // synchronous fallback path (no showSaveFilePicker)
  assertEqual(capture.filename, 'data_remold.js',
    'fallback download uses filename "data_remold.js"');
  assert(capture.content && capture.content.includes('REMOLD_DATA'),
    'fallback blob content includes REMOLD_DATA');
  const ctx4 = execDataFile(capture.content);
  assertEqual(ctx4.REMOLD_DATA.length, 5,
    'fallback content is re-parseable and preserves row count');
}

// ── AFFECTION ────────────────────────────────────────────────────────────────

console.log('\n── affection ───────────────────────────────────────────────────────');

{
  const masterAffection = readFile('data/master_affection.js');
  const testData        = readFile('tests/web/data_affection.js');
  const moduleSrc       = readFile('js/affection.js');

  const stub = makeDomStub();
  const combined = [masterAffection, testData, moduleSrc].join('\n');
  const ctx = execInContext(combined, { document: stub.document, window: stub.window });

  // 1. Round-trip fidelity
  const serialised = ctx.buildDataFileContent();
  assert(typeof serialised === 'string' && serialised.length > 0,
    'serialised output is a non-empty string');
  assert(serialised.includes('const RAW_OWNERSHIP'),
    'output contains RAW_OWNERSHIP declaration');

  const ctx2 = execDataFile(serialised);
  assertEqual(Object.keys(ctx2.RAW_OWNERSHIP).length, 4,
    'round-trip preserves doll count (4)');
  assertEqual(ctx2.RAW_OWNERSHIP['Suomi'], { GM: 4, IB: 2 },
    'round-trip preserves Suomi affection values');
  assertEqual(ctx2.RAW_OWNERSHIP['Groza'], { IB: 4 },
    'round-trip preserves Groza affection (single owner)');

  // 2. Mutation propagation: change an existing level
  ctx.recordOverride('Groza', 'GM', 3);
  const serialised2 = ctx.buildDataFileContent();
  const ctx3 = execDataFile(serialised2);
  assertEqual(ctx3.RAW_OWNERSHIP['Groza']['GM'], 3,
    'new affection entry is reflected in re-serialised output');

  // 3. Doll order preservation: original dolls appear before runtime additions
  ctx.recordOverride('NewDoll', 'GM', 1);
  const serialised3 = ctx.buildDataFileContent();
  const ctx3b = execDataFile(serialised3);
  const keys = Object.keys(ctx3b.RAW_OWNERSHIP);
  assert(keys.indexOf('Suomi') < keys.indexOf('NewDoll'),
    'original dolls appear before runtime-added dolls in output');

  // 4. Fallback save path
  const { capture, globals } = makeSaveCapture();
  const ctxSave = execInContext(
    [masterAffection, testData, moduleSrc].join('\n'),
    globals
  );
  ctxSave.saveDataFile();
  // Known issue #5: affection uses 'data/data_affection.js' (path prefix) rather than
  // bare 'data_affection.js'. The test asserts the current (known) behaviour so that
  // any future fix to issue #5 causes this test to be updated intentionally.
  assertEqual(capture.filename, 'data/data_affection.js',
    'fallback download filename is "data/data_affection.js" [known issue #5 — current behaviour]');
  assert(capture.content && capture.content.includes('RAW_OWNERSHIP'),
    'fallback blob content includes RAW_OWNERSHIP');
  const ctx4 = execDataFile(capture.content);
  assertEqual(Object.keys(ctx4.RAW_OWNERSHIP).length, 4,
    'fallback content is re-parseable and preserves doll count');
}

// ── TASK ─────────────────────────────────────────────────────────────────────

console.log('\n── task ────────────────────────────────────────────────────────────');

{
  const testData  = readFile('tests/web/data_owner.js');
  const moduleSrc = readFile('js/task.js');

  // Test bridge to expose let-scoped dailyRows for mutation testing.
  const testBridge = `
    var __mutateDailyCount = (taskIdx, ownerId, val) => {
      dailyRows[taskIdx].counts[ownerId] = val;
    };
    var __mutateTimedCount = (taskIdx, ownerId, val) => {
      timedRows[taskIdx].counts[ownerId] = val;
    };
  `;

  const stub = makeDomStub();
  const combined = [testData, moduleSrc, testBridge].join('\n');
  const ctx = execInContext(combined, { document: stub.document, window: stub.window });

  // 1. Round-trip fidelity
  const serialised = ctx.buildDataFileContent();
  assert(serialised.includes('const DATA_OWNER'),     'output contains DATA_OWNER');
  assert(serialised.includes('const DATA_TASK_DAILY'),'output contains DATA_TASK_DAILY');
  assert(serialised.includes('const DATA_TASK_TIMED'),'output contains DATA_TASK_TIMED');

  const ctx2 = execDataFile(serialised);
  assertEqual(ctx2.DATA_OWNER.length, 2,
    'round-trip preserves owner count (2)');
  assertEqual(ctx2.DATA_TASK_DAILY.length, 2,
    'round-trip preserves daily task count (2)');
  assertEqual(ctx2.DATA_TASK_TIMED.length, 1,
    'round-trip preserves timed task count (1)');
  assertEqual(ctx2.DATA_TASK_DAILY[0][0], 'Daily Login',
    'round-trip preserves first daily task name');
  assertEqual(ctx2.DATA_TASK_DAILY[0][1][1], 5,
    'round-trip preserves owner-1 count for first daily task');

  // 2. Mutation propagation: increment a count
  ctx.__mutateDailyCount(0, 1, 99);
  const serialised2 = ctx.buildDataFileContent();
  const ctx3 = execDataFile(serialised2);
  assertEqual(ctx3.DATA_TASK_DAILY[0][1][1], 99,
    'count mutation is reflected in re-serialised output');

  // 3. Timed task mutation
  ctx.__mutateTimedCount(0, 2, 7);
  const serialised3 = ctx.buildDataFileContent();
  const ctx3b = execDataFile(serialised3);
  assertEqual(ctx3b.DATA_TASK_TIMED[0][2][2], 7,
    'timed task count mutation is reflected in re-serialised output');

  // 4. Fallback save path
  const { capture, globals } = makeSaveCapture();
  const ctxSave = execInContext([testData, moduleSrc].join('\n'), globals);
  ctxSave.saveDataFile();
  assertEqual(capture.filename, 'data_owner.js',
    'fallback download uses filename "data_owner.js"');
  assert(capture.content && capture.content.includes('DATA_OWNER'),
    'fallback blob content includes DATA_OWNER');
  const ctx4 = execDataFile(capture.content);
  assertEqual(ctx4.DATA_OWNER.length, 2,
    'fallback content is re-parseable and preserves owner count');
}

// ── summary ───────────────────────────────────────────────────────────────────

console.log(`\n${'─'.repeat(60)}`);
console.log(`Tests: ${passed + failed} total  |  ${passed} passed  |  ${failed} failed`);
if (failed > 0) process.exit(1);
ture.content.includes('DATA_OWNER'),
    'fallback blob content includes DATA_OWNER');
  const ctx4 = execDataFile(capture.content);
  assertEqual(ctx4.DATA_OWNER.length, 2,
    'fallback content is re-parseable and preserves owner count');
}

// summary

const SEP = '-'.repeat(60);
console.log('\n' + SEP);
console.log('Tests: ' + (passed + failed) + ' total  |  ' + passed + ' passed  |  ' + failed + ' failed');
if (failed > 0) process.exit(1);
