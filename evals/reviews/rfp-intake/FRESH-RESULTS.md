# Fresh Case A results — tie, no demonstrated model-quality gain

Two fresh BB threads, one attempt per skill version, sequential. Both scored
**15/15** on `FRESH-RUBRIC.md` with no hard failure. This is one case on one
model, not a statistical success-rate estimate. The coordinating AI worker
performed source-by-source rubric review; no independent model judge or human
reviewer was used. The frozen rubric's phrase “Human source comparison” names
a manual-style rubric, not the identity of the actual evaluator.

| Rubric item | Baseline evidence | Revised evidence | Scores |
|---|---|---|---|
| 1. Recommendation / authority | Opens “Recommendation: No-go”; “Decision owner: Mike.” | Opens “Recommendation: No-go”; Mike retains final approval. | 1 / 1 |
| 2. Qualification supersession | Two within four years versus company's one; no assumed waiver. | Same controlling requirement and shortfall; A2 does not undo A1. | 1 / 1 |
| 3. Current deadline | March 15, 2027, 11:00 local town time. | Same, cited to A2. | 1 / 1 |
| 4. Delivery / superseded terms | Portal; paper not accepted; March 12 and 14:00 superseded. | Reconciliation table explicitly tracks all three stages. | 1 / 1 |
| 5. Post-bid list | 13:00 March 15 calculated from two hours; omission non-responsive. | Same, expressly derived; historical 16:00 also labeled derived/superseded. | 1 / 1 |
| 6. Other key dates | March 4 09:00 visit; March 8 noon questions, local time. | Same; internal meeting time remains unknown. | 1 / 1 |
| 7. Forms / alternates | Signed form, registration, addenda, both named alternates, blank-price trap. | Same full requirements with missing form/portal details separated. | 1 / 1 |
| 8. Bonds | 10% base plus all alternates; 100% final bonds within seven days. | Same; explicitly gives base + A + B calculation basis. | 1 / 1 |
| 9. Insurance | CGL 1M/2M, auto 1M, statutory WC; town builder's risk favorable. | Same; unchecked company capacity preserved. | 1 / 1 |
| 10. Labor | Weekly certified payroll; wage schedule missing, no assumed wage law. | Same, without inventing a statute/reporting system. | 1 / 1 |
| 11. Material risks | Operating continuity, missing abatement extent, time-only delay recovery with consequences. | Same; distinguishes identified versus unidentified hazardous materials. | 1 / 1 |
| 12. Warranty | One year after acceptance; acceptance date unknown. | Same, no invented extension. | 1 / 1 |
| 13. Source limits | P1–P8 and survey absent; no invented capacity, quantities, budget, award/start. | Same; separates inferred trade groupings from verified subcontract packages. | 1 / 1 |
| 14. Company criteria | Experience gate controls, capacity Unknown, reasons per criterion. | Same; explicitly rejects averaging away the No-go gate. | 1 / 1 |
| 15. Citations / follow-ups | Material facts cite sections/addenda; actions remain proposed. | Document keys and section/line citations; no submissions claimed. | 1 / 1 |

No model-output defect requiring a follow-up revision was identified by this
bounded rubric. Minor differences in supplemental ratings are judgment calls,
not contradictions of supplied company criteria. No extra trial was launched.

## Process and limitations

- Baseline `thr_99rywwrr6n`, environment `env_4ap5zny3r5`; revised
  `thr_pd5uamwkm2`, environment `env_gmr5cbi9dj`. Both under explicit project
  `proj_sxhtrh8yts`, fresh unmanaged directories containing only assigned skill,
  identical four input documents, and output directory. No parent conversation
  was forked and no hidden rubric or expected output was supplied.
- Both resolved Codex `gpt-6-astra`, medium reasoning, default service tier,
  auto permission mode. Recorded request-to-completion times: baseline 91.548s;
  revised 126.901s. Both below the 600-second cap. Revised queue delay was
  host `concurrency-limit`, distinct from model execution; no retry occurred.
- Transcripts show each read assigned SKILL.md, checklist, all bundled samples
  and prompts, and the four local inputs, then wrote only the requested review.
  No external service, parent thread, repository history, rubric, sibling
  output, or remote document read appears in either trace. Both runtime stops
  succeeded. Coordinator was notified to release the logical slot before grading.
- Both read every bundled reference/example/sample; this pair does **not** prove
  improved progressive disclosure. Baseline output 2,432 whitespace-delimited
  words; revised 3,158, an increase of 726 (~29.9%). No concision improvement
  or runtime advantage is established. Single-trial timings are observations,
  not benchmarks.
- Same host, normal BB injected tools/global skill catalog; the isolation is a
  fresh conversation plus separate assigned files and an explicit read boundary,
  not an OS-level denial of other filesystem reads. Trace review found no
  cross-lane/hidden reads. Explicit skill use means this is not trigger-rate proof.
- Input/skill hashes matched pre-run `fresh-input-hashes.json` after completion.
  `fresh-results.json` records output/transcript hashes and run metadata. Full
  artifacts remain in thread-storage, not committed evidence.

## Exact full evidence paths

Root: `/home/mikeastock/.bb/thread-storage/thr_4wnqeue5ke/paired/`

- Baseline transcript: `baseline-transcript.json`
- Revised transcript: `revised-transcript.json`
- Baseline output: `baseline/output/intake-review.md`
- Revised output: `revised/output/intake-review.md`
- Spawn metadata: `baseline-spawn.json`, `revised-spawn.json`
- Resolved revised environment: `revised-show.json`
- Runtime stops: `baseline-stop.json`, `revised-stop.json`
- Queue admission evidence: `revised-queue.json`
- Identical initial prompt: `prompt.txt` (bounded copy also `fresh-prompt.txt` here)

Missing-package Case B was not run. No live MCP/CRM persistence, PDF extraction,
OCR, rendering/theme, trigger-rate, broad matrix, or independent-judge evaluation
was performed. The demonstrated grader-fairness change is separate: the same
alternate-heading control fails the baseline verifier and passes the revision,
while five other identical control outcomes tie.
