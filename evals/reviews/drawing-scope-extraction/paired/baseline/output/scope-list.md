# Scope list: Juniper Transit Break Room

4 candidates recorded: 1 included, 2 for review, 1 excluded. Sheets: 3 of 4 reviewed (0 via OCR, 1 unreadable, 0 not reviewed).

Drawing-backed scope only. No quantities or pricing. Each item cites the sheet and the place on the sheet it came from. This is a draft for review against the full contract documents, not a takeoff or an estimate.

## Included scope

### Division 06: Wood, Plastics, and Composites

- **Wood backing** (direct) [cand-001]
  Source: G-010, GN-1: "PROVIDE WOOD BACKING AT NEW WALL-MOUNTED SHELVES."
  Note: Backing is explicitly required. Shelf layout remains unresolved separately; no dimensions or extent inferred.

## Assumptions

None recorded.

## Exclusions (by others)

### Division 23: Heating, Ventilating, and Air Conditioning (HVAC)

- **Temperature sensors** (by_others) [cand-004]
  Source: M-110, Note 1: "TEMPERATURE SENSORS FURNISHED AND INSTALLED BY OWNER UNDER SEPARATE CONTRACT."
  Reason: M-110 Note 1 explicitly assigns both furnishing and installation to the owner under a separate contract. Division 23 is the mechanical temperature-control placement judgment; the text does not establish an integrated automation or DDC system to justify prior Division 25.

## RFIs / review items

### RFIs

- What is the dimensioned staff-room shelf layout referenced on A-610? The supplied A-610 text has no readable content to verify it; shelves remain under review. (Source: A-110 Note 1; A-610 unreadable) [cand-002]
- What door hardware does the A-610 schedule require? No legible rows are available, so hardware remains under review. (Source: A-110 Note 2; A-610 unreadable) [cand-003]

### Review items

Drawing-backed but unresolved. Each stays off the included list until the question in its reason is answered.

#### Division 06: Wood, Plastics, and Composites

- **Plastic laminate shelves in staff room** (direct) [cand-002]
  Source: A-110, also A-610, Note 1: "PROVIDE PLASTIC LAMINATE SHELVES IN STAFF ROOM. DIMENSIONED LAYOUT SEE A-610."
  Reason: A-110 Note 1 directly requires shelves, but their dimensioned layout depends on unreadable A-610. Keep under review until the layout is verified. Division 06 for plastic laminate architectural shelving.
  Note: A-610 is a referenced dependency only; no layout was read there.

#### Division 08: Openings

- **New door hardware** (reference_only) [cand-003]
  Source: A-110, also A-610, Note 2: "NEW DOOR HARDWARE PER A-610 SCHEDULE."
  Reason: Corrected prior attribution: the quote is on A-110 Note 2, not A-610. Hardware is defined by the unreadable A-610 schedule; no schedule rows or hardware sets can be verified. Division 08 for door hardware.
  Note: A-610 is a referenced dependency only, not verified schedule evidence.

## Coverage ledger

### Sheets

| Sheet | Title | Status | Candidates | Note |
|---|---|---|---|---|
| G-010 | General notes | reviewed | cand-001 | Read all supplied extracted text: GN-1 verifies backing. Text-only review; no PDF inspected. |
| A-110 | Room plan | reviewed | cand-002, cand-003 | Read both supplied notes in full. Shelves and hardware depend on unreadable A-610 and remain under review. No PDF inspected. |
| A-610 | Door schedule | unreadable | cand-002, cand-003 | Supplied index reports scan and prior OCR with no legible rows; no new OCR performed and no native PDF supplied. No independent scope extracted. Candidate IDs mark unresolved dependencies, not verified content. |
| M-110 | Mechanical notes | reviewed | cand-004 | Read all supplied extracted text: Note 1 assigns temperature sensors to owner. Exclusion only; no included scope. No PDF inspected. |

### Probes and other sources

| Source | Kind | Status | Candidates | Note |
|---|---|---|---|---|
| demolition [terms: demolition, remove, existing to remain, salvage, relocate] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| concrete [terms: concrete, slab, pad, patch, level, core drill] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| blocking [terms: blocking, backing, nailer, plywood, in-wall support] | probe | covered | cand-001 | Matches: G-010 text line 1. Backing verified and included. |
| casework [terms: casework, millwork, cabinet, countertop, shelving, plam] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| firestopping [terms: firestopping, firestop, fire-rated, rated, UL, penetration] | probe | excluded | none | Substring-only false positives: UL in SCHEDULE on A-110 Note 2 and schedule in the A-610 unreadability notice. No firestopping work stated; A-610 remains unreadable. |
| sealant [terms: sealant, caulk, acoustical seal, joint] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| roofing [terms: roofing, roof, flashing, curb, membrane] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| door hardware [terms: door hardware, hardware set, HW, lockset, closer, cylinder, keyed] | probe | needs_followup | cand-003 | Matches: A-110 text line 2. Referenced layout/schedule unresolved; affected items remain under review. |
| access panels [terms: access panels, access door, AP, ceiling access] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| glazing [terms: glazing, glass, tempered, storefront, sidelite, mirror, film] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| gypsum board [terms: gypsum board, GWB, gyp, partition type, stud, furring, soffit] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| acoustical ceiling [terms: acoustical ceiling, ACT, ceiling tile, grid, lay-in, ceiling height] | probe | excluded | none | Substring-only false positive: ACT in CONTRACT on M-110 Note 1. No acoustical ceiling work stated. |
| resilient flooring [terms: resilient flooring, LVT, VCT, base, RB, carpet, CPT, tile, transition] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| painting [terms: painting, paint, PT, finish, coating, stain] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| toilet accessories [terms: toilet accessories, grab bar, dispenser, accessory, TA] | probe | excluded | none | Substring-only false positives: TA in STAFF on A-110 Note 1 and INSTALLED on M-110 Note 1. No toilet accessory work stated. |
| wall protection [terms: wall protection, corner guard, FRP, crash rail, wainscot] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| sprinkler [terms: sprinkler, fire protection, FP, head, sprink] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| plumbing fixtures [terms: plumbing fixtures, sink, faucet, fixture, rough-in, cap, waste, vent, water heater] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| HVAC [terms: HVAC, diffuser, grille, VAV, exhaust, thermostat, duct, T&B, balance] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| electrical [terms: electrical, fixture, lighting, receptacle, circuit, panel, sensor, dimmer, fire alarm, data, access control] | probe | excluded | cand-004 | Matches: M-110 text line 1. Sensors are owner work and excluded; search category does not determine CSI division. |
| shelves / laminate / layout [terms: shelves, plastic laminate, dimensioned layout] | probe | needs_followup | cand-001, cand-002 | Matches: A-110 text line 1, G-010 text line 1. Backing verified and included. Referenced layout/schedule unresolved; affected items remain under review. |
| hardware / schedule [terms: hardware, schedule] | probe | needs_followup | cand-003 | Matches: A-110 text line 2, A-610 text line 1. Referenced layout/schedule unresolved; affected items remain under review. A-610 match is an unreadability notice, not schedule evidence. |
| temperature sensors / owner [terms: temperature sensors, owner, separate contract] | probe | excluded | cand-004 | Matches: M-110 text line 1. Sensors are owner work and excluded; search category does not determine CSI division. |
| thermostat / controls / DDC / BMS [terms: thermostat, controls, DDC, BMS] | probe | no_hits | none | No matches in supplied sheet text; does not establish absence on unreadable A-610 or unprovided PDF content. |
| A-610 schedule and A-110 referenced dimensioned layout | source | needs_followup | cand-002, cand-003 | No readable schedule rows or layout available. Prior OCR failure reported by input; no OCR-derived quotes used. Both dependent candidates remain under review. |
