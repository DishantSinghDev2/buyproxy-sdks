// Mock of the BuyProxy API used to prove every SDK speaks the same wire protocol.
import http from "node:http";

const log = [];
let rateLimitSeen = false;

const json = (res, status, body, headers = {}) => {
  res.writeHead(status, { "content-type": "application/json", ...headers });
  res.end(JSON.stringify(body));
};

const plan = {
  id: "plan_1", productId: "residential-lite", productKey: "residential", name: "Core Residential", label: null,
  dataGbRemaining: 8.5, dataGbTotal: 10, expiresAt: null, createdAt: "2026-10-01T00:00:00.000Z",
  generate: { maxCount: 1000, maxStickyMinutes: 60, protocols: ["http", "socks5"], targeting: { country: true, state: true, city: true, isp: false } },
};
const customer = { username: "bp_acme_1", label: "Acme", status: "active", createdAt: "2026-10-01T00:00:00.000Z" };
const tx = { id: "st_abc", kind: "topup", status: "succeeded", paymentMethod: "card", interval: null, amountCents: 1990, currency: "usd", gb: 10, productKey: "residential", plan: null, resellerPool: false, createdAt: "2026-10-01T00:00:00.000Z" };
const pool = [{ productKey: "residential", productId: "residential-lite", label: "Core Residential", gb: 50 }];

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x");
  if (url.pathname === "/__log") return json(res, 200, log);
  if (url.pathname === "/__reset") { log.length = 0; rateLimitSeen = false; return json(res, 200, {}); }

  let raw = "";
  for await (const c of req) raw += c;
  const key = req.headers["x-api-key"];
  log.push({
    method: req.method,
    path: url.pathname + url.search,
    body: raw ? JSON.parse(raw) : null,
    apiKey: key ?? null,
    idempotencyKey: req.headers["idempotency-key"] ?? null,
    contentType: raw ? req.headers["content-type"] : null,
    userAgent: /^buyproxy-/.test(req.headers["user-agent"] ?? ""),
  });

  const p = url.pathname, m = req.method;
  if (key === "bad") return json(res, 401, { error: "Invalid BuyProxy API key" });
  if (key === "ratelimit-once" && !rateLimitSeen) { rateLimitSeen = true; return json(res, 429, { error: "Rate limit exceeded — 60 requests/minute" }, { "retry-after": "0" }); }
  if (key === "broke") return json(res, 402, { error: "Not enough Core Residential in your reseller pool" });

  if (p === "/v1/products" && m === "GET") return json(res, 200, {
    products: [{ productKey: "residential", productId: "residential-lite", name: "Core Residential", description: "d", minGb: 1, pricePerGbCents: 199, currency: "usd" }],
    volumeBonus: { thresholdGb: 100, rate: 0.1 }, plans: [{ plan: "pro", monthlyPriceCents: 3000, includedGb: 20 }] });
  if (p === "/v1/account") return json(res, 200, { email: "a@b.co", name: "A", plan: "pro", planExpiresAt: null, balanceGb: 4.2, createdAt: "2026-10-01T00:00:00.000Z" });
  if (p === "/v1/balances") return json(res, 200, { balances: [{ productKey: "residential", productId: "residential-lite", planId: "plan_1", activeGb: 8.5, pendingGb: 0, totalGb: 8.5, expiresAt: null }] });
  if (p === "/v1/plans" && m === "GET") return json(res, 200, { plans: [plan] });
  if (/^\/v1\/plans\/[^/]+\/generate$/.test(p)) return json(res, 200, { lines: ["user-country-us:pw@gw.buyproxy.org:6969", "user2-country-us:pw2@gw.buyproxy.org:6969"] });
  if (p === "/v1/topup/card") return json(res, 200, { payUrl: "https://checkout.stripe.com/c/pay/x", transactionId: "st_abc" });
  if (p === "/v1/topup/crypto") return json(res, 200, { url: "https://nowpayments.io/payment/?iid=1", transactionId: "crypto_abc" });
  if (p === "/v1/transactions" && m === "GET") return json(res, 200, { transactions: [tx] });
  if (p.startsWith("/v1/transactions/")) return json(res, 200, tx);
  if (p === "/v1/me") return json(res, 200, { email: "a@b.co", customerCount: 1, activeCustomerCount: 1, pool });
  if (p === "/v1/customers" && m === "GET") return json(res, 200, { customers: [customer] });
  if (p === "/v1/customers" && m === "POST") return json(res, 201, customer);
  if (/^\/v1\/customers\/[^/]+$/.test(p) && m === "GET") return json(res, 200, { ...customer, plans: [{ ...plan, remainingGb: 8.5 }], pending: [{ productId: "residential-premium", productKey: "premium", gb: 2 }] });
  if (/^\/v1\/customers\/[^/]+$/.test(p) && m === "PATCH") return json(res, 200, { ...customer, status: "suspended" });
  if (/\/usage$/.test(p)) return json(res, 200, { plans: [{ id: "plan_1", productId: "residential-lite", productKey: "residential", remainingGb: 8.5, totalGb: 10, usedGb: 1.5, expiresAt: null }], pending: [] });
  if (/\/allocate$/.test(p)) return json(res, 201, { productKey: "premium", productId: "residential-premium", gb: 10, alreadyApplied: false, poolRemainingGb: 40 });
  if (/^\/v1\/customers\/[^/]+\/generate$/.test(p)) return json(res, 200, { lines: ["acme-country-de:pw@gw.buyproxy.org:6969"] });
  if (p === "/v1/pool") return json(res, 200, { pool });
  if (p === "/v1/pool/topup/card") return json(res, 200, { payUrl: "https://checkout.stripe.com/c/pay/pool", transactionId: "st_pool" });
  if (p === "/v1/pool/topup/crypto") return json(res, 200, { url: "https://nowpayments.io/payment/?iid=2", transactionId: "crypto_pool" });
  if (p === "/api/auth/signup") return json(res, 200, { ok: true, cooldownSeconds: 60 });
  if (p === "/api/auth/verify-otp") return json(res, 200, { ok: true, isNew: true, user: { email: "a@b.co", name: "A" } });
  if (p === "/api/auth/resend-otp") return json(res, 200, { ok: true });
  return json(res, 404, { error: "Not found" });
});

const port = Number(process.env.PORT || 4010);
server.listen(port, () => console.log(`mock listening on ${port}`));
