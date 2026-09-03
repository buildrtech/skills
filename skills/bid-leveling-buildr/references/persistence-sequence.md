# Persistence sequence

Read this at phase 5. Run the steps in this order, one `execute` body per
step, and do the verification read before moving on. Parameter names are
illustrative; take the exact shape from `codemode.describe("buildr.<op>")`
before the first call. Nothing in this table runs before the user confirms
the phase 4 dry run.

| # | Operation | Inputs | Verify after |
|---|---|---|---|
| 1 | `getProjectById` | `project_id` from phase 1 | Project name matches the user's request. |
| 2 | `createBiddingPackage` or `updateBiddingPackage` (skip if reusing) | `project_id`, package name, `cost_code_id` | `getBiddingPackageById` returns the package with the right cost code. Note the `package_id`. |
| 3 | `listCompanies` / `listContacts` | bidder names from evidence | Matched existing companies by exact or user-confirmed match. Never create a company for a name that already exists in a slightly different form without asking. |
| 4 | `createBiddingBidder` (one per bidder pricing company) | `project_id`, `package_id`, company id or new company details | `listBiddingBidders` shows one bidder per company, no duplicates. Note each `bidder_id`. |
| 5 | `createBiddingBidderContact` (optional) | `bidder_id`, contact from the proposal | `listBiddingBidderContacts` shows the contact on the right bidder; a contact from another company is a mistake. |
| 6 | `createBiddingSubmission` (one per bidder pricing version) | `project_id`, `package_id`, `bidder_id`, `amount_in_cents` = base bid total from evidence | `listBiddingSubmissions` shows one submission per bidder, the amount matches the evidence, and it is the latest version. Note each `submission_id` and re-key the leveling model. |
| 7 | `createBiddingSubmissionAttachment` (when the operation accepts the file) | `submission_id`, the bid document | `getBiddingSubmissionById` lists the file. If upload is not possible from the sandbox, tell the user and do not claim it. |
| 8 | `vcsListBranches` | `project_id` | A branch with `branch_type === "current_user_change_request"` and `mutable === true`. If none, step 9. |
| 9 | `vcsCreateBranch` (only if step 8 found none) | `project_id`, `change_request_title` | `vcsListBranches` shows the new branch as mutable. Note `branch_id`. Use it for every later step. |
| 10 | `vcsListLineItems` | `project_id`, `branch_id`, `with_working_changes: true` | Existing scope rows on the cost code, including rows not yet assigned to a package. Reuse compatible `record_id`s; stop and ask if more than one row could match a modeled row. |
| 11 | `vcsCreateLineItems` | `project_id`, `branch_id`, `line_items` from `base_rows` (description, quantity, uom, `unit_cost_in_cents: 0`, `cost_code_id`, `bidding_package_id`; include `record_id` when updating an existing row) | The response lists one `record_id` per modeled base row. Reload with `vcsListLineItems` and confirm no duplicates. Write each `record_id` into the leveling model. |
| 12 | `vcsUpsertSubmissionLineItems` (one call per submission) | `project_id`, `package_id`, `submission_id`, `branch_id`, `line_items` with `record_id`, status, and amount only on included itemized rows | `getBiddingLevelView` for the branch and cost code shows every submission with a cell for every base row and amounts equal to the evidence. If one upsert fails, stop and report; do not continue or commit. |
| 13 | `updateBiddingSubmission` (only for intentional lump-sum pricing) | `submission_id`, `branch_id`, `amount_in_cents` | The submission amount matches the evidence total; the change is on the same branch as the rows. |
| 14 | `listAlternates` then `createAlternate` and `createAlternateOption` (solicited alternates only, status open) | `project_id`, `package_id`, alternate name from the bid form | `listAlternates` shows the alternate open with its option. Reuse an existing alternate rather than creating a second one for the same scope. |
| 15 | `vcsCreateAlternateLineItems` | `project_id`, `branch_id`, lines with `bidding_package_id`, `cost_code_id`, and `alternate_option_id` for solicited rows (omit it for unsolicited review rows, priced at zero) | `vcsListAlternateLineItems` returns one GC alternate line per alternate row with a `record_id`. |
| 16 | `vcsUpsertSubmissionAlternateLineItems` (per submission) | `project_id`, `package_id`, `submission_id`, `branch_id`, lines with the GC alternate `record_id` and the bidder's amount (omit `alternate_option_id` on unsolicited rows) | `getBiddingLevelView` shows each bidder's alternate amount; unsolicited rows appear under the package's unsolicited alternate line items. |
| 17 | `vcsCarryLineItems` | `project_id`, `package_id`, `branch_id`, plus the selection payload from `describe`, containing only the selections the user confirmed | `getBiddingLevelView` (or `biddingLevelingValidate`'s `carry_selections`) shows exactly those selections and nothing else. |
| 18 | `biddingLevelingValidate` | `project_id`, `branch_id`, `cost_code_id` | `ready_for_handoff: true` and `blockers: []`. Repair only named blockers; never invent a plug or change a status to pass. |
| 19 | `getBiddingLevelView` | `project_id`, `branch_id`, `cost_code_id` | Every amount matches an evidence record or user-stated plug; `branch_id` in the view equals the working branch. Present the matrix and ask for approval to commit. |
| 20 | `vcsCreateCommit` (only after approval) | `project_id`, `branch_id`, commit message | `vcsListBranchStatuses` shows the branch clean; a final `getBiddingLevelView` matches the pre-commit view. |

## Notes

- Steps 2 through 7 run before step 8 on purpose: package and submission
  creation can advance budget main, and a branch created earlier would be
  stale.
- Steps 10 through 17 all use the same `branch_id`. Mixing branches leaves
  rows the view cannot see.
- If the user stops at any step, leave the branch as it is, reload, and
  report the exact state: which records exist, which are working changes,
  and that nothing was committed.
- For a read-only request (verify an existing package), run only steps 1, 8,
  18, and 19 and report.
