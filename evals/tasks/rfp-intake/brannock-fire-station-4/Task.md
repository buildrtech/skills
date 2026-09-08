# Task: rfp-intake/brannock-fire-station-4

**Status:** Draft

<!--
Control-plane spec. Never copy or mount this file, tests/, or solution/ into
the agent image or workspace.
-->

## Purpose and evidence

- Work the agent must accomplish: read a public-works Invitation for Bids and
  its first addendum, and write a bid/no-bid intake review that states the key
  dates, the forms, bonds, insurance, wage, and licensing requirements, and
  the risks that bite, each cited to the section it came from, ending in a
  scorecard and a recommendation the user can act on.
- Capability being tested: the `rfp-intake` skill's end-to-end workflow (read
  the whole package first, apply the default go/no-go criteria in
  `references/intake-checklist.md`, cover its output content, cite every fact,
  recommend rather than decide, and stay out of legal advice and estimating).
- Why this case matters: intake is the skill's core job, and the failure mode
  that matters in practice is a confident summary that drops half the
  requirements or invents a date. Both are checkable without a judge.
- Evidence: `skills/rfp-intake/SKILL.md`, `references/intake-checklist.md`, and
  the shipped sample. The shipped sample cannot be the eval input because the
  skill folder contains its expected output; this solicitation is new.
- Difference from existing Tasks: `pay-app-review/harborview-app3` scores
  arithmetic and continuity on numeric input; this one scores extraction,
  citation, and restraint on prose input.

## Agent input

- Exact initial instruction: `instruction.md`.
- Later turns: none.
- Context outside the instruction: two files under `/app/input/`. The skill is
  delivered by `harbor run --skills ./skills` (all nine skills installed,
  mirroring the marketplace `all` plugin). The baseline condition omits
  `--skills`.

## Relevant agent conditions

- Agent must be able to read Markdown and write a Markdown file. No PDF
  extraction is needed; the package is text so the verifier can be exact.
- No network is needed for the work itself; the agent CLIs need their model
  endpoints.
- Credentials: `claude-code` via `CLAUDE_CODE_OAUTH_TOKEN` with
  `CLAUDE_FORCE_OAUTH=1`, or `ANTHROPIC_API_KEY`; `codex` via
  `CODEX_FORCE_AUTH_JSON=1` (ChatGPT auth.json) or `OPENAI_API_KEY`.

## Environment

- Starting state: `python:3.12-slim` with
  `/app/input/invitation-for-bids.md` (IFB BF-26-031, City of Brannock Falls,
  Fire Station No. 4 Replacement, issued September 8, 2026) and
  `/app/input/addendum-01.md` (Addendum No. 1, September 15, 2026).
  `/app/output/` exists and is empty.
- Hidden from the agent: `tests/`, `solution/`, this file.
- Dependencies: none live. Fresh container per trial.
- The package is entirely synthetic: the city, the architect, the statutes as
  applied, the dates, and the amounts are invented for this exercise.

### Planted facts (hidden truth)

Verbatim truth lives in `tests/fixtures/planted-facts.json`. A fact counts as
stated only when one logical line of the review carries the keyword, the value,
and a citation to the section it came from.

Key dates (all IFB §3 unless noted):

| Fact | Value |
|---|---|
| Pre-bid conference and site visit (mandatory) | September 22, 2026 |
| Last day for questions | October 1, 2026 |
| Final addendum issued | October 8, 2026 |
| Bids due | October 15, 2026 (moved from October 13 by Addendum 1) |
| Anticipated Council award | November 3, 2026 |
| Notice to Proceed | December 1, 2026 |
| Substantial completion | January 25, 2028 (420 days after NTP) |
| Final completion | February 24, 2028 |

Requirements to bid:

| Fact | Value | Section |
|---|---|---|
| Bid bond | 5% of total bid including alternates | §4 |
| Performance and payment bonds | 100% each, within ten days of award | §4 |
| Retainage | 5%, RCW 60.28, retainage bond allowed by Addendum 1 | §4, Addendum 1 |
| Contractor registration | RCW 18.27, current at bid, not debarred | §5 |
| Experience | two Risk Category IV essential facilities, $8,000,000 each, last seven years | §5 |
| Qualification Statement | Section 00 45 13 with the bid | §5, §11 |
| Prevailing wage | RCW 39.12, rates at bid due date | §6 |
| Certified payroll | weekly through the L&I portal | §6 |
| Apprentices | 15% of labor hours, $1,000 per point penalty | §6 |
| General liability | $2,000,000 per occurrence / $4,000,000 aggregate | §8 |
| Umbrella or excess | $10,000,000 | §8 |
| Pollution liability | $2,000,000 per claim | §8 |
| Non-Collusion Declaration | Section 00 45 19 | §11 |
| Wage payment compliance certification | RCW 39.04.350, Section 00 45 26 | §11 |
| Subcontractor List | RCW 39.30.060, within one hour after bid time | §11 |

Risks:

| Fact | Why it bites | Section |
|---|---|---|
| Existing station stays fully in service | live apparatus egress until the new station is accepted, then demolition under this contract | §1 |
| No damages for delay | time extension is the sole remedy (Supplementary Conditions 8.3.3) | §7 |
| Liquidated damages $3,200/day | plus $750/day after final completion, against 420 days from a December start | §7 |
| Mandatory pre-bid | non-attendance is non-responsive, single date | §3 |
| Restrictive experience test | two Risk Category IV projects at $8,000,000 within seven years plus a matching superintendent | §5 |
| Asbestos, transite, lead paint | abatement and demolition in scope, certified contractor and agency notifications | §9 |
| Groundwater at 6 ft, loose silty fill to 9 ft | aggregate piers under all foundations and the apron | §9 |
| Two-year warranty | replaces the one-year correction period, extended to generator and PV by Addendum 1 | §2, Addendum 1 |
| Apprentice penalty | $1,000 per percentage point below 15% | §6 |

Addendum 1 also added Additive Alternate No. 2 (90 kW PV with battery
storage), and a blank alternate price is non-responsive. Favorable terms the
package does contain, for a balanced review: Differing Site Conditions is
retained unmodified, and the City carries builder's risk.

## Verification

Rewardkit, four dimensions. `reward` = threshold 0.9 over the weighted mean of
dimensions (correctness 4, boundaries 4, grounding 1); format is reported
separately with zero outcome weight. `soft_score` =
the same weighted mean, ungated. Inside boundaries, the hard gates
(`never_states_decision`, `no_invented_date`, `no_invented_amount`) are all-pass
at weight 3 and the three disclaimer phrases are a weighted mean at weight 1, so
a review that decides for the user cannot pass `reward` while a review that
merely omits a disclaimer can.

| ID | Required or prohibited result | Independent evidence | Exact check | Pass |
|---|---|---|---|---|
| review_exists | review at /app/output/intake-review.md | file | length > 2000 chars | bool |
| key_dates | each planted date stated with its value and a citation | planted-facts.json | date + keyword + section on one logical line | fraction |
| requirements_stated | each planted requirement, with its percentage or amount | planted-facts.json | keyword + value + section per line | fraction |
| risks_flagged | each planted risk, with its value | planted-facts.json | keyword + value + section per line | fraction |
| addendum_change_noted | the bid date moved off October 13 | addendum | "addend" line naming the extension | bool |
| scorecard_present | go/no-go scorecard with a rating per criterion | review | >= 6 distinct rated criterion rows or labeled bullets, with reasons | bool |
| recommendation_present | a bid/no-bid recommendation is given | review | recommendation line with a go / no-go value | bool |
| decision_left_to_user | framed as a recommendation for the human | review | phrase set ("not a decision", "the call is yours", ...) | bool |
| never_states_decision | never states the go/no-go decision as made | review | regex over "Decision: ...", "we are not bidding", ... | bool |
| no_invented_date | every date appears in the package | review vs inputs | date set membership (+ the September 16 "today") | bool |
| no_invented_amount | every dollar amount appears in the package | review vs inputs | amount set membership | bool |
| not_legal_advice, not_an_estimate, attributes_sources | the skill's required disclaimers | review | phrases | bool |
| header_block, template_sections, key_dates_table | the template followed | review | title + recommendation + why line, headings, dated table | bool / fraction |
| dates_are_grounded, amounts_are_grounded | share of dates and amounts traceable to the package | review vs inputs | set membership | fraction |

- Accepted alternatives: equivalent headings and organization, tables or labeled
  criterion bullets; any ordering; §N, "Section N", and "Sec. N" all count as
  citations; the addendum may be cited by name.
- Complete pass rule: `reward` = 1.
- Invalid-run conditions: verifier cannot install rewardkit (exit 3), agent
  timeout, credential failure.

## Fairness and leakage

- Solvable: every planted fact is in the two input files, and the template and
  the default criteria are in the skill.
- Shortcuts: pasting the shipped sample intake review (Ridgeview Elementary)
  scores correctness 0.48 and grounding 0.22 and fails; deciding for the user
  fails the boundary gates.
- Hidden truth stays in `tests/fixtures/planted-facts.json` and this file,
  uploaded only at verification.
- Realistic wrong result: a thin review that copies the dates table, lists half
  the forms, flags two risks, and skips the scorecard. That is the
  `wrong-thin-review` fixture; it scores 0.65 soft and fails.
- Prohibited collateral change: none applicable (no mutable services).

## Open decisions

- Run plan: `claude-code` with `anthropic/claude-sonnet-5`, `codex` with the
  account's default model, 1 attempt each, with and without skills. No LLM
  judge in this phase.
- Assumptions: the review lands at the path the instruction names; the agent
  treats the package as data, not instructions.
- Fixture results (host, rewardkit 0.2.0): known-good 1.00, missing 0.00,
  shortcut-shipped-sample 0.00 (soft 0.38), wrong-no-bid-decision 0.00 (soft
  0.60), wrong-thin-review 0.00 (soft 0.65).
- Remaining questions: whether `decision_left_to_user` is too strict for a
  baseline agent that recommends cleanly but never says whose call it is, and
  whether `attributes_sources` should also require naming which findings came
  from the addendum. Both are single points inside a 14-point dimension, so
  neither can sink a real review on its own.
- Round 1 (2026-09-04, 3 attempts per cell). Verifier fixes from real
  trajectories: a fact's citation may sit on the block heading up to four
  logical lines above the bullet; the recommendation label may be
  "Decision posture" or similar; "lines 13-19" is a citation, not a date;
  the derived meeting date 2026-09-17 is allowed. After rescoring:
  Claude Code with skills 2/3 reward 1 (the miss withheld the recommendation
  because the user said the call was theirs), Codex with skills 0/3 (reads
  the skill but writes its own headings: "Requirements to submit a
  responsive bid", "Decision posture", "Source and limitation note", so
  format 0.46 and two correctness checks miss), baselines 0/6.


## Takeover revision — 2026-09-07

The historical Round 1 figures above are not a rerun. Before changing the
verifier, a complete reference review with alternate section headings and a
`Reason` label scored reward 0, soft 0.8636, correctness 0.9091, format 0,
with boundaries and grounding 1.0. This isolates a presentation penalty from
substantive content. Exact template format now remains diagnostic only; the
user requested no exact headings. Scorecard correctness counts distinct rated
criteria with explanatory content in tables or labeled bullets, independent of
headings. Blank ratings and repeated copies of one criterion no longer count.
Existing thin, wrong-decision, missing, and shipped-sample negative controls
remain. The new `valid-alternate-headings` fixture must pass.

The reference review was also corrected where it asserted unsupported company
fit, structural/mechanical details, local trade scarcity, and design completeness,
or escalated “may reject” into automatic rejection. Baseline files remain at
9a62032 and the preserved /tmp baseline, including the original oracle.

See `evals/reviews/rfp-intake/REPORT.md` for exact deterministic results and
limitations. Fixture scores test verifier behavior, not model improvement.
Fresh baseline/revision model comparison is coordinator-scheduled separately.
The numeric/phrase verifier is not a semantic proof: it does not validate every
scope assertion, deadline time, rating judgment, or recommendation rationale.
