# Design review

Inspect the PDF as pages before
delivery, not just the HTML in a browser: page breaks, repeated table
headers, and print margins only show up in the PDF.

## Convert

Run from the working directory so flat sibling assets resolve. Use the
first converter that is installed:

```bash
# Headless Chrome / Chromium (binary may be chromium, chromium-browser, or chrome)
google-chrome --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=/path/to/job/document.pdf file:///path/to/job/document.html

# WeasyPrint
weasyprint document.html document.pdf
```

If the agent runtime exposes its own HTML-to-PDF capability, that is
equally acceptable. If nothing is available, deliver the HTML and tell the
user to open it in a browser and print to PDF with headers and footers off.

Chrome honors `page-break-after`, `break-inside: avoid`, and
`thead { display: table-header-group }`, which the templates rely on.
Converter support differs, especially for grid layouts in milestone and
proposal documents. Inspect the actual PDF; successful conversion alone is
not a layout check. Generators declare US Letter with 0.45-inch page margins.

## Render pages to images (optional)

Rendering pages to PNG lets you look at every page at once. Skip this step
if neither tool is installed and review the PDF directly instead.

```bash
# ImageMagick 7 (needs Ghostscript)
magick -density 150 document.pdf -background white -alpha remove -quality 90 page_%02d.png
# or ImageMagick 6
convert -density 150 document.pdf -background white -alpha remove -quality 90 page_%02d.png
# or poppler
pdftoppm -r 150 -png document.pdf page
```

Open each image and check it against the list below. Note the page count;
a one-page export that came out as three pages usually means a table
overflowed or a `min-height` pushed content onto a blank page.

## Review checklist

- Document family and theme match the user's request.
- No leftover sample text: search the HTML for "Owner Name",
  "Contractor Name", "Riverside", and any sample dollar amount or date.
- Theme is applied consistently across all pages; cover, headings, tables,
  callouts, and footers use one visual system.
- No orphaned headings at the bottom of a page.
- No clipped table columns; long descriptions wrap, numeric columns do not.
- Table headers repeat when a table spans pages.
- Totals and money values are right-aligned, legible, and match the source
  data exactly.
- Dense budget pages keep their hierarchy (division rows stand out from
  line items) rather than reading as a raw export.
- Folio and footer page numbers are sequential and correct.
- Source HTML and data file are saved next to the PDF for revisions.
- Family-specific checks in the generator's `qa.md` pass, where supplied.

## Required loop

Generate, convert, inspect, and list issues. Fix actual layout or transcription
errors, reconvert, and reinspect affected pages. Preserve source discrepancies
and report them instead of changing the figures. If no issues are found,
record that result without making a gratuitous change. If inspection cannot
run, identify the unverified parts in the delivery note.
