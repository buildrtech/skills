# Bid leveling verification

## Revision 4.0.0: Markdown in, one workbook out

Previous revision: `b3ec0a7` (3.0.0), an interactive HTML bid tab, an Excel
workbook and a Markdown brief, built from PDF, XLSX and email bids by a
1,100-line engine. Mike asked for "significantly simpler, just markdown in and
spreadsheets out". Decisions he made for this revision:

- The brief is folded into a Questions sheet. The workbook is the only output.
- Totals stay live formulas, with cached values for viewers that don't calculate.
- Suggested plugs **count by default** (Carry "Yes", labelled "Suggested: <bidder>
  itemized $X"). 3.0.0 kept them out until accepted.
- A smaller sample: three bidders, eight scope lines, one missed addendum, one
  revised number.

### What changed

- Removed: the HTML tab and its templates, the brief, scenarios, the evidence
  registry, row classes, alternates, bond and tax basis, governing
  submissions, the extraction reference, and the PDF/XLSX/email sample bids.
  Bond, tax, alternates and a superseded number go in a bid's `notes`.
- `scripts/level.mjs` (one file, no dependencies) validates a short
  `bid-data.json`, levels the bids and writes four sheets: Leveled totals,
  Scope, Plugs, Questions. Money in the JSON is dollars.
- Leveled total = base + `SUMIFS` of plugs marked Carry "Yes". Open gaps are
  `COUNTIFS` of gaps without a carried figure. The lowest complete row uses
  `_xlfn.MINIFS`.
- The skill folder went from about 4,900 lines across 21 files to about 650
  lines across 9.

### Sample

Cedar Hollow clinic, package 09A. Northgate has the lowest base bid
($752,000) but misses Addendum 2's lobby finish, excludes sheathing, and is
unclear on firestopping, so it stays incomplete at $807,800 with one open gap.
Ridgeline is leveled on its next-morning revision ($789,500 to $822,100).
Prairie is the lowest complete leveled total at $803,800.

### Verification

- `node --test evals/tasks/bid-leveling/level.test.mjs`: 11 tests, including
  a byte comparison of the bundled workbook against a fresh build. They run in CI.
- Mutation check: seven deliberate breaks each failed between 1 and 6 tests:
  lowest instead of highest suggestion, suggestions for unclear scope, plugs
  on included lines, suggestions not carried, quotes not required, no
  addendum question, and an open-gap count that ignores blank plugs.
- LibreOffice 7 (headless): with every cached formula value stripped, the
  recalculated sheets matched the script's values. After setting Northgate's
  firestopping plug to $9,800, Ridgeline's batts Carry to "No" and Prairie's
  base to $900,000, LibreOffice recomputed Northgate as complete at $817,600
  and Ridgeline as incomplete at $799,300, and moved "lowest complete" to
  Northgate.
- Fresh-context comparison (Claude Code general-purpose subagent, model
  claude-opus-5-5, 2026-10-13): unfamiliar synthetic inputs in
  `fresh-input/` (07A TPO roofing, three bids, one entered plug). Same prompt
  for both revisions; the agent saw only the skill folder and the inputs.
  Expected: lowest base Crestline $412,000; lowest complete Harbor Peak
  $458,000; Crestline $468,200 with the entered $8,000 walkway plug and a
  $48,200 coping suggestion; Kettle River incomplete at $440,400 (crickets
  unclear, addenda unstated).
  - 4.0.0: every expected status, plug, total and question; ran the bundled
    script; one output file. It wrote one stray temp folder outside the work
    directory, then deleted it.
  - 3.0.0: the same extraction and the same "if accepted" totals. Its headline
    totals leave suggestions uncounted by design. It wrote five files
    (data, scenario, HTML, XLSX, brief).
  - Limitations: one run per revision, one model, no Codex lane.

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
