# Drawing scope extraction takeover — 2026-09-07

Version **1.1.0**: six CLI tests and six fixture controls pass. Fresh Codex
pair **7/8 → 8/8**; explicitly required shelf inclusion is the sole improvement.

Owner: `thr_hxa96szkr5`; coordinator: `thr_hpvpiweaze`.
Scope: only drawing-scope-extraction skill, task, and review directories. No production writes.

## Sources and authoring

Read takeover audit and handoff, skill resources and samples, Larkspur task inputs, reference candidates, fixture differences, verifier and Task.md. Other skills' bid identity, RFP completeness, PDF theme, and RFI air-content review requests are outside this ownership.

Applied [Agent Skills specification](https://agentskills.io/specification), [authoring guidance](https://agentskills.io/skill-creation/best-practices), and [evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills): source-based defects, conditional resource reads, tested deterministic script, and paired behavior evidence. Read local writing-great-skills and BB skill-creator guides. No relevant memory registry entry found.

Baseline remains at git `9a62032` and `/tmp/skills-takeover-baseline-9a62032`.

## Findings and revisions

- Version 1.1.0, plus human-facing `metadata.summary` requested by coordinator.
- Accept supplied sheet-indexed text explicitly; preserve extraction limits and distinguish text review from actual PDF/OCR work. Prior wording required PDFs even when the actual task supplied text only.
- Read grounding rules before recording candidates, and explicitly reconcile the ledger and quotes against supplied source. Script acceptance cannot prove source truth.
- Validator now rejects inclusion on unreadable/unreviewed primary sheets. Readable primary evidence can establish an item independently of an unreadable related sheet; retain unresolved dependencies under review.
- Optional array/string types now fail with actionable diagnostics instead of crashing. Boolean sheet counts and malformed candidate IDs are rejected. File read failures report clean errors. No added runtime dependency.
- Review heading prose now accommodates inferences and unresolved references without calling all of them drawing-backed; regenerated the shipped sample from the actual script.
- Probe example uses `rg`.

## Verifier evidence before optimization

Original five fixture cases behaved as expected (`baseline-fixtures.txt`). Headings remain lexical. Format has weight 1 in both the strict reward aggregation and soft score, so format can affect pass/fail; it is not diagnostic-only. No heading optimization or format-weight change was made.

Added `wrong-required-work-excluded`, generated from the hidden reference candidate set by excluding 31 of the 33 included items, keeping Division 06 included so unrelated blocking correctness remains intact. Original verifier awarded reward and soft score **1.0** (`baseline-negative-control.txt`).

Required-item correctness now checks the included section. That alone still earned reward 1 at soft score 0.92 (`revised-fixtures.txt`) because weighted aggregation dilutes large omissions. A coarse hard boundary therefore requires at least half of the 33 required items to remain included. Detailed recall stays a soft correctness measure. This deliberately tolerates lexical misses while catching wholesale exclusion. Existing negative controls remain; no fixture truth or threshold was weakened.

Remaining verifier limits: keyword matching is not semantic understanding; the extra-scope vocabulary fallback and broad negation filter are imperfect. Current comparison does not establish acceptance of all valid paraphrases or rejection of all fabricated scope. No claim of universal fairness.

## Deterministic commands and results

```
python -m unittest discover -s evals/reviews/drawing-scope-extraction -p 'test_*.py' -v
SCOPE_SCRIPT=/tmp/skills-takeover-baseline-9a62032/skills/drawing-scope-extraction/scripts/scope_list.py python -m unittest discover -s evals/reviews/drawing-scope-extraction -p 'test_*.py' -v
UV_CACHE_DIR=/tmp/drawing-uv-cache UV_TOOL_DIR=/tmp/drawing-uv-tools python3 evals/scripts/check_fixtures.py evals/tasks/drawing-scope-extraction/larkspur-ridge-ops-addition
git diff --check -- skills/drawing-scope-extraction evals/tasks/drawing-scope-extraction
```

Revised CLI: six tests pass. Baseline: seven failures across three test methods; three positive/control methods pass. Logs: `revised-tests.txt`, `baseline-tests.txt`. Tests invoke the actual subprocess CLI with sample/oracle input and malformed mutations, not mocked behavior. Initial fixture attempt hit read-only UV tools storage; both UV cache and tool directories were redirected to `/tmp` for successful execution.

Final fixtures: **6/6 expected outcomes**, including the added negative at reward 0, soft score 0.62. See `revised-fixtures-final.txt`. The generated sample exactly matches the shipped output (`cmp` exit 0); scoped `git diff --check` passed. Metadata summary is 114 characters and required resource paths exist.

## Fresh paired evaluation

Coordinator approved two sequential fresh threads, one attempt each using the same default model. A four-sheet unfamiliar Juniper Transit text fixture exercises readable backing, shelves with an unreadable related layout, hardware falsely cited to an unreadable primary, and owner-provided sensors. Hidden expectations stay outside evaluator directories. Evaluators receive only their lane's skill copy and identical task/input, with no implementation authority.

Baseline thread: `thr_jtxcbgrhig`, environment `env_mmwh7nv532`, `/tmp/drawing-paired-20260907/baseline`. Revised thread: `thr_7yxz6v35ht`, environment `env_br23mh76ap`,
`/tmp/drawing-paired-20260907/revised`. Both completed sequentially using
`gpt-6-astra`, medium reasoning, default service tier, auto permissions (verified
from each transcript's execution event).

`python evals/reviews/drawing-scope-extraction/check_pair.py` produced
`paired-results.json`: baseline **7/8**, revised **8/8**. Both corrected hardware's
primary citation to A-110, held schedule-dependent hardware for review, excluded
owner sensors, kept the four real ledger sheets with A-610 unreadable, and used
verbatim primary-sheet quotes. Both outputs exactly reproduce their bundled
renderer output. The distinction: baseline deferred explicitly required shelves;
revised included their stated material and room while recording the unreadable
layout as an RFI. This is a scope-list requirement, not a claim that dimensions
or fabrication details are resolved. Both selected Division 23 for generic
temperature sensors rather than claiming an unsupported DDC system; that
reasonable placement judgment was not graded as an error.

Inspected full command traces and artifacts: both read their supplied SKILL and
references, generated sheet text and probe ledgers, ran the actual bundled
renderer, and checked primary-sheet quotes. Neither modified skill/input files,
called MCP, ran OCR, or accessed other evaluation lanes in the observed commands.
Baseline recorded 24 probes; revised 25. Both explicitly reported text-only
coverage and no new OCR. No evaluator was told hidden checks or expected decisions.

Full transcripts remain outside the repository at
`/home/mikeastock/.bb/thread-storage/thr_hxa96szkr5/drawing-evidence/baseline-transcript.json`
and
`/home/mikeastock/.bb/thread-storage/thr_hxa96szkr5/drawing-evidence/revised-transcript.json`.
Small final messages are `baseline-output.json` and `revised-output.json`. Durable
copies of task inputs, prompts, outputs, and evaluated skill hashes are in
`paired/{baseline,revised}/`. The revised snapshot predates only a whitespace/
reference-read wording cleanup in step 5; tested behavior and script are identical.
No second attempt or optional pair was launched.

## Live limits

This is explicitly synthetic local fixture replay. No MCP needed or called; no remote API was invented, no construction records written. No actual PDF, OCR engine, graphical drawing interpretation, quantity takeoff, chat-app, or live MCP compatibility was tested. The fresh pair is a narrow behavior check, not a statistical performance claim. Missing-source and quantity-only near-miss pairs were proposed but not authorized in this phase.

## Integration follow-up

The paired checker reads saved `paired/` inputs and outputs. By default it runs
the standalone baseline renderer directly from git `9a62032`, so the original
`/tmp` directories are unnecessary. If that git object is unavailable (for
example, a shallow clone), supply a reconstructed baseline repository root:

```
python evals/reviews/drawing-scope-extraction/check_pair.py --baseline-root /path/to/baseline
DRAWING_BASELINE_ROOT=/path/to/baseline python evals/reviews/drawing-scope-extraction/check_pair.py
```

The baseline root must contain
`skills/drawing-scope-extraction/scripts/scope_list.py` from `9a62032`.
Default git-backed, explicit-root, and environment-root executions each matched
saved `paired-results.json` byte for byte. These replay the saved agent artifacts;
they do not rerun models. Original format weights remain unchanged.
