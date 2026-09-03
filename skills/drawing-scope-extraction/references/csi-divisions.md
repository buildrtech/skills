# CSI MasterFormat divisions

MasterFormat 2018 division numbers and names as general contractors use them
to organize scope lists, bid packages, and cost codes. Assign every candidate
one of these two-digit divisions. Reserved divisions exist in the numbering
but carry no work; do not assign candidates to them.

## Divisions 00 to 49

| Division | Name | Group |
|---|---|---|
| 00 | Procurement and Contracting Requirements | Procurement and contracting |
| 01 | General Requirements | General requirements |
| 02 | Existing Conditions | Facility construction |
| 03 | Concrete | Facility construction |
| 04 | Masonry | Facility construction |
| 05 | Metals | Facility construction |
| 06 | Wood, Plastics, and Composites | Facility construction |
| 07 | Thermal and Moisture Protection | Facility construction |
| 08 | Openings | Facility construction |
| 09 | Finishes | Facility construction |
| 10 | Specialties | Facility construction |
| 11 | Equipment | Facility construction |
| 12 | Furnishings | Facility construction |
| 13 | Special Construction | Facility construction |
| 14 | Conveying Equipment | Facility construction |
| 15 to 19 | Reserved | Facility construction |
| 20 | Reserved | Facility services |
| 21 | Fire Suppression | Facility services |
| 22 | Plumbing | Facility services |
| 23 | Heating, Ventilating, and Air Conditioning (HVAC) | Facility services |
| 24 | Reserved | Facility services |
| 25 | Integrated Automation | Facility services |
| 26 | Electrical | Facility services |
| 27 | Communications | Facility services |
| 28 | Electronic Safety and Security | Facility services |
| 29 | Reserved | Facility services |
| 30 | Reserved | Site and infrastructure |
| 31 | Earthwork | Site and infrastructure |
| 32 | Exterior Improvements | Site and infrastructure |
| 33 | Utilities | Site and infrastructure |
| 34 | Transportation | Site and infrastructure |
| 35 | Waterway and Marine Construction | Site and infrastructure |
| 36 to 39 | Reserved | Site and infrastructure |
| 40 | Process Interconnections | Process equipment |
| 41 | Material Processing and Handling Equipment | Process equipment |
| 42 | Process Heating, Cooling, and Drying Equipment | Process equipment |
| 43 | Process Gas and Liquid Handling, Purification, and Storage Equipment | Process equipment |
| 44 | Pollution and Waste Control Equipment | Process equipment |
| 45 | Industry-Specific Manufacturing Equipment | Process equipment |
| 46 | Water and Wastewater Equipment | Process equipment |
| 47 | Reserved | Process equipment |
| 48 | Electrical Power Generation | Process equipment |
| 49 | Reserved | Process equipment |

## Placement calls that come up on most commercial sets

The drawings decide the division, not the trade that usually installs it.
When a call is a judgment, say so in the candidate's `reason`.

| Work shown on the drawings | Division | Note |
|---|---|---|
| Selective demolition, removal of partitions, ceilings, flooring, casework | 02 | 02 41 19. Electrical and mechanical demolition may instead be carried in 26 or 23 when the electrical or mechanical sheets assign the removal to that trade; record which sheet assigned it. |
| Temporary partitions, dust control, protection of existing finishes, patching damage from demolition | 01 | 01 50 00 temporary facilities and 01 73 29 cutting and patching. |
| Slab preparation, floor leveling, moisture mitigation for new flooring | 09 | 09 05 61 common work results for flooring preparation. Structural slab repair or new slab is 03. |
| Wood blocking, backing, and nailers, even when they support Division 08, 09, 10, or 12 items | 06 | 06 10 53 miscellaneous rough carpentry. This is the standard example of the first-two-digit check: blocking behind a Division 09 partition is still Division 06. |
| Plastic laminate and wood casework | 06 | 06 41 00 architectural wood casework. |
| Solid surface, quartz, or stone countertops | 06 or 12 | MasterFormat lists countertops at 12 36 00. Many contractors carry them with casework in 06. Follow the user's cost code list if one is provided and record the choice. |
| Firestopping, joint sealants, acoustical sealant | 07 | 07 84 00 and 07 92 00. Sealant at partitions belongs here even though the drywall trade often installs it. |
| Sound attenuation batts inside partitions | 07 or 09 | 07 21 16 thermal insulation, or merged into the 09 21 16 gypsum board assembly when the partition type names it as part of the assembly. Record which. |
| Doors, frames, hardware, sidelites, storefront, glazing, access doors | 08 | Access doors and panels are 08 31 00 regardless of which trade's ceiling they sit in. |
| Metal stud and gypsum board partitions, ceilings, flooring, tile, base, acoustical ceilings, painting | 09 | One candidate per partition type, ceiling type, and finish code. |
| Toilet accessories, fire extinguishers and cabinets, corner guards, wall protection, signage, lockers | 10 | |
| Appliances, food service equipment, projection screens | 11 | Tenant-furnished equipment is an exclusion, not a candidate. |
| Window treatments, furniture, systems furniture, entrance mats | 12 | Furniture is usually by the tenant; record as an exclusion when the drawings say NIC. |
| Sprinkler heads, piping, relocation | 21 | |
| Plumbing fixtures, rough-in, water heaters | 22 | |
| Ductwork, diffusers, VAV boxes, exhaust fans, thermostats, test and balance | 23 | |
| Building automation and DDC connections | 25 | Frequently by the building's controls vendor; then it is `by_others`. |
| Lighting, power, receptacles, branch circuits, electrical demolition assigned to the electrical sheets | 26 | Lighting controls (sensors, dimmers) stay in 26 unless a 25 or 27 sheet claims them. |
| Data, telephone, audiovisual cabling | 27 | |
| Fire alarm devices, access control, security cameras | 28 | Base building fire alarm vendors and tenant access control vendors are common `by_others` cases. |

## Division versus cost code sanity check

When the user supplies a cost code list and asks for a mapping, check that
the first two digits of the chosen cost code match the candidate's division
before finalizing. If they do not, either the division on the candidate is
wrong or the cost code is; search the list again with the division and the
scope name. Use a cross-division code only when the drawings genuinely put
the work in that other division, and write the reason on the candidate.

Cost code lists that are not CSI-based (for example, a company's own
numbering) cannot be checked this way. Say so, map on scope name alone, and
mark every mapping as needing the estimator's confirmation.
