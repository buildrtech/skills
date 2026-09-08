# G702 and G703 fields

The AIA G702 (Application and Certificate for Payment) is the one-page cover
sheet. The G703 (Continuation Sheet) is the schedule of values behind it.
Most owner-custom or subcontractor forms use the same nine cover-sheet lines
and the same nine columns under different labels, so this reference uses the
AIA names and the letter and line numbers that every finding cites.

Read this once at step 2 of the workflow, before extracting the schedule.

## G702 cover sheet lines

| Line | Field | Comes from | Must equal |
|---|---|---|---|
| 1 | Original contract sum | The signed contract | The contract, not the application |
| 2 | Net change by change orders | The change order summary box on the G702 (additions minus deductions, approved only) | The approved change order log total |
| 3 | Contract sum to date | Line 1 + Line 2 | The G703 column C total |
| 4 | Total completed and stored to date | The G703 column G total | Sum of column D + E + F across every line |
| 5 | Retainage | 5a: percent of completed work (columns D + E); 5b: percent of stored materials (column F); total 5a + 5b | The G703 column I total when the sheet carries a retainage column |
| 6 | Total earned less retainage | Line 4 minus Line 5 | |
| 7 | Less previous certificates for payment | Cumulative previous certificates for payment | Reconcile certificate history; under full certification this ties to prior cumulative Line 6 |
| 8 | Current payment due | Line 6 minus Line 7 | |
| 9 | Balance to finish, including retainage | Line 3 minus Line 6 | |

Below the nine lines the G702 has a change order summary box: total
additions and total deductions approved in previous months by the owner, plus
those approved this month, netting to Line 2. Below that are the contractor's
certification (signature, date, notary block) and the architect's certificate
(amount certified for this period, which may differ from Line 8 and adds to
cumulative previous certificates on the next application).

Relationships the script enforces on the cover sheet:

- Line 1 + Line 2 = Line 3
- Line 3 = G703 column C total
- Line 4 = G703 column G total
- Line 5 = retainage percent applied to (D + E) plus the stored-materials
  percent applied to F, across all lines
- Line 4 − Line 5 = Line 6
- Line 6 − Line 7 = Line 8
- Line 3 − Line 6 = Line 9
- Line 7 = cumulative previous certificates, independently reconciled

## G703 continuation sheet columns

| Column | Field | Comes from | Must equal |
|---|---|---|---|
| A | Item number | The schedule of values; stable from period to period | Same item number for the same scope as the prior application |
| B | Description of work | The schedule of values | |
| C | Scheduled value | The approved schedule of values, plus a line for each approved change order | Sum across lines = G702 Line 3 |
| D | Work completed from previous application | Column D + E of the prior application for the same line | Prior D + E exactly |
| E | Work completed this period | The contractor's assessment of progress this period | Field progress; not a computed value |
| F | Materials presently stored, not in D or E | Materials bought and stored (on site, or off site if allowed) but not yet installed | Backup: bill of sale, insurance, location, photos |
| G | Total completed and stored to date | D + E + F | Sum across lines = G702 Line 4 |
| G/C | Percent complete | G ÷ C, as a percentage | |
| H | Balance to finish | C − G | |
| I | Retainage | Retainage percent × (D + E) plus stored percent × F, or a single percent × G when the terms do not distinguish | Sum across lines = G702 Line 5 |

Some forms split column I into retainage on completed work and retainage on
stored materials; some omit column I and carry retainage only on the cover
sheet. Some forms print a separate "from previous application" and "this
period" pair for stored materials as well. Map whatever the form shows into
the CSV columns below and note in the memo any column that had to be derived.

## Period-to-period movement

- Work installed this period goes in E. Materials that were in F last period
  and were installed this period move out of F and into E; they are never
  counted in both. So F can go down from one period to the next while D + E
  goes up.
- Column D of this period equals D + E of the prior period, never D + E + F.
  Stored materials do not roll into D; they either stay in F or move to E
  when installed.
- Column C only changes when an approved change order adds, deducts, or
  reallocates scheduled value. A change order is normally its own line with
  its own item number, added at the bottom of the schedule.
- Line 7 is cumulative prior certification, not just the last period's
  increment. Do not infer it by applying today's retainage rate to a prior
  schedule. A reduced certificate does not identify which work lines changed;
  request the documented allocation or revised schedule before altering D.

## CSV layout the script reads

`scripts/check_pay_app.py` reads one CSV per period. Header names are matched
case-insensitively; extra columns are ignored; a row whose item is "total",
"totals", or "grand total" is skipped, as is any row with a blank item and
description.

| CSV column | G703 column | Required | Notes |
|---|---|---|---|
| `item` | A | yes | Keep exactly as printed, including leading zeros, so findings cite the line the reader can find |
| `description` | B | yes | Keep as printed; quote if it contains commas |
| `scheduled_value` | C | yes | |
| `previous_completed` | D | yes | |
| `this_period` | E | yes | |
| `stored_materials` | F | yes | Use explicit 0 only when the source establishes no stored materials |
| `retainage_pct` | | no | Independent contract rate, not an as-submitted rate; when present the script applies it to G and ignores the `--retainage` flags for that line |
| `total_completed` | G | no | The value printed on the form; checked against D + E + F |
| `percent_complete` | G/C | no | As printed; checked against G ÷ C within 0.05 percentage points |
| `balance_to_finish` | H | no | As printed; checked against C − G |
| `retainage` | I | no | As printed; checked against the retainage terms |

Amounts may be written as `1,234.56`, `$1,234.56`, `(500.00)` for negative,
or `10%` for percent columns; the script strips the punctuation. When a value
on the form is unreadable, leave the cell blank rather than guessing: a blank
optional column skips that check; a blank required amount stops the checker
with exit 2 and a file/row diagnostic. Resolve it or mark the schedule review
incomplete; never substitute zero for an unreadable amount.

The cover sheet is not read from a file. Pass each G702 line as submitted
with the matching flag (`--g702-change-orders` for Line 2 through
`--g702-balance` for Line 9) so the script can compare it with what the
schedule and the contract terms support. Line 1 is `--contract-sum`, which
comes from the contract, and the approved change order total is
`--change-orders`, which comes from the change order log, never from the
application.

Pass `--prior-certified` for the independently verified cumulative prior
certificate total; `--g702-previous` is only the current submitted Line 7.
Without certificate history the computed Line 7 and Line 8 remain `n/a`.
Unknown contract sum, change-order total, or retainage terms may be omitted;
checks depending on them remain open. Explicit zero means known zero.

Field semantics follow the [AIA G702 instructions](https://help.aiacontracts.com/hc/en-us/articles/1500009308242-instructions-g702-1992-application-and-certificate-for-payment).
