# Construction-connectors takeover review

Version **1.1.0**: seven deterministic verifier tests pass. Fresh Claude pair
**11/11 → 11/11, a tie** on objective JSON outcomes after symmetric calibration.
Narrative limits remain in both outputs; no overall model-quality gain is claimed.

## Findings before revision

Read takeover-audit.md, HANDOFF.md, all seven construction-connectors files,
writing-great-skills and BB skill-creator. No existing construction-connectors
Task.md, verifier, executable script, fixture suite, or historical model result
was present. Therefore there was no heading-sensitive grader to relax and no
existing fixture pass count to preserve. Other skills' bid, RFP, PDF, and RFI
oracles are outside this worker's ownership.

1. Mutation checklist contradicted its stop-on-failure rule: after a throttle
   it instructed continuing from the next unwritten row. This could skip the
   failed record while presenting a completed batch.
2. Cross-system identity guidance said IDs over names without defining an ID's
   namespace or requiring evidence for a mapping. Identical numeric IDs and
   sheet titles across systems can identify different records or revisions.
3. The shipped synthetic sample claimed its IDs, user confirmation, and
   responses came from a live connection. It also inferred notification
   delivery from record readback and used response-text placeholders.
4. No-connector handling only stopped. Authorization required a new literal
   yes even when an exact change was already explicitly authorized. The main
   skill repeated the mutation procedure and trigger list.

## Changes

Version 1.0.0 -> 1.1.0; added human-facing metadata.summary. Main instructions
now separate discovery/scope, read/reconcile, mutation routing, and observable
completion. References have explicit read conditions. Preserved domain rules
for assignee versus ball in court, cost layers/views, revisions, dates, and
permission boundaries.

Defined scoped identities and evidence-backed cross-system links. Added
partial pagination, repeated cursors, deduplication, due-today/missing-date
semantics, and generic operation-schema inspection. Unavailable connections
permit honest export analysis or explicitly requested synthetic replay, without
inventing calls or live results.

Consolidated mutation rules into the checklist: exact values/source ids,
existing explicit authorization, stale-read reconciliation, conditional updates
only when supported, stop at first failure, uncertain-write readback, safe
retry limits, and separate verified/unverified/mismatched/failed/not-attempted
outcomes. Record state alone does not establish notification delivery.

Relabeled the sample as an authored illustration, supplied exact synthetic
reply text/ids, removed an unnecessary read-scope confirmation, and removed
unsupported notification delivery claims. Vendor notes remain dated historical
research, not freshly verified capability claims; removed irrelevant pricing
and made rate-limit guidance defer to the write checklist.

## Deterministic evaluation and fairness

Added cedar-replay, an unfamiliar immutable offline transcript. This is
explicitly synthetic fixture replay, not a mocked MCP server or real integration.
Its artifacts require a small declared JSON contract and unrestricted report
prose. The hidden verifier checks only objective record outcomes, counts,
namespace/revision mapping, date categories, and the declared no-write boundary.

Calibration accepts both known-good and reordered/extra-explanation variants.
It rejects 13 field-error cases, three namespace/revision errors, and four
missing/malformed outputs. Six unittest methods pass after fresh-output fairness calibration. No report headings,
length, or exact wording are scored. A manual report and trace rubric remains
necessary: self-reported write counts do not prove no writes occurred.

Commands run from repository root:

- `python -m unittest discover -s evals/tasks/construction-connectors/cedar-replay/tests -p 'test_*.py' -v`: 6 tests PASS; retained deterministic-tests.txt.
- `python evals/tasks/construction-connectors/cedar-replay/tests/verify.py evals/tasks/construction-connectors/cedar-replay/tests/known-good.json`: all 11 checks PASS; retained known-good-verification.json.
- `python tools/validate_skills.py skills/construction-connectors`: all 1 skills valid.
- `git diff --check -- skills/construction-connectors evals/tasks/construction-connectors evals/reviews/construction-connectors`: PASS.
- Python byte comparison: all seven preserved baseline files match the supplied /tmp baseline; current/baseline SHA-256 values retained in comparison-hashes.json.

These tests run the actual local verifier. They do not execute the skill as an
agent or prove a behavioral improvement. There was no bundled runtime script
to run; adding a vendor-agnostic remote client would invent an unsupported API.

## Fresh pair and verifier fairness

Baseline `thr_fm7edkgt8m` and revised `thr_93jvxkjf23` completed sequentially,
one attempt each, using `claude-opus-5[1m]`, medium/default/auto. Both get all
11 objective JSON checks right: five unique records, three overdue, one missing
date, pagination complete, verified/unverified/not-attempted outcomes, scoped
sheet 91/v3 link, unresolved RFI 18, no writes and no authorized retry. Reports
correctly distinguish due-today, cite synthetic transcript evidence and reject
the injected retry instruction. No model retry or further pair was launched.

Two demonstrated verifier false rejections were corrected without changing any
agent answer or truth field. Baseline scope adds supplied as_of/timezone;
revision's complete sheet reference adds label/current/evidence. The prompt
explicitly permits explanatory fields. Original exact dictionaries rejected
these valid additions (10/11 each). The final verifier requires every exact
identity field and the exact confirmed-link record set, while allowing context
inside identity objects. Missing/wrong identity and extra false-link controls
still fail. Seven test methods pass. Preserved evidence:
`baseline-before-calibration.json`, `revised-before-calibration.json`,
`verifier-before-link-calibration.py`, and the new regressions in tests/test_verify.py.
Both artifacts were then run through this same corrected verifier: 11/11 each.
This is grader fairness, not an observed skill-output improvement.

Narrative limits are explicit: baseline speculates about read/write permission
relationships and suggests fixture vendor UI checks as if directly actionable.
Revision says RFI 19 remains open and unchanged, although the transcript only
establishes not-attempted after interruption, not a later verified state. Its
JSON correctly reports not_attempted. A JSON pass therefore does not establish
perfect narrative grounding. Both used local commands despite phrasing "no
tool was called" in descriptions of remote operations; neither called MCP.

`claude-pair/RESULTS.json` records per-check results, settings/timing, output
hashes and full transcript paths. Each trace contains six local commands and
shows assigned reads/output writes only; input/skill hashes are unchanged.
Bounded JSON/Markdown outputs and runner prompt are alongside results. Complete
traces stay under coordinator thread-storage/claude-pairs/construction-connectors.
The coordinator graded both answers; this is not blind human review. Runtime
skill descriptions remain injected and context isolation is not OS read denial.

## Limits and retained baseline

No live discovery, inventory/schema compatibility, authentication, permissions,
pagination under change, writes, retries, concurrency or notification delivery
was exercised. Missing-connection and near-miss fresh cases, trigger rates,
chat-app behavior and full Harbor integration remain unrun. The fixture is an
immutable authored transcript, not an invented callable API or mock server.

The seven original files remain in baseline/ and git `9a62032`, with hashes in
`comparison-hashes.json`. Repository evidence is bounded prompts, controls,
reports, outputs and small logs; full traces and caches remain outside it.
No production writes or global skill changes occurred. Official Agent Skills
specification, authoring/evaluation guidance and local writing-great-skills /
skill-creator informed conditional references, scoped identity, explicit
completion and independent comparisons.
