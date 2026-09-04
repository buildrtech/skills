# Task: bid-leveling/millbrook-roofing-07a

**Status:** Draft

<!--
Control-plane spec. Never copy or mount this file, tests/, or solution/ into
the agent image or workspace.
-->

## Purpose and evidence

- Work the agent must accomplish: level three subcontractor bids for one
  roofing package against the package scope sheet, apply the estimator's
  recorded plugs and adjustment, and write the leveled comparison with the
  matrix, the plug summary with sources, and the questions for each bidder.
- Capability being tested: the `bid-leveling` skill's end-to-end workflow
  (read every bid, extract each into the evidence schema, classify rows,
  run `scripts/level_bids.py` with the decisions file, review the leveling
  flags, present the result from `references/comparison-template.md`, and
  never make the award call).
- Why this case matters: the raw low bidder is not the leveled low bidder.
  A comparison built without extraction and plugs ranks Blue Heron first at
  $571,900; the leveled ranking puts Cardinal first at $580,850. The task
  separates leveling from sorting by base bid.
- Evidence: `skills/bid-leveling/SKILL.md`, `references/extraction-schema.md`,
  `references/leveling-model.md`, `references/comparison-template.md`, and
  `scripts/level_bids.py`. The shipped sample cannot be the eval input because
  the skill folder contains its extractions and its expected output; this
  fixture is a new trade, new bidders, and new numbers.
- Difference from existing Tasks: second task in the suite; the first one for
  a skill whose deliverable is produced by a script the agent must run.

## Agent input

- Exact initial instruction: `instruction.md`.
- Later turns: none.
- Context outside the instruction: two files under `/app/input/`. The skill
  is delivered by `harbor run --skills ./skills` (all nine skills installed,
  mirroring the marketplace `all` plugin). The baseline condition omits
  `--skills`.

## Relevant agent conditions

- Agent must be able to run Python 3 (`scripts/level_bids.py` is standard
  library only; `openpyxl` is needed only for the optional `--xlsx` workbook,
  which this task does not ask for) and write a Markdown file.
- No network is needed for the work itself; the agent CLIs need their model
  endpoints.
- Credentials: `claude-code` via `CLAUDE_CODE_OAUTH_TOKEN` with
  `CLAUDE_FORCE_OAUTH=1`, or `ANTHROPIC_API_KEY`; `codex` via
  `CODEX_FORCE_AUTH_JSON=1` (ChatGPT auth.json) or `OPENAI_API_KEY`.

## Environment

- Starting state: `python:3.12-slim-bookworm` with `/app/input/bids.md` (the
  07A scope sheet plus all three bids transcribed as received) and
  `/app/input/estimator-decisions.json` (four plugs and one adjustment, each
  with a source). `/app/output/` exists and is empty.
- Hidden from the agent: `tests/`, `solution/`, this file. In particular the
  three reference extraction JSONs under `tests/fixtures/` and the script
  output run on them are never in the image; the agent has to produce its
  own extractions from the bid text.
- Dependencies: none live. Fresh container per trial.

### Hidden truth

Base bids as submitted: Ironwood $612,400, Blue Heron $571,900,
Cardinal $598,750. Raw ranking: Blue Heron, Cardinal, Ironwood.

Five base-scope gaps, four of them plugged from the decisions file:

| # | Bidder | Scope | Status in the bid | Plug |
|---|---|---|---|---|
| 1 | Blue Heron | Self-adhered vapor retarder (07 26 00) | excluded, "Vapor retarder by others" | $38,600 |
| 2 | Blue Heron | Walkway pads | omitted; the email never mentions them | $4,200 |
| 3 | Blue Heron | 20-year NDL system warranty | unknown; "standard 20-year membrane warranty" is not the NDL system warranty in 07 54 23 | none: unresolved |
| 4 | Cardinal | Hoisting | excluded, bid form row 11 reads "By GC" | $9,500 |
| 5 | Ironwood | Roof hatch (07 72 33) | excluded, "Roof hatch by others" | $6,850 |

One adjustment: Cardinal −$27,400 to remove metal wall panels at the
mechanical screen (07 42 13), which the scope sheet puts in package 07B and
Cardinal priced inside its total at bid form row 12.

Leveled totals (base bid + plugs + adjustments):

| Bidder | Base bid | Plugs | Adjustments | Leveled total |
|---|---|---|---|---|
| Ironwood Roofing Systems, Inc. | $612,400 | $6,850 | none | $619,250 |
| Blue Heron Roofing & Sheet Metal LLC | $571,900 | $42,800 | none | $614,700 (incomplete) |
| Cardinal Commercial Roofing Co. | $598,750 | $9,500 | −$27,400 | $580,850 |

Leveled ranking: Cardinal $580,850 (lowest complete), Blue Heron $614,700
(incomplete, one unresolved gap), Ironwood $619,250. The raw low bidder is
third once the vapor retarder and the walkway pads are carried.

Planted errors the comparison has to flag:

- **Bid form footing.** Cardinal's rows 1 through 13 sum to $600,550 against
  a stated total of $598,750, a difference of $1,800. `level_bids.py` raises
  this as a leveling check; the bid form in `bids.md` contains the rows that
  produce it.
- **Bond bases.** Cardinal carries an $8,900 performance and payment bond
  inside its total; Ironwood excludes the bond and would add 1.5% if
  required; Blue Heron says "Bond not included." Nothing in the leveled
  totals reflects a bond decision, and the priced qualifications table has to
  say so rather than quietly normalising it.

Secondary traps, not separately scored: Blue Heron's silence on walkway pads
is a gap and not an inclusion; Blue Heron's quote is an email body with no
attachment; Cardinal's voluntary −$31,000 mechanically attached membrane
deduct is not the specified system and belongs nowhere near a leveled total;
Alternate 1 is priced by all three and is never added to a total.

## Verification

Rewardkit, four dimensions. `reward` = threshold 0.9 over the weighted mean
of dimensions (correctness 4, boundaries 4, format 1, grounding 1).
`soft_score` = the same weighted mean without the threshold. Inside
boundaries, the hard gates (`never_awards`, `no_invented_amounts`) are
all-pass at weight 3 and the three Basis-line disclaimers are a weighted mean
at weight 1, so a comparison that names a winner cannot pass `reward` but one
that merely drops a Basis line can.

Truth comes from `tests/fixtures/script-output.md`, which is
`scripts/level_bids.py` run on the three hidden reference extractions and the
agent-visible decisions file. It was regenerated and diffed against the
committed copy while writing this task.

| ID | Required or prohibited result | Independent evidence | Exact check | Pass |
|---|---|---|---|---|
| comparison_exists | comparison at /app/output/leveled-comparison.md | file | length > 2000 chars | bool |
| leveled_totals | each bidder's leveled total within $1 of the fixture | comparison vs fixture | a line naming the bidder carries a number within $1 | fraction |
| all_leveled_totals_match | all three match | same | all three | bool |
| leveled_ranking | leads with the lowest complete leveled total, never calls the raw low bidder low | comparison | headline names Cardinal and $580,850; Blue Heron carries incomplete or unresolved | bool |
| plugs_and_adjustment | each plug and the adjustment named with scope, bidder, and amount | comparison vs decisions file | line-scoped co-occurrence | fraction |
| gaps_named | each of the five base-scope gaps named with its bidder and status | comparison vs fixture | line-scoped co-occurrence | fraction |
| planted_flags | Cardinal's $1,800 footing error and the mismatched bond bases | comparison vs fixture | amount and phrase co-occurrence | fraction |
| never_awards | no award recommendation | comparison | regex, negation-aware | bool |
| no_invented_amounts | no dollar figure absent from the inputs or the leveling arithmetic | comparison vs inputs + fixture | set membership incl. pairwise sums and differences | bool |
| disclaims_* | not an award recommendation; not a scope review; plugs are estimator decisions | comparison | phrases | bool |
| header_block, template_sections, matrix_shape | template followed | comparison | title, headline, section headings, matrix columns and rows | bool / fraction |
| amounts_are_grounded | share of dollar amounts tracing to inputs or leveling arithmetic | comparison vs inputs + fixture | set membership | fraction |

- Accepted alternatives: any wording; any table layout as long as the
  headings exist and the matrix keeps one column per bidder; any ordering of
  gaps, plugs, and questions; the bidder columns in any order.
- Complete pass rule: `reward` = 1.
- Invalid-run conditions: verifier cannot install rewardkit (exit 3), agent
  timeout, credential failure.

## Fairness and leakage

- Solvable: every bid fact is in `bids.md`, every plug and its source is in
  `estimator-decisions.json`, the extraction schema and the leveling
  arithmetic are in the skill, and the script is in the skill.
- Shortcuts: pasting the shipped sample comparison (a drywall package with
  different bidders and numbers) fails correctness, grounding, and the
  invented-amount gate; ranking by base bid fails correctness and format;
  naming a winner fails the boundaries gate.
- Hidden truth stays in `tests/fixtures/` and this file, uploaded only at
  verification.
- Realistic wrong result: a comparison that reads Blue Heron's silence on
  walkway pads as an inclusion, so its leveled total lands at $610,500
  instead of $614,700 (`wrong-gap-missed`, scores 0.85 against the 0.9
  threshold), or one that ranks the bids as submitted (`wrong-raw-ranking`).
- Prohibited collateral change: none applicable (no mutable services).

## Open decisions

- Run plan: `claude-code` with `anthropic/claude-sonnet-5`, `codex` with the
  account's default model, 1 attempt each, with and without skills. No LLM
  judge in this phase.
- Assumptions: the comparison lands at the path the instruction names; the
  agent produces its own extractions rather than being handed them.
- Remaining questions: `wrong-gap-missed` fails by 0.05, the thinnest margin
  of the six fixture cases, because format, grounding, and boundaries are all
  legitimately clean on it. If a model trial lands there, tighten the
  correctness weights rather than the threshold.
- Round 1 (2026-09-04, 3 attempts per cell). One verifier fix: the
  invented-amount gate now allows three-term arithmetic on input figures
  (a bid form's rows 1-10 stated as total minus two excluded rows was
  rejected as invented). After rescoring: with skills 6/6 reward 1 in both
  lanes; baselines 0/6 (Claude 0.73 and Codex 0.83 correctness with no
  template and one Claude baseline awarding the package).
