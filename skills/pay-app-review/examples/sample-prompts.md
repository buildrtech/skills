# Sample prompts

Prompts that should trigger this skill. Attach the pay application (cover
sheet and continuation sheet) in each case, and the prior period and contract
terms when available.

- "Review this pay app from our steel sub before I send it to the owner. Last month's is attached too."
- "Check pay application 4 against the contract: $2.45M original, two approved COs, 10% retainage."
- "Approve this pay app." (Triggers the skill. The skill prepares the review and says so; it never approves. The memo ends with a hold/release list for the person who signs.)
- "Reconcile this G703 with last period's. Column D looks off on a couple of lines."
- "The GC billed 100% on doors and hardware but the punch list isn't done. Audit this billing."
- "Does the retainage on this application match the contract? They're supposed to be at 5% now."
- "Verify the schedule of values totals to the contract sum with CO-003 included."
- "Here's the sub's progress invoice and their lien waiver. Tell me what's missing before we pay."
- "Run the pay app checker on these two CSVs and write up the findings."

Prompts that should not trigger this skill:

- "Create a change order for the added dock leveler." (change order drafting; this skill only reconciles approved change orders against the application)
- "Build a schedule of values for the new job." (SOV preparation, not review)
- "Forecast our cash flow for the next six months." (forecasting from many applications, not a review of one)
- "Is this lien waiver form valid in Texas?" (legal question; the skill reports presence only)
- "Are these certified payroll wages correct for the electrician classification?" (wage determination, out of scope)
- "Pay this invoice." (a payment action; the skill never releases funds or changes records)
