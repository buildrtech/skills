# Buildr MCP server

How this skill talks to Buildr. Read this before phase 1 and again if any
call fails.

## Connection

Add the server to the agent's MCP client configuration:

```json
{
  "mcpServers": {
    "buildr": {
      "type": "http",
      "url": "https://mcp.buildr.com/mcp"
    }
  }
}
```

The first call opens an OAuth login in the browser. Grant both the `read`
and `write` scopes; leveling needs writes, and read-only diagnosis works
with `read` alone. The session belongs to the signed-in Buildr user, so
every write is attributed to them and limited to their permissions.

If the connection or login fails, tell the user to ask their Buildr admin
whether the MCP server is enabled for their account. It is rolling out and
not every account has it yet. Do not retry in a loop.

## The two tools

The server exposes exactly two tools. Both take `code` (a string containing
the body of an async JavaScript arrow function) and an optional `timeout` in
milliseconds. The sandbox has no network access apart from the Buildr API
and exposes only two globals, `buildr` and `codemode`.

| Tool | Purpose | Touches account data |
|---|---|---|
| `search` | Discover operations and read their parameter and response shapes with `codemode.search(...)` and `codemode.describe(...)`. | No |
| `execute` | Run operations against the account with `buildr.<operationId>(args)` and return a value. Every mutation takes effect immediately. | Yes |

Do not invent tool names. There is no separate tool per operation; the
operation is chosen inside the code you pass.

## Code-mode pattern

### `search` example

```javascript
// search tool, code:
const matches = await codemode.search("bid packages");
const shape = await codemode.describe("buildr.getBiddingLevelView");
return { matches, shape };
```

`codemode.search` takes a plain-language query and returns matching
operation ids with one-line summaries. `codemode.describe` takes a
fully-qualified operation id (`buildr.<operationId>`) and returns its
parameters and response shape. Always describe an operation before calling
it for the first time in a session; parameter names in this skill are
illustrative and the described shape wins.

### `execute` example

```javascript
// execute tool, code:
const packages = await buildr.listBiddingPackages({ project_id: PROJECT_ID });
return packages;
```

Return whatever the next step needs. Keep each `execute` body to one
logical step (one group of reads, or one write plus its reload) so a failure
is easy to locate and nothing runs that the user has not confirmed. Do not
batch several unrelated mutations into one body.

## Operations this skill uses

Reads: `listProjects`, `getProjectById`, `listBiddingPackages`,
`getBiddingPackageById`, `listBiddingBidders`, `getBiddingBidderById`,
`listBiddingBidderContacts`, `listBiddingSubmissions`,
`getBiddingSubmissionById`, `getBiddingLevelView`,
`listBiddingPackageDocuments`, `listCompanies`, `listContacts`,
`listCostCodes`, `listAlternates`, `vcsListBranches`,
`vcsListBranchStatuses`, `vcsListLineItems`, `vcsListAlternateLineItems`,
`biddingLevelingValidate`.

Writes: `createBiddingPackage`, `updateBiddingPackage`,
`createBiddingBidder`, `updateBiddingBidderIntent`,
`createBiddingBidderContact`, `createBiddingSubmission`,
`updateBiddingSubmission`, `createBiddingSubmissionAttachment`,
`createAlternate`, `createAlternateOption`, `vcsCreateBranch`,
`vcsCreateLineItems`, `vcsCreateAlternateLineItems`,
`vcsUpsertSubmissionLineItems`, `vcsUpsertSubmissionAlternateLineItems`,
`vcsCarryLineItems`, `vcsCreateCommit`.

`biddingLevelingValidate` takes `project_id`, `branch_id`, and
`cost_code_id` and returns `ready_for_handoff`, `blockers`, and
`carry_selections`.

## Budget VCS rules

- Budget changes (GC scope rows, alternate lines, submission line items,
  carry selections) need a branch. Use `vcsListBranches` and pick the branch
  whose `branch_type === "current_user_change_request"` and
  `mutable === true`. If none exists, create one with `vcsCreateBranch` and
  a short `change_request_title`.
- Package and submission creation can advance budget main. Create and
  reload those before selecting or creating the branch, so the branch is not
  stale before its first scope write.
- Working changes on the branch stay uncommitted until `vcsCreateCommit`. A
  branch with uncommitted changes is dirty; a dirty branch is never a
  completed change request and must never be described as one.
- Commit only after the user approves the validated matrix. If they decline,
  leave the branch dirty and say so.
- Amounts are integer cents everywhere: `41250000` is $412,500.00.
- Cost code divisions 00 and 01 are indirect cost; every other division is
  direct. Bid packages for trade work belong on direct cost codes.

## Error handling

- On any failure, report the exact operation id, the arguments sent (with
  ids), and the error text. Do not paraphrase the error and do not retry
  with guessed parameter shapes; re-run `codemode.describe` and compare.
- A failed read is not evidence that a record does not exist. An empty
  `codemode.search` result is not evidence that an operation is unavailable;
  describe the operation id directly.
- A failed write in the middle of phase 5: stop, reload the affected records
  with the matching list or get operation, tell the user exactly what was
  created before the failure, and do not continue to the next group or
  commit until they say how to proceed.
- Permission errors on writes usually mean the `write` scope was not granted
  or the user's Buildr role cannot edit budgets; say which is likely and
  stop.
- Timeouts: pass a larger `timeout` for large reloads
  (`getBiddingLevelView` on a big package) rather than splitting a mutation.
