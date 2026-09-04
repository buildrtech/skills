# QA notes: Alder Creek Elementary School Classroom Addition budget export

Document: `budget-export.html` (construction budget export generator,
Warm Owner-Facing theme). Every figure is printed exactly as exported from
`alder-creek-budget-export.csv`; nothing was re-priced, rounded, or
reconciled.

## One item does not foot

Division 09 Finishes: the export prints a division subtotal of $294,100,
but the four line items under it sum to $291,400.

| Line item | Amount |
|---|---|
| Gypsum board partitions and ceilings | $136,400 |
| Acoustic ceiling tile | $47,600 |
| Resilient flooring and carpet tile | $74,400 |
| Painting and wall protection | $33,000 |
| **Sum of line items** | **$291,400** |
| **Division 09 subtotal as exported** | **$294,100** |
| **Difference** | **$2,700** |

The exported subtotal is what the document shows, because the handoff notes
say the subtotal rows are printed by the estimating system rather than
computed from the rows above, and because the direct cost subtotal of
$2,150,450 is the sum of the exported division subtotals. Correcting the
Division 09 line items or the subtotal at the source would move the direct
cost subtotal and the grand total, so the fix belongs in the estimate, not
in this document.

## Everything else reconciles

- Direct cost subtotal $2,150,450 equals the ten exported division subtotals.
- Markups $428,000 equal the four markup rows ($187,200 + $47,300 +
  $107,500 + $86,000).
- Grand total $2,578,450 equals $2,150,450 + $428,000.
- Estimating contingency $107,500 is 5.00% of the $2,150,450 direct cost,
  matching the handoff note.
- Alternate 1 ($64,800) and Alternate 2 (-$18,200) are shown in their own
  table and are excluded from the grand total, as the export intends.

## Production notes

- Template: `templates/construction-budget-export/field-ready-technical/render.mjs`.
- Theme: `themes/warm-owner-facing.css`, applied by replacing the generated
  document's `:root` block, so the whole page picks up the warm palette.
- No PDF converter (headless Chrome, Chromium, or WeasyPrint) is installed
  in this environment, so no PDF was produced. Print `budget-export.html`
  to PDF from a browser at US Letter with background graphics on.
