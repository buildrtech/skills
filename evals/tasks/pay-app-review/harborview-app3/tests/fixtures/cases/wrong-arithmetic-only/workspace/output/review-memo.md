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

## Contract terms used

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

## Script findings

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


## Items on hold for a human decision

| # | Item | Line / column | Amount in question | Source | What would clear it |
|---|---|---|---|---|---|
| 1 | Column D overstated | G703 line 04 | $3,500.00 | script | corrected D |

## Sources

This memo prepares a review and is not an approval, certification, or rejection of payment, not legal advice, and not a wage determination.
