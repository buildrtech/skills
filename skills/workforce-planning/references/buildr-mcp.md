# Buildr connection and discovery

Read before live tool use. This package contains no live API schema or proof
that a particular account exposes workforce operations. Use the authenticated
Buildr MCP connection configured in the user's client. If absent or failing,
report the observed connection/auth error and request connection or an export;
do not claim an account rollout state or diagnose scopes without evidence.

Inspect the actual MCP tool listing and input schemas. If the connection
exposes code-mode `search` and `execute`, inspect their schemas and discovery
help before supplying code. Discover workforce operations, then describe each
operation needed for the request. The names in data-model.md are lookup hints
from prior examples, not guaranteed callable APIs. Never synthesize endpoint,
parameter, filter, pagination, or response names from them.

Use discovered read operations for roles, employees, assignments, time off,
utilization periods, and any required project/certification/experience data.
Follow the documented pagination termination condition. Preserve filters,
window, read timestamp, and completeness; repeated cursors or missing pages
are an incomplete read, not an empty result. Confirm whether date bounds are
exclusive and how open-ended periods and missing intervals are represented.
If that contract cannot be established, report uncertain intervals.

Keep discovery and reads separate from mutations. Before any authorized write,
describe the mutation and verify actual permission; do not infer permission
from tool availability. Return identifiers and stored fields for verification.
A read-only connection can deliver analysis and a dry run.

On unknown operation or invalid parameter, return to discovery. On validation
failure, report the relevant error and revise the affected proposal. On partial
failure or timeout, stop and re-read affected state before any retry; a timed-out
write may have succeeded. Do not assume transactional batches or an undo API.

For supplied exports and fixtures, skip MCP calls entirely. Label results
"offline snapshot" or "synthetic fixture replay" and name the supplied source.
Such a replay tests local rules only, not OAuth, tool discovery, schemas,
pagination, permissions, mutation behavior, or current account data.
