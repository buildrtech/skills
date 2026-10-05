# Bid leveling verification

## Revision 3.0.0: interactive bid-day tab

Previous revision: `7d8e853` (2.0.0), a Python script that printed a Markdown
comparison from per-bid extraction files and an estimator decisions file. This
revision replaces it. The script, its three reference docs, its samples, the
Millbrook roofing task, and the 2.0.0 review harness are removed.

### Why the redesign

- **The output was a report.** Bid day is iterative: the estimator plugs a gap,
  hears back from a bidder, carries the bond, and checks who is low again. 2.0.0
  needed a hand-edited decisions file and a rerun for each change. The tab
  recomputes in the browser and exports the same state to Excel.
- **Every gap started blank.** 2.0.0 never suggested a plug, so a first run was
  mostly "unresolved". 3.0.0 suggests the highest itemized price another bidder
  gave for the same row, labels it as a suggestion, and keeps the bid
  incomplete until the estimator accepts it. Unclear scope gets no suggestion.
- **The 2.0.0 review's P1 finding:** a plug on a row the extraction never
  recorded made that bidder complete. 3.0.0 requires every package row in
  every bid, and the scenario validator rejects plugs on anything but a gap on
  a base row.
- **The 2.0.0 review harness** depended on an unversioned `/tmp` checkout and
  overwrote committed evidence when replayed. It is removed, not repaired.

### What changed

- `scripts/leveling-core.mjs` is a pure module with no dependencies. It
  validates the data and the scenario, levels each bid, writes the HTML tab and
  the Markdown brief, and builds the XLSX workbook (a stored zip with a fixed
  timestamp, so the output is reproducible).
- Leveled total = base + plugs + adjustments + accepted alternates + carried
  basis items. A bid is complete only when every base gap has a plug, every
  accepted alternate is priced, and every carried basis item has a figure.
- Flags: itemized lines that don't add up to the total, addenda not
  acknowledged or not mentioned, outside-package scope carried in a bid (with a
  suggested removal), bidder-proposed alternates, and tax or bond not on a
  common basis.
- `scripts/level.mjs` inlines the core into `templates/tab.html`, so the browser
  recomputes with the same code. The page is pre-rendered and readable with
  scripts blocked.
- The workbook's totals are formulas: plugs and adjustments are `SUMIFS` over
  their sheets, so changing a plug's "Counts" cell in Excel recomputes the
  total.

### Sample

Cedar Hollow clinic, package 09A, four bidders, shipped as the source files an
estimator gets: a two-page PDF proposal, a bid-form XLSX with its cover email,
an email quote, and a one-line lump sum revised the morning after bids closed.
Planted problems:

- Summit's quote cites Addendum 1 only and misses the Addendum 2 lobby finish.
- Prairie's bid form adds up to $872,700 against a stated $871,200.
- Prairie carries $46,000 of ACT ceilings, which belong to package 09B.
- Summit offers a lift deduct nobody asked for.
- Bond and tax are on four different bases.

With the estimator's first pass (`estimator-scenario.json`), Prairie is the
lowest complete leveled total at $833,700. Ridgeline has the lowest base bid
($789,500), but it stays incomplete with eight open items.

### Verification

- `node --test evals/tasks/bid-leveling/leveling-core.test.mjs`: 18 tests,
  including exact byte comparison of the bundled HTML, brief, and XLSX against a
  fresh build. These run in CI.
- Mutation check: nine deliberate breaks each failed between 1 and 7 tests:
  - suggesting the lowest itemized price instead of the highest
  - counting unaccepted suggestions
  - allowing a plug on an included row
  - ignoring open gaps
  - wrong percent math
  - skipping the sum check
  - dropping HTML escaping
  - suggesting plugs for unclear scope
  - skipping the governing check
- XLSX opened in LibreOffice: the values match the tab. With cached values
  stripped and one plug switched to "No", LibreOffice recomputed Northgate from
  $893,500 to $852,300.
- Browser, Chromium:
  - accept a suggestion, enter a plug, reject an invalid amount
  - toggle Alternate 1, carry the bond
  - export to Excel, export the scenario, reset, then import it
  - 390px width with no horizontal scroll
  - the static view with scripts removed
  - axe: 0 violations

### Not yet tested

A fresh agent extracting bids it has never seen. The arithmetic is tested; the
extraction judgment (omitted versus unknown, matching alternates by scope) is
not. The removed Millbrook task graded a Markdown comparison from the 2.0.0
contract and needs a rewrite for the new outputs.
