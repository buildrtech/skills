# Superintendent coverage for d_01 on p_birch (Birch School): 2028-01-01 to 2028-03-01 (end exclusive)

**Finding:** Coverage can be defensibly proposed for only part of the need. Blair (e_b) can carry
50% for 2028-01-01 to 2028-02-01, and Aster (e_a) can carry 50% for 2028-01-01 to 2028-01-31 and
2028-02-01 to 2028-02-16. That fully covers the 100% requirement for 30 of the 60 days
(2028-01-01 to 2028-01-31) and leaves residual unfilled demand on every other interval, including
100% unfilled for 2028-02-16 to 2028-03-01. Casey (e_c) is disqualified: no c_site certification
record exists.

**Source:** Explicitly supplied synthetic snapshot (TASK.md fixture), as-of 2027-12-01. No Buildr MCP
connection exists and none was attempted; no reads or writes were performed against any account.
Completeness: the fixture states it contains all employees, assignments, certifications and time off,
except that Blair's utilization response is explicitly incomplete. Offline replay cannot establish
current availability and cannot execute changes — this ends at a dry run.

**Window:** 2028-01-01 to 2028-03-01, end date exclusive ("Jan 1 through Feb 29, 2028"; 2028 is a leap
year, so the window is 60 calendar days). The staffing need d_01 runs 2028-01-01 to 2028-03-01, so the
analysis window and the need window coincide. All day counts are calendar days. Certification
expiration dates are inclusive, per the supplied contract.

## Read scope and limitations

- Entities used: role r_super; employees e_a, e_b, e_c (all active superintendents, all in headcount);
  unfilled assignment d_01; filled assignments a_b, a_c1, a_c2; time off t_01; certification type
  c_site and the two employee certification rows; supplied computed utilization periods.
- Computed utilization periods were used as the source of current utilization; they were not
  reconstructed from the assignment rows. Assignment rows are cited only to explain conflicts and
  side effects.
- Missing coverage is treated as unknown, never as zero: Blair has no period covering
  2028-02-01 to 2028-03-01 (29 days). No experience projection rows were supplied, and none are
  needed — the need states no minimum experience.
- Deterministic clipping, bench runs, capacity and duration-weighted averages were computed with the
  bundled helper `scripts/analyze_periods.py`, one normalized file per employee (inputs retained under
  `output/work/`). Unfilled demand d_01 contributes to nobody's utilization.

## Utilization summary

Calendar-day-weighted across the 60-day window. The team row would cap each period at 100 before
weighting and divide by the eligible headcount of 3 (all three employees are active and in headcount;
none are excluded or dismissed).

| Employee | Role | Avg % (window) | Capped avg % | Peak % | Peak period | Time off in window | Note |
|---|---|---|---|---|---|---|---|
| e_a Aster | r_super Superintendent | 0 | 0 | 0 | whole window | 2028-01-31 to 2028-02-01 (t_01) | Complete timeline |
| e_b Blair | r_super Superintendent | unknown | unknown | 50 (observed) | 2028-01-01 to 2028-02-01 | none supplied | 2028-02-01 to 2028-03-01 not returned |
| e_c Casey | r_super Superintendent | 100 | 50 | 200 | 2028-01-01 to 2028-01-31 | none supplied | Capped by 100 points for 30 days |
| **Team (capped at 100), n=3** | | **cannot be established** | | | | | Blair's window average is unknown, so no team average is defensible |

Individual figures are reported where the data supports them (Aster, Casey). Blair's window average —
capped or uncapped — cannot be established, and because a team average requires all three members of
the stated denominator, no team-wide capped or uncapped average can be established either. Averaging
only the returned periods would silently reduce Blair's window to 31 of 60 days.

Note that Casey's uncapped 100 reads as "fully busy on average" while the capped 50 exposes what is
actually there: 30 days at double allocation followed by 30 idle days. Neither is availability.

## Bench (30+ consecutive days at 0%, inside the window)

Standard definition used: at least 30 consecutive calendar days at 0% utilization, excluding time off,
clipped to the window.

| Employee | Role | Bench start | Bench end (excl.) | Days | Note |
|---|---|---|---|---|---|
| e_a Aster | r_super | 2028-01-01 | 2028-01-31 | 30 | Run terminated by time off t_01, not by an assignment |
| e_c Casey | r_super | 2028-01-31 | 2028-03-01 | 30 | Follows the end of a_c1 and a_c2 |

Not bench: Aster's second zero run, 2028-02-01 to 2028-03-01, is 29 days — one day short. It is not
merged with the January run, because the intervening period is time off. Blair has no bench run; the
observed portion is at 50% and the remainder is unknown, and unknown intervals cannot form or extend a
bench run.

## Unfilled demand (observed, before any proposal)

| Assignment | Project | Role | Start | End (excl.) | % | Days |
|---|---|---|---|---|---|---|
| d_01 | p_birch Birch School | r_super Superintendent | 2028-01-01 | 2028-03-01 | 100 | 60 |

## Conflicts

| Employee | Type | Period | Detail | Records involved |
|---|---|---|---|---|
| e_c Casey | Overallocated | 2028-01-01 to 2028-01-31 | Computed utilization 200% — 100 points over capacity for 30 days | a_c1 (p_west West Depot, 100%), a_c2 (p_east East Depot, 100%) |

No time-off overlap, dismissal or role-mismatch conflicts exist in the supplied data. Casey's
overallocation is a pre-existing condition on p_west/p_east; it is reported here but is not resolved by
this staffing question, and Casey is disqualified for d_01 on other grounds anyway.

## Candidates for r_super Superintendent on p_birch (d_01), 2028-01-01 to 2028-03-01, at 50%

| Rank | Employee | Role | c_site certification | Experience | Capacity at 50% in window | Disqualifier / limit |
|---|---|---|---|---|---|---|
| 1 | e_b Blair | r_super — match | Valid: issued 2027-01-01, expires 2029-01-01 (inclusive) — covers every day of the need | None required | 50% available 2028-01-01 to 2028-02-01 (exactly meets the 50% ask); unknown 2028-02-01 to 2028-03-01 | Availability for the last 29 days is unknown, not zero — cannot be proposed |
| 2 | e_a Aster | r_super — match | Valid: issued 2027-01-01, expires 2028-02-15 (inclusive) — lapses mid-need; last certified day 2028-02-15, so certified coverage ends 2028-02-16 (exclusive) | None required | 100% available except time off t_01 | Unavailable 2028-01-31 to 2028-02-01 (t_01); not certified 2028-02-16 to 2028-03-01 |
| — | e_c Casey | r_super — match | **No c_site row in Buildr** | None required | 0% available 2028-01-01 to 2028-01-31 (200% utilized); 100% available 2028-01-31 to 2028-03-01 | Missing certification evidence for a need that requires c_site — disqualified for the whole window |

Blair is ranked first on fit: the certification is valid for every day the need runs, whereas Aster's
lapses inside the window. Aster is ranked second but supplies more proposable days.

Two statements the data does not support and which are not made anywhere in this analysis: that
Aster's c_site will be renewed before 2028-02-16, and that Casey holds c_site in the real world. A
missing certification row establishes only missing evidence in Buildr; it is not a judgement about
Casey's actual qualification, and it is not something to work around by changing a role or assuming a
renewal. If either of those is in fact wrong, the fix is a corrected certification record, after which
the affected intervals below should be re-evaluated.

## Staffing proposal (dry run, nothing applied — offline replay cannot execute)

### Option A: split d_01 at 50% per candidate, preserving the full 100% requirement

| # | Action | Assignment | Employee | Project | Role | Start | End (excl.) | % | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Create (new row N1) | new | e_b Blair | p_birch | r_super | 2028-01-01 | 2028-02-01 | 50 | Blair has exactly 50% free and valid c_site; stops at 2028-02-01 because availability after that is unknown |
| 2 | Create (new row N2) | new | e_a Aster | p_birch | r_super | 2028-01-01 | 2028-01-31 | 50 | Aster is on bench with 100% free and certified; stops before time off t_01 |
| 3 | Create (new row N3) | new | e_a Aster | p_birch | r_super | 2028-02-01 | 2028-02-16 | 50 | Resumes after t_01; ends at the first day Aster's c_site is no longer valid |
| 4 | Keep unfilled (residual) | d_01 (retain, reduced or split) | unfilled | p_birch | r_super | see residual table | | | The original 100% requirement is preserved; only the covered share is deducted |

Rows 1–3 are new assignment rows. d_01 must **not** simply be shortened or marked filled: doing so
would erase uncovered demand. The residual below is the requirement that remains open.

**Residual demand** (original requirement = proposed filled + still unfilled, interval by interval):

| Interval (end excl.) | Days | Required | Proposed filled | Residual unfilled | Note |
|---|---|---|---|---|---|
| 2028-01-01 to 2028-01-31 | 30 | 100% | 100% (Blair 50 + Aster 50) | 0% | Fully covered |
| 2028-01-31 to 2028-02-01 | 1 | 100% | 50% (Blair) | 50% | Aster unavailable — time off t_01. No assignment is proposed across this day; had one been written at 50%, it would still supply zero coverage |
| 2028-02-01 to 2028-02-16 | 15 | 100% | 50% (Aster) | 50% | Blair's capacity here is unknown, so no Blair coverage is claimed |
| 2028-02-16 to 2028-03-01 | 14 | 100% | 0% | 100% | Aster's c_site expired after 2028-02-15; Blair unknown; Casey uncertified |

Totals: 30 of 60 days fully covered; 16 days covered at half; 14 days entirely uncovered. This is
partial coverage, not a fully staffed recommendation for d_01.

**Side effects**
- No existing project loses coverage. a_b (p_lake Lake Clinic, 50%), a_c1 (p_west) and a_c2 (p_east)
  are untouched, so Blair stays at 100% total and Casey's 200% overallocation is neither worsened nor
  fixed.
- Blair reaches exactly 100% utilization for 2028-01-01 to 2028-02-01 — no remaining headroom on that
  interval, and no margin if a_b is extended or another need arrives.
- Aster's 30-day January bench run is consumed by this proposal; after it, Aster is at 50%, not 0%.
- 2028-02-16 to 2028-03-01 remains fully open demand on p_birch and needs a source outside this
  roster, or a corrected/renewed certification record.

**Resulting utilization (proposed, computed at every affected boundary — not server state)**

| Employee | Period (end excl.) | Before | After |
|---|---|---|---|
| e_a Aster | 2028-01-01 to 2028-01-31 | 0 | 50 |
| e_a Aster | 2028-01-31 to 2028-02-01 | 0 (time off t_01) | 0 (time off t_01 — unavailable regardless) |
| e_a Aster | 2028-02-01 to 2028-02-16 | 0 | 50 |
| e_a Aster | 2028-02-16 to 2028-03-01 | 0 | 0 |
| e_b Blair | 2028-01-01 to 2028-02-01 | 50 | 100 |
| e_b Blair | 2028-02-01 to 2028-03-01 | unknown | unknown + 0 proposed |
| e_c Casey | whole window | 200 then 0 | unchanged |

**Not changed:** Casey (e_c) — role matches and 2028-01-31 onward is genuinely free, but the missing
c_site record disqualifies them for a need that requires it; no role change or assumed certification
was used to manufacture a match. a_b, a_c1, a_c2, t_01 and the p_lake/p_west/p_east commitments are
all left alone. No employee was created, updated, or dismissed to solve this scheduling question.

## Conditions that would change the answer

1. **Blair's missing utilization for 2028-02-01 to 2028-03-01.** If Blair is confirmed at or below 50%
   there, Blair could extend to 2028-03-01 at 50%, which would reduce the residual on
   2028-02-01 to 2028-02-16 to 0% and on 2028-02-16 to 2028-03-01 to 50%. This requires re-reading
   Blair's computed periods, not an assumption.
2. **Aster's c_site renewal.** If a renewed row is recorded covering 2028-02-16 through 2028-02-29,
   row 3 could extend to 2028-03-01, cutting the final residual to 50%. Conditional on the record
   existing at execution time, per the pre-execution re-read rule.
3. **A c_site record for Casey.** If one exists and is valid through 2028-02-29, Casey becomes a
   candidate from 2028-01-31 onward and could close the remaining February gap.
4. **A reduced requirement.** Accepting less than 100% coverage on the partially covered intervals is a
   separate user decision about the need itself, not a staffing finding, and would have to be recorded
   against d_01 explicitly.

Nothing has been written and nothing can be: this is an offline replay of a supplied synthetic
snapshot with no MCP connection. Applying any of the above requires a live authenticated session, a
fresh re-read of the affected assignments, certifications and computed periods, and explicit
authorization of the specific numbered changes.
