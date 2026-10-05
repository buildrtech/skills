# RFP intake verification

## Revision 2.0.0: scripted go/no-go brief

Previous revision: 1.1.0, a prompt-only review written straight to Markdown
from a default checklist. This revision keeps the job (prep the bid/no-bid
meeting for one opportunity) and makes the decision checkable.

### What changed

- **Company profile.** `company-profile.json` is reused across runs. It holds
  licenses, bonding and insurance limits, days needed to bid, terms the
  company won't accept, scoring context, and the go/no-go criteria, weights,
  and thresholds. The first run asks for it once. Missing facts become
  Unknown, never guesses.
- **Gates.** `scripts/intake.mjs` checks:
  - licenses, where a license needed at bid and not held fails, and one
    needed before contract is a condition
  - single and aggregate bonding
  - insurance limits
  - mandatory meetings already passed
  - days to bid
  - disqualifying terms

  Each gate is pass, fail, or unknown.
- **Score.** Weighted 0 to 5 criteria scaled to 100. Unknown criteria are left
  out, and their share of the weight is reported.
- **Recommendation.**
  - Any failed gate means No-go.
  - Unknown gates, too much unknown weight, or a score between the thresholds
    mean Go with conditions, each condition written as an action.
  - Otherwise the score decides Go or No-go.
- **Citations are validated.** Every fact cites `{ doc, page }`. The script
  rejects pages beyond a document's page count, and citations to documents
  that were referenced but never supplied.
- The brief keeps the 1.1.0 headings the Brannock verifier checks, and adds
  Gates, "This week", and Changed by addenda.
- `references/intake-checklist.md` is replaced by
  `references/data-contract.md` and `references/reading-solicitations.md`.

### Sample

Cedar Hollow Public Schools, Prairie View Elementary addition and renovation,
an $18.2M hard bid. The package ships as three PDFs: an 8-page ITB and two
addenda. Planted problems:

- a mandatory pre-bid meeting three days out
- a city license required before contract that the company doesn't hold
- pollution liability added by Addendum 2 and missing from the profile
- a bond at 91% of the single-job limit
- liquidated damages against a renovation window that ends on the
  Substantial Completion date
- the hazardous materials survey referenced but not supplied

Result: Go with conditions, a score of 63 against a go line of 65, with 20%
of the weight unknown.

### Verification

- `node --test evals/tasks/rfp-intake/intake.test.mjs`: 11 tests, in CI. They
  include an exact match of the bundled brief against a fresh build, each of
  the 7 gate failures forcing No-go, unknowns forcing conditions, score
  thresholds, default criteria, and citation validation.
- Mutation check: 10 deliberate breaks each failed at least one test.
- The sample brief passes the Brannock task's header and section checks.

### Not yet tested

A fresh agent extracting a solicitation it hasn't seen, including physical
page numbers on PDFs whose printed numbers differ.

---

# Revision 1.1.0: takeover report

RFP intake is revised to 1.1.0. Changes are local and limited to
`skills/rfp-intake/`, `evals/tasks/rfp-intake/`, and this review directory.
No publication, production writes, or MCP calls were performed.
Both coordinator-approved Case A runs completed, and both runtimes and the
evaluation slot were released. **Fresh result: 15/15 baseline and 15/15 revised,
a tie.** This pair demonstrates no model-quality gain; the grader-fairness fix
has separate deterministic evidence. See `FRESH-RESULTS.md` and `fresh-results.json`.


## Findings before revision

Read takeover audit, full HANDOFF.md, every existing skill file, the RFP Task.md,
agent inputs, reference solution, and verifier/fixtures. The Task.md historical
Round 1 reports Claude with skills 2/3 and Codex 0/3; those are historical,
not fresh measurements. It records one withheld recommendation and Codex
heading mismatches. Actual current-source inspection confirmed exact-heading
format scoring contributes to pass/fail and exact scorecard headings also
reduce correctness. The old scorecard check counts rows without checking ratings.

A controlled reference review with only presentation changes failed the old
verifier: reward 0, soft 0.8636, correctness 0.9091, format 0, boundaries and
grounding 1.0. This was obtained before changing the verifier. See
`baseline-alternate-headings.json`. The final corrected positive fixture was
also replayed against preserved baseline and revised verifiers; see
`final-paired-verifier.json`. No negative was removed to obtain a pass. `compare_verifiers.py` reproduces
the final comparison. `comparison-hashes.json` records 34 input/skill/verifier
file hashes; every available baseline copy was compared byte-for-byte with
`git show 9a62032:<path>`.

The shipped sample inferred company fit and “Full CD set” from no company
criteria and unreviewed drawings. The reference oracle also invented structural
steel, a dedicated mechanical zone, local trade scarcity, and assured company
qualifications while elsewhere acknowledging those inputs were unavailable.
These are source-grounding defects, even though the numeric grader passed them.

## Revisions

- Main workflow inventories reviewed versus referenced documents, reconciles
  each supplied addendum, distinguishes superseded deadlines/delivery terms,
  and checks material requirements before delivery. It calls for advice even
  when the user reserves the final decision, with conditions and unknowns.
- Added section/line citations for Markdown, document/page citations for PDF,
  and explicit OCR/unread-page limits. Optional company inputs no longer block
  a review. Unknown company capacity stays unknown. Narrow extractions need
  not produce an unrelated full scorecard.
- Reference checklist makes headings defaults, while preserving full-intake
  criteria ratings and material requirements. Added missing material limits,
  bond basis, insurance endorsements, alternate/forms and post-bid checks.
- Sample and oracle corrected unsupported fit/design/system claims and
  preserved “may reject” versus mandatory consequences. Original comparison
  evidence remains recoverable from 9a62032 and the /tmp baseline.
- Exact template formatting remains visible as a diagnostic dimension with
  zero outcome weight. Outcome threshold remains 0.9, weights 4 correctness,
  4 boundaries, 1 grounding. Scorecard check now requires distinct criteria,
  actual ratings, and reasons, independent of headings. Seven tests cover
  alternate headings, bullets, blank ratings, duplicate criteria, dates, and
  missing reasons.
- Added `metadata.summary` per coordinator; bumped behavior version to 1.1.0.

## Commands and results

Run from repository root. UV cache/tool directories are isolated in /tmp:

```sh
UV_TOOL_DIR=/tmp/rfp-uv-tools UV_CACHE_DIR=/tmp/rfp-uv-cache \
  python3 evals/scripts/check_fixtures.py evals/tasks/rfp-intake/brannock-fire-station-4
python3 evals/reviews/rfp-intake/test_verifier.py
UV_TOOL_DIR=/tmp/rfp-uv-tools UV_CACHE_DIR=/tmp/rfp-uv-cache \
  uvx --with pyyaml python tools/validate_skills.py skills/rfp-intake
git diff --check -- skills/rfp-intake evals/tasks/rfp-intake evals/reviews/rfp-intake
```

Baseline five fixtures behaved as expected (`baseline-fixtures.txt`). Revised
six fixtures behave as expected (`revised-fixtures.txt`): known-good and alternate
headings pass; missing, shipped-sample shortcut, wrong final decision, and thin
review fail. Seven deterministic helper tests pass (`unit-results.txt`). Skill
validation passes, both task shell scripts pass `bash -n`, and whitespace
check is clean. These are real Rewardkit 0.2.0
executions against local synthetic documents, not mocked scores or model trials.

Initial fixture invocation failed because uv attempted a read-only global tool
directory; rerun with UV_TOOL_DIR in /tmp succeeded. Direct validator invocation
lacked PyYAML; isolated `uvx --with pyyaml` succeeded. Neither required shared
code changes. No bundled RFP production script exists to run; the executable
surface here is the actual task verifier and targeted tests.

## Limits

Missing-package Case B, live API integration and graphical PDF extraction were
not fresh-tested. This pair uses unfamiliar synthetic text documents. Verifier
phrase/amount matching is not a semantic check of every citation, deadline
relationship or judgment; the frozen fresh rubric and trace inspection provide
separate evidence. The six deterministic comparisons retain five ties and the
heading-only false-negative correction. Details: `paired-controls.json`.

## Authoring guidance applied

Read local writing-great-skills and BB skill-creator SKILL.md. Applied checkable
completion, conditional resource pointers, coherent scope, and comparison before
optimization from the official [specification](https://agentskills.io/specification),
[best practices](https://agentskills.io/skill-creation/best-practices), and
[evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills).
Fresh testing began only after the coordinator released the slot. Both outputs
and transcripts were assessed; missing-package and other unrun limits remain.


## Completed fresh evaluation

Baseline `thr_99rywwrr6n` / `env_4ap5zny3r5` and revised `thr_pd5uamwkm2` /
`env_gmr5cbi9dj` completed sequentially on the same Codex gpt-6-astra medium
settings. Both passed all 15 frozen rubric items. Inputs and assigned skill
hashes were unchanged; traces show no forbidden reads or writes. Both read all
bundled sample material, so progressive-disclosure improvement is not established.
Revised output is 3,158 words versus baseline 2,432; no concision improvement.
Single-run request-to-completion times were 126.901s versus 91.548s, both under
the ten-minute cap, not performance benchmarks. Host queue delay is recorded
separately. No additional trial was launched and Case B remains unrun.

Detailed per-item evidence, exact thread-storage transcript/output paths,
normal BB catalog/isolation caveats, and the AI-worker scoring limit appear in
`FRESH-RESULTS.md`; machine-readable metadata and hashes in `fresh-results.json`.
The baseline/revision quality tie does not erase the separately reproduced
verifier false negative. No further behavior revision was made after this pair.
