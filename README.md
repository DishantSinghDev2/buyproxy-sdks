# BuyProxy SDKs & CLI — Official Residential Proxy API Libraries

Official client libraries for the [BuyProxy](https://www.buyproxy.org) proxy API. Generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and run a **proxy reseller** business — in your language, with full types.

> **Payments changed on 9 November 2026.** BuyProxy now sells from one prepaid wallet. The per-product top-up calls in this README (card and crypto top-ups for a product, and reseller pool top-ups) are retired: the API refuses them with a message that names the call to use. Until this SDK adds wallet methods, add money with `POST /v1/wallet/topup` and buy with `POST /v1/wallet/purchase` (resellers buy pool bandwidth with `POST /v1/pool/purchase`); see the [API reference](https://www.buyproxy.org/docs/api-reference/introduction). Plan subscriptions by card still work. The [Go SDK](https://github.com/DishantSinghDev2/buyproxy-go) has the wallet methods from v1.1.0.

| Language | Package | Install | Repo |
|---|---|---|---|
| **TypeScript / Node.js** | `buyproxy` | Coming soon (not on its registry yet) | [buyproxy-node](https://github.com/DishantSinghDev2/buyproxy-node) |
| **Python** | `buyproxy` | Coming soon (not on its registry yet) | [buyproxy-python](https://github.com/DishantSinghDev2/buyproxy-python) |
| **Go** | `github.com/DishantSinghDev2/buyproxy-go` | `go get github.com/DishantSinghDev2/buyproxy-go` | [buyproxy-go](https://github.com/DishantSinghDev2/buyproxy-go) |
| **PHP** | `buyproxy/buyproxy` | Coming soon (not on its registry yet) | [buyproxy-php](https://github.com/DishantSinghDev2/buyproxy-php) |
| **Ruby** | `buyproxy` | Coming soon (not on its registry yet) | [buyproxy-ruby](https://github.com/DishantSinghDev2/buyproxy-ruby) |
| **Java** | `org.buyproxy:buyproxy` | Coming soon (not on its registry yet) | [buyproxy-java](https://github.com/DishantSinghDev2/buyproxy-java) |
| **C# / .NET** | `BuyProxy` | Coming soon (not on its registry yet) | [buyproxy-dotnet](https://github.com/DishantSinghDev2/buyproxy-dotnet) |
| **Rust** | `buyproxy` | Coming soon (not on its registry yet) | [buyproxy-rust](https://github.com/DishantSinghDev2/buyproxy-rust) |
| **CLI** | `buyproxy-cli` | Coming soon (not on its registry yet) | [buyproxy-cli](https://github.com/DishantSinghDev2/buyproxy-cli) |

> Packages appear on their registries as each library is released — see [docs/RELEASING.md](docs/RELEASING.md).

## What every SDK does

- **Generate proxies** — rotating or sticky sessions, HTTP or SOCKS5, country targeting (state, city and ASN on Premium Residential)
- **Account & billing** — balances per product, wallet deposits by card (Stripe) or crypto, plan subscriptions by card, payment history with `wait`-until-settled
- **Reseller API** — buy bandwidth into a pool, create isolated customers, allocate GB (idempotent), suspend / reactivate, generate on their behalf
- **Account creation without a browser** — signup + email-code verification
- **Resilience built in** — typed errors, `Retry-After`-aware retries for rate limits, safe-by-default retry rules for writes
- **Framework helpers** — Playwright, Puppeteer, requests, httpx, Scrapy, Guzzle, Laravel, Faraday, `HttpClient`, reqwest and more

## One behaviour, eight languages

All SDKs are verified against the **same mock API and the same 28-request sequence** ([`conformance/`](conformance)): method, path, query, JSON body, API key, idempotency key and user agent must match exactly, and `401` / `402` / `429` handling must behave the same. A change to the API lands in every SDK or the suite fails.

```bash
./conformance/run-all.sh
```

## Quick look

```ts
import { BuyProxy } from "buyproxy";

const bp = new BuyProxy(); // reads BUYPROXY_API_KEY
const [plan] = await bp.plans.list();
const { proxies } = await bp.plans.generate(plan.id, { country: "US", count: 5 });
console.log(proxies[0].url); // http://user-country-us:pass@gw.buyproxy.org:6969
```

```python
from buyproxy import BuyProxy

proxy = BuyProxy().plans.generate(plan_id, country="US").proxies[0]
requests.get("https://api.ipify.org", proxies=proxy.to_requests())
```

```bash
buyproxy generate residential -c US -n 5     # or just run `buyproxy` for the interactive UI
```

## Links

- Documentation: <https://www.buyproxy.org/docs/sdks>
- API reference: <https://www.buyproxy.org/docs/api-reference/introduction> · OpenAPI: <https://www.buyproxy.org/openapi.yaml>
- Get an API key: <https://www.buyproxy.org/dashboard/api-keys>
- Support: <support@buyproxy.org>

## License

[MIT](LICENSE) © BuyProxy
