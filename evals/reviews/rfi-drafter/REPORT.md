# RFI drafter takeover review — 2026-09-07

Version **1.1.0**: four regression tests and nine fixture controls pass. Fresh
Codex pair **8/8 → 8/8, a tie**; missed-date preservation differs qualitatively.

## Scope and evidence

Owned only skills/rfi-drafter/, evals/tasks/rfi-drafter/, and this review
folder. The worker made no shared tooling/catalog changes, live data access, or
production writes. Read the takeover audit/handoff, all original skill and
RFI task files, and the complete PR-review JSON (six review threads); the
RFI review specifically concerns reference-rfi-023.md line 80.
Baseline remains git 9a62032 and /tmp/skills-takeover-baseline-9a62032.

Applied the local writing-great-skills and BB skill-creator guidance, plus
[official specification](https://agentskills.io/specification),
[authoring guidance](https://agentskills.io/skill-creation/best-practices), and
[evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills):
keep scope coherent, route date detail to its reference, make completion
checkable, and compare actual unfamiliar behavior with the prior version.

## Findings and revisions

- **Valid oracle defect:** spec 2.6.C makes 3% air conditional on both interior
  location and hard-troweled finish. Neither is established for Area B. The
  old oracle unconditionally proposed that maximum and rejected M-3 on air.
  Revised oracle preserves 4,000 psi / 0.45, requests applicability confirmation,
  and explains why returned wall mix M-3 still needs slab suitability review.
  If the engineer overrides strength, w/cm also needs resolution. The skill
  now explicitly checks applicability and supplied precedence rules.
- **Verifier fairness, before heading optimization:** a byte-preserved original
  reference with only two headings and the request opener changed received
  reward 0. `baseline-equivalence.txt` preserves the rejection. The parser now
  accepts Clarification requested / Proposed resolution and Could you confirm.
  Format scoring remains independent and unchanged. No regex claims to prove
  engineering applicability; that remains a semantic review requirement.
- Added equivalent-heading withheld-resolution and Please-proceed controls;
  retained every original negative fixture unchanged. The equivalent positive
  deliberately retains the old oracle text to isolate the parser comparison;
  its pass is **not** evidence that the old air-content claim is correct.
- **Date defect:** removed silent clamping to today. Preserve requested dates,
  use project/as-of context, show missed deadlines and day-basis assumptions,
  and flag turnaround mismatch. Optional missing routing/dates use placeholders.
- **Example defect:** removed unconfirmed no-impact claim from writing-rules.
  The demonstration now frames relocation as a proposal, identifies unknown
  offset clearance, states the weekday-calendar assumption, and labels its log
  a draft for issue. Its original input stays unchanged.
- Added body/log consistency completion check, revision trigger, version 1.1.0,
  and coordinator-requested human-facing metadata.summary (under 200 chars).

## Deterministic verification

Commands run from repository root:

```sh
UV_CACHE_DIR=/tmp/rfi-uv-cache UV_TOOL_DIR=/tmp/rfi-uv-tools python /tmp/skills-takeover-baseline-9a62032/evals/scripts/check_fixtures.py /tmp/skills-takeover-baseline-9a62032/evals/tasks/rfi-drafter/sable-creek-rfi-023
UV_CACHE_DIR=/tmp/rfi-uv-cache UV_TOOL_DIR=/tmp/rfi-uv-tools python evals/scripts/check_fixtures.py evals/tasks/rfi-drafter/sable-creek-rfi-023
python evals/reviews/rfi-drafter/test_regressions.py
python tools/validate_skills.py skills/rfi-drafter
git diff --check -- skills/rfi-drafter evals/tasks/rfi-drafter evals/reviews/rfi-drafter
```

- Revised fixture runner: **9/9 expected results**, including known-good and
  equivalent positive. Existing missing, sample shortcut, directive,
  invented-source, withheld-resolution controls all reject. Detailed scores:
  revised-fixtures.txt. Equivalent correctness improves 0.77 → 1.00; format
  stays 0.91; reward improves 0 → 1. This measures grading fairness.
- Parser boundaries, quoted source dates, and sample date/log arithmetic: **4 tests pass**; see
  regressions.txt. This executes actual helpers, without mocking rewardkit.
- Skill validator passes; see validation.txt. Scoped diff whitespace check passes.
- Baseline original fixture runner: **6/6 expected results**; baseline-fixtures.txt.
- Source-date parsing also missed October 19 across quoted Markdown lines,
  penalizing the known-good oracle grounding (0.94). Removing blockquote
  markers before date extraction restores grounding to 1.00; a wrapped-date
  test includes a different-date negative assertion. No expected date was
  inserted into the allowed set.
- Initial uv invocation failed on read-only ~/.local/share/uv/tools; rerun with
  both cache and tool directories under /tmp succeeded. No global installation.

## Fresh paired evaluation

Coordinator authorized one pair after deterministic work. Frozen rubric is
paired-rubric.md. Agent environments contain only assigned skill and identical
unfamiliar synthetic input at /tmp/rfi-paired-thr-tvachgvz9u/{baseline,revised}.
Each runs one attempt, sequentially, with explicit project/environment and the
same default model. No optional second pair was run.

- Baseline: thr_f893tchs7j, environment env_qxrpzv9g2m.
- Revised: thr_qwvyjmi3cd, environment env_zsuqexnjb7.
- Both execution records confirm Codex / gpt-6-astra / medium / default tier.
- Both read only input.md, assigned SKILL.md, writing-rules and rfi-template;
  neither read the sample answer, sibling lane or hidden rubric. Each wrote
  output/rfi.md. Completed tool-call transcripts show no remote calls, issuing,
  source edits or worker spawns. Assigned skill trees still match their sources.
- Frozen 8-point rubric: **baseline 8/8, revised 8/8**. Both ground strength
  and w/cm, propose the supported resolution, preserve conditional air,
  identify the missed November 5 date, calculate November 19 turnaround,
  complete placeholders/log, and refrain from external actions. Criterion 4
  specifically forbids *silent* clamping: baseline explicitly explains its
  November 9 replacement, so it retains credit. The rubric was not tightened
  after observing the result.
- Qualitative difference: baseline sets header/log response-needed-by to
  November 9 (expedited) without user agreement. Revised retains November 5
  as missed in both and leaves revised placement/expedited arrangements for
  agreement. This is the intended date behavior, but the one-pair score is a
  tie, not evidence of a broad measurable output gain. Both already handled
  conditional air correctly; the oracle correction fixes test truth, not a
  demonstrated model failure in this pair.
- Saved input and both outputs: paired-input.md, paired-baseline-rfi.md,
  paired-revised-rfi.md. Exact execution configuration, commands, artifact
  hashes and complete transcript paths: paired-execution.json. Full transcripts
  remain in /tmp/rfi-paired-thr-tvachgvz9u/{baseline,revised}-transcript.json.
- Evaluation slot released to coordinator immediately after the revised run
  became idle. No extra evaluation runs.

## Limits

This is a neutral drafting skill: no MCP is needed or exercised. All supplied
construction examples are explicitly synthetic fixture replay, not real project
validation. No PDF renderer belongs to this skill, so PDF/theme and bid/RFP
changes remain with their owners. No broad/heavy eval matrix was started.
Historical six with-skill passes in Task.md are prior evidence, not current
reruns. Regex checks remain limited: token presence cannot establish conditional
applicability, engineering suitability, or all possible prose equivalents.
