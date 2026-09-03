# Checks

Every check `scripts/check_pay_app.py` performs, then the checks the agent
does by hand because they need documents or judgment the script does not
have. Read this at step 3 when you need to explain a finding, and at steps 4
through 9 for the manual checks.

## How the script reports

- Output is Markdown: a findings table sorted by severity (error, warning,
  info), then line, then column; followed by a G702 summary table of computed
  versus as-submitted values for Lines 1 through 9 plus the G703 column C
  total. Paste both tables into the memo unchanged.
- Each finding carries the line (`item description` from the schedule, or
  `G702` for cover-sheet checks), the column or cover-sheet line, a short
  check name, and a message that shows the arithmetic.
- Exit code 0: no error-severity findings. Exit code 1: at least one error.
  Exit code 2: the CSV could not be read (missing file, missing required
  column, unparseable amount); the message is on stderr and names the file
  and row.
- `--tolerance` (default 0.01) is the rounding allowance for every currency
  comparison. Percent comparisons use a fixed 0.05 percentage point allowance.
- `--jump-threshold` (default 50) is the percent of scheduled value billed in
  one period that triggers the percent-jump warning.
- `--retainage` applies to columns D + E; `--stored-retainage` applies to
  column F and defaults to the same percent. A per-line `retainage_pct` CSV
  column overrides both for that line and is applied to G.
- Checks that compare against an as-submitted value only run when that value
  is present: a stated CSV column for line checks, a `--g702-*` flag for
  cover-sheet checks. A skipped check is not a passed check; the memo must
  say which as-submitted values were not available.

Severity meanings: an **error** is an arithmetic or continuity fact that
must be corrected or explained before the application can move; a
**warning** is something a person must look at (backup, field progress, a
recomputed figure that differs because of an error elsewhere). The script
never emits info-severity findings today; the level is reserved.

## Line checks (every row of the current schedule)

| Check | Severity | Column | Rule | Message wording |
|---|---|---|---|---|
| `duplicate-item` | warning | A | The same item number appears on more than one row. | "Item number {A} also appears on row {n}; confirm which line is which before comparing to the prior application." |
| `negative-amount` | error | C, D, E, or F | Any of the four input columns is below zero. One finding per negative column. | "Column {X} is ({amount}); negative amounts belong on a credit change order line or a corrected prior period, not in this column." |
| `column-math` | error | G | Stated G differs from D + E + F by more than the tolerance. Runs only when `total_completed` is present. | "Column G as submitted is {G} but D + E + F = {D} + {E} + {F} = {sum}." |
| `percent-math` | error | G/C | Stated percent differs from (D + E + F) ÷ C by more than 0.05 points. Runs only when `percent_complete` is present and C is not zero. | "Percent complete as submitted is {p}% but G / C = {G} / {C} = {computed}%." |
| `balance-math` | error | H | Stated H differs from C − (D + E + F) by more than the tolerance. Runs only when `balance_to_finish` is present. | "Column H as submitted is {H} but C - G = {C} - {G} = {computed}." |
| `line-retainage` | error | I | Stated I differs from the retainage terms applied to the line: `--retainage` percent of D + E plus `--stored-retainage` percent of F, or the per-line `retainage_pct` of G. Runs only when `retainage` is present. | "Column I as submitted is {I} but {basis} = {computed}; difference {I − computed}." |
| `over-100-percent` | error | G | D + E + F exceeds C by more than the tolerance, on a line with C above zero. | "Total completed and stored {G} exceeds scheduled value {C} by {excess} ({p}% complete). Column G cannot exceed column C without a change order." |
| `zero-value-billing` | error | C | C is zero and D + E + F is not. | "Line bills {G} against a scheduled value of 0.00." |
| `stored-materials` | warning | F | F is greater than zero. Fires on every line with stored materials, every period, because the backup must be in every package. | "Stored materials of {F} billed this period; confirm bill of sale, insurance, location, and photos are in the backup." |
| `percent-jump` | warning | G (with prior) | With a prior schedule: this period's G ÷ C minus the prior period's G ÷ C is at or above the jump threshold. | "Percent complete moved from {before}% on the prior application to {after}% in one period (up {delta}% of scheduled value); confirm progress with the field or inspection log." |
| `percent-jump` | warning | E+F (no prior) | Without a prior schedule for that line: (E + F) ÷ C is at or above the jump threshold. | "This period bills {p}% of the line's scheduled value in one period (E + F = {amount}); confirm progress with the field or inspection log." |

## Continuity checks (only when `--prior` is given)

Lines are matched by item number (column A), so item numbers must be keyed
exactly as printed on both schedules.

| Check | Severity | Column | Rule | Message wording |
|---|---|---|---|---|
| `continuity` | error | D | The line exists on the prior schedule and this period's D differs from the prior period's D + E by more than the tolerance. Stored materials (prior F) are excluded on purpose. | "Column D is {D} but the prior application's D + E for this line is {pD} + {pE} = {sum}; difference {D − sum}." |
| `continuity` | error | D | The line does not exist on the prior schedule and D is not zero. | "Column D is {D} but no line with item {A} exists on the prior application." |
| `new-line` | warning | A | The line does not exist on the prior schedule and D is zero. | "Line {A} is not on the prior application; confirm it was added by an approved change order." |
| `scheduled-value-change` | warning | C | The line exists on the prior schedule and C differs from the prior C by more than the tolerance. | "Scheduled value changed from {pC} on the prior application to {C}; confirm an approved change order supports the change." |
| `missing-line` | error | A | A line on the prior schedule has no line with the same item number on this schedule. | "Line {A} was on the prior application with {pG} completed and stored but is missing from this application." |

## Cover sheet checks (G702)

"Computed" means recalculated from the schedule CSV and the contract terms
passed as flags. "As submitted" means the `--g702-*` value. Two kinds of
cover-sheet check exist: an as-submitted line checked against the
contractor's own other as-submitted lines (internal math, always an error
when it fails) and an as-submitted line checked against the recomputed value
(a warning when it fails only because an earlier finding already explains
the difference).

| Check | Severity | Cover-sheet line | Rule | Message wording |
|---|---|---|---|---|
| `contract-sum` | error | Line 3 / G703 C total | The schedule's column C total differs from `--contract-sum` + `--change-orders`. Always runs. | "Schedule of values totals {C total} but contract sum to date is {sum} (original {L1} + approved change orders {COs}); difference {sum − C total}. An approved change order may not be reflected on the schedule." |
| `change-orders` | error | Line 2 | `--g702-change-orders` differs from `--change-orders` (the approved log). | "Net change by change orders as submitted is {L2} but the approved change order log totals {COs}." |
| `contract-sum` | error | Line 3 | `--g702-contract-sum-to-date` differs from `--contract-sum` + `--change-orders`. | "Contract sum to date as submitted is {L3} but Line 1 + Line 2 = {L1} + {COs} = {sum}." |
| `total-completed` | error | Line 4 | `--g702-completed` differs from the sum of D + E + F across the schedule. | "Total completed and stored to date as submitted is {L4} but the G703 column G total is {computed}." |
| `retainage` | error | Line 5 | `--g702-retainage` differs from the retainage terms applied to the schedule totals. When the shortfall equals exactly the stored-materials percent of total F, the message adds the hint sentence. | "Retainage as submitted is {L5} but {r}% of completed work {D+E total} plus {s}% of stored materials {F total} = {computed}; difference {L5 − computed}." Hint: "The shortfall equals {s}% of stored materials ({F total}), so retainage appears not to have been applied to stored materials." |
| `earned-math` | error | Line 6 | `--g702-earned` differs from as-submitted Line 4 − as-submitted Line 5 (computed values stand in for any flag not given). | "Total earned less retainage as submitted is {L6} but Line 4 - Line 5 as submitted = {L4} - {L5} = {diff}." |
| `earned-recomputed` | warning | Line 6 | `--g702-earned` differs from computed Line 4 − computed Line 5. | "Total earned less retainage recomputed from the schedule and contract terms is {computed}, versus {L6} as submitted; difference {L6 − computed}." |
| `previous-certificates` | error | Line 7 | With `--prior` and `--g702-previous`: Line 7 differs from the prior schedule's total earned less retainage (prior D + E + F total minus retainage terms applied to it). | "Less previous certificates as submitted is {L7} but the prior application's total earned less retainage is {prior earned}; difference {L7 − prior earned}." |
| `due-math` | error | Line 8 | `--g702-due` differs from as-submitted Line 6 − as-submitted Line 7. | "Current payment due as submitted is {L8} but Line 6 - Line 7 as submitted = {L6} - {L7} = {diff}." |
| `due-recomputed` | warning | Line 8 | `--g702-due` differs from computed Line 6 − Line 7 (Line 7 taken from the flag, else from the prior schedule). | "Current payment due recomputed from the schedule and contract terms is {computed}, versus {L8} as submitted; difference {L8 − computed}." |
| `balance-math` | error | Line 9 | `--g702-balance` differs from as-submitted Line 3 − as-submitted Line 6. | "Balance to finish including retainage as submitted is {L9} but Line 3 - Line 6 as submitted = {L3} - {L6} = {diff}." |
| `no-prior` | warning | Line 7 / G703 D | `--prior` was not given. Always fires in that case so the memo cannot silently omit continuity. | "No prior-period schedule was provided, so column D continuity and Line 7 were not verified against the previous certificate." |

When `--g702-previous` is not given but `--prior` is, the script uses the
prior schedule's total earned less retainage as Line 7 for the computed
column. That is the amount the prior application requested, not necessarily
what was certified; see the manual check below.

## Manual checks the agent adds

The script sees numbers. These checks need the documents in the package,
the contract, or a question to the field. Record each as present, missing,
not required, or open; never judge sufficiency and never approve.

1. **Same schedule, same version.** Before trusting continuity, confirm the
   prior CSV came from the application as certified (not a draft) and that
   item numbers were not renumbered, split, or merged. A renumbered line
   shows up as one `missing-line` plus one `new-line`; say so instead of
   reporting two problems.
2. **Line 7 equals the certified amount.** Compare Line 7 to the architect's
   or owner's certificate on the prior application, not to the amount the
   contractor requested. If the prior application was certified for less than
   requested, this period's column D should be reduced to match; a `continuity`
   finding may be the contractor rolling forward the requested amount.
3. **Change order approvals.** Walk the approved change order log against
   three places: G702 Line 2 and the change order summary box; a G703 line
   for each approved change order (or a documented reallocation into existing
   lines); and any schedule line, description, or scheduled-value change with
   no approved change order behind it. List pending, disputed, or unsigned
   change orders separately and flag any billing against them. The script's
   `contract-sum`, `change-orders`, `new-line`, and `scheduled-value-change`
   findings point at the totals; the log tells you which change order.
4. **Stored materials backup.** For every line the script flagged
   `stored-materials`, check the package for what the contract requires,
   usually a bill of sale or paid invoice, an insurance certificate or
   endorsement covering the stored materials, the storage location (and
   whether off-site storage is permitted), and dated photos. Confirm the
   stored amount plus completed work does not exceed the scheduled value and
   that materials installed this period moved from F to E rather than staying
   in both. Note when a stored amount went down: that is normal when material
   is installed, and should match an increase in E.
5. **Retainage terms.** Confirm the percent used matches the contract for
   completed work and for stored materials (they can differ), whether a
   reduction milestone (for example 5 percent after 50 percent complete) has
   been reached by the contract's measure, and whether retainage held to date
   on the cover sheet equals the running total from prior certificates plus
   this period. The script only applies the percents it was given.
6. **Lien waivers.** Check for a conditional waiver for the current period
   from the contractor, an unconditional waiver for the prior period from the
   contractor, and the same pair from each subcontractor or supplier the
   contract requires (by tier or by dollar threshold). Match names and
   amounts to the application. Report present or missing; whether a waiver
   form is legally sufficient is a question for counsel, not this review.
7. **Certified payroll.** When the project requires it, check that a
   certified payroll report exists for every week in the billing period for
   the contractor and each subcontractor with labor on site. Report present,
   missing, or not required. Whether the reported wages comply is a wage
   determination and is out of scope.
8. **Certification and signatures.** The contractor's signature, date, and
   notary block if the form calls for one; the architect's or owner's
   certificate block left blank for them to complete.
9. **Cover sheet ties to the continuation sheet.** The script compares the
   cover sheet to its own recomputation of the schedule. Separately, compare
   the cover sheet to the footings printed on the continuation sheet: a
   cover sheet that ties to a mis-footed schedule and a cover sheet keyed
   from a different version of the schedule are different problems with
   different fixes.
10. **Overbilling signals for the field.** For every `over-100-percent`,
    `percent-jump`, and any line billed at 100 percent, and for general
    conditions billed ahead of elapsed contract time, write a question for
    the superintendent or inspector rather than a conclusion. Front-loading
    is a judgment about progress, not arithmetic.
11. **Unreadable or derived cells.** List every cell that was OCR'd with low
    confidence, left blank because it was unreadable, or derived because the
    form did not print it (for example column I computed from a single
    cover-sheet retainage figure). Each one is an open check, not a pass.
