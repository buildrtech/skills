# Proposal Builder verification

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
