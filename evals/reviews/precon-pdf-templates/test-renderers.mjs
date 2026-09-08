import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, join } from 'node:path';
import { spawnSync } from 'node:child_process';

const skill = resolve(process.env.PRECON_SKILL || 'skills/precon-pdf-templates');
const families = ['construction-budget-export', 'milestone-export', 'employee-resume'];
function run(family, data, args = []) {
  const dir = mkdtempSync(join(tmpdir(), 'precon-test-'));
  try {
    writeFileSync(join(dir, 'data.json'), JSON.stringify(data));
    const result = spawnSync('node', [join(skill, 'templates', family, 'field-ready-technical/render.mjs'), 'data.json', 'out.html', ...args], {cwd:dir, encoding:'utf8'});
    let html = '';
    try {html = readFileSync(join(dir, 'out.html'), 'utf8');} catch {}
    return {...result, html};
  } finally {rmSync(dir, {recursive:true, force:true});}
}
const sample = family => JSON.parse(readFileSync(join(skill, 'templates', family, 'field-ready-technical/sample-data.json')));
for (const family of families) {
  test(`${family}: shipped sample matches actual renderer`, () => {
    const result = run(family, sample(family));
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.html, readFileSync(join(skill, 'templates', family, 'field-ready-technical/sample-output.html'), 'utf8'));
  });
  test(`${family}: warm theme resolves outside skill cwd`, () => {
    const result = run(family, sample(family), ['--theme', 'warm-owner-facing']);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.html, /--primary: #3f2e24/);
    assert.doesNotMatch(result.html, /#334155|#0f766e/);
    assert.match(result.html, /thead \{ display: table-header-group/);
    assert.match(result.html, /@page \{ size: letter/);
  });
}
test('budget: cents, negative deduct, zero, escaped input and mismatched exported totals survive', () => {
  const data = sample(families[0]);
  data.project = '<script>alert("x")</script> & School';
  data.divisions[0].lineItems[0].totalCents = 12345;
  data.divisions[0].totalCents = 12789;
  data.alternates = [{description:'Deduct',totalCents:-1820017},{description:'No charge',totalCents:0}];
  const result = run(families[0], data);
  assert.equal(result.status, 0, result.stderr);
  for (const amount of ['$123.45', '$127.89', '-$18,200.17', '$0.00']) assert.ok(result.html.includes(amount), amount);
  assert.match(result.html, /&lt;script&gt;/);
  assert.doesNotMatch(result.html, /<script>/);
});
test('budget: missing, null, fractional, string and unsafe cents fail before output', () => {
  for (const invalid of [undefined, null, 1.2, '100', 9007199254740992]) {
    const data = sample(families[0]); data.totals.grandTotalCents = invalid;
    const result = run(families[0],data);
    assert.notEqual(result.status,0); assert.equal(result.html,'');
    assert.match(result.stderr,/safe integer cents/);
  }
});
test('milestone: cost per SF preserves the supplied $67.93', () => {
  assert.match(run(families[1],sample(families[1])).html,/\$67\.93/);
});
test('milestone: missing construction cost fails without inventing zero', () => {
  const data = sample(families[1]); delete data.summary.constructionCostCents;
  const result = run(families[1],data); assert.notEqual(result.status,0); assert.equal(result.html,'');
});
test('resume: absent optional meta never claims years experience', () => {
  const data = {employee:{name:'Casey',role:'Estimator'},projectExperience:[]};
  const result = run(families[2],data); assert.equal(result.status,0,result.stderr);
  assert.doesNotMatch(result.html,/years experience|undefined|NaN/);
});
test('unknown theme and extra arguments fail without output', () => {
  for (const args of [['--theme','missing'],['--theme','../warm-owner-facing'],['extra'],['--theme','warm-owner-facing','extra']]) {
    const result = run(families[0],sample(families[0]),args);
    assert.notEqual(result.status,0); assert.equal(result.html,'');
  }
});
