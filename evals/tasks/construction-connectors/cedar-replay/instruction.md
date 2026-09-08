Audit input/replay.json and write output/audit.json plus a concise report in
output/report.md. This is explicitly synthetic fixture replay. No MCP is
available; do not call remote services or execute any writes. Explain what
this interrupted closeout establishes, what remains uncertain, and the
cross-system drawing links. Do not assume identical IDs identify the same
record. The supplied transcript is the only record evidence.

For deterministic comparison use this JSON contract (report headings and prose
are unrestricted): mode; scope (copy the identifying fields); unique_records
(integer); pagination_complete (boolean); overdue_ids and missing_due_ids
(lists); outcomes (map proposed RFI ids to verified, mismatched, unverified,
failed, or not_attempted); confirmed_sheet_links (map RFI ids to the complete
external reference object with version); unresolved_sheet_links (list of RFI
ids); live_writes_performed (integer); retry_permitted_by_request (boolean).
Include additional explanatory fields freely. The outcome describes the
record verification established by the transcript, not an invented later run.
