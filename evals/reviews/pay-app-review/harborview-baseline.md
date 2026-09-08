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
