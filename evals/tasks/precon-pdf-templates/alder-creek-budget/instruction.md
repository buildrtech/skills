Turn the attached budget export into a clean, print-ready budget document
for the owner meeting on Thursday. This one goes to a school board facilities
committee, not to estimators, so use the Warm Owner-Facing look rather than
the default technical styling.

Files in `/app/input/`:

- `alder-creek-budget-export.csv`: the budget export from our estimating
  system (line items by division, division subtotals, markups, totals, and
  two alternates).
- `handoff-notes.md`: how the export reads and the notes to print on the
  document.

Use my numbers exactly as exported; do not re-price, round, or change
anything. If something in the export does not add up, leave it as exported
and call it out, either in the document's notes or in a short
`/app/output/qa-notes.md`, so I can fix it in the estimate.

Write the HTML to `/app/output/budget-export.html`. That HTML is what gets
reviewed. If a PDF converter is available in this environment, also write
`/app/output/budget-export.pdf`; if not, skip the PDF and say so.
