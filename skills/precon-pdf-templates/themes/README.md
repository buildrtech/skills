# Themes

Standalone stylesheets for the templates in this skill. Every template
already inlines its theme in a `<style>` block, so these files are for two
cases: building a document from scratch, or restyling a blueprint with a
different theme.

To use one, copy its contents into the document's `<style>` block, or save
it as a flat sibling file next to the HTML and link it by bare filename:

```html
<link rel="stylesheet" href="field-ready-technical.css">
```

Do not reference a theme through a nested or absolute path from generated
HTML. PDF converters resolve assets relative to the HTML file, and the
working directory should hold every asset as a flat sibling.

Each theme defines the same variables (`--ink`, `--muted`, `--primary`,
`--accent`, `--surface`, `--border`, `--font-body`, `--font-display`), so
swapping themes on a blueprint usually means replacing the `:root` block
and adjusting a few component rules. Brand colors and fonts supplied by
the user go into those variables; do not guess them.

See `references/template-catalog.md` for what each theme looks like and
which template it pairs with.
