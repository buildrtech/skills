# Pay app review: Harborview Medical Office Building, Phase 1, Application No. 3, period ending August 31, 2026

**Status:** Recommend hold for review
**In one line:** The schedule of values foots to $3,086,750.00 against a contract sum to date of $3,196,550.00 because line 12 (fire protection, $118,000.00 scheduled, $11,800.00 previously certified) was dropped from the application and the $8,200.00 credit on CO-002 is not reflected on Line 2, Line 3, or the schedule; retainage is $3,600.00 short on line 11's stored materials, line 04 column D is $3,500.00 above the certified prior period, line 07 is billed at 103.85 percent, and Line 8 does not equal Line 6 minus Line 7 by $1,000.00.

## Summary

Stanhope & Reyes Builders submitted Application No. 3 for $564,965.00 (G702
Line 8 as submitted) for the period ending August 31, 2026. This review
covered the G702 cover sheet and cover letter, the 13-line G703 continuation
sheet, the Application No. 2 continuation sheet as certified August 6, 2026,
the change order log dated September 1, 2026, the package document list, and
the contract terms in Articles 3, 4, and 5 and General Conditions 9.3.2 as
supplied by the reviewer. The script found 11 errors and 7 warnings. Four
things drive the hold: line 12 was removed from the schedule with $11,800.00
already certified against it, so column C no longer foots to the contract
(G703 column C total; G702 Line 3); the approved CO-002 credit of $8,200.00
is missing from Line 2, Line 3, and the schedule; retainage was not withheld
on line 11's $36,000.00 of stored materials, which is also stored off site
without owner approval or an insurance certificate; and line 04 column D is
$3,500.00 higher than what was certified last period. This memo prepares the
review. It is not an approval, certification, or rejection of payment.

## Review basis

| Term | Value | Source |
|---|---|---|
| Original contract sum | $3,180,000.00 | Agreement, Article 4 (reviewer-supplied) |
| Approved change orders | $16,550.00 net: CO-001 +$24,750.00 approved July 20, 2026; CO-002 −$8,200.00 approved August 18, 2026 | Change order log dated September 1, 2026 |
| Pending change orders | $31,400.00: CO-003, pending owner signature; not approved | Change order log dated September 1, 2026 |
| Retainage on completed work | 10% | Agreement, Article 5.1.7 |
| Retainage on stored materials | 10% | Agreement, Article 5.1.7 |
| Retainage reduction milestone | Not reached. Total completed and stored as submitted is $1,538,400.00 against a contract sum to date of $3,196,550.00, 48.13%; the milestone is 50% and needs the owner's written approval, none issued. | Agreement, Article 5.1.8; script G702 summary Lines 3 and 4 |
| Stored materials rules | On site, or bonded off-site warehouse with owner's written approval; paid invoice or bill of sale, insurance certificate naming owner, location, dated photos | General Conditions 9.3.2 |
| Lien waiver requirement | Conditional current period and unconditional prior period from contractor and every subcontractor or supplier billing over $25,000.00 in the period | Agreement, Article 5.1.9 |
| Certified payroll requirement | Required weekly for contractor and every subcontractor with labor on site | Agreement, Article 3 |
| Prior application certified | $822,195.00 on August 6, 2026, full amount requested | Architect's certificate, Application No. 2 |

## Arithmetic findings

Command run from the skill directory:

```
python3 scripts/check_pay_app.py /app/input/pay-app-3.csv \
  --prior /app/input/pay-app-2.csv \
  --contract-sum 3180000 --change-orders 16550 --retainage 10 \
  --g702-change-orders 24750 --g702-contract-sum-to-date 3204750 \
  --g702-completed 1538400 --g702-retainage 150240 --g702-earned 1388160 \
  --g702-previous 822195 --g702-due 564965 --g702-balance 1816590
```

Exit code 1 (error-severity findings present). Output unchanged:

## Findings (11 error, 7 warning, 0 info)

| # | Severity | Line | Column | Check | Finding |
|---|---|---|---|---|---|
| 1 | error | 04 Masonry | D | continuity | Column D is 46,500.00 but the prior application's D + E for this line is 0.00 + 43,000.00 = 43,000.00; difference 3,500.00. |
| 2 | error | 06 Roofing and sheet metal | G/C | percent-math | Percent complete as submitted is 45.00% but G / C = 72,000.00 / 180,000.00 = 40.00%. |
| 3 | error | 07 Doors, frames, and hardware | G | over-100-percent | Total completed and stored 54,000.00 exceeds scheduled value 52,000.00 by 2,000.00 (103.85% complete). Column G cannot exceed column C without a change order. |
| 4 | error | 11 HVAC | I | line-retainage | Column I as submitted is 9,875.00 but 10% of D + E plus 10% of F = 13,475.00; difference (3,600.00). |
| 5 | error | 12 Fire protection | A | missing-line | Line 12 was on the prior application with 11,800.00 completed and stored but is missing from this application. |
| 6 | error | 13 Electrical | H | balance-math | Column H as submitted is 301,500.00 but C - G = 445,000.00 - 133,500.00 = 311,500.00. |
| 7 | error | G702 | Line 2 | change-orders | Net change by change orders as submitted is 24,750.00 but the approved change order log totals 16,550.00. |
| 8 | error | G702 | Line 3 | contract-sum | Contract sum to date as submitted is 3,204,750.00 but Line 1 + Line 2 = 3,180,000.00 + 16,550.00 = 3,196,550.00. |
| 9 | error | G702 | Line 3 / G703 C total | contract-sum | Schedule of values totals 3,086,750.00 but contract sum to date is 3,196,550.00 (original 3,180,000.00 + approved change orders 16,550.00); difference 109,800.00. An approved change order may not be reflected on the schedule. |
| 10 | error | G702 | Line 5 | retainage | Retainage as submitted is 150,240.00 but 10% of completed work 1,432,400.00 plus 10% of stored materials 106,000.00 = 153,840.00; difference (3,600.00). |
| 11 | error | G702 | Line 8 | due-math | Current payment due as submitted is 564,965.00 but Line 6 - Line 7 as submitted = 1,388,160.00 - 822,195.00 = 565,965.00. |
| 12 | warning | 05 Structural and miscellaneous steel | F | stored-materials | Stored materials of 31,000.00 billed this period; confirm bill of sale, insurance, location, and photos are in the backup. |
| 13 | warning | 07 Doors, frames, and hardware | F | stored-materials | Stored materials of 24,000.00 billed this period; confirm bill of sale, insurance, location, and photos are in the backup. |
| 14 | warning | 07 Doors, frames, and hardware | G | percent-jump | Percent complete moved from 0.00% on the prior application to 103.85% in one period (up 103.85% of scheduled value); confirm progress with the field or inspection log. |
| 15 | warning | 08 Overhead doors | F | stored-materials | Stored materials of 15,000.00 billed this period; confirm bill of sale, insurance, location, and photos are in the backup. |
| 16 | warning | 11 HVAC | F | stored-materials | Stored materials of 36,000.00 billed this period; confirm bill of sale, insurance, location, and photos are in the backup. |
| 17 | warning | G702 | Line 6 | earned-recomputed | Total earned less retainage recomputed from the schedule and contract terms is 1,384,560.00, versus 1,388,160.00 as submitted; difference 3,600.00. |
| 18 | warning | G702 | Line 8 | due-recomputed | Current payment due recomputed from the schedule and contract terms is 562,365.00, versus 564,965.00 as submitted; difference 2,600.00. |

## G702 summary: computed from the schedule and contract terms versus as submitted

| Line | Field | Computed | As submitted | Difference |
|---|---|---|---|---|
| 1 | Original contract sum | 3,180,000.00 | 3,180,000.00 | 0.00 |
| 2 | Net change by change orders | 16,550.00 | 24,750.00 | 8,200.00 |
| 3 | Contract sum to date | 3,196,550.00 | 3,204,750.00 | 8,200.00 |
| G703 C | Schedule of values total | 3,086,750.00 | n/a | n/a |
| 4 | Total completed and stored to date | 1,538,400.00 | 1,538,400.00 | 0.00 |
| 5 | Retainage | 153,840.00 | 150,240.00 | (3,600.00) |
| 6 | Total earned less retainage | 1,384,560.00 | 1,388,160.00 | 3,600.00 |
| 7 | Less previous certificates for payment | 822,195.00 | 822,195.00 | 0.00 |
| 8 | Current payment due | 562,365.00 | 564,965.00 | 2,600.00 |
| 9 | Balance to finish, including retainage | 1,811,990.00 | 1,816,590.00 | 4,600.00 |

Lines checked: 13. Retainage basis: 10% of completed work, 10% of stored materials. Tolerance: 0.01. Percent-jump threshold: 50% of scheduled value in one period.

This output prepares a review. It is not an approval, certification, or rejection of payment.

## Document and field review

- **Line 12, fire protection, was removed with $11,800.00 already certified
  against it.** The cover letter says the scope is being reassigned and a
  revised schedule will follow with Application No. 4. A line cannot leave
  the schedule between applications: $118,000.00 of scheduled value and
  $11,800.00 certified on Application No. 2 (pay-app-2.csv, line 12,
  columns C and G) have nowhere to sit, so column C foots to $3,086,750.00
  instead of $3,196,550.00 (script finding 9) and Line 7 still carries the
  $11,800.00 less its retainage. Until an approved change order or a
  documented reallocation moves that value, line 12 must stay on the
  schedule with its prior-period amounts in column D.
- **CO-002 is not reflected anywhere in the application.** The change order
  log shows CO-002, a credit of $8,200.00, approved August 18, 2026. Line 2
  as submitted is $24,750.00 (CO-001 only) and the change order summary box
  shows no deductions, so Line 3 is $3,204,750.00 instead of $3,196,550.00
  (script findings 7 and 8). No G703 line or reduction to line 04 carries
  the credit. Of the $109,800.00 gap in script finding 9, $118,000.00 is the
  dropped line 12 and −$8,200.00 is the missing CO-002 credit. CO-003
  ($31,400.00) is pending and correctly absent; no line bills against it.
- **Line 04 column D rolls forward more than was certified.** Application
  No. 2 was certified for the full amount requested, so the certified column
  D + E for masonry is $43,000.00 (pay-app-2.csv, line 04). This application
  shows $46,500.00 in column D (pay-app-3.csv, line 04, column D), $3,500.00
  more, with no revised prior application on file. Column G, the percent,
  column H, and column I on line 04 are computed from the overstated D, so
  each is off by the same $3,500.00 ($350.00 of it retainage) even though
  the script's line math on them ties.
- **Line 07 is billed over its scheduled value with unsupported stored
  materials.** Column E $30,000.00 plus column F $24,000.00 equals
  $54,000.00 against a scheduled value of $52,000.00 (pay-app-3.csv, line
  07). No change order adds value to doors, frames, and hardware, and the
  package has no stored materials backup for this line. Column D was $0.00
  on the prior application, so the line moved from nothing to over complete
  in one period. Question for the field: the August daily reports should
  show whether frames were set; $24,000.00 of doors and hardware stored on
  site needs the invoice and photos before it is considered.
- **Line 08 appears to count the same overhead doors twice.** Application
  No. 2 carried $15,000.00 in column F for overhead doors stored on site
  (pay-app-2.csv, line 08). This period shows $15,000.00 installed in column
  E and $15,000.00 still stored in column F (pay-app-3.csv, line 08). If the
  stored doors were installed, column F should have gone to $0.00 and column
  G is overstated by $15,000.00 ($1,500.00 of it retainage). If a second set
  of doors arrived, the package needs its own invoice, insurance, location,
  and photos; the only backup on file is from the Application No. 2 package.
  Question for the field: were the overhead doors set in August, and is
  there a second set on site?
- **Line 11 stored materials are off site without approval and without
  insurance, and retainage was not withheld on them.** The $36,000.00 in
  column F (pay-app-3.csv, line 11) is stated as stored at Northwind
  Mechanical's yard in Joliet. General Conditions 9.3.2 allows off-site
  storage only in a bonded warehouse the owner has approved in writing;
  nothing on file shows that approval, and there is no insurance certificate
  naming the owner. Column I on this line is 10 percent of D + E only,
  $9,875.00 instead of $13,475.00 (script finding 4), which is the whole
  $3,600.00 shortfall on Line 5 (script finding 10). Line 5b on the cover
  sheet shows $7,000.00 of stored-materials retainage, which is 10 percent
  of $70,000.00, not of the $106,000.00 in column F.
- **Line 07 and line 08 stored materials backup.** Line 05's $31,000.00 has
  all four items General Conditions 9.3.2 requires. Line 07's $24,000.00 has
  nothing. Line 08's $15,000.00 relies on the invoice and photos from the
  Application No. 2 package plus an insurance certificate; see the
  double-count question above.
- **Line 6 and Line 8 arithmetic.** Line 6 as submitted equals Line 4 minus
  Line 5 as submitted. Line 8 as submitted, $564,965.00, is $1,000.00 below
  Line 6 minus Line 7 as submitted, $565,965.00 (script finding 11). The
  script's recomputed Line 8 of $562,365.00 uses the contract's retainage
  terms and does not incorporate corrections to line 04, line 07, line 08,
  line 12, or CO-002.
- **Line 7 ties.** $822,195.00 as submitted equals the amount certified on
  Application No. 2 (architect's certificate, August 6, 2026) and the prior
  schedule's total earned less retainage (script G702 summary, Line 7).
- **Retainage reduction milestone is not reached.** 48.13 percent complete
  by the contract's measure; see the contract terms table. Noted so the
  reviewer does not have to re-check.
- **Certified payroll for the week ending August 21, 2026 is missing.**
  Article 3 requires weekly reports; the package has August 7, 14, and 28
  (package document list). Whether the reported wages comply is a wage
  determination and is out of scope.
- **Lien waivers.** Missing: Kestrel Steel Erectors' unconditional waiver
  for period 2 (line 05 billed $155,000.00 in period 2), Tallgrass Roofing's
  conditional waiver for period 3 (line 06 bills $72,000.00 this period),
  and Meridian Door Systems' conditional waiver for period 3 (line 07 bills
  $54,000.00 this period). Every other subcontractor over the $25,000.00
  threshold has both waivers on file. Whether a waiver form is sufficient is
  a question for counsel.
- **Nothing was derived or unreadable.** Both schedules were supplied as CSV
  with every column populated, so no cell was OCR'd or estimated.

## Hold points

| # | Item | Line / column | Amount in question | Source | What would clear it |
|---|---|---|---|---|---|
| 1 | Line 12 removed from the schedule with prior certified work | G703 line 12; G703 column C total; G702 Line 3 | $118,000.00 scheduled; $11,800.00 previously certified | pay-app-2.csv line 12; cover letter; script findings 5 and 9 | Line 12 restored with $11,800.00 in column D, or an approved change order or documented reallocation moving its value |
| 2 | CO-002 credit missing from Lines 2 and 3 and from the schedule | G702 Line 2, Line 3; G703 column C total | $8,200.00 | Change order log, CO-002; script findings 7, 8, 9 | Line 2 = $16,550.00, Line 3 = $3,196,550.00, and a G703 credit line or reduced line 04 so column C foots to $3,196,550.00 |
| 3 | Column D overstated against the certified prior period | G703 line 04, column D | $3,500.00 ($350.00 of it retainage) | pay-app-3.csv line 04 D vs pay-app-2.csv line 04 D + E; Application No. 2 certificate; script finding 1 | Column D corrected to $43,000.00, or a revised and certified Application No. 2 |
| 4 | Line billed at 103.85 percent with no change order | G703 line 07, columns E, F, G | $2,000.00 over scheduled value; $54,000.00 billed on the line | pay-app-3.csv line 07; change order log; script findings 3 and 14 | Column G at or below $52,000.00 with the field confirming installed work, or an approved change order adding value to this line |
| 5 | Stored materials on line 07 with no backup | G703 line 07, column F | $24,000.00 | pay-app-3.csv line 07 F; package document list; script finding 13 | Paid invoice or bill of sale, insurance certificate, on-site location, dated photos per GC 9.3.2 |
| 6 | Overhead doors possibly counted in both E and F | G703 line 08, columns E and F | $15,000.00 ($1,500.00 of it retainage) | pay-app-2.csv and pay-app-3.csv line 08; script finding 15 | Field confirmation of what was installed and what is on site; column F at $0.00 if the stored doors were installed, or new backup if a second set arrived |
| 7 | Line 11 stored materials off site without owner approval or insurance | G703 line 11, column F | $36,000.00 | pay-app-3.csv line 11 F; package document list; GC 9.3.2; script finding 16 | Owner's written approval of the Joliet location and a bonded warehouse, plus an insurance certificate naming the owner; otherwise column F to $0.00 |
| 8 | Retainage not withheld on line 11 stored materials | G703 line 11, column I; G702 Line 5 and 5b | $3,600.00 | Agreement Article 5.1.7; script findings 4 and 10 | Column I and Line 5 recomputed at 10 percent of columns D + E + F |
| 9 | Line 8 does not equal Line 6 minus Line 7 | G702 Line 8 | $1,000.00 | G702 as submitted; script finding 11 | A reissued cover sheet whose Line 8 equals Line 6 minus Line 7 after the other corrections |
| 10 | Percent complete and balance to finish keyed wrong | G703 line 06, percent; line 13, column H | Line 06 shows 45.00% against 40.00%; line 13 shows $301,500.00 against $311,500.00 | pay-app-3.csv lines 06 and 13; script findings 2 and 6 | Corrected cells on resubmission; no amount due changes |
| 11 | Lien waivers missing for three subcontractors over the $25,000.00 threshold | Lines 05, 06, 07 | $155,000.00 (line 05, period 2); $72,000.00 (line 06); $54,000.00 (line 07) | Agreement Article 5.1.9; package document list | Kestrel Steel Erectors' unconditional waiver for period 2; Tallgrass Roofing's and Meridian Door Systems' conditional waivers for period 3 |
| 12 | Certified payroll missing for the week ending August 21, 2026 | Article 3 | Whole application | Package document list | The missing weekly report for the contractor and each subcontractor with labor on site |

Amounts in this table are the amounts each finding puts in question, cited
to the application and the contract terms. They are not proposed deductions
and are not totaled. The script's recomputed Line 8 of $562,365.00 is
arithmetic on the schedule as submitted with the contract's retainage terms;
it does not incorporate corrections to lines 04, 07, 08, or 12 or to CO-002,
and is not a corrected amount due.

## Checks without exceptions

- Lines 01, 02, 03, 09, 10, 13 (except column H), and 14: column D equals
  the prior period's D + E, column G equals D + E + F, percent ties, column I
  equals 10 percent of D + E with no stored materials, and no line exceeds
  its scheduled value (script line and continuity checks, no findings other
  than line 13 column H).
- Line 05: the $62,000.00 stored last period moved to column E this period
  and column D equals the prior D + E (pay-app-2.csv and pay-app-3.csv, line
  05); the new $31,000.00 in column F has all four backup items; retainage on
  the line is correct.
- Line 06: work billed this period ties to column G; only the printed
  percent is wrong (script finding 2).
- G702 Line 1 equals the contract (Article 4). Line 4 equals the G703
  column G footing and the script's recomputation. Line 7 equals the
  certified Application No. 2 amount. Line 6 and Line 9 are arithmetically
  consistent with the cover sheet's own Lines 3, 4, and 5 (script: no
  `earned-math` or `balance-math` finding on the cover sheet).
- Contractor's own conditional (period 3) and unconditional (period 2) lien
  waivers: present. Certification signed and notarized.

## Package checklist

| Document | Required by | Status | Note |
|---|---|---|---|
| G702 cover sheet, signed and notarized | Form | present | |
| G703 continuation sheet | Form | present | 13 lines; line 12 dropped; no line for CO-002 |
| Contractor's cover letter | Form | present | States line 12 removal |
| Change order log dated September 1, 2026 | Reviewer | present | CO-001 and CO-002 approved; CO-003 pending |
| Application No. 2 continuation sheet as certified | Reviewer | present | Used for continuity |
| Conditional lien waiver, period 3, Stanhope & Reyes Builders | Article 5.1.9 | present | |
| Unconditional lien waiver, period 2, Stanhope & Reyes Builders | Article 5.1.9 | present | |
| Conditional and unconditional waivers, Ridgecrest Concrete (line 03) | Article 5.1.9 | present | |
| Conditional and unconditional waivers, Brickline Masonry (line 04) | Article 5.1.9 | present | |
| Conditional lien waiver, period 3, Kestrel Steel Erectors (line 05) | Article 5.1.9 | present | |
| Unconditional lien waiver, period 2, Kestrel Steel Erectors | Article 5.1.9 (line 05 billed $155,000.00 in period 2) | missing | |
| Conditional lien waiver, period 3, Tallgrass Roofing (line 06) | Article 5.1.9 (line 06 bills $72,000.00 this period) | missing | |
| Conditional lien waiver, period 3, Meridian Door Systems (line 07) | Article 5.1.9 (line 07 bills $54,000.00 this period) | missing | |
| Conditional lien waiver, period 3, Summit Overhead Door (line 08) | Article 5.1.9 | present | |
| Conditional lien waiver, period 3, Aster Finishes (line 09) | Article 5.1.9 | present | |
| Conditional and unconditional waivers, Halden Plumbing (line 10) | Article 5.1.9 | present | |
| Conditional and unconditional waivers, Northwind Mechanical (line 11) | Article 5.1.9 | present | |
| Conditional and unconditional waivers, Copperline Electric (line 13) | Article 5.1.9 | present | |
| Stored materials backup, line 05 | GC 9.3.2 | present | Invoice, insurance certificate, on-site location, photos |
| Stored materials backup, line 07 | GC 9.3.2 | missing | Nothing in package |
| Stored materials backup, line 08 | GC 9.3.2 | open | Invoice and photos from Application No. 2; insurance certificate present; see double-count question |
| Stored materials backup, line 11 | GC 9.3.2 | open | Invoice and photos present; off-site location without owner approval; insurance certificate missing |
| Certified payroll, weeks ending August 7, 14, 28 | Article 3 | present | |
| Certified payroll, week ending August 21 | Article 3 | missing | |
| Superintendent's daily reports, August | Not required for payment | present | Use to answer the line 07 and line 08 field questions |

Presence only. Whether a waiver form is sufficient is a question for counsel.
Not legal advice.

## Resubmission actions

1. Return the application to Stanhope & Reyes with hold items 1 through 10
   and ask for a corrected Application No. 3: line 12 restored or moved by
   an approved change order; CO-002 on Line 2, Line 3, and the schedule;
   line 04 column D at the certified $43,000.00; line 07 at or under
   scheduled value with backup for anything stored; line 08 column F
   resolved; line 11 storage approved and insured or column F removed;
   column I and Line 5 at 10 percent of D + E + F; and a Line 8 that equals
   Line 6 minus Line 7.
2. Ask for the three missing lien waivers and the August 21 certified
   payroll (hold items 11 and 12).
3. Ask the superintendent whether door frames were set in August, whether
   the overhead doors were installed, and whether a second set is on site
   (lines 07 and 08, daily reports).
4. The reviewer decides whether to certify a reduced amount now or wait for
   the resubmission. This memo does not recommend either.

On request, a question list for the contractor or a corrected schedule for
them to resubmit can be prepared. Nothing is sent or recorded without
approval.

## Evidence

Application figures: `cover-sheet.md` (G702 as submitted, cover letter,
footings, contract terms, change order log, package document list) and
`pay-app-3.csv` (G703 as submitted). Prior period: `pay-app-2.csv` and the
Application No. 2 certificate as stated by the reviewer. Contract clauses
were not read directly; any interpretation of Articles 3, 5.1.7, 5.1.8, or
5.1.9 or General Conditions 9.3.2 belongs to the reviewer. Arithmetic:
`scripts/check_pay_app.py` with the command shown above. All checks in
`references/checks.md` ran; none were skipped. This memo prepares a review
and is not an approval, certification, or rejection of payment, not legal
advice, and not a wage determination.
