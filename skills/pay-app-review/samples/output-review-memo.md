# Pay app review: Pinecrest Cross-Dock Warehouse, Building B, Application No. 2, period ending August 31, 2026

**Status:** Recommend hold for review
**In one line:** The cover sheet requests $343,850.00 but does not tie to its own continuation sheet (Line 4 is keyed as $738,500.00 against a G703 column G footing of $783,500.00), the approved change order CO-001 for $18,500.00 is missing from Lines 2 and 3 and from the schedule, and $6,800.00 of retainage was not withheld on stored materials.

## Summary

Harlow Brothers Construction submitted Application No. 2 for $343,850.00
(G702 Line 8 as submitted) for the period ending August 31, 2026. This review
covered the G702 cover sheet, the 12-line G703 continuation sheet, the
Application No. 1 continuation sheet as certified August 5, 2026, the change
order log dated September 1, 2026, and the contract terms in Articles 3, 5,
and General Conditions 9.3.2 as supplied by the reviewer. The script found 9
errors and 5 warnings. Four things drive the hold: the cover sheet does not
reflect CO-001 and neither does the schedule of values (G702 Lines 2 and 3,
G703 column C total); Line 4 on the cover sheet is $45,000.00 below the
continuation sheet's column G footing, so every cover-sheet line from 4 down
is wrong; column D on line 03 is $5,000.00 higher than what was certified
last period; and line 07 is billed at 104.44 percent of its scheduled value
with $20,000.00 of stored materials that have no backup. This memo prepares
the review. It is not an approval, certification, or rejection of payment.

## Contract terms used

| Term | Value | Source |
|---|---|---|
| Original contract sum | $2,450,000.00 | Agreement, Article 4 (reviewer-supplied) |
| Approved change orders | $18,500.00: CO-001, approved August 14, 2026 | Change order log dated September 1, 2026 |
| Pending change orders | $12,300.00: CO-002, pending owner signature; not approved | Change order log dated September 1, 2026 |
| Retainage on completed work | 10% | Agreement, Article 5.1.7 |
| Retainage on stored materials | 10% | Agreement, Article 5.1.7 |
| Retainage reduction milestone | Not reached. Total completed and stored recomputed from the schedule is $783,500.00 against a contract sum to date of $2,468,500.00, 31.7%; the milestone is 50% and needs owner's written approval, none issued. | Agreement, Article 5.1.8; script G702 summary Lines 3 and 4 |
| Stored materials rules | On-site only; paid invoice or bill of sale, insurance certificate naming owner, location, dated photos | General Conditions 9.3.2 |
| Lien waiver requirement | Conditional current period and unconditional prior period from contractor and every subcontractor or supplier billing over $25,000.00 in the period | Agreement, Article 5.1.9 |
| Certified payroll requirement | Not required | Agreement, Article 3 |
| Prior application certified | $323,100.00 on August 5, 2026, full amount requested | Architect's certificate, Application No. 1 |

## Script findings

Command run from the skill directory:

```
python3 scripts/check_pay_app.py samples/input-pay-app-2.csv \
  --prior samples/input-pay-app-1.csv \
  --contract-sum 2450000 --change-orders 18500 --retainage 10 \
  --g702-change-orders 0 --g702-contract-sum-to-date 2450000 \
  --g702-completed 738500 --g702-retainage 71550 --g702-earned 666950 \
  --prior-certified 323100 --g702-previous 323100 --g702-due 343850 --g702-balance 1783050
```

Exit code 1 (error-severity findings present). Output unchanged:

## Findings (9 error, 5 warning, 0 info)

| # | Severity | Line | Column | Check | Finding |
|---|---|---|---|---|---|
| 1 | error | 03 Concrete foundations and slab | D | continuity | Column D is 84,500.00 but the prior application's D + E for this line is 0.00 + 79,500.00 = 79,500.00; difference 5,000.00. |
| 2 | error | 05 Structural and miscellaneous steel | I | line-retainage | Column I as submitted is 7,200.00 but 10% of D + E plus 10% of F = 12,000.00; difference (4,800.00). |
| 3 | error | 07 Doors, frames, and hardware | G | over-100-percent | Total completed and stored 47,000.00 exceeds scheduled value 45,000.00 by 2,000.00 (104.44% complete). Column G cannot exceed column C without a change order. |
| 4 | error | 07 Doors, frames, and hardware | I | line-retainage | Column I as submitted is 2,700.00 but 10% of D + E plus 10% of F = 4,700.00; difference (2,000.00). |
| 5 | error | G702 | Line 2 | change-orders | Net change by change orders as submitted is 0.00 but the approved change order log totals 18,500.00. |
| 6 | error | G702 | Line 3 | contract-sum | Contract sum to date as submitted is 2,450,000.00 but Line 1 + Line 2 = 2,450,000.00 + 18,500.00 = 2,468,500.00. |
| 7 | error | G702 | Line 3 / G703 C total | contract-sum | Schedule of values totals 2,450,000.00 but contract sum to date is 2,468,500.00 (original 2,450,000.00 + approved change orders 18,500.00); difference 18,500.00. An approved change order may not be reflected on the schedule. |
| 8 | error | G702 | Line 4 | total-completed | Total completed and stored to date as submitted is 738,500.00 but the G703 column G total is 783,500.00. |
| 9 | error | G702 | Line 5 | retainage | Retainage as submitted is 71,550.00 but 10% of completed work 715,500.00 plus 10% of stored materials 68,000.00 = 78,350.00; difference (6,800.00). The shortfall equals 10% of stored materials (68,000.00), so retainage appears not to have been applied to stored materials. |
| 10 | warning | 05 Structural and miscellaneous steel | F | stored-materials | Stored materials of 48,000.00 billed this period; confirm bill of sale, insurance, location, and photos are in the backup. |
| 11 | warning | 07 Doors, frames, and hardware | F | stored-materials | Stored materials of 20,000.00 billed this period; confirm bill of sale, insurance, location, and photos are in the backup. |
| 12 | warning | 07 Doors, frames, and hardware | G | percent-jump | Percent complete moved from 0.00% on the prior application to 104.44% in one period (up 104.44% of scheduled value); confirm progress with the field or inspection log. |
| 13 | warning | G702 | Line 6 | earned-recomputed | Total earned less retainage recomputed from the schedule and contract terms is 705,150.00, versus 666,950.00 as submitted; difference (38,200.00). |
| 14 | warning | G702 | Line 8 | due-recomputed | Current payment due recomputed from the schedule and contract terms is 382,050.00, versus 343,850.00 as submitted; difference (38,200.00). |

## G702 summary: computed from the schedule and contract terms versus as submitted

| Line | Field | Computed | As submitted | Difference |
|---|---|---|---|---|
| 1 | Original contract sum | 2,450,000.00 | 2,450,000.00 | 0.00 |
| 2 | Net change by change orders | 18,500.00 | 0.00 | (18,500.00) |
| 3 | Contract sum to date | 2,468,500.00 | 2,450,000.00 | (18,500.00) |
| G703 C | Schedule of values total | 2,450,000.00 | n/a | n/a |
| 4 | Total completed and stored to date | 783,500.00 | 738,500.00 | (45,000.00) |
| 5 | Retainage | 78,350.00 | 71,550.00 | (6,800.00) |
| 6 | Total earned less retainage | 705,150.00 | 666,950.00 | (38,200.00) |
| 7 | Less previous certificates for payment | 323,100.00 | 323,100.00 | 0.00 |
| 8 | Current payment due | 382,050.00 | 343,850.00 | (38,200.00) |
| 9 | Balance to finish, including retainage | 1,763,350.00 | 1,783,050.00 | 19,700.00 |

Lines checked: 12. Retainage basis: 10.00% of completed work, 10.00% of stored materials; explicit per-line overrides apply. Tolerance: 0.01. Percent-jump threshold: 50% of scheduled value in one period.

This output prepares a review. It is not an approval, certification, or rejection of payment.

## Findings the script cannot make

- **Cover sheet does not tie to the continuation sheet (G702 Line 4).** The
  G703 as printed foots column G to $783,500.00 (cover sheet package, footings
  table), and the script recomputes the same $783,500.00 from D + E + F. The
  cover sheet shows $738,500.00 on Line 4, which reads as a transposition of
  the first three digits. Lines 6, 8, and 9 as submitted are internally
  consistent with the wrong Line 4 (the script raised no `earned-math`,
  `due-math`, or `balance-math` finding), so the cover sheet was computed
  from the keyed figure rather than from the schedule. Every cover-sheet line
  from 4 down changes on resubmission.
- **CO-001 is not reflected anywhere in the application.** The change order
  log shows CO-001 approved August 14, 2026 for $18,500.00. It is absent from
  G702 Line 2 (as submitted $0.00), from the change order summary box (all
  zeros), and from the G703, which has no line for it and still foots column
  C to the original $2,450,000.00. Script findings 5, 6, and 7 are all this
  one omission. CO-002 ($12,300.00) is pending and correctly absent; no line
  on the schedule bills against it.
- **Line 03 column D rolls forward more than was certified.** Application
  No. 1 was certified for the full amount requested, so the certified column
  D + E for line 03 is $79,500.00 (input-pay-app-1.csv, line 03, columns D
  and E). This application shows $84,500.00 in column D (input-pay-app-2.csv,
  line 03, column D), $5,000.00 more, with no revised prior application on
  file. Column G, the percent, column H, and column I on line 03 are all
  computed from the overstated D, so they are each off by the same $5,000.00
  (retainage by $500.00) even though the script's line math on them ties.
- **Line 07 is billed over its scheduled value with unsupported stored
  materials.** Column E $27,000.00 plus column F $20,000.00 equals $47,000.00
  against a scheduled value of $45,000.00 (input-pay-app-2.csv, line 07). No
  change order in the log adds scope or value to doors, frames, and hardware,
  and the package contains no stored materials backup for this line. Column D
  was $0.00 on the prior application, so the line moved from nothing to over
  complete in one period. Question for the field: the August daily reports
  should show whether frames were set this period; hardware and doors usually
  arrive late in a job, so $20,000.00 stored on this line needs the invoice
  and photos before it is even considered.
- **Retainage was withheld on completed work only.** Column I on lines 05
  and 07 equals 10 percent of D + E and nothing on column F (script findings
  2 and 4, together $6,800.00), and G702 Line 5b shows 0 percent of stored
  material. Article 5.1.7 sets 10 percent on both. Application No. 1 did
  withhold retainage on the $72,000.00 stored on line 05 (input-pay-app-1.csv,
  line 05, column I $7,200.00), so this is a change in practice, not a
  contract interpretation question.
- **Line 05 stored materials movement is correct.** The $72,000.00 stored on
  line 05 last period moved to column E this period and column D stayed at
  $0.00 (input-pay-app-1.csv and input-pay-app-2.csv, line 05), which is the
  right treatment for material installed this period. The new $48,000.00 in
  column F has a paid invoice, dated photos, and a stated on-site location,
  but no insurance certificate (package document list).
- **Line 7 ties.** $323,100.00 as submitted equals the amount certified on
  Application No. 1 (architect's certificate) and the prior schedule's total
  earned less retainage (script G702 summary, Line 7).
- **Retainage reduction milestone is not reached.** See the contract terms
  table; no finding, noted so the reviewer does not have to re-check.
- **Nothing was derived or unreadable.** Both schedules were supplied as
  CSV with every column populated, so no cell was OCR'd or estimated.

## Items on hold for a human decision

| # | Item | Line / column | Amount in question | Source | What would clear it |
|---|---|---|---|---|---|
| 1 | Cover sheet Line 4 keyed as $738,500.00; continuation sheet foots $783,500.00 | G702 Line 4, and Lines 6, 8, 9 that follow from it | $45,000.00 difference; the whole cover sheet | G702 as submitted; G703 footings; script finding 8 | A reissued, signed G702 whose Line 4 equals the corrected G703 column G total |
| 2 | CO-001 missing from Lines 2 and 3 and from the schedule of values | G702 Line 2, Line 3; G703 column C total | $18,500.00 | Change order log, CO-001; script findings 5, 6, 7 | Line 2 = $18,500.00, Line 3 = $2,468,500.00, a G703 line for CO-001 (or a documented reallocation) so column C foots to $2,468,500.00 |
| 3 | Column D overstated against the certified prior period | G703 line 03, column D | $5,000.00 ($500.00 of it retainage) | input-pay-app-2.csv line 03 D vs input-pay-app-1.csv line 03 D + E; Application No. 1 certificate; script finding 1 | Column D corrected to $79,500.00, or a revised and certified Application No. 1 showing $84,500.00 |
| 4 | Line billed at 104.44 percent with no change order | G703 line 07, columns E, F, G | $2,000.00 over scheduled value; $47,000.00 billed on the line | input-pay-app-2.csv line 07; change order log; script findings 3 and 12 | Column G at or below $45,000.00 with the field confirming installed work, or an approved change order adding value to this line |
| 5 | Stored materials on line 07 with no backup | G703 line 07, column F | $20,000.00 | input-pay-app-2.csv line 07 F; package document list; script finding 11 | Paid invoice or bill of sale, insurance certificate, on-site location, dated photos per GC 9.3.2 |
| 6 | Stored materials on line 05 missing the insurance certificate | G703 line 05, column F | $48,000.00 | input-pay-app-2.csv line 05 F; package document list; script finding 10 | Insurance certificate naming the owner for the stored value per GC 9.3.2 |
| 7 | Retainage not withheld on stored materials | G703 lines 05 and 07, column I; G702 Line 5b | $6,800.00 ($4,800.00 line 05, $2,000.00 line 07) | Agreement Article 5.1.7; script findings 2, 4, 9 | Column I and Line 5 recomputed at 10 percent of columns D + E + F |
| 8 | Conditional lien waivers missing for two subcontractors over the $25,000.00 threshold | Lines 05 and 07 | $120,000.00 billed this period on line 05 (E + F); $47,000.00 on line 07 | Agreement Article 5.1.9; package document list | Conditional waivers for period 2 from Corvid Steel Fabricators Inc. and Meridian Door Systems |
| 9 | Contractor's certification not notarized | G702 certification block | Whole application | G702 as submitted | Notarized signature, if the owner's form requires it (the reviewer to confirm the form's requirement) |

Amounts in this table are the amounts each finding puts in question, cited
to the application and the contract terms. They are not proposed deductions
and are not totaled. The script's recomputed Line 8 of $382,050.00 is
arithmetic on the schedule as submitted with the contract's retainage terms;
it does not incorporate corrections to line 03, line 07, or the CO-001
line, and is not a corrected amount due.

## Items ready

- Lines 01, 02, 04, 10, 11, and 12: column D equals the prior period's D + E,
  column G equals D + E + F, percent and balance tie, column I equals 10
  percent of D + E with no stored materials, and no line exceeds its
  scheduled value (script line and continuity checks, no findings).
- Lines 06, 08, and 09: no activity either period; scheduled values unchanged
  (script continuity checks, no findings).
- Line 02 moved from 70 percent to 90 percent complete, under the 50-point
  jump threshold, and Ridgeline Earthworks' conditional and unconditional
  waivers are both present (package document list).
- G702 Line 1 equals the contract (Article 4). Line 7 equals the certified
  Application No. 1 amount. Lines 6, 8, and 9 are arithmetically consistent
  with the cover sheet's own Lines 3, 4, 5, and 7 (script: no `earned-math`,
  `due-math`, or `balance-math` finding); they are wrong only because Lines
  2, 3, 4, and 5 are wrong.
- Contractor's own conditional (period 2) and unconditional (period 1) lien
  waivers: present.

## Documents

| Document | Required by | Status | Note |
|---|---|---|---|
| G702 cover sheet, signed | Form | present | Notary block blank |
| G703 continuation sheet | Form | present | 12 lines; no line for CO-001 |
| Conditional lien waiver, period 2, Harlow Brothers | Article 5.1.9 | present | |
| Unconditional lien waiver, period 1, Harlow Brothers | Article 5.1.9 | present | |
| Conditional lien waiver, period 2, Ridgeline Earthworks | Article 5.1.9 (line 02 bills $42,000.00 this period) | present | |
| Unconditional lien waiver, period 1, Ridgeline Earthworks | Article 5.1.9 | present | |
| Conditional lien waiver, period 2, Corvid Steel Fabricators | Article 5.1.9 (line 05 bills $120,000.00 this period) | missing | |
| Unconditional lien waiver, period 1, Corvid Steel Fabricators | Article 5.1.9 | open | Line 05 billed $72,000.00 stored in period 1; reviewer to confirm whether a period 1 waiver was collected then |
| Conditional lien waiver, period 2, Meridian Door Systems | Article 5.1.9 (line 07 bills $47,000.00 this period) | missing | |
| Stored materials backup, line 05 | GC 9.3.2 | open | Paid invoice, photos, and location present; insurance certificate missing |
| Stored materials backup, line 07 | GC 9.3.2 | missing | Nothing in package |
| Certified payroll | Article 3 | not required | |
| Daily reports, August | Not required for payment | present | Use to answer the line 07 field question |

Presence only. Whether a waiver form is sufficient is a question for counsel.
Not legal advice.

## Next steps

1. Return the application to Harlow Brothers with hold items 1 through 7 and
   ask for a corrected Application No. 2: CO-001 on Line 2, Line 3, and a new
   G703 line; line 03 column D at the certified $79,500.00 or a revised prior
   certificate; line 07 at or under scheduled value with backup for anything
   stored; column I and Line 5 at 10 percent of D + E + F; a Line 4 that
   equals the column G footing; and a notarized signature if the form calls
   for one.
2. Ask for the two missing conditional waivers and the line 05 insurance
   certificate (hold items 5, 6, 8).
3. Ask the superintendent whether door frames were set in August and whether
   any door or hardware material is on site (line 07, daily reports).
4. The reviewer decides whether to certify a reduced amount now or wait for
   the resubmission. This memo does not recommend either.

On request, a question list for the contractor or a corrected schedule for
them to resubmit can be prepared. Nothing is sent or recorded without
approval.

## Sources

Application figures: `input-cover-sheet.md` (G702 as submitted, footings,
package document list) and `input-pay-app-2.csv` (G703 as submitted). Prior
period: `input-pay-app-1.csv` and the Application No. 1 certificate as stated
by the reviewer. Contract terms and change order log: as supplied by the
reviewer in `input-cover-sheet.md`; clauses were not read directly and any
interpretation of Articles 5.1.7, 5.1.8, or 5.1.9 belongs to the reviewer.
Arithmetic: `scripts/check_pay_app.py` with the command shown above. All
checks in `references/checks.md` ran; none were skipped. This memo prepares
a review and is not an approval, certification, or rejection of payment, not
legal advice, and not a wage determination.
