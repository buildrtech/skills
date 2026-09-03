# Vendor notes

What exists per vendor as of the access dates below: official MCP servers,
community servers, authentication, known limits, and where the information
came from. These notes are a starting point for the inventory step, never a
substitute for it. Tool names listed here are the ones each server's own
documentation or README showed on the access date; every one of them can be
renamed, removed, or gated behind a plan. Trust the live tool list.

Terminology: "official" means published by the vendor. "Community" means
published by a third party under its own license and terms; using one
still binds you to the vendor's API terms.

## Procore

**What exists (accessed 2026-09-03).**

- No official, end-user-connectable Procore MCP server was published as of
  the access date. Procore's Agentic APIs documentation describes a
  "Converse API" (natural-language prompts over project data with optional
  citations) built on infrastructure from the Datagrid acquisition
  (January 2026), and states that declaring MCP servers and agents as
  components of Procore apps in the Developer Portal is planned. The same
  page lists the program as a Design Partner pilot with general availability
  "in development" and no committed date. A Procore blog post dated
  March 2, 2026 had targeted late March 2026 for general availability; treat
  the documentation page as the current source and re-check before relying
  on either.
- Procore's guidance is that create, read, update, and delete operations
  against individual records stay on the REST API. Any MCP server you meet
  today is therefore a wrapper over REST.
- Community servers (verify the license and maintainer before use):
  - `TylerIlunga/procore-mcp-server` (MIT): generates one tool per REST
    operation from Procore's OpenAPI spec (about 2,900 after
    deduplication), which is too large for most context windows, so the
    default mode exposes seven meta-tools instead:
    `procore_discover_categories`, `procore_discover_endpoints`,
    `procore_search_endpoints`, `procore_get_endpoint_details`,
    `procore_api_call`, `procore_get_config`, `procore_set_config`. The
    full per-endpoint mode is opt-in. Requires the user to download the
    OpenAPI spec from the developer portal separately.
  - `zeniasupp0rt-cmyk/procore-mcp-server` (MIT): a small hand-written set:
    `list_projects`, `get_project`, `list_rfis`, `get_rfi`, `create_rfi`,
    `list_submittals`, `get_submittal`, `create_submittal`, `list_folders`,
    `list_files`, `list_budget_line_items`, `get_budget_summary`. Note
    there is no update or close tool in that list; closing an RFI would
    need a different server.
  - Hosted intermediaries (Zapier MCP, viaSocket, CData) also advertise
    Procore MCP endpoints. They route through the intermediary's own
    account and terms; ask the user whether that is acceptable before
    using one.

**Auth.** OAuth 2.0 (authorization code for user-facing tools; client
credentials for service integrations). Every call is scoped to a company id
and most to a project id. The Agentic APIs use the same OAuth tokens.

**Known limits.**

- Two rate limits: an hourly window and a 10-second spike window. Responses
  carry `X-Rate-Limit-Limit`, `X-Rate-Limit-Remaining`, and
  `X-Rate-Limit-Reset` (Unix seconds). On `429`, wait until the reset time
  and retry with backoff and jitter. Errors (400, 403, 404) count against
  the limit too. Procore's docs give example values only and say limits
  vary by account; third-party integrators commonly cite 3,600 per hour as
  a default that can be raised on request.
- Pagination uses `page` and `per_page`; Procore recommends `per_page` at
  or below 2,000. Responses carry `Total`, `Per-Page`, and a `Link` header
  with first, prev, next, and last. Not all endpoints paginate.
- Procore is moving its Marketplace to a managed, reviewed model; apps
  that declare agentic components will go through that review.

**Sources.**

- Agentic APIs documentation: https://procore.github.io/documentation/agentic-apis (accessed 2026-09-03)
- Blog, "Building the Foundation for AI in Construction": https://www.procore.com/blog/building-the-foundation-for-ai-in-construction-the-next-era-of-the-procore (accessed 2026-09-03 via search summary; the page itself returned 404 on fetch)
- Rate limiting: https://procore.github.io/documentation/rate-limiting (accessed 2026-09-03)
- Pagination: https://procore.github.io/documentation/pagination (accessed 2026-09-03)
- Community server: https://github.com/TylerIlunga/procore-mcp-server (accessed 2026-09-03)
- Community server: https://github.com/zeniasupp0rt-cmyk/procore-mcp-server (accessed 2026-09-03)

## JobTread

**What exists (accessed 2026-09-03).**

- JobTread publishes an official remote MCP server branded the "AI
  Connector", launched in spring 2026 (JobTread's explainer post is dated
  May 28, 2026; the company reported more than 2,500 companies connected in
  under two months). JobTread's help article gives the server URL as
  `https://api.jobtread.com/mcp` and walks through adding it as a custom
  connector in Claude; JobTread says any MCP-capable client can connect.
- It reads and writes: JobTread states the AI "can create, edit, and in
  some cases delete data" and that every action runs as the connected user
  under that user's JobTread permissions. JobTread's launch announcement
  says access levels are customizable and every action is logged and
  auditable.
- JobTread did not publish a tool list on the pages reviewed. Do not
  assume tool names; run the inventory.
- Third-party aggregators (Zapier MCP, viaSocket) also expose JobTread
  actions under their own terms.

**Auth.** Sign in with the user's JobTread login during the connector's
authorization flow. Actions are attributed to that user. No separate API key
was described for the official connector.

**Known limits.** Not published on the pages reviewed. Expect the normal
JobTread permission model to apply (a user who cannot edit a budget in the
app cannot edit it through the connector). JobTread's own disclaimer says AI
outputs should be reviewed before anything is sent or relied on for cost or
schedule decisions.

**Sources.**

- Help article, "AI: Claude Integration": https://app.jobtread.com/help/ai-claude-integration (accessed 2026-09-03; URL and steps taken from the search summary because the page requires the app shell to render)
- Explainer post: https://www.jobtread.com/blog/the-jobtread-ai-connector-what-it-is-and-how-it-works (accessed 2026-09-03)
- Integration page: https://www.jobtread.com/integrations/ai (accessed 2026-09-03)
- Launch announcement: https://www.jobtread.com/news/jobtread-launches-ai-connector-giving-contractors-a-new-way-to-run-their-business (accessed 2026-09-03 via search summary)
- Adoption announcement: https://www.jobtread.com/news/jobtreads-ai-connector-becomes-the-companys-fastest-growing-integration-ever (accessed 2026-09-03 via search summary)

## Bluebeam (Revu and Bluebeam Max)

**What exists (accessed 2026-09-03).**

- Bluebeam ships an official local MCP server inside Revu for desktop,
  available only on the Bluebeam Max plan, Revu 21.9 or later. It runs on
  the user's machine and, per Bluebeam, only sends the text and metadata
  needed for the request to the AI client. Documented clients: Claude
  desktop app, GitHub Copilot CLI, ChatGPT, and AnythingLLM.
- Bluebeam's support page lists more than 40 tools. Names shown there on
  the access date include `get_page_count`, `get_page_information`,
  `save_as_text`, `search`, `list_markups_in_pdf`, `add_markup`,
  `delete_markup`, `set_markup_property`, `set_markup_state`,
  `get_markup_state`, `create_bookmarks`, `set_page_labels`, `add_links`,
  `delete_links`, `stamp`, `redact`, `open_file`, `list_studio_projects`,
  and `studio_project_search`. These are Bluebeam's names for the Revu MCP
  server and may change with Revu releases.
- The server works on PDFs and markups, not on RFIs, submittals, or cost
  records. Cross-referencing to a project management system means reading
  markup metadata here and record data there, then matching by sheet
  number and revision.

**Auth.** Tied to the signed-in Revu user and Max subscription; the user
controls which tools the AI may call and approves or denies command
execution.

**Known limits.**

- One primary Revu instance at a time; multiple open instances cause
  errors.
- Text-based search only; no visual search.
- Token budgets belong to the AI client, not Bluebeam; large drawing sets
  need paging by page ranges.
- Bluebeam published introductory Max pricing of 590 USD per user per year
  locked through 2027 renewals; confirm current pricing with Bluebeam.

**Sources.**

- Revu and MCP: https://support.bluebeam.com/revu/resources/revu-mcp.html (accessed 2026-09-03)
- Bluebeam Max features: https://support.bluebeam.com/revu/resources/max.html (accessed 2026-09-03 via search summary)
- Bluebeam Max product page: https://www.bluebeam.com/bluebeam-max/ (accessed 2026-09-03)
- Revu and AnythingLLM setup: https://support.bluebeam.com/revu/how-to/mcp-anything.html (accessed 2026-09-03 via search summary)

## Autodesk (Revit and Autodesk Construction Cloud)

**What exists (accessed 2026-09-03).**

- **Revit Public MCP Server (Tech Preview), official.** Available for Revit
  2027 since April 2026 and described in an Autodesk blog post dated
  June 17, 2026. Installed from the Autodesk Account portal under Revit
  extensions and surfaced through Autodesk Assistant; works with the user's
  own AI client accounts. Autodesk's help page describes finding elements,
  checking parameters and counts, capturing view snapshots, and bulk
  parameter edits; independent April 2026 coverage of the first tech
  preview described it as read-only. The write capability therefore depends
  on the build installed: run the inventory and treat any edit tool as a
  mutation subject to the full checklist. Tool names were not published on
  the pages reviewed.
- **Autodesk Construction Cloud.** No official ACC MCP server was found on
  the access date. Autodesk instead publishes guidance and sample servers
  for building your own on Autodesk Platform Services (blog dated
  April 8, 2026): `aps-mcp-app-example` (JavaScript, Streamable HTTP),
  `aps-aecdm-mcp-dotnet` (.NET, stdio, AEC Data Model API), and
  `aps-mcp-server-python`. Samples cover Data Management, OSS, ACC, and AEC
  Data Model APIs. Some third-party listings report that Autodesk renamed
  Autodesk Construction Cloud to Autodesk Forma in March 2026; confirm the
  current product name in the user's account rather than assuming.
- **Community servers.** `Demolinator/revit-mcp-server` (pyRevit-based,
  about 48 tools, Revit 2024 through 2027) and `LuDattilo/revit-mcp-server`
  (80+ tools, Revit 2023 through 2026) can read, create, modify, and delete
  Revit elements, which makes them far more destructive than the official
  preview. A hosted community server from ScanBIM Labs covers ACC projects,
  issues, RFIs, documents, and submittals over Streamable HTTP (released
  April 13, 2026). Check license, maintainer, and data handling before
  connecting any of these to a live model or project.

**Auth.** APS OAuth 2.0 in three patterns: two-legged (application
identity), Secure Service Accounts (automated workflows), and three-legged
(user consent). Data Management and ACC calls need a hub id and a project
id; the project id format differs between the Data Management API and the
ACC Build APIs. Revit servers run locally against the open model and act
as the signed-in Revit user.

**Known limits.**

- Tech preview means behavior changes between releases; re-run the
  inventory after any Revit update.
- Revit servers see the model that is open; confirm which model, and
  whether it is a central or local file, before reporting counts.
- ACC APIs page with limit and offset or cursor parameters depending on the
  endpoint; follow the server's own next-page mechanism.

**Sources.**

- Revit Public MCP Server (Tech Preview), Revit 2027 help: https://help.autodesk.com/cloudhelp/2027/ENU/Revit-WhatsNew/files/GUID-97697CBF-0E11-484E-96E5-4277E3E8D61F.htm (accessed 2026-09-03)
- Autodesk AEC blog, "Introducing the Revit Public MCP Server": https://www.autodesk.com/blogs/aec/2026/06/17/revit-public-mcp-server/ (accessed 2026-09-03 via search summary; direct fetch was blocked)
- BIM Chapters, "Revit MCP Public Server Tech Preview now available for Revit 2027": https://bimchapters.blogspot.com/2026/04/revit-mcp-public-server-tech-preview.html (accessed 2026-09-03)
- APS blog, "Building Custom MCP Servers with Autodesk Platform Services": https://aps.autodesk.com/blog/building-custom-mcp-servers-autodesk-platform-services (accessed 2026-09-03)
- Community Revit server: https://github.com/Demolinator/revit-mcp-server (accessed 2026-09-03 via search summary)
- Community Revit server: https://github.com/LuDattilo/revit-mcp-server (accessed 2026-09-03 via search summary)
- Community ACC server listing: https://www.pulsemcp.com/servers/scanbimlabs-acc (accessed 2026-09-03)

## OpenTakeoff

**What exists (accessed 2026-09-03).**

- Open-source (Apache-2.0) PDF takeoff engine from Kentucky-ai with an
  official stdio MCP server, listed on the public MCP registry. Runs with
  `npx -y opentakeoff-mcp` on Node 20 or later; no account needed.
- The README describes 47 tools grouped by function, with names such as
  `one_click` (room detection), `set_scale`, `measure_polygon`,
  `sheet_graph` (reading schedules), and `export_marked_pdf`. Same geometry
  code as the browser canvas, so agent-committed shapes match hand-drawn
  ones.
- Design choices that matter for agents: unscaled sheets refuse
  measurement until `set_scale` succeeds; the engine prefers refusing to
  guessing; agent work exports as "pencil" proposals that a human approves
  before they become final.

**Auth.** None; it works on local files. Treat the plan set the user
provides as the scope boundary.

**Known limits.** Quantities are only as good as the scale and the sheet
legibility. Report the scale, the sheet, and the measurement method with
every number, and never round a quantity into a bid figure; that is the
estimator's job.

**Sources.**

- Repository and README: https://github.com/Kentucky-ai/opentakeoff (accessed 2026-09-03)
- MCP server source: https://github.com/Kentucky-ai/opentakeoff/blob/main/mcp/server.ts (accessed 2026-09-03 via search summary)
- Product page: https://opentakeoff.kentucky-ai.com/ (accessed 2026-09-03 via search summary)

## Vendors without notes here

Sage, Viewpoint (Trimble), CMiC, Autodesk BuildingConnected, PlanGrid
(now part of Autodesk Build), Fieldwire, Buildertrend, and others may have
connectors through aggregators or community projects. The same workflow
applies: inventory first, read before writing, ids over names, dry-run and
confirm. Add a section here with dated sources when you verify one.
