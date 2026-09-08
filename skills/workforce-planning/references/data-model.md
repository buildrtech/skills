# Workforce data model

The entities behind every staffing answer, and the arithmetic rules the
skill applies to them. Field names below are illustrative; the exact names
and filters must be discovered from the connected tool schemas. Operation names
are historical lookup hints, not a callable contract.

## Entities

```text
Workforce role
  `-- Employee
        |-- Assignments ------> Project + phase + date range + allocation %
        |-- Time off
        |-- Certifications ---> Certification type + issued/expires
        `-- Experience -------> assignment-derived + previous employer

Unfilled assignment
  `-- Role + Project + phase + date range + allocation %, with no employee
```

| Entity | Operations | Key fields |
|---|---|---|
| Role | `listWorkforceRoles`, `createWorkforceRole` | `id`, `name`. Account-specific job titles (Superintendent, Project Manager, Foreman). Employees and assignments reference a role. |
| Employee | `listWorkforceEmployees`, `showWorkforceEmployee`, `createWorkforceEmployee`, `updateWorkforceEmployee`, `dismissWorkforceEmployee` | `id`, `name`, `role_id`, headcount flag, dismissal state and effective date. An employee can be excluded from headcount and still be assignable. |
| Assignment | `listWorkforceAssignments`, `showWorkforceAssignment`, `createWorkforceAssignment`, `updateWorkforceAssignment`, `deleteWorkforceAssignment` | `id`, `employee_id` (null when unfilled), `role_id`, `project_id`, phase or stage, `start_date`, `end_date` (exclusive), `utilization` (percent of one person). May use date formulas tied to project dates instead of fixed dates; inspect `describe` before writing formulas. |
| Utilization period | `listWorkforceEmployeeUtilizationPeriods` | `employee_id`, `start_date`, `end_date` (exclusive), `utilization` (combined percent), contributing assignment ids, time-off flag. Read-only and computed by Buildr. |
| Time off | `listWorkforceTimeOffs`, `createWorkforceTimeOff` | `id`, `employee_id`, `start_date`, `end_date` (exclusive). Reduces availability to zero for its range. |
| Certification type | `listWorkforceCertificationTypes` | `id`, `name` (OSHA 30, First Aid/CPR, state license classes). |
| Employee certification | `listWorkforceEmployeeCertifications` | `employee_id`, `certification_type_id`, issued date, `expires_on`. Absent means the employee does not hold it in Buildr. |
| Experience | `listWorkforceEmployeeExperiences` (read-only projection), `listWorkforcePreviousEmployerExperiences` (writable backing rows) | `employee_id`, project or employer, role, dates, `source.resource` saying whether the row came from an assignment or a previous-employer record. |
| Project | `listProjects`, `getProjectById`, `listProjectStages` | `id`, `name`, preconstruction and construction dates, stages or phases that assignments attach to. |

## Rules

### Utilization

- Assignment utilization is the share of one employee's capacity that
  assignment consumes during its date range.
- Employee utilization is the sum of overlapping assignment allocations.
  100 means fully allocated. Above 100 means overallocated. Below 100 means
  capacity remains.
- Buildr computes utilization periods by splitting the timeline at every
  assignment and time-off boundary and summing what overlaps each piece.
  Use those periods as the authoritative answer; recompute from raw
  assignments only when the user asks for a custom method.
- Only filled periods are employee utilization. An assignment with no
  employee is demand for a role, and it contributes to nobody's number.

Worked example. Employee `emp_0107` has assignment A at 60 percent from
2026-11-01 to 2026-12-19 and assignment B at 60 percent from 2026-12-01 to
2027-01-15. The periods are:

| Period (end exclusive) | Contributing | Utilization | Reading |
|---|---|---|---|
| 2026-11-01 to 2026-12-01 | A | 60 | 40 available |
| 2026-12-01 to 2026-12-19 | A + B | 120 | overallocated by 20 |
| 2026-12-19 to 2027-01-15 | B | 60 | 40 available |

### Team averages

For each employee, weight periods by calendar days inside the window.
For the team figure, cap each period at 100 BEFORE duration weighting, then
average across the stated eligible headcount. Capping an employee window
average afterward can hide idle days. Excluded-from-headcount employees can
still be candidates but do not enter that denominator. State how time off
and dismissal affect the denominator; if data is incomplete report unknown
rather than silently averaging only returned periods. Three employees at 120, 100, and 0:

- Uncapped: (120 + 100 + 0) / 3 = 73.3, which reads as a reasonably busy
  team.
- Capped: (100 + 100 + 0) / 3 = 66.7, and the 0 stands out as one person
  fully on the bench.

Report the capped figure and, when useful, list who was capped and by how
much.

### Bench

Bench is a sustained run of zero utilization. The standard definition is at
least 30 consecutive days at 0 percent, inside the analysis window. Use the
user's definition instead if they give one, and say which was used.

- 0 percent from 2026-12-19 to 2027-01-10 is 22 days: not bench, just a gap.
- 0 percent from 2026-12-19 to 2027-02-01 is 44 days: bench.
- A run that starts before the window or ends after it counts only for the
  days inside the window unless the user asks otherwise.

Time off is not bench. A period flagged as time off may show zero or nonzero allocation;
either way the person is unavailable, not idle. Merge adjacent zero periods
only when neither is time off. Missing timeline intervals are unknown and
break a bench run; never infer zero from an omitted row.

### Exclusive end dates

`end_date` on assignments, time off, and utilization periods is exclusive:
the range covers `start_date` up to but not including `end_date`.

- 2026-11-01 to 2026-12-19 covers 48 days; its last working calendar day is
  2026-12-18.
- Two assignments are back to back, not overlapping, when the first ends on
  the date the second starts.
- "Through July 31" means `end_date: "2027-08-01"`.

Day counts here are calendar days. Do not convert to working days unless
the user asks and gives the calendar to use.

### Availability

Availability is capacity left after assignments and time off, over a given
window. It is never a timeless attribute of an employee. For a candidate
question, report the periods inside the window where the person has enough
capacity for the requested allocation, and the periods where they do not.

### Conflicts

Report each of these as a conflict with the ids involved:

- Any utilization period above 100.
- An assignment overlapping the same employee's time off.
- An assignment on a dismissed employee that ends after the dismissal
  effective date.
- An assignment whose role differs from the employee's role. Report it;
  the user decides whether it is intentional.

### Dismissal

Dismissal is a workforce lifecycle state with an effective date. It is not
deletion and not soft deletion. Rules:

- Use `dismissWorkforceEmployee` only for real departures the user asks
  for. Never delete an employee, or only exclude them from headcount, to
  simulate a departure.
- Dismissed employees are not candidates for current or future work.
- Dismissed employees may hold historical assignments that end on or
  before the dismissal effective date. For historical imports, create the
  employee in the intended dismissal state first, then create only
  assignments ending on or before that date.
- Active employees and unfilled assignments are what current staffing works
  with.

### Certifications and experience

- A certification counts only if a row exists for the employee and the
  certification type, and it is issued by the first needed day and valid through the last needed
  day. Treat absent expiration as non-expiring only when the source contract
  says so; otherwise validity is unknown. Confirm whether expiration itself
  is inclusive. In the supplied sample, expiration is inclusive. Expired or missing is a disqualifier, stated as
  such, never rounded up to "probably renewed".
- Experience rows carry `source.resource`. Assignment-derived rows come
  from Buildr assignments and cannot be edited. Previous-employer rows are
  editable through the previous-employer operations. Say which kind each
  cited row is.
- Role is the employee's role in Buildr. A person in an adjacent role
  (Assistant Superintendent for a Superintendent need) is reported as a
  role mismatch, not silently promoted.

### Coverage conservation

For each project/role interval, retain original required allocation as filled
plus residual unfilled demand. Filling 50% of a 100% row leaves 50% unfilled.
An employee assigned during time off supplies no available coverage for that
interval even if the assignment still reports 100%. Report that conflict
separately from ordinary unfilled rows, and avoid double-counting the need.
