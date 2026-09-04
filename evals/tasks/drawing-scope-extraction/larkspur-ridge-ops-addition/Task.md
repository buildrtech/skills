# Task: drawing-scope-extraction/larkspur-ridge-ops-addition

**Status:** Draft

<!--
Control-plane spec. Never copy or mount this file, tests/, or solution/ into
the agent image or workspace.
-->

## Purpose and evidence

- Work the agent must accomplish: read the extracted text of an 18-sheet
  permit set and a first-pass candidate file recorded by someone else, check
  the candidates against the sheet index, and write a scope list grouped by
  CSI division with every item cited to a sheet and a place on that sheet,
  assumptions, exclusions, and RFIs kept separate, and a coverage ledger.
- Capability being tested: the `drawing-scope-extraction` skill's end-to-end
  workflow (inventory the sheets and start the ledger, read each sheet, run
  the trade probes, record candidates in the schema, apply the grounding
  rules, run `scripts/scope_list.py`, report coverage). The planted problems
  are exactly the four things the grounding rules exist to catch: scope
  invented against sheets that are not in the set, cross-sheet references and
  by-others work carried as included scope, a division assigned from the
  trade that installs the item rather than from what the drawings show, and a
  sheet left off the ledger.
- Why this case matters: this is the skill's only script-validated artifact
  and the one place where "did the agent actually read the set" is
  measurable. The set spans A, S, M, E, P, and C series so division
  assignment is a real decision rather than a single-discipline lookup.
- Evidence: `skills/drawing-scope-extraction/SKILL.md`,
  `references/grounding-rules.md`, `references/candidate-schema.json`,
  `references/csi-divisions.md`, `references/trade-probes.md`, and
  `scripts/scope_list.py`. The shipped sample cannot be the eval input
  because `samples/output-scope-list.md` is the expected output and is
  visible to the agent whenever the skill is installed; this fixture is a new
  project with new sheets and new items.
- Difference from existing Tasks: second task in the suite, first for this
  skill. `pay-app-review/harborview-app3` scores arithmetic and continuity
  findings; this one scores grounding and coverage.

## Agent input

- Exact initial instruction: `instruction.md`.
- Later turns: none.
- Context outside the instruction: two files under `/app/input/`. The skill is
  delivered by `harbor run --skills ./skills` (all nine skills installed,
  mirroring the marketplace `all` plugin). The baseline condition omits
  `--skills`.

## Relevant agent conditions

- Agent must be able to run Python 3 (the skill's script is standard library)
  and write a Markdown file.
- No network is needed for the work itself; the agent CLIs need their model
  endpoints.
- Credentials: `claude-code` via `CLAUDE_CODE_OAUTH_TOKEN` with
  `CLAUDE_FORCE_OAUTH=1`, or `ANTHROPIC_API_KEY`; `codex` via
  `CODEX_FORCE_AUTH_JSON=1` (ChatGPT auth.json) or `OPENAI_API_KEY`.

## Environment

- Starting state: `python:3.12-slim-bookworm` with
  `/app/input/sheet-index.md` (the G-000 sheet index plus the extracted text
  of every sheet: general notes, keyed notes, schedules, and details) and
  `/app/input/candidates.json` (a first-pass candidates file in the shape of
  `references/candidate-schema.json`, with the problems below planted).
  `/app/output/` exists and is empty.
- Hidden from the agent: `tests/`, `solution/`, this file.
- Dependencies: none live. Fresh container per trial.

### The set

Larkspur Ridge Water District, Operations Building Addition and Yard
Improvements, Permit Set 2026-07-30. Invented project, owner, architect,
engineers, sheets, and items. 18 sheets across the G, A, C, S, M, P, and E
series. The first-pass candidates file carries 38 candidates; the corrected
set is 39 candidates in 20 divisions, 33 of them included scope.

### Planted problems (hidden truth)

Script-detectable (`scripts/scope_list.py` exits 1 on the input file with
exactly these three errors):

| # | Where | Problem |
|---|---|---|
| 1 | top level | `sheet_count` is 18 but the ledger lists 17 sheets: C-501 Site Details was never entered |
| 2 | cand-038 | `sheet_number` A-702 is not a sheet in the coverage ledger |
| 3 | cand-039 | `sheet_number` E-401 is not a sheet in the coverage ledger |

Judgment calls the script cannot make:

- **Two candidates cite sheets that are not in the set.** cand-038 (room
  identification signage, ADA tactile) cites A-702; cand-039 (automatic
  transfer switch and standby generator connection) cites E-401. Neither
  sheet is in the G-000 index and neither subject appears anywhere in the
  extracted text. Correct handling is to drop both from the candidates and
  write each as an RFI. Inventing ledger rows for A-702 and E-401 so the
  script accepts the file is the realistic wrong answer and is what the
  `wrong-lists-phantom-sheets` case does.
- **Two weakly supported items are tagged `direct` / `include` in the first
  pass.** cand-009 (electrical service conduit and pull vault) rests on
  C-201 keyed utility note 4, which says "SEE E-101"; E-101's extracted text
  has no service conduit, vault, transformer pad, one-line diagram, or panel
  schedule, so it is `reference_only` / `review` plus an RFI. cand-032
  (thermostats and DDC points) rests on M-101 mechanical note 2, which
  assigns them to the District's controls vendor under a separate contract,
  so it is `by_others` / `exclude` and belongs in Division 25, not 23.
- **One item is filed under the wrong division.** cand-002, the FRT wood
  blocking required by G-000 GN-3, is filed under Division 10 because it
  backs grab bars and wall-mounted equipment. `references/csi-divisions.md`
  uses this exact case as the first-two-digits example: blocking is Division
  06 rough carpentry no matter what it backs.
- **Coverage ledger.** All 18 sheets must have a ledger entry. C-501 is
  missing from the first pass and, once read, contributes the bollards at
  each overhead door jamb (Division 05) and the yard apron pavement section
  (Division 32). Two sheets were read and carry no scope: A-002 (code
  analysis and egress diagram only) and S-001 (design criteria, load values,
  and code references only). A-601 is a scanned raster sheet whose OCR
  recovered fewer than twenty words; it is `unreadable`, and the personnel
  doors, frames, hardware, and windows that A-102 note 3 points to it for
  stay under review with an open RFI.

The corrected candidates file is `tests/fixtures/reference-candidates.json`
and the script's output on it is `tests/fixtures/script-output.md`. The
reference deliverable is that output plus the coverage report the skill's
last workflow step asks for.

## Verification

Rewardkit, four dimensions. `reward` = threshold 0.9 over the weighted mean of
dimensions (correctness 4, boundaries 4, format 1, grounding 1). `soft_score`
= the same weighted mean, ungated. Inside boundaries, the hard gates
(`citations_exist`, `no_extra_scope`) are all-pass at weight 3 and the three
disclaimer phrases are a weighted mean at weight 1, so a list that cites a
sheet outside the index cannot pass `reward` but a list that merely drops a
disclaimer can.

A sheet number named on a line that reports it as missing ("not in the sheet
index", "does not exist", "RFI", and the rest of `NEGATIONS` in
`tests/common.py`) is a gap being reported, not a citation, and is not counted
against the list. That distinction is what lets the correct answer name A-702
and E-401 in its RFIs.

| ID | Required or prohibited result | Independent evidence | Exact check | Pass |
|---|---|---|---|---|
| scope_list_exists | list at /app/output/scope-list.md | file | length > 2000 chars | bool |
| expected_scope_items | each of the 39 corrected candidates present with its sheet | list vs hidden fixture | keyword group and sheet number in the same block | fraction |
| bad_citations_flagged | A-702 and E-401 items never listed as scope, each explicitly flagged | list vs sheet index | keyword absent from the Included scope section, and a block naming it that says the sheet is missing | fraction |
| weak_support_tagged | service conduit reference-only/review; thermostats and DDC by others/excluded | list vs sheet text | keyword absent from Included scope and a block carrying the tag | fraction |
| division_corrected | wood blocking under Division 06 | list | blocking inside the Division 06 group, or blocking within 400 chars of "division 06" or "06 10 53" | bool |
| ledger_lists_every_sheet | all 18 sheets in the ledger | list vs index | sheet number present in the coverage ledger section | fraction |
| no_scope_sheets_noted | A-002 and S-001 recorded as carrying no scope; A-601 recorded as unreadable | list | markers in that sheet's ledger row | fraction |
| citations_exist | no citation names a sheet outside the index | list vs index | sheet tokens on citation lines all in the 18 | bool, gate |
| no_extra_scope | no invented scope | list vs candidate vocabulary | at least 90% of Included scope bullets match a known item | bool, gate |
| not_a_takeoff, no_quantities_or_pricing, draft_for_review | the skill's standing disclaimers | list | phrases | bool |
| title_and_summary, grouped_by_division, standard_sections, ledger_table | the shape the script prints | list | title, 16 division headings, five sections, ledger table | bool / fraction |
| sheet_ids_are_grounded | sheet numbers printed exist | list vs index | share of sheet tokens outside gap-reporting lines that are in the index | fraction |

- Accepted alternatives: any wording; any ordering; the agent may write the
  scope list by hand as long as the sections, the citations, and the ledger
  are there. Nothing requires the script to have been run, only that the
  output matches what a correct run would say.
- Complete pass rule: `reward` = 1.
- Invalid-run conditions: verifier cannot install rewardkit (exit 3), agent
  timeout, credential failure.

## Fairness and leakage

- Solvable: every fact is in the two input files. The sheet index says which
  18 sheets exist; the extracted text says what each one calls for; the
  schema, the divisions table, the probes, and the script are in the skill.
- Shortcuts: pasting the shipped sample scope list is a different project and
  scores correctness 0.40, boundaries 0.25, reward 0. Accepting the first-pass
  file and inventing ledger rows for A-702 and E-401 fails the citation gate.
- Hidden truth stays in `tests/fixtures/` and this file, uploaded only at
  verification.
- Realistic wrong result: a scope list that reproduces the first pass with the
  three script errors fixed the lazy way, keeping the phantom items and the
  weak-support tags as they were.
- Prohibited collateral change: none applicable (no mutable services).

## Open decisions

- Run plan: `claude-code` with `anthropic/claude-sonnet-5`, `codex` with the
  account's default model, 1 attempt each, with and without skills. No LLM
  judge in this phase.
- Assumptions: the scope list lands at the path the instruction names.
- Fixture cases (`python3 evals/scripts/check_fixtures.py`):

  | case | reward | soft | correctness | boundaries | format | grounding |
  |---|---|---|---|---|---|---|
  | known-good | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
  | missing | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
  | shortcut-shipped-sample | 0.00 | 0.43 | 0.40 | 0.25 | 0.87 | 0.81 |
  | wrong-lists-phantom-sheets | 0.00 | 0.64 | 0.86 | 0.25 | 1.00 | 0.95 |
  | wrong-no-ledger | 0.00 | 0.87 | 0.75 | 1.00 | 0.74 | 1.00 |

- Remaining questions: `no_extra_scope` is a keyword-vocabulary gate rather
  than a true set comparison, so an invented item that happens to reuse a
  known term (another partition type, another light fixture) would slip
  through it; the citation gate and `expected_scope_items` are what actually
  carry that weight. `wrong-no-ledger` clears the threshold by only 0.026, so
  a later loosening of any correctness or format check should be rechecked
  against it.
- Round 1 (2026-09-04, 3 attempts per cell). One verifier fix: the citation
  gate skipped only lines matching a fixed negation phrase list, so correct
  memos that said the phantom sheets "do not appear" or "neither sheet
  exists" were rejected; `is_negated` now uses a broad negation regex. After
  rescoring: Claude Code with skills 3/3 reward 1; baselines 0/6.
