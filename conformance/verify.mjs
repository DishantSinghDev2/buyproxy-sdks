// Usage: node verify.mjs  — compares the mock's recorded requests with expected-log.json.
import { readFileSync } from "node:fs";
const sortDeep = (v) => Array.isArray(v) ? v.map(sortDeep) : v && typeof v === "object" ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, sortDeep(v[k])])) : v;
const base = process.env.MOCK || "http://127.0.0.1:4010";
const expected = JSON.parse(readFileSync(new URL("./expected-log.json", import.meta.url)));
const actual = await (await fetch(`${base}/__log`)).json();
let bad = 0;
const fail = (i, msg) => { bad++; console.error(`  ✗ call #${i + 1}: ${msg}`); };
if (actual.length !== expected.length) { bad++; console.error(`  ✗ expected ${expected.length} requests, got ${actual.length}`); }
expected.forEach((e, i) => {
  const a = actual[i]; if (!a) return;
  if (a.method !== e.method) fail(i, `method ${a.method} != ${e.method}`);
  if (a.path !== e.path) fail(i, `path ${a.path} != ${e.path}`);
  if (JSON.stringify(sortDeep(a.body)) !== JSON.stringify(sortDeep(e.body))) fail(i, `body ${JSON.stringify(a.body)} != ${JSON.stringify(e.body)}`);
  if (e.path !== "/v1/products" && a.apiKey !== e.apiKey) fail(i, `api key ${a.apiKey} != ${e.apiKey}`);
  if ((a.idempotencyKey ?? null) !== (e.idempotencyKey ?? null)) fail(i, `idempotency ${a.idempotencyKey} != ${e.idempotencyKey ?? null}`);
  if (e.contentType && !String(a.contentType).startsWith(e.contentType)) fail(i, `content-type ${a.contentType}`);
  if (!a.userAgent) fail(i, `user-agent missing the buyproxy-* prefix`);
});
console.log(bad ? `FAILED (${bad})` : `PASS — ${expected.length} requests identical to the canonical sequence`);
process.exit(bad ? 1 : 0);
