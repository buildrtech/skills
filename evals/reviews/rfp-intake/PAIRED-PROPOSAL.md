# Bounded fresh-context paired proposal — coordinator scheduling required

Coordinator decision: Case A only approved, TWO fresh runs total, sequential
baseline/revision on the same default model. Do not launch until drawing/RFI
slots release and coordinator signals readiness. Case B is manual/deterministic
coverage only, not approved for a fresh run. Original proposal retained below.

Do not launch from this worker. Four trials total: two prompts, each against
baseline 9a62032 rfp-intake and revised 1.1.0. Use the same coordinator-selected
CLI/model/settings for both lanes, one attempt per cell, fresh isolated context,
no other skill content. No network, MCP, persistence, or review workers.
Keep verifier, expected results below, reports, and previous outputs hidden.
Record model/version/settings, exact skill hashes, transcript, reads, final
artifact, and any execution failure separately from behavior. Maximum 10 minutes
per trial; stop for coordinator assessment after these four, without retries.

## Case A — complete intake with explicit company criterion and two addenda

Mount only `paired-input/` under `/app/input/`. Prompt:

> As of March 3, 2027, review the Harbor Crossing invitation, both addenda,
> and our checklist in /app/input for tomorrow's precon meeting. Write a
> complete bid/no-bid review to /app/output/intake-review.md with cited dates,
> bid requirements, risks, and a recommendation. I will make the final call.

Hidden expected findings: recommend No-go because two qualifying projects are
required after A1 and company has one; do not withhold advice because Mike owns
the decision. Final bid March 15 at 11:00 via portal, superseding paper delivery
and 14:00; list deadline two hours later (13:00, labeled derived). Site visit
March 4 09:00; questions March 8 noon. No invented timezone offset, award/start,
budget, survey quantities, or drawing review. Base plus both alternates is bond
basis; Alternate B added, blank prices non-responsive; signed form, registration,
all addenda acknowledgment, all bond/insurance values and weekly payroll remain.
Live operations, abatement, and delay-only remedy are risks; owner builder's risk
is favorable. Distinguish missing wage-rate schedule/survey/drawings from reviewed
files. Criteria ratings and reasons must apply company criterion, with capacity
unknown. Score correctness and grounding independently of exact headings.

## Case B — missing package

No input files. Prompt:

> Can you run a bid/no-bid intake for the county pump station RFP? I haven't
> sent you the solicitation yet.

Expected: request solicitation once and stop intake pending it; no invented
package, generic scored review, remote API, or record creation. Asking optional
checklist information alongside the necessary package is acceptable.

## Interpretation

These are unfamiliar synthetic cases, not shipped smoke samples. Use the same
hidden checklist for both lanes and read transcripts for actual resource use.
Two cases cannot establish trigger-rate reliability or live MCP/PDF compatibility.
Case A exercises completeness, recommendation, source limits, and supersession;
Case B exercises missing-input behavior. Add no trials without scheduling.
