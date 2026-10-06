# pdfcn rendering and design

Upstream: https://github.com/shadcn-labs/pdfcn
Tested registry revision: `39c75c1abbbad7b89ad1d8d3ea740ef635818a4b`.
The setup script installs pdfcn's Forme text/table components and their shared
utilities/theme from that revision. Components remain editable in the proposal
workspace, with the upstream MIT license. This is actual pdfcn component code,
not a lookalike HTML-to-PDF template. React 19.2.5, Forme 0.25.0 and tsx 4.21.0
are pinned in the generated package manifest; retain the generated lockfile.

Default direction: an editorial, quiet design.

- **Cover:** a full-bleed evergreen cover with the project in serif, the
  summary as a lead, and a four-column meta strip (prepared for, prepared by,
  RFP, issued) anchored to the foot.
- **Interior chrome:** a repeating header (proposer, client, RFP number) and
  footer (status, reference, date, page X / Y).
- **Sections:** each one opens on a new page with its tab label, a brass rule
  and a serif title, so the compliance check can find where it starts.
- **By kind:**
  - Projects and team render as cards with a field grid.
  - Narrative and schedule items render as grouped, numbered lists.
  - The fee leads with a dark lump-sum band, then a pdfcn table.
  - Forms render as a checklist, and the compliance matrix as a pdfcn table.

Design tokens live in the `c` object at the top of `render.tsx`: evergreen ink
`#163b35`, brass accent `#c39a4f`, pale tint `#f1f5f3`, hairline `#d8e0dc`.
Swap them for a supplied brand palette. Never invent a client's logo. Use
color for hierarchy only; keep body text dark on white for print contrast.
In `DRAFT` status every item prints its source line, and claims from prior
proposals that aren't confirmed print in rust with "confirm still true".
`FOR REVIEW` hides the source lines.
Leave room for uncertainty labels and commercial qualifications, not just sales
copy. Add project photography only when supplied or explicitly approved.

Forme details verified here:
- Page size is `Letter` (case-sensitive). Page margins use the `margin` prop;
  cover backgrounds and padding belong on a `View` inside the page.
- Built-in fonts: `Helvetica` and `Times`. The family `Times-Roman` (used by
  pdfcn's professional theme) silently falls back to Helvetica; use `Times`.
  Confirm faces with `pdffonts`. Register a supplied brand font with Forme's
  `Font.register` rather than substituting a lookalike.
- `Fixed position="header" | "footer"` repeats on every page and supports
  `{{pageNumber}}` / `{{totalPages}}`. Do not uppercase those placeholders.
- pdfcn's `Table` is View-based: its header does not repeat across pages. When
  a schedule spills, split it into page-sized tables, each with its heading.
  Section headings are kept with their first item via `wrap={false}`.
- The pdfcn professional theme is the default. A provider returning arrays or
  directly invoking Forme primitives can lose content in standalone serialization;
  the tested template uses the default theme and explicit component colors.
- Serialize using the same `@formepdf/react` instance that supplied the primitives,
  then pass its JSON to `renderPdf` from `@formepdf/core`.
- PDF metadata strings (title, author, subject) are written as PDFDocEncoding.
  Keep them ASCII; an em dash comes out as mojibake. `render.tsx` strips
  non-ASCII from them.
- `wrap={false}` cards that don't fit move whole to the next page. One card
  alone on a page is the most common awkward break: tighten the card, shorten
  the section lead, or drop the weakest entry, then re-render.
- A successful process exit alone is insufficient: verify nonzero PDF page count,
  extracted content and rasterized pages. Longer inputs require pagination review.

```bash
pdfinfo proposal.pdf
pdftotext -layout proposal.pdf proposal.txt
pdftoppm -scale-to 1400 -png proposal.pdf proposal-page
```

Review every generated PNG and the extracted text. The bundled source preview
shows the rendered fictional sample; it is not a substitute for inspecting the
user's final PDF. No client documents are uploaded to a rendering service.
