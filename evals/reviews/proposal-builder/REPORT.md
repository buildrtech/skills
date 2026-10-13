# Proposal Builder verification

## Revision 2.0.0: RFP responses, compliance first

Previous revision: 1.0.0, a polished proposal PDF from a free-form brief. This
revision keeps pdfcn and Forme but changes the job: answer an owner's RFP after
a go decision, and prove it answers everything.

### What changed

- **Data.** `proposal.json` now carries:
  - the RFP's requirements (with points), required forms, and page limit
  - every source, with its kind and date
  - facts that can differ between sources
  - sections in the RFP's order, each listing the requirements it answers
- **Checks.** `templates/proposal-core.mjs` is dependency-free and shared by
  the renderer and `scripts/check.mjs`. The check writes
  `compliance-check.md`.
  - **Blocking:**
    - unanswered requirements
    - missing forms
    - counted pages over the limit, measured on the rendered PDF with Poppler
    - an unpriced fee
  - **Warnings:**
    - requirements answered only by unconfirmed claims from prior proposals
    - stale sources
    - values that differ between sources, when the proposal uses the older one
- **Review findings from 1.0.0, fixed:**
  - P1, $0 proposals: an absent fee is `unpriced`, and zero lump sums are
    rejected.
  - Sample provenance: every item cites a real page or library file.
  - PDF title mojibake: metadata is made ASCII.
  - Non-two-decimal currencies: now rejected instead of rounded.
  - Setup: no longer checks paths with `/`, now uses `npm.cmd` on Windows,
    and removes a half-built workspace on failure.
  - Long-name chapter opener: aligned to the top.
- **Renderer.** `render.tsx` renders:
  - the RFP's tab order
  - project and team cards
  - grouped narrative lists
  - the fee table with percentage lines
  - a forms checklist
  - a compliance matrix appendix

  Source lines print in `DRAFT`, and unconfirmed prior claims print in rust.

### Sample

Cedar Hollow County, Riverside Branch Library, a CM at Risk RFP with a 20-page
limit. Inputs:

- the RFP PDF
- Larkspur Builders' library (projects, people, safety, approach)
- two prior proposals as PDFs
- the user's fee and team email

Planted problems:

- Tab G (small and local business, 5 points) has no library content
- Form 2 isn't included
- the 2024 proposal carries a 2023 EMR and a GMP instead of the final cost
- a "within 3% of GMP" claim is lifted from the 2024 proposal

Rendered: 10 pages, 6 counted toward the limit. The check reports 2 blocking
items and 2 warnings.

### Verification

- `node --test evals/tasks/proposal-builder/proposal-core.test.mjs`: 12 tests,
  in CI, which now installs Poppler. They include:
  - the bundled compliance check reproduced byte for byte from the bundled PDF
  - per-section page measurement
  - fixing the planted gaps clears every blocking item
  - fee rules, validation, and CLI exit codes
- Mutation check: 10 deliberate breaks each failed between 1 and 4 tests.
- A fresh `setup.mjs` workspace installed the pinned pdfcn revision and
  rendered the sample.
  - All pages were rasterized and inspected.
  - One card alone on page 4 was fixed by tightening the card layout and
    shortening the section lead.
  - The PDF title reads cleanly in `pdfinfo`.
- `refresh-preview.py` reproduces the committed 225 KB page preview, which is
  under the catalog's 256 KB inline limit.

### Not yet tested

A fresh agent building a proposal from a library and an RFP it hasn't seen,
especially whether it leaves a requirement unanswered rather than writing
around it.

---

# Revision 1.0.0

Baseline: skills main `8adb4d30a1ce3266f564cdd52f76c391eadd7403`.
The broad PDF skill is replaced, not maintained as a compatibility alias.
Pay App Review and RFI Drafter and their task/review directories are removed.

Renderer: pdfcn registry `39c75c1abbbad7b89ad1d8d3ea740ef635818a4b`, Forme
0.25.0, React 19.2.5, tsx 4.21.0. A fresh workspace setup using the committed
lockfile succeeded, then the bundled sample rendered to five Letter pages.
Poppler extracted the base $144,500.25, credit –$1,250.50 and separate
option $8,425.50; `pdffonts` confirmed Helvetica and Times faces. All five page images were inspected. The HTML preview is
regenerated from actual PDF pages by `refresh-preview.py`.

Three Node tests cover exact cents/option exclusion, invalid structures/missing
sources/duplicate IDs/unsafe numbers/status and input immutability. Shared
Python tooling tests: 11 passed. All five skills and marketplace validate.

An additional synthetic probe (45 price rows, seven rows in every narrative
section) rendered to eleven pages; all 45 row labels survived text extraction
and no section heading was stranded at a page foot. This is a deterministic pagination
probe, not a claim that arbitrary long proposals are visually approved. Longer
commercial tables require repeated headings and page-by-page design review;
the instructions require editing the workspace template and re-rendering.

Caught during integration: Forme's page enum is `Letter`; styling the page
itself did not paint the cover; a pdfcn provider wrapping arrays/primitives
could discard content. The tested default uses pdfcn's professional theme,
actual text/table components, page margin props and a styled cover View.

Commands:

```bash
node skills/proposal-builder/scripts/setup.mjs /path/to/new-workspace
cd /path/to/new-workspace
npm run render -- /path/to/input-proposal.json /path/to/proposal.pdf
pdfinfo /path/to/proposal.pdf
pdftotext -layout /path/to/proposal.pdf /path/to/proposal.txt
pdftoppm -scale-to 1400 -png /path/to/proposal.pdf /path/to/page
```

No fresh model comparison or trigger-rate claim is made for this new skill.
This evidence establishes executable setup/rendering and arithmetic boundaries,
not autonomous proposal-writing quality. The unrelated workforce findings remain.
