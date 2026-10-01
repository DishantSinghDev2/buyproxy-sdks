# SDK conformance suite

A tiny mock of the BuyProxy API (`mock-server.mjs`) plus a canonical sequence of **28 requests** (`expected-log.json`).
Every SDK has a smoke script that replays the sequence; `verify.mjs` then checks the mock's request log — method, path,
query string, JSON body (key order ignored), `X-API-Key`, `Idempotency-Key`, `Content-Type` and the `buyproxy-*`
user agent — and fails on the first difference.

It also covers behaviours, not just paths: a `401` raises the typed auth error, a `429` with `Retry-After: 0` is retried
transparently, and a `402` raises the typed insufficient-bandwidth error.

```bash
./run-all.sh              # every language that's installed
./run-all.sh node go      # a subset
```

When you change an endpoint, update `mock-server.mjs` and `expected-log.json`, then fix every SDK until the suite is green.
