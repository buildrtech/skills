# Plan and log: close out overdue RFIs on Ridgeview

SYNTHETIC ILLUSTRATION ONLY. All records, tool names, user replies, and
outcomes below are authored examples, not captured execution. No remote
system was read or changed. This is not an independently replayable fixture.
The response ids and exact text below are also authored examples. A real
proposal must obtain them from record detail before requesting approval.

## 1. Inventory

Connected server: `pm-connector` (community wrapper over a project
management REST API, running as the configured credential; the credential
itself is not shown here).

| Object | Read tools | Write tools |
|---|---|---|
| Companies | `list_companies` | none |
| Projects | `list_projects`, `get_project` | none |
| RFIs | `list_rfis`, `get_rfi` | `update_rfi` |
| Submittals | `list_submittals`, `get_submittal` | none |
| Contacts | `list_users` | none |

Not available: submittal or change order writes, drawing tools, daily
logs. Only RFIs can be changed through this connection.

## 2. Scope

`list_companies` returned two companies: Northwind Builders (id 1101) and
Northwind Service Division (id 1102). `list_projects` on 1101 returned one
match for "Ridgeview": **Ridgeview Elementary Classroom Addition**
(project id 88214, project number 26-014). Company 1102 has no project
containing "Ridgeview".

One match across the visible companies resolves scope; report its name and
ids and proceed with reads. No additional yes is needed for this read.

## 3. Read-only pass

`list_rfis` with filters `project_id=88214`, `status=open`, paged with
`per_page=100`; the server reported 2 pages, 137 open RFIs total, and both
pages were read. Overdue was computed as `due_date` earlier than
2026-09-03 (today, project time zone America/Denver, taken from
`get_project`). That yields four overdue RFIs, not three:

| RFI | Id | Subject | Due | Ball in court | Assignee | Engineer reply in thread? |
|---|---|---|---|---|---|---|
| 031 | 550031 | Footing depth at Grid 7 tie-in | 2026-08-21 | Holloway Peterson (engineer) | Dana Whitfield | Yes, 2026-08-27 |
| 034 | 550034 | Storm line conflict at bus loop | 2026-08-25 | Northwind Builders | Marcus Lee | Yes, 2026-08-28 |
| 036 | 550036 | Casework finish, learning commons | 2026-08-28 | Northwind Builders | Dana Whitfield | Yes, 2026-08-29 |
| 038 | 550038 | Roof drain overflow sizing | 2026-08-30 | Holloway Peterson (engineer) | Marcus Lee | No reply in thread |

Each of the four was read individually with `get_rfi`. Findings:

- RFI 038 has no engineer reply, so it does not match "the answers are
  already in the threads". It is excluded from the close-out below and
  listed for the user.
- RFIs 031 and 036 are assigned to Dana Whitfield (user id 7021), whom the
  user says has left. `list_users` shows her account still active in the
  directory. This run does not reassign; that is a separate change.
- `get_rfi` shows the status vocabulary as `draft`, `open`, `closed`. The
  `official_response` field is empty on all three candidates; the
  engineer's replies are in the `responses` array.

## 4. Dry run

Server: `pm-connector`
Account: Northwind Builders (1101)
Project: Ridgeview Elementary Classroom Addition (88214)

| # | Record | Id | Field | Current value | New value | Tool (example name) |
|---|---|---|---|---|---|---|
| 1 | RFI 031 | 550031 | status | open | closed | `update_rfi` |
| 2 | RFI 031 | 550031 | official_response | (empty) | “Use the footing depth shown in detail 3/S-102.” (response 88031, Holloway Peterson, 2026-08-27) | `update_rfi` |
| 3 | RFI 034 | 550034 | status | open | closed | `update_rfi` |
| 4 | RFI 034 | 550034 | official_response | (empty) | “Maintain the storm line elevation shown in the revised profile.” (response 88034, Holloway Peterson, 2026-08-28) | `update_rfi` |
| 5 | RFI 036 | 550036 | status | open | closed | `update_rfi` |
| 6 | RFI 036 | 550036 | official_response | (empty) | “Use finish PL-2 for the learning commons casework.” (response 88036, Holloway Peterson, 2026-08-29) | `update_rfi` |

Side effects documented by the server's API notes: closing an RFI sends a
notification to the distribution list and sets `closed_date` to the
current time. Dana Whitfield is on the distribution list for 031 and 036.

Not changing: RFI 038 (no engineer reply); assignee on 031 and 036 (user
asked to note it, not change it); anything in company 1102.

## 5. Confirmation

"Apply these 6 changes (three RFIs closed, three official responses set) to
Ridgeview Elementary Classroom Addition (88214)? Reply yes to proceed."

Hypothetical user reply: yes (illustration only, not authorization).

## 6. Write log

| # | Tool | Id | Fields sent | Result |
|---|---|---|---|---|
| 1 | `update_rfi` | 550031 | status, official_response | 200 OK |
| 2 | `update_rfi` | 550034 | status, official_response | 200 OK |
| 3 | `update_rfi` | 550036 | status, official_response | 200 OK |

No rate-limit responses. Status and official response were sent together
in one call per RFI, in dry-run order.

## 7. Verification (re-read)

`get_rfi` on each changed id after writing:

| RFI | Id | status | official_response matches thread reply | closed_date (set by server) | Result |
|---|---|---|---|---|---|
| 031 | 550031 | closed | yes | 2026-09-03T15:42:10-06:00 | verified |
| 034 | 550034 | closed | yes | 2026-09-03T15:42:14-06:00 | verified |
| 036 | 550036 | closed | yes | 2026-09-03T15:42:19-06:00 | verified |

Unverified: none. Mismatched: none.

## 8. Report

**Changed:** RFIs 031 (550031), 034 (550034), and 036 (550036) on Ridgeview
Elementary Classroom Addition (88214) are now `closed`, each with the
engineer's thread reply set as the official response. All three were
re-read and match. The server set `closed_date` on each; documented behavior would notify
each distribution list, which for 031 and 036 includes Dana Whitfield.
Delivery is not verified by these record reads.

**Not changed:** RFI 038 (550038, roof drain overflow sizing) is also
overdue but has no engineer reply in its thread, so it was left open with
the ball in court at Holloway Peterson. You asked for three; the system had
four overdue.

**Noted:** RFIs 031 and 036 were assigned to Dana Whitfield (7021), whose
directory account is still active. Reassigning them and removing her from
distribution lists would be a separate change; say who should take them and
this skill will dry-run it.

**Sources:** every id, status, date, and name above is synthetic example
data. There were no live `pm-connector` responses. Closing an RFI records that the
question was answered; it is not a design approval or a cost decision.
