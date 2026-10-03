// Keep commercial figures in integer cents; never infer rates, taxes or terms.
export function validate(data) {
  const text = (value, path) => {
    if (typeof value !== "string" || !value.trim())
      throw new Error(`${path} must be nonempty text`);
  };
  if (!data || typeof data !== "object" || Array.isArray(data))
    throw new Error("Proposal must be an object");
  for (const key of [
    "project",
    "client",
    "contractor",
    "date",
    "reference",
    "summary",
    "currency",
  ])
    text(data[key], key);
  if (!/^[A-Z]{3}$/.test(data.currency))
    throw new Error("currency must be an ISO currency code");
  if (!["DRAFT", "FOR REVIEW"].includes(data.status))
    throw new Error("status must be DRAFT or FOR REVIEW");
  for (const key of [
    "scope",
    "approach",
    "team",
    "schedule",
    "exclusions",
    "questions",
  ]) {
    if (!Array.isArray(data[key]) || !data[key].length)
      throw new Error(`${key} must be a nonempty array`);
    for (const [i, row] of data[key].entries()) {
      text(row?.text, `${key}[${i}].text`);
      text(row?.source, `${key}[${i}].source`);
    }
  }
  if (!Array.isArray(data.pricing) || !data.pricing.length)
    throw new Error("pricing must be a nonempty array");
  const ids = new Set();
  for (const row of data.pricing) {
    for (const key of ["id", "label", "source"])
      text(row?.[key], `pricing.${key}`);
    if (ids.has(row.id)) throw new Error("Duplicate pricing ID");
    ids.add(row.id);
    if (!["base", "option"].includes(row.kind))
      throw new Error("Price kind must be base or option");
    if (!Number.isSafeInteger(row.cents))
      throw new Error("Price must use safe integer cents");
  }
  const total = data.pricing
    .filter((p) => p.kind === "base")
    .reduce((sum, p) => sum + BigInt(p.cents), 0n);
  if (
    !Number.isSafeInteger(data.baseTotalCents) ||
    total !== BigInt(data.baseTotalCents)
  )
    throw new Error(
      "Base total does not reconcile; options must stay separate",
    );
  return data;
}
