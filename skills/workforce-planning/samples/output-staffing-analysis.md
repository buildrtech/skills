# Superintendent for Ridgeview Elementary Classroom Addition: 2026-11-01 to 2027-08-01 (end exclusive)

**Finding:** No superintendent with a current OSHA 30 is free for the whole window. Dana Whitfield (emp_0107) is the best fit: valid OSHA 30, prior K-12 superintendent experience, and available December 19–March 14 and March 22–July 31, but she is at 100% on Lakeside Clinic TI through December 18, so staffing her from day one means splitting her for seven weeks. Marcus Bell (emp_0093) is free for the entire window with no side effects, but his OSHA 30 shows expired on 2026-06-30 in Buildr.

**Source:** Synthetic fixture replay of supplied Buildr-shaped records, as of 2026-09-03; no live calls or writes: `getProjectById`, `listWorkforceRoles`, `listWorkforceEmployees`, `listWorkforceAssignments`, `listWorkforceTimeOffs`, `listWorkforceEmployeeUtilizationPeriods`, `listWorkforceCertificationTypes`, `listWorkforceEmployeeCertifications`, `listWorkforceEmployeeExperiences`.

**Window:** "November through July" resolves to 2026-11-01 to 2027-08-01. The staffing need asg_0410 starts one day later on 2026-11-02 and ends 2027-08-01 (last day 2027-07-31). Substantial completion is 2027-07-30 per `getProjectById`.

## Unfilled demand on Ridgeview

| Assignment | Project | Role | Start | End (excl.) | % | Days |
|---|---|---|---|---|---|---|
| asg_0410 | proj_0031 Ridgeview Elementary Classroom Addition | Superintendent | 2026-11-02 | 2027-08-01 | 100 | 272 |
| asg_0411 | proj_0031 Ridgeview Elementary Classroom Addition | Project Manager | 2026-11-02 | 2027-08-01 | 50 | 272 |

The question is about asg_0410. The PM demand (asg_0411) is also open; it is listed so it is not forgotten and is not analyzed here.

## Candidates for Superintendent on Ridgeview

Ranked by fit (role, OSHA 30, experience), then availability. Certification and experience are exactly what Buildr holds; nothing is assumed.

| Rank | Employee | Role | OSHA 30 | Relevant experience | Capacity in window | Disqualifier |
|---|---|---|---|---|---|---|
| 1 | emp_0107 Dana Whitfield | Superintendent | Valid, expires 2028-03-14 | Fairview Elementary Renovation, Superintendent, 2024-06 to 2025-08 (assignment-derived) | 0% free 2026-11-02 to 2026-12-19; 100% free 2026-12-19 to 2027-03-15 and 2027-03-22 to 2027-08-01; unavailable during time off 2027-03-15 to 2027-03-22 | asg_0388 at 100% through 2026-12-18; unavailable March 15–21 |
| 2 | emp_0093 Marcus Bell | Superintendent | Expired 2026-06-30 | Pinecrest Middle School Gym, Superintendent, 2022-01 to 2023-06 (previous employer, Northfield Builders); Cedar Mill Warehouse (assignment-derived) | 100% free for the entire window; 273-day bench in the analysis window; prior assignment ended 2026-10-03 | OSHA 30 expired in Buildr. Renewal requires verified records before he can become an eligible option. |
| 3 | emp_0121 Priya Natarajan | Superintendent | Valid, expires 2029-09-02 | Harbor Point Parking Structure (assignment-derived); no K-12 rows | 0% free; asg_0402 Harbor Point at 100% through 2027-09-30 | Fully committed for the whole window; freeing her means replacing her on Harbor Point |
| 4 | emp_0088 Tom Okafor | Assistant Superintendent | Valid, expires 2030-05-20 | Lakeside Clinic TI, Assistant Superintendent (assignment-derived) | 50% free through 2027-02-26, then 100% free | Role mismatch: Assistant Superintendent, not Superintendent. Listed only because he holds the certification and has capacity. |

Not a candidate: emp_0042 Luis Herrera, Superintendent, dismissed effective 2026-08-15. Dismissed employees are not staffed on current or future work.

## Conflicts noticed while reading

Not part of the question, reported because they affect the same people.

| Employee | Type | Period | Detail | Assignments involved |
|---|---|---|---|---|
| emp_0121 Priya Natarajan | Time off overlap | 2027-02-01 to 2027-02-15 | asg_0402 stays at 100% during time off tof_0052; utilization periods show 100% across the time off | asg_0402, tof_0052 |

## Staffing proposal (dry run, nothing applied)

### Option A: Dana Whitfield, split for the first seven weeks

Dana finishes Lakeside Clinic TI at half allocation while covering Ridgeview mobilization at half, then moves to Ridgeview full time on December 19.

| # | Action | Assignment | Employee | Project | Role | Start | End (excl.) | % | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Update | asg_0388 | emp_0107 Dana Whitfield | proj_0027 Lakeside Clinic TI | Superintendent | 2026-06-01 | 2026-11-02 | 100 | End full-time Lakeside the day before Ridgeview starts |
| 2 | Create | (new) | emp_0107 Dana Whitfield | proj_0027 Lakeside Clinic TI | Superintendent | 2026-11-02 | 2026-12-19 | 50 | Keep half coverage on Lakeside through its original end |
| 3 | Create | (new) | emp_0107 Dana Whitfield | proj_0031 Ridgeview Elementary Classroom Addition | Superintendent | 2026-11-02 | 2026-12-19 | 50 | Ridgeview mobilization at half allocation |
| 4 | Update | asg_0410 | emp_0107 Dana Whitfield | proj_0031 Ridgeview Elementary Classroom Addition | Superintendent | 2026-12-19 | 2027-08-01 | 100 | Fill the demand once Lakeside ends; time-off conflict remains |
| 5 | Create | (new residual demand) | (unfilled) | proj_0031 Ridgeview Elementary Classroom Addition | Superintendent | 2026-11-02 | 2026-12-19 | 50 | Preserve the uncovered half of the original 100% need |
| 6 | Create | (new residual demand) | (unfilled) | proj_0027 Lakeside Clinic TI | Superintendent | 2026-11-02 | 2026-12-19 | 50 | Preserve coverage lost by reducing Lakeside to half |

**Side effects**

- Lakeside Clinic TI (proj_0027) drops from 100% to 50% superintendent coverage for 2026-11-02 to 2026-12-19 (47 days). Tom Okafor (emp_0088) is already there at 50% as Assistant Superintendent; whether that is enough for closeout is your call, and this proposal does not add anyone to Lakeside.
- Ridgeview (proj_0031) has 50% superintendent coverage, not 100%, for its first 47 days. Rows 3 and 5 retain the original 100% need as 50% filled plus 50% unfilled. Row 6 also retains Lakeside’s lost 50% coverage; neither project’s requirement is reduced.
- Dana's time off tof_0061 (2027-03-15 to 2027-03-22) falls inside the Ridgeview assignment. That is 7 days with no superintendent on site unless you cover it; it is left as is here.
- asg_0411 (Ridgeview Project Manager, 50%) stays unfilled.

**Resulting utilization for emp_0107 Dana Whitfield**

| Period (end excl.) | Before | After |
|---|---|---|
| 2026-11-02 to 2026-12-19 | 100 (asg_0388) | 100 (rows 2 and 3, 50 + 50) |
| 2026-12-19 to 2027-03-15 | 0 | 100 (asg_0410) |
| 2027-03-15 to 2027-03-22 | 0, time off | 100 assigned during time off; flagged above |
| 2027-03-22 to 2027-08-01 | 0 | 100 (asg_0410) |

No assignment allocation exceeds 100, but March 15–21 remains a time-off conflict with zero available coverage. Dana's two bench runs, December 19–March 15 (86 days) and March 22–August 1 (132 days), are consumed; the intervening 7 days of time off were never bench. These are projected assignment allocations, not re-read server utilization.

### Option B: Marcus Bell, if his OSHA 30 has been renewed

One change, no side effects on anyone else, but only valid once Buildr holds a current OSHA 30 for him. This skill will not assume the renewal.

| # | Action | Assignment | Employee | Project | Role | Start | End (excl.) | % | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Update | asg_0410 | emp_0093 Marcus Bell | proj_0031 Ridgeview Elementary Classroom Addition | Superintendent | 2026-11-02 | 2027-08-01 | 100 | Fill the demand; Marcus is at 0% for the entire window |

Resulting utilization for emp_0093: 100 from 2026-11-02 to 2027-08-01, consuming 272 days of the 273-day observed bench window; November 1 remains free.

**Not changed in either option:** emp_0121 Priya Natarajan (fully committed to Harbor Point), emp_0088 Tom Okafor (role mismatch), asg_0411 (PM demand, outside the question).

This is a staffing analysis, not a determination that anyone meets the project's safety or licensing requirements; the OSHA 30 check is against the certification rows in Buildr only.

This offline replay stops at the proposal. For live execution, Option A requires authorization of all six changes and its remaining gaps. Option B requires re-reading the recorded renewal and authorizing that specific change. Nothing has been written.
