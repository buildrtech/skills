import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { validate } from "../../../skills/proposal-builder/templates/validate.mjs";
const sample = JSON.parse(
  readFileSync(
    new URL(
      "../../../skills/proposal-builder/samples/input-proposal.json",
      import.meta.url,
    ),
  ),
);
test("preserves signed cents and excludes options from the base", () => {
  assert.equal(validate(sample).baseTotalCents, 14450025);
  const d = structuredClone(sample);
  d.baseTotalCents += d.pricing.at(-1).cents;
  assert.throws(() => validate(d), /reconcile/);
});
test("rejects wrong shape, missing evidence and duplicate prices", () => {
  for (const change of [
    (d) => (d.scope = {}),
    (d) => (d.team[0].source = ""),
    (d) => d.pricing.push(d.pricing[0]),
    (d) => (d.pricing[0].cents = 1.5),
    (d) => (d.pricing[0].cents = Number.MAX_SAFE_INTEGER + 1),
    (d) => (d.status = "APPROVED"),
  ]) {
    const d = structuredClone(sample);
    change(d);
    assert.throws(() => validate(d));
  }
  assert.throws(() => validate(null));
});
test("does not mutate user data", () => {
  const d = structuredClone(sample);
  validate(d);
  assert.deepEqual(d, sample);
});
