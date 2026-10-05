# Normalizing staffing sources

Staffing data arrives as the files operations already keeps. Read every file
before writing JSON, and record each judgment call as an open question with the
file and row it came from.

## The staffing sheet

Usually one row per person and one column per month, often with colour coding
and comments that do not survive a CSV export. Ask for the original workbook
if colour carries meaning ("red means tentative").

- **Bare job code** means 100% unless the sheet's legend says otherwise.
- **Split cells** like `LKW 50 / ARV 50` or `LKW/ARV` are allocations. When
  the split has no numbers, use a note that states it ("GS split 4 ways");
  otherwise ask.
- **Pencilled work** (`RIV?`, italics, "pending", "if we win") is a pursuit
  assignment, never committed work.
- **Nicknames** (`St V`, `Union Stn`) map to one job code. List the mappings
  you applied.
- **Placeholder rows** ("TBD Super", "need super") are unfilled seats, not
  people. Do not create a person for them.
- **Cells that look like notes** ("PTO 2 wks", "covering nights") are either
  leave or allocation. Treat them consistently and ask.
- **Blank cells** mean unassigned only if the sheet uses blanks that way.

## The project list

Use the *current* phase dates. When the list shows a moved substantial
completion and the sheet still rolls the team off on the old date, keep the
sheet's assignments as they are and let the plan show the unfilled seats. Ask
who extends. Never extend people automatically.

Planned team columns become seats. Keep phase changes (100% in construction,
50% in closeout) as separate seats. Carry certification requirements (ICRA,
OSHA 30, owner-specific badging) onto the seat.

## The pursuit export

Probability comes from the CRM. Do not adjust it. Use the latest start date and
note any change. The staffing need becomes seats; pencilled names on the sheet
become pursuit assignments.

## The roster

Titles map to roles. Certifications and sector experience come from here, not
from the staffing sheet. Leave, start dates, and retirements become `leave`,
`start`, and `end`. If the sheet has someone working while the roster has them
on leave, keep both; the plan shows the conflict.

## Never invent

Do not invent people, percentages, dates, certifications, thresholds, or
probabilities. Missing values stay missing: ask, or leave the item out and say
so. A plan built on guessed allocations is worse than no plan.
