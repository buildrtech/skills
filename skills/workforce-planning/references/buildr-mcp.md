# Buildr MCP server

How this skill talks to Buildr. Read this before the first tool call.

## Connection

Add the server to the agent's MCP client configuration:

```json
{ "type": "http", "url": "https://mcp.buildr.com/mcp" }
```

The server uses OAuth login. On first use the agent opens a browser login
for the user's Buildr account. Two scopes exist: `read` (all list and show
operations) and `write` (create, update, dismiss, and delete operations).
Analysis needs `read`; staffing changes need `write`.

If the connection fails, the login does not complete, or the two tools do
not appear, tell the user to ask their Buildr admin whether the MCP server
is enabled for their account. It is rolling out, so a healthy Buildr account
can still be missing it. Stop there; do not answer from memory or guess at
the account's data.

## The two tools

The server exposes exactly two tools. Do not look for or invent others.

| Tool | Purpose | Touches account data | Parameters |
|---|---|---|---|
| `search` | Discover operations and their parameter and response shapes | Never | `code: string`, `timeout?: number` |
| `execute` | Run operations against the account | Yes; mutations are immediate | `code: string`, `timeout?: number` |

`code` is the body of an async JavaScript arrow function. The server wraps
it, runs it, and returns whatever the body returns. Use `await` freely and
`return` a value; anything not returned is lost.

Inside `search`, two helpers are available:

- `codemode.search(query)` returns the operations matching a keyword, with
  their operationIds and one-line descriptions.
- `codemode.describe(operationId)` returns the parameters and the response
  shape for one operation. The operationId is written with the `buildr.`
  prefix, for example `codemode.describe("buildr.listWorkforceAssignments")`.

Inside `execute`, the `buildr` object exposes every operation as an async
function: `await buildr.<operationId>(args)`.

## Operations this skill uses

Reads: `listWorkforceEmployees`, `showWorkforceEmployee`,
`listWorkforceRoles`, `listWorkforceAssignments`, `showWorkforceAssignment`,
`listWorkforceEmployeeUtilizationPeriods`, `listWorkforceTimeOffs`,
`listWorkforceCertificationTypes`, `listWorkforceEmployeeCertifications`,
`listWorkforceEmployeeExperiences`, `listWorkforcePreviousEmployerExperiences`,
`listProjects`, `getProjectById`, `listProjectStages`.

Writes: `createWorkforceEmployee`, `updateWorkforceEmployee`,
`dismissWorkforceEmployee`, `createWorkforceRole`,
`createWorkforceAssignment`, `updateWorkforceAssignment`,
`deleteWorkforceAssignment`, `createWorkforceTimeOff`.

Parameter names, filter names, pagination, and response fields are whatever
`codemode.describe` returns for the account. The examples in this skill use
plausible snake_case names so the pattern is clear; confirm each one before
relying on it.

## Code-mode pattern

Discover once per session, read in as few round trips as the API allows,
compute locally in the agent, and write only after the user confirms.

Discovery with `search`:

```js
const ops = await codemode.search("workforce");
const assignments = await codemode.describe("buildr.listWorkforceAssignments");
const periods = await codemode.describe("buildr.listWorkforceEmployeeUtilizationPeriods");
const certs = await codemode.describe("buildr.listWorkforceEmployeeCertifications");
return { ops, assignments, periods, certs };
```

Reading with `execute`, paging until the list is exhausted:

```js
const all = [];
let page = 1;
while (true) {
  const res = await buildr.listWorkforceAssignments({
    start_date_before: "2027-08-01",
    end_date_after: "2026-11-01",
    page,
  });
  all.push(...res.data);
  if (!res.next_page) break;
  page = res.next_page;
}
return all;
```

Writing with `execute`, after confirmation, returning what the server
actually stored so it can be compared with the dry run:

```js
const updated = await buildr.updateWorkforceAssignment({
  id: "asg_0410",
  employee_id: "emp_0107",
});
return updated;
```

Keep each `execute` body small and single-purpose. A body that reads,
computes, and writes in one call cannot be stopped between the dry run and
the mutation, which defeats the confirmation gate.

## Error handling

- Connection or auth failure: stop and tell the user to check with their
  Buildr admin that the MCP server is enabled for the account. Do not
  proceed with partial data.
- Unknown operation or unexpected parameter: re-run `codemode.describe`
  for that operation and fix the call. Do not guess at alternate names.
- Permission error on a write: the login likely has only the `read`
  scope. Report the dry run as the deliverable and tell the user which
  scope is missing.
- Validation error on a write (dates, allocation, role mismatch): report
  the server's message verbatim, fix only what the message names, and
  re-present the corrected item for confirmation rather than retrying
  silently.
- Failure partway through a batch: stop at the first error. Report which
  changes were applied and which were not, re-read the affected
  assignments, and let the user decide whether to continue.
- Timeouts on large accounts: narrow the date window or add the operation's
  employee, project, or role filters and read in smaller pieces. Pass a
  larger `timeout` only when the read is legitimately large.
