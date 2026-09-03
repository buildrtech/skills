# Object map

How common construction objects are named across major vendors, and the
fields an agent usually needs before it can read or change one safely.

Names below come from each vendor's public documentation and API references
as of September 2026. They are a translation aid, not a schema. Always
confirm the object and field names against the live tool list and the
record the server actually returns. Where a vendor has no native object for
a row, the cell says so rather than suggesting a substitute.

Vendor columns: PM = the vendor's project management product (Procore Project
Management; Autodesk Build inside Autodesk Construction Cloud, which some
listings now report under the Autodesk Forma name; JobTread). Bluebeam Revu
and OpenTakeoff are document and takeoff tools and are listed only where they
hold a comparable object.

| Object | Procore | Autodesk Construction Cloud (Build) | JobTread | Bluebeam Revu / OpenTakeoff | Fields agents usually need |
|---|---|---|---|---|---|
| Account / tenant | Company (company id scopes almost every call) | Account and Hub (hub id, then project id) | Organization | Bluebeam: Studio account; OpenTakeoff: none (local files) | Account or company id; which one the user means when several are visible |
| Project | Project (company-scoped; has project number, name, stage, active flag) | Project (inside a hub; has project id, name, type, status) | Job (job number, name, status, customer) | Bluebeam: Studio Project; OpenTakeoff: a plan set or sheet | Project id, display name, number, active or archived, and whether the connector user is a member |
| Company / vendor | Directory: Vendor (company-level and project-level records; project vendors reference company vendors) | Companies (account-level, with project membership) | Customer or Account (for clients); Vendor and subcontractor records under Accounts | Not a first-class object | Vendor id, legal name, trade, whether it is the project-level or company-level record |
| Contact / person | Directory: User or Contact (users can log in; contacts cannot) | Members and Users (account and project level) | Contact (linked to an Account) | Bluebeam: Studio session attendee | Person id, name, email, company id, role or permission template |
| RFI | RFI (number, subject, status Draft/Open/Closed, ball in court, assignee(s), RFI manager, due date, official response, distribution list, linked drawings and specs) | RFI (custom identifier, title, status such as draft/open/answered/closed, assigned to, reviewer, due date, official response, linked sheets) | No native RFI object; teams often track them as To-Dos or Documents. Confirm with the user before treating anything as an RFI. | Bluebeam: markups in a Studio Session can carry an RFI status via custom columns, not a separate object | RFI id and number, status, ball in court or assignee, due date, question, official response, links, attachments, closed date |
| Submittal | Submittal (number, revision, spec section, type, status, ball in court, workflow with approver steps, due dates, distribution) | Submittal item (spec section, revision, status, workflow steps, due dates, package) | No native submittal object; often tracked as Documents or To-Dos | Not a first-class object | Submittal id, number and revision, spec section, workflow step and who holds it, due dates, response status |
| Change order | Layered: Change Event, then Potential Change Order or Change Order Request, then Commitment Change Order (to a sub) or Prime Contract Change Order (to the owner); each has status and amount | Cost Management: Potential Change Order (PCO), Request for Quote (RFQ), Request for Change Order (RCO), Owner Change Order (OCO), Supplier Change Order (SCO) | Change Order on a Job (amount, status, line items, customer approval) | Not applicable | Change order id, layer (potential vs executed, prime vs commitment), amount, status, linked contract id, line items with cost codes, approval date; never collapse layers |
| Budget and cost codes | Budget (line items keyed by cost code and cost type; budget views), Cost Codes (work breakdown structure, company and project level) | Budget (budget codes built from segments; original, revised, committed, forecast columns) | Budget on a Job: Cost Items grouped by Cost Codes and Cost Groups; Estimate and Budget are separate views of the same items | Not applicable; OpenTakeoff produces quantities that feed an estimate | Cost code id and code string, description, original and revised budget, committed, forecast, and which budget view or column the number came from |
| Schedule | Schedule tasks (imported from scheduling tools or built in; task id, start, finish, percent complete, lookaheads) | Schedule (activities with start, finish, predecessors, percent complete) | Schedule: Tasks on a Job (start, end, dependencies, assignees) | Not applicable | Task id, name, start, finish, percent complete, predecessors, and whether the schedule is the working copy or a baseline |
| Daily log | Daily Log (date-keyed; sections for manpower, weather, notes, equipment, visitors, delays, etc.) | Daily Log (date-keyed; weather, labor, notes) | Daily Log on a Job (date, notes, photos, weather) | Not applicable | Date, project id, log section, entries with ids, whether the day is completed or locked |
| Drawings and documents | Drawings (drawing areas, sets, revisions, sheet number and title), Documents (folders and files), Specifications | Sheets (with versions) and Files/Folders in Docs | Documents and Folders on a Job (files, plans) | Bluebeam: PDFs, pages, markups, Studio Projects; OpenTakeoff: sheets, title block, scale, measurements | Sheet id and number, revision or version id, set name, file id, folder path, and whether the sheet is current |
| Issues, observations, punch | Observations, Punch List items, Inspections | Issues (types, status, assignee, location), Forms | To-Dos | Bluebeam: markups with status | Item id, type, status, assignee, location or sheet reference, due date |
| Photos | Photos (albums, project-level) | Photos (Build) | Photos on Jobs and Daily Logs | Not applicable | Photo id, date, uploader, linked record |

## Field notes that prevent common mistakes

- **Scope ids first.** Procore calls need a company id and usually a
  project id. Autodesk calls need a hub id and a project id, and the project
  id format differs between Data Management (prefixed) and ACC Build APIs
  (unprefixed). JobTread scopes most records to an Organization and a Job.
  Resolve and echo these before anything else.
- **Status vocabularies differ.** "Closed" in one system is "answered" or
  "resolved" in another. Read the allowed values from the record or the tool
  schema before proposing a status change, and quote the exact value.
- **Ball in court is not the same as assignee.** Procore RFIs and submittals
  track who currently owes a response separately from who was assigned. Do
  not report one as the other.
- **Change orders are layered.** A potential change order is not a
  commitment and a commitment change order is not a prime contract change
  order. Report the layer with every amount.
- **Budget numbers have views.** Ask which column the user means (original,
  revised, committed, projected, forecast) and report the column with the
  number.
- **Drawings have revisions.** Always report the revision or version id, and
  say whether it is the current one.
- **Daily logs are date-keyed.** Confirm the date and time zone of the
  project before adding or editing a day.
