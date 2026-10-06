import React from "react";
import { readFile, writeFile } from "node:fs/promises";
import { Document, Fixed, Page, View, serialize } from "@formepdf/react";
import { renderPdf } from "@formepdf/core";
import { Text } from "@/components/pdf/text/text";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/components/pdf/table/table";
import { analyze, money as fmtMoney, validate } from "./proposal-core.mjs";

const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error("Usage: npm run render -- proposal.json proposal.pdf");
const d = validate(JSON.parse(await readFile(input, "utf8")));
const m = d.meta;
const compliance = analyze(d);

// Design tokens. Swap these for the proposer's brand when one is supplied.
const c = {
  ink: "#163b35",
  sage: "#a9c9bb",
  brass: "#c39a4f",
  tint: "#f1f5f3",
  rule: "#d8e0dc",
  muted: "#66736f",
  body: "#1f2624",
  white: "#ffffff",
  alert: "#9a3412",
};
const serif = "Times"; // Forme's built-in serif; "Times-Roman" silently falls back to Helvetica
const sans = "Helvetica";
const W = 612;
const H = 792;
const M = 56;
const CW = W - 2 * M;

type Source = { id: string; page?: number; section?: string };
type Item = { text: string; source: Source; alsoFrom?: Source[]; title?: string; group?: string; fields?: Record<string, string>; facts?: string[]; confirmed?: boolean };
type Section = { id: string; title: string; kind: string; tab?: string; lead?: string; answers?: string[]; items?: Item[] };

const money = (cents: number) => fmtMoney(cents, m.currency);
const longDate = (iso: string) =>
  new Date(`${iso}T12:00:00Z`).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
const two = (n: number) => String(n).padStart(2, "0");
const statusLabel = m.status === "DRAFT" ? "Draft" : "For review";
const showSources = m.status === "DRAFT";
const sourceTitle = (s: Source) => {
  const src = d.sources.find((x: any) => x.id === s.id);
  return `${src?.short ?? src?.title ?? s.id}${s.page ? ` p. ${s.page}` : ""}`;
};

// ---------- Typographic primitives (all pdfcn Text) ----------
const Eyebrow = ({ children, color = c.muted, style = {} }: any) => (
  <Text noMargin color={color} style={{ fontFamily: sans, fontSize: 7.5, letterSpacing: 1.4, lineHeight: 1.3, ...style }}>
    {String(children).toUpperCase()}
  </Text>
);
const Body = ({ children, color = c.body, size = 10, style = {} }: any) => (
  <Text noMargin color={color} style={{ fontFamily: sans, fontSize: size, lineHeight: 1.55, ...style }}>
    {children}
  </Text>
);
const Display = ({ children, size, color = c.ink, style = {} }: any) => (
  <Text noMargin color={color} style={{ fontFamily: serif, fontSize: size, lineHeight: 1.12, ...style }}>
    {children}
  </Text>
);
const SourceLine = ({ item }: { item: Item }) => {
  if (!showSources) return null;
  const unconfirmed = d.sources.find((s: any) => s.id === item.source.id)?.kind === "prior" && !item.confirmed;
  return (
    <Eyebrow color={unconfirmed ? c.alert : c.muted} style={{ marginTop: 4, fontSize: 6.5 }}>
      {`Source · ${[item.source, ...(item.alsoFrom ?? [])].map(sourceTitle).join(" + ")}${unconfirmed ? " · confirm still true" : ""}`}
    </Eyebrow>
  );
};

// ---------- Blocks ----------
const Heading = ({ children }: any) => (
  <View style={{ paddingBottom: 7, borderBottomWidth: 1, borderBottomColor: c.ink }}>
    <Text noMargin color={c.ink} style={{ fontFamily: sans, fontSize: 11, fontWeight: 700, lineHeight: 1.3 }}>
      {children}
    </Text>
  </View>
);

const NumberedList = ({ title, items }: { title?: string; items: Item[] }) => {
  const row = (item: Item, i: number) => (
    <View key={i} wrap={false} style={{ flexDirection: "row", paddingVertical: 9, borderBottomWidth: i === items.length - 1 ? 0 : 0.5, borderBottomColor: c.rule }}>
      <View style={{ width: 34, paddingTop: 2 }}>
        <Text noMargin color={c.brass} style={{ fontFamily: sans, fontSize: 8, fontWeight: 700, letterSpacing: 0.6 }}>
          {two(i + 1)}
        </Text>
      </View>
      <View style={{ width: CW - 34, paddingRight: 16 }}>
        {item.title ? <Body style={{ fontWeight: 700, color: c.ink }}>{item.title}</Body> : null}
        <Body>{item.text}</Body>
        <SourceLine item={item} />
      </View>
    </View>
  );
  return (
    <View style={{ marginBottom: 22 }}>
      {/* Keep the heading with its first item so it never strands at a page foot. */}
      <View wrap={false}>
        {title ? <Heading>{title}</Heading> : null}
        {row(items[0], 0)}
      </View>
      {items.slice(1).map((item, i) => row(item, i + 1))}
    </View>
  );
};

const groups = (items: Item[]) => {
  const out: { title?: string; items: Item[] }[] = [];
  for (const item of items) {
    const last = out[out.length - 1];
    if (last && last.title === item.group) last.items.push(item);
    else out.push({ title: item.group, items: [item] });
  }
  return out;
};

const Fields = ({ fields }: { fields: Record<string, string> }) => (
  <View style={{ flexDirection: "row", flexWrap: "wrap", marginTop: 6, marginBottom: 2 }}>
    {Object.entries(fields).map(([k, v]) => (
      <View key={k} style={{ width: v.length > 30 ? CW : CW / 4, paddingRight: 10, marginBottom: 5 }}>
        <Eyebrow style={{ fontSize: 6.5, marginBottom: 2 }}>{k}</Eyebrow>
        <Body size={9} style={{ lineHeight: 1.35 }}>
          {v}
        </Body>
      </View>
    ))}
  </View>
);

const Card = ({ item }: { item: Item }) => (
  <View wrap={false} style={{ borderTopWidth: 1, borderTopColor: c.ink, paddingTop: 8, marginBottom: 12 }}>
    <Display size={15}>{item.title ?? ""}</Display>
    {item.fields ? <Fields fields={item.fields} /> : null}
    <Body size={9.5}>{item.text}</Body>
    <SourceLine item={item} />
  </View>
);

const Letter = ({ items }: { items: Item[] }) => (
  <View>
    {items.map((item, i) => (
      <View key={i} style={{ marginBottom: 12 }}>
        <Body size={10.5}>{item.text}</Body>
        <SourceLine item={item} />
      </View>
    ))}
    <View wrap={false} style={{ marginTop: 28, width: 240 }}>
      <View style={{ height: 34, borderBottomWidth: 0.75, borderBottomColor: c.body }} />
      <Body size={9} color={c.muted} style={{ marginTop: 6 }}>
        {`Signature not applied · ${statusLabel.toLowerCase()} for ${m.proposer}`}
      </Body>
    </View>
  </View>
);

const cell = (text: string, extra: any = {}) => (
  <Text noMargin color={c.body} style={{ fontFamily: sans, fontSize: 9.5, lineHeight: 1.4, ...extra }}>
    {text}
  </Text>
);

const Fee = () => {
  if (d.fee.status === "unpriced")
    return (
      <View wrap={false} style={{ backgroundColor: c.tint, borderLeftWidth: 3, borderLeftColor: c.alert, padding: 20 }}>
        <Eyebrow color={c.alert} style={{ marginBottom: 6 }}>
          Unpriced draft
        </Eyebrow>
        <Body>{`Fee not yet supplied. ${d.fee.note}`}</Body>
      </View>
    );
  const lines = d.fee.lines;
  return (
    <View>
      <View wrap={false} style={{ backgroundColor: c.ink, paddingVertical: 22, paddingHorizontal: 24, flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 20 }}>
        <View style={{ maxWidth: 250 }}>
          <Eyebrow color={c.brass} style={{ marginBottom: 6 }}>
            Lump-sum total
          </Eyebrow>
          <Body size={8.5} color={c.sage}>
            Preconstruction fee and general conditions. Percentage fees apply to the Cost of the Work and are listed below.
          </Body>
        </View>
        <Display size={30} color={c.white} style={{ textAlign: "right" }}>
          {money(d.fee.totalCents)}
        </Display>
      </View>
      <Table variant="line">
        <TableHeader>
          <TableRow header style={{ borderBottomWidth: 1, borderBottomColor: c.ink }}>
            <TableCell width={34} style={{ paddingLeft: 0 }}>{""}</TableCell>
            <TableCell>
              <Eyebrow color={c.ink}>Fee component</Eyebrow>
            </TableCell>
            <TableCell width={150} align="right" style={{ paddingRight: 0 }}>
              <Eyebrow color={c.ink} style={{ textAlign: "right" }}>{`Amount (${m.currency})`}</Eyebrow>
            </TableCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {lines.map((l: any, i: number) => (
            <TableRow key={l.id} style={{ borderBottomColor: c.rule }}>
              <TableCell width={34} style={{ paddingLeft: 0, justifyContent: "flex-start" }}>
                {cell(two(i + 1), { color: c.brass, fontSize: 8, fontWeight: 700, paddingTop: 1 })}
              </TableCell>
              <TableCell style={{ justifyContent: "flex-start" }}>
                {cell(`${l.label}${l.option ? " (option, not in total)" : ""}`, { fontWeight: 700, color: c.ink })}
                {l.note ? cell(l.note, { fontSize: 8.5, color: c.muted, marginTop: 2 }) : null}
                {showSources ? <Eyebrow style={{ marginTop: 3, fontSize: 6.5 }}>{`Source · ${sourceTitle(l.source)}`}</Eyebrow> : null}
              </TableCell>
              <TableCell width={150} align="right" style={{ paddingRight: 0, justifyContent: "flex-start" }}>
                {cell(l.basis === "lump" ? money(l.cents) : `${l.percent}%${l.of ? ` of ${l.of}` : ""}`, { textAlign: "right" })}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </View>
  );
};

const Forms = () => (
  <View>
    {d.rfp.forms.map((f: any, i: number) => (
      <View key={f.id} wrap={false} style={{ flexDirection: "row", paddingVertical: 10, borderBottomWidth: 0.5, borderBottomColor: c.rule }}>
        <View style={{ width: 34, paddingTop: 2 }}>
          <View style={{ width: 9, height: 9, borderWidth: 0.75, borderColor: f.included ? c.ink : c.alert, backgroundColor: f.included ? c.ink : c.white }} />
        </View>
        <View style={{ width: CW - 34 }}>
          <Body style={{ fontWeight: 700, color: c.ink }}>{f.name}</Body>
          <Body size={9} color={f.included ? c.muted : c.alert}>
            {f.included ? "Completed form follows." : "Required and not yet completed."}
          </Body>
        </View>
      </View>
    ))}
  </View>
);

const Matrix = () => (
  <Table variant="line">
    <TableHeader>
      <TableRow header style={{ borderBottomWidth: 1, borderBottomColor: c.ink }}>
        <TableCell width={44} style={{ paddingLeft: 0 }}>
          <Eyebrow color={c.ink}>Item</Eyebrow>
        </TableCell>
        <TableCell>
          <Eyebrow color={c.ink}>RFP requirement</Eyebrow>
        </TableCell>
        <TableCell width={150} style={{ paddingRight: 0 }}>
          <Eyebrow color={c.ink}>Where we answer it</Eyebrow>
        </TableCell>
      </TableRow>
    </TableHeader>
    <TableBody>
      {compliance.matrix.map((x: any) => (
        <TableRow key={x.req.id} style={{ borderBottomColor: c.rule }}>
          <TableCell width={44} style={{ paddingLeft: 0, justifyContent: "flex-start" }}>
            {cell(x.req.id, { fontWeight: 700, color: c.ink, fontSize: 8.5 })}
          </TableCell>
          <TableCell style={{ justifyContent: "flex-start" }}>{cell(x.req.text, { fontSize: 9 })}</TableCell>
          <TableCell width={150} style={{ paddingRight: 0, justifyContent: "flex-start" }}>
            {cell(x.sections.length ? x.sections.map((s: any) => `${s.tab ? `${s.tab}: ` : ""}${s.title}`).join("; ") : "Not yet answered", {
              fontSize: 9,
              color: x.sections.length ? c.body : c.alert,
            })}
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);

const Chapter = ({ section, index, first }: { section: Section; index: number; first: boolean }) => {
  const items = section.items ?? [];
  let content: any;
  if (section.kind === "letter") content = <Letter items={items} />;
  else if (section.kind === "projects" || section.kind === "team") content = items.map((item, i) => <Card key={i} item={item} />);
  else if (section.kind === "fee") content = <Fee />;
  else if (section.kind === "forms") content = <Forms />;
  else if (section.kind === "matrix") content = <Matrix />;
  else content = groups(items).map((g, i) => <NumberedList key={i} title={g.title} items={g.items} />);
  return (
    <View style={first ? {} : { breakBefore: true }}>
      <View wrap={false} style={{ marginBottom: 24 }}>
        <View style={{ flexDirection: "row", alignItems: "flex-start", marginBottom: 12 }}>
          <Text noMargin color={c.brass} style={{ fontFamily: sans, fontSize: 8, fontWeight: 700, letterSpacing: 1.4 }}>
            {section.tab ? section.tab.toUpperCase() : two(index + 1)}
          </Text>
          <View style={{ width: 22, height: 0.75, backgroundColor: c.brass, marginHorizontal: 8, marginTop: 4 }} />
          <Eyebrow>{m.project}</Eyebrow>
        </View>
        <Display size={28}>{section.title}</Display>
        {section.lead ? (
          <Body size={11} color={c.muted} style={{ marginTop: 10, maxWidth: 420 }}>
            {section.lead}
          </Body>
        ) : null}
      </View>
      {content}
      {section.kind === "fee" && items.length ? <NumberedList title="Fee basis" items={items} /> : null}
    </View>
  );
};

// ---------- Cover ----------
const coverMeta: [string, string][] = [
  ["Prepared for", m.client],
  ["Prepared by", m.proposer],
  ["In response to", d.rfp.number ?? d.rfp.title],
  ["Issued", longDate(m.date)],
];
const cover = (
  <Page size="Letter" margin={0}>
    <View style={{ width: W, height: H, backgroundColor: c.ink, paddingHorizontal: 56, paddingTop: 52, paddingBottom: 48, justifyContent: "space-between" }}>
      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <Text noMargin color={c.white} style={{ fontFamily: sans, fontSize: 9, fontWeight: 700, letterSpacing: 2.2 }}>
          {m.proposer.toUpperCase()}
        </Text>
        <View style={{ borderWidth: 0.75, borderColor: c.brass, paddingHorizontal: 8, paddingVertical: 3 }}>
          <Eyebrow color={c.brass}>{statusLabel}</Eyebrow>
        </View>
      </View>
      <View>
        <View style={{ width: 36, height: 2, backgroundColor: c.brass, marginBottom: 20 }} />
        <Eyebrow color={c.sage} style={{ marginBottom: 14 }}>
          {m.kicker ?? "Proposal"}
        </Eyebrow>
        <Display size={46} color={c.white} style={{ maxWidth: 480, lineHeight: 1.04 }}>
          {m.project}
        </Display>
        {m.summary ? (
          <Body size={12.5} color={c.sage} style={{ marginTop: 26, maxWidth: 410, lineHeight: 1.6 }}>
            {m.summary}
          </Body>
        ) : null}
      </View>
      <View>
        <View style={{ flexDirection: "row", borderTopWidth: 0.75, borderTopColor: "#3e625b", paddingTop: 16 }}>
          {coverMeta.map(([label, value]) => (
            <View key={label} style={{ flex: 1, paddingRight: 12 }}>
              <Eyebrow color={c.sage} style={{ marginBottom: 5 }}>
                {label}
              </Eyebrow>
              <Body size={9.5} color={c.white} style={{ lineHeight: 1.35 }}>
                {value}
              </Body>
            </View>
          ))}
        </View>
        <Body size={7.5} color={c.sage} style={{ marginTop: 22 }}>
          {m.status === "DRAFT" ? "Draft for internal review. Not for submission." : "For internal review before submission."}
        </Body>
      </View>
    </View>
  </Page>
);

const header = (
  <Fixed position="header">
    <View style={{ flexDirection: "row", justifyContent: "space-between", paddingBottom: 8, marginBottom: 28, borderBottomWidth: 0.5, borderBottomColor: c.rule }}>
      <Text noMargin color={c.ink} style={{ fontFamily: sans, fontSize: 7.5, fontWeight: 700, letterSpacing: 1.6 }}>
        {m.proposer.toUpperCase()}
      </Text>
      <Eyebrow>{`${m.client} · ${d.rfp.number ?? m.reference}`}</Eyebrow>
    </View>
  </Fixed>
);
const footer = (
  <Fixed position="footer">
    <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingTop: 10 }}>
      <Eyebrow>{`${statusLabel} · ${m.reference} · ${longDate(m.date)}`}</Eyebrow>
      <Text noMargin color={c.ink} style={{ fontFamily: sans, fontSize: 7.5, letterSpacing: 1.4, lineHeight: 1.3 }}>
        {"{{pageNumber}} / {{totalPages}}"}
      </Text>
    </View>
  </Fixed>
);

// PDF metadata strings are PDFDocEncoding in Forme: keep them ASCII.
const ascii = (s: string) => s.replace(/[‒-―]/g, "-").replace(/[^\x20-\x7e]/g, "");
const doc = (
  <Document title={ascii(`${m.project} - Proposal ${m.reference}`)} author={ascii(m.proposer)} subject={ascii(`Proposal to ${m.client}`)}>
    {cover}
    <Page size="Letter" margin={{ top: 40, bottom: 36, left: M, right: M }}>
      {header}
      {footer}
      {d.sections.map((s: Section, i: number) => (
        <Chapter key={s.id} section={s} index={i} first={i === 0} />
      ))}
    </Page>
  </Document>
);
await writeFile(output, Buffer.from(await renderPdf(JSON.stringify(serialize(doc)))));
console.log(`Rendered ${output}`);
