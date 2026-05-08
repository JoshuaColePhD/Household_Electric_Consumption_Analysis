import { cp, mkdir, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const dist = path.join(root, "dist");

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

for (const entry of ["index.html", "assets", "figures", "data"]) {
  const source = path.join(root, entry);
  if (existsSync(source)) {
    await cp(source, path.join(dist, entry), { recursive: true });
  }
}

console.log("Static dashboard built to dist/");
