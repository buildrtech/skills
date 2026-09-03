# Comparison template

The Markdown `scripts/level_bids.py` prints, section by section, and how to
read each one. Read this at step 6 of the workflow before presenting the
result. `samples/output-leveled-comparison.md` is a full example.

The script prints the comparison; the agent does not retype it. When the
user needs a change, change the extraction or the decisions file and rerun.

## Layout

Sections marked (if any) are skipped when they would be empty.

```
# Leveled bid comparison: <--title, or the extracted trade_scope>

**Lowest complete leveled total:** <bidder> at <amount>.
**<incomplete bidder>:** <amount> before N unresolved gaps (<row labels>).
**<bidder with no total>:** no stated total, so no leveled total.

Leveled total = base bid + plugs + adjustments. Alternates, unit prices, and
priced qualifications are listed but not applied. ...

## Summary
| Bidder | Base bid | Plugs | Adjustments | Leveled total | Unresolved gaps | Documents |

## Base scope matrix
| Scope | <bidder 1> | <bidder 2> | ... |

## Scope gaps and plugs
| Scope | Bidder | Bid says | Plug | Plug source | Evidence |
N gaps on base scope, M unresolved. ...

## Adjustments                              (if any)
| Bidder | Adjustment | Amount | Source |

## Alternates
| Alternate | Kind | Solicited | <bidder 1> | <bidder 2> | ... |

## Unit prices                              (if any)
| Bidder | Unit price line | Unit | Unit price | Quantity | Evidence |

## Priced qualifications (not applied)      (if any)
| Bidder | Priced qualification | Amount | In bid total? | Evidence |

## Outside package scope                    (if any)
## Supplier and installer splits            (if any)
## Review rows                              (if any)
| Scope | <bidder 1> | <bidder 2> | ... |

## Review items
- <bidder>: <item> (<evidence ref>)
- Leveling check: <flag raised by the script>

## Qualifications
**<bidder>**
- <qualification> (<evidence ref>)

## Evidence
| Bidder | Ref | Source file | Location | Quote |

## Basis
- (four fixed lines stating what the script did and did not do)
```

Bidders appear in the order their extraction files were given on the
command line. Rows appear in the order they were first encountered across
those files, so the first extraction's row order sets the matrix order.

## Reading each section

**Headline.** The first bold line names the lowest leveled total among
bidders whose totals are complete: a stated base bid and no unresolved base
gaps. If no bidder is complete it says so. One line follows for each
incomplete bidder, listing the gaps holding it up. Lead the presentation
with these lines, in the same words. A bidder that is lowest but
incomplete is not "low"; say what would have to be resolved first.

**Summary.** One row per bidder. `Plugs` and `Adjustments` show `none`
when nothing was recorded. `Leveled total` carries `(incomplete)` when any
base gap has no plug. `Documents` lists the source files, which is how the
reader knows an email quote from a signed proposal.

**Base scope matrix.** One row per `base` scope key, one column per bidder.
Cell values:

| Cell | Meaning |
|---|---|
| `Included` | The bid says it is in; no itemized amount. |
| `Included ($22,800)` | In, and the bid itemizes that amount. Itemized amounts are informational; they are never summed across bidders. |
| `Excluded; plug $41,200` | The bid excludes it and the decisions file carries a plug. |
| `Excluded` / `Omitted (silent)` / `Unknown` | A gap with no plug. This bidder's total is incomplete. |
| `Not addressed` | The extraction never mentioned the row. A flag under Review items asks for it to be re-read. |

**Scope gaps and plugs.** The gap list, one row per bidder per gap, in
matrix order. `Bid says` repeats the status and the extraction's `note`,
which should be the bid's own words. `Plug` is the amount or
`none: unresolved`. `Plug source` is copied from the decisions file; if it
does not say who decided and from what, the decisions file needs fixing.
`Evidence` is the ref to look up in the Evidence table. The closing line
counts gaps and unresolved gaps. This table is the plug summary the user
asked for; present it in plain language (bidder, scope, amount, source) and
call out every `none: unresolved` as a question for that bidder.

**Adjustments.** Signed amounts applied to a bidder's total for a stated
reason other than a base gap, most often removing outside-scope work or
putting bonds and taxes on a common basis. Each names its source.

**Alternates.** One row per alternate key, with each bidder's price or
`not offered`. `Solicited` distinguishes alternates the bid documents asked
for from ones a bidder volunteered (`no (bidder-proposed)`). A price of
`priced: not stated` means the bidder offered the alternate without a
number. Nothing here is in a leveled total. When presenting, point out
solicited alternates where a bidder is missing and bidder-proposed
alternates that would change the comparison if accepted.

**Unit prices.** Listed for side-by-side comparison. `Quantity` is filled
only when the bid states one. Never multiply these into a total.

**Priced qualifications (not applied).** Bonds, taxes, escalation,
delivery, overtime, permits. `In bid total?` is `yes` only when the bid
says the amount is already inside the base bid. The closing sentence is the
rule: these stay here until the estimator decides the common basis. When
presenting, name the bids that are on different bases (one includes bond,
one excludes it) so the estimator can decide.

**Outside package scope, Supplier and installer splits, Review rows.**
Matrices for the non-base row classes, each printed only when it has rows.
Amounts in Outside package scope are inside that bidder's total; the note
under the table says to remove them with a sourced adjustment. Rows in the
other two sections are visible but do not count.

**Review items.** Two kinds of bullets. Bidder-prefixed items come from the
extractions: things a person must confirm with the bidder or the documents.
`Leveling check` items are flags the script raised while building the
model (itemized lines that do not sum to the total, rows not addressed,
plugs ignored, duplicate bidders, mismatched trade scopes). Every leveling
check should be either fixed in the inputs or explained in the
presentation. This list, with the unresolved gaps, is the source for the
questions to send each bidder.

**Qualifications.** Non-priced conditions per bidder, with evidence refs.
Read them for anything that changes the comparison without a dollar
figure: an old drawing date, a mobilization assumption, a validity window.

**Evidence.** Every quote the extractions cite, keyed by ref. This is how a
reader checks any cell in the matrix against the bid. Keep it in the
deliverable; do not trim it for length.

**Basis.** Four fixed statements: bidders and amounts come only from the
extractions; base bids stay at the submission level; plugs are estimator
decisions; the output is arithmetic, not an award recommendation and not a
scope review. Repeat the last one when presenting.

## Presenting the result

The comparison is the deliverable, but the user usually wants it read to
them first. A good presentation, in order:

1. The headline lines, verbatim.
2. What it took to get there: the plugs and adjustments in plain language
   with their sources, and which gaps are still unresolved.
3. What could move the ranking: unresolved gaps, priced qualifications on
   different bases, bidder-proposed alternates, and leveling check flags.
4. The questions to send each bidder, grouped by bidder.
5. The full comparison, or the XLSX workbook if the user asked for one.

Do not add an award recommendation. If asked for one, give it with its
assumptions and the open items listed beside it.
