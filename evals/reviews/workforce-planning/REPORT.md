# Workforce planning takeover review

Version **1.1.0**: 12 deterministic tests pass. Fresh Claude pair completed:
seven shared factual/boundary controls tie; revision resolves baseline's
contradictory unfilled-demand action. No post-hoc composite score is assigned.

## Evidence read and fairness review

Read the complete seven original skill files (SKILL.md, three references,
example prompts, and both samples), takeover audit and HANDOFF, local
writing-great-skills and skill-creator guides. No workforce task directory,
Task.md, verifier, historical outcome score, script, or fixture runner existed
at baseline. Existing shared check_fixtures.py was inspected: it requires a
Harbor/rewardkit task with fixtures, which this skill did not have. No existing
workforce Harbor fixture check could be run or honestly reported as passing.
The new checks are standard-library local tests, explicitly synthetic replay.

Authoring sources consulted:
- https://agentskills.io/specification
- https://agentskills.io/skill-creation/best-practices
- https://agentskills.io/skill-creation/evaluating-skills

Applied conditional reference reads, discovered rather than illustrative API
contracts, checkable completion, scripts for fragile arithmetic, and a fresh
paired evaluation proposal. Output headings are flexible. New Task.md scores
substance separately from formatting and retains substantive negative controls.
The sample table parser is only a deterministic smoke checker for the shipped
sample; it is explicitly not a model-output grader. A future agent's equivalent
prose or alternative valid proposal must not fail merely for changing headings.

## Findings and revisions

1. **Incorrect bench and capacity example.** Baseline output claimed Dana had
   a continuous 225-day bench run despite seven days of time off. Supplied
   periods establish runs of 86 and 132 days separated by seven unavailable
   days. Revised sample and helper preserve both runs. Missing periods remain
   unknown, adjacent known zero periods merge, and time off always breaks bench.
2. **Lost demand in staffing proposal.** Baseline shortened the Ridgeview
   unfilled row and reduced Lakeside coverage, retaining only 50% of each
   original 100% need for 47 days. Revised Option A has six actions, including
   two explicit 50% residual demand rows. Existing March time-off conflict is
   prominently retained; the proposal does not claim complete staffing.
3. **Unsupported live API assurances.** Removed claims of exactly two tools,
   guaranteed scope names, account rollout state, and plausible callable
   snake_case examples. Reference operation names remain historical lookup
   hints only. Actual discovery determines tools, arguments, pagination and
   date semantics. Missing connection permits an explicitly supplied snapshot,
   with its limitations stated, and never fabricated live data.
4. **Ambiguous weighting and dates.** Calendar request window now remains
   Nov 1–Aug 1, separate from Nov 2 demand start. Periods are clipped; team
   contributions cap per period before duration weighting. Headcount exclusion,
   incomplete timelines, certificate issuance/expiration, and unknown expiration
   semantics are explicit. Sample bench wording no longer extends outside the
   observed window solely because a past assignment ended.
5. **Write verification.** Retain specific-plan authorization; honor prior
   authorization of that same plan. Re-read eligibility and affected records
   before execution; changed plans require renewed authorization. Partial errors
   and timeouts require state reconciliation, not blind retries or claimed undo.
6. **Resources and catalog.** Main skill routes to references and optional local
   helper; templates no longer contain a misleading four-row proposal. Added
   human-facing summary without replacing the agent-trigger description.

## Deterministic commands and results

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evals/tasks/workforce-planning/period-replay -p 'test_*.py' -v`
  — **12 passed**, including actual script subprocess, leap year, clipping,
  adjacent runs, time-off exclusion, unknown gaps, period capping, invalid
  values, overlap rejection, sample arithmetic and demand conservation.
- `python3 skills/workforce-planning/scripts/analyze_periods.py evals/tasks/workforce-planning/period-replay/sample-dana.json`
  — exit 0, two bench runs of **86 and 132 days**; seven days unavailable.
  Result preserved in `sample-replay.json`.
- Applied `check_sample.coverage_gaps` to preserved baseline and revised input/
  output samples — baseline has **two 47-day, 50% demand losses**; revised has
  **zero**. Removing the revised residual rows is a negative control and fails
  with those same two losses. `comparison.json` preserves findings and SHA-256
  hashes of baseline/revised skill files; baseline remains untouched.
- `UV_CACHE_DIR=/tmp/workforce-takeover-uv uv run --with pyyaml python tools/validate_skills.py skills/workforce-planning`
  — **1 skill valid**. Initial direct Python attempt lacked PyYAML; initial uv
  attempt could not write its default cache. A task-specific temporary cache
  resolved this without modifying shared dependencies or requiring approval.
- `git diff --check -- skills/workforce-planning evals/tasks/workforce-planning evals/reviews/workforce-planning`
  — exit 0, no whitespace errors.

Logs: `test-results.txt`, `validation.txt`, `sample-replay.json`, and
`comparison.json`. This proves local arithmetic and sample improvements, not
that a fresh model follows the instructions better.

## Fresh paired evaluation

Baseline `thr_mvsexhgv4c` and revised `thr_3ccumvyqzz` completed sequentially,
one attempt each, using `claude-opus-5[1m]`, medium/default/auto. Both correctly
handle the 60-day window, Aster's 30/29-day split, Blair's unknown February,
Casey's 100% uncapped/50% capped utilization, certification limits, no eligible
whole-window candidate and no writes. Both propose the same valid partial
coverage intervals and compute the residual table correctly.

The baseline then explicitly instructs keeping the unfilled d_01 open at 100%
for the entire window while adding three filled assignments. That conflicts
with its own correct residual table and would double-count demand if executed.
Revision says reduce/split d_01 to the listed residual, conserving the original
requirement. This is a concrete action-level improvement, not a claim that the
baseline omitted all residual information. The frozen Task.md asked for
conservation but prescribed no numeric composite; we retain dimension findings
instead of inventing a post-hoc score.

Baseline also says "two" days while naming a 30-day interval and reports 40
equivalent covered days where its correct 3,800 percent-days imply 38 (63.33%).
Revision omits that erroneous total, but has imprecise "no assignment" wording
in the Jan31 row despite correctly retaining Blair's 50% coverage. Neither
answer is presented as flawless.

Revision ran the supplied `analyze_periods.py` for three normalized employees,
exit 0. Both completed traces show only assigned local reads/output writes;
input/skill hashes are unchanged. `claude-pair/RESULTS.json` retains facts,
model/settings, timing, hashes and exact full trace paths. Bounded output copies
are alongside it; full transcripts remain in thread storage. This authorized
Claude lane followed the Codex provider limit; no cross-provider comparison.

## Limits and retained evidence

The coordinator graded both answers; this is not blind human review or OS-level
read isolation. Runtime skill descriptions remain injected. No live Buildr MCP,
OAuth, discovery, schemas, permissions, pagination, utilization semantics or
mutations were tested. Missing-connection and hiring near-miss fresh cases,
chat-app behavior and full Harbor integration remain unrun. The offline helper
is arithmetic, not a remote client or complete eligibility/mutation engine.

The seven original files remain byte-identical to git `9a62032`; `comparison.json`
preserves baseline/revised hashes and sample defects. Reusable tests, prompts,
hidden rubric and small logs are committed evidence; caches and full traces
remain outside the repo. No production or global skill writes occurred.
