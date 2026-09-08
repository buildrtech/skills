# Themes

Generators accept a bundled theme name directly:

```bash
node templates/construction-budget-export/field-ready-technical/render.mjs /path/to/job/data.json /path/to/job/document.html --theme warm-owner-facing
```

Omit `--theme` for Field-Ready Technical. The option replaces the palette
variables and uses the selected display font for headings, preserving table
geometry and print rules. It inlines everything; no CSS copy is needed.
Supported names are the eight `.css` basenames in this folder. Swiss Transit
Technical is a blueprint only and has no standalone stylesheet.

For blueprints, work on a copy outside the package. Preserve layout rules
when changing visual styles. The short Architectural Ink and Executive Dark
blueprints use `--primary`, `--surface`, `--font-body`, and related variables;
the longer proposal blueprints also use `--paper`, `--line`, `--quiet`, and
hardcoded cover colors/fonts. These are not interchangeable stylesheets:
map those rules to the selected theme and inspect every page, especially
cover contrast, table headers, and footer positions.

If using external CSS, save it beside the HTML and link its bare filename
after existing styles so overrides apply. Unlinked CSS has no effect.
User-provided branding replaces theme colors/fonts; do not guess brand assets.
