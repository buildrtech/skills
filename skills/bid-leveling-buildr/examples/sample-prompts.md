# Sample prompts

Prompts that should trigger this skill. The Buildr MCP server must be
connected; attach the bid documents or point at submissions already in
Buildr.

- "Level these three drywall bids into Buildr for the Larkspur Health Center. Package is 'Drywall & Framing - 09 20 00'. Use $14,000 for insulation if anyone excludes it."
- "The concrete bids are already attached to the submissions in Buildr on the Westfield Depot project. Build the GC scope rows and price each submission against them."
- "Set up a bid package for roofing on the Harmon Street Lofts project, add the four bidders from these proposals, and get the leveling matrix ready for review. Don't commit until I've looked at it."
- "Check the electrical package on Larkspur: is it ready for handoff, what blockers does validation show, and which bidder is carried on each row?"
- "Two of these are the same bidder, the second one is a revised proposal. Level the package in Buildr using the revision and tell me what changed."
- "Add Alternate 2 from the bid form to the mechanical package in Buildr and price each bidder's response to it."

Prompts that should not trigger this skill:

- "Level these bids and give me a spreadsheet." (no Buildr persistence requested; use a neutral bid-leveling skill)
- "Email the bidders that the bid date moved." (bidder messaging, not leveling)
- "Which sub should we award?" (award decisions belong to the estimator; the skill produces a comparison, not a recommendation)
- "Estimate the drywall for this project from the drawings." (estimating, not leveling submitted bids)
