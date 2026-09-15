# Capacity rules and calculator contract

Use one unit at a time. Percent allocations need their stated denominator:
50% of a 32-hour week is 16 hours, not 20. FTE requires an explicit standard
workweek. Subtract only absence hours inside scheduled working time, and count
overlapping absences once. Ask whether a supplied availability total already
excludes time off before subtracting it. Do not net an overtime week against an
underloaded future week.

For each period:
- usable = capacity_hours - unavailable_hours
- free = max(0, usable - assigned_hours)
- overallocated = max(0, assigned_hours - usable)
- after proposed assignments, reduce free and demand by the same hours.

Use local dates with an explicit timezone. Resolve conflicting revisions and
unknown IDs before merging records. For weekly rows, `week` is an ISO date
(YYYY-MM-DD), consistently the start of the user's planning week. Split
multiweek assignments using the actual calendar, not an even split unless the
source supports it. The calculator cannot prove shift feasibility.

Input JSON has three arrays:

- `capacity`: unique `id` for each person/week row, `person`, `week`, numeric
  `capacity_hours`, `unavailable_hours`, `assigned_hours`.
- `demand`: unique `id`, `week`, numeric `hours` representing **unfilled** demand.
- `proposals` (optional): `capacity_id`, `demand_id`, numeric `hours`. Referenced
  weeks must match. Each proposal is an increment, not a replacement total.

Keep source citations and role/credential/shift checks in the accompanying
report. Row IDs should refer back to original data. No missing-value defaults
are used for capacity or demand. Values must be finite, nonnegative numbers;
time off cannot exceed gross scheduled hours. Duplicate IDs or person/week
rows are errors. The calculator rejects proposals exceeding remaining capacity
or unfilled demand and preserves current overallocations in its output.

Output contains capacity and demand ledgers. Hours are decimal strings to retain
exact arithmetic. The calculator reads input and prints JSON; it never edits
source files or changes assignments.
