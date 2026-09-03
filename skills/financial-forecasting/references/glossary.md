# Glossary

Plain definitions for the terms in this skill's outputs. These are the
common construction-accounting meanings; the user's own accountant sets
the treatment that goes on their WIP schedule.

**Estimate at completion (EAC).** The total cost a project is expected to
incur when finished: actual cost to date plus the estimated cost to
complete the remaining work. Recorded on each closed period as of that
month. When the EAC rises without a matching change in contract value,
margin falls.

**Cost-to-cost percent complete.** Progress measured by spend: actual cost
to date divided by EAC. It is the input-based method most contractors use
for percentage-of-completion accounting. It moves when cost is incurred and
also when EAC is revised, which is why a reforecast can change percent
complete without any new work being put in place.

**Contract value.** Prime contract amount plus approved change orders.
Pending or rejected change orders are excluded until approved.

**Earned revenue.** Revenue recognized to date under the cost-to-cost
method: percent complete multiplied by contract value. It is the figure
billings are compared against, not the amount invoiced.

**Estimated profit at completion.** Contract value minus EAC. **Margin** is
that profit divided by contract value, expressed as a percentage. A "point"
of margin is one percentage point.

**Billed to date.** Cumulative amounts invoiced to the owner through the
period, from the closed period record.

**Over/under billing.** Billed to date minus earned revenue. Overbilled
(positive) means invoices are ahead of earned revenue; on a WIP schedule it
appears as "billings in excess of costs and estimated earnings", a
liability. Underbilled (negative) means earned revenue is ahead of
invoices; it appears as "costs and estimated earnings in excess of
billings", an asset. Some overbilling early in a job is normal (mobilization,
front-loaded schedules of values); persistent underbilling is a cash and
change-order warning sign.

**Closed period.** A month whose actuals have been recorded: cost to date,
billed to date, and EAC as of that month. Once closed, it is the record the
later forecast is rebuilt from.

**Forecast period.** A future month with a planned percent complete.
Buildr recalculates the remaining forecast periods from the latest closed
period using cost-to-cost completion.

**Billing period.** The derived month-by-month view of a project that
combines closed (actual) months and forecast months in one sequence. Each
row carries a `type` of actual or forecast.

**Work in progress (WIP).** Awarded projects currently under construction
with cost being incurred and periods being closed.

**Backlog.** Awarded projects that have not yet started construction, or
the unearned remainder of contract value on projects that have. In this
skill, the `backlog` tab means the former: awarded, not yet started.

**Pursuits.** Projects being bid or negotiated that have not been awarded.
Their revenue is speculative and is usually shown probability-weighted.

**Probability-weighted pipeline.** Each pursuit's amount multiplied by its
probability of award (a 0 to 1 fraction), summed across the population. It
is an expected value, not a forecast of any single outcome, and it is only
as good as the probabilities the team maintains.

**Margin bridge.** A walk from a project's margin at one close to its margin
at a later close, attributing the change to contract value changes
(approved change orders), EAC changes (cost growth or savings), and any
correction to prior actuals. Where the data does not explain a step, the
bridge says so.

**Margin fade.** Margin declining over successive closes as EAC grows. The
opposite is margin gain. Two points in either direction on one close is a
common review threshold.

**Reforecast.** Rebuilding the remaining forecast periods after a close so
that planned percent complete, remaining revenue, and remaining cost agree
with the latest EAC.
