// Staffing plan core: validation, analysis, and rendering.
//
// Pure functions with no imports, so the same file runs in Node (plan.mjs)
// and is inlined into the generated HTML for live what-if recalculation.
// All allocations are whole percent integers (100 = one full-time person)
// to keep the arithmetic exact.

const MONTH = /^\d{4}-(0[1-9]|1[0-2])$/;
const MODES = ["weighted", "won", "lost"];

// ---------- Months ----------

export function addMonths(month, n) {
  const [y, m] = month.split("-").map(Number);
  const index = y * 12 + (m - 1) + n;
  return `${Math.floor(index / 12)}-${String((index % 12) + 1).padStart(2, "0")}`;
}

export function horizonMonths(horizon) {
  return Array.from({ length: horizon.months }, (_, i) => addMonths(horizon.start, i));
}

const MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function monthLabel(month) {
  const [y, m] = month.split("-");
  return `${MONTH_NAMES[Number(m) - 1]} ${y.slice(2)}`;
}

function plural(n, word) {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

function statusText(status) {
  return status === "leave" ? "on leave" : status === "not started" ? "not yet started" : "no longer employed";
}

function fte(pct) {
  return `${(pct / 100).toFixed(1)} FTE`;
}

function gapLabel(gap) {
  return gap.gapMin === gap.gap ? `${gap.gap}%` : `${gap.gapMin}–${gap.gap}%`;
}

function article(word) {
  return /^[AEIOU]/i.test(word) ? "an" : "a";
}

function rangeLabel(from, to) {
  return from === to ? monthLabel(from) : `${monthLabel(from)} to ${monthLabel(to)}`;
}

// ---------- Validation ----------

function toPct(value) {
  return Math.round(value * 100);
}

function isWholePct(value) {
  return Math.abs(value * 100 - Math.round(value * 100)) < 1e-9;
}

/** Validate normalized staffing data. Throws one error listing every problem. */
export function validate(data) {
  const errors = [];
  const fail = (path, message) => errors.push(`${path}: ${message}`);
  const text = (value, path) => {
    if (typeof value !== "string" || !value.trim()) fail(path, "must be nonempty text");
  };
  const month = (value, path) => {
    if (typeof value !== "string" || !MONTH.test(value)) fail(path, "must be a month like 2026-10");
  };
  const range = (item, path) => {
    month(item?.from, `${path}.from`);
    month(item?.to, `${path}.to`);
    if (MONTH.test(item?.from ?? "") && MONTH.test(item?.to ?? "") && item.from > item.to) fail(path, "from is after to");
  };
  const fraction = (value, path, max) => {
    if (typeof value !== "number" || !Number.isFinite(value) || value <= 0 || value > max) {
      fail(path, `must be a number above 0 and at most ${max}`);
    } else if (!isWholePct(value)) {
      fail(path, "must be a whole percent (for example 0.25, not 0.333)");
    }
  };
  const list = (value, path) => {
    if (Array.isArray(value)) return value;
    fail(path, "must be a list");
    return [];
  };
  const strings = (value, path) => {
    if (value === undefined) return;
    if (!Array.isArray(value) || value.some((v) => typeof v !== "string" || !v.trim())) fail(path, "must be a list of text");
  };

  if (!data || typeof data !== "object" || Array.isArray(data)) throw new Error("Staffing data must be an object");
  text(data.company?.name, "company.name");
  month(data.horizon?.start, "horizon.start");
  if (!Number.isInteger(data.horizon?.months) || data.horizon.months < 1 || data.horizon.months > 36) {
    fail("horizon.months", "must be a whole number from 1 to 36");
  }
  if (typeof data.asOf !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(data.asOf)) fail("asOf", "must be a date like 2026-10-05");
  for (const [role, value] of Object.entries(data.thresholds ?? {})) fraction(value, `thresholds.${role}`, 3);
  for (const [role, fits] of Object.entries(data.roleFits ?? {})) {
    strings(fits?.same, `roleFits.${role}.same`);
    strings(fits?.stepUp, `roleFits.${role}.stepUp`);
  }

  const personIds = new Set();
  list(data.people, "people").forEach((p, i) => {
    const path = `people[${i}]`;
    text(p?.id, `${path}.id`);
    if (personIds.has(p?.id)) fail(`${path}.id`, `duplicate id ${p.id}`);
    personIds.add(p?.id);
    text(p?.name, `${path}.name`);
    text(p?.role, `${path}.role`);
    strings(p?.sectors, `${path}.sectors`);
    strings(p?.certs, `${path}.certs`);
    if (p?.start !== undefined) month(p.start, `${path}.start`);
    if (p?.end !== undefined) month(p.end, `${path}.end`);
    list(p?.leave ?? [], `${path}.leave`).forEach((l, j) => {
      range(l, `${path}.leave[${j}]`);
      fraction(l?.fraction, `${path}.leave[${j}].fraction`, 1);
    });
  });

  const jobIds = new Set();
  const seats = (job, path) => {
    if (!Array.isArray(job?.seats)) return fail(`${path}.seats`, "must be a list");
    job.seats.forEach((s, j) => {
      text(s?.role, `${path}.seats[${j}].role`);
      range(s, `${path}.seats[${j}]`);
      fraction(s?.fraction, `${path}.seats[${j}].fraction`, 10);
      strings(s?.requires?.certs, `${path}.seats[${j}].requires.certs`);
    });
  };
  for (const [key, kind] of [["projects", "project"], ["pursuits", "pursuit"]]) {
    list(data[key], key).forEach((job, i) => {
      const path = `${key}[${i}]`;
      text(job?.id, `${path}.id`);
      if (jobIds.has(job?.id)) fail(`${path}.id`, `duplicate job id ${job.id}`);
      jobIds.add(job?.id);
      text(job?.name, `${path}.name`);
      text(job?.sector, `${path}.sector`);
      seats(job, path);
      if (kind === "pursuit") {
        if (typeof job?.probability !== "number" || job.probability < 0 || job.probability > 1) {
          fail(`${path}.probability`, "must be a number from 0 to 1");
        }
        month(job?.start, `${path}.start`);
      }
    });
  }

  list(data.assignments, "assignments").forEach((a, i) => {
    const path = `assignments[${i}]`;
    if (!personIds.has(a?.person)) fail(`${path}.person`, `unknown person ${a?.person}`);
    if (!jobIds.has(a?.job)) fail(`${path}.job`, `unknown job ${a?.job}`);
    text(a?.role, `${path}.role`);
    range(a, path);
    fraction(a?.fraction, `${path}.fraction`, 1);
    text(a?.source, `${path}.source`);
  });
  list(data.openQuestions ?? [], "openQuestions").forEach((q, i) => {
    text(q?.text, `openQuestions[${i}].text`);
    text(q?.source, `openQuestions[${i}].source`);
  });

  if (errors.length) throw new Error(`Invalid staffing data:\n- ${errors.join("\n- ")}`);
  return data;
}

export function defaultScenario(data) {
  return { pursuits: Object.fromEntries(data.pursuits.map((p) => [p.id, "weighted"])), moves: [] };
}

/** Validate a what-if scenario against its data. Throws on the first problem list. */
export function validateScenario(data, scenario) {
  const errors = [];
  const people = new Set(data.people.map((p) => p.id));
  const jobs = new Set([...data.projects, ...data.pursuits].map((j) => j.id));
  const months = new Set(horizonMonths(data.horizon));
  for (const [id, mode] of Object.entries(scenario?.pursuits ?? {})) {
    if (!data.pursuits.some((p) => p.id === id)) errors.push(`unknown pursuit ${id}`);
    if (!MODES.includes(mode)) errors.push(`pursuit ${id} mode must be weighted, won, or lost`);
  }
  (scenario?.moves ?? []).forEach((m, i) => {
    if (!people.has(m?.person)) errors.push(`moves[${i}]: unknown person ${m?.person}`);
    if (!jobs.has(m?.job)) errors.push(`moves[${i}]: unknown job ${m?.job}`);
    if (typeof m?.role !== "string" || !m.role.trim()) errors.push(`moves[${i}]: role is required`);
    if (!months.has(m?.from) || !months.has(m?.to) || m.from > m.to) errors.push(`moves[${i}]: months must be inside the horizon, from before to`);
    if (!Number.isInteger(m?.pct) || m.pct === 0 || m.pct < -100 || m.pct > 100) errors.push(`moves[${i}]: pct must be a whole percent from -100 to 100, not 0`);
  });
  if (errors.length) throw new Error(`Invalid scenario:\n- ${errors.join("\n- ")}`);
  return scenario;
}

// ---------- Analysis ----------

function groupRuns(items, key) {
  // Collapse consecutive month entries with the same key into ranges.
  const runs = [];
  for (const item of items) {
    const last = runs.at(-1);
    if (last && last.key === key(item) && addMonths(last.to, 1) === item.month) {
      last.to = item.month;
      last.items.push(item);
    } else {
      runs.push({ key: key(item), from: item.month, to: item.month, items: [item] });
    }
  }
  return runs;
}

function fitFor(data, seatRole, personRole) {
  if (seatRole === personRole) return "match";
  const fits = data.roleFits?.[seatRole] ?? {};
  if (fits.same?.includes(personRole)) return "match";
  if (fits.stepUp?.includes(personRole)) return "step-up";
  return null;
}

/** Compute the staffing picture for one scenario. Deterministic; never edits data. */
export function analyze(data, scenario = defaultScenario(data)) {
  const months = horizonMonths(data.horizon);
  const inHorizon = new Set(months);
  const people = data.people;
  const personById = Object.fromEntries(people.map((p) => [p.id, p]));
  const jobs = [
    ...data.projects.map((j) => ({ ...j, kind: "project", mode: "committed" })),
    ...data.pursuits.map((j) => ({ ...j, kind: "pursuit", mode: scenario.pursuits?.[j.id] ?? "weighted" })),
  ];
  const jobById = Object.fromEntries(jobs.map((j) => [j.id, j]));
  const isCommitted = (job) => job.kind === "project" || job.mode === "won";
  const threshold = (role) => toPct(data.thresholds?.[role] ?? data.thresholds?.default ?? 1);

  // Person x month cells.
  const cells = {};
  for (const p of people) {
    cells[p.id] = {};
    for (const m of months) {
      let capacity = 100;
      let status = "available";
      if ((p.start && m < p.start) || (p.end && m > p.end)) {
        capacity = 0;
        status = p.start && m < p.start ? "not started" : "departed";
      } else {
        for (const l of p.leave ?? []) {
          if (m >= l.from && m <= l.to) {
            capacity -= toPct(l.fraction);
            status = "leave";
          }
        }
        capacity = Math.max(0, capacity);
      }
      cells[p.id][m] = { capacity, status, committed: 0, tentative: 0, parts: {} };
    }
  }

  // Allocations from the staffing sheet plus what-if moves.
  const allocations = [
    ...data.assignments.map((a) => ({ ...a, pct: toPct(a.fraction), move: false })),
    ...(scenario.moves ?? []).map((m) => ({ ...m, move: true })),
  ];
  const moveIssues = [];
  for (const a of allocations) {
    const job = jobById[a.job];
    if (job.mode === "lost") continue;
    const tentative = !isCommitted(job);
    for (const m of months) {
      if (m < a.from || m > a.to) continue;
      const cell = cells[a.person][m];
      const partKey = `${a.job}|${a.role}`;
      const part = (cell.parts[partKey] ??= { job: a.job, role: a.role, pct: 0, tentative, moved: false });
      part.pct += a.pct;
      if (a.move) part.moved = true;
    }
  }
  for (const p of people) {
    for (const m of months) {
      const cell = cells[p.id][m];
      for (const part of Object.values(cell.parts)) {
        if (part.pct < 0) {
          moveIssues.push({ person: p.id, job: part.job, month: m, message: `${p.name} would go below 0% on ${part.job} in ${monthLabel(m)}; the reduction was capped at their allocation.` });
          part.pct = 0;
        }
        if (part.tentative) cell.tentative += part.pct;
        else cell.committed += part.pct;
      }
      cell.parts = Object.values(cell.parts).filter((part) => part.pct > 0);
    }
  }

  // Overloads: any rolling three-month window whose average load is over the role threshold.
  const overloads = [];
  const conflicts = [];
  for (const p of people) {
    const limit = threshold(p.role);
    const flagged = new Set();
    for (let i = 0; i < months.length; i++) {
      const window = months.slice(i, i + 3);
      if (window.length < Math.min(3, months.length)) break;
      // Months with no capacity (leave, not started, departed) are conflicts, not overloads.
      const working = window.filter((m) => cells[p.id][m].capacity > 0);
      if (!working.length) continue;
      const load = working.reduce((sum, m) => sum + cells[p.id][m].committed, 0);
      const capacity = working.reduce((sum, m) => sum + cells[p.id][m].capacity, 0);
      if (load * 100 > capacity * limit) working.forEach((m) => flagged.add(m));
    }
    const flaggedMonths = months.filter((m) => flagged.has(m)).map((month) => ({ month }));
    for (const run of groupRuns(flaggedMonths, () => "over")) {
      const runMonths = run.items.map((i) => i.month);
      const peakMonth = runMonths.reduce((a, b) => (cells[p.id][b].committed > cells[p.id][a].committed ? b : a));
      overloads.push({ person: p.id, from: run.from, to: run.to, peak: cells[p.id][peakMonth].committed, peakMonth, threshold: limit });
    }
    // Assigned while on leave, before starting, or after leaving.
    const blocked = months
      .filter((m) => cells[p.id][m].status !== "available" && cells[p.id][m].committed > cells[p.id][m].capacity)
      .map((month) => ({ month, status: cells[p.id][month].status }));
    for (const run of groupRuns(blocked, (i) => i.status)) {
      const jobsInRun = [...new Set(run.items.flatMap((i) => cells[p.id][i.month].parts.filter((x) => !x.tentative).map((x) => x.job)))];
      conflicts.push({ person: p.id, from: run.from, to: run.to, status: run.key, jobs: jobsInRun });
    }
  }

  // Seat coverage by job, role, and month.
  const seatGaps = [];
  for (const job of jobs) {
    if (job.mode === "lost") continue;
    const roles = [...new Set(job.seats.map((s) => s.role))];
    for (const role of roles) {
      const rows = [];
      for (const m of months) {
        const seatsNow = job.seats.filter((s) => s.role === role && m >= s.from && m <= s.to);
        const required = seatsNow.reduce((sum, s) => sum + toPct(s.fraction), 0);
        if (!required) continue;
        const filled = people.reduce(
          (sum, p) => sum + cells[p.id][m].parts.filter((x) => x.job === job.id && x.role === role).reduce((s, x) => s + x.pct, 0),
          0,
        );
        const gap = required - filled;
        if (gap > 0) {
          const certs = [...new Set(seatsNow.flatMap((s) => s.requires?.certs ?? []))].sort();
          rows.push({ month: m, gap, required, filled, certs });
        }
      }
      for (const run of groupRuns(rows, (r) => r.certs.join(","))) {
        const sizes = run.items.map((r) => r.gap);
        seatGaps.push({
          job: job.id,
          role,
          from: run.from,
          to: run.to,
          gap: Math.max(...sizes),
          gapMin: Math.min(...sizes),
          byMonth: Object.fromEntries(run.items.map((r) => [r.month, r.gap])),
          certs: run.items[0].certs,
          ifWon: job.kind === "pursuit" && job.mode === "weighted",
        });
      }
    }
  }

  // People filling a seat without its required certification.
  const certIssues = [];
  for (const job of jobs) {
    if (job.mode === "lost") continue;
    for (const p of people) {
      const missingByMonth = months
        .map((m) => {
          const certs = job.seats
            .filter((s) => s.requires?.certs?.length && m >= s.from && m <= s.to && cells[p.id][m].parts.some((x) => x.job === job.id && x.role === s.role))
            .flatMap((s) => s.requires.certs);
          const missing = [...new Set(certs)].filter((c) => !(p.certs ?? []).includes(c)).sort();
          return { month: m, missing };
        })
        .filter((r) => r.missing.length);
      for (const run of groupRuns(missingByMonth, (r) => r.missing.join(","))) {
        certIssues.push({ person: p.id, job: job.id, from: run.from, to: run.to, missing: run.items[0].missing, tentative: !isCommitted(job) });
      }
    }
  }

  // Internal candidates for each gap.
  for (const gap of seatGaps) {
    const job = jobById[gap.job];
    const gapMonths = months.filter((m) => m >= gap.from && m <= gap.to);
    const candidates = [];
    for (const p of people) {
      const fit = fitFor(data, gap.role, p.role);
      if (!fit) continue;
      const freeBy = Object.fromEntries(gapMonths.map((m) => [m, Math.max(0, cells[p.id][m].capacity - cells[p.id][m].committed)]));
      const covered = gapMonths.filter((m) => freeBy[m] >= gap.byMonth[m]);
      const freeMonths = gapMonths.filter((m) => freeBy[m] > 0);
      if (!freeMonths.length) continue;
      const missingCerts = gap.certs.filter((c) => !(p.certs ?? []).includes(c));
      const sectorMatch = (p.sectors ?? []).includes(job.sector);
      const pencilled = [
        ...new Set(gapMonths.flatMap((m) => cells[p.id][m].parts.filter((x) => x.tentative && x.job !== job.id).map((x) => x.job))),
      ];
      // Suggested move: the first stretch of free months with the same gap size, at what they can give.
      const startIndex = gapMonths.indexOf(freeMonths[0]);
      let end = startIndex;
      const startGap = gap.byMonth[gapMonths[startIndex]];
      while (end + 1 < gapMonths.length && freeBy[gapMonths[end + 1]] > 0 && gap.byMonth[gapMonths[end + 1]] === startGap) end++;
      const span = gapMonths.slice(startIndex, end + 1);
      const pct = Math.min(...span.map((m) => Math.min(freeBy[m], gap.byMonth[m])));
      const reasons = [
        covered.length === gapMonths.length
          ? `free for all of it`
          : covered.length
            ? `covers ${covered.length} of ${gapMonths.length} months, from ${monthLabel(covered[0])}`
            : `only ${Math.max(...freeMonths.map((m) => freeBy[m]))}% free, from ${monthLabel(freeMonths[0])}`,
      ];
      if (fit === "step-up") reasons.push(`step up from ${p.role}`);
      reasons.push(sectorMatch ? `${job.sector} experience` : `no ${job.sector} experience on the roster`);
      if (missingCerts.length) reasons.push(`missing ${missingCerts.join(", ")}`);
      if (pencilled.length) reasons.push(`pencilled on ${pencilled.join(", ")}`);
      candidates.push({
        person: p.id,
        fit,
        covered: covered.length,
        missingCerts,
        sectorMatch,
        pencilled,
        reasons,
        move: { person: p.id, job: gap.job, role: gap.role, from: span[0], to: span.at(-1), pct },
        sort: [fit === "step-up" ? 1 : 0, missingCerts.length, -covered.length, sectorMatch ? 0 : 1, pencilled.length, -freeMonths.length, p.name],
      });
    }
    candidates.sort((a, b) => {
      for (let i = 0; i < a.sort.length; i++) {
        if (a.sort[i] < b.sort[i]) return -1;
        if (a.sort[i] > b.sort[i]) return 1;
      }
      return 0;
    });
    gap.candidates = candidates.slice(0, 3).map(({ sort, ...c }) => c);
  }

  // Roll-offs: committed load drops by at least 25 points.
  const rollOffs = [];
  for (const p of people) {
    for (let i = 1; i < months.length; i++) {
      const before = cells[p.id][months[i - 1]];
      const after = cells[p.id][months[i]];
      if (after.capacity === 0) continue;
      if (before.committed - after.committed >= 25) {
        const ending = before.parts
          .filter((x) => !x.tentative && !after.parts.some((y) => y.job === x.job && y.role === x.role && y.pct >= x.pct))
          .map((x) => x.job);
        rollOffs.push({ person: p.id, month: months[i], from: before.committed, to: after.committed, jobs: [...new Set(ending)] });
      }
    }
  }

  // Role balance: supply minus committed load, committed gaps, and weighted pursuit demand.
  const roles = [...new Set([...people.map((p) => p.role), ...jobs.flatMap((j) => j.seats.map((s) => s.role))])];
  const roleBalance = {};
  for (const role of roles) {
    roleBalance[role] = months.map((m) => {
      const staff = people.filter((p) => p.role === role);
      const supply = staff.reduce((s, p) => s + cells[p.id][m].capacity, 0);
      const committed = staff.reduce((s, p) => s + cells[p.id][m].committed, 0);
      const openGaps = seatGaps
        .filter((g) => !g.ifWon && g.role === role)
        .reduce((s, g) => s + (g.byMonth[m] ?? 0), 0);
      const weighted = jobs
        .filter((j) => j.kind === "pursuit" && j.mode === "weighted")
        .reduce((s, j) => s + j.probability * j.seats.filter((x) => x.role === role && m >= x.from && m <= x.to).reduce((t, x) => t + toPct(x.fraction), 0), 0);
      return { month: m, supply, committed, openGaps, weighted: Math.round(weighted), balance: Math.round(supply - committed - openGaps - weighted) };
    });
  }
  const hiring = [];
  for (const role of roles) {
    const short = roleBalance[role].filter((r) => r.balance <= -50);
    for (const run of groupRuns(short, () => "short")) {
      if (run.items.length < 2) continue;
      const peak = Math.min(...run.items.map((r) => r.balance));
      const withoutPursuits = Math.min(...run.items.map((r) => r.balance + r.weighted));
      hiring.push({ role, from: run.from, to: run.to, peakShort: -peak, shortWithoutPursuits: withoutPursuits < 0 ? -withoutPursuits : 0 });
    }
  }

  // Pursuit risks: tentative people who would be overloaded if the pursuit is won.
  const pursuitRisks = [];
  for (const job of jobs.filter((j) => j.kind === "pursuit" && j.mode === "weighted")) {
    for (const p of people) {
      const limit = threshold(p.role);
      const risky = months
        .filter((m) => {
          const cell = cells[p.id][m];
          const extra = cell.parts.filter((x) => x.job === job.id).reduce((s, x) => s + x.pct, 0);
          return extra > 0 && cell.committed + extra > (cell.capacity * limit) / 100;
        })
        .map((month) => ({ month }));
      for (const run of groupRuns(risky, () => "risk")) {
        const peak = Math.max(...run.items.map((i) => cells[p.id][i.month].committed + cells[p.id][i.month].parts.filter((x) => x.job === job.id).reduce((s, x) => s + x.pct, 0)));
        pursuitRisks.push({ job: job.id, person: p.id, from: run.from, to: run.to, peak, threshold: limit });
      }
    }
  }

  rollOffs.sort((x, y) => x.month.localeCompare(y.month) || personById[x.person].name.localeCompare(personById[y.person].name));

  // Decisions for the meeting, most urgent first.
  const soonLimit = addMonths(months[0], 2);
  const name = (id) => personById[id].name;
  const jobName = (id) => jobById[id].name;
  const decisions = [];
  for (const c of conflicts) {
    decisions.push({
      urgency: c.from <= soonLimit ? "now" : "soon",
      month: c.from,
      title: `${name(c.person)} is assigned while ${statusText(c.status)}`,
      detail: `${rangeLabel(c.from, c.to)} on ${c.jobs.map(jobName).join(", ")}. Name cover or move the assignment.`,
    });
  }
  const committedGaps = seatGaps.filter((g) => !g.ifWon);
  for (const jobId of [...new Set(committedGaps.map((g) => g.job))]) {
    const gaps = committedGaps.filter((g) => g.job === jobId);
    const from = gaps.map((g) => g.from).sort()[0];
    const option = (g) => {
      const top = g.candidates[0];
      return top ? `best internal option ${name(top.person)} (${top.reasons.join("; ")})` : "no internal candidate has capacity";
    };
    if (gaps.length === 1) {
      const g = gaps[0];
      decisions.push({
        urgency: from <= soonLimit ? "now" : "soon",
        month: from,
        title: `${jobName(jobId)} needs ${article(g.role)} ${g.role}${g.gap === 100 && g.gapMin === 100 ? "" : ` (${gapLabel(g)})`} from ${monthLabel(g.from)}`,
        detail: `${rangeLabel(g.from, g.to)}${g.certs.length ? `, requires ${g.certs.join(", ")}` : ""}; ${option(g)}.`,
      });
    } else {
      decisions.push({
        urgency: from <= soonLimit ? "now" : "soon",
        month: from,
        title: `${jobName(jobId)} has ${gaps.length} unfilled seats from ${monthLabel(from)}`,
        detail: "Seats the staffing sheet leaves open:",
        items: gaps.map((g) => `${g.role} ${gapLabel(g)} ${rangeLabel(g.from, g.to)}${g.certs.length ? ` (requires ${g.certs.join(", ")})` : ""}: ${option(g)}`),
      });
    }
  }
  for (const c of certIssues) {
    decisions.push({
      urgency: c.tentative ? "watch" : c.from <= soonLimit ? "now" : "soon",
      month: c.from,
      title: `${name(c.person)} ${c.tentative ? "is pencilled on" : "is assigned to"} ${jobName(c.job)} without ${c.missing.join(", ")}`,
      detail: `${rangeLabel(c.from, c.to)}. The seat requires ${c.missing.join(", ")}; the roster does not list it. Schedule the training or name someone certified.`,
    });
  }
  for (const o of overloads) {
    decisions.push({
      urgency: o.from <= soonLimit ? "now" : "soon",
      month: o.from,
      title: `${name(o.person)} is over capacity ${rangeLabel(o.from, o.to)}`,
      detail: `Peaks at ${o.peak}% in ${monthLabel(o.peakMonth)} against a ${o.threshold}% limit for ${personById[o.person].role}.`,
    });
  }
  for (const r of pursuitRisks) {
    decisions.push({
      urgency: "watch",
      month: r.from,
      title: `If ${jobName(r.job)} is won, ${name(r.person)} goes to ${r.peak}%`,
      detail: `${rangeLabel(r.from, r.to)} against a ${r.threshold}% limit. Pencilled on the pursuit while still committed elsewhere.`,
    });
  }
  for (const h of hiring) {
    decisions.push({
      urgency: "watch",
      month: h.from,
      title: `${h.role}s run ${fte(h.peakShort)} short ${rangeLabel(h.from, h.to)}`,
      detail: h.shortWithoutPursuits
        ? `${fte(h.shortWithoutPursuits)} short on committed work alone; the rest is weighted pursuit demand.`
        : "Short only once pursuits are weighted by win probability.",
    });
  }
  const order = { now: 0, soon: 1, watch: 2 };
  decisions.sort((a, b) => order[a.urgency] - order[b.urgency] || a.month.localeCompare(b.month) || a.title.localeCompare(b.title));

  return { months, cells, overloads, conflicts, certIssues, seatGaps, rollOffs, roleBalance, hiring, pursuitRisks, decisions, moveIssues, jobs: jobById };
}

// ---------- Rendering ----------

export function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function loadClass(load, capacity, limit) {
  if (capacity === 0) return load > 0 ? "over" : "off";
  const ratio = (load / capacity) * 100;
  if (ratio > limit) return "over";
  if (ratio > 100) return "high";
  if (ratio >= 75) return "full";
  if (ratio > 0) return "part";
  return "free";
}

function table(head, rows, empty, caption) {
  if (!rows.length) return `<p class="empty">${esc(empty)}</p>`;
  return `<div class="table-wrap"><table>${caption ? `<caption class="sr-only">${esc(caption)}</caption>` : ""}<thead><tr>${head.map((h) => `<th scope="col">${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody></table></div>`;
}

/** Render the interactive plan body. The same markup is pre-rendered by plan.mjs. */
export function renderApp(data, scenario, a) {
  const people = data.people;
  const personById = Object.fromEntries(people.map((p) => [p.id, p]));
  const name = (id) => esc(personById[id].name);
  const jobName = (id) => esc(a.jobs[id].name);
  const limit = (role) => toPct(data.thresholds?.[role] ?? data.thresholds?.default ?? 1);
  const roles = [...new Set(people.map((p) => p.role))];
  const counts = {
    now: a.decisions.filter((d) => d.urgency === "now").length,
    gaps: a.seatGaps.filter((g) => !g.ifWon).length,
    over: a.overloads.length,
  };
  const wonCount = Object.values(scenario.pursuits).filter((m) => m === "won").length;
  const lostCount = Object.values(scenario.pursuits).filter((m) => m === "lost").length;

  const decisions = a.decisions
    .map(
      (d) =>
        `<li class="decision ${d.urgency}"><span class="badge">${d.urgency === "now" ? "Decide now" : d.urgency === "soon" ? "Plan" : "Watch"}</span><div><strong>${esc(d.title)}</strong><p>${esc(d.detail)}</p>${d.items ? `<ul>${d.items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>` : ""}</div></li>`,
    )
    .join("");

  const pursuits = data.pursuits
    .map((p) => {
      const mode = scenario.pursuits[p.id] ?? "weighted";
      const radios = MODES.map(
        (m) =>
          `<label class="seg ${mode === m ? "on" : ""}"><input type="radio" name="mode-${esc(p.id)}" id="mode-${esc(p.id)}-${m}" value="${m}" data-pursuit="${esc(p.id)}" ${mode === m ? "checked" : ""}>${m === "weighted" ? `${Math.round(p.probability * 100)}%` : m === "won" ? "Won" : "Lost"}</label>`,
      ).join("");
      const ifWon = a.seatGaps.filter((g) => g.job === p.id).map((g) => `${esc(g.role)} ${gapLabel(g)}`).join(", ");
      return `<tr><th scope="row"><span class="code">${esc(p.id)}</span> ${esc(p.name)}<div class="sub">${esc(p.stage ?? "")}${p.value ? ` · $${(p.value / 1e6).toFixed(1)}M` : ""}</div></th><td>${monthLabel(p.start)}</td><td><fieldset class="segmented"><legend class="sr-only">${esc(p.name)} scenario</legend>${radios}</fieldset></td><td>${mode === "lost" ? "Not counted" : ifWon || "Fully pencilled"}</td></tr>`;
    })
    .join("");

  const header = a.months.map((m) => `<th scope="col">${esc(monthLabel(m))}</th>`).join("");
  const gridRows = roles
    .map((role) => {
      const rows = people
        .filter((p) => p.role === role)
        .map((p) => {
          const cellsHtml = a.months
            .map((m) => {
              const c = a.cells[p.id][m];
              const cls = loadClass(c.committed, c.capacity, limit(p.role));
              const committed = c.parts.filter((x) => !x.tentative);
              const tentative = c.parts.filter((x) => x.tentative);
              const tip = [
                ...committed.map((x) => `${x.job} ${x.pct}%${x.moved ? " (what-if)" : ""}`),
                ...tentative.map((x) => `${x.job}? ${x.pct}% pencilled`),
                c.status !== "available" ? c.status : "",
              ].filter(Boolean).join(", ") || "Unassigned";
              const label = c.capacity === 0 && !c.committed ? (c.status === "departed" ? "gone" : c.status === "not started" ? "starts later" : "leave") : `${c.committed}%`;
              return `<td class="cell ${cls}${tentative.length ? " tentative" : ""}${committed.some((x) => x.moved) ? " moved" : ""}${c.status === "leave" ? " leave" : ""}" title="${esc(tip)}"><span class="pct">${esc(label)}${c.tentative ? ` <i>+${c.tentative}%?</i>` : ""}</span><span class="jobs">${esc(committed.map((x) => x.job).join(" "))}${tentative.length ? ` <i>${esc(tentative.map((x) => `${x.job}?`).join(" "))}</i>` : ""}</span></td>`;
            })
            .join("");
          return `<tr><th scope="row" class="person">${name(p.id)}</th>${cellsHtml}</tr>`;
        })
        .join("");
      return `<tr class="group"><th scope="rowgroup" colspan="${a.months.length + 1}">${esc(role)}s <span class="sub">limit ${limit(role)}%</span></th></tr>${rows}`;
    })
    .join("");

  const gapRows = a.seatGaps.map((g) => {
    const cands = g.candidates.length
      ? `<ol class="cands">${g.candidates
          .map(
            (c) =>
              `<li><strong>${name(c.person)}</strong> <span class="sub">${esc(c.reasons.join("; "))}</span> <button type="button" class="try" data-try='${esc(JSON.stringify(c.move))}'>Try</button></li>`,
          )
          .join("")}</ol>`
      : `<span class="sub">No internal candidate has capacity</span>`;
    return `<tr class="${g.ifWon ? "ifwon" : ""}"><th scope="row">${jobName(g.job)}${g.ifWon ? ` <span class="pill">if won</span>` : ""}</th><td>${esc(g.role)}${g.certs.length ? `<div class="sub">requires ${esc(g.certs.join(", "))}</div>` : ""}</td><td class="when">${esc(rangeLabel(g.from, g.to))}</td><td class="num">${gapLabel(g)}</td><td>${cands}</td></tr>`;
  });

  const overRows = a.overloads.map(
    (o) => `<tr><th scope="row">${name(o.person)}</th><td>${esc(personById[o.person].role)}</td><td>${esc(rangeLabel(o.from, o.to))}</td><td class="num">${o.peak}% in ${esc(monthLabel(o.peakMonth))}</td><td class="num">${o.threshold}%</td></tr>`,
  );
  const conflictRows = a.conflicts.map(
    (c) => `<tr><th scope="row">${name(c.person)}</th><td>${esc(statusText(c.status))}</td><td>${esc(rangeLabel(c.from, c.to))}</td><td>${c.jobs.map(jobName).join(", ")}</td></tr>`,
  );
  const certRows = a.certIssues.map(
    (c) => `<tr><th scope="row">${name(c.person)}</th><td>${jobName(c.job)}${c.tentative ? ` <span class="pill">pencilled</span>` : ""}</td><td>${esc(rangeLabel(c.from, c.to))}</td><td>${esc(c.missing.join(", "))}</td></tr>`,
  );
  const rollRows = a.rollOffs.map(
    (r) => `<tr><th scope="row">${name(r.person)}</th><td>${esc(personById[r.person].role)}</td><td>${esc(monthLabel(r.month))}</td><td class="num">${r.from}% → ${r.to}%</td><td>${r.jobs.map(jobName).join(", ") || "—"}</td></tr>`,
  );
  const balanceRows = Object.entries(a.roleBalance)
    .filter(([, rows]) => rows.some((r) => r.supply || r.openGaps || r.weighted))
    .map(
      ([role, rows]) =>
        `<tr><th scope="row">${esc(role)}</th>${rows.map((r) => `<td class="num ${r.balance <= -50 ? "neg" : r.balance < 0 ? "warn" : ""}" title="supply ${fte(r.supply)}, committed ${fte(r.committed)}, open seats ${fte(r.openGaps)}, weighted pursuits ${fte(r.weighted)}">${r.balance > 0 ? "+" : ""}${(r.balance / 100).toFixed(1)}</td>`).join("")}</tr>`,
    );
  const moves = (scenario.moves ?? []).map(
    (m, i) =>
      `<li><span>${name(m.person)} ${m.pct > 0 ? "+" : ""}${m.pct}% on ${jobName(m.job)} as ${esc(m.role)}, ${esc(rangeLabel(m.from, m.to))}${m.note ? ` <span class="sub">${esc(m.note)}</span>` : ""}</span><button type="button" data-remove-move="${i}" aria-label="Remove move ${i + 1}">Remove</button></li>`,
  );
  const questions = (data.openQuestions ?? []).map((q) => `<li>${esc(q.text)} <span class="sub">${esc(q.source)}</span></li>`).join("");

  const personOptions = roles
    .map((role) => `<optgroup label="${esc(role)}s">${people.filter((p) => p.role === role).map((p) => `<option value="${esc(p.id)}">${esc(p.name)}</option>`).join("")}</optgroup>`)
    .join("");
  const jobOptions = [
    `<optgroup label="Projects">${data.projects.map((j) => `<option value="${esc(j.id)}">${esc(j.id)} · ${esc(j.name)}</option>`).join("")}</optgroup>`,
    `<optgroup label="Pursuits">${data.pursuits.map((j) => `<option value="${esc(j.id)}">${esc(j.id)} · ${esc(j.name)}</option>`).join("")}</optgroup>`,
  ].join("");
  const monthOptions = a.months.map((m) => `<option value="${m}">${esc(monthLabel(m))}</option>`).join("");
  const roleOptions = [...new Set([...roles, ...data.projects.flatMap((j) => j.seats.map((s) => s.role))])]
    .map((r) => `<option value="${esc(r)}">${esc(r)}</option>`)
    .join("");

  return `
<header class="top">
  <div>
    <p class="eyebrow">Staffing plan · ${esc(data.company.name)} · as of ${esc(data.asOf)}</p>
    <h1>${esc(rangeLabel(a.months[0], a.months.at(-1)))}</h1>
    <p class="summary"><strong>${plural(counts.now, "decision")}</strong> needed now · <strong>${plural(counts.gaps, "unfilled seat")}</strong> · <strong>${plural(counts.over, "overload")}</strong> · scenario: ${wonCount} won, ${lostCount} lost, ${plural((scenario.moves ?? []).length, "what-if move")}</p>
  </div>
  <div class="actions">
    <button type="button" id="export-json">Export scenario</button>
    <label class="file">Import scenario<input type="file" id="import-json" accept="application/json,.json"></label>
    <button type="button" id="export-csv">Export grid CSV</button>
    <button type="button" id="reset">Reset</button>
  </div>
</header>
<p id="status" role="status" class="status"></p>
${a.moveIssues.length ? `<ul class="issues">${a.moveIssues.map((m) => `<li>${esc(m.message)}</li>`).join("")}</ul>` : ""}
<section aria-labelledby="h-decisions"><h2 id="h-decisions">Decisions for this meeting</h2><ol class="decisions">${decisions || `<li class="empty">Nothing needs a decision in this scenario.</li>`}</ol></section>
<section aria-labelledby="h-pursuits"><h2 id="h-pursuits">Pursuits</h2><p class="hint">Weighted counts each pursuit at its win probability in role totals; pencilled names stay tentative. Won commits them. Lost removes the pursuit.</p>
${table(["Pursuit", "Start", "Scenario", "Unfilled if won"], [pursuits], "No pursuits supplied.", "Pursuits and their scenario")}</section>
<section aria-labelledby="h-grid"><h2 id="h-grid">Who is where</h2><p class="hint">Committed allocation by month. Dashed cells also carry pencilled pursuit work (job codes with ?). Hover a cell for the breakdown.</p>
<div class="grid-wrap" tabindex="0" role="region" aria-labelledby="h-grid"><table class="grid"><thead><tr><th scope="col">Person</th>${header}</tr></thead><tbody>${gridRows}</tbody></table></div>
<p class="legend"><span class="cell free">free</span><span class="cell part">part</span><span class="cell full">75–100%</span><span class="cell high">over 100%</span><span class="cell over">over limit</span><span class="cell tentative">pencilled</span><span class="cell moved">what-if</span></p></section>
<section aria-labelledby="h-gaps"><h2 id="h-gaps">Unfilled seats</h2>${table(["Job", "Role", "When", "Gap", "Internal options (Try adds a what-if move)"], gapRows, "Every seat is filled in this scenario.", "Unfilled seats")}</section>
<section aria-labelledby="h-moves"><h2 id="h-moves">What-if moves</h2>
<form id="move-form" class="move-form">
  <label>Person<select name="person" required>${personOptions}</select></label>
  <label>Job<select name="job" required>${jobOptions}</select></label>
  <label>Role<select name="role" required>${roleOptions}</select></label>
  <label>From<select name="from" required>${monthOptions}</select></label>
  <label>To<select name="to" required>${monthOptions}</select></label>
  <label>Change %<input name="pct" type="number" min="-100" max="100" step="5" value="50" required></label>
  <label class="wide">Note<input name="note" type="text" placeholder="Why, for the record"></label>
  <button type="submit">Add move</button>
</form>
${moves.length ? `<ul class="moves">${moves.join("")}</ul>` : `<p class="empty">No what-if moves yet. Nothing here changes the staffing sheet.</p>`}</section>
<section aria-labelledby="h-over"><h2 id="h-over">Overloads and conflicts</h2>
${table(["Person", "Role", "Rolling 3-month window", "Peak", "Limit"], overRows, "Nobody is over their limit.", "Overloads")}
${table(["Person", "Status", "When", "Still assigned to"], conflictRows, "Nobody is assigned while unavailable.", "Assignment conflicts")}
${table(["Person", "Job", "When", "Missing certification"], certRows, "Everyone in a seat has its required certifications.", "Missing certifications")}</section>
<section aria-labelledby="h-roll"><h2 id="h-roll">Roll-offs</h2>${table(["Person", "Role", "From", "Load", "Ending"], rollRows, "No roll-offs in the horizon.", "Roll-offs")}</section>
<section aria-labelledby="h-balance"><h2 id="h-balance">Role balance (FTE, negative is short)</h2><p class="hint">Supply minus committed load, open seats, and weighted pursuit demand. Hover for the parts.</p>
${table(["Role", ...a.months.map(monthLabel)], balanceRows, "No roles.", "Role balance by month")}</section>
${questions ? `<section aria-labelledby="h-q"><h2 id="h-q">Open questions from the source files</h2><ul class="questions">${questions}</ul></section>` : ""}
<footer class="foot">Proposal for review. Nothing here changes an assignment or notifies anyone. Calculated from the supplied files; thresholds: ${esc(Object.entries(data.thresholds ?? {}).map(([r, v]) => `${r} ${toPct(v)}%`).join(", "))}.</footer>`;
}

/** Markdown brief for chat or email, from the same analysis. */
export function renderBrief(data, scenario, a) {
  const personById = Object.fromEntries(data.people.map((p) => [p.id, p]));
  const name = (id) => personById[id].name;
  const jobName = (id) => a.jobs[id].name;
  const lines = [];
  lines.push(`# Staffing meeting brief: ${data.company.name}`);
  lines.push("");
  lines.push(`As of ${data.asOf}. Horizon ${rangeLabel(a.months[0], a.months.at(-1))}. Pursuits: ${data.pursuits.map((p) => `${p.id} ${scenario.pursuits[p.id] === "weighted" ? `${Math.round(p.probability * 100)}%` : scenario.pursuits[p.id]}`).join(", ")}. What-if moves: ${(scenario.moves ?? []).length}.`);
  lines.push("");
  lines.push("## Decisions");
  lines.push("");
  if (!a.decisions.length) lines.push("Nothing needs a decision in this scenario.");
  a.decisions.forEach((d, i) => {
    lines.push(`${i + 1}. **${d.urgency === "now" ? "Decide now" : d.urgency === "soon" ? "Plan" : "Watch"}: ${d.title}.** ${d.detail}`);
    for (const item of d.items ?? []) lines.push(`   - ${item}`);
  });
  lines.push("");
  lines.push("## Unfilled seats");
  lines.push("");
  const gaps = a.seatGaps.filter((g) => !g.ifWon);
  if (!gaps.length) lines.push("Every committed seat is filled.");
  else {
    lines.push("| Job | Role | When | Gap | Best internal options |");
    lines.push("|---|---|---|---:|---|");
    for (const g of gaps) {
      lines.push(`| ${jobName(g.job)} | ${g.role}${g.certs.length ? ` (requires ${g.certs.join(", ")})` : ""} | ${rangeLabel(g.from, g.to)} | ${gapLabel(g)} | ${g.candidates.map((c) => `${name(c.person)}: ${c.reasons.join("; ")}`).join("<br>") || "None with capacity"} |`);
    }
  }
  lines.push("");
  lines.push("## Overloads and conflicts");
  lines.push("");
  if (!a.overloads.length && !a.conflicts.length && !a.certIssues.length) lines.push("Nobody is over their limit or assigned while unavailable.");
  for (const o of a.overloads) lines.push(`- ${name(o.person)} (${personById[o.person].role}): ${rangeLabel(o.from, o.to)}, peak ${o.peak}% in ${monthLabel(o.peakMonth)}, limit ${o.threshold}%.`);
  for (const c of a.conflicts) lines.push(`- ${name(c.person)}: assigned ${rangeLabel(c.from, c.to)} while ${statusText(c.status)} (${c.jobs.map(jobName).join(", ")}).`);
  for (const c of a.certIssues) lines.push(`- ${name(c.person)}: ${c.tentative ? "pencilled on" : "assigned to"} ${jobName(c.job)} ${rangeLabel(c.from, c.to)} without ${c.missing.join(", ")}.`);
  lines.push("");
  lines.push("## Roll-offs");
  lines.push("");
  const soonRollOffs = a.rollOffs.filter((r) => r.month <= addMonths(a.months[0], 5));
  lines.splice(lines.length - 2, 1, "## Roll-offs in the next six months");
  if (!soonRollOffs.length) lines.push("No roll-offs in the next six months.");
  for (const r of soonRollOffs) lines.push(`- ${monthLabel(r.month)}: ${name(r.person)} ${r.from}% → ${r.to}%${r.jobs.length ? ` (${r.jobs.map(jobName).join(", ")} ending)` : ""}.`);
  lines.push("");
  lines.push("## If pursuits are won");
  lines.push("");
  lines.push("| Pursuit | Win % | Start | Unfilled if won | Pencilled people who would go over |");
  lines.push("|---|---:|---|---|---|");
  for (const p of data.pursuits) {
    const gaps = a.seatGaps.filter((g) => g.job === p.id && g.ifWon).map((g) => `${g.role} ${gapLabel(g)}`).join(", ");
    const risks = a.pursuitRisks.filter((r) => r.job === p.id).map((r) => `${name(r.person)} ${r.peak}%`).join(", ");
    lines.push(`| ${p.name} | ${Math.round(p.probability * 100)}% | ${monthLabel(p.start)} | ${scenario.pursuits[p.id] === "weighted" ? gaps || "Fully pencilled" : scenario.pursuits[p.id]} | ${risks || "None"} |`);
  }
  if (a.hiring.length) {
    lines.push("");
    lines.push("## Hiring signal");
    lines.push("");
    for (const h of a.hiring) lines.push(`- ${h.role}: ${fte(h.peakShort)} short ${rangeLabel(h.from, h.to)}${h.shortWithoutPursuits ? ` (${fte(h.shortWithoutPursuits)} short on committed work alone)` : " (only with weighted pursuits)"}.`);
  }
  if (data.openQuestions?.length) {
    lines.push("");
    lines.push("## Open questions");
    lines.push("");
    for (const q of data.openQuestions) lines.push(`- ${q.text} (${q.source})`);
  }
  lines.push("");
  lines.push("Proposal for review. Nothing was changed in the staffing sheet and nobody was notified.");
  return `${lines.join("\n")}\n`;
}

/** Person x month grid as CSV, for pasting back into the staffing sheet. */
export function gridCsv(data, a) {
  const quote = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
  const rows = [["Person", "Role", ...a.months.map(monthLabel)]];
  for (const p of data.people) {
    rows.push([
      p.name,
      p.role,
      ...a.months.map((m) => {
        const c = a.cells[p.id][m];
        return c.parts.map((x) => `${x.job}${x.tentative ? "?" : ""} ${x.pct}%`).join(" / ") || (c.capacity === 0 ? c.status : "");
      }),
    ]);
  }
  return `${rows.map((r) => r.map(quote).join(",")).join("\n")}\n`;
}
