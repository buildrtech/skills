# Cedar Hollow staffing plan

The proposed 20 hours would leave **4 hours uncovered**, and Cam is already
**4 hours over capacity**. These are separate issues; uncovered demand is not
offset by somebody else's overload. Neither move is ready to schedule until
daily timing is checked; Bo's 12 hours also require confirmed site orientation.

Planning week: 2026-09-21, America/Denver. Source: the fictional scheduler
export and qualification notes in [input-week.md](input-week.md). Calculation
input: [input-week.json](input-week.json). Hours are weekly, not FTE.

| Row | Usable capacity | Existing assignments | Free before | Overallocated | Proposed addition | Free after |
|---|---:|---:|---:|---:|---:|---:|
| c-ana | 40 - 8 = 32 | 24 | 8 | 0 | 8 | 0 |
| c-bo | 32 - 0 = 32 | 20 | 12 | 0 | 12 | 0 |
| c-cam | 40 - 0 = 40 | 44 | 0 | 4 | 0 | 0 |

| Demand | Unfilled before | Proposed coverage | Unfilled after |
|---|---:|---:|---:|
| d-library | 24 | 8 + 12 = 20 | 4 |

No existing assignment is reduced. Proposed additions total 20 hours, exactly
the reduction in unfilled demand. Cam's overload remains visible rather than
being treated as negative bench or silently assigned to overtime.

## Decisions and checks

- **Ana → d-library, 8 hours:** finish carpentry is confirmed by the supplied
  roster. Check her actual absence dates, existing shifts, and travel before
  selecting the work slots.
- **Bo → d-library, 12 hours:** trade matches; orientation is unverified. Confirm
  it and check daily timing before scheduling. If Bo cannot work, the residual
  after Ana alone is 16 hours, not 4.
- Resolve Cam's existing 4-hour overload with the scheduler. Moving Cam could
  create a different gap; no reassignment or overtime is assumed here.
- Find coverage for the remaining 4 hours, or agree a demand change. No other
  candidate data was supplied. Weekly arithmetic does not establish shift fit.

This is a proposal only. No assignments were saved and nobody was notified.
