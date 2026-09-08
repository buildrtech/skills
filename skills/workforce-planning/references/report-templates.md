# Report templates

Lead with the finding, then the detail. Every employee appears as id and
name, every project as id and supplied name, and every assignment by id. Each section says which
operation the facts came from and the window they cover. Use only the
sections the question needs; a bench question does not need a staffing
proposal.

## Header

```
# <Question in one line>: <window start> to <window end> (end exclusive)

**Finding:** <the answer in one or two sentences>
**Source:** <live Buildr operations OR supplied offline/synthetic source>, read/as-of <date>; <completeness>
**Window:** <start> to <end>, end date exclusive. <how the window was resolved>
```

## Utilization summary

One row per employee in scope. Utilization is the calendar-day-weighted average
of the employee's periods across the window, with each period capped at 100 before weighting for the team
average row. State the headcount denominator; unknown intervals prevent a
complete window average. Peak is the highest single period.

```
## Utilization summary

| Employee | Role | Avg % (window) | Peak % | Peak period | Time off in window | Note |
|---|---|---|---|---|---|---|
| emp_0107 Dana Whitfield | Superintendent | 62 | 100 | 2026-11-01 to 2026-12-19 | 2027-03-15 to 2027-03-22 | |
| ... | | | | | | |
| **Team (capped at 100)** | | 66.7 | | | | 1 employee capped |
```

## Bench list

Runs of 0 percent utilization at least 30 consecutive days long (or the
user's definition), inside the window. Exclude time off; say so.

```
## Bench (30+ consecutive days at 0%)

| Employee | Role | Bench start | Bench end (excl.) | Days | Last assignment | Next assignment |
|---|---|---|---|---|---|---|
| emp_0093 Marcus Bell | Superintendent | 2026-11-01 | 2027-08-01 | 273 | asg_0371 Cedar Mill Warehouse | none |
```

## Demand list

Assignments with no employee. These are not utilization. Group by project.

```
## Unfilled demand

| Assignment | Project | Role | Phase | Start | End (excl.) | % | Days |
|---|---|---|---|---|---|---|---|
| asg_0410 | proj_0031 Ridgeview Elementary Addition | Superintendent | Construction | 2026-11-02 | 2027-08-01 | 100 | 272 |
```

## Conflict list

One row per conflict with the ids that produce it and a plain reading of
what it means.

```
## Conflicts

| Employee | Type | Period | Detail | Assignments involved |
|---|---|---|---|---|
| emp_0121 Priya Natarajan | Time off overlap | 2027-02-01 to 2027-02-15 | 100% assigned during time off tof_0052 | asg_0402 |
```

Conflict types: Overallocated (above 100), Time off overlap, Dismissed
after effective date, Role mismatch.

## Candidate ranking

For "find a candidate" and "staff a project" questions. Rank by fit (role,
certification, experience) then availability. State every disqualifier.

```
## Candidates for <role> on <project>, <window>

| Rank | Employee | Role | <Certification> | Relevant experience | Capacity in window | Disqualifier |
|---|---|---|---|---|---|---|
| 1 | emp_0107 Dana Whitfield | Superintendent | Valid, expires 2028-03-14 | 1 K-12 project (assignment-derived) | 0% until 2026-12-19; 100% afterward except March 15–21 time off | Occupied Nov 2–Dec 18; unavailable March 15–21 |
| 2 | emp_0093 Marcus Bell | Superintendent | Expired 2026-06-30 | 1 K-12 project (previous employer) | 100% entire window | OSHA 30 expired in Buildr |
```

## Staffing proposal

The dry run. Numbered, one row per assignment change, with side effects
and the projected allocation for every affected employee. Include residual
unfilled rows where coverage is split. For live changes awaiting authorization,
end with the specific confirmation question. Offline replay ends at the proposal.

```
## Staffing proposal (dry run, nothing applied)

### Option A: <one-line description>

| # | Action | Assignment | Employee | Project | Role | Start | End (excl.) | % | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 1 | <action> | <existing ID or new-row label> | <employee or unfilled> | <project> | <role> | <start> | <end> | <allocation> | <reason> |

**Residual demand:** <original requirement = filled + still unfilled, by interval;
include unavailable coverage during time off>

**Side effects**
- <project that loses coverage, by how much, for what dates>
- <any demand this leaves open>

**Resulting utilization**
| Employee | Period | Before | After |
|---|---|---|---|

**Not changed:** <employees and assignments reviewed but left alone, and why>

Reply "apply option A" to make these <n> changes now, or tell me what to adjust. Nothing has been written.
```

After execution, replace the proposal with a verification section:

```
## Applied and verified

| # | Action | Assignment | Result |
|---|---|---|---|
| 1 | Update | asg_0410 | employee_id emp_0107, 2026-12-19 to 2027-08-01, 100% (re-read) |

Utilization periods for emp_0107 re-read after the change: <summary>.
```
