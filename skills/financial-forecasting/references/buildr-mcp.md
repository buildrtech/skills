# Buildr MCP server

How this skill talks to Buildr. Read this before the first tool call.

## Connection

Client configuration:

```json
{ "type": "http", "url": "https://mcp.buildr.com/mcp" }
```

Login is OAuth. Request the `read` and `write` scopes; `write` is only used
in the confirmed mutation step. If the connection fails, the OAuth flow does
not complete, or the two tools below do not appear, stop and tell the user
to ask their Buildr admin whether the MCP server is enabled for their
account. It is rolling out and is not enabled everywhere yet. Do not retry
with guessed URLs or tool names.

## The two tools

The server exposes exactly two tools. Both take `code` (a string holding the
body of an async JavaScript arrow function) and an optional `timeout`. The
return value of the function body is the tool result.

| Tool | Effect | What is available inside `code` |
|---|---|---|
| `search` | Read-only discovery. Never touches account data. | `codemode.search(query)` returns operations matching a phrase. `codemode.describe("buildr.<operationId>")` returns the parameters and response shape of one operation. |
| `execute` | Runs against the account. Reads are safe; mutations take effect immediately with no undo. | `buildr.<operationId>(args)` calls an operation and returns its result. |

Discovery example:

```js
const ops = await codemode.search("forecast periods");
const shape = await codemode.describe("buildr.listFinancialsForecastPeriods");
return { ops, shape };
```

Read example:

```js
const project = await buildr.getProjectById({ id: "prj_1001" });
const periods = await buildr.listFinancialsBillingPeriods({ project_id: "prj_1001" });
return { project, periods };
```

Parameter names in this skill (`id`, `project_id`, `tab`, `metric`,
`grouping`, `start_date`, `end_date`) are illustrative. Always take the
exact names, required fields, enum values, and pagination shape from
`codemode.describe` for the account you are connected to.

## Operations this skill uses

Reads (safe to call at any time):

| operationId | Use |
|---|---|
| `listProjects` | Resolve project names to ids; list projects in a stage. |
| `getProjectById` | Project start and end dates, stage, and metadata before any period work. |
| `listProjectStages` | Resolve stage names to ids for filtering. |
| `listForecastPeriods` | Account-wide forecast: totals by month, quarter, or year for one `tab`, plus optional project rows. Response is `{ item: { metadata, totals, projects } }`, not a paginated `items` list. `totals[].amount_in_dollars` is already in dollars. Project `probability` is a 0 to 1 fraction. |
| `listFinancialsForecastPeriods` | A project's forecast periods: planned percent complete by month. Paginate to the end. |
| `getFinancialsForecastPeriodById` | One forecast period; use to verify after an update. |
| `listFinancialsClosedPeriods` | A project's closed periods: actual cost, billed amount, and EAC by month. Cost, billed, and EAC fields are in cents. Paginate to the end. |
| `getFinancialsClosedPeriodById` | One closed period; use to verify after a create or update. |
| `listFinancialsBillingPeriods` | Derived, read-only month view combining actual and forecast months. Default source for trend, variance, and health analysis. Carries `type`, `month_label`, margin, and probability values; preserve them as returned. |
| `listFinancialsPrimeContracts` | Prime contract value for a project. |
| `listFinancialsChangeOrders` | Change orders, with status; only approved ones count toward contract value. |
| `showProjectBudget` | Current budget for a project. |
| `listBudgetMilestones` | Budget milestones (estimate versions) for a project. |

Writes (only after a confirmed dry run):

| operationId | Effect |
|---|---|
| `updateFinancialsForecastPeriod` | Changes a forecast period's planned percent complete. |
| `createFinancialsClosedPeriod` | Records a month's actual cost, billed amount, and EAC. Must follow the sequencing rules in `forecast-model.md`. |
| `updateFinancialsClosedPeriod` | Edits an existing closed period's actuals or EAC. |
| `deleteFinancialsClosedPeriodById` | Removes a closed period. Only the latest closed period should be deleted, and only on explicit instruction. |
| `createFinancialsPrimeContract` | Records a prime contract. |
| `createFinancialsChangeOrder` | Records a change order. |

There are no other operation ids to use for this work. If `codemode.search`
returns something not in these tables, describe it and ask before relying
on it.

## Pagination and volume

List operations may be paginated. Read `codemode.describe` for the cursor
or page parameter and loop until the response indicates there are no more
pages. Do the loop inside one `execute` call and return the collected array
so the sequencing checks see every period:

```js
const all = [];
let cursor;
do {
  const page = await buildr.listFinancialsClosedPeriods({ project_id: "prj_1001", cursor });
  all.push(...page.items);
  cursor = page.next_cursor;
} while (cursor);
return all;
```

Field names in that loop are illustrative; use the ones `describe` returns.

## Mutation discipline

1. Read the current state (project, forecast periods, closed periods).
2. Produce the dry run: operation, project id, month, each field's current
   and proposed value, and the source of the proposed value.
3. Wait for an explicit yes from the user.
4. Run one `execute` per mutation. Do not batch several months in one call
   unless the user confirmed the whole sequence and the sequence is valid.
5. Re-read with the matching `get...ById` operation and
   `listFinancialsBillingPeriods` and report the verified values.

Never place a mutation inside a `search` call, and never run a mutation
inside the same `execute` as exploratory reads.
