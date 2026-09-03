# Sample prompts

Prompts that should trigger this skill. Each assumes at least one
construction software MCP server or connector is already connected.

- "What construction tools do you have access to right now, and what can you actually change?"
- "List the overdue RFIs on the Ridgeview job and who has the ball."
- "Close out the three overdue RFIs on the Ridgeview job in our project management system and tell me what changed."
- "How much is committed against cost code 03-3000 on the Canyon Road project, and which change orders are still pending?"
- "Pull every submittal in Division 26 that is waiting on the engineer and summarize by spec section."
- "Cross-reference the RFIs that mention sheet A-401 with the current revision of that sheet in the drawing tool."
- "Add yesterday's daily log for the Ridgeview job from these field notes." (attach the notes)
- "Reassign the open RFIs from Dana to Priya on the Harbor Street project."
- "Which vendors on the Harbor Street project have no contact with an email address?"
- "Measure the flooring on sheet A-101 in the takeoff tool and put the quantities in a table with the scale you used."

Prompts that should not trigger this skill:

- "Should we approve this change order?" (a cost and contract decision, not a connector task)
- "Write an RFI asking the engineer about the footing depth." (drafting; use this skill only once the user wants it created in a system)
- "Estimate the electrical scope." (estimating, not a read or write against a connector)
