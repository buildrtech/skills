# Grounding rules

These rules decide what becomes a candidate, how it is described, and how
the coverage ledger proves the set was actually read. Read this before
recording the first candidate.

## What becomes a candidate

- Only drawing-backed work becomes a candidate. Every candidate cites a
  sheet number in the sheet inventory, the place on the sheet (keyed note,
  schedule row, detail, partition type, legend entry), and a short quote of
  the text that supports it.
- Every concrete CSI-section-level item found on a reviewed sheet becomes
  one of: an `include` candidate, a `review` candidate, or an `exclude`
  candidate with a reason. Items that fall into none of these were not
  reviewed. Concrete means a named material, product, assembly, schedule
  row, keyed note, manufacturer or model, or a provide, install, remove,
  relocate, or reconnect activity.
- Ignore text that does not describe work: title blocks, revision clouds
  without content, standards-only references, administrative notes,
  responsibility-ambiguous tag fragments. Say so in the ledger when a probe
  surfaced only text like this.
- Cross-discipline references ("see P-101", "coordinate with", "protect",
  "refer to") that do not show installed scope on the current sheet are
  `reference_only` or `review`, never `include`, until the referenced sheet
  confirms the work.
- Never create scope from sheet titles, file names, or general construction
  knowledge. If a tenant improvement usually needs sprinkler head relocation
  and the set never mentions it, that is an RFI, not a candidate.
- If the set is large but the candidate list is short, extraction was
  over-compressed. Redo the pass sheet by sheet before writing the ledger.

## Support levels

| `support_level` | Use when |
|---|---|
| `direct` | A note, detail, or plan callout on the cited sheet describes the work itself. |
| `schedule` | A schedule row (door, finish, fixture, equipment, partition type) defines the item. |
| `spec_requirement` | A specification section provided by the user requires the work and the drawings show where it applies. |
| `reference_only` | The cited sheet points to another sheet, discipline, or document for the work and does not show it. |
| `by_others` | The drawings assign the work to the owner, tenant, a base-building vendor, or a separate contract. |
| `inferred` | The work is not stated but a stated item cannot be built without it. Use rarely, always with `decision: review`, and say what stated item drives the inference. |

## Decisions

| `decision` | Meaning |
|---|---|
| `include` | Goes on the scope list under its division; the primary cited sheet must be `reviewed` or `reviewed_ocr`. |
| `review` | Unresolved evidence: ambiguous text, OCR uncertainty, a referenced sheet that is missing or unreadable, or an inference. Listed separately under its division with the reason. |
| `exclude` | Recorded so the ledger is complete, but not scope for the user: by others, NIC, reference only, or text that does not describe work. |

## Describing a candidate

- The `candidate` field names only the work item: product, assembly, or
  activity, with its location when the drawings give one. Sheet numbers,
  division names, and cost code context go in `location`, `reason`, and
  `notes`, not in the description.
- Do not group distinct products, locations, assemblies, or
  responsibilities just because they share a trade, division, sheet, or
  cost code. Three partition types are three candidates. Two light fixture
  types are two candidates. Carpet and rubber base are two candidates.
- Do not split one item just because it appears on two sheets. Cite the
  primary sheet in `sheet_number` and list the others in `related_sheets`.
- Use cautious language when the text is sparse, OCR-derived, or ambiguous:
  "approximately 100 CFM (OCR, partly illegible)" rather than "100 CFM".
- Quantities printed on the drawings may appear inside the quote as
  evidence. They are not a takeoff and must not be restated as counts in the
  candidate description or presented as quantities to price.
- Assumptions, exclusions, and RFIs are separate lists. An assumption is a
  reading the user should confirm. An exclusion is work the drawings put on
  someone else or outside the contract. An RFI is a question the documents
  cannot answer. None of them is a candidate.

## Coverage ledger discipline

The ledger exists so a reader can tell what was reviewed, not just what was
found. Build it from the sheets and probes first, then map candidates onto
it; never generate it backward from the candidate list.

- Every sheet in the inventory has a status: `reviewed`, `reviewed_ocr`,
  `unreadable`, or `not_reviewed`. A sheet that was skipped is
  `not_reviewed` with the reason; it is never silently omitted.
- Keep work dependent on an unreadable or unreviewed sheet under review.
  A readable primary sheet may independently establish an item even when a
  related sheet is unavailable; explain that distinction in the reason.
- Every probe that was run has a ledger entry, including probes with no
  hits. For each hit, record what concrete items surfaced and whether each
  became a candidate, was merged into another candidate, was excluded with a
  reason, or needs follow-up.
- Notable sources that are not probes (a schedule, a general-note list, a
  blanket requirement) get their own `source` entries when their treatment
  would not be obvious from the candidates.
- Before writing the scope list, compare the ledger against the sheet
  inventory and the probe list. Any reviewed sheet or run probe without an
  entry means the review is incomplete.
- Do not mark a whole division as "no scope found" unless every concrete
  item surfaced for that division has its own exclusion or reference reason.

## Division and cost code checks

- Assign the division from what the drawings show, using
  `references/csi-divisions.md`. Record judgment calls in `reason`.
- When mapping to a user-supplied CSI-based cost code list, the first two
  digits of the cost code must match the candidate's division. Wood blocking
  that backs a Division 09 partition is still Division 06. When they differ,
  fix one or the other and record why.
- Mapping to a cost code list is an offer after the scope list is
  delivered, not part of the default output. Never invent cost codes.
