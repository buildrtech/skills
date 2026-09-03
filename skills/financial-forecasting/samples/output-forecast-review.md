# Forecast: WIP revenue and profit, Q1 2027 (Jan to Mar)

**Finding:** Q1 WIP revenue is $9,785,000 with $798,650 profit (8.2% blended margin). Two of four projects moved margin more than two points since the December close: Harbor Street Parking Structure fell 3.0 points on $372,000 of cost growth, and Cedar Ridge Middle School gained 2.5 points on a $205,000 EAC reduction.
**Population:** `wip` (4 projects; source: `listForecastPeriods` metadata)
**Actual through:** January 2027. February and March are forecasts.
**Weighting:** unweighted revenue and profit.
**Interpretation:** "since the last close" is read as the January 2027 close compared with the December 2026 close, the two most recent closed periods on every project. Say the word and I will compare January against the current forecast rows instead; on these four projects the February forecast rows carry the January EAC, so the answer would not change.

All figures are synthetic. Project and period ids are placeholders.

## Totals

| Period | Revenue | Profit | Margin | Actual/forecast |
|---|---|---|---|---|
| Jan 2027 | $2,980,000 | $240,700 | 8.1% | actual (all four projects closed) |
| Feb 2027 | $3,265,000 | $266,250 | 8.2% | forecast |
| Mar 2027 | $3,540,000 | $291,700 | 8.2% | forecast |
| **Q1 total** | **$9,785,000** | **$798,650** | **8.2%** | mixed |

Source: `listForecastPeriods` with tab `wip`, metric `revenue` then
`profit`, grouping `month`, window 2027-01-01 to 2027-03-31, with project
rows. Totals are `amount_in_dollars` as returned. January is marked actual
because every WIP project's January billing period has `type` actual
(`listFinancialsBillingPeriods`).

## By project

| Project | Id | Q1 revenue | Q1 profit | Margin now | Margin at Dec close | Movement |
|---|---|---|---|---|---|---|
| Harbor Street Parking Structure | prj_1001 | $3,900,000 | $273,000 | 7.0% | 10.0% | **-3.0 pts** |
| Cedar Ridge Middle School Renovation | prj_1002 | $1,510,000 | $173,650 | 11.5% | 9.0% | **+2.5 pts** |
| Northgate Distribution Center | prj_1003 | $3,420,000 | $256,500 | 7.5% | 8.0% | -0.5 pts |
| Riverside Clinic Tenant Improvement | prj_1004 | $955,000 | $95,500 | 10.0% | 10.0% | 0.0 pts |
| **Total** | | **$9,785,000** | **$798,650** | 8.2% | | |

Q1 revenue per project sums the January actual row and the February and
March forecast rows from each project's billing periods. "Margin now" is
the margin on the January closed period (`cp_<project>_2027-01`); "margin at
Dec close" is the margin on the December closed period
(`cp_<project>_2026-12`). Both are computed from contract value and EAC as
shown under Formulas.

## Flags (movement beyond 2.0 points)

- **Harbor Street Parking Structure (prj_1001): -3.0 points.** EAC rose
  from $11,160,000 (cp_1001_2026-12) to $11,532,000 (cp_1001_2027-01), cost
  growth of $372,000 on a $12,400,000 contract. No change order was approved
  between the two closes (`listFinancialsChangeOrders`: one approved CO of
  $400,000 dated October 2026, already in contract value; none pending). The
  closed period records the new EAC but not the reason; ask the project
  manager what drove the January reforecast. The project is 60.0% complete
  and overbilled by $310,000, so the margin fade will show up as the
  overbilling unwinds over the remaining months.
- **Cedar Ridge Middle School Renovation (prj_1002): +2.5 points.** EAC
  fell from $7,462,000 (cp_1002_2026-12) to $7,257,000 (cp_1002_2027-01), a
  $205,000 reduction on an $8,200,000 contract. No change orders on the
  project. The project is 40.0% complete and underbilled by $180,000; if the
  EAC reduction is buyout savings that is good news, but confirm it is not
  scope that has been deferred rather than removed.

Northgate (-0.5) and Riverside (0.0) are inside the threshold and are shown
for completeness.

## Over/under billing, as of the January close

| Project | Id | % complete | Earned revenue | Billed to date | Over/(under) | Period id |
|---|---|---|---|---|---|---|
| Harbor Street Parking Structure | prj_1001 | 60.0% | $7,440,000 | $7,750,000 | $310,000 | cp_1001_2027-01 |
| Cedar Ridge Middle School Renovation | prj_1002 | 40.0% | $3,280,000 | $3,100,000 | ($180,000) | cp_1002_2027-01 |
| Northgate Distribution Center | prj_1003 | 80.0% | $16,800,000 | $16,800,000 | $0 | cp_1003_2027-01 |
| Riverside Clinic Tenant Improvement | prj_1004 | 25.0% | $900,000 | $1,050,000 | $150,000 | cp_1004_2027-01 |
| **Net** | | | **$28,420,000** | **$28,700,000** | **$280,000 overbilled** | |

Riverside's $150,000 overbilling at 25% complete is consistent with
mobilization and a front-loaded schedule of values; nothing in the data
suggests otherwise. Cedar Ridge's underbilling is the one to watch given it
has no pending change orders to explain it.

## Sources

- Portfolio totals and project rows: `listForecastPeriods` (tab `wip`,
  grouping `month`, 2027-01-01 to 2027-03-31), run once for revenue and
  once for profit.
- Contract values: `listFinancialsPrimeContracts` plus approved
  `listFinancialsChangeOrders` per project.
- Actual cost, billed, and EAC: `listFinancialsClosedPeriods` per project,
  paginated to the end; December and January periods used. Values were
  returned in cents and converted to dollars.
- Actual/forecast labels: `type` on `listFinancialsBillingPeriods` rows.
- Nothing was written. This is a forecast review, not an accounting close or
  a revenue recognition opinion; WIP schedule treatment is for your
  accountant.

## Formulas

Shown once using Harbor Street (prj_1001), January close (cp_1001_2027-01):

- Contract value = prime contract + approved change orders
  = $12,000,000 + $400,000 = $12,400,000
- Percent complete (cost-to-cost) = actual cost to date / EAC
  = $6,919,200 / $11,532,000 = 60.0%
- Earned revenue = percent complete x contract value
  = 0.600 x $12,400,000 = $7,440,000
- Margin = (contract value - EAC) / contract value
  = ($12,400,000 - $11,532,000) / $12,400,000 = 7.0%
- Margin at prior close = ($12,400,000 - $11,160,000) / $12,400,000 = 10.0%
- Margin movement = 7.0% - 10.0% = -3.0 points
- Over/under billing = billed to date - earned revenue
  = $7,750,000 - $7,440,000 = +$310,000 (overbilled)
- Q1 profit per project = sum of monthly profit rows; monthly profit rows
  are the project's margin applied to that month's revenue, as returned on
  the billing periods.

Next step if useful: a full project health card for Harbor Street with the
month-by-month period table, or the same Q1 view for `wip_and_pursuits`.
