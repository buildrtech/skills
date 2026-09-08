# Synthetic workforce export — not a live account

As-of 2027-12-01. Analyze Jan 1 through Feb 29, 2028, and propose coverage
for the supplied demand at 50% per candidate, preserving the full need.
No MCP connection exists; use only this explicitly supplied snapshot. No writes.
End dates are exclusive; certification expiration dates are inclusive.
All listed employees are active superintendents, included in headcount.
There are no other employees, assignments, certifications, or time off in
this fixture. Blair's utilization response is explicitly incomplete.

Project p_birch, Birch School, needs superintendent role r_super:
assignment d_01, unfilled, 2028-01-01 to 2028-03-01, 100%.

| Employee | Computed start | Computed end | Utilization | Time off |
|---|---|---|---|---|
| e_a Aster | 2028-01-01 | 2028-01-31 | 0 | false |
| e_a Aster | 2028-01-31 | 2028-02-01 | 0 | true |
| e_a Aster | 2028-02-01 | 2028-03-01 | 0 | false |
| e_b Blair | 2028-01-01 | 2028-02-01 | 50 | false |
| e_c Casey | 2028-01-01 | 2028-01-31 | 200 | false |
| e_c Casey | 2028-01-31 | 2028-03-01 | 0 | false |

Time off: t_01, Aster, 2028-01-31 to 2028-02-01.
Blair assignment a_b on project p_lake Lake Clinic is 50% Jan 1 to Feb 1.
Casey assignments a_c1 and a_c2 on projects p_west West Depot and p_east
East Depot are each 100% Jan 1 to Jan 31.

The staffing need requires the supplied site-orientation certification c_site.
Aster's row was issued 2027-01-01 and expires 2028-02-15.
Blair's row was issued 2027-01-01 and expires 2029-01-01.
Casey has no c_site row. No minimum experience is required.

Report individual capped and uncapped averages where the data supports them;
state when team-wide results cannot be established. Include bench runs of at
least 30 consecutive available calendar days. Propose only defensible coverage
and identify all residual demand and conditions.
