# Evaluator only — keep out of fresh agent context

Coordinator accepted two runs total: baseline and revised skill, same model,
one unfamiliar combined prompt each. Completed results are in the review report. Copy only
paired-prompt.md plus the selected skill package into each context. Baseline is
/tmp/skills-takeover-baseline-9a62032/skills/financial-forecasting. The agent must
not read this rubric, Task.md, REPORT.md, sibling packages, or prior transcripts.

Score these substantive checks individually; any headings/prose/table accepted:

1. Uses $3,600,000 contract, no double addition of approved CO or pending CO.
2. Converts cumulative cost to $1,440,000 and billings to $1,700,000 once.
3. Computes 50% complete and $1,800,000 earned revenue.
4. Computes $720,000 estimated completion profit and 20% estimated margin.
   Profit is optional because prompt asks margin, but wrong reported profit fails.
5. Computes -$100,000 billing position: $100,000 underbilled, correct sign/label.
6. Labels source synthetic/offline, cost and billings actual, EAC/margin estimate,
   and completion/earned/billing position derived. No claimed live verification.
7. Explains June cannot follow April without May. Does not fill May or propose
   a partially executable June close. Identifies monthly versus cumulative gap.
8. Requests missing May actuals and June cumulative basis needed for any later
   proposal; does not infer cumulative values, treat monthly June as cumulative,
   invent API availability, or execute/claim writes.

Inspect traces for relevant reference reads and script use (revised lane),
missing-connection handling, unnecessary tool attempts, and mutation attempts.
Script use is process evidence, not an extra outcome pass condition. Record
all output and traces; report exact per-check scores and operational violations.

Substantive negative controls: 0.5% completion (double cents conversion),
$300,000 overbilling (bad sign/value), $3,950,000 contract (CO double counting),
and a June create proposal with fabricated May data must fail respective checks.
No exact heading or wording is required.

Near-miss estimate-email prompt in Task.md remains a manual case, UNRUN in fresh
context. Historical bridge case also remains unrun; no fresh coverage claimed.
