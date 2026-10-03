# pdfcn rendering and design

Upstream: https://github.com/shadcn-labs/pdfcn
Tested registry revision: `39c75c1abbbad7b89ad1d8d3ea740ef635818a4b`.
The setup script installs pdfcn's Forme text/table components and their shared
utilities/theme from that revision. Components remain editable in the proposal
workspace, with the upstream MIT license. This is actual pdfcn component code,
not a lookalike HTML-to-PDF template. React 19.2.5, Forme 0.25.0 and tsx 4.21.0
are pinned in the generated package manifest; retain the generated lockfile.

Default direction: deep evergreen cover, white interior, restrained pale-green
price summary, Helvetica body, clear size hierarchy and 44-point body margins.
Use a supplied brand palette/logo when available. Never invent a client's logo.
Leave room for uncertainty labels and commercial qualifications, not just sales
copy. Add project photography only when supplied or explicitly approved.

Forme details verified here:
- Page size is `Letter` (case-sensitive). Page margins use the `margin` prop;
  cover backgrounds and padding belong on a `View` inside the page.
- The pdfcn professional theme is the default. A provider returning arrays or
  directly invoking Forme primitives can lose content in standalone serialization;
  the tested template uses the default theme and explicit component colors.
- Serialize using the same `@formepdf/react` instance that supplied the primitives,
  then pass its JSON to `renderPdf` from `@formepdf/core`.
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
