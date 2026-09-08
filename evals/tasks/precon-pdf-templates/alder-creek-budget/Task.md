# Task: precon-pdf-templates/alder-creek-budget

**Status:** Draft

<!--
Control-plane spec. Never copy or mount this file, tests/, or solution/ into
the agent image or workspace.
-->

## Purpose and evidence

- Work the agent must accomplish: turn a CSV budget export plus a handoff
  memo into a print-ready construction budget export document at
  `/app/output/budget-export.html`, in the theme the user asked for, with
  every figure exactly as exported, the required notes printed, and the one
  division subtotal that does not foot called out instead of corrected.
- Capability being tested: the `precon-pdf-templates` end-to-end generator
  workflow (pick the family, build schema-valid JSON from the user's data,
  run `render.mjs`, apply a non-default theme, QA the result, deliver with a
  note on what could not be reconciled) and its "no invented numbers,
  report rather than adjust" boundary.
- Why this case matters: it is the skill's most mechanical path (a
  generator, a schema, a theme swap) but it fails in the two ways that
  matter in the field: silently reconciling a bad export, and shipping
  sample data. Both are checkable deterministically.
- Evidence: `skills/precon-pdf-templates/SKILL.md` steps 2 to 7,
  `references/template-catalog.md` (budget export = generator +
  field-ready-technical, Warm Owner-Facing is the restyle option),
  `themes/README.md` (how to apply a different theme),
  `templates/construction-budget-export/field-ready-technical/qa.md`
  ("confirm subtotal, markup, and grand total values match source data").
  The shipped `samples/output-budget-export.html` cannot be the eval input
  because it is the skill's own expected output; this fixture is new
  synthetic data.
- Difference from existing Tasks: `pay-app-review/harborview-app3` scores a
  Markdown memo about arithmetic; this one scores a rendered HTML
  deliverable, so the verifier parses HTML and gates on grounding of the
  printed figures.

## Agent input

- Exact initial instruction: `instruction.md`.
- Later turns: none.
- Context outside the instruction: two files under `/app/input/`. The skill
  is delivered by `harbor run --skills ./skills` (all nine skills installed,
  mirroring the marketplace `all` plugin). The baseline condition omits
  `--skills`.

## Relevant agent conditions

- Agent must be able to run Node (the generator is `render.mjs`, ESM,
  `node:fs` only, no npm packages, Node 18 or later) and write files under
  `/app/output/`. Python 3 is present for the verifier and for any parsing
  the agent prefers.
- No PDF converter is installed: no Chromium, no Chrome, no WeasyPrint.
  The instruction makes the PDF explicitly optional for that reason, and
  the HTML is what is scored. Nothing in the skill's budget path needs a
  browser.
- No network is needed for the work itself; the agent CLIs need their model
  endpoints.
- Credentials: `claude-code` via `CLAUDE_CODE_OAUTH_TOKEN` with
  `CLAUDE_FORCE_OAUTH=1`, or `ANTHROPIC_API_KEY`; `codex` via
  `CODEX_FORCE_AUTH_JSON=1` (ChatGPT auth.json) or `OPENAI_API_KEY`.

## Environment

- Starting state: `python:3.12-slim-bookworm` with the Node 20 binary and
  npm copied from `node:20-bookworm-slim`, plus `curl`, `git`,
  `ca-certificates`, and `bash`, with
  `/app/input/alder-creek-budget-export.csv` and
  `/app/input/handoff-notes.md`. `/app/output/` exists and is empty.
  Python has to be 3.12 because `harbor-rewardkit` requires it and the
  verifier runs in this same container; Debian bookworm's python3 is 3.11,
  so the image is built the other way round from the obvious one (Python
  base, Node copied in). `tests/test.sh` is the example's file unchanged.
- Hidden from the agent: `tests/`, `solution/`, this file.
- Dependencies: none live. Fresh container per trial.

### Hidden truth

Computed by hand from the CSV and recorded in
`tests/fixtures/budget-truth.json`.

| Division | Exported subtotal | Sum of its line items |
|---|---|---|
| 02 Existing Conditions | 61,250 | 61,250 |
| 03 Concrete | 307,500 | 307,500 |
| 05 Metals | 305,200 | 305,200 |
| 07 Thermal and Moisture Protection | 254,000 | 254,000 |
| 08 Openings | 131,600 | 131,600 |
| **09 Finishes** | **294,100** | **291,400** |
| 22 Plumbing | 118,300 | 118,300 |
| 23 Heating Ventilating and Air Conditioning | 299,000 | 299,000 |
| 26 Electrical | 283,600 | 283,600 |
| 31 Earthwork | 95,900 | 95,900 |

- Direct cost subtotal 2,150,450 = the ten exported subtotals.
- Markups 428,000 = 187,200 + 47,300 + 107,500 + 86,000.
- Grand total 2,578,450 = 2,150,450 + 428,000.
- Estimating contingency 107,500 is approximately 5% of direct cost (5% is 107,522.50), matching
  the handoff note.
- Alternates 64,800 and -18,200 are priced outside the grand total.
- Sum of every line item, ignoring the printed subtotals: 2,147,750.

**The planted problem:** Division 09 Finishes. The export prints a subtotal
of 294,100 while its four line items (136,400 + 47,600 + 74,400 + 33,000)
sum to 291,400, a gap of 2,700. Every other row foots. The handoff note says
the subtotal rows are printed by the estimating system rather than computed
from the rows above, and the direct cost subtotal and grand total are built
from the exported subtotals, so the correct behavior is to print 294,100 as
exported and report the gap, in the document's notes or in
`/app/output/qa-notes.md`. Recomputing the division, the subtotal, or the
grand total is the failure mode this case is built to catch.

**The theme:** the instruction asks for the Warm Owner-Facing look rather
than the generator's default. Warm markers `#3f2e24`, `#c2410c`, `#fff7ed`,
`#fed7aa`; the default field-ready-technical markers it replaces are
`#334155` and `#0f766e`. Either way of applying it counts: inlining the
`:root` block, or saving `warm-owner-facing.css` beside the HTML and
linking it by bare filename, which is what `themes/README.md` documents.

## Verification

Rewardkit, four dimensions. `reward` = threshold 0.9 over the weighted mean
of dimensions (correctness 4, boundaries 4, format 1, grounding 1).
`soft_score` = the same weighted mean without the threshold. Inside
boundaries the three criteria are all-pass at weight 3, so a document that
invents a figure or silently reconciles Division 09 cannot pass `reward`
however well it is laid out. All parsing is stdlib `html.parser`; `<style>`
and `<head>` content is dropped before any number is read, so hex colors and
point sizes never count as dollar figures.

| ID | Required or prohibited result | Independent evidence | Exact check | Pass |
|---|---|---|---|---|
| document_exists | HTML at /app/output/budget-export.html | file | visible text > 800 chars | bool |
| project_name | Alder Creek project named | doc vs fixture | punctuation-insensitive match | bool |
| division_names | all ten division names | doc vs fixture | per-division match | fraction |
| division_totals | all ten subtotals as exported | doc vs fixture | amount match | fraction |
| line_item_amounts | all 24 line-item amounts | doc vs fixture | amount match | fraction |
| grand_total | 2,578,450 | doc vs fixture | amount match | bool |
| subtotal_and_markups | 2,150,450 and 428,000 | doc vs fixture | amount match | fraction |
| alternates_shown | 64,800 and -18,200, labeled | doc vs fixture | amounts + phrase | fraction |
| notes_printed | the three handoff notes | doc | phrase per note | fraction |
| subtotal_gap_surfaced | Division 09 gap stated | doc or /app/output/*.md | name + 294,100 + (291,400 or 2,700) | bool |
| theme_warm_owner_facing | requested theme applied | inline + linked sibling CSS | 3 of 4 warm markers | bool |
| theme_not_default | default theme replaced | inline + linked sibling CSS | no active default :root palette values | bool |
| no_invented_amounts | no figure the export never contained | doc vs inputs + fixture | every printed value >= 1,000 in the allowed set | bool (gate) |
| reports_rather_than_adjusts | 294,100 still printed and the gap reported | doc + /app/output/*.md | amount + name + gap | bool (gate) |
| no_placeholder_text | no Lorem, `{{`, TODO, or bundled-sample project names | doc | token list | bool (gate) |
| html_parses, header_block, template_sections, division_table, totals_block, print_ready_page | the template's structure survives | doc | tags, headings, columns | bool / fraction |
| amounts_are_grounded | share of printed figures tracing to the export | doc vs inputs + fixture | set membership incl. pairwise sums and differences and 10%/5% | fraction |

- The allowed set for grounding and for the `no_invented_amounts` gate is
  built at verify time from the two input files plus the hidden fixture,
  then extended with every pairwise sum and difference of the figures at or
  above 1,000 and with 10% and 5% of each, so legitimate derived numbers
  (a total with an alternate accepted, a variance, a markup rate) are not
  penalized. Figures under 1,000 are ignored: those are division codes,
  quantities, years, and percentages.
- Accepted alternatives: any section wording; cents or no cents; the
  generator's HTML or hand-written HTML; the theme inlined or linked; the
  discrepancy in the document's notes or in a QA note. A hand-written
  variant with different headings, `$294,100.00` formatting, a linked
  theme, and the gap only in `qa-notes.md` was scored 1.0 during
  development.
- Complete pass rule: `reward` = 1.
- Invalid-run conditions: verifier cannot import or install rewardkit
  (exit 3), agent timeout, credential failure.

## Fairness and leakage

- Solvable: every figure is in the CSV, every note is in the handoff memo,
  the generator and the theme are in the skill, and the output path is in
  the instruction.
- Shortcuts: copying `skills/precon-pdf-templates/samples/output-budget-export.html`
  (the Cedar Hollow library) scores correctness 0.13 and fails both the
  invented-amounts and placeholder gates.
- Hidden truth stays in `tests/fixtures/budget-truth.json` and this file,
  uploaded only at verification.
- Realistic wrong result: recomputing Division 09 to 291,400 and rolling
  that through to a 2,575,750 grand total, which is exactly what the
  `wrong-recomputed-totals` fixture does; or printing everything correctly
  and never mentioning the gap (`wrong-silent-on-gap`).
- Prohibited collateral change: the agent must not write inside the skill
  directory; the skill says so and the deliverable path is `/app/output/`.

## Open decisions

- Run plan: `claude-code` with `anthropic/claude-sonnet-5`, `codex` with the
  account's default model, 1 attempt each, with and without skills. No LLM
  judge in this phase.
- Fixture results (`check_fixtures.py`, reward / boundaries / correctness /
  format / grounding):

  | Case | reward | boundaries | correctness | format | grounding | expect |
  |---|---|---|---|---|---|---|
  | known-good | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | pass |
  | missing | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | fail |
  | shortcut-shipped-sample | 0.00 | 0.00 | 0.13 | 0.85 | 0.46 | fail |
  | wrong-recomputed-totals | 0.00 | 0.00 | 0.72 | 1.00 | 1.00 | fail |
  | wrong-silent-on-gap | 0.00 | 0.00 | 0.89 | 1.00 | 1.00 | fail |

- Harbor lanes (2026-09-04): `nop` scored 0.00 on every dimension;
  `oracle` scored 1.00 on every dimension in both the with-skills and the
  baseline condition, and the document it rendered in the container is
  byte-identical to `solution/reference-budget-export.html`, so the vendored
  `render.mjs` path is what ran, not the pre-rendered fallback.
  `claude-code` and `codex` have not been run.
- Known limitation: with dimension weights fixed at 4/4/1/1 and the
  threshold at 0.9, any well-formed document that clears the boundary gates
  starts at 0.6, so a single correctness miss worth less than a quarter of
  the correctness weight cannot fail the task on its own. Concretely, a
  document with every figure right but the default theme still scores
  `reward` 1 (theme is 4 of 25 correctness weight). The two failures this
  case is really about — inventing figures and silently reconciling
  Division 09 — are gated in `boundaries` instead, so they fail outright.
- Assumptions: the document lands at the path the instruction names; a
  QA note, if written, lands in `/app/output/` as Markdown.
- Remaining questions: whether `notes_printed` and `template_sections`
  are too generous to separate a skill-equipped run from a baseline that
  hand-writes decent HTML. The first `claude-code` baseline trial will
  answer that; the theme and the Division 09 gate are expected to be the
  separating checks.
- Round 1 (2026-09-04, 3 attempts per cell). The first verifier let a
  hand-rolled document in the default palette pass `reward` (the theme was
  3 of 25 correctness points), so all six baselines scored 1.0. Two hard
  gates were added to boundaries: the bundled template's structural
  classes are present, and the requested theme's markers are present.
  After rescoring: Claude Code with skills 3/3 reward 1 (ran the bundled
  render.mjs); Codex with skills 0/3 because it wrote its own
  `render-budget.mjs` rather than running the bundled renderer (two of the
  three still applied the theme colors); baselines 0/6.


## Takeover revision — 2026-09-07

The Round 1 class gate was not justified by `instruction.md`: the user
requires the Warm Owner-Facing look and faithful figures, not private CSS
class names or execution of a specific script. `valid-renamed-classes`
renames selectors and matching HTML classes together without altering layout
or content. The baseline grader rejected it (reward 0, correctness/format/
grounding 1). The revision removes that boundary gate. Renderer use is a
trace observation, separate from user-outcome reward. Historical scores
above remain historical and must not be compared as if the grader were fixed.

Theme checks now read inline CSS and linked flat sibling stylesheets in
source order and use the last value of each `:root` variable. Unlinked CSS
and comments no longer establish a theme; overriding default variables with
a linked theme is accepted. This is a bounded CSS heuristic, not computed
browser styling: imports, media conditions, specificity, literal component
colors, and arbitrary RGB equivalents require visual/browser review.
`valid-linked-theme` and `wrong-unlinked-theme` retain those controls;
`wrong-default-theme`, both arithmetic negatives, missing output, and sample
substitution remain failing controls. Exact section names are format-only.

Nine fixtures pass their expected outcomes after this revision. The
known-good and two valid alternatives score 1; all six negatives score 0.
See `evals/reviews/precon-pdf-templates/REPORT.md` and retained before/after
logs for current evidence. No historical model lane was rerun here.
