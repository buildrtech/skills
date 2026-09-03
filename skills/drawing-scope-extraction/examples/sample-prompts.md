# Sample prompts

Prompts that should trigger this skill. Attach the drawing set (and any spec
sections or cost code list) in each case.

- "Pull a scope of work from this drawing set. Group it by CSI division."
- "Here are the permit drawings for the Suite 300 TI. Build me a scope list I can send to subs."
- "Read the sheet notes and schedules on these plans and tell me what trades have work, with the sheet each item came from."
- "Extract the scope from A-101 through A-601 only. I just need the architectural trades."
- "We have the drawing set and Divisions 09 and 26 spec sections. List the scope with assumptions, exclusions, and RFIs separated."
- "Takeoff prep: what is on these sheets that I need to count? No quantities yet, just the list of items by division."
- "Map the scope from these drawings to our cost code list (attached) and flag anything that does not fit."

Prompts that should not trigger this skill:

- "Price this scope." (estimating with the user's own cost data, not extraction)
- "How many light fixtures are on E-201?" (quantity takeoff; this skill lists items, not counts)
- "Level these three drywall bids." (bid leveling happens after the scope list exists)
- "Write an RFI about the missing door schedule." (RFI drafting; this skill only identifies the question)
