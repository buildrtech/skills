# Precon PDF templates takeover

Version **1.1.0**: 12 renderer tests and nine fixture controls pass. Fresh
Codex pair **10/10 → 10/10, a tie**; revision avoids repairing cents formatting.

Scoped to `skills/precon-pdf-templates/`, its task, and this review directory.
No publication, shared-tool edits, production writes, or live MCP use.
Baseline: `9a62032a237cd7588f6f6c687021acc076cd6fb7`, preserved in Git and
`/tmp/skills-takeover-baseline-9a62032`. `skill-sha256.json` records file hashes.

## Findings and changes

- Budget and milestone generators rounded cents to dollars. The shipped
  milestone's 6793 cents printed as **$68**, rather than **$67.93**. They also
  turned absent money into zero. Shared `scripts/generator-utils.mjs` now
  formats safe integer cents exactly, including negative deducts, and rejects
  missing/null/string/fractional/unsafe money before writing HTML. Resume's
  unused formatter was removed; absent experience no longer prints an empty
  “years experience” claim.
- Theme swapping required agent-written CSS surgery, and the path placeholder
  misleadingly implied a renderer existed under every theme. All generators
  now accept `--theme <bundled-name>` from any working directory. It replaces
  palette variables and heading font while preserving family layout; the
  installed package remains intact. Unknown themes/extra arguments fail.
- Generators now declare Letter pages with 0.45-inch margins, keep headings
  and division headers with following content, and avoid splitting rows. The
  budget no longer forces alternates, markups, and totals into one large
  unsplittable group; only the totals block stays together. Re-rendered and
  inspected the changed pages. Blueprints retain their existing layouts.
- Schemas now describe nested monetary rows and required totals using bounded
  integer cents. Schema validation remains an agent preparation step; the
  renderer enforces money validity but is not a general JSON Schema engine.
- Main instructions now distinguish formatting supplied content from pricing,
  extraction, RFP decisions, and copywriting; route optional references by
  branch; make missing-input and output-path behavior concrete; and remove
  the artificial requirement to make a fix even when QA finds no problem.
  Version bumped **1.0.0 → 1.1.0**. Added the requested human-facing summary.
- Regenerated all three generator samples and the Cedar Hollow sample. Added
  Markdown sample companions derived from the actual JSON/HTML, with honest
  PDF verification context, using `refresh-sample-preview.py`.
- Corrected an oracle documentation arithmetic claim: 107,500 is approximately
  5% of 2,150,450, not exactly 5%; exactly 5% is 107,522.50. Preserved exported
  amounts and the original hand-transcribed oracle renderer/reference HTML.

## Verifier fairness, before prompt optimization

`instruction.md` requires faithful figures and Warm Owner-Facing styling; it
never requires internal CSS class names. Round 1 had added a hard gate on
those names. `valid-renamed-classes` changes selectors and class attributes
consistently without changing layout/content. The old grader rejected it:
reward **0**, while correctness/format/grounding were all **1**. Removed this
unsupported boundary gate. Bundled renderer use is a separate trace finding,
not the user-outcome grade. Historical 0/3 Codex scores are therefore not proof
of three substantive document failures and are not current reruns.

Theme grading previously scanned *all* sibling CSS (including unlinked files)
and rejected a valid linked override if old default colors remained in the
HTML. It now reads inline and linked sibling CSS in source order, strips CSS
comments, and uses final `:root` values. Retained positive linked-override and
negative unlinked/default-theme fixtures alongside existing substantive
negatives. No heading optimization was used to improve the correctness score.

| Deterministic comparison | Baseline | Revised |
|---|---:|---:|
| Same 12 renderer tests | 3 pass / 9 fail | 12 pass / 0 fail |
| Renamed-class valid document | reward 0 (false reject) | reward 1 |
| Known-good document | reward 1 | reward 1 |
| Default theme, recomputed totals, silent gap, sample substitution, missing output | fail | fail |
| Final fixture suite | five original controls behaved as expected | 9/9 expected outcomes |

Evidence: `baseline-renderers.txt`, `revised-renderers.txt`,
`baseline-fixtures.txt`, `before-fairness.txt`, `revised-fixtures.txt`.
These are local synthetic fixture replays, not model outcomes or MCP evidence.

## Commands and actual verification

Run from repository root. UV caches/tools were redirected to `/tmp/precon-uv-*`;
no global packages or skills were changed.

```sh
PRECON_SKILL=/tmp/skills-takeover-baseline-9a62032/skills/precon-pdf-templates node --test evals/reviews/precon-pdf-templates/test-renderers.mjs
node --test evals/reviews/precon-pdf-templates/test-renderers.mjs
UV_TOOL_DIR=/tmp/precon-uv-tools UV_CACHE_DIR=/tmp/precon-uv-cache python3 evals/scripts/check_fixtures.py evals/tasks/precon-pdf-templates/alder-creek-budget
UV_TOOL_DIR=/tmp/precon-uv-tools UV_CACHE_DIR=/tmp/precon-uv-cache uv run --with jsonschema python evals/reviews/precon-pdf-templates/test-schemas.py
UV_TOOL_DIR=/tmp/precon-uv-tools UV_CACHE_DIR=/tmp/precon-uv-cache uv run --with pyyaml python tools/validate_skills.py skills/precon-pdf-templates
python3 evals/reviews/precon-pdf-templates/refresh-sample-preview.py
git diff --check -- skills/precon-pdf-templates evals/tasks/precon-pdf-templates evals/reviews/precon-pdf-templates
```

All revised commands passed. First fixture attempt hit UV's read-only default
tool directory; setting `UV_TOOL_DIR` resolved it. Host Python lacked
`jsonschema`/`yaml`; isolated UV dependencies resolved validation. These were
runner setup failures, not skill failures.

Actual renderer executions covered the three bundled sample-data files,
Cedar Hollow JSON, and Alder Creek oracle JSON with the warm theme. Actual
Chrome 149 PDF conversion used `--headless --disable-gpu
--no-pdf-header-footer --user-data-dir=/tmp/precon-chrome-profile
--print-to-pdf=<absolute-pdf> file://<absolute-html>`. `pdfinfo`, `pdftotext
-layout`, and `pdftoppm -scale-to 1000 -png` checked the results.

Inspected all pages: Alder Creek 2, Cedar Hollow 2, milestone 1, resume 1.
No clipped columns, missing money, broken deduct signs, or blank extra pages
were observed. Alder Creek's second page repeats table headers and prints
both exported 294,100.00 and the quantified 2,700 discrepancy. Milestone now
prints 67.93. Browser-computed warm heading and header colors were
`rgb(63, 46, 36)`, heading font Liberation Serif/DejaVu Serif, with no horizontal
overflow at 1000px. Markdown previews reflect these actual renders.

Full HTML/PDF/PNG/text/browser proof is intentionally outside the repo at:
`/home/mikeastock/.bb/thread-storage/thr_mtamhw7f8u/precon-takeover/rendered/`.
`rendered-sha256.json` retains exact artifact paths and hashes.

## Fresh paired evaluation

Coordinator approved **A only**, sequential baseline/revised, one attempt each,
10-minute execution cap. B (missing milestone cost) remains a deterministic
script/schema negative; no fresh missing-input or trigger-rate claim is made.

Inputs and prompt: `paired/input/`, `paired/PROMPT.md`. Expected results and
checker: `paired/EXPECTED.json`, `paired/check-output.py`, hidden outside both
agent workspaces. Each workspace contains only its assigned skill, identical
input, and prompt. Same project defaults: Codex **gpt-6-astra**, medium reasoning,
default service tier, auto permission. The evaluator prompt restricts work to
output and forbids other agents/network/outside-workspace inspection. This
is context isolation, not a filesystem security boundary against a hostile agent.

- Baseline: `thr_aja4h52gia`, environment `env_67uacm567z`, workspace
  `/tmp/precon-paired-A-20260907/baseline`. Completed; independently passed
  signed exported amount occurrence checks in HTML/PDF, gap disclosure,
  requested computed color/font, and one-page Letter visual inspection.
  It copied/adapted the bundled renderer to fix currency precision, restyled
  the output, and corrected an overflowing footer. The baseline therefore
  succeeded despite the underlying script defect.
- Revised: `thr_e6zdsjdchh`, environment `env_rjmu2egju7`, workspace
  `/tmp/precon-paired-A-20260907/revised`. Completed and stopped. It ran the
  assigned bundled renderer with `--theme warm-owner-facing`, then adjusted
  output spacing after inspecting a reconciliation note spilling onto page 2.
  Its final one-page Letter PDF passed the same ten independent checks and
  visual inspection. The trace confirms actual image inspection and exact
  signed amount checks. No currency/renderer rewrite was necessary.

**Outcome: tie, both pass.** Baseline completed its turn in 73.52 seconds;
revised in 88.24 seconds (provider turn timestamps, excluding host queue).
This one attempt provides no speed or overall model-success improvement
claim. It demonstrates that the revised agent used the tested renderer/theme
path without repairing its monetary behavior. Both still needed a spacing
fix, so visual QA remains necessary. Both models/settings match exactly.
The revised run was temporarily queued by the host concurrency-limit plugin
at 32/32; it was neither duplicated nor bypassed. Both executions were below
the approved ten-minute cap. Coordinator was notified immediately after the
pair completed and the logical slot was released.

`paired/baseline-checks.json`, `paired/revised-checks.json`, and
`paired/results.json` preserve rubric results, model/settings, timing,
workspace/thread IDs, exact assigned skill hashes, and artifact/trace hashes.
No additional fresh cases or review workers were launched.

Baseline full trace:
`/home/mikeastock/.bb/thread-storage/thr_mtamhw7f8u/precon-takeover/baseline-transcript.json`.
Revised full trace: sibling `revised-transcript.json`.
Independent checks, original deliverables, and page proof: sibling
`paired-baseline/` and `paired-revised/` directories. Reviewed each final PDF
page independently; both retain the deduct and explicitly exclude alternates.

## Limits and authoring basis

No production data or live MCP calls; no API invention or remote writes. Only
synthetic local fixtures. No broad model matrix, no independent review worker,
no chat-app coverage, no fresh B/near-miss tests. WeasyPrint, supplied brand fonts,
all eight alternate theme combinations, arbitrary long proposal blueprints,
and automatic division-label repetition across pages were not visually tested.
The two long-budget PDFs demonstrate column header repetition, not repeated
division labels. Existing old Riverside generator samples contain inconsistent
exported totals; preservation smoke tests do not certify their arithmetic.

The fixture grader is still a heuristic: `:root` scanning is not a full CSS
cascade (imports, specificity, media rules, component colors, equivalent RGB
styles require browser review). Existing amount presence/grounding checks are
not complete row-identity or sign-aware accounting verification; the fresh
paired checker separately checks signed amount multiplicities. Do not treat
one all-green fixture suite as exhaustive document correctness.

Applied [Agent Skills specification](https://agentskills.io/specification),
[authoring best practices](https://agentskills.io/skill-creation/best-practices),
and [evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills):
coherent invocation, conditional reference reads, deterministic helpers for
fragile work, checkable delivery, and fresh paired behavior evaluation separate
from samples. Also read the takeover audit/handoff, local writing-great-skills,
BB skill-creator, and all skill resources. RFI air-content review is outside
this skill's ownership and was not modified here.

## Final sample presentation correction

After the fresh pair, root's 390px visual review requested a prose-only sample
change: the output companion now leads with Cedar Hollow's project heading,
a brief layout link, and the unchanged date/preparer/tables. The input companion
says "for this example budget". The generator for these companions was updated
so regeneration preserves that presentation. Chrome 149 inspection occurred on
2026-09-07; those QA details belong here rather than above the sample content.
No JSON, HTML, renderer, monetary value or table changed. Fresh PDF results and
the existing revised hash group describe the earlier evaluated package;
`current_after_preview_copy` records the final package after this copy edit.
