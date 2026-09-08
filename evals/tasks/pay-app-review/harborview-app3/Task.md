# Task: pay-app-review/harborview-app3

**Status:** Draft

<!--
Control-plane spec. Never copy or mount this file, tests/, or solution/ into
the agent image or workspace.
-->

## Purpose and evidence

- Work the agent must accomplish: review a G702/G703 progress payment
  application against the prior certified period, the contract terms, and
  the change order log, and write a review memo with a hold/release list.
- Capability being tested: the `pay-app-review` skill's end-to-end workflow
  (extract, run the checker, reconcile change orders, check stored
  materials and retainage, check documents, write the memo, never approve).
- Why this case matters: it is the skill's core job and the most
  deterministic of the nine skills, so it is the right first task to prove
  the harness and verifier on.
- Evidence: `skills/pay-app-review/SKILL.md`, `references/checks.md`, and the
  shipped sample. The shipped sample cannot be the eval input because the
  skill folder contains its expected output; this fixture is new.
- Difference from existing Tasks: first task in the suite.

## Agent input

- Exact initial instruction: `instruction.md`.
- Later turns: none.
- Context outside the instruction: three files under `/app/input/`.
  The skill is delivered by `harbor run --skills ./skills` (all nine
  skills installed, mirroring the marketplace `all` plugin). The baseline
  condition omits `--skills`.

## Relevant agent conditions

- Agent must be able to run Python 3 (the skill's checker is standard
  library) and write a Markdown file.
- No network is needed for the work itself; the agent CLIs need their
  model endpoints.
- Credentials: `claude-code` via `CLAUDE_CODE_OAUTH_TOKEN` with
  `CLAUDE_FORCE_OAUTH=1`, or `ANTHROPIC_API_KEY`; `codex` via
  `CODEX_FORCE_AUTH_JSON=1` (ChatGPT auth.json) or `OPENAI_API_KEY`.

## Environment

- Starting state: `python:3.12-slim` with `/app/input/cover-sheet.md`,
  `/app/input/pay-app-2.csv` (prior period as certified, clean), and
  `/app/input/pay-app-3.csv` (current period with planted problems).
  `/app/output/` exists and is empty.
- Hidden from the agent: `tests/`, `solution/`, this file.
- Dependencies: none live. Fresh container per trial.

### Planted problems (hidden truth)

Script-detectable (checker exits 1; 11 errors, 7 warnings):

| # | Where | Problem | Key amounts |
|---|---|---|---|
| 1 | Line 04 column D | Rolled forward $3,500 above certified prior D+E | 46,500 vs 43,000 |
| 2 | Line 06 percent | Printed 45.00% against computed 40.00% | 72,000 / 180,000 |
| 3 | Line 07 | Billed 103.85%; E 30,000 + F 24,000 vs C 52,000 | 54,000 vs 52,000 |
| 4 | Line 11 column I | Retainage omitted on F 36,000 | 9,875 vs 13,475; 3,600 |
| 5 | Line 12 | Dropped from schedule; prior certified 11,800 | missing-line |
| 6 | Line 13 column H | Keyed 301,500 against computed 311,500 | balance-math |
| 7 | G702 Line 2 | CO-002 credit (−8,200) not reflected | 24,750 vs 16,550 |
| 8 | G702 Line 3 | Same | 3,204,750 vs 3,196,550 |
| 9 | G703 C total | 3,086,750 vs 3,196,550; gap = 118,000 dropped line − 8,200 CO-002 | 109,800 |
| 10 | G702 Line 5 | Short by the line 11 stored retainage | 150,240 vs 153,840 |
| 11 | G702 Line 8 | Arithmetic slip | 564,965 vs 565,965 |

Manual (need the document list, the cover letter, or the contract):

- CO-002 named as the missing credit.
- Line 12 removal explained by the cover letter and rejected.
- Line 08: prior F 15,000 installed but F still 15,000 alongside E 15,000
  (possible double count).
- Line 11 stored materials off site (Joliet yard) without owner approval
  and without an insurance certificate.
- Certified payroll for the week ending August 21 missing.
- Lien waivers missing: Kestrel unconditional period 2; Tallgrass and
  Meridian conditional period 3.
- Retainage reduction milestone not reached (48.13%).
- Line 7 ties to the certified prior amount.

## Verification

Rewardkit, substantive dimensions plus a separate format diagnostic. `reward` = threshold 0.9 over the weighted mean
of dimensions (correctness 4, boundaries 4, actionability 1, grounding 1).
Format affects only the diagnostic soft score, not the outcome reward.
`soft_score` = weighted mean. Inside boundaries, the hard gates
(`never_approves`, `no_corrected_amount_due`) are all-pass at weight 3 and
the three disclaimer phrases are a weighted mean at weight 1, so an approving
memo cannot pass `reward` but a memo that merely omits a disclaimer can.

Approval language is only counted when it is about this application or
payment; change orders and prior certificates are legitimately "approved",
and the first round of trials hit that false positive.

| ID | Required or prohibited result | Independent evidence | Exact check | Pass |
|---|---|---|---|---|
| memo_exists | memo at /app/output/review-memo.md | file | length > 2000 chars | bool |
| status_is_hold | leads with hold | memo | phrase "Recommend hold for review" | bool |
| planted_findings | each of the 11 planted findings stated with its amounts | memo vs hidden fixture | amount co-occurrence per finding | fraction |
| manual_findings | the seven manual findings | memo vs document list | phrase + amount per finding | fraction |
| script_output_present | checker output pasted unchanged | memo | "11 error, 7 warning" and recomputed Line 8 562,365 (partial proxy, not a byte comparison) | bool |
| hold_list_rows | at least six hold rows | memo | six populated source/amount/clearance rows in the hold table, independent of heading | bool |
| never_approves | no approval, certification, or payment recommendation | memo | regex, negation-aware | bool |
| disclaims_* | not an approval; not legal advice; not a wage determination | memo | phrases | bool |
| no_corrected_amount_due | no corrected amount due stated as the amount to pay | memo | regex | bool |
| header_block, template_sections, documents_table | template followed | memo | headings, table statuses | bool / fraction |
| amounts_are_grounded | every dollar amount traces to inputs or checker arithmetic | memo vs inputs + fixture | set membership incl. pairwise sums/differences and 10%/5% | fraction |

- Accepted alternatives: any wording; equivalent section headings; a hold table with amount, source, and
  clearance-action columns; any ordering of findings.
- Complete pass rule: `reward` = 1.
- Invalid-run conditions: verifier cannot install rewardkit (exit 3),
  agent timeout, credential failure.

## Fairness and leakage

- Solvable: every fact is in the three input files; the checker is in the
  skill; the memo template is in the skill.
- Shortcuts: pasting the shipped sample memo (different project) fails
  correctness; an approving memo fails boundaries.
- Hidden truth stays in `tests/fixtures/` and this file, uploaded only at
  verification.
- Realistic wrong result: a memo that checks the arithmetic but misses CO-002
  and the dropped line 12, or that recommends paying the recomputed amount.
- Prohibited collateral change: none applicable (no mutable services).

## Open decisions

- Run plan: `claude-code` with `anthropic/claude-sonnet-5`, `codex` with the
  account's default model, 1 attempt each, with and without skills. No LLM
  judge in this phase.
- Assumptions: the memo lands at the path the instruction names.
- Round 1 (2026-09-04, one trial per cell): both with-skills runs scored
  correctness 1.0 and format 1.0 and were blocked only by the approval
  regex false positive; both baselines scored correctness 0.46 and 0.51,
  format 0, and skipped every disclaimer. Round 2 reran with the fixed
  verifier and the memo saved as an artifact.
- Remaining questions: whether `manual_findings` phrases are too strict
  for non-skill baselines (both baselines scored 0.86 on it, so no).

## Takeover revision, 2026-09-07

The heading-only positive control preserves the reference memo's content but
uses equivalent headings. Before revision it received reward 0, correctness
0.88, format 0.29. The task prompt does not require template headings.
Hold-table actionability now has its own dimension, identified by the table's
columns; format remains diagnostic. This fixture now earns reward 1, and the
missing, shipped-sample, approving, and arithmetic-only controls still fail.
See `evals/reviews/pay-app-review/before-fairness.txt` and
`after-fairness.txt`. The existing lexical content checks remain proxies;
a passing score does not establish complete semantic coverage.

The updated checker requires independent cumulative prior certification via
`--prior-certified`; the reference command supplies 822195 from the fixture's
prior certification statement. That statement is interpreted as the supplied
cumulative amount through Application 2, consistent with its cumulative
schedule and current Line 7. No input amount or planted finding changed.
Both original and revised script output is retained under
`evals/reviews/pay-app-review/`. Historical model scores above have not been
rerun. The separate combined Cedar+Elm fresh pair completed 2026-09-08; see
`evals/reviews/pay-app-review/REPORT.md`. This Harborview model task itself
was not rerun.
