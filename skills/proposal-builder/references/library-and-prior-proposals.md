# Building from the library and prior proposals

## The company library

A folder the company keeps across proposals. Any format works as long as each
file says when it was last verified. A good starting set:

| File | Holds |
|---|---|
| `projects.json` | Name, owner, sector, delivery method, final cost, completion, owner reference with phone, and the people who worked on it. |
| `people.json` | Name, title, years, credentials, and project ids. |
| `safety.json` | EMR by year, TRIR by year. |
| `boilerplate.md` | Approach text the company stands behind: estimating, value analysis, procurement, safety on public sites. |

When the user has no library, offer to start one from what they supply for
this proposal, dated today, and save it in their working directory.

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
