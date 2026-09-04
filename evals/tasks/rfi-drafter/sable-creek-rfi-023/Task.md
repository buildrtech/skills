# Task: rfi-drafter/sable-creek-rfi-023

**Status:** Draft

<!--
Control-plane spec. Never copy or mount this file, tests/, or solution/ into
the agent image or workspace.
-->

## Purpose and evidence

- Work the agent must accomplish: draft an RFI to the architect from a
  drawing/specification conflict on slab-on-grade concrete strength, citing
  only the sheets, details, and spec paragraphs supplied, proposing the
  resolution the documents support, and producing the RFI log row.
- Capability being tested: the `rfi-drafter` skill's workflow (read
  everything, state the conflict with both sources, ask rather than direct,
  propose only what the documents support, flag turnaround, produce the log
  row).
- Why this case matters: a 500 psi strength conflict with a mix already
  returned "No Exceptions Taken" is a common, expensive real-world RFI; the
  temptation is to tell the sub to pour or to tell the engineer to revise.
- Evidence: `skills/rfi-drafter/SKILL.md`, `references/rfi-template.md`,
  `references/writing-rules.md`. The shipped sample cannot be the eval input
  because the skill folder contains its expected output; this fixture is new.
- Difference from existing Tasks: document drafting rather than review;
  the boundary is "ask, do not direct".

## Agent input

- Exact initial instruction: `instruction.md`.
- Later turns: none.
- Context outside the instruction: four files under `/app/input/`
  (`request.md`, `drawing-excerpts.md`, `spec-03-30-00.md`,
  `submittal-03-30-00-02.md`). Skills delivered by `--skills ./skills`;
  baseline omits them.

## Relevant agent conditions

- Only file reading and Markdown writing are needed.
- Credentials as in the pay-app-review task.

## Environment

- Starting state: `python:3.12-slim` with the four input files;
  `/app/output/` empty.
- Hidden from the agent: `tests/`, `solution/`, this file.
- Fresh container per trial; no services.

### Hidden truth

| Item | Value |
|---|---|
| RFI number | RFI-023 |
| To | Oakhaven Studio Architects (routes to Tremont Engineering Group) |
| Date issued | 2026-10-12 |
| Response needed by | 2026-10-19 (three working days before the 2026-10-23 pour) |
| Contract turnaround | 14 calendar days, so 2026-10-26; the RFI must say the needed-by date is shorter |
| Conflict | S-001 General Note 5 says 3,500 psi for slabs on grade; 03 30 00 paragraph 2.6.C says 4,000 psi; submittal 03 30 00-02 mix M-2 at 3,500 psi returned No Exceptions Taken; detail 3/S-101 points strength to S-001 Note 5 |
| Supported resolution | 4,000 psi per 2.6.C, because S-001 Note 1 says the more stringent requirement governs unless the engineer directs otherwise in writing |
| References that may be cited | S-001, S-101, 3/S-101, 03 30 00 (1.4.B, 2.6.A, 2.6.C, 2.6.D); S-501, 6/S-501, and 07 26 00 are named in the excerpts but were not reviewed and may be mentioned only as such |
| Must not appear | any other sheet, detail, or paragraph; a direction to proceed, pour, or revise; a statement of no cost or schedule impact (nothing has been priced) |

## Verification

Rewardkit, four dimensions. `reward` = threshold 0.9 over the weighted mean
of dimensions (correctness 4, boundaries 4, format 1, grounding 1).
`soft_score` = weighted mean. Boundaries: hard gates all-pass at weight 3
(no invented references, does not direct or decide, no unconfirmed
no-impact statement) plus weighted disclaimers under `boundaries/disclaimers/`.

| ID | Required or prohibited result | Independent evidence | Exact check | Pass |
|---|---|---|---|---|
| rfi_exists | RFI at /app/output/rfi-023.md | file | length > 1500 | bool |
| conflict_sources_cited | S-001 Note 5, 03 30 00 2.6.C, the returned M-2 submittal, 3/S-101 | RFI text | token co-occurrence | fraction |
| strengths_stated | 3,500 psi and 4,000 psi both stated | RFI text | psi tokens | bool |
| question_leads_with_ask | question section opens with "Please ..." | RFI text | first line | bool |
| resolution_proposed | suggested resolution names 4,000 psi per 2.6.C, not withheld | RFI section | tokens | bool |
| precedence_note_cited | S-001 Note 1, more stringent governs | RFI text | tokens | bool |
| response_date_present | 2026-10-19 in the header table | RFI header | date parse | bool |
| rfi_number_present | RFI-023 in the title | first line | prefix | bool |
| log_row_present | log row with number, To, needed-by, Open, impacts, related sheets | table row | six field checks | fraction |
| turnaround_flagged | notes the contract date 2026-10-26 or that 14 days is longer than needed | RFI text | date or phrase | bool |
| no_invented_references | every sheet, detail, spec, paragraph cited exists in the provided or named set | RFI text vs truth.json | set inclusion | bool (gate) |
| does_not_direct_or_decide | no proceed/pour/revise directives, no entitlement language | RFI text | regex, negation-aware | bool (gate) |
| no_unconfirmed_no_impact | never states no cost or schedule impact | RFI text | regex | bool (gate) |
| format/* | template sections and header table | RFI text | headings | fraction |
| grounding | share of references and dates in the RFI that appear in the inputs | RFI vs inputs | set membership | fraction |

- Accepted alternatives: any wording; the log row may be in a separate
  table as long as it is in the same file.
- Complete pass rule: `reward` = 1.
- Invalid-run conditions: verifier cannot install rewardkit (exit 3),
  agent timeout, credential failure.

## Fairness and leakage

- Solvable: every fact is in the four inputs; the template is in the skill.
- Shortcuts: pasting the shipped sample RFI (different project) fails
  correctness and references; an RFI that tells the sub to pour at 3,500
  fails the directive gate.
- Hidden truth stays in `tests/fixtures/truth.json` and this file.
- Realistic wrong result: an RFI that withholds the resolution although the
  precedence note supports one, or that cites 6/S-501 as reviewed.
- Prohibited collateral change: none (no mutable services).

## Open decisions

- Run plan: `claude-code` and `codex`, with and without skills, 3 attempts.
- Assumptions: the RFI lands at the path the instruction names.
- Round 1 (2026-09-04, 3 attempts per cell): with the skill, both lanes
  proposed 4,000 psi in every trial, two of them citing S-001 Note 1 as the
  basis rather than paragraph 2.6.C; `resolution_proposed` now accepts
  either. `verification_note` accepts "verify"/"confirmed against" as well
  as "verified". After rescoring: with-skills 6/6 reward 1, baseline 0/6.
- Remaining questions: `question_leads_with_ask` and `unreviewed_marked`
  are still opinionated but were met by every with-skill trial.
