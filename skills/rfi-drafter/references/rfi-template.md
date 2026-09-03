# RFI template and log row

Use this layout for every RFI unless the project already has a form, in
which case map these fields onto that form and keep the field order the
project expects. Leave placeholders visible (`RFI-___`, `[date]`) rather
than filling them with guesses.

## RFI body

```
# RFI-<number>: <subject>

| | |
|---|---|
| Project | <project name and number, as given by the user> |
| From | <GC firm, person, role> |
| To | <architect or engineer of record, person if known> |
| Cc | <other design disciplines, owner's rep, affected subcontractor> |
| Date issued | <date> |
| Response needed by | <date>, because <the activity waiting on the answer> |
| Location | <level, grid, room, or detail> |
| Discipline | <architectural, structural, mechanical, electrical, plumbing, civil, fire protection> |

## Question

<One question. Lead with the specific ask, then the minimum context needed
to answer it. Two to five sentences.>

## References

- <Sheet>, <detail or note>: <what it shows or says, quoting short excerpts where wording matters>
- <Spec section number and title>, paragraph <x.y.z>: <what it requires>
- Referenced but not reviewed: <anything the provided documents point to that was not supplied>

## Suggested resolution

<Only when the provided documents support a specific answer. Phrase as a
proposal for the design team to confirm. Otherwise: "None proposed; request
direction." followed by what information would allow a proposal.>

## Impact

- Cost: <"Potential" plus the reason, or the user's quantified figure attributed to them>
- Schedule: <"Potential" plus the activity affected and the date it is waiting on, or the user's figure>
- <Note on contract notice if the conflict could become a change or delay claim: check with PM or counsel; not legal advice.>

## Attachments

- <Marked-up sheet excerpt, photo, sketch, or spec page the user should attach>
```

### Field notes

- **Subject.** Location first, then the issue. "Grid C/4, Level 2: duct
  riser DR-2 conflicts with W24x76 beam" reads faster in a log than "Duct
  conflict".
- **To.** Address the party contractually responsible for answering, usually
  the architect of record, even when the engineer of record will write the
  answer. Put the engineer on cc.
- **Response needed by.** Downstream activity date minus the time the team
  needs to act on the answer, never earlier than today. When the project
  turnaround is known and the needed-by date is shorter, say so in the
  Impact section so the design team sees why.
- **Discipline.** The discipline whose drawing or spec has to change, or
  "multiple" when the answer requires coordination between disciplines.

## RFI log row

One row per RFI. Column order matches most GC log templates; keep it if the
project does not have its own.

| Column | Content |
|---|---|
| Number | Project convention, for example `RFI-047`; `RFI-___` when unknown |
| Subject | Same as the RFI subject line |
| Date issued | Date the RFI is sent, as given by the user |
| To | Firm the RFI is addressed to |
| From | GC firm and person |
| Response needed by | Date from the RFI header |
| Ball in court | The party who owes the next action; the "To" firm on issue |
| Status | Open on issue; then Answered, Closed, Void, or Reissued |
| Cost impact | Potential, None (user confirmed), or a figure attributed to the user |
| Schedule impact | Potential, None (user confirmed), or a figure attributed to the user |
| Related sheets/specs | Sheet and spec numbers cited in the RFI |

Markdown row for pasting into a log:

```
| RFI-<number> | <subject> | <date issued> | <to> | <from> | <response needed by> | <ball in court> | Open | <cost impact> | <schedule impact> | <sheets/specs> |
```
