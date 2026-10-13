# Workforce planning verification

## Revision 3.0.0: staffing meeting prep for project staff

Previous revision: `7d8e853` (2.0.0), a weekly hours calculator for three
named field workers. This revision replaces it outright; the hours calculator,
its contract, and its samples are removed.

### Why the reframe

Public material on how commercial GCs run workforce planning describes a
different job from the 2.0.0 skill:

- Bridgit, *How to run an effective workforce planning meeting*
- Bridgit, *Guide to workforce forecasting*
- Bridgit, Skender case study
- Buildr, *Construction Workforce Management: 2026 Ops Director Guide*

That job is salaried project staff (PMs, superintendents, PEs, APMs,
assistant superintendents) allocated by month over 6 to 12 months. It covers
pursuits weighted by win probability, roll-offs including closeout, and
overload limits per role (commonly 120% for PMs and 100% for superintendents).
The work is usually done in a people-by-month Excel sheet in a weekly or
monthly ops meeting. Crew scheduling by the hour is a separate job and is now
out of scope.

### What changed

- `scripts/staffing-core.mjs` is a pure module with no dependencies. It
  validates data, computes:
  - load
  - overloads (rolling three-month window)
  - leave and employment conflicts
  - unfilled seats
  - certification gaps
  - ranked internal candidates with a suggested move
  - roll-offs
  - role balance and hiring signals
  - pursuit risks

  It also renders the plan and the brief.
- `scripts/plan.mjs` builds one self-contained HTML file. The same core is
  inlined, so pursuit toggles and what-if moves recalculate in the browser with
  identical arithmetic. The HTML is pre-rendered, so it reads correctly with
  scripts disabled.
- The sample company "Halvorsen Builders" is invented: 34 staff, 9 jobs, 6
  pursuits. It ships the messy source exports a real ops team would send:
  - a staffing sheet with nicknames, bare codes, pencilled `?` work, a GS
    split with no percentages, and a "TBD Super" row
  - a project list with a slipped substantial completion
  - a CRM export with a moved start date
  - an HR roster with a retirement, a new hire, and parental leave

  The normalized JSON records each judgment call as an open question.

### Checks run

| Check | Result |
|---|---|
| `node --test evals/tasks/workforce-planning/staffing-core.test.mjs` (Node 24.21) | 14/14 pass |
| Mutation check: roll-off threshold, overload limit, candidate sort order, lost-pursuit handling, HTML escaping, gap threshold, end-date capacity each broken in turn | every mutation fails 1 to 5 tests |
| Bundled `output-staffing-plan.html` and `output-staffing-brief.md` | byte-identical to a fresh `plan.mjs` run (asserted by a test) |
| Browser (Chromium via agent-browser) on the bundled plan | no console errors |
| Pursuit toggle | marking Riverside won commits its seats and raises Dave Kowalski to 125% in March |
| **Try** on an unfilled seat | adds a move and recomputes; **Remove** restores the totals |
| **Export scenario**, then **Import scenario** (real file upload) | round trip restores state; `plan.mjs --scenario` accepts the same file |
| 390 px viewport | no horizontal overflow |
| axe-core (WCAG 2.1 A/AA) | 0 violations. Two items need manual review: contrast over the hatched leave pattern, and header-only grid group rows. |

### Not established

No fresh-context model comparison has been run on this revision, so nothing
here shows how well an agent normalizes an unfamiliar staffing sheet. The
sample is a demonstration and is not held-out evidence. The arithmetic is
deterministic and tested; the normalization judgment is not.

### Commands

```bash
node skills/workforce-planning/scripts/plan.mjs skills/workforce-planning/samples/staffing-data.json /tmp/plan.html --brief /tmp/brief.md
node skills/workforce-planning/scripts/plan.mjs skills/workforce-planning/samples/staffing-data.json --json
node --test evals/tasks/workforce-planning/staffing-core.test.mjs
```
