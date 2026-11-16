// Proposal PDF from proposal.json. Render with Typst (https://typst.app):
//
//   typst compile proposal.typ proposal.pdf
//
// Reads proposal.json next to this file, or another file in the same folder
// with --input data=other.json. Run scripts/check.mjs on the data: it validates
// it and names any problem, which this template does not.

#let d = json(sys.inputs.at("data", default: "proposal.json"))
#let m = d.meta

// Design tokens. Swap these for the proposer's brand when one is supplied.
#let c = (
  ink: rgb("#163b35"),
  sage: rgb("#a9c9bb"),
  brass: rgb("#c39a4f"),
  tint: rgb("#f1f5f3"),
  rule: rgb("#d8e0dc"),
  muted: rgb("#66736f"),
  body: rgb("#1f2624"),
  alert: rgb("#9a3412"),
)
// Libertinus Serif ships inside Typst, so the PDF looks the same on every machine.
// For a brand font, pass its folder with --font-path and name it here.
#let font = "Libertinus Serif"

#let status-label = if m.status == "DRAFT" { "Draft" } else { "For review" }
#let show-sources = m.status == "DRAFT"
#let two(n) = if n < 10 { "0" + str(n) } else { str(n) }
#let long-date(iso) = {
  let (y, mo, da) = iso.split("-").map(int)
  datetime(year: y, month: mo, day: da).display("[month repr:long] [day padding:none], [year]")
}
// Money is integer cents. Common currencies get their symbol, others their ISO code.
#let money(cents) = {
  let s = str(calc.quo(cents, 100))
  let groups = ()
  while s.len() > 3 {
    groups.insert(0, s.slice(s.len() - 3))
    s = s.slice(0, s.len() - 3)
  }
  groups.insert(0, s)
  let r = calc.rem(cents, 100)
  let symbol = (USD: "$", EUR: "€", GBP: "£", CAD: "CA$", AUD: "A$").at(m.currency, default: m.currency + " ")
  symbol + groups.join(",") + "." + if r < 10 { "0" } + str(r)
}
#let source-title(s) = {
  let src = d.sources.find(x => x.id == s.id)
  let name = if src == none { s.id } else { src.at("short", default: src.title) }
  name + if "page" in s { " p. " + str(s.page) }
}

// ---------- Type ----------
#let eyebrow(body, color: c.muted, size: 7.5pt) = text(size: size, tracking: 1.4pt, fill: color, upper(body))
#let display(body, size, color: c.ink) = text(size: size, fill: color, body)
#let strong-ink(body) = text(weight: "bold", fill: c.ink, body)

#let source-line(item) = if show-sources {
  let src = d.sources.find(s => s.id == item.source.id)
  let unconfirmed = src.kind == "prior" and not item.at("confirmed", default: false)
  let refs = (item.source,) + item.at("alsoFrom", default: ())
  v(5pt, weak: true)
  eyebrow(
    "Source · " + refs.map(source-title).join(" + ") + if unconfirmed { " · confirm still true" },
    color: if unconfirmed { c.alert } else { c.muted },
    size: 6.5pt,
  )
}

// ---------- Blocks ----------
#let group-heading(title) = block(
  width: 100%, inset: (bottom: 7pt), stroke: (bottom: 1pt + c.ink), below: 0pt,
  text(size: 11pt, weight: "bold", fill: c.ink, title),
)

#let numbered-list(items, title: none) = {
  let row(item, i) = block(
    breakable: false, width: 100%, inset: (y: 9pt), above: 0pt, below: 0pt,
    stroke: if i < items.len() - 1 { (bottom: 0.5pt + c.rule) },
    grid(
      columns: (34pt, 1fr),
      text(size: 8pt, weight: "bold", tracking: 0.6pt, fill: c.brass, two(i + 1)),
      pad(right: 16pt)[
        #if "title" in item [#strong-ink(item.title) \ ]
        #item.text
        #source-line(item)
      ],
    ),
  )
  block(below: 22pt, {
    // Keep the heading with its first item so it never strands at a page foot.
    block(breakable: false, below: 0pt, {
      if title != none { group-heading(title) }
      row(items.at(0), 0)
    })
    for (i, item) in items.enumerate().slice(1) { row(item, i) }
  })
}

#let groups(items) = {
  let out = ()
  for item in items {
    let g = item.at("group", default: none)
    if out.len() > 0 and out.last().title == g { out.last().items.push(item) } else { out.push((title: g, items: (item,))) }
  }
  out
}

// Short values sit four to a row; a long value takes a row of its own.
#let fields(f) = {
  let cells = ()
  let col = 0
  for (k, v) in f.pairs() {
    let cell = [#eyebrow(k, size: 6.5pt) \ #text(size: 9pt, v)]
    if v.len() > 30 {
      if col > 0 { cells += ([],) * (4 - col) }
      cells.push(grid.cell(colspan: 4, cell))
      col = 0
    } else {
      cells.push(cell)
      col = calc.rem(col + 1, 4)
    }
  }
  grid(columns: (1fr,) * 4, column-gutter: 10pt, row-gutter: 6pt, ..cells)
}

#let card(item) = block(breakable: false, width: 100%, stroke: (top: 1pt + c.ink), inset: (top: 8pt), below: 14pt)[
  #display(item.at("title", default: ""), 15pt)
  #if "fields" in item { block(above: 8pt, below: 8pt, fields(item.fields)) }
  #text(size: 9.5pt, item.text)
  #source-line(item)
]

#let letter(items) = {
  for item in items {
    block(below: 14pt)[#text(size: 10.5pt, item.text) #source-line(item)]
  }
  block(breakable: false, above: 28pt, width: 240pt)[
    #v(34pt)
    #line(length: 100%, stroke: 0.75pt + c.body)
    #text(size: 9pt, fill: c.muted)[Signature not applied · #lower(status-label) for #m.proposer]
  ]
}

#let hairlines(x, y) = (bottom: if y == 0 { 1pt + c.ink } else { 0.5pt + c.rule })

#let fee() = {
  if d.fee.status == "unpriced" {
    return block(breakable: false, width: 100%, fill: c.tint, stroke: (left: 3pt + c.alert), inset: 20pt)[
      #eyebrow("Unpriced draft", color: c.alert) \
      Fee not yet supplied. #d.fee.note
    ]
  }
  block(breakable: false, width: 100%, fill: c.ink, inset: (x: 24pt, y: 22pt), below: 20pt, grid(
    columns: (1fr, auto), align: (left + bottom, right + bottom),
    box(width: 250pt)[
      #eyebrow("Lump-sum total", color: c.brass) \
      #text(size: 8.5pt, fill: c.sage)[Preconstruction fee and general conditions. Percentage fees apply to the Cost of the Work and are listed below.]
    ],
    display(money(d.fee.totalCents), 30pt, color: white),
  ))
  table(
    columns: (34pt, 1fr, 150pt), stroke: hairlines, inset: (x: 0pt, y: 8pt), align: (left, left, right),
    table.header([], eyebrow("Fee component", color: c.ink), eyebrow("Amount (" + m.currency + ")", color: c.ink)),
    ..d.fee.lines.enumerate().map(((i, l)) => (
      text(size: 8pt, weight: "bold", fill: c.brass, two(i + 1)),
      [
        #strong-ink(l.label + if l.at("option", default: false) { " (option, not in total)" })
        #if "note" in l [\ #text(size: 8.5pt, fill: c.muted, l.note)]
        #if show-sources [\ #eyebrow("Source · " + source-title(l.source), size: 6.5pt)]
      ],
      if l.basis == "lump" { money(l.cents) } else { str(l.percent) + "%" + if "of" in l { " of " + l.of } },
    )).flatten(),
  )
}

#let forms() = for f in d.rfp.forms {
  block(breakable: false, width: 100%, inset: (y: 10pt), above: 0pt, below: 0pt, stroke: (bottom: 0.5pt + c.rule), grid(
    columns: (34pt, 1fr),
    pad(top: 2pt, box(width: 9pt, height: 9pt, stroke: 0.75pt + if f.included { c.ink } else { c.alert }, fill: if f.included { c.ink } else { white })),
    [
      #strong-ink(f.name) \
      #text(size: 9pt, fill: if f.included { c.muted } else { c.alert })[#if f.included [Completed form follows.] else [Required and not yet completed.]]
    ],
  ))
}

#let matrix() = table(
  columns: (44pt, 1fr, 158pt), stroke: hairlines, inset: (x, y) => (left: if x == 2 { 8pt } else { 0pt }, y: 8pt),
  table.header(eyebrow("Item", color: c.ink), eyebrow("RFP requirement", color: c.ink), eyebrow("Where we answer it", color: c.ink)),
  ..d.rfp.requirements.map(r => {
    let answered = d.sections.filter(s => r.id in s.at("answers", default: ()))
    (
      text(size: 8.5pt, weight: "bold", fill: c.ink, r.id),
      text(size: 9pt, r.text),
      if answered.len() == 0 { text(size: 9pt, fill: c.alert)[Not yet answered] } else {
        text(size: 9pt, answered.map(s => if "tab" in s { s.tab + ": " } + s.title).join("; "))
      },
    )
  }).flatten(),
)

#let chapter(s, index) = {
  let items = s.at("items", default: ())
  // Each section opens on a new page with its title, so the check can find where it starts.
  pagebreak(weak: true)
  block(breakable: false, below: 24pt)[
    #text(size: 8pt, weight: "bold", tracking: 1.4pt, fill: c.brass, upper(s.at("tab", default: two(index + 1))))
    #h(6pt) #box(line(length: 22pt, stroke: 0.75pt + c.brass), baseline: -2.5pt) #h(6pt)
    #eyebrow(m.project)
    #block(above: 18pt, below: 0pt, display(s.title, 28pt))
    #if "lead" in s { block(above: 16pt, width: 420pt, text(size: 11pt, fill: c.muted, s.lead)) }
  ]
  if s.kind == "letter" { letter(items) }
  else if s.kind in ("projects", "team") { for item in items { card(item) } }
  else if s.kind == "fee" { fee() }
  else if s.kind == "forms" { forms() }
  else if s.kind == "matrix" { matrix() }
  else { for g in groups(items) { numbered-list(g.items, title: g.title) } }
  if s.kind == "fee" and items.len() > 0 { v(22pt); numbered-list(items, title: "Fee basis") }
}

// ---------- Document ----------
#set document(title: m.project + " - Proposal " + m.reference, author: m.proposer, description: "Proposal to " + m.client)
#set text(font: font, size: 10pt, fill: c.body, lang: "en")
#set par(leading: 0.62em, spacing: 0.9em)
#set page(paper: "us-letter")

// Cover
#page(fill: c.ink, margin: (x: 56pt, top: 52pt, bottom: 48pt), grid(
  rows: (auto, 1fr, auto), columns: 100%,
  grid(
    columns: (1fr, auto), align: horizon,
    text(size: 9pt, weight: "bold", tracking: 2.2pt, fill: white, upper(m.proposer)),
    box(stroke: 0.75pt + c.brass, inset: (x: 8pt, y: 4pt), eyebrow(status-label, color: c.brass)),
  ),
  align(horizon, pad(top: 120pt)[
    #box(width: 36pt, height: 2pt, fill: c.brass)
    #v(16pt)
    #eyebrow(m.at("kicker", default: "Proposal"), color: c.sage)
    #v(10pt)
    #block(width: 480pt, par(leading: 0.3em, display(m.project, 46pt, color: white)))
    #if "summary" in m { block(above: 26pt, width: 410pt, par(leading: 0.75em, text(size: 12.5pt, fill: c.sage, m.summary))) }
  ]),
  [
    #block(width: 100%, stroke: (top: 0.75pt + rgb("#3e625b")), inset: (top: 16pt), grid(
      columns: (1fr,) * 4, column-gutter: 12pt,
      ..(
        ("Prepared for", m.client),
        ("Prepared by", m.proposer),
        ("In response to", d.rfp.at("number", default: d.rfp.title)),
        ("Issued", long-date(m.date)),
      ).map(((label, value)) => [#eyebrow(label, color: c.sage) \ #text(size: 9.5pt, fill: white, value)]),
    ))
    #v(18pt)
    #text(size: 7.5pt, fill: c.sage)[#if m.status == "DRAFT" [Draft for internal review. Not for submission.] else [For internal review before submission.]]
  ],
))

// Interior pages. Page numbers count the cover, so they match the PDF viewer.
#set page(
  margin: (x: 56pt, top: 92pt, bottom: 64pt),
  header: block(width: 100%, inset: (bottom: 8pt), stroke: (bottom: 0.5pt + c.rule), grid(
    columns: (1fr, auto),
    text(size: 7.5pt, weight: "bold", tracking: 1.6pt, fill: c.ink, upper(m.proposer)),
    eyebrow(m.client + " · " + d.rfp.at("number", default: m.reference)),
  )),
  footer: grid(
    columns: (1fr, auto),
    eyebrow(status-label + " · " + m.reference + " · " + long-date(m.date)),
    context text(size: 7.5pt, tracking: 1.4pt, fill: c.ink)[#counter(page).display() / #counter(page).final().first()],
  ),
)
#for (i, s) in d.sections.enumerate() { chapter(s, i) }
