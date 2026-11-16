# Rendering and design

The PDF comes from one file, `templates/proposal.typ`, compiled by
[Typst](https://typst.app): a single binary with no packages to install and no
network access. It reads `proposal.json` from its own folder; pass
`--input data=other.json` to read another file in that folder. Tested with
Typst 0.15.1; it needs 0.13 or newer.

```bash
typst compile proposal.typ proposal.pdf
```

Default direction: an editorial, quiet design.

- **Cover:** a full-bleed evergreen cover with the project in large type, the
  summary as a lead, and a four-column meta strip (prepared for, prepared by,
  RFP, issued) anchored to the foot.
- **Interior chrome:** a repeating header (proposer, client, RFP number) and
  footer (status, reference, date, page X / Y, counting the cover).
- **Sections:** each one opens on a new page with its tab label, a brass rule
  and its title, so the compliance check can find where it starts.
- **By kind:**
  - Projects and team render as cards with a field grid.
  - Narrative and schedule items render as grouped, numbered lists.
  - The fee leads with a dark lump-sum band, then a table.
  - Forms render as a checklist, and the compliance matrix as a table.

Design tokens live in the `c` dictionary at the top of `proposal.typ`:
evergreen ink `#163b35`, brass accent `#c39a4f`, pale tint `#f1f5f3`, hairline
`#d8e0dc`. Swap them for a supplied brand palette. Never invent a client's
logo. Use color for hierarchy only; keep body text dark on white for print
contrast. In `DRAFT` status every item prints its source line, and claims from
prior proposals that aren't confirmed print in rust with "confirm still true".
`FOR REVIEW` hides the source lines. Leave room for uncertainty labels and
commercial qualifications, not just sales copy. Add project photography only
when supplied or explicitly approved, with Typst's `image()`.

Typst details that matter here:

- **Fonts.** The template uses Libertinus Serif, which ships inside Typst, so
  the PDF looks the same on every machine. For a supplied brand font, put the
  font files in a folder, compile with `--font-path that-folder`, and set
  `font` at the top of the template. Check the family name with
  `typst fonts --font-path that-folder`; Typst warns about an unknown family
  and falls back. Confirm the embedded faces with `pdffonts`.
- **Money.** The template formats integer cents itself. USD, EUR, GBP, CAD and
  AUD print with their symbol; other currencies print their ISO code. Add a
  symbol to the `money` function when a proposal needs one.
- **Tables** repeat their header row on every page they spill onto.
- **Keeping things together.** Cards, form rows and each list heading with its
  first item are `block(breakable: false)`, so they move whole to the next
  page. One card alone on a page is the most common awkward break: tighten the
  card, shorten the section lead, or drop the weakest entry, then re-render.
- **Text from the data** is inserted as plain strings, so `$`, `#` and `*` in
  proposal text print as written.
- A successful compile alone is insufficient: verify the page count, the
  extracted text and the rasterized pages. Longer inputs require pagination
  review.

```bash
pdfinfo proposal.pdf
pdftotext -layout proposal.pdf proposal.txt
pdftoppm -scale-to 1400 -png proposal.pdf proposal-page
```

Some Poppler versions print `Syntax Error: Suspects object is wrong type` for
Typst PDFs. It's harmless; the page count and text are read correctly.

Review every generated PNG and the extracted text. The bundled source preview
shows the rendered fictional sample; it is not a substitute for inspecting the
user's final PDF. No client documents are uploaded to a rendering service.
