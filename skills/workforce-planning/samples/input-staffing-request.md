# Staffing meeting prep request

Fictional sample. Halvorsen Builders, its people, projects, clients, and
pursuits are invented.

> **From:** Linda Marsh, VP Operations
> **Sent:** Monday, October 5, 2026, 6:52 AM
> **Subject:** Staffing meeting Thursday
>
> Can you get the staffing picture ready for Thursday's ops meeting? Exports
> attached. Same questions as always: who's slammed, who's open, and where we
> have holes. Specifically:
>
> - We still don't have a super for Wash Park. GMP is December 15, and they
>   start digging in January.
> - Tony retires March 31 and Arvada isn't done until May.
> - Riverside interviews on the 20th. If we win it, who runs it? The owner
>   will ask about ICRA.
> - Union Station slipped again (see the 9/28 schedule update). I don't think
>   the sheet reflects that.
>
> Don't move anyone in the sheet. I want options I can put in front of the
> PXs, not decisions.

## Attached files

| File | What it is | Quirks to expect |
|---|---|---|
| [input-staffing-sheet.csv](input-staffing-sheet.csv) | The "Field + PM" tab of *Staffing 2026-27.xlsx*: one row per person, one column per month | Bare job codes mean 100%; `?` means pencilled for a pursuit; `St V` and `Union Stn` are the same jobs as `STV` and `UNI`; Frank's cells list jobs with no percentages; a "TBD Super" row at the bottom; free-text notes |
| [input-projects.csv](input-projects.csv) | Ops project list with phase dates and each job's planned team | Union Station's substantial completion moved from April to July 2027; planned teams use shorthand like `AS 100% (ICRA)` |
| [input-pursuits.csv](input-pursuits.csv) | CRM pipeline export | Win probability is a percentage string; Riverside's start moved from February to March; staffing needs use the same shorthand |
| [input-roster.csv](input-roster.csv) | HR roster | Certifications, sector experience, travel, the new hire's start date, Tony's retirement, and Megan's parental leave |

The agent normalized these into [staffing-data.json](staffing-data.json),
recording each ambiguity it resolved as an open question with its source row,
then ran the bundled script to produce the brief and the interactive plan.
