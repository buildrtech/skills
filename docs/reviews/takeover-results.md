# Nine-skill takeover results

Baseline: `9a62032a237cd7588f6f6c687021acc076cd6fb7`.
Shared architecture findings and worker IDs: [takeover-audit.md](takeover-audit.md).
All nine existing skills have revised files, deterministic verification and a
completed fresh baseline/revised comparison. Exactly nine skill-owner threads
were created; their IDs and ownership are in the linked audit.

## Coverage

| Skill | Main revision | Deterministic evidence | Fresh baseline → revised |
|---|---|---|---|
| bid-leveling | Submission identity and printed alternate reconciliation | 14 tests including XLSX; 8 fixture expectations | Claude 8/8 → 8/8 tie; Codex artifact tie, quota interruption |
| construction-connectors | Scoped identities, uncertain writes, honest offline replay | 7 verifier tests | Claude 11/11 → 11/11 objective tie; narrative caveats |
| drawing-scope-extraction | Readability-backed inclusion and safe validation | 6 CLI tests; 6 fixture expectations | 7/8 → 8/8 |
| financial-forecasting | Cumulative units, as-of margins, undefined values | 6 arithmetic/CLI tests | Claude 8/8 → 8/8 tie; extra commentary caveats |
| pay-app-review | Missing values and prior certificates | 8 CLI tests; 6 fixture expectations | Codex 6/6 → 6/6 tie |
| precon-pdf-templates | Exact cents, theme selection, honest rendering | 12 renderer cases; 9 fixture expectations | 10/10 → 10/10 tie |
| rfi-drafter | Conditional spec applicability and missed deadlines | 4 regressions; 9 fixture expectations | 8/8 → 8/8 tie |
| rfp-intake | Completeness, superseding addenda, recommendation | 7 tests; 6 fixture expectations | 15/15 → 15/15 tie |
| workforce-planning | Bench/time-off intervals, residual demand | 12 timeline/CLI tests | Seven shared controls tie; conflicting demand action corrected |

Each skill's `evals/reviews/<skill>/REPORT.md` records changes, evidence, baseline
hashes, execution IDs, and limitations. Fresh pairs use unfamiliar synthetic
inputs with hidden expected results and only one attempt per version. Two slots
bound active evaluator work; no broad model matrix was run.

## Shared verification

Ten shared tooling regression tests pass. They cover required human summaries,
synthetic sample presence, marketplace membership, no invented install command,
runner separator parsing/argument privacy/auth precedence, symlink rejection
and atomic result writes. Recording-executable tests verify the wrapper's process
contract and are not Harbor integration proof. All nine skills validate with
PyYAML in an isolated temporary environment. The integration run of all six
existing Harbor task verifiers passed **44/44 fixture expectations**. Targeted
shared and skill suites also pass, including real XLSX reopening, all three PDF
generators and their JSON schemas. Bounded logs are in
`evals/reviews/integration/`. Catalog regeneration is complete and checked against all final skill files.

## Interpretation and limits

Drawing's single improvement is inclusion of explicitly required shelves while
keeping unreadable layout details unresolved. RFI ties under its frozen rubric;
both handle conditional air correctly. Revised RFI keeps the requested missed
date, while baseline explicitly substitutes an expedited date. This qualitative
difference is not reported as a measured gain. PDF also ties at 10/10: both
produce correct signed amounts, gap and theme. Baseline repaired a copied
renderer; revision used the supplied renderer. Both adjusted output spacing. RFP ties at 15/15; the revision is longer and
slower in this pair, so neither concision nor runtime gains are claimed. Both
read samples, so no disclosure-efficiency gain was observed.

Pay-app ties at 6/6: baseline safely overrode an old false certificate finding;
revision uses the corrected CLI. Claude bid ties at 8/8 with both complete;
baseline uses option-name suffixes/crosswalks while revision uses native IDs.
Forecasting ties at 8/8 on its frozen rubric, but both answers contain unscored
causal commentary unsupported by the fixture; see its report. Workforce gets
seven main factual/boundary controls right in both. Baseline preserves a correct
residual table but directs keeping the unfilled need at 100% while adding fills,
contradicting conservation. Revision reduces/splits the residual explicitly.
No numeric composite was prescribed, so none was invented after seeing outputs.

Five clean pairs use Codex gpt-6-astra; four use the separately authorized
Claude Code claude-opus-5[1m] lane after the Codex weekly limit. Each pair uses
matching medium/default/auto settings and one attempt per version. The earlier
Codex bid pair is retained separately: both artifacts pass eight checks, but
revision hits the usage limit after generation, preventing terminal success.
One unnecessary Claude pay baseline was canceled when the original Codex pay
pair completed; it is unpaired, not a skill failure. No score compares across
providers. Grading is by the coordinator/skill workers, not a blind human panel.
Connector JSON outcomes tie at 11/11 after preserving and correcting false
rejections of permitted extra scope/reference context. Seven verifier tests
retain wrong/missing identities and extra-link negatives. Baseline speculates
about read/write permissions; revision overclaims RFI 19 remained unchanged
without readback. Both caveats survive the objective JSON pass.

Runtime skill descriptions remain injected; isolated task folders are not an
OS-level security boundary. All full traces remain outside the repository.

Synthetic connector replay does not establish live API compatibility, auth,
permissions, pagination, writes or notification delivery. Neutral text fixtures
do not establish graphical PDF/OCR accuracy. These fresh CLI/BB evaluations do
not test ChatGPT.com or Claude.ai interfaces and cannot establish statistical
trigger rates. Historical Harbor results remain historical.

No push, merge, production write, marketing snapshot edit, or global skill edit
was performed in this skills environment. The final catalog is `catalog.json` (921614 bytes), SHA-256
`bb56596391c8b322c0d9d8e0321bd824458769be7c96466bf7e82235459ae070`.
Root independently synced and accepted this exact catalog. Shared changes are
in local commit `07d397a`. Source/evaluation integration is committed locally as
`4b42325bc00d076246b3a0a1b8bdab2277ead272`; this documentation follow-up records
that completed state. Final validation, marketplace/catalog checks and staged
whitespace checks passed. No marketing snapshot was edited here.

## Authoring and evidence basis

The audit applied the official [Agent Skills specification](https://agentskills.io/specification),
[authoring best practices](https://agentskills.io/skill-creation/best-practices)
and [evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills),
plus local writing-great-skills and skill-creator. Changes follow observed
source defects, conditional resource use, executable fragile arithmetic and
checkable completion. Verifier equivalence controls precede heading changes;
semantic and format limitations are retained in each skill report.

All nine summaries are canonical metadata; activation descriptions remain agent
oriented. Marketplace validation retains nine skills and the existing six-task
Harbor suite; connected bid-leveling remains removed. New offline cases for the
three connected-workflow skills are explicitly separate from Harbor integration.
The PDF sample companion received a final presentation-only edit after its pair;
its report separates evaluated-package hashes from final companion hashes.

Versioned terminal logs have trailing whitespace normalized only; original log
bytes remain under coordinator thread-storage/original-log-whitespace. Model
outputs, baseline files and their hashes were not normalized. Full transcripts
and rendered PDF/image proofs remain outside the repo; bounded reusable results,
fixtures and tests are retained. No further comparisons are scheduled.
