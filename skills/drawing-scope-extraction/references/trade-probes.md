# Trade probes

A probe is a term searched across the extracted text of every sheet after
the sheets have been read. Probes raise recall; they do not replace reading
the general notes, keyed notes, schedules, and legends on each sheet. A
probe with no hits is a finding to record in the coverage ledger, not a
reason to invent scope.

## How to run probes

Extract each sheet's text to its own file (for example
`sheet-text/A-101.txt`), then search all of them at once with a
case-insensitive match and line numbers so each hit can be traced back to a
sheet and a note:

```bash
grep -i -n "casework" sheet-text/*.txt
```

Search the drawing's abbreviations as well as the plain term. Common ones:
GWB or GYP (gypsum board), ACT (acoustical ceiling tile), VCT, LVT, CPT
(flooring), RB (rubber base), FRP (fiberglass reinforced panels), HM (hollow
metal), SC (solid core), PLAM or PL (plastic laminate), SS (stainless steel
or solid surface, check context), VAV, FA (fire alarm), EM (emergency),
NIC (not in contract), OFCI and OFOI (owner-furnished), VIF (verify in
field), TYP (typical), UNO (unless noted otherwise).

On OCR text, expect broken words and dropped characters. Probe shorter
fragments (`sprink`, `firestop`) and read the surrounding lines.

## First-pass probes for a whole set

Run all twenty on every set. For a single-discipline or single-sheet request,
drop the probes that cannot apply and add terms specific to the target.

| Probe | Usual divisions | What it usually surfaces | Also try |
|---|---|---|---|
| demolition | 02 | Keyed demolition notes, salvage and turnover instructions, items to remain and protect | remove, existing to remain, salvage, relocate |
| concrete | 03, 09 | Slab infill, housekeeping pads, core drilling, floor prep and leveling, curbs | slab, pad, patch, level, core drill |
| blocking | 06 | Backing for casework, accessories, TV mounts, grab bars, handrails; general-note blanket requirements | backing, nailer, plywood, in-wall support |
| casework | 06, 12 | Base and upper cabinets, millwork, reception desks, countertops, shelving | millwork, cabinet, countertop, shelving, plam |
| firestopping | 07 | Penetrations through rated assemblies, head-of-wall, rated partition notes | firestop, fire-rated, rated, UL, penetration |
| sealant | 07 | Joint sealants, acoustical sealant at partition tracks, caulking at fixtures and countertops | caulk, acoustical seal, joint |
| roofing | 07 | Roof patching at new penetrations, curbs, walkway pads, flashing; usually empty on interior work | roof, flashing, curb, membrane |
| door hardware | 08 | Hardware sets, keying, closers, electrified hardware, hold-opens | hardware set, HW, lockset, closer, cylinder, keyed |
| access panels | 08 | Access doors in gypsum ceilings and shafts for valves, dampers, and cleanouts | access door, AP, ceiling access |
| glazing | 08 | Sidelites, borrowed lites, storefront, glass doors, mirrors, film | glass, tempered, storefront, sidelite, mirror, film |
| gypsum board | 09 | Partition types, soffits, furring, shaft walls, ceiling assemblies | GWB, gyp, partition type, stud, furring, soffit |
| acoustical ceiling | 09 | Ceiling tile and grid types, ceiling heights, areas of new versus existing grid | ACT, ceiling tile, grid, lay-in, ceiling height |
| resilient flooring | 09 | LVT, VCT, sheet vinyl, rubber base, transitions, floor prep; carpet and tile appear nearby in the same schedule | LVT, VCT, base, RB, carpet, CPT, tile, transition |
| painting | 09 | Paint codes, substrates to paint, frames and doors to paint, existing surfaces to repaint | paint, PT, finish, coating, stain |
| toilet accessories | 10 | Accessory schedules, grab bars, dispensers, mirrors; general blocking notes name them even when no restroom is in scope | grab bar, dispenser, accessory, TA |
| wall protection | 10 | Corner guards, crash rails, FRP, wainscot panels | corner guard, FRP, crash rail, wainscot |
| sprinkler | 21 | Head relocation or add notes, fire protection sheets, deferred submittal notes; silence on a set with new full-height walls or ceiling changes is an RFI | fire protection, FP, head, sprink |
| plumbing fixtures | 22 | Fixture schedules, sinks, water heaters, rough-in and reconnection notes, cap and abandon notes | sink, faucet, fixture, rough-in, cap, waste, vent, water heater |
| HVAC | 23 | Diffusers and grilles, VAV boxes, exhaust fans, thermostats, test and balance, duct modifications | diffuser, grille, VAV, exhaust, thermostat, duct, T&B, balance |
| electrical | 26, 27, 28 | Fixture schedules, lighting controls, receptacles, circuits, panel schedules, fire alarm, data, access control | fixture, lighting, receptacle, circuit, panel, sensor, dimmer, fire alarm, data, access control |

## Follow-up probes

Issue follow-ups when the first pass surfaces a named system or leaves a
concrete gap. A first-pass hit for a broad term does not close the more
specific schedule, finish, accessory, or system gaps under it. Typical
second-pass terms:

- countertop, millwork, shelving, reception
- caulk, acoustical sealant, backer rod
- access door, ceiling access
- storefront, mirror, film, borrowed lite
- coating, epoxy, sealer, stain
- corner guard, crash rail, FRP
- lighting control, occupancy sensor, dimmer, emergency, exit sign
- receptacle, power, circuit, panel, disconnect
- fire alarm, strobe, horn, pull station, smoke detector
- thermostat, controls, DDC, BMS
- water heater, floor drain, cleanout, backflow
- signage, room sign, code sign
- window treatment, shade, blind
- appliance, refrigerator, dishwasher, microwave

Record every follow-up probe in the coverage ledger the same way as the
first-pass probes, including the ones that found nothing.
