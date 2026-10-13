# Staffing data contract

`scripts/plan.mjs` reads one JSON file. Fractions are of one full-time person
(1 = 100%) and must be whole percents (0.25, not 0.333). Months are `YYYY-MM`
and ranges are inclusive. See `samples/staffing-data.json` for a complete
example.

## Top level

| Field | Required | Meaning |
|---|---|---|
| `company.name` | yes | Shown in the plan header. |
| `asOf` | yes | `YYYY-MM-DD` date of the source exports. |
| `horizon` | yes | `{ "start": "2026-10", "months": 12 }`, 1 to 36 months. |
| `thresholds` | no | Overload limit by role as a fraction, plus `default`. Missing means 1.0. Use the company's own limits when given; common practice is 1.2 for PMs and 1.0 for superintendents. |
| `roleFits` | no | Which roles can fill a seat: `{ "Superintendent": { "same": [], "stepUp": ["Assistant Superintendent"] } }`. Step-ups rank below direct matches. Use the company's career ladder; do not invent one. |
| `people` | yes | Salaried project staff. |
| `projects` | yes | Awarded jobs. |
| `pursuits` | yes (may be empty) | Jobs being chased. |
| `assignments` | yes | Who is on what, from the staffing sheet. |
| `openQuestions` | no | Ambiguities resolved during normalization, each with `text` and `source`. |

## People

`id`, `name`, `role` are required. Optional: `office`, `travel` (boolean),
`sectors` and `certs` (lists of text from the roster), `start` (first month
for a new hire), `end` (last month before retirement or departure), and
`leave`: `[{ "from", "to", "fraction", "note" }]`. Leave reduces capacity for
those months; it is not an assignment.

## Projects and pursuits

Both need a unique `id` (shared namespace), `name`, `sector`, and `seats`.
A seat is one role the job needs: `{ "role", "from", "to", "fraction",
"requires": { "certs": ["ICRA"] } }`. Two assistant superintendents can be one
seat at `2` or two seats at `1`. Take seats from the project list's planned
team, the pursuit's staffing need, or the company's staffing standard. When
none is supplied, ask; do not derive seats from who happens to be assigned.

Pursuits also need `probability` (0 to 1) and `start`. Optional on both:
`number`, `phase`, `stage`, `value`, `client`, `substantialCompletion`,
`closeoutEnd`, `note`, `source`.

## Assignments

`{ "person", "job", "role", "from", "to", "fraction", "source" }`. `role` is the
seat the person fills on that job, usually their title. `source` names the
file and row. Assignments to a pursuit are pencilled: they count only when the
scenario marks the pursuit won. Oversight with no seat (a general
superintendent split across jobs) is still an assignment; it uses capacity but
fills no seat.

## Scenario (optional, `--scenario`)

`{ "pursuits": { "RIV": "won" }, "moves": [...] }`. Pursuit modes are
`weighted` (default), `won`, or `lost`. A move is `{ "person", "job", "role",
"from", "to", "pct", "note" }` where `pct` is a whole percent from -100 to 100
added to that person's allocation. The HTML plan's **Export scenario** file is
also accepted.

## What the script computes

- **Load**: per person and month, the sum of committed allocations (projects,
  won pursuits, and moves) against capacity after leave, start, and end dates.
- **Overloads**: any rolling three-month window whose total load, over the
  months the person is available, exceeds capacity times the role threshold.
- **Conflicts**: committed work in a month the person is on leave, not yet
  started, or gone.
- **Unfilled seats**: seat requirement minus the allocation of people in that
  role on that job, by month, merged into ranges.
- **Certification gaps**: a person filling a seat whose `requires.certs` they
  do not hold.
- **Candidates**: people whose role fits, ranked by step-up last, missing
  certifications, months they can fully cover, sector experience, other
  pencilled work, and free months. Each comes with a suggested what-if move.
- **Roll-offs**: committed load dropping by 25 points or more month to month.
- **Role balance**: supply minus committed load, open seats, and pursuit seats
  times win probability. Two or more months at least 0.5 FTE short is a
  hiring signal.
