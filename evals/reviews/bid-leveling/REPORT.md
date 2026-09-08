# Bid-leveling takeover report

Version **2.0.0** is verified by 14 targeted tests and eight fixture controls.
Fresh Claude fallback: **8/8 baseline → 8/8 revised, a tie**, both completed.
The original Codex pair also tied on artifacts, but revision hit its provider
usage limit after producing the comparison; it is not a clean terminal pass.

## Findings and changes

- **Submission identity:** the baseline keyed bids by company name and discarded
  every later extraction with that name. Version **2.0.0** requires stable
  `submission_id` values and targets decisions by ID. Company names and IDs
  appear together in both Markdown and XLSX. Supporting documents can share one
  extraction; distinct options remain separate, and governing revisions require
  an estimator decision before ranking. Duplicate IDs are rejected.
- **Alternate reconciliation:** duplicate keys previously overwrote prices, and
  the first bidder's metadata silently governed a joined row. Printed labels
  now remain beside their price and evidence ref. Differing printed labels
  require mapping notes citing the package basis. Conflicting common scope
  labels/kinds are rejected; voluntary options stay separate per submission.
  The agent must match scope, not printed number alone. Unknown mappings remain
  separate with questions. These validation checks cannot establish that a
  prose mapping is truthful; source review remains necessary.
- **Arithmetic/control defects:** duplicate plugs previously counted twice while
  showing one cell value; now rejected. Decisions are validated before any
  arithmetic. Malformed decision containers return exit 2 instead of a stack
  trace. Duplicate scope rows, conflicting row classes, missing/broken evidence,
  duplicate evidence refs and wrong alternate signs are rejected. Root independently
  reproduced the scope/alternate namespace collision during review; the final
  scan checks each namespace separately, with the exact regression retained.
- **Authoring:** retained the domain-specific workflow and conditional references;
  made artifact completion explicit (generated tables plus sourced explanation
  and bidder questions), documented identity and alternate mapping, added an
  identity trigger example, and added the requested human-facing metadata.summary.
  Updated owned sample/task JSON and regenerated their script outputs. This is
  a deliberate schema change: there is no bidder-name decision fallback.

RFP completeness, PDF theme/renderer changes, and the RFI conditional-air oracle
belong to other owners and were not edited here. This skill remains neutral;
connected bid leveling was not restored.

## Verifier fairness, inspected before layout changes

The old correctness check required the exact “lowest complete leveled total”
phrase and could reject an accurate raw-low contrast. Exact headings also
contributed to the pass threshold. A complete known-good deliverable was changed
only to use descriptive headings and equivalent ranking wording. Preserved
`fairness-before.json`: reward **0**, correctness **0.88**, format **0.1786**,
soft_score **0.8699**. No facts or totals were removed.

The retained `valid-alternate-wording` control now passes. Format remains a
separate diagnostic and contributes to soft_score, not the pass reward. Ranking
accepts equivalent wording while requiring the correct bidder, amount, and
completeness. The new `wrong-leveled-low` control changes only the headline to
name Blue Heron incorrectly; it exposed that the first weight adjustment was
insufficient (`fixtures-intermediate.txt`). Final totals/ranking weights are 10
apiece; wrong ranking and wrong gap arithmetic both fail, alongside all prior
substantive negative controls. No baseline output was overwritten to hide that
intermediate failure.

The verifier remains heuristic: amount-set membership can allow an unrelated
arithmetic-derived number, and line-based checks do not prove every narrative
claim or question. Format/shape diagnostics are not an exhaustive deliverable
completeness gate. Fresh comparison review must inspect the artifact and trace;
do not interpret reward 1 as proof of every skill requirement.

## Deterministic paired evidence

Baseline preserved at git **9a62032a237cd7588f6f6c687021acc076cd6fb7** and
`/tmp/skills-takeover-baseline-9a62032`. `baseline-check.json` records actual
script/output SHA-256 values and arithmetic/completeness from both versions.

| Case | Baseline | Revised |
|---|---|---|
| Two submissions, same company | Exit 0, second silently omitted | Exit 0, both retained |
| Different printed labels, no mapping | Exit 0, implicit join | Exit 2, asks for reconciliation |
| Duplicate alternate, conflicting price | Exit 0, later price overwrites | Exit 2, duplicate rejected |
| Duplicate cleanup plug | Exit 0, adds twice | Exit 2, duplicate rejected |
| Original drywall sample | Correct arithmetic | **Tie**, unchanged arithmetic/completeness |
| Original Millbrook roofing fixture | Correct arithmetic | **Tie**, unchanged arithmetic/completeness |

Small CLI outputs, errors and synthetic input facts are retained in comparison/;
`replay_comparison.py` reproduces them. Old-schema decisions are translated only
for the baseline invocation, preserving the same targeting and dollar facts.
This is **explicitly synthetic fixture replay**, not an agent/model comparison
or a live MCP test. Samples are smoke checks, not unfamiliar evaluation inputs.

Final tests: **14/14 pass**, including the real CLI, same-company targeting,
printed-label mapping, voluntary isolation, duplicate controls, malformed input,
evidence integrity, original arithmetic, and an XLSX workbook reopened with
openpyxl to inspect submission/alternate cells. **8/8 verifier fixture controls**
behave as expected (two valid positives, six negatives).

## Commands and results

Run from the repository root:

```sh
python3 evals/reviews/bid-leveling/replay_comparison.py
python3 evals/reviews/bid-leveling/check_baseline.py
UV_CACHE_DIR=/tmp/bid-uv-cache uv run --no-project --with openpyxl==3.1.5 python3 -m unittest discover -s evals/reviews/bid-leveling -p 'test_*.py' -v
UV_TOOL_DIR=/tmp/bid-uv-tools UV_CACHE_DIR=/tmp/bid-uv-cache python3 evals/scripts/check_fixtures.py evals/tasks/bid-leveling/millbrook-roofing-07a
python3 skills/bid-leveling/scripts/level_bids.py skills/bid-leveling/samples/*.json
python3 skills/bid-leveling/scripts/level_bids.py evals/tasks/bid-leveling/millbrook-roofing-07a/tests/fixtures/extraction-ironwood.json evals/tasks/bid-leveling/millbrook-roofing-07a/tests/fixtures/extraction-blue-heron.json evals/tasks/bid-leveling/millbrook-roofing-07a/tests/fixtures/extraction-cardinal.json evals/tasks/bid-leveling/millbrook-roofing-07a/environment/input/estimator-decisions.json
git diff --check -- skills/bid-leveling evals/tasks/bid-leveling evals/reviews/bid-leveling
```

Logs: tests-final.txt, fixtures-before.txt, fixtures-final.txt, baseline-check.json,
comparison/results.json. Diff check clean. Initial host-only test run skipped
optional openpyxl; the final isolated uv run installed pinned openpyxl in /tmp
and exercised XLSX successfully. Initial fixture invocation hit a read-only uv
tools directory; setting UV_TOOL_DIR under /tmp resolved it. These were local
environment issues, not skill/model failures.

## Fresh evaluation and live limits

The coordinator approved exactly two sequential default-provider runs. Results
are in paired/RESULTS.json, with hashes and exact trace/artifact paths.

| Condition | Fresh thread | Actual runtime | Result |
|---|---|---|---|
| Baseline | thr_k9nesni24h | 59.849 seconds | Completed; all 8 substantive artifact checks pass |
| Revised | thr_8c7uyeacdr | 39.679 seconds | All 8 artifact checks pass; provider usage-limit failure after generation |

**Artifact-level tie, n=1 each.** Baseline worked around name-based deduplication
by suffixing company names with option labels and appended a printed-alternate
crosswalk. Revised used native submission IDs and printed-label mapping notes.
Both ran their assigned bundled script successfully and preserved company/option
identity, 46800 complete / 44000 incomplete / 47100 complete, the single 1800
cleanup plug, all alternate labels/prices, and bidder questions without an award.
The revised script command completed at trace seq 62; provider usageLimitExceeded
occurred at seq 69 before final assistant review/supplement. Thus the revised
artifact exists, but this is not a clean terminal-success comparison. The initial
failed-turn UI suggested no deliverable; filesystem and full-trace inspection
corrected that report, and the coordinator was notified immediately.

Both runs used identical omitted/default model settings. Captured events identify
Codex but do not expose a resolved model ID. Separate unmanaged directories
contained only INPUT.md plus the assigned skill before execution; hidden expected
results/tests/opposite skill were not copied. Command traces show no outside
resource reads. Global runtime skill descriptions were still injected, so this
is isolated task context, not an OS-level read-denial sandbox or a trigger test.
Input/skill file hashes were unchanged after both runs. No timeout or retry.

Full evidence remains under
`/home/mikeastock/.bb/thread-storage/thr_kefaywjbew/fencing-pair/`:
`baseline-log.json`, `revised-log.json`, and each lane's `output/` hold full
traces, generated JSON, and comparisons. Only bounded rubric results/hashes
are retained in the repo. Evaluation slot released to the coordinator.
The authorized separate Claude fallback completed as `thr_qu7sf5ud8x` and
`thr_xqen96xebw`, both `claude-opus-5[1m]`, medium/default/auto. All eight
frozen artifact checks pass in both, with unchanged assigned inputs/skills.
Both ran their bundled script successfully; observed reads stayed within each
lane and no remote writes occurred. Baseline used option-name suffixes and a
crosswalk; revision used native IDs/mapping. This is a process difference,
not an outcome gain. `claude-pair/RESULTS.json` retains per-check results,
settings, timing, hashes and full transcript paths; bounded output copies are
alongside it. No cross-provider score comparison or statistical claim is made.

Not run: trigger-rate tests, broader model matrix, live MCP compatibility, remote
bid retrieval, PDF extraction from actual PDFs, or production writes. No remote
API was invented. Plain-text fixtures test the deterministic comparison path;
XLSX inspection tests generated cell contents, not Excel/LibreOffice visual UX.

## Authoring sources applied

Read the audit, handoff, all bundled skill resources, task truth and verifier
fixtures, plus writing-great-skills and the BB skill-creator guidance. Applied
[Agent Skills specification](https://agentskills.io/specification),
[authoring best practices](https://agentskills.io/skill-creation/best-practices),
and [evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills):
retain domain expertise, put fragile computation in tested scripts, route
references by use, calibrate format controls to user requirements, preserve
substantive negative controls, and compare fresh isolated behavior separately
from deterministic smoke checks. Fresh evaluation was scheduled by the coordinator
per the user's explicit concurrency instruction.
