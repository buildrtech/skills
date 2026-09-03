# Staffing request

**From the user, 2026-09-03:**

> Who can superintend the Ridgeview job from November through July? Needs
> OSHA 30. And what does that do to their current assignments?

The Buildr MCP server is connected with read and write scope. Everything
below is what the account returned; it is synthetic and every id is a
placeholder.

## Project (`listProjects`, `getProjectById`)

| Field | Value |
|---|---|
| id | proj_0031 |
| name | Ridgeview Elementary Classroom Addition |
| construction start | 2026-11-02 |
| substantial completion | 2027-07-30 |
| stages | Preconstruction (ended 2026-10-30), Construction (2026-11-02 to 2027-07-31) |

## Roles (`listWorkforceRoles`)

| id | name |
|---|---|
| role_0002 | Assistant Superintendent |
| role_0003 | Superintendent |
| role_0005 | Project Manager |

## Employees in the Superintendent and Assistant Superintendent roles (`listWorkforceEmployees`)

| id | name | role | status |
|---|---|---|---|
| emp_0042 | Luis Herrera | Superintendent | dismissed, effective 2026-08-15 |
| emp_0088 | Tom Okafor | Assistant Superintendent | active |
| emp_0093 | Marcus Bell | Superintendent | active |
| emp_0107 | Dana Whitfield | Superintendent | active |
| emp_0121 | Priya Natarajan | Superintendent | active |

## Assignments overlapping 2026-11-01 to 2027-08-01 for those employees and for Ridgeview (`listWorkforceAssignments`)

| id | employee | project | role | start | end (excl.) | % |
|---|---|---|---|---|---|---|
| asg_0388 | emp_0107 Dana Whitfield | proj_0027 Lakeside Clinic TI | Superintendent | 2026-06-01 | 2026-12-19 | 100 |
| asg_0402 | emp_0121 Priya Natarajan | proj_0029 Harbor Point Parking Structure | Superintendent | 2026-04-06 | 2027-10-01 | 100 |
| asg_0395 | emp_0088 Tom Okafor | proj_0027 Lakeside Clinic TI | Assistant Superintendent | 2026-08-03 | 2027-02-27 | 50 |
| asg_0410 | (unfilled) | proj_0031 Ridgeview Elementary Classroom Addition | Superintendent | 2026-11-02 | 2027-08-01 | 100 |
| asg_0411 | (unfilled) | proj_0031 Ridgeview Elementary Classroom Addition | Project Manager | 2026-11-02 | 2027-08-01 | 50 |

Marcus Bell (emp_0093) has no assignment in the window. His last assignment
was asg_0371 on proj_0024 Cedar Mill Warehouse, ending 2026-10-03.

## Time off overlapping the window (`listWorkforceTimeOffs`)

| id | employee | start | end (excl.) |
|---|---|---|---|
| tof_0052 | emp_0121 Priya Natarajan | 2027-02-01 | 2027-02-15 |
| tof_0061 | emp_0107 Dana Whitfield | 2027-03-15 | 2027-03-22 |

## Utilization periods, 2026-11-01 to 2027-08-01 (`listWorkforceEmployeeUtilizationPeriods`)

| employee | start | end (excl.) | % | note |
|---|---|---|---|---|
| emp_0088 Tom Okafor | 2026-11-01 | 2027-02-27 | 50 | asg_0395 |
| emp_0088 Tom Okafor | 2027-02-27 | 2027-08-01 | 0 | |
| emp_0093 Marcus Bell | 2026-11-01 | 2027-08-01 | 0 | |
| emp_0107 Dana Whitfield | 2026-11-01 | 2026-12-19 | 100 | asg_0388 |
| emp_0107 Dana Whitfield | 2026-12-19 | 2027-03-15 | 0 | |
| emp_0107 Dana Whitfield | 2027-03-15 | 2027-03-22 | 0 | time off tof_0061 |
| emp_0107 Dana Whitfield | 2027-03-22 | 2027-08-01 | 0 | |
| emp_0121 Priya Natarajan | 2026-11-01 | 2027-02-01 | 100 | asg_0402 |
| emp_0121 Priya Natarajan | 2027-02-01 | 2027-02-15 | 100 | asg_0402 during time off tof_0052 |
| emp_0121 Priya Natarajan | 2027-02-15 | 2027-08-01 | 100 | asg_0402 |

## Certifications (`listWorkforceCertificationTypes`, `listWorkforceEmployeeCertifications`)

Certification type cert_0004 is "OSHA 30-Hour Construction".

| employee | certification | issued | expires |
|---|---|---|---|
| emp_0088 Tom Okafor | cert_0004 OSHA 30 | 2025-05-20 | 2030-05-20 |
| emp_0093 Marcus Bell | cert_0004 OSHA 30 | 2021-06-30 | 2026-06-30 |
| emp_0107 Dana Whitfield | cert_0004 OSHA 30 | 2023-03-14 | 2028-03-14 |
| emp_0121 Priya Natarajan | cert_0004 OSHA 30 | 2024-09-02 | 2029-09-02 |

Luis Herrera (emp_0042) has no certification rows.

## Experience (`listWorkforceEmployeeExperiences`)

| employee | project or employer | role | dates | source.resource |
|---|---|---|---|---|
| emp_0093 Marcus Bell | Pinecrest Middle School Gym (previous employer: Northfield Builders) | Superintendent | 2022-01 to 2023-06 | previous_employer_experience |
| emp_0093 Marcus Bell | proj_0024 Cedar Mill Warehouse | Superintendent | 2025-11-03 to 2026-10-03 | assignment |
| emp_0107 Dana Whitfield | proj_0018 Fairview Elementary Renovation | Superintendent | 2024-06-03 to 2025-08-15 | assignment |
| emp_0107 Dana Whitfield | proj_0027 Lakeside Clinic TI | Superintendent | 2026-06-01 to 2026-12-19 | assignment |
| emp_0121 Priya Natarajan | proj_0029 Harbor Point Parking Structure | Superintendent | 2026-04-06 to 2027-10-01 | assignment |
| emp_0088 Tom Okafor | proj_0027 Lakeside Clinic TI | Assistant Superintendent | 2026-08-03 to 2027-02-27 | assignment |
