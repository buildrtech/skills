# Queued fresh-context paired evaluation

Exactly two runs, sequential, same coordinator-selected provider/model/settings: first baseline skill at git 9a62032 (execution copy /tmp/skills-takeover-baseline-9a62032/skills/bid-leveling), then revised skills/bid-leveling at version 2.0.0. Give each only INPUT.md and its isolated skill folder. Empty output directory; no tests, EXPECTED.md, REPORT.md, source repo, or baseline/revised results exposed. Do not give pre-extracted JSON: each run must interpret the option identity and printed alternates itself.

Use one unfamiliar site-fencing case, one attempt per condition, no review workers, no remote APIs/MCP, no writes outside sandbox output. Suggested limit 10 minutes/run. Preserve deliverable, extraction/decision inputs, full trace and exit result for coordinator review against hidden EXPECTED.md. Make no statistical trigger-rate or general-model claims from n=1.

Authorization: approved by coordinator after PDF released its slot. Both sequential attempts executed; see RESULTS.json for artifact-level tie and revised provider failure. No worker retry.
