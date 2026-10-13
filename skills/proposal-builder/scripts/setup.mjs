#!/usr/bin/env node
// Install pinned pdfcn registry components into a NEW user-owned workspace.
import { mkdir, writeFile, copyFile, rm } from "node:fs/promises";
import { resolve, dirname, relative, isAbsolute } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
const revision = "39c75c1abbbad7b89ad1d8d3ea740ef635818a4b";
const target = process.argv[2];
if (!target) throw new Error("Usage: node setup.mjs NEW_WORKSPACE");
const root = resolve(target);
await mkdir(root); // Fail rather than overwrite an existing project.
try {
const base = `https://raw.githubusercontent.com/shadcn-labs/pdfcn/${revision}/`;
async function download(path) {
  const response = await fetch(base + path);
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
  return response.text();
}
const installed = new Set();
async function install(name) {
  if (installed.has(name)) return;
  installed.add(name);
  const entry = JSON.parse(await download(`apps/web/public/r/${name}.json`));
  for (const dependency of entry.registryDependencies ?? []) {
    if (!dependency.startsWith("@pdfcn/"))
      throw new Error(`Unexpected registry: ${dependency}`);
    await install(dependency.slice(7));
  }
  for (const file of entry.files) {
    const path = resolve(root, file.target);
    const rel = relative(root, path);
    if (!rel || rel.startsWith("..") || isAbsolute(rel))
      throw new Error("Registry path escapes workspace");
    await mkdir(dirname(path), { recursive: true });
    await writeFile(path, file.content);
  }
}
await install("forme/text");
await install("forme/table");
await writeFile(resolve(root, "PDFCN-LICENSE"), await download("LICENSE"));
await writeFile(
  resolve(root, "pdfcn-source.json"),
  JSON.stringify(
    {
      repository: "https://github.com/shadcn-labs/pdfcn",
      revision,
      components: [...installed],
    },
    null,
    2,
  ),
);
await writeFile(
  resolve(root, "package.json"),
  JSON.stringify(
    {
      private: true,
      type: "module",
      scripts: { render: "tsx render.tsx" },
      dependencies: {
        "@formepdf/core": "0.25.0",
        "@formepdf/react": "0.25.0",
        react: "19.2.5",
        tsx: "4.21.0",
      },
    },
    null,
    2,
  ),
);
await writeFile(
  resolve(root, "tsconfig.json"),
  JSON.stringify(
    {
      compilerOptions: {
        jsx: "react-jsx",
        baseUrl: ".",
        paths: { "@/*": ["./*"] },
      },
    },
    null,
    2,
  ),
);
const templates = fileURLToPath(new URL("../templates/", import.meta.url));
for (const name of ["render.tsx", "proposal-core.mjs", "package-lock.json"])
  await copyFile(resolve(templates, name), resolve(root, name));
execFileSync(process.platform === "win32" ? "npm.cmd" : "npm", ["ci", "--ignore-scripts", "--no-audit", "--no-fund"], {
  cwd: root,
  stdio: "inherit",
  shell: process.platform === "win32",
});
} catch (error) {
  // Leave nothing half-built behind, so a rerun can start clean.
  await rm(root, { recursive: true, force: true });
  throw error;
}
console.log(
  `Ready: ${root}. Render with npm run render -- proposal.json proposal.pdf`,
);
