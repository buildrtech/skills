# Pay-app-review takeover — completed 2026-09-08

**Revision 1.1.0 is verified locally.** Eight CLI regression tests and all six
verifier controls pass. The completed fresh Codex comparison is a **6/6 versus
6/6 outcome tie**, with improved script behavior in the revision. No production writes or edits outside the three owned directories by this worker.

## Changes and control evidence

- **Missing terms:** unknown contract sum, approved change orders and retainage
  remain unknown; dependent totals show `n/a`. Explicit zero remains valid.
  Supported submitted cover-sheet arithmetic can run without contract terms.
- **Unreadable/invalid inputs:** blank required C/D/E/F amounts, nonfinite
  numbers and invalid rate/tolerance arguments receive exit 2 diagnostics.
  Unreadable cells no longer silently become zero.
- **Prior certification:** `--prior-certified` supplies independently sourced
  cumulative previous certificates. Current submitted Line 7 is separate.
  Prior certification is no longer reconstructed with today's retainage rate.
  References explain cumulative history and avoid allocating reduced
  certification to work lines without a documented revised schedule.
- **Verifier fairness:** a reference memo changed only to equivalent headings
  originally failed (reward 0, correctness 0.88, format 0.29). It now passes
  (reward 1, correctness 1, format 0.29). Actionable hold rows have their own
  outcome dimension; template format remains diagnostic. All four original
  substantive negative controls still fail. No threshold was lowered.
- **Authoring:** updated missing-input and independent-rate instructions,
  preserved conditional references and sourced memo completion criteria,
  added `metadata.summary` (133 characters), bumped version to 1.1.0, and
  refreshed executable sample commands/output. Headings are defaults.

## Verification

```sh
python3 evals/reviews/pay-app-review/test_checker.py
PAY_APP_SCRIPT=/tmp/skills-takeover-baseline-9a62032/skills/pay-app-review/scripts/check_pay_app.py python3 evals/reviews/pay-app-review/test_checker.py
python3 evals/reviews/pay-app-review/replay_samples.py
UV_CACHE_DIR=/tmp/pay-app-uv-cache UV_TOOL_DIR=/tmp/pay-app-uv-tools python3 evals/scripts/check_fixtures.py evals/tasks/pay-app-review/harborview-app3
git diff --check -- skills/pay-app-review evals/tasks/pay-app-review evals/reviews/pay-app-review
```

| Check | Result | Retained evidence |
|---|---|---|
| Revised CLI regression tests | 8/8 pass | revised-tests.txt, test_checker.py |
| Frozen CLI against revised contracts | All eight fail; some failures are unsupported new flags, not independent behavior comparisons | baseline-tests.txt |
| Same-input certificate scenario | Old false error: 4500 vs 4750; revision clean using independent 4500 | certificate-comparison.json, certificate-{baseline,revised}.md |
| Pinecrest and Harborview replay | Ties: 9 errors/5 warnings and 11 errors/7 warnings; findings and monetary rows byte-identical | sample-replay.json, sample/harborview-{baseline,revised}.md |
| Verifier controls | 6/6 expected outcomes; known-good and heading variant pass, four negatives fail | original-fixtures.txt, before-fairness.txt, final-fixtures.txt |
| Metadata/resource paths and diff whitespace | Pass | revised-sha256.json; coordinator also confirmed all-nine validation |

Only explanatory script footers changed in the package replays. uv initially
could not write its default tool directory; successful runs used the `/tmp`
cache/tool paths above. No global install, cache commit, or escalation.

## Fresh paired evaluation

Two fresh contexts, sequential, one attempt each. Actual execution records
confirm identical **Codex / gpt-6-astra / medium reasoning / default tier /
auto permissions**. Same runner and combined unfamiliar Cedar+Elm prompt.

| Lane | Thread | Actual start–finish UTC, September 8 | Duration | Substantive checks |
|---|---|---|---|---|
| Frozen 1.0.0 | thr_eedv9mxebb | 00:02:57.687–00:05:32.778 | 155.091 s | 6/6 |
| Revised 1.1.0 | thr_hz39e6knn4 | 00:05:46.667–00:08:06.786 | 140.119 s | 6/6 |

Both final outputs keep the projects separate, identify Cedar's readable
arithmetic errors, preserve its unreadable E and unknown terms, reconcile
Elm's independent certificates/current due, and retain the human payment
decision. This is a final-outcome tie, not evidence of superior memo accuracy.
The worker inspected both memos and tool traces against the hidden rubric;
there was no additional LLM judge. Headings/length were not scored.

The revision improved the observed process: baseline safely avoided Cedar's
unsafe CLI defaults and checked manually; it manually resolved Elm's false
certificate error after checker exit 1. Revised documented Cedar's full-input
exit 2, checked a clearly labeled readable-row subset (exit 1), and ran Elm
with independent certificates (exit 0, no errors/warnings). No manual override
of an incorrect script result was needed. One pair cannot establish speed or
reliability rates; the elapsed-time difference is observational.

Each workspace received only the assigned skill, PROMPT.md, input/ and an
empty output directory. Hidden rubric/checks and the other version were not
copied. Traces show assigned-file/local-output activity only: no external
skill/memory reads, network/MCP, or delegation. Input and skill hashes remained
unchanged. This is file-delivery isolation with explicit read constraints,
not an OS-level barrier to all host files; ambient BB instructions remained.
Explicit skill invocation means this does not measure natural triggering.
Both runs met the ten-minute limit, were stopped, and the slot was released.

**Excluded run:** coordinator-started Claude baseline `thr_s4u7i9xyz3` was
coordinator-canceled/unpaired to avoid a duplicate comparison. It is not a
skill failure or part of the results above. Its thread was inspected; it was
not resumed or replaced. No Claude revised run was performed. Artifacts:
`/home/mikeastock/.bb/thread-storage/thr_hpvpiweaze/claude-pairs/pay-app-review/`.

## Evidence and limits

Baseline preserved at git `9a62032a237cd7588f6f6c687021acc076cd6fb7` and
`/tmp/skills-takeover-baseline-9a62032`. Revised hashes: revised-sha256.json.
The `fresh-pair/` folder retains prompts, input, hidden rubric, spawn metadata,
input/skill hashes and RESULTS.json with matching execution settings,
timestamps, six rubric assessments, and output hashes. Full Codex evidence:

- `/home/mikeastock/.bb/thread-storage/thr_enucp8t8e3/pay-app-pair/baseline-log.json`
- `/home/mikeastock/.bb/thread-storage/thr_enucp8t8e3/pay-app-pair/revised-log.json`
- `/home/mikeastock/.bb/thread-storage/thr_enucp8t8e3/pay-app-pair/baseline/output/`
- `/home/mikeastock/.bb/thread-storage/thr_enucp8t8e3/pay-app-pair/revised/output/`

Each output directory contains both review memos and checker artifacts;
`{baseline,revised}-commands.json` beside the logs contains extracted commands.
No further behavior revision was justified by the completed pair.

All executed cases used synthetic local data. No live MCP/accounting, PDF/OCR,
legal-sufficiency, payment, or remote-write proof. Unrun: other completed model
pairs, broader prompts/trigger coverage, and a full repository suite. Existing
historical Harborview model scores were not rerun. Lexical grader checks are
proxies; actionability supports the demonstrated table layout, not arbitrary
prose. Duplicate/renumbered item identity still requires manual reconciliation;
credit-line policy and exotic numeric representations lack new coverage.
Bid/RFP/PDF/RFI-specific changes belong to other owners.

Read the requested handoff/audit, complete owned skill/task/evidence, and both
authoring skills. Applied [official specification](https://agentskills.io/specification),
[authoring guidance](https://agentskills.io/skill-creation/best-practices), and
[evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills).
Certificate semantics checked against [AIA G702 instructions](https://help.aiacontracts.com/hc/en-us/articles/1500009308242-instructions-g702-1992-application-and-certificate-for-payment).
