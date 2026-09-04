#!/usr/bin/env node
// Swap the theme on a generated budget export.
//
// The budget generator inlines the field-ready-technical variables. The
// documented way to restyle a document with another bundled theme is to
// replace the `:root` block with the theme's own (themes/README.md), which
// recolors every rule because the template only uses var() references.
//
//   node apply-theme.mjs document.html warm-owner-facing.css

import { readFileSync, writeFileSync } from "node:fs";

const [htmlPath, cssPath] = process.argv.slice(2);
if (!htmlPath || !cssPath) {
  console.error("Usage: node apply-theme.mjs document.html theme.css");
  process.exit(1);
}

const css = readFileSync(cssPath, "utf8");
const themeRoot = css.match(/:root\s*\{[^}]*\}/);
if (!themeRoot) {
  console.error(`no :root block in ${cssPath}`);
  process.exit(1);
}

const vars = themeRoot[0]
  .replace(/^:root\s*\{/, "")
  .replace(/\}$/, "")
  .split(";")
  .map((line) => line.trim())
  .filter(Boolean)
  .join("; ");

const html = readFileSync(htmlPath, "utf8");
if (!/:root\s*\{[^}]*\}/.test(html)) {
  console.error(`no :root block in ${htmlPath}`);
  process.exit(1);
}

const themed = html
  .replace(/:root\s*\{[^}]*\}/, `:root { ${vars}; }`)
  .replace(
    /(h1 \{ color: var\(--primary\);)/,
    "h1, h2 { font-family: var(--font-display); }\n    $1",
  );

writeFileSync(htmlPath, themed);
