# Superintendent coverage for Birch School (d_01): 2028-01-01 to 2028-03-01 (end exclusive)

**Finding:** The full 100% need cannot be defensibly covered for the whole window from this snapshot. Only two of the 60 days' worth of demand can be fully covered: **2028-01-01 to 2028-01-31 (30 days)** at 100%, using e_b Blair and e_a Aster at 50% each. After that, coverage degrades — Aster is on time off 2028-01-31, Aster's c_site certification expires after 2028-02-15, Blair's availability from 2028-02-01 is not in the data, and e_c Casey has no c_site row at all. **Residual demand: 50% on 2028-01-31, 50% for 2028-02-01 to 2028-02-16, and 100% for 2028-02-16 to 2028-03-01.** Nothing has been written.

**Source:** Not read from Buildr. There is no Buildr MCP connection in this environment, so no `search` or `execute` call was made and no live account data was consulted. Every fact below comes from the synthetic snapshot supplied in the request (as-of 2027-12-01), which the request states is complete except where noted. Field-for-field this stands in for `listWorkforceEmployees`, `listWorkforceAssignments`, `listWorkforceTimeOffs`, `listWorkforceEmployeeUtilizationPeriods`, `listWorkforceEmployeeCertifications`, and the project/role lists. Because the snapshot is the sole source, the usual "re-read to verify" step is not available and none of these findings has been confirmed against a live account.

**Window:** 2028-01-01 to 2028-03-01, end date exclusive — Jan 1 through Feb 29, 2028 inclusive, 60 calendar days (2028 is a leap year). This matches the unfilled assignment d_01 exactly. Assignment, time-off, and utilization-period end dates are exclusive throughout; certification expiration dates are inclusive.

## Unfilled demand

| Assignment | Project | Role | Start | End (excl.) | % | Days |
|---|---|---|---|---|---|---|
| d_01 | p_birch Birch School | r_super Superintendent | 2028-01-01 | 2028-03-01 | 100 | 60 |

Requirement on the need: certification c_site (site orientation). No minimum experience required, so experience is not a differentiator here and no experience rows were supplied.

## Utilization summary

All three employees are active superintendents included in headcount. Averages are capacity-weighted across the days of the window that the utilization periods actually cover.

| Employee | Role | Days covered by data | Avg % uncapped | Avg % capped at 100 | Peak % | Peak period | Time off in window |
|---|---|---|---|---|---|---|---|
| e_a Aster | r_super | 60 / 60 | 0 | 0 | 0 | — | t_01, 2028-01-31 to 2028-02-01 (1 day) |
| e_b Blair | r_super | 31 / 60 | **not establishable for the window** (50 over the 31 covered days) | **not establishable for the window** (50 over the 31 covered days) | 50 | 2028-01-01 to 2028-02-01 | none in data |
| e_c Casey | r_super | 60 / 60 | 100 | 50 | 200 | 2028-01-01 to 2028-01-31 | none in data |
| **Team** | | | **not establishable** | **not establishable** | | | |

Arithmetic shown:

- **e_a Aster** — 0% for 2028-01-01 to 2028-01-31 (30 days), 0% with the time-off flag for 2028-01-31 to 2028-02-01 (1 day), 0% for 2028-02-01 to 2028-03-01 (29 days). (0×60)/60 = 0 uncapped and capped. The single time-off day is zero-utilization but unavailable, not idle.
- **e_c Casey** — 200% for 2028-01-01 to 2028-01-31 (30 days, a_c1 and a_c2 at 100% each), 0% for 2028-01-31 to 2028-03-01 (30 days). Uncapped (200×30 + 0×30)/60 = 100. Capped (100×30 + 0×30)/60 = 50. Casey is capped by 100 points across 30 days; the uncapped figure of 100 would read as a fully-committed superintendent and hide a full month of idle time.
- **e_b Blair** — the utilization response is explicitly incomplete: it carries one period, 50% for 2028-01-01 to 2028-02-01 (31 days), and nothing for 2028-02-01 to 2028-03-01 (29 days). Blair's assignment a_b on p_lake Lake Clinic ends 2028-02-01, so a_b contributes nothing after that date, but absence of an assignment row in an admittedly-partial read is not evidence of zero utilization. A window average would require assuming the missing 29 days, so **no window average is reported for Blair, capped or uncapped**, only the 50%/50% figure over the 31 days the data covers.

**Why no team average:** capped and uncapped team averages both require every in-scope employee's full-window figure. Blair's is missing for 29 of 60 days, so the team average cannot be established from this snapshot and none is stated. For reference only, and *not* an answer to the question: if Blair's missing 29 days were 0%, the team capped average would be 16.7; if they were 100%, it would be 32.8. The spread is wide enough that reporting a single number would be misleading.

## Bench (30+ consecutive days at 0%)

Standard 30-day definition, applied inside the window. Time off is excluded from bench, which breaks a run.

| Employee | Bench start | Bench end (excl.) | Days | Qualifies | Note |
|---|---|---|---|---|---|
| e_a Aster | 2028-01-01 | 2028-01-31 | 30 | **Yes** | Run ends at time off t_01 on 2028-01-31 |
| e_c Casey | 2028-01-31 | 2028-03-01 | 30 | **Yes** | Follows the 200% overallocated month; runs to the window edge |
| e_a Aster | 2028-02-01 | 2028-03-01 | 29 | No | 29 days, one short of the threshold; reported so it is not lost |
| e_b Blair | — | — | — | Unknown | 50% for the covered 31 days, so no bench there; 2028-02-01 to 2028-03-01 (29 days) is unknown and could not qualify on length anyway |

Aster is idle for 59 of the 60 days in the window but has no *single* qualifying run longer than 30 days, because the one-day time off splits the window into 30 and 29. This is a real reading of the rule, not a data problem: both segments are stated, and the 29-day segment is availability even though it is not bench.

## Conflicts

| Employee | Type | Period | Detail | Assignments involved |
|---|---|---|---|---|
| e_c Casey | Overallocated | 2028-01-01 to 2028-01-31 (30 days) | Two 100% assignments run concurrently for 200% combined; 100 points over capacity | a_c1 (p_west West Depot), a_c2 (p_east East Depot) |

No time-off overlap conflicts: Aster holds no assignment during t_01. No role mismatches: all three employees and d_01 are r_super. No dismissed employees in this fixture.

## Candidates for r_super on p_birch, 2028-01-01 to 2028-03-01

Ranked by fit (role, then c_site certification), then availability. Certification status is exactly what the snapshot holds; nothing is assumed renewed.

| Rank | Employee | Role | c_site | Capacity in window | Disqualifier |
|---|---|---|---|---|---|
| 1 | e_b Blair | r_super ✓ | Valid, issued 2027-01-01, expires 2029-01-01 — covers the entire window | Exactly 50% free 2028-01-01 to 2028-02-01 (a_b on p_lake Lake Clinic takes the other 50%); **unknown** 2028-02-01 to 2028-03-01 | None for Jan 1–Feb 1 at 50%. Cannot be proposed beyond 2028-02-01: utilization data is missing, so free capacity there is unestablished |
| 2 | e_a Aster | r_super ✓ | Valid but **expires 2028-02-15**, i.e. covers only through 2028-02-15 and not the last 14 days of the window | 100% free the whole window except 2028-01-31 (time off t_01) | Certification lapses 2028-02-16; unavailable 2028-01-31 |
| 3 | e_c Casey | r_super ✓ | **No c_site row in the data** | 0% free 2028-01-01 to 2028-01-31 (already 200%, overallocated); 100% free 2028-01-31 to 2028-03-01 | Missing certification — disqualifying for this need regardless of the 30-day bench that follows |

Casey is the one person with clean, uncontested capacity for exactly the stretch that is hardest to cover (2028-01-31 onward), and is the one person who cannot be proposed for it. That is the central tension in this window.

## Staffing proposal (dry run, nothing applied)

Coverage at 50% per candidate, as requested, with the full 100% need preserved — d_01 is **not** shortened or reduced. Every segment below is a defensible fill: the employee holds r_super, holds a valid c_site for every day of that segment, is not on time off, and has at least 50 points of free capacity in that segment from the data as given.

| # | Action | Assignment | Employee | Project | Role | Start | End (excl.) | % | Days | Reason |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Create | (new) | e_b Blair | p_birch Birch School | r_super | 2028-01-01 | 2028-02-01 | 50 | 31 | Blair's only free 50 points, and c_site is valid throughout. Takes Blair to exactly 100%, not over |
| 2 | Create | (new) | e_a Aster | p_birch Birch School | r_super | 2028-01-01 | 2028-01-31 | 50 | 30 | Aster is at 0%, c_site valid; ends the day before time off t_01 |
| 3 | Create | (new) | e_a Aster | p_birch Birch School | r_super | 2028-02-01 | 2028-02-16 | 50 | 15 | Resumes the day time off ends; ends the day after 2028-02-15, the last day Aster's c_site is valid (expiration inclusive) |

**Do not change:** d_01 stays open at 100% for its full 2028-01-01 to 2028-03-01 range so the unmet portion stays visible as demand rather than being absorbed. Rows 1–3 are additive coverage against it. No existing assignment (a_b, a_c1, a_c2) is shortened, moved, or ended; nothing about Casey's overallocation is resolved here.

**Resulting coverage on d_01**

| Segment | Days | Covered | By | Residual |
|---|---|---|---|---|
| 2028-01-01 to 2028-01-31 | 30 | **100%** | Blair 50 + Aster 50 | 0 |
| 2028-01-31 to 2028-02-01 | 1 | 50% | Blair 50 (Aster on time off t_01) | **50%** |
| 2028-02-01 to 2028-02-16 | 15 | 50% | Aster 50 | **50%** |
| 2028-02-16 to 2028-03-01 | 14 | **0%** | nobody | **100%** |

Weighted, 40 of the 60 need-days are covered (100% for 30 days, 50% for 16 days, 0% for 14 days = 3,800 of 6,000 percent-days, 63%).

**Resulting utilization for the affected employees**

| Employee | Period | Before | After |
|---|---|---|---|
| e_b Blair | 2028-01-01 to 2028-02-01 | 50 | 100 |
| e_b Blair | 2028-02-01 to 2028-03-01 | unknown | unchanged (not touched) |
| e_a Aster | 2028-01-01 to 2028-01-31 | 0 | 50 |
| e_a Aster | 2028-01-31 to 2028-02-01 | 0 (time off) | 0 (time off, unchanged) |
| e_a Aster | 2028-02-01 to 2028-02-16 | 0 | 50 |
| e_a Aster | 2028-02-16 to 2028-03-01 | 0 | 0 (unchanged) |
| e_c Casey | whole window | 200 then 0 | unchanged; not proposed for anything |

No employee goes above 100 under this proposal, and no proposed segment overlaps time off.

## Residual demand and the conditions that would clear it

Three gaps remain. Each has a specific, checkable condition attached; none can be closed from the snapshot alone.

1. **2028-01-31, 50% (1 day).** Aster is on time off t_01. Closing it needs a fourth superintendent, or Blair going above 100% for the day, or moving the time off — all outside what this data supports.
2. **2028-02-01 to 2028-02-16, 50% (15 days).** Blair is the natural fill: c_site is valid to 2029-01-01 and a_b on p_lake ends 2028-02-01, so Blair may well be free. **Condition:** re-read Blair's utilization periods for 2028-02-01 to 2028-03-01. If they come back at 50% or less, extending row 1 through 2028-03-01 closes this gap and half of gap 3.
3. **2028-02-16 to 2028-03-01, 100% (14 days).** Aster's c_site expires after 2028-02-15 and Casey holds no c_site row. **Conditions, in order of likelihood:** (a) confirm Blair's February capacity as above, which covers 50 of the 100 points; (b) if Casey's site orientation exists but is not recorded, adding the certification row makes Casey a clean fit — Casey is at 0% for this entire stretch and is on a qualifying 30-day bench from 2028-01-31; (c) if Aster renews c_site before 2028-02-16, row 3 extends to 2028-03-01 for the other 50 points.

Even with all three conditions met, the arithmetic still leaves 2028-01-31 at 50% uncovered.

## Caveats

- **Nothing has been applied.** This is a dry run. The proposal above would create three assignments; per the skill's boundaries those require your explicit confirmation of this specific list, and in this environment there is no write path to Buildr in any case.
- **This snapshot cannot be verified.** No live read happened and no re-read after writing is possible. If this window is being staffed for real, the numbers should be re-derived from `listWorkforceEmployeeUtilizationPeriods` and `listWorkforceEmployeeCertifications` against the live account before anyone is committed — particularly Blair's February periods and Casey's certification rows, the two facts that most change the answer.
- **Certification status here is a data fact, not a compliance determination.** "c_site expires 2028-02-15" and "no c_site row for Casey" are statements about what the record holds. Whether either person may lawfully or contractually be on the Birch School site on a given day is a question for whoever owns site compliance, not for this analysis. This is staffing analysis, not an HR decision, an approval, or a determination of qualification under any regulation.
- Day counts are calendar days, not working days; no working calendar was supplied. 2028 is a leap year, so the window is 60 days rather than 59.
