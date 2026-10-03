import React from "react";
import { readFile, writeFile } from "node:fs/promises";
import { Document, Fixed, Page, View, serialize } from "@formepdf/react";
import { renderPdf } from "@formepdf/core";
import { Text } from "@/components/pdf/text/text";
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
  TableHeader,
  TableRow,
} from "@/components/pdf/table/table";
import { validate } from "./validate.mjs";

const [input, output] = process.argv.slice(2);
if (!input || !output)
  throw new Error("Usage: npm run render -- INPUT.json OUTPUT.pdf");
const d = validate(JSON.parse(await readFile(input, "utf8")));

// Design tokens. Swap these for the proposer's brand when one is supplied.
const c = {
  ink: "#163b35",
  inkDeep: "#0f2b26",
  sage: "#a9c9bb",
  brass: "#c39a4f",
  tint: "#f1f5f3",
  rule: "#d8e0dc",
  muted: "#66736f",
  body: "#1f2624",
  white: "#ffffff",
};
const serif = "Times"; // Forme's built-in serif; "Times-Roman" silently falls back to Helvetica
const sans = "Helvetica";
const W = 612;
const H = 792;
const M = 56; // interior side margin
const CW = W - 2 * M; // interior content width

type Row = { text: string; source: string };
type Price = { id: string; label: string; kind: string; cents: number; source: string };

// Exact decimal formatting from integer cents (no floating-point rounding).
const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: d.currency,
});
const money = (cents: number) => {
  const abs = Math.abs(cents);
  const value = `${Math.floor(abs / 100)}.${String(abs % 100).padStart(2, "0")}`;
  return `${cents < 0 ? "–" : ""}${currency.format(value as unknown as number)}`;
};
const longDate = (iso: string) => {
  const parsed = /^\d{4}-\d{2}-\d{2}$/.test(iso)
    ? new Date(`${iso}T12:00:00Z`)
    : null;
  return parsed && !Number.isNaN(parsed.valueOf())
    ? parsed.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        timeZone: "UTC",
      })
    : iso;
};
const two = (n: number) => String(n).padStart(2, "0");

const base: Price[] = d.pricing.filter((p: Price) => p.kind === "base");
const options: Price[] = d.pricing.filter((p: Price) => p.kind === "option");
const statusLabel = d.status === "DRAFT" ? "Draft" : "For review";

// ---------- Typographic primitives (all pdfcn Text) ----------
const Eyebrow = ({ children, color = c.muted, style = {} }: any) => (
  <Text
    noMargin
    color={color}
    style={{ fontFamily: sans, fontSize: 7.5, letterSpacing: 1.4, lineHeight: 1.3, ...style }}
  >
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

// One source note per section when every row shares it; otherwise per row.
const sharedSource = (rows: Row[]) =>
  rows.every((r) => r.source === rows[0].source) ? rows[0].source : null;

const Section = ({ title, rows, marker = "number" }: { title: string; rows: Row[]; marker?: "number" | "check" }) => {
  const shared = sharedSource(rows);
  const item = (row: Row, i: number) => (
    <View
      key={i}
      wrap={false}
      style={{
        flexDirection: "row",
        paddingVertical: 10,
        borderBottomWidth: i === rows.length - 1 ? 0 : 0.5,
        borderBottomColor: c.rule,
      }}
    >
      <View style={{ width: 34, paddingTop: 2 }}>
        {marker === "check" ? (
          <View style={{ width: 9, height: 9, borderWidth: 0.75, borderColor: c.ink, marginTop: 1 }} />
        ) : (
          <Text noMargin color={c.brass} style={{ fontFamily: sans, fontSize: 8, fontWeight: 700, letterSpacing: 0.6 }}>
            {two(i + 1)}
          </Text>
        )}
      </View>
      <View style={{ width: CW - 34, paddingRight: 16 }}>
        <Body>{row.text}</Body>
        {shared ? null : (
          <Eyebrow style={{ marginTop: 4, fontSize: 7 }}>{`Source · ${row.source}`}</Eyebrow>
        )}
      </View>
    </View>
  );
  return (
    <View style={{ marginBottom: 26 }}>
      {/* Keep the heading with its first item so it never strands at a page foot. */}
      <View wrap={false}>
        <View
          style={{
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "flex-end",
            paddingBottom: 7,
            borderBottomWidth: 1,
            borderBottomColor: c.ink,
          }}
        >
          <Text noMargin color={c.ink} style={{ fontFamily: sans, fontSize: 11, fontWeight: 700, lineHeight: 1.3 }}>
            {title}
          </Text>
          {shared ? <Eyebrow>{`Source · ${shared}`}</Eyebrow> : null}
        </View>
        {item(rows[0], 0)}
      </View>
      {rows.slice(1).map((row, i) => item(row, i + 1))}
    </View>
  );
};

const Chapter = ({ number, title, lead, first = false, children }: any) => (
  <View style={first ? {} : { breakBefore: true }}>
    <View wrap={false} style={{ marginBottom: 28 }}>
      <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 12 }}>
        <Text noMargin color={c.brass} style={{ fontFamily: sans, fontSize: 8, fontWeight: 700, letterSpacing: 1.4 }}>
          {number}
        </Text>
        <View style={{ width: 22, height: 0.75, backgroundColor: c.brass, marginHorizontal: 8 }} />
        <Eyebrow>{d.project}</Eyebrow>
      </View>
      <Display size={30}>{title}</Display>
      {lead ? (
        <Body size={11} color={c.muted} style={{ marginTop: 10, maxWidth: 400 }}>
          {lead}
        </Body>
      ) : null}
    </View>
    {children}
  </View>
);

// ---------- Cover ----------
const coverMeta: [string, string][] = [
  ["Prepared for", d.client],
  ["Prepared by", d.contractor],
  ["Issued", longDate(d.date)],
  ["Reference", d.reference],
];

const cover = (
  <Page size="Letter" margin={0}>
    <View
      style={{
        width: W,
        height: H,
        backgroundColor: c.ink,
        paddingHorizontal: 56,
        paddingTop: 52,
        paddingBottom: 48,
        justifyContent: "space-between",
      }}
    >
      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <Text noMargin color={c.white} style={{ fontFamily: sans, fontSize: 9, fontWeight: 700, letterSpacing: 2.2 }}>
          {d.contractor.toUpperCase()}
        </Text>
        <View style={{ borderWidth: 0.75, borderColor: c.brass, paddingHorizontal: 8, paddingVertical: 3 }}>
          <Eyebrow color={c.brass}>{statusLabel}</Eyebrow>
        </View>
      </View>

      <View>
        <View style={{ width: 36, height: 2, backgroundColor: c.brass, marginBottom: 20 }} />
        <Eyebrow color={c.sage} style={{ marginBottom: 14 }}>
          Construction proposal
        </Eyebrow>
        <Display size={50} color={c.white} style={{ maxWidth: 470, lineHeight: 1.04 }}>
          {d.project}
        </Display>
        <Body size={12.5} color={c.sage} style={{ marginTop: 26, maxWidth: 400, lineHeight: 1.6 }}>
          {d.summary}
        </Body>
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
          {`${statusLabel} for discussion. Pricing and schedule are subject to the qualifications and open decisions in this proposal.`}
        </Body>
      </View>
    </View>
  </Page>
);

// ---------- Interior chrome ----------
const header = (
  <Fixed position="header">
    <View
      style={{
        flexDirection: "row",
        justifyContent: "space-between",
        paddingBottom: 8,
        marginBottom: 30,
        borderBottomWidth: 0.5,
        borderBottomColor: c.rule,
      }}
    >
      <Text noMargin color={c.ink} style={{ fontFamily: sans, fontSize: 7.5, fontWeight: 700, letterSpacing: 1.6 }}>
        {d.contractor.toUpperCase()}
      </Text>
      <Eyebrow>{`${d.client} · ${d.reference}`}</Eyebrow>
    </View>
  </Fixed>
);
const footer = (
  <Fixed position="footer">
    <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingTop: 10 }}>
      <Eyebrow>{`${statusLabel} · ${longDate(d.date)}`}</Eyebrow>
      <Text noMargin color={c.ink} style={{ fontFamily: sans, fontSize: 7.5, letterSpacing: 1.4, lineHeight: 1.3 }}>
        {"{{pageNumber}} / {{totalPages}}"}
      </Text>
    </View>
  </Fixed>
);

// ---------- At a glance ----------
const facts: [string, string, string][] = [
  ["Base proposal", money(d.baseTotalCents), `${base.length} priced line${base.length === 1 ? "" : "s"}`],
  [
    "Options",
    options.length ? String(options.length) : "None",
    options.length ? "Priced separately, not in base" : "No optional scope priced",
  ],
  ["Open decisions", String(d.questions.length), "To resolve before acceptance"],
];
const glance = (
  <View wrap={false} style={{ flexDirection: "row", backgroundColor: c.tint, marginBottom: 30 }}>
    {facts.map(([label, value, note], i) => (
      <View
        key={label}
        style={{
          flex: i === 0 ? 1.4 : 1,
          paddingVertical: 14,
          paddingHorizontal: 16,
          borderLeftWidth: i === 0 ? 0 : 0.5,
          borderLeftColor: c.rule,
        }}
      >
        <Eyebrow style={{ marginBottom: 6 }}>{label}</Eyebrow>
        <Display size={20}>{value}</Display>
        <Body size={8} color={c.muted} style={{ marginTop: 4 }}>
          {note}
        </Body>
      </View>
    ))}
  </View>
);

// ---------- Commercial ----------
const cell = (text: string, extra: any = {}) => (
  <Text noMargin color={c.body} style={{ fontFamily: sans, fontSize: 9.5, lineHeight: 1.4, ...extra }}>
    {text}
  </Text>
);
const priceTable = (title: string, rows: Price[], totalLabel?: string, totalCents?: number) => (
  <View style={{ marginBottom: 22 }}>
    <Table variant="line">
      <TableHeader>
        <TableRow header style={{ borderBottomWidth: 1, borderBottomColor: c.ink }}>
          <TableCell width={34} style={{ paddingLeft: 0 }}>{""}</TableCell>
          <TableCell>
            <Eyebrow color={c.ink}>{title}</Eyebrow>
          </TableCell>
          <TableCell width={120} align="right" style={{ paddingRight: 0 }}>
            <Eyebrow color={c.ink} style={{ textAlign: "right" }}>
              {`Amount (${d.currency})`}
            </Eyebrow>
          </TableCell>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row, i) => (
          <TableRow key={row.id} style={{ borderBottomColor: c.rule }}>
            <TableCell width={34} style={{ paddingLeft: 0, justifyContent: "flex-start" }}>
              {cell(two(i + 1), { color: c.brass, fontSize: 8, fontWeight: 700, paddingTop: 1 })}
            </TableCell>
            <TableCell style={{ justifyContent: "flex-start" }}>
              {cell(row.label, { fontWeight: 700, color: c.ink })}
              <Eyebrow style={{ marginTop: 3, fontSize: 7 }}>{row.source}</Eyebrow>
            </TableCell>
            <TableCell width={120} align="right" style={{ paddingRight: 0, justifyContent: "flex-start" }}>
              {cell(money(row.cents), { textAlign: "right", color: row.cents < 0 ? c.muted : c.body })}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
      {totalLabel ? (
        <TableFooter>
          <TableRow footer style={{ borderTopWidth: 1, borderTopColor: c.ink, borderBottomWidth: 0 }}>
            <TableCell width={34} style={{ paddingLeft: 0 }}>{""}</TableCell>
            <TableCell>{cell(totalLabel, { fontWeight: 700, color: c.ink })}</TableCell>
            <TableCell width={120} align="right" style={{ paddingRight: 0 }}>
              {cell(money(totalCents!), { textAlign: "right", fontWeight: 700, color: c.ink })}
            </TableCell>
          </TableRow>
        </TableFooter>
      ) : null}
    </Table>
  </View>
);

const totalBand = (
  <View
    wrap={false}
    style={{
      backgroundColor: c.ink,
      paddingVertical: 22,
      paddingHorizontal: 24,
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "flex-end",
      marginBottom: 14,
    }}
  >
    <View style={{ maxWidth: 230 }}>
      <Eyebrow color={c.brass} style={{ marginBottom: 6 }}>
        Base proposal total
      </Eyebrow>
      <Body size={8.5} color={c.sage}>
        {options.length
          ? "Excludes the optional scope listed below. See Qualifications for exclusions."
          : "See Qualifications for exclusions and the commercial basis."}
      </Body>
    </View>
    <Display size={32} color={c.white} style={{ textAlign: "right" }}>
      {money(d.baseTotalCents)}
    </Display>
  </View>
);

// ---------- Document ----------
const doc = (
  <Document
    title={`${d.project} — Proposal ${d.reference}`}
    author={d.contractor}
    subject={`Construction proposal for ${d.client}`}
  >
    {cover}
    <Page size="Letter" margin={{ top: 40, bottom: 36, left: M, right: M }}>
      {header}
      {footer}
      <Chapter number="01" title="Scope & approach" lead={d.summary} first>
        {glance}
        <Section title="Included scope" rows={d.scope} />
        <Section title="Our approach" rows={d.approach} />
      </Chapter>
      <Chapter number="02" title="Team & schedule">
        <Section title="Proposed team" rows={d.team} />
        <Section title="Schedule basis" rows={d.schedule} />
      </Chapter>
      <Chapter number="03" title="Commercial proposal">
        {totalBand}
        <View style={{ marginTop: 16 }}>
          {priceTable("Base scope", base, "Base proposal total", d.baseTotalCents)}
          {options.length
            ? priceTable("Optional scope — not included in base", options)
            : null}
        </View>
      </Chapter>
      <Chapter number="04" title="Qualifications & next steps">
        <Section title="Exclusions and commercial basis" rows={d.exclusions} />
        <Section title="Open decisions" rows={d.questions} marker="check" />
        <View wrap={false} style={{ borderLeftWidth: 2, borderLeftColor: c.brass, paddingLeft: 14, paddingVertical: 4 }}>
          <Eyebrow color={c.ink} style={{ marginBottom: 4 }}>
            Before acceptance
          </Eyebrow>
          <Body size={9.5} color={c.muted}>
            {`This proposal is marked ${statusLabel.toLowerCase()}. Resolve the open decisions above before it is issued for acceptance.`}
          </Body>
        </View>
      </Chapter>
    </Page>
  </Document>
);
await writeFile(
  output,
  Buffer.from(await renderPdf(JSON.stringify(serialize(doc)))),
);
console.log(`Rendered ${output}`);
