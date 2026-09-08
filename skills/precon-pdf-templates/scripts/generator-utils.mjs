import { readFileSync, writeFileSync } from "node:fs";

// Keep integer cents exact, including deducts and values near JS's safe limit.
export function formatMoney(cents) {
  if (!Number.isSafeInteger(cents)) {
    throw new Error("Money must be supplied as safe integer cents; missing values are not zero.");
  }
  const magnitude = BigInt(cents < 0 ? -cents : cents);
  const dollars = (magnitude / 100n).toLocaleString("en-US");
  const fraction = String(magnitude % 100n).padStart(2, "0");
  return `${cents < 0 ? "-" : ""}$${dollars}.${fraction}`;
}

export function runGenerator(render) {
  const [inputPath, outputPath, flag, theme, ...extra] = process.argv.slice(2);
  try {
    if (!inputPath || !outputPath || extra.length ||
        (flag !== undefined && (flag !== "--theme" || !theme))) {
      throw new Error("Usage: node render.mjs input.json output.html [--theme theme-name]");
    }
    let html = render(JSON.parse(readFileSync(inputPath, "utf8")));
    if (theme) {
      if (!/^[a-z]+(?:-[a-z]+)*$/.test(theme)) throw new Error("Invalid theme name.");
      const css = readFileSync(new URL(`../themes/${theme}.css`, import.meta.url), "utf8");
      const root = css.match(/:root\s*\{[^}]*\}/)?.[0];
      if (!root) throw new Error("Theme must declare :root variables.");
      // Retain the generator's page/table geometry. Replace palette, not layout.
      html = html.replace(/:root\s*\{[^}]*\}/, root);
      if (theme !== "field-ready-technical") {
        html = html.replace("</style>", "h1, h2 { font-family: var(--font-display); }\n  </style>");
      }
    }
    writeFileSync(outputPath, html);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
