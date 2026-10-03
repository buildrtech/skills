import React from "react";
import { readFile, writeFile } from "node:fs/promises";
import { Document, Page, View, serialize } from "@formepdf/react";
import { renderPdf } from "@formepdf/core";
import { Text } from "@/components/pdf/text/text";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/components/pdf/table/table";
import { validate } from "./validate.mjs";

const [input, output] = process.argv.slice(2);
if (!input || !output)
  throw new Error("Usage: npm run render -- INPUT.json OUTPUT.pdf");
const d = validate(JSON.parse(await readFile(input, "utf8")));
const ink = "#163b35";
const money = (cents: number) =>
  `${d.currency} ${cents < 0 ? "-" : ""}${Math.floor(Math.abs(cents) / 100).toLocaleString("en-US")}.${String(Math.abs(cents) % 100).padStart(2, "0")}`;
const section = (title: string, rows: { text: string; source: string }[]) => (
  <View style={{ marginBottom: 20 }}>
    <Text variant="xl" weight="bold" color={ink}>
      {title}
    </Text>
    {rows.map((row, i) => (
      <View key={i} style={{ marginBottom: 10 }}>
        <Text>{row.text}</Text>
        <Text variant="xs" color="#666666">
          Source: {row.source}
        </Text>
      </View>
    ))}
  </View>
);
const page = (number: string, title: string, children: React.ReactNode) => (
  <Page size="Letter" margin={44}>
    <View>
      <Text variant="xs" color={ink}>
        {d.contractor.toUpperCase()} / {d.reference} / {d.status}
      </Text>
      <Text variant="3xl" weight="bold" color={ink}>
        {title}
      </Text>
      <Text variant="sm" color="#666666">
        {d.project} · {d.client} · {d.date}
      </Text>
      <View style={{ marginTop: 22 }}>{children}</View>
      <Text variant="xs" color="#666666">
        Section {number} / Proposal for review · {d.reference}
      </Text>
    </View>
  </Page>
);
const doc = (
  <Document>
    <Page size="Letter" margin={0}>
      <View style={{ padding: 48, minHeight: 792, backgroundColor: ink }}>
        <Text variant="sm" color="#c6ded4">
          {d.contractor.toUpperCase()}
        </Text>
        <View style={{ marginTop: 90, marginBottom: 42 }}>
          <Text variant="sm" color="#c6ded4">
            CONSTRUCTION PROPOSAL
          </Text>
          <Text variant="3xl" weight="bold" color="#ffffff">
            {d.project}
          </Text>
          <Text variant="xl" color="#ffffff">
            Prepared for {d.client}
          </Text>
        </View>
        <Text color="#ffffff">{d.summary}</Text>
        <View style={{ marginTop: 90 }}>
          <Text variant="sm" color="#c6ded4">
            {d.date} · {d.reference}
          </Text>
          <Text variant="sm" color="#ffffff">
            {d.status} — Subject to the qualifications and open decisions in
            this proposal.
          </Text>
        </View>
      </View>
    </Page>
    {page(
      "02",
      "Scope & delivery",
      <>
        {section("Included scope", d.scope)}
        {section("Our approach", d.approach)}
      </>,
    )}
    {page(
      "03",
      "People & programme",
      <>
        {section("Proposed team", d.team)}
        {section("Schedule basis", d.schedule)}
      </>,
    )}
    {page(
      "04",
      "Commercial proposal",
      <>
        <Table variant="line">
          <TableHeader>
            <TableRow>
              <TableCell>Scope / basis</TableCell>
              <TableCell align="right">Amount</TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {d.pricing.map((row: any) => (
              <TableRow key={row.id}>
                <TableCell>{`${row.label}${row.kind === "option" ? " (OPTION — not in base)" : ""}\nSource: ${row.source}`}</TableCell>
                <TableCell align="right">{money(row.cents)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <View
          style={{ marginTop: 20, padding: 16, backgroundColor: "#edf3ef" }}
        >
          <Text variant="sm" color={ink}>
            BASE PROPOSAL · OPTIONS EXCLUDED
          </Text>
          <Text variant="2xl" weight="bold" color={ink}>
            {money(d.baseTotalCents)}
          </Text>
        </View>
      </>,
    )}
    {page(
      "05",
      "Qualifications & next steps",
      <>
        {section("Exclusions and commercial basis", d.exclusions)}
        {section("Open decisions", d.questions)}
      </>,
    )}
  </Document>
);
await writeFile(
  output,
  Buffer.from(await renderPdf(JSON.stringify(serialize(doc)))),
);
console.log(`Rendered ${output}`);
