# Building from the library and prior proposals

## The company library

The material the company keeps across proposals, in whatever form it has:
a project list spreadsheet, project sheets, resumes, the carrier's EMR letter,
OSHA 300A summaries, approach write-ups in Word. Read it as it is. Don't ask
the user to convert or restructure anything.

Each source needs the date it was last known true. Take it from the document
itself (the EMR letter's date, a resume's revision date, a "last updated"
line). File modification times don't count. When a document has no date, ask
whether it's current; if the user confirms it, date it today and cite the user
as well.

When the user has no library, offer to start one from what they supply for
this proposal, and save it in their working directory as plain Markdown files
the team can read and edit without you. Open each file with a
`Last verified: YYYY-MM-DD` line. `samples/company-library/` shows the shape:

| File | Holds |
|---|---|
| `projects.md` | Name, owner, sector, delivery method, final cost, completion, and owner reference with phone. |
| `people.md` | Name, title, years, credentials, and the projects each person worked on. |
| `safety.md` | EMR by year, TRIR by year, and the documents they came from. |
| `boilerplate.md` | Approach text the company stands behind: estimating, value analysis, procurement, safety on public sites. |

## Using it

- Pick projects that match what the RFP scores: sector, delivery method, size,
  and recency. Say why a weaker match is included ("listed for local
  experience only").
- People: list only people the user names for this pursuit. Take time
  commitments from the user, not the library.
- Quote approach text as written. Tailor it to the project only with facts
  from the RFP (budget, site, schedule), and cite both sources with `alsoFrom`.
- Don't stretch a library entry to fit a requirement it doesn't answer.

## Prior proposals

Prior proposals are useful leads and risky facts. They capture what was true
when they were written, often with sales gloss.

- Lifted text cites the prior proposal and page, and stays unconfirmed. The PDF
  prints "confirm still true" beside it in draft, and the check flags it.
- Record every value that also appears in the library (EMR, project values,
  completion dates) as a `fact` from both sources. The check lists the
  conflicts and flags any item that uses the older value.
- Prefer the library value. A prior proposal's GMP is not a final cost, and
  last year's EMR is not this year's.
- When the user confirms a claim, set `confirmed: true`, and suggest adding it
  to the library so the next proposal starts from it.

## When nothing answers a requirement

Leave it unanswered rather than writing around it. The check will block
submission and name the requirement and its points. Add a question saying
exactly what's needed and who might have it.
