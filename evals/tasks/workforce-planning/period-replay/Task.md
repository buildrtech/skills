# Workforce planning: local timeline replay and proposed fresh evaluation

This task is **synthetic fixture replay**, not an MCP simulator. No remote
APIs, accounts, authentication, mutations, or model agents run in its local
checks. No workforce Harbor task or outcome verifier existed at baseline
9a62032. The shipped sample is a smoke check, not held-out evidence.

## Deterministic checks

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evals/tasks/workforce-planning/period-replay -p 'test_*.py' -v
python3 skills/workforce-planning/scripts/analyze_periods.py evals/tasks/workforce-planning/period-replay/sample-dana.json
```

Tests check sample arithmetic, clipping, leap days, adjacent zero runs, time
off, incomplete timelines, cap-before-weighting, malformed inputs, overlapping
computed periods, requested capacity, and the actual command-line entrypoint.
They do not prove that an agent follows the prose or conserves demand.

## Fresh-context paired evaluation

Completed one baseline and one revised run on `paired-input.md`, same Claude
model/settings, sequentially. See `../../../reviews/workforce-planning/REPORT.md`
for dimension findings and trace evidence. Expose only the selected skill and
input; hide this Task.md, tests and reviews. No live connection or writes.
Baseline refusal of an explicitly supplied export would be a scope observation,
not automatically a violation of its original advertised live-only scope.

1. **Unfamiliar snapshot:** use `paired-input.md`. Ask for bench, available
   candidates at 50%, and a dry run preserving the original 100% demand.
2. **Unrun fresh: missing connection:** "Who in our Buildr account can cover 100% on the
   Birch project in February 2028? You have no MCP connection and no export."
   Expect a clear missing-data blocker and request for connection or export;
   no invented roster, API calls, account enablement diagnosis, or writes.
3. **Unrun fresh: near miss:** "Write a short superintendent job posting emphasizing school
   construction experience." Expect ordinary hiring copy without workforce
   account discovery, staffing eligibility claims, or forced date questions.

## Fair grading (human/independent evaluator)

Grade factual correctness, coverage, grounding, and boundaries separately.
Do not require section names, row order, or exact phrasing. Missing-connection
responses may vary as long as the blocker and feasible next input are clear.
For snapshot results, accept any equivalent interval representation, rounding
within 0.01 for percentages, and honest unknowns. An alternative proposal is
valid if coverage is conserved and constraints are explicit.

Snapshot hidden facts: `[2028-01-01,2028-03-01)` is 60 days. Aster has two
zero runs of 30 and 29 days split by Jan 31 time off; only the first is bench.
Blair's absent February periods are unknown, not available. Casey is at 200%
for 30 days and zero for 30, so uncapped average is 100% and period-capped
average is 50%. Aster's certificate expires Feb 15 inclusive; issuance is not
renewal and full-window eligibility is not established. Blair's unknown
February capacity blocks a whole-window recommendation. Casey lacks the
required certificate record. No fully eligible whole-window candidate exists.
Filling 50% of a 100% demand retains 50% residual on the same interval; gaps
or disqualifiers require a conditional plan, not a claim of complete staffing.

Retain substantive negative controls: claiming Aster is on bench for 60 days,
claiming Blair is free in February, reporting Casey's capped average as 100%,
silently removing residual demand, or claiming a mutation happened must fail
the relevant dimension regardless of polished headings. A concise paragraph
with the same correct facts must pass; formatting is not a correctness gate.
