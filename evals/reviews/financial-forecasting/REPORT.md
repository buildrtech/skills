# Financial forecasting takeover review

Version **1.1.0**: six arithmetic/CLI tests pass; fresh Claude pair
**8/8 → 8/8, a tie** on the frozen rubric. Both block the invalid June close.
Revised uses the bundled calculator. Unsupported extra commentary remains in
both outputs, described below; no broad quality improvement is claimed.

## Evidence and findings

Read takeover audit/HANDOFF, all eight original skill files, both requested
local authoring skills, and official authoring/evaluation guidance. No existing
`evals/tasks/financial-forecasting` task, verifier, historical outcome trace, or
script existed. The sample input does not supply the numbers in its companion
output; it is an illustrative demonstration, not a reproducible account fixture.
This limitation is now explicit. No heading optimization or grader relaxation
was necessary. New tests use independent numeric expectations and no headings.
Bid reconciliation, RFP, PDF, and RFI oracle work belong to other skill owners.

Concrete baseline defects and revisions:

- Read-only reviews required write scopes and asserted exactly two tools plus
  an exhaustive operation list. Read access now suffices; documented operation
  names are candidates requiring current discovery/schema verification. Missing
  connection and explicit offline export/fixture paths are distinct.
- Closing example used ambiguous monthly amounts despite the cumulative model.
  Cumulative basis, units, source mapping and missing actuals are now explicit.
  Exact prior approval is respected; state is re-read before mutation and each
  write verified before continuing. Uncertain writes must not be blindly retried.
- Historical margin could reuse today's contract at both closes. Added as-of
  contract requirement and a reconciled contract-first bridge convention.
- Undefined denominators, cost above EAC, snapshot summing, mixed portfolio
  actuals and double probability weighting lacked guidance. Added explicit
  unavailable-value and reconciliation rules plus a local Decimal calculator.
- Template marked prior-close estimated completion margin actual. Corrected it.
  Portfolio provenance no longer requires fictitious project/period ids. Samples
  no longer assert mobilization or future billing behavior as established causes.

## Deterministic verification

Commands run from the worktree root:

- `python3 -m unittest discover -s evals/tasks/financial-forecasting/offline-health -v`
  — PASS, six tests. Preserved in `test-results.txt`. Actual CLI yields 45%
  completion, 16% margin, $1,125,000 earned and $45,000 underbilling on the new
  synthetic snapshot. Existing Harbor sample yields 60%, 7%, $310,000 overbilling.
  Tests also cover zero/negative EAC, zero contract, uncapped 105% completion,
  missing/nonfinite/boolean amounts, and missing ids.
- `python3 skills/financial-forecasting/scripts/forecast_math.py evals/tasks/financial-forecasting/offline-health/input.json`
  — PASS; preserved `offline-result.json`. This is synthetic fixture replay,
  not an MCP emulator or account result. Wrong cents conversion, inverted billing
  sign, silently zero-filled missing values, and capped completion fail the
  independent expected-value assertions (substantive negative cases).
- Default `python3 tools/validate_skills.py --help` failed import: PyYAML absent.
  Initial uv attempt failed because default cache was read-only. Retried with
  `UV_CACHE_DIR=/tmp/forecasting-uv-cache uv run --with pyyaml python tools/validate_skills.py skills/financial-forecasting`
  — PASS: all 1 skills valid. No shared dependency files changed.
- `git diff --check -- skills/financial-forecasting evals/tasks/financial-forecasting evals/reviews/financial-forecasting`
  — PASS.

`comparison.json` preserves SHA256 hashes for every original/revised skill file
and checks the baseline execution copy against git 9a62032. Original files remain
available in git and `/tmp/skills-takeover-baseline-9a62032`. The new calculator
has no baseline script equivalent; deterministic tests alone do not demonstrate
agent behavior improvement.

## Fresh paired evaluation and limits

Baseline `thr_q9puj7bmfm` and revised `thr_yjs3rjb5es` completed sequentially
with `claude-opus-5[1m]`, medium/default/auto, one attempt each. This authorized
Claude lane followed the Codex provider limit; no cross-provider comparison.
Both pass all eight checks in the frozen `paired-rubric.md`: contract $3.6m,
cumulative cost $1.44m and billed $1.7m, 50% completion/$1.8m earned, 20% margin,
$100k underbilling, actual/estimate labels, and missing-May/cumulative blockers.
Assigned file hashes are unchanged. Completed command traces stay within the
lane and show no remote calls or writes; revision runs `forecast_math.py` exit 0.

Outside the frozen rubric, baseline claims performed pending-CO work would
understate both completion and margin. That direction is unsupported without
cost/EAC treatment. Revision correctly labels a fixed-EAC sensitivity, but
calls no added cost "most likely" wrong without evidence and overstates
underbilling as a cash rather than margin problem. These remain quality limits;
we did not retrofit the rubric to manufacture a win or claim perfect grounding.

`claude-pair/RESULTS.json` records per-check scores, execution settings/timing,
output hashes and exact full transcript paths. Bounded answers and pre-run
input/skill hashes are alongside it. Full traces remain in thread storage.
Context isolation is not OS read denial; runtime skill descriptions were
injected. The same coordinator graded both answers, not a blind human panel.

Near-miss, historical-bridge fresh cases, trigger rates and chat-app behavior
remain unrun. Discovery, real API schemas/units, OAuth, pagination and mutation
sequencing are not live-tested. The offline script is real local arithmetic,
not an MCP emulator. Baseline file hashes remain in `comparison.json` and git
`9a62032`; no remote API was invented or production state changed.

Authoring applied the official Agent Skills specification, authoring and
evaluation guidance, plus local writing-great-skills and skill-creator:
conditional references, observed defects, deterministic fragile arithmetic,
and paired unfamiliar outcomes separate from shipped sample smoke checks.
