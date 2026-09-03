# Evidence schema

Every bid is reduced to one record in this shape before any Buildr write.
One record per bidder pricing version: several files that together make up
one bid share a record; a revised bid gets a new record with `revision_of`
set to the earlier record's `key`.

Use every top-level key. Use `null` for an unavailable scalar and `[]` for an
unavailable list; never omit a key and never fill one with a guess.

```json
{
  "key": "cedar-ridge-r0",
  "revision_of": null,
  "bidder_name": "Cedar Ridge Drywall, Inc.",
  "bidder_name_source": "proposal letterhead, p. 1",
  "source_files": ["cedar-ridge-drywall-proposal.pdf"],
  "document_role": "bid_proposal",
  "trade_scope": "Drywall and metal framing",
  "package_reference": "Drywall & Framing - 09 20 00",
  "total_bid_amount_in_cents": 41250000,
  "total_source": "p. 1, Base Bid",
  "scopes_of_work": [
    {
      "description": "Metal stud framing - interior partitions",
      "amount_in_cents": 16800000,
      "quantity": null,
      "uom": null,
      "source": "p. 2, Schedule of Values line 1"
    }
  ],
  "excluded_scopes": [
    { "description": "Firestopping at rated penetrations", "wording": "by others", "source": "p. 3, Exclusions" }
  ],
  "alternate_lines": [
    {
      "label": "Alternate 1 - Level 5 finish at lobby",
      "kind": "add",
      "solicited": true,
      "amount_in_cents": 840000,
      "source": "p. 2, Alternates"
    }
  ],
  "unit_price_lines": [],
  "priced_qualifications": [
    { "description": "Additional mobilizations beyond two", "amount_in_cents": 250000, "uom": "ea", "source": "p. 3, Qualifications" }
  ],
  "review_items": [],
  "qualifications": ["Pricing valid 30 days from proposal date (p. 3)"],
  "evidence": [
    { "claim": "Base bid $412,500", "source": "p. 1" }
  ]
}
```

## Field rules

- `bidder_name` is the company name as the proposal states it, with the
  page it came from. It is evidence and a display label only. Executable
  mappings in the leveling model are keyed by Buildr `submission_id` after
  submissions are created and reloaded.
- `document_role` is one of `bid_proposal`, `quote`, `scope_letter`,
  `bid_form`, `clarification`, `revision`. Shared solicitation material
  (specs, addenda, the GC's bid form) is not bid evidence; it is a package
  document and does not get a record.
- Every amount is integer cents and has a `source` naming the file and page
  (or sheet and cell for spreadsheets). An amount without a source does not
  go in the record.
- `scopes_of_work` holds itemized lines when the bid provides them. When a
  bid is lump-sum only, leave `scopes_of_work` with the scope descriptions
  the bid names and `amount_in_cents: null` on each; the total stays in
  `total_bid_amount_in_cents`. Never allocate a lump sum across scopes.
- `excluded_scopes` records the bidder's own wording ("by others", "NIC",
  "not included", "excluded") so the leveling model can classify it.
- `alternate_lines` holds only true options that change what the buyer may
  purchase: solicited alternates from the bid form, bidder-proposed adds,
  deducts, or substitutions, and bond options. `kind` is `add`, `deduct`,
  or `replace`; `solicited` is true only when the option matches one the GC
  asked for.
- `priced_qualifications` holds delivery, escalation, overtime, weather,
  extra mobilizations, restocking, taxes, permits, and any priced note that
  is not an option. These never become alternates.
- `unit_price_lines` holds unit rates the bid offers for quantity
  adjustments.
- `review_items` holds anything the extractor could not classify with
  confidence, with the wording and page. Uncertainty is recorded, not
  resolved by guessing.
- `qualifications` holds unpriced conditions (validity period, schedule
  assumptions, payment terms) as short quotes with pages.

## Combining documents

When two proposals from the same bidder cover distinct, non-overlapping
portions of the package, use their combined total and cite both. Do not sum a
proposal with its own revision, a bid form with the proposal it restates, or
an alternate with the base bid.

## Merging records

If the agent has a filesystem, keep one JSON file per record and a merged
`extractions.json` listing them all, and fix the file rather than re-reading
the PDF from memory. If not, keep the records in the conversation and quote
them verbatim when building the leveling model.
