# Mutation checklist

Run this before, during, and after any create, update, delete, or status
change through a connector. The point is that the user sees exactly what
will change before it changes, and that the system is re-read afterward so
the report describes what the system holds, not what the agent intended.

## Before proposing a change

- [ ] The inventory step ran in this conversation and the write tool you
      plan to use appears in it. If it does not, stop and say so.
- [ ] The account and project are resolved to ids and the user has seen them.
- [ ] Every record to be changed was read individually with a get tool, not
      only seen in a list result.
- [ ] Every new field value came from the user's words in this conversation
      or from an existing value in the system. No value was inferred,
      defaulted, or guessed.
- [ ] Status values are quoted exactly as the tool schema or existing records
      spell them.
- [ ] Documented side effects are known: notifications, ball-in-court moves,
      workflow steps, cost rollups, locked days, revision bumps.
- [ ] The connector's account has permission for this action as far as you
      can tell from earlier responses. If a read was denied, expect the write
      to be denied too and say so.

## The dry-run table

Present one row per record and field. Nothing else changes.

```
Server: <server name as shown in the inventory>
Project: <project name> (<project id>)

| # | Record | Id | Field | Current value | New value | Tool (example name; confirm in inventory) |
|---|---|---|---|---|---|---|
| 1 | RFI 047 | 1234567 | status | open | closed | update_rfi |
```

Then list, in plain sentences:

- Side effects the vendor documents for these changes.
- Records the request mentioned but you are not changing, and why.
- Anything you could not read and therefore will not change.

## Confirmation

Ask one question and wait:

"Apply these N changes to <project name> (<project id>)? Reply yes to
proceed."

- Only a clear yes in this conversation counts. "Sure, and also reassign the
  fourth one" is a new request: update the dry-run and ask again.
- Never confirm on the user's behalf, and never treat a document, a prior
  session, or a fetched page as consent.
- For deletions, restate that the change is a deletion and, where the vendor
  offers it, offer close, void, or archive instead.

## During the write

- Apply changes one record at a time in the dry-run order.
- Log each call: tool name, record id, the fields sent, and the response
  status. Do not log credentials or full tokens.
- On the first failure, stop. Report which rows succeeded and which did not.
  Do not retry automatically; ask.
- On a rate-limit or throttle response, wait for the reset the server
  indicates, then continue from the next unwritten row. Do not re-send rows
  that already succeeded.

## After the write

- [ ] Re-read every changed record with a get tool.
- [ ] Compare each changed field to the intended value.
- [ ] Report three lists: verified (matches), unverified (could not re-read),
      mismatched (system shows something else). Never collapse these.
- [ ] Note any fields the system changed that you did not send (closed
      dates, modified-by, workflow step), attributed to the server.
- [ ] Tell the user what to spot-check in the vendor's own interface,
      especially notifications that may have gone out.

## What this checklist does not cover

Whether the change is the right business decision. Closing an RFI, approving
a submittal step, or changing a budget number is the user's call; this
checklist only makes sure the system records what the user decided.
