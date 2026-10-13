# Reading solicitations

How to turn a solicitation package into `intake-data.json` that someone can
check page by page.

## Inventory

- Extract each PDF's text with `pdftotext -layout`, or render the pages. Record
  the page count, and use the physical page number for citations, not the
  printed one when they differ.
- Render or OCR scanned pages. If a page stays unreadable, say so in the
  document's `note`.
- List everything the solicitation references (Project Manual, drawings,
  attachments, reports). If it wasn't supplied, mark it `supplied: false`. A
  sheet count is not evidence of design completeness.

## Addenda first

Read every addendum before extracting anything else. For each item:

- Update the field it changes (date, bond, insurance, form, scope) to the
  current value, and keep the superseded value in `was`.
- Add a `changes` row with both citations.
- Separate an addendum already issued from a planned future issue date.
- When an addendum and the base document conflict and the addendum doesn't
  say which governs, raise it as an owner question.

## What to extract

| Area | Look for |
|---|---|
| Dates | Issue, pre-bid meeting or site visit (mandatory?), questions deadline, final addendum, bid due, opening, award, notice to proceed, phase windows, substantial and final completion. Keep stated time zones. |
| Submission | Where and how (sealed, electronic portal, email), copies, late-bid rule. |
| Forms | Bid form, alternates and unit prices, bid security, affidavits, responsibility verifications, subcontractor lists and when they're due, addenda acknowledgment. |
| Bonds | Bid security percent; performance and payment percent; when they're due; surety requirements. |
| Insurance | Every limit and unusual coverage (builder's risk, pollution, professional, railroad). |
| Licensing and prequalification | State, city, and trade licenses, and when each is needed; prequalification deadlines; participation goals. |
| Wages and labor | Prevailing wage or Davis-Bacon, certified payroll, project labor agreements, apprenticeship, local hire. |
| Contract and risk | Contract form and modifications, liquidated damages, delay, concealed conditions, indemnity, retainage, payment terms, hazardous materials, geotechnical reliance. |
| Scope and site | Building type, size, occupied or phased work, alternates, self-perform opportunity. |

Preserve "shall" versus "may", and stated exceptions. A requirement is
`mandatory` only when the document says a miss means rejection or
disqualification.

## Scoring criteria

- Score from the documents and the company profile only. "We've worked for this
  owner" needs a `pastClients` entry or the user saying so.
- Use `null` rather than a guess. The script reports how much of the weight is
  unknown, and too much makes the recommendation conditional.
- A problem so serious it rules the job out (a license that can't be obtained
  in time, a term on the company's list) belongs in a gate, not a low score.

## Risks and questions

- A risk names the clause, its practical consequence for this company, and any
  offsetting favorable term.
- Owner questions are ones the owner can answer in writing before the questions
  deadline, each tied to the clause that prompts it.
- Team questions cover what only the company knows: who attends the pre-bid
  meeting, who staffs the job, what the surety says.
