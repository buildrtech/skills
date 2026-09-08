#!/usr/bin/env python3
"""Check a schedule-of-values pay application for math, continuity, and total errors.

Reads the current period's schedule of values (G703-style continuation sheet)
as CSV, optionally the prior period's CSV, and the contract terms as flags.
Prints a Markdown findings table plus a computed-vs-stated G702 summary.
Exits 1 if any finding has severity "error", otherwise 0.

The script prepares a review. It does not approve, certify, or reject payment.

Usage:
    python3 check_pay_app.py CURRENT.csv --contract-sum 2450000 \
        --change-orders 18500 --retainage 10 --prior PRIOR.csv \
        --g702-completed 783500 --g702-retainage 71550 ...

CSV columns (header names, case-insensitive; extra columns are ignored):
    item, description, scheduled_value, previous_completed, this_period,
    stored_materials, retainage_pct (optional, per-line override)
    Optional "as submitted" columns, checked when present:
    total_completed, percent_complete, balance_to_finish, retainage

Standard library only. Python 3.9 or later.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

CENT = Decimal("0.01")
REQUIRED_COLUMNS = (
    "item",
    "description",
    "scheduled_value",
    "previous_completed",
    "this_period",
    "stored_materials",
)
OPTIONAL_COLUMNS = (
    "retainage_pct",
    "total_completed",
    "percent_complete",
    "balance_to_finish",
    "retainage",
)
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass
class Finding:
    severity: str
    line: str
    column: str
    check: str
    message: str


@dataclass
class Line:
    row: int
    item: str
    description: str
    scheduled_value: Decimal
    previous_completed: Decimal
    this_period: Decimal
    stored_materials: Decimal
    retainage_pct: Decimal | None
    stated: dict[str, Decimal | None] = field(default_factory=dict)

    @property
    def total_completed(self) -> Decimal:
        return self.previous_completed + self.this_period + self.stored_materials

    @property
    def work_completed(self) -> Decimal:
        return self.previous_completed + self.this_period

    @property
    def balance_to_finish(self) -> Decimal:
        return self.scheduled_value - self.total_completed

    def percent(self, amount: Decimal) -> Decimal | None:
        if self.scheduled_value == 0:
            return None
        return (amount / self.scheduled_value * 100).quantize(CENT, ROUND_HALF_UP)


def money(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    q = value.quantize(CENT, ROUND_HALF_UP)
    text = f"{abs(q):,.2f}"
    return f"({text})" if q < 0 else text


def pct(value: Decimal | None) -> str:
    return "n/a" if value is None else f"{value.quantize(CENT, ROUND_HALF_UP)}%"


def parse_amount(raw: str | None, *, default: Decimal | None = None) -> Decimal | None:
    """Parse '1,234.56', '$1,234.56', '(500)', '12%', or blank."""
    if raw is None:
        return default
    text = raw.strip().replace("$", "").replace(",", "").replace("%", "")
    if text == "":
        return default
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1]
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"cannot parse amount {raw!r}") from exc
    if not value.is_finite():
        raise ValueError(f"amount must be finite: {raw!r}")
    return -value if negative else value


def read_sov(path: Path) -> list[Line]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: empty file")
        header_map = {name.strip().lower(): name for name in reader.fieldnames}
        missing = [c for c in REQUIRED_COLUMNS if c not in header_map]
        if missing:
            raise ValueError(f"{path}: missing required columns: {', '.join(missing)}")

        lines: list[Line] = []
        for index, row in enumerate(reader, start=2):
            def cell(name: str) -> str | None:
                key = header_map.get(name)
                return row.get(key) if key else None

            item = (cell("item") or "").strip()
            description = (cell("description") or "").strip()
            if not item and not description:
                continue
            if item.lower() in {"total", "totals", "grand total"}:
                continue
            try:
                amounts = {}
                for name in REQUIRED_COLUMNS[2:]:
                    amount = parse_amount(cell(name))
                    if amount is None:
                        raise ValueError(f"{name} is blank; supply an explicit amount or resolve the unreadable cell")
                    amounts[name] = amount
                line = Line(
                    row=index,
                    item=item or f"row {index}",
                    description=description,
                    scheduled_value=amounts["scheduled_value"],
                    previous_completed=amounts["previous_completed"],
                    this_period=amounts["this_period"],
                    stored_materials=amounts["stored_materials"],
                    retainage_pct=parse_amount(cell("retainage_pct")),
                )
                if line.retainage_pct is not None and not 0 <= line.retainage_pct <= 100:
                    raise ValueError("retainage_pct must be between 0 and 100")
                for name in ("total_completed", "percent_complete", "balance_to_finish", "retainage"):
                    line.stated[name] = parse_amount(cell(name))
            except ValueError as exc:
                raise ValueError(f"{path} row {index}: {exc}") from exc
            lines.append(line)
    if not lines:
        raise ValueError(f"{path}: no schedule-of-values lines found")
    return lines


def close(a: Decimal | None, b: Decimal | None, tolerance: Decimal) -> bool:
    if a is None or b is None:
        return True
    return abs(a - b) <= tolerance


def line_retainage(line: Line, work_pct: Decimal | None, stored_pct: Decimal | None) -> Decimal | None:
    if line.retainage_pct is not None:
        rate = line.retainage_pct / 100
        return (line.total_completed * rate).quantize(CENT, ROUND_HALF_UP)
    if work_pct is None or stored_pct is None:
        return None
    work = line.work_completed * work_pct / 100
    stored = line.stored_materials * stored_pct / 100
    return (work + stored).quantize(CENT, ROUND_HALF_UP)


def check_lines(lines: list[Line], prior: list[Line] | None, args: argparse.Namespace) -> list[Finding]:
    findings: list[Finding] = []
    tol = args.tolerance
    prior_by_item = {p.item: p for p in prior} if prior is not None else {}
    seen: dict[str, int] = {}
    for line in lines:
        ref = f"{line.item} {line.description}".strip()
        if line.item in seen:
            findings.append(Finding("warning", ref, "A", "duplicate-item",
                                    f"Item number {line.item} also appears on row {seen[line.item]}; confirm which line is which before comparing to the prior application."))
        seen.setdefault(line.item, line.row)

        for name, col in (("scheduled_value", "C"), ("previous_completed", "D"), ("this_period", "E"), ("stored_materials", "F")):
            if getattr(line, name) < 0:
                findings.append(Finding("error", ref, col, "negative-amount",
                                        f"Column {col} is {money(getattr(line, name))}; negative amounts belong on a credit change order line or a corrected prior period, not in this column."))

        total = line.total_completed
        stated_total = line.stated.get("total_completed")
        if not close(total, stated_total, tol):
            findings.append(Finding("error", ref, "G", "column-math",
                                    f"Column G as submitted is {money(stated_total)} but D + E + F = {money(line.previous_completed)} + {money(line.this_period)} + {money(line.stored_materials)} = {money(total)}."))

        computed_pct = line.percent(total)
        stated_pct = line.stated.get("percent_complete")
        if computed_pct is not None and stated_pct is not None and abs(computed_pct - stated_pct) > Decimal("0.05"):
            findings.append(Finding("error", ref, "G/C", "percent-math",
                                    f"Percent complete as submitted is {pct(stated_pct)} but G / C = {money(total)} / {money(line.scheduled_value)} = {pct(computed_pct)}."))

        stated_balance = line.stated.get("balance_to_finish")
        if not close(line.balance_to_finish, stated_balance, tol):
            findings.append(Finding("error", ref, "H", "balance-math",
                                    f"Column H as submitted is {money(stated_balance)} but C - G = {money(line.scheduled_value)} - {money(total)} = {money(line.balance_to_finish)}."))

        expected_ret = line_retainage(line, args.retainage, args.stored_retainage)
        stated_ret = line.stated.get("retainage")
        if not close(expected_ret, stated_ret, tol):
            basis = (f"{line.retainage_pct}% of G" if line.retainage_pct is not None
                     else f"{args.retainage}% of D + E plus {args.stored_retainage}% of F")
            findings.append(Finding("error", ref, "I", "line-retainage",
                                    f"Column I as submitted is {money(stated_ret)} but {basis} = {money(expected_ret)}; difference {money(stated_ret - expected_ret)}."))

        if line.scheduled_value > 0 and total > line.scheduled_value + tol:
            findings.append(Finding("error", ref, "G", "over-100-percent",
                                    f"Total completed and stored {money(total)} exceeds scheduled value {money(line.scheduled_value)} by {money(total - line.scheduled_value)} ({pct(computed_pct)} complete). Column G cannot exceed column C without a change order."))
        elif line.scheduled_value == 0 and total != 0:
            findings.append(Finding("error", ref, "C", "zero-value-billing",
                                    f"Line bills {money(total)} against a scheduled value of 0.00."))

        if line.stored_materials > 0:
            findings.append(Finding("warning", ref, "F", "stored-materials",
                                    f"Stored materials of {money(line.stored_materials)} billed this period; confirm bill of sale, insurance, location, and photos are in the backup."))

        if line.scheduled_value > 0:
            prev = prior_by_item.get(line.item) if prior_by_item else None
            if prev is not None:
                before = prev.percent(prev.total_completed) or Decimal(0)
                after = computed_pct or Decimal(0)
                if after - before >= args.jump_threshold:
                    findings.append(Finding("warning", ref, "G", "percent-jump",
                                            f"Percent complete moved from {pct(before)} on the prior application to {pct(after)} in one period (up {pct(after - before)} of scheduled value); confirm progress with the field or inspection log."))
            else:
                jump = line.percent(line.this_period + line.stored_materials)
                if jump is not None and jump >= args.jump_threshold:
                    findings.append(Finding("warning", ref, "E+F", "percent-jump",
                                            f"This period bills {pct(jump)} of the line's scheduled value in one period (E + F = {money(line.this_period + line.stored_materials)}); confirm progress with the field or inspection log."))
    return findings


def check_continuity(lines: list[Line], prior: list[Line], tolerance: Decimal) -> list[Finding]:
    findings: list[Finding] = []
    prior_by_item = {p.item: p for p in prior}
    current_items = {c.item for c in lines}
    for line in lines:
        ref = f"{line.item} {line.description}".strip()
        prev = prior_by_item.get(line.item)
        if prev is None:
            if line.previous_completed != 0:
                findings.append(Finding("error", ref, "D", "continuity",
                                        f"Column D is {money(line.previous_completed)} but no line with item {line.item} exists on the prior application."))
            else:
                findings.append(Finding("warning", ref, "A", "new-line",
                                        f"Line {line.item} is not on the prior application; confirm it was added by an approved change order."))
            continue
        if not close(line.previous_completed, prev.work_completed, tolerance):
            findings.append(Finding("error", ref, "D", "continuity",
                                    f"Column D is {money(line.previous_completed)} but the prior application's D + E for this line is {money(prev.previous_completed)} + {money(prev.this_period)} = {money(prev.work_completed)}; difference {money(line.previous_completed - prev.work_completed)}."))
        if not close(line.scheduled_value, prev.scheduled_value, tolerance):
            findings.append(Finding("warning", ref, "C", "scheduled-value-change",
                                    f"Scheduled value changed from {money(prev.scheduled_value)} on the prior application to {money(line.scheduled_value)}; confirm an approved change order supports the change."))
    for prev in prior:
        if prev.item not in current_items:
            findings.append(Finding("error", f"{prev.item} {prev.description}".strip(), "A", "missing-line",
                                    f"Line {prev.item} was on the prior application with {money(prev.total_completed)} completed and stored but is missing from this application."))
    return findings


def g702(lines: list[Line], args: argparse.Namespace) -> dict[str, Decimal | None]:
    sov_total = sum((l.scheduled_value for l in lines), Decimal(0))
    completed = sum((l.total_completed for l in lines), Decimal(0))
    line_retainages = [line_retainage(l, args.retainage, args.stored_retainage) for l in lines]
    retainage = sum(line_retainages, Decimal(0)) if all(v is not None for v in line_retainages) else None
    earned = subtract(completed, retainage)
    previous = args.prior_certified
    contract_to_date = (args.contract_sum + args.change_orders
                        if args.contract_sum is not None and args.change_orders is not None else None)
    return {
        "sov_total": sov_total,
        "contract_to_date": contract_to_date,
        "completed": completed,
        "work_completed": sum((l.work_completed for l in lines), Decimal(0)),
        "stored": sum((l.stored_materials for l in lines), Decimal(0)),
        "retainage": retainage,
        "earned": earned,
        "previous": previous,
        "due": subtract(earned, previous),
        "balance": subtract(contract_to_date, earned),
    }


def subtract(a: Decimal | None, b: Decimal | None) -> Decimal | None:
    return a - b if a is not None and b is not None else None


def check_totals(totals: dict[str, Decimal | None], prior: list[Line] | None, args: argparse.Namespace) -> list[Finding]:
    findings: list[Finding] = []
    tol = args.tolerance
    ref = "G702"

    if not close(totals["sov_total"], totals["contract_to_date"], tol):
        findings.append(Finding("error", ref, "Line 3 / G703 C total", "contract-sum",
                                f"Schedule of values totals {money(totals['sov_total'])} but contract sum to date is {money(totals['contract_to_date'])} (original {money(args.contract_sum)} + approved change orders {money(args.change_orders)}); difference {money(totals['contract_to_date'] - totals['sov_total'])}. An approved change order may not be reflected on the schedule."))
    if args.g702_change_orders is not None and not close(args.g702_change_orders, args.change_orders, tol):
        findings.append(Finding("error", ref, "Line 2", "change-orders",
                                f"Net change by change orders as submitted is {money(args.g702_change_orders)} but the approved change order log totals {money(args.change_orders)}."))
    if args.g702_contract_sum_to_date is not None and not close(args.g702_contract_sum_to_date, totals["contract_to_date"], tol):
        findings.append(Finding("error", ref, "Line 3", "contract-sum",
                                f"Contract sum to date as submitted is {money(args.g702_contract_sum_to_date)} but Line 1 + Line 2 = {money(args.contract_sum)} + {money(args.change_orders)} = {money(totals['contract_to_date'])}."))
    if args.g702_completed is not None and not close(args.g702_completed, totals["completed"], tol):
        findings.append(Finding("error", ref, "Line 4", "total-completed",
                                f"Total completed and stored to date as submitted is {money(args.g702_completed)} but the G703 column G total is {money(totals['completed'])}."))
    if args.g702_retainage is not None and not close(args.g702_retainage, totals["retainage"], tol):
        diff = args.g702_retainage - totals["retainage"]
        hint = ""
        stored_ret = ((totals["stored"] * args.stored_retainage / 100).quantize(CENT, ROUND_HALF_UP)
                      if args.stored_retainage is not None else Decimal(0))
        if stored_ret > 0 and close(-diff, stored_ret, tol):
            hint = f" The shortfall equals {args.stored_retainage}% of stored materials ({money(totals['stored'])}), so retainage appears not to have been applied to stored materials."
        basis = ("sum of independently supplied per-line retainage terms"
                 if args.retainage is None or args.stored_retainage is None
                 else f"{args.retainage}% of completed work {money(totals['work_completed'])} plus {args.stored_retainage}% of stored materials {money(totals['stored'])}")
        findings.append(Finding("error", ref, "Line 5", "retainage",
                                f"Retainage as submitted is {money(args.g702_retainage)} but {basis} = {money(totals['retainage'])}; difference {money(diff)}.{hint}"))
    if args.g702_earned is not None:
        stated_basis = args.g702_completed if args.g702_completed is not None else totals["completed"]
        stated_ret = args.g702_retainage if args.g702_retainage is not None else totals["retainage"]
        if not close(args.g702_earned, subtract(stated_basis, stated_ret), tol):
            findings.append(Finding("error", ref, "Line 6", "earned-math",
                                    f"Total earned less retainage as submitted is {money(args.g702_earned)} but Line 4 - Line 5 as submitted = {money(stated_basis)} - {money(stated_ret)} = {money(subtract(stated_basis, stated_ret))}."))
        if not close(args.g702_earned, totals["earned"], tol):
            findings.append(Finding("warning", ref, "Line 6", "earned-recomputed",
                                    f"Total earned less retainage recomputed from the schedule and contract terms is {money(totals['earned'])}, versus {money(args.g702_earned)} as submitted; difference {money(args.g702_earned - totals['earned'])}."))
    if args.prior_certified is not None and not close(args.g702_previous, args.prior_certified, tol):
        findings.append(Finding("error", ref, "Line 7", "previous-certificates",
                                f"Less previous certificates as submitted is {money(args.g702_previous)} but the independently supplied cumulative prior certified amount is {money(args.prior_certified)}; difference {money(args.g702_previous - args.prior_certified)}."))
    if args.g702_due is not None:
        stated_earned = args.g702_earned if args.g702_earned is not None else totals["earned"]
        stated_prev = args.g702_previous if args.g702_previous is not None else totals["previous"]
        if stated_prev is not None and not close(args.g702_due, subtract(stated_earned, stated_prev), tol):
            findings.append(Finding("error", ref, "Line 8", "due-math",
                                    f"Current payment due as submitted is {money(args.g702_due)} but Line 6 - Line 7 as submitted = {money(stated_earned)} - {money(stated_prev)} = {money(subtract(stated_earned, stated_prev))}."))
        if totals["due"] is not None and not close(args.g702_due, totals["due"], tol):
            findings.append(Finding("warning", ref, "Line 8", "due-recomputed",
                                    f"Current payment due recomputed from the schedule and contract terms is {money(totals['due'])}, versus {money(args.g702_due)} as submitted; difference {money(args.g702_due - totals['due'])}."))
    if args.g702_balance is not None:
        stated_ctd = args.g702_contract_sum_to_date if args.g702_contract_sum_to_date is not None else totals["contract_to_date"]
        stated_earned = args.g702_earned if args.g702_earned is not None else totals["earned"]
        if not close(args.g702_balance, subtract(stated_ctd, stated_earned), tol):
            findings.append(Finding("error", ref, "Line 9", "balance-math",
                                    f"Balance to finish including retainage as submitted is {money(args.g702_balance)} but Line 3 - Line 6 as submitted = {money(stated_ctd)} - {money(stated_earned)} = {money(subtract(stated_ctd, stated_earned))}."))
    if prior is None:
        findings.append(Finding("warning", ref, "G703 D", "no-prior",
                                "No prior-period schedule was provided, so column D continuity was not verified."))
    for column, check, missing in (
        ("Line 3", "missing-contract-terms", totals["contract_to_date"] is None),
        ("Line 5", "missing-retainage-terms", totals["retainage"] is None),
        ("Line 7", "missing-prior-certificate", args.prior_certified is None),
    ):
        if missing:
            findings.append(Finding("warning", ref, column, check,
                                    "Independent supporting input was not supplied; this check and dependent computed totals remain unverified (n/a)."))
    return findings


def render(findings: list[Finding], totals: dict[str, Decimal | None], args: argparse.Namespace, lines: list[Line]) -> str:
    out: list[str] = []
    findings = sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.line, f.column))
    counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITY_ORDER}
    out.append(f"## Findings ({counts['error']} error, {counts['warning']} warning, {counts['info']} info)")
    out.append("")
    if findings:
        out.append("| # | Severity | Line | Column | Check | Finding |")
        out.append("|---|---|---|---|---|---|")
        for n, f in enumerate(findings, start=1):
            out.append(f"| {n} | {f.severity} | {f.line} | {f.column} | {f.check} | {f.message} |")
    else:
        out.append("No findings in the checks run. Missing as-submitted values are unverified.")
    out.append("")
    out.append("## G702 summary: computed from the schedule and contract terms versus as submitted")
    out.append("")
    out.append("| Line | Field | Computed | As submitted | Difference |")
    out.append("|---|---|---|---|---|")

    def row(no: str, label: str, computed: Decimal | None, stated: Decimal | None) -> None:
        diff = (stated - computed) if (computed is not None and stated is not None) else None
        out.append(f"| {no} | {label} | {money(computed)} | {money(stated)} | {money(diff)} |")

    row("1", "Original contract sum", args.contract_sum, args.contract_sum)
    row("2", "Net change by change orders", args.change_orders, args.g702_change_orders)
    row("3", "Contract sum to date", totals["contract_to_date"], args.g702_contract_sum_to_date)
    row("G703 C", "Schedule of values total", totals["sov_total"], None)
    row("4", "Total completed and stored to date", totals["completed"], args.g702_completed)
    row("5", "Retainage", totals["retainage"], args.g702_retainage)
    row("6", "Total earned less retainage", totals["earned"], args.g702_earned)
    row("7", "Less previous certificates for payment", totals["previous"], args.g702_previous)
    row("8", "Current payment due", totals["due"], args.g702_due)
    row("9", "Balance to finish, including retainage", totals["balance"], args.g702_balance)
    out.append("")
    out.append(f"Lines checked: {len(lines)}. Retainage basis: {pct(args.retainage)} of completed work, {pct(args.stored_retainage)} of stored materials; explicit per-line overrides apply. "
               f"Tolerance: {money(args.tolerance)}. Percent-jump threshold: {args.jump_threshold}% of scheduled value in one period.")
    out.append("")
    out.append("This output prepares a review. It is not an approval, certification, or rejection of payment.")
    return "\n".join(out)


def decimal_arg(text: str) -> Decimal:
    try:
        value = parse_amount(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if value is None:
        raise argparse.ArgumentTypeError("expected a number")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("current", type=Path, help="current period schedule of values CSV")
    parser.add_argument("--contract-sum", type=decimal_arg, default=None, help="original contract sum from contract; omit if unknown")
    parser.add_argument("--change-orders", type=decimal_arg, default=None, help="net approved change orders from the log; explicit 0 if none, omit if unknown")
    parser.add_argument("--retainage", type=decimal_arg, default=None, help="retainage percent on completed work; explicit 0 if none, omit if unknown")
    parser.add_argument("--stored-retainage", type=decimal_arg, default=None, help="retainage percent on stored materials (default: same as --retainage)")
    parser.add_argument("--prior-certified", type=decimal_arg, default=None, help="cumulative amount of all previous certificates, independently sourced; never infer from the current Line 7 or current retainage rate")
    parser.add_argument("--prior", type=Path, default=None, help="prior period schedule of values CSV, same layout")
    parser.add_argument("--jump-threshold", type=decimal_arg, default=Decimal(50), help="flag lines billing at least this percent of scheduled value in one period (default 50)")
    parser.add_argument("--tolerance", type=decimal_arg, default=Decimal("0.01"), help="rounding tolerance in currency units (default 0.01)")
    stated = parser.add_argument_group("G702 as submitted (optional; each is checked when given)")
    stated.add_argument("--g702-change-orders", type=decimal_arg, default=None, help="Line 2")
    stated.add_argument("--g702-contract-sum-to-date", type=decimal_arg, default=None, help="Line 3")
    stated.add_argument("--g702-completed", type=decimal_arg, default=None, help="Line 4")
    stated.add_argument("--g702-retainage", type=decimal_arg, default=None, help="Line 5 total")
    stated.add_argument("--g702-earned", type=decimal_arg, default=None, help="Line 6")
    stated.add_argument("--g702-previous", type=decimal_arg, default=None, help="Line 7")
    stated.add_argument("--g702-due", type=decimal_arg, default=None, help="Line 8")
    stated.add_argument("--g702-balance", type=decimal_arg, default=None, help="Line 9")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    for name in ("retainage", "stored_retainage"):
        value = getattr(args, name)
        if value is not None and not 0 <= value <= 100:
            parser.error(f"--{name.replace(chr(95), chr(45))} must be between 0 and 100")
    if args.tolerance < 0 or args.jump_threshold < 0:
        parser.error("tolerance and jump threshold must be nonnegative")
    if args.stored_retainage is None:
        args.stored_retainage = args.retainage
    try:
        lines = read_sov(args.current)
        prior = read_sov(args.prior) if args.prior else None
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    findings = check_lines(lines, prior, args)
    if prior is not None:
        findings.extend(check_continuity(lines, prior, args.tolerance))
    totals = g702(lines, args)
    findings.extend(check_totals(totals, prior, args))
    print(render(findings, totals, args, lines))
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
