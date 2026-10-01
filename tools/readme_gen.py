#!/usr/bin/env python3
"""readme_gen.py <sdks-dir> — writes README.md for every SDK repo from one template + per-language snippets."""
import sys, pathlib
root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
GH = "DishantSinghDev2"

L = {}

L["node"] = dict(
    repo="buyproxy-node", pkg="buyproxy", title="BuyProxy Node.js SDK",
    h1="BuyProxy Node.js & TypeScript SDK — Residential Proxy API Client",
    pitch="The official **Node.js / TypeScript SDK** for [BuyProxy](https://www.buyproxy.org): generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and run a **proxy reseller** business — all from one typed client with zero runtime dependencies.",
    badges=[
        "[![npm](https://img.shields.io/npm/v/buyproxy?logo=npm&color=cb3837)](https://www.npmjs.com/package/buyproxy)",
        "[![downloads](https://img.shields.io/npm/dm/buyproxy)](https://www.npmjs.com/package/buyproxy)",
        f"[![CI](https://github.com/{GH}/buyproxy-node/actions/workflows/ci.yml/badge.svg)](https://github.com/{GH}/buyproxy-node/actions/workflows/ci.yml)",
        "![types](https://img.shields.io/badge/types-included-3178c6?logo=typescript&logoColor=white)",
        "[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)",
    ],
    requires="Node.js 18+, Bun, Deno, Cloudflare Workers and any runtime with a global `fetch`. Ships ESM and CommonJS builds with full `.d.ts` types.",
    install="```bash\nnpm install buyproxy\n# or: pnpm add buyproxy · yarn add buyproxy · bun add buyproxy\n```",
    features=["Zero dependencies — uses the platform's `fetch`", "Complete TypeScript types for every request and response", "Automatic retries with back-off for rate limits (`429`) and transient errors", "Typed errors: `AuthenticationError`, `InsufficientBandwidthError`, `RateLimitError`, …", "Helpers for **Playwright**, **Puppeteer**, **Axios** and environment variables"],
    quickstart='''```ts
import { BuyProxy } from "buyproxy";

const bp = new BuyProxy({ apiKey: process.env.BUYPROXY_API_KEY }); // or just set BUYPROXY_API_KEY

// 1. See what you have
const balances = await bp.balances.list();
const [plan] = await bp.plans.list();

// 2. Generate 5 US proxies in Austin, rotating on every request
const { proxies } = await bp.plans.generate(plan.id, { country: "US", city: "Austin", count: 5 });

console.log(proxies[0].url); // http://user-country-us-city-austin:pass@gw.buyproxy.org:6969
```

Add `stickyMinutes: 10` to keep the same IP for ten minutes, or `protocol: "socks5"` for SOCKS5.''',
    frameworks=[
        ("Playwright", '''```ts
import { chromium } from "playwright";

const browser = await chromium.launch({ proxy: proxies[0].toPlaywright() });
const page = await browser.newPage();
await page.goto("https://api.ipify.org");
```'''),
        ("Puppeteer", '''```ts
import puppeteer from "puppeteer";

const { args, credentials } = proxies[0].toPuppeteer();
const browser = await puppeteer.launch({ args });
const page = await browser.newPage();
await page.authenticate(credentials);
```'''),
        ("Axios", '''```ts
import axios from "axios";

const { data } = await axios.get("https://api.ipify.org", { proxy: proxies[0].toAxios() });
```'''),
        ("Node.js `fetch` / undici", '''```ts
import { ProxyAgent } from "undici";

const res = await fetch("https://api.ipify.org", { dispatcher: new ProxyAgent(proxies[0].url) });
```'''),
        ("curl & shell", '''```ts
console.log(proxies[0].toCurl());   // curl -x 'http://user:pass@gw.buyproxy.org:6969' https://api.ipify.org
console.log(proxies[0].toEnv());    // { HTTP_PROXY, HTTPS_PROXY, ALL_PROXY, … }
```'''),
    ],
    payments='''```ts
// Buy 10 GB of Core Residential by card — open payUrl in a browser
const { payUrl, transactionId } = await bp.topup.card({ kind: "topup", productKey: "residential", gb: 10 });

// Or subscribe to a plan (monthly or yearly)
await bp.topup.card({ kind: "plan", plan: "pro", interval: "year" });

// Crypto (pay-as-you-go top-ups only)
await bp.topup.crypto({ productKey: "residential", gb: 50 });

// Wait for the payment to settle — GB appears on bp.balances.list() right after
const tx = await bp.transactions.wait(transactionId!);
console.log(tx.status); // "succeeded"
```''',
    reseller='''```ts
const reseller = new BuyProxy({ apiKey: process.env.BUYPROXY_RESELLER_KEY }); // bp_live_… key

await reseller.reseller.pool.topupCard({ productKey: "residential", gb: 500 });     // buy into your pool
const customer = await reseller.reseller.customers.create({ label: "Acme Inc" });   // isolated sub-account

await reseller.reseller.customers.allocate(customer.username, {
  productKey: "residential", gb: 20, idempotencyKey: "order-1042",                  // safe to retry
});

const { proxies } = await reseller.reseller.customers.generate(customer.username, {
  planId: (await reseller.reseller.customers.get(customer.username)).plans[0].id,
  country: "DE",
});

await reseller.reseller.customers.update(customer.username, { status: "suspended" });
```''',
    errors='''```ts
import { BuyProxy, AuthenticationError, InsufficientBandwidthError, RateLimitError } from "buyproxy";

try {
  await bp.plans.generate(planId);
} catch (err) {
  if (err instanceof InsufficientBandwidthError) console.log("Out of GB — top up first");
  else if (err instanceof RateLimitError) console.log(`Slow down; retry in ${err.retryAfterSeconds}s`);
  else if (err instanceof AuthenticationError) console.log("Check your API key");
  else throw err;
}
```
Every error extends `BuyProxyError` and exposes `status` and the parsed `body`.''',
    config='''```ts
new BuyProxy({
  apiKey: "bp_key_…",          // default: process.env.BUYPROXY_API_KEY
  baseUrl: "https://www.buyproxy.org",
  timeoutMs: 30_000,
  maxRetries: 2,                // 429s always; 5xx only for safe requests
  fetch: myFetch,               // bring your own fetch
});
```''',
    api=[
        ("Catalog & prices", "`bp.products.list()`"), ("Account", "`bp.account.get()`"), ("Spendable GB per product", "`bp.balances.list()`"),
        ("Plans", "`bp.plans.list()`"), ("Generate proxies", "`bp.plans.generate(planId, params)`"),
        ("Card checkout", "`bp.topup.card(params)`"), ("Crypto checkout", "`bp.topup.crypto(params)`"),
        ("Payments", "`bp.transactions.list()` · `.get(id)` · `.wait(id)`"), ("Create an account", "`bp.auth.signup()` · `.verifyOtp()` · `.resendOtp()`"),
        ("Reseller summary", "`bp.reseller.me()`"), ("Customers", "`bp.reseller.customers.list/create/get/update/usage/allocate/generate`"),
        ("Reseller pool", "`bp.reseller.pool.get/topupCard/topupCrypto`"),
    ],
    dev="```bash\nnpm install\nnpm run typecheck && npm test && npm run build\n```",
)

L["python"] = dict(
    repo="buyproxy-python", pkg="buyproxy", title="BuyProxy Python SDK",
    h1="BuyProxy Python SDK — Residential Proxy API Client (sync & async)",
    pitch="The official **Python SDK** for [BuyProxy](https://www.buyproxy.org): generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and manage **reseller** customers — with a fully typed sync **and** async client built on `httpx`.",
    badges=[
        "[![PyPI](https://img.shields.io/pypi/v/buyproxy?logo=pypi&logoColor=white)](https://pypi.org/project/buyproxy/)",
        "[![Python](https://img.shields.io/pypi/pyversions/buyproxy)](https://pypi.org/project/buyproxy/)",
        f"[![CI](https://github.com/{GH}/buyproxy-python/actions/workflows/ci.yml/badge.svg)](https://github.com/{GH}/buyproxy-python/actions/workflows/ci.yml)",
        "![typed](https://img.shields.io/badge/typed-mypy%20strict-blue)",
        "[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)",
    ],
    requires="Python 3.9+. Ships `py.typed`; passes `mypy --strict`.",
    install="```bash\npip install buyproxy\n# or: uv add buyproxy · poetry add buyproxy\n```",
    features=["Sync (`BuyProxy`) and async (`AsyncBuyProxy`) clients with identical APIs", "Typed dataclass models — autocomplete everywhere, unknown fields never break you", "Automatic retries with back-off for rate limits and transient errors", "One-line helpers for **requests**, **httpx**, **aiohttp**, **Playwright** and **Scrapy**"],
    quickstart='''```python
from buyproxy import BuyProxy

bp = BuyProxy()  # reads BUYPROXY_API_KEY — or BuyProxy(api_key="bp_key_…")

plan = bp.plans.list()[0]
result = bp.plans.generate(plan.id, country="US", city="Austin", count=5)

proxy = result.proxies[0]
print(proxy.url)  # http://user-country-us-city-austin:pass@gw.buyproxy.org:6969
```

Pass `sticky_minutes=10` to keep the same IP for ten minutes, or `protocol="socks5"` for SOCKS5.

**Async:**

```python
from buyproxy import AsyncBuyProxy

async with AsyncBuyProxy() as bp:
    plans = await bp.plans.list()
    result = await bp.plans.generate(plans[0].id, country="DE", count=3)
```''',
    frameworks=[
        ("requests", '''```python
import requests

print(requests.get("https://api.ipify.org", proxies=proxy.to_requests()).text)
```'''),
        ("httpx", '''```python
import httpx

with httpx.Client(proxy=proxy.to_httpx()) as client:
    print(client.get("https://api.ipify.org").text)
```'''),
        ("aiohttp", '''```python
async with aiohttp.ClientSession() as session:
    async with session.get("https://api.ipify.org", proxy=proxy.to_aiohttp()) as r:
        print(await r.text())
```'''),
        ("Playwright", '''```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(proxy=proxy.to_playwright())
    page = browser.new_page()
    page.goto("https://api.ipify.org")
```'''),
        ("Scrapy", '''```python
def start_requests(self):
    yield scrapy.Request("https://api.ipify.org", meta=proxy.to_scrapy_meta())
```'''),
    ],
    payments='''```python
# Buy 10 GB of Core Residential by card — open pay_url in a browser
checkout = bp.topup.card(product_key="residential", gb=10)
print(checkout.pay_url)

# Or subscribe to a plan (monthly or yearly)
bp.topup.card(plan="pro", interval="year")

# Crypto (pay-as-you-go top-ups only)
bp.topup.crypto(product_key="residential", gb=50)

# Wait for the payment to settle — GB appears on bp.balances.list() right after
tx = bp.transactions.wait(checkout.transaction_id)
print(tx.status)  # "succeeded"
```''',
    reseller='''```python
reseller = BuyProxy(api_key="bp_live_…")

reseller.reseller.pool.topup_card(product_key="residential", gb=500)       # buy into your pool
customer = reseller.reseller.customers.create("Acme Inc")                  # isolated sub-account

reseller.reseller.customers.allocate(
    customer.username, product_key="residential", gb=20, idempotency_key="order-1042",  # safe to retry
)

detail = reseller.reseller.customers.get(customer.username)
result = reseller.reseller.customers.generate(customer.username, plan_id=detail.plans[0].id, country="DE")

reseller.reseller.customers.update(customer.username, status="suspended")
```''',
    errors='''```python
from buyproxy import AuthenticationError, InsufficientBandwidthError, RateLimitError

try:
    bp.plans.generate(plan_id)
except InsufficientBandwidthError:
    print("Out of GB — top up first")
except RateLimitError as e:
    print(f"Slow down; retry in {e.retry_after_seconds}s")
except AuthenticationError:
    print("Check your API key")
```
Every exception extends `BuyProxyError` and carries `.status` and the parsed `.body`.''',
    config='''```python
BuyProxy(
    api_key="bp_key_…",            # default: $BUYPROXY_API_KEY
    base_url="https://www.buyproxy.org",
    timeout=30.0,
    max_retries=2,                  # 429s always; 5xx only for safe requests
    http_client=my_httpx_client,    # bring your own httpx.Client
)
```''',
    api=[
        ("Catalog & prices", "`bp.products.list()`"), ("Account", "`bp.account.get()`"), ("Spendable GB per product", "`bp.balances.list()`"),
        ("Plans", "`bp.plans.list()`"), ("Generate proxies", "`bp.plans.generate(plan_id, **params)`"),
        ("Card checkout", "`bp.topup.card(...)`"), ("Crypto checkout", "`bp.topup.crypto(...)`"),
        ("Payments", "`bp.transactions.list()` · `.get(id)` · `.wait(id)`"), ("Create an account", "`bp.auth.signup()` · `.verify_otp()` · `.resend_otp()`"),
        ("Reseller summary", "`bp.reseller.me()`"), ("Customers", "`bp.reseller.customers.list/create/get/update/usage/allocate/generate`"),
        ("Reseller pool", "`bp.reseller.pool.get/topup_card/topup_crypto`"),
    ],
    dev='```bash\npython -m venv .venv && . .venv/bin/activate\npip install -e ".[dev]"\nruff check src tests && mypy src && pytest\n```',
)

L["go"] = dict(
    repo="buyproxy-go", pkg="github.com/DishantSinghDev2/buyproxy-go", title="BuyProxy Go SDK",
    h1="BuyProxy Go SDK — Residential Proxy API Client for Golang",
    pitch="The official **Go SDK** for [BuyProxy](https://www.buyproxy.org): generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and manage **reseller** customers. Idiomatic Go — `context` on every call, `errors.Is` sentinels, and **zero third-party dependencies**.",
    badges=[
        f"[![Go Reference](https://pkg.go.dev/badge/github.com/{GH}/buyproxy-go.svg)](https://pkg.go.dev/github.com/{GH}/buyproxy-go)",
        f"[![CI](https://github.com/{GH}/buyproxy-go/actions/workflows/ci.yml/badge.svg)](https://github.com/{GH}/buyproxy-go/actions/workflows/ci.yml)",
        f"[![Go Report Card](https://goreportcard.com/badge/github.com/{GH}/buyproxy-go)](https://goreportcard.com/report/github.com/{GH}/buyproxy-go)",
        "[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)",
    ],
    requires="Go 1.21+. Standard library only.",
    install=f"```bash\ngo get github.com/{GH}/buyproxy-go\n```",
    features=["Standard library only — no transitive dependencies", "`context.Context` on every call; safe for concurrent use", "`errors.Is(err, buyproxy.ErrInsufficientBandwidth)` and friends", "`Proxy.HTTPClient()` returns an `*http.Client` already routed through the proxy"],
    quickstart=f'''```go
package main

import (
	"context"
	"fmt"
	"io"
	"log"

	buyproxy "github.com/{GH}/buyproxy-go"
)

func main() {{
	ctx := context.Background()
	client := buyproxy.New() // reads BUYPROXY_API_KEY — or buyproxy.WithAPIKey("bp_key_…")

	plans, err := client.Plans.List(ctx)
	if err != nil || len(plans) == 0 {{
		log.Fatal("no plans yet — top up first: ", err)
	}}

	res, err := client.Plans.Generate(ctx, plans[0].ID, &buyproxy.GenerateParams{{Country: "US", City: "Austin", Count: 5}})
	if err != nil {{
		log.Fatal(err)
	}}

	resp, err := res.Proxies[0].HTTPClient().Get("https://api.ipify.org")
	if err != nil {{
		log.Fatal(err)
	}}
	defer resp.Body.Close()
	ip, _ := io.ReadAll(resp.Body)
	fmt.Println("exit IP:", string(ip))
}}
```

Set `StickyMinutes: 10` to keep the same IP for ten minutes, or `Protocol: buyproxy.SOCKS5` for SOCKS5.''',
    frameworks=[
        ("net/http", '''```go
proxy := res.Proxies[0]

client := &http.Client{Transport: &http.Transport{Proxy: http.ProxyURL(proxy.URL())}}
// or simply: client := proxy.HTTPClient()
```'''),
        ("Colly", '''```go
c := colly.NewCollector()
c.SetProxyFunc(http.ProxyURL(res.Proxies[0].URL()))
```'''),
        ("chromedp / Rod", '''```go
opts := append(chromedp.DefaultExecAllocatorOptions[:],
	chromedp.ProxyServer(res.Proxies[0].URL().Host)) // add auth via a fetch.AuthRequired handler
```'''),
        ("curl & shell", '''```go
fmt.Println(res.Proxies[0].Curl())  // ready-to-run curl command
fmt.Println(res.Proxies[0].Env())   // HTTP_PROXY, HTTPS_PROXY, ALL_PROXY, …
```'''),
    ],
    payments='''```go
// Buy 10 GB of Core Residential by card — open PayURL in a browser
checkout, _ := client.Topup.Card(ctx, buyproxy.TopupCardParams(buyproxy.ProductResidential, 10))
fmt.Println(checkout.PayURL)

// Or subscribe to a plan (monthly or yearly)
client.Topup.Card(ctx, buyproxy.PlanCardParams(buyproxy.PlanPro, buyproxy.Yearly))

// Crypto (pay-as-you-go top-ups only)
client.Topup.Crypto(ctx, buyproxy.ProductResidential, 50)

// Wait for the payment to settle — GB appears on client.Balances.List right after
tx, _ := client.Transactions.Wait(ctx, *checkout.TransactionID, 3*time.Second)
fmt.Println(tx.Status) // "succeeded"
```''',
    reseller='''```go
reseller := buyproxy.New(buyproxy.WithAPIKey("bp_live_…"))

reseller.Reseller.Pool.TopupCard(ctx, buyproxy.PoolTopupParams{ProductKey: buyproxy.ProductResidential, GB: 500})
customer, _ := reseller.Reseller.Customers.Create(ctx, "Acme Inc") // isolated sub-account

reseller.Reseller.Customers.Allocate(ctx, customer.Username, buyproxy.AllocateParams{
	ProductKey: buyproxy.ProductResidential, GB: 20, IdempotencyKey: "order-1042", // safe to retry
})

detail, _ := reseller.Reseller.Customers.Get(ctx, customer.Username)
res, _ := reseller.Reseller.Customers.Generate(ctx, customer.Username, buyproxy.CustomerGenerateParams{
	PlanID: detail.Plans[0].ID, GenerateParams: buyproxy.GenerateParams{Country: "DE"},
})

reseller.Reseller.Customers.Update(ctx, customer.Username, buyproxy.CustomerUpdate{Status: buyproxy.CustomerSuspended})
```''',
    errors='''```go
_, err := client.Plans.Generate(ctx, planID, nil)

switch {
case errors.Is(err, buyproxy.ErrInsufficientBandwidth):
	log.Println("Out of GB — top up first")
case errors.Is(err, buyproxy.ErrRateLimited):
	var apiErr *buyproxy.APIError
	errors.As(err, &apiErr)
	log.Printf("Slow down; retry in %s", apiErr.RetryAfter)
case errors.Is(err, buyproxy.ErrAuthentication):
	log.Println("Check your API key")
}
```
Non-2xx responses are `*buyproxy.APIError` (with `Status`, `Message`, `Body`); network failures are `*buyproxy.ConnectionError`.''',
    config='''```go
client := buyproxy.New(
	buyproxy.WithAPIKey("bp_key_…"),            // default: $BUYPROXY_API_KEY
	buyproxy.WithBaseURL("https://www.buyproxy.org"),
	buyproxy.WithHTTPClient(&http.Client{Timeout: 10 * time.Second}),
	buyproxy.WithMaxRetries(2),                  // 429s always; 5xx only for safe requests
)
```''',
    api=[
        ("Catalog & prices", "`client.Products.List(ctx)`"), ("Account", "`client.Account.Get(ctx)`"), ("Spendable GB per product", "`client.Balances.List(ctx)`"),
        ("Plans", "`client.Plans.List(ctx)`"), ("Generate proxies", "`client.Plans.Generate(ctx, planID, params)`"),
        ("Card checkout", "`client.Topup.Card(ctx, params)`"), ("Crypto checkout", "`client.Topup.Crypto(ctx, product, gb)`"),
        ("Payments", "`client.Transactions.List/Get/Wait`"), ("Create an account", "`client.Auth.Signup/VerifyOTP/ResendOTP`"),
        ("Reseller summary", "`client.Reseller.Me(ctx)`"), ("Customers", "`client.Reseller.Customers.List/Create/Get/Update/Usage/Allocate/Generate`"),
        ("Reseller pool", "`client.Reseller.Pool.Get/TopupCard/TopupCrypto`"),
    ],
    dev="```bash\ngo vet ./... && go test -race ./...\n```",
)

L["php"] = dict(
    repo="buyproxy-php", pkg="buyproxy/buyproxy", title="BuyProxy PHP SDK",
    h1="BuyProxy PHP SDK — Residential Proxy API Client for Laravel, Symfony & PHP",
    pitch="The official **PHP SDK** for [BuyProxy](https://www.buyproxy.org): generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and manage **reseller** customers. PHP 8.1+, typed, named arguments, works with **Laravel**, **Symfony**, Guzzle and plain cURL.",
    badges=[
        "[![Packagist](https://img.shields.io/packagist/v/buyproxy/buyproxy?logo=packagist&logoColor=white)](https://packagist.org/packages/buyproxy/buyproxy)",
        "[![PHP](https://img.shields.io/packagist/php-v/buyproxy/buyproxy)](https://packagist.org/packages/buyproxy/buyproxy)",
        f"[![CI](https://github.com/{GH}/buyproxy-php/actions/workflows/ci.yml/badge.svg)](https://github.com/{GH}/buyproxy-php/actions/workflows/ci.yml)",
        "[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)",
    ],
    requires="PHP 8.1+ with `ext-curl` and `ext-json`. No other runtime dependencies.",
    install="```bash\ncomposer require buyproxy/buyproxy\n```",
    features=["Typed `readonly` models and exceptions", "PHP 8 named arguments: `generate($planId, country: 'US', count: 5)`", "Pluggable HTTP transport (cURL by default) — swap in Guzzle or Symfony HttpClient", "Helpers for **Guzzle**, **Laravel `Http`**, **Symfony HttpClient** and raw **cURL**"],
    quickstart='''```php
<?php
require 'vendor/autoload.php';

use BuyProxy\\Client;

$bp = new Client(apiKey: getenv('BUYPROXY_API_KEY')); // or omit it — reads BUYPROXY_API_KEY

$plan = $bp->plans->list()[0];
$result = $bp->plans->generate($plan->id, country: 'US', city: 'Austin', count: 5);

echo $result->proxies[0]->url(); // http://user-country-us-city-austin:pass@gw.buyproxy.org:6969
```

Pass `stickyMinutes: 10` to keep the same IP for ten minutes, or `protocol: 'socks5'` for SOCKS5.''',
    frameworks=[
        ("Guzzle", '''```php
$http = new GuzzleHttp\\Client($result->proxies[0]->toGuzzle());
echo $http->get('https://api.ipify.org')->getBody();
```'''),
        ("Laravel", '''```php
use Illuminate\\Support\\Facades\\Http;

$ip = Http::withOptions($result->proxies[0]->toGuzzle())->get('https://api.ipify.org')->body();
```

Register the client once in a service provider:

```php
$this->app->singleton(\\BuyProxy\\Client::class, fn () => new \\BuyProxy\\Client(apiKey: config('services.buyproxy.key')));
```'''),
        ("Symfony HttpClient", '''```php
$client = Symfony\\Component\\HttpClient\\HttpClient::create($result->proxies[0]->toSymfony());
echo $client->request('GET', 'https://api.ipify.org')->getContent();
```'''),
        ("cURL", '''```php
$ch = curl_init('https://api.ipify.org');
curl_setopt_array($ch, $result->proxies[0]->toCurl() + [CURLOPT_RETURNTRANSFER => true]);
echo curl_exec($ch);
```'''),
    ],
    payments='''```php
// Buy 10 GB of Core Residential by card — send the customer to payUrl
$checkout = $bp->topup->card(productKey: 'residential', gb: 10);
header('Location: ' . $checkout->payUrl);

// Or subscribe to a plan (monthly or yearly)
$bp->topup->card(plan: 'pro', interval: 'year');

// Crypto (pay-as-you-go top-ups only)
$bp->topup->crypto('residential', 50);

// Wait for the payment to settle — GB appears on $bp->balances->list() right after
$tx = $bp->transactions->wait($checkout->transactionId);
echo $tx->status; // "succeeded"
```''',
    reseller='''```php
$reseller = new Client(apiKey: 'bp_live_…');

$reseller->reseller->pool->topupCard('residential', 500);           // buy into your pool
$customer = $reseller->reseller->customers->create('Acme Inc');     // isolated sub-account

$reseller->reseller->customers->allocate($customer->username, 'residential', 20, idempotencyKey: 'order-1042');

$detail = $reseller->reseller->customers->get($customer->username);
$result = $reseller->reseller->customers->generate($customer->username, $detail->plans[0]->id, country: 'DE');

$reseller->reseller->customers->update($customer->username, status: 'suspended');
```''',
    errors='''```php
use BuyProxy\\Exceptions\\{AuthenticationException, InsufficientBandwidthException, RateLimitException};

try {
    $bp->plans->generate($planId);
} catch (InsufficientBandwidthException) {
    echo 'Out of GB — top up first';
} catch (RateLimitException $e) {
    echo "Slow down; retry in {$e->retryAfterSeconds}s";
} catch (AuthenticationException) {
    echo 'Check your API key';
}
```
Every exception extends `BuyProxy\\Exceptions\\BuyProxyException` and exposes `->status` and `->body`.''',
    config='''```php
new Client(
    apiKey: 'bp_key_…',                 // default: getenv('BUYPROXY_API_KEY')
    baseUrl: 'https://www.buyproxy.org',
    timeout: 30.0,
    maxRetries: 2,                       // 429s always; 5xx only for safe requests
    transport: new MyGuzzleTransport(),  // implement BuyProxy\\Http\\Transport
);
```''',
    api=[
        ("Catalog & prices", "`$bp->products->list()`"), ("Account", "`$bp->account->get()`"), ("Spendable GB per product", "`$bp->balances->list()`"),
        ("Plans", "`$bp->plans->list()`"), ("Generate proxies", "`$bp->plans->generate($planId, …)`"),
        ("Card checkout", "`$bp->topup->card(…)`"), ("Crypto checkout", "`$bp->topup->crypto($product, $gb)`"),
        ("Payments", "`$bp->transactions->list()` · `->get($id)` · `->wait($id)`"), ("Create an account", "`$bp->auth->signup()` · `->verifyOtp()` · `->resendOtp()`"),
        ("Reseller summary", "`$bp->reseller->me()`"), ("Customers", "`$bp->reseller->customers->list/create/get/update/usage/allocate/generate`"),
        ("Reseller pool", "`$bp->reseller->pool->get/topupCard/topupCrypto`"),
    ],
    dev="```bash\ncomposer install\nvendor/bin/phpunit\n```",
)

L["ruby"] = dict(
    repo="buyproxy-ruby", pkg="buyproxy", title="BuyProxy Ruby SDK",
    h1="BuyProxy Ruby SDK — Residential Proxy API Client Gem",
    pitch="The official **Ruby gem** for [BuyProxy](https://www.buyproxy.org): generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and manage **reseller** customers. Zero runtime dependencies; works with **Rails**, **Faraday**, **HTTParty** and `Net::HTTP`.",
    badges=[
        "[![Gem](https://img.shields.io/gem/v/buyproxy?logo=rubygems&logoColor=white)](https://rubygems.org/gems/buyproxy)",
        "[![downloads](https://img.shields.io/gem/dt/buyproxy)](https://rubygems.org/gems/buyproxy)",
        f"[![CI](https://github.com/{GH}/buyproxy-ruby/actions/workflows/ci.yml/badge.svg)](https://github.com/{GH}/buyproxy-ruby/actions/workflows/ci.yml)",
        "[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)",
    ],
    requires="Ruby 3.0+. No runtime dependencies (uses `Net::HTTP`).",
    install="```bash\ngem install buyproxy\n# or in your Gemfile:\nbundle add buyproxy\n```",
    features=["Zero runtime dependencies", "Idiomatic keyword arguments and snake_case models", "Automatic retries with back-off for rate limits and transient errors", "Helpers for **Faraday**, **HTTParty** and `Net::HTTP`"],
    quickstart='''```ruby
require "buyproxy"

bp = BuyProxy::Client.new(api_key: ENV["BUYPROXY_API_KEY"]) # or omit — reads BUYPROXY_API_KEY

plan = bp.plans.list.first
result = bp.plans.generate(plan.id, country: "US", city: "Austin", count: 5)

puts result.first.url # http://user-country-us-city-austin:pass@gw.buyproxy.org:6969
```

Pass `sticky_minutes: 10` to keep the same IP for ten minutes, or `protocol: "socks5"` for SOCKS5.''',
    frameworks=[
        ("Faraday", '''```ruby
conn = Faraday.new(proxy: result.first.to_faraday)
puts conn.get("https://api.ipify.org").body
```'''),
        ("HTTParty", '''```ruby
puts HTTParty.get("https://api.ipify.org", **result.first.to_httparty).body
```'''),
        ("Net::HTTP", '''```ruby
uri = URI("https://api.ipify.org")
http = Net::HTTP.new(uri.host, uri.port, *result.first.to_net_http)
http.use_ssl = true
puts http.get(uri.request_uri).body
```'''),
        ("Rails", '''```ruby
# config/initializers/buyproxy.rb
BUYPROXY = BuyProxy::Client.new(api_key: Rails.application.credentials.dig(:buyproxy, :api_key))
```'''),
    ],
    payments='''```ruby
# Buy 10 GB of Core Residential by card — send the customer to pay_url
checkout = bp.topup.card(product_key: "residential", gb: 10)
puts checkout.pay_url

# Or subscribe to a plan (monthly or yearly)
bp.topup.card(plan: "pro", interval: "year")

# Crypto (pay-as-you-go top-ups only)
bp.topup.crypto(product_key: "residential", gb: 50)

# Wait for the payment to settle — GB appears on bp.balances.list right after
tx = bp.transactions.wait(checkout.transaction_id)
puts tx.status # "succeeded"
```''',
    reseller='''```ruby
reseller = BuyProxy::Client.new(api_key: "bp_live_…")

reseller.reseller.pool.topup_card(product_key: "residential", gb: 500)        # buy into your pool
customer = reseller.reseller.customers.create(label: "Acme Inc")             # isolated sub-account

reseller.reseller.customers.allocate(customer.username, product_key: "residential", gb: 20, idempotency_key: "order-1042")

detail = reseller.reseller.customers.get(customer.username)
result = reseller.reseller.customers.generate(customer.username, plan_id: detail.plans.first.id, country: "DE")

reseller.reseller.customers.update(customer.username, status: "suspended")
```''',
    errors='''```ruby
begin
  bp.plans.generate(plan_id)
rescue BuyProxy::InsufficientBandwidthError
  puts "Out of GB — top up first"
rescue BuyProxy::RateLimitError => e
  puts "Slow down; retry in #{e.retry_after}s"
rescue BuyProxy::AuthenticationError
  puts "Check your API key"
end
```
Every error inherits from `BuyProxy::Error` and exposes `#status` and `#body`.''',
    config='''```ruby
BuyProxy::Client.new(
  api_key: "bp_key_…",                    # default: ENV["BUYPROXY_API_KEY"]
  base_url: "https://www.buyproxy.org",
  timeout: 30,
  max_retries: 2,                          # 429s always; 5xx only for safe requests
  transport: MyTransport.new               # responds to #call(method, uri, headers, body, timeout)
)
```''',
    api=[
        ("Catalog & prices", "`bp.products.list`"), ("Account", "`bp.account.get`"), ("Spendable GB per product", "`bp.balances.list`"),
        ("Plans", "`bp.plans.list`"), ("Generate proxies", "`bp.plans.generate(plan_id, **params)`"),
        ("Card checkout", "`bp.topup.card(...)`"), ("Crypto checkout", "`bp.topup.crypto(...)`"),
        ("Payments", "`bp.transactions.list` · `.get(id)` · `.wait(id)`"), ("Create an account", "`bp.auth.signup` · `.verify_otp` · `.resend_otp`"),
        ("Reseller summary", "`bp.reseller.me`"), ("Customers", "`bp.reseller.customers.list/create/get/update/usage/allocate/generate`"),
        ("Reseller pool", "`bp.reseller.pool.get/topup_card/topup_crypto`"),
    ],
    dev="```bash\nbundle install\nbundle exec rake test\n```",
)

L["java"] = dict(
    repo="buyproxy-java", pkg="org.buyproxy:buyproxy", title="BuyProxy Java SDK",
    h1="BuyProxy Java SDK — Residential Proxy API Client for the JVM",
    pitch="The official **Java SDK** for [BuyProxy](https://www.buyproxy.org): generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and manage **reseller** customers. Java 17+, immutable records, built on the JDK's `HttpClient` — works with **Spring**, **Quarkus**, **Micronaut** and plain Java.",
    badges=[
        "[![Maven Central](https://img.shields.io/maven-central/v/org.buyproxy/buyproxy?logo=apachemaven&logoColor=white)](https://central.sonatype.com/artifact/org.buyproxy/buyproxy)",
        f"[![CI](https://github.com/{GH}/buyproxy-java/actions/workflows/ci.yml/badge.svg)](https://github.com/{GH}/buyproxy-java/actions/workflows/ci.yml)",
        "![Java](https://img.shields.io/badge/Java-17%2B-orange)",
        "[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)",
    ],
    requires="Java 17+. Depends only on Jackson (`jackson-databind`) and `jspecify` annotations.",
    install="**Maven**\n\n```xml\n<dependency>\n  <groupId>org.buyproxy</groupId>\n  <artifactId>buyproxy</artifactId>\n  <version>1.0.0</version>\n</dependency>\n```\n\n**Gradle**\n\n```kotlin\nimplementation(\"org.buyproxy:buyproxy:1.0.0\")\n```",
    features=["Immutable `record` models, `@Nullable`-annotated for NullAway/Kotlin", "Unchecked, typed exceptions — compose cleanly with streams and lambdas", "Automatic retries with back-off for rate limits and transient errors", "`ProxyEndpoint.httpClientBuilder()` returns a `java.net.http.HttpClient` already routed through the proxy"],
    quickstart='''```java
import org.buyproxy.*;

BuyProxy bp = BuyProxy.builder().apiKey(System.getenv("BUYPROXY_API_KEY")).build(); // or omit — reads BUYPROXY_API_KEY

var plan = bp.plans().list().get(0);
GeneratedProxies result = bp.plans().generate(plan.id(),
        GenerateParams.create().country("US").city("Austin").count(5));

System.out.println(result.get(0).url()); // http://user-country-us-city-austin:pass@gw.buyproxy.org:6969
```

Add `.stickyMinutes(10)` to keep the same IP for ten minutes, or `.protocol("socks5")` for SOCKS5.''',
    frameworks=[
        ("java.net.http.HttpClient", '''```java
HttpClient http = result.get(0).httpClientBuilder().build();
String ip = http.send(HttpRequest.newBuilder(URI.create("http://api.ipify.org")).build(), BodyHandlers.ofString()).body();
```

> The JDK disables Basic auth for HTTPS tunnelling by default. To reach `https://` targets through an HTTP proxy, start the JVM with `-Djdk.http.auth.tunneling.disabledSchemes=""`.'''),
        ("HttpURLConnection", '''```java
HttpURLConnection conn = (HttpURLConnection) new URL("http://api.ipify.org").openConnection(result.get(0).toNetProxy());
```'''),
        ("Spring Boot", '''```java
@Configuration
class BuyProxyConfig {
    @Bean
    BuyProxy buyProxy(@Value("${buyproxy.api-key}") String key) {
        return BuyProxy.builder().apiKey(key).build();
    }
}
```'''),
        ("Selenium / Playwright", '''```java
// Selenium: new org.openqa.selenium.Proxy().setHttpProxy(p.host() + ":" + p.port())
// Playwright: new Browser.NewContextOptions().setProxy(new Proxy(p.server()).setUsername(p.username()).setPassword(p.password()))
```'''),
    ],
    payments='''```java
// Buy 10 GB of Core Residential by card — send the customer to payUrl
CardCheckout checkout = bp.topup().card(CardCheckoutParams.topup("residential", 10));
System.out.println(checkout.payUrl());

// Or subscribe to a plan (monthly or yearly)
bp.topup().card(CardCheckoutParams.plan("pro", "year"));

// Crypto (pay-as-you-go top-ups only)
bp.topup().crypto("residential", 50);

// Wait for the payment to settle — GB appears on bp.balances().list() right after
Transaction tx = bp.transactions().await(checkout.transactionId(), Duration.ofSeconds(3), Duration.ofMinutes(10));
```''',
    reseller='''```java
BuyProxy reseller = BuyProxy.builder().apiKey("bp_live_…").build();

reseller.reseller().pool().topupCard("residential", 500);                 // buy into your pool
Customer customer = reseller.reseller().customers().create("Acme Inc");   // isolated sub-account

reseller.reseller().customers().allocate(customer.username(), "residential", 20, "order-1042"); // idempotency key → safe to retry

var detail = reseller.reseller().customers().get(customer.username());
GeneratedProxies result = reseller.reseller().customers()
        .generate(customer.username(), detail.plans().get(0).id(), GenerateParams.create().country("DE"));

reseller.reseller().customers().update(customer.username(), null, "suspended");
```''',
    errors='''```java
try {
    bp.plans().generate(planId);
} catch (BuyProxyException.InsufficientBandwidth e) {
    System.out.println("Out of GB — top up first");
} catch (BuyProxyException.RateLimit e) {
    System.out.println("Slow down; retry in " + e.retryAfterSeconds() + "s");
} catch (BuyProxyException.Authentication e) {
    System.out.println("Check your API key");
}
```
Every exception extends `BuyProxyException` and exposes `status()` and `body()`.''',
    config='''```java
BuyProxy.builder()
    .apiKey("bp_key_…")                        // default: $BUYPROXY_API_KEY
    .baseUrl("https://www.buyproxy.org")
    .timeout(Duration.ofSeconds(30))
    .maxRetries(2)                              // 429s always; 5xx only for safe requests
    .httpClient(myHttpClient)                   // bring your own java.net.http.HttpClient
    .build();
```''',
    api=[
        ("Catalog & prices", "`bp.products().list()`"), ("Account", "`bp.account().get()`"), ("Spendable GB per product", "`bp.balances().list()`"),
        ("Plans", "`bp.plans().list()`"), ("Generate proxies", "`bp.plans().generate(planId, params)`"),
        ("Card checkout", "`bp.topup().card(params)`"), ("Crypto checkout", "`bp.topup().crypto(product, gb)`"),
        ("Payments", "`bp.transactions().list/get/await`"), ("Create an account", "`bp.auth().signup/verifyOtp/resendOtp`"),
        ("Reseller summary", "`bp.reseller().me()`"), ("Customers", "`bp.reseller().customers().list/create/get/update/usage/allocate/generate`"),
        ("Reseller pool", "`bp.reseller().pool().get/topupCard/topupCrypto`"),
    ],
    dev="```bash\nmvn verify\n```",
)

L["dotnet"] = dict(
    repo="buyproxy-dotnet", pkg="BuyProxy", title="BuyProxy .NET SDK",
    h1="BuyProxy .NET SDK — Residential Proxy API Client for C#",
    pitch="The official **.NET / C# SDK** for [BuyProxy](https://www.buyproxy.org): generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and manage **reseller** customers. Async-first, nullable-annotated, no dependencies — works with **ASP.NET Core**, **Playwright for .NET** and plain `HttpClient`.",
    badges=[
        "[![NuGet](https://img.shields.io/nuget/v/BuyProxy?logo=nuget&logoColor=white)](https://www.nuget.org/packages/BuyProxy)",
        "[![downloads](https://img.shields.io/nuget/dt/BuyProxy)](https://www.nuget.org/packages/BuyProxy)",
        f"[![CI](https://github.com/{GH}/buyproxy-dotnet/actions/workflows/ci.yml/badge.svg)](https://github.com/{GH}/buyproxy-dotnet/actions/workflows/ci.yml)",
        "[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)",
    ],
    requires=".NET 6 and later (`net6.0`, `net8.0`). No NuGet dependencies.",
    install="```bash\ndotnet add package BuyProxy\n```",
    features=["Async API with `CancellationToken` on every call", "Immutable `record` models with nullable reference types", "Automatic retries with back-off for rate limits and transient errors", "`ProxyEndpoint.CreateHttpClient()` returns an `HttpClient` already routed through the proxy"],
    quickstart='''```csharp
using BuyProxy;

var bp = new BuyProxyClient(Environment.GetEnvironmentVariable("BUYPROXY_API_KEY")!); // or new BuyProxyClient() — reads BUYPROXY_API_KEY

var plan = (await bp.Plans.ListAsync())[0];
var result = await bp.Plans.GenerateAsync(plan.Id, new GenerateParams { Country = "US", City = "Austin", Count = 5 });

Console.WriteLine(result.Proxies[0].Url); // http://user-country-us-city-austin:pass@gw.buyproxy.org:6969
```

Set `StickyMinutes = 10` to keep the same IP for ten minutes, or `Protocol = "socks5"` for SOCKS5.''',
    frameworks=[
        ("HttpClient", '''```csharp
using var http = result.Proxies[0].CreateHttpClient();
Console.WriteLine(await http.GetStringAsync("https://api.ipify.org"));
```'''),
        ("ASP.NET Core / dependency injection", '''```csharp
builder.Services.AddSingleton(_ => new BuyProxyClient(new BuyProxyOptions
{
    ApiKey = builder.Configuration["BuyProxy:ApiKey"],
}));
```'''),
        ("Playwright for .NET", '''```csharp
var p = result.Proxies[0];
await using var browser = await playwright.Chromium.LaunchAsync(new()
{
    Proxy = new Microsoft.Playwright.Proxy { Server = p.Server, Username = p.Username, Password = p.Password },
});
```'''),
        ("curl & shell", '''```csharp
foreach (var (k, v) in result.Proxies[0].Env()) Console.WriteLine($"export {k}='{v}'");
```'''),
    ],
    payments='''```csharp
// Buy 10 GB of Core Residential by card — send the customer to PayUrl
var checkout = await bp.Topup.CardAsync(CardCheckoutParams.Topup("residential", 10));
Console.WriteLine(checkout.PayUrl);

// Or subscribe to a plan (monthly or yearly)
await bp.Topup.CardAsync(CardCheckoutParams.Plan("pro", "year"));

// Crypto (pay-as-you-go top-ups only)
await bp.Topup.CryptoAsync("residential", 50);

// Wait for the payment to settle — GB appears on bp.Balances.ListAsync() right after
var tx = await bp.Transactions.WaitAsync(checkout.TransactionId!);
Console.WriteLine(tx.Status); // "succeeded"
```''',
    reseller='''```csharp
var reseller = new BuyProxyClient("bp_live_…");

await reseller.Reseller.Pool.TopupCardAsync("residential", 500);                 // buy into your pool
var customer = await reseller.Reseller.Customers.CreateAsync("Acme Inc");        // isolated sub-account

await reseller.Reseller.Customers.AllocateAsync(customer.Username, "residential", 20, idempotencyKey: "order-1042");

var detail = await reseller.Reseller.Customers.GetAsync(customer.Username);
var result = await reseller.Reseller.Customers.GenerateAsync(customer.Username, detail.Plans[0].Id, new GenerateParams { Country = "DE" });

await reseller.Reseller.Customers.UpdateAsync(customer.Username, status: "suspended");
```''',
    errors='''```csharp
try
{
    await bp.Plans.GenerateAsync(planId);
}
catch (InsufficientBandwidthException)
{
    Console.WriteLine("Out of GB — top up first");
}
catch (RateLimitException e)
{
    Console.WriteLine($"Slow down; retry in {e.RetryAfterSeconds}s");
}
catch (AuthenticationException)
{
    Console.WriteLine("Check your API key");
}
```
Every exception derives from `BuyProxyException` and exposes `Status` and `Body`.''',
    config='''```csharp
new BuyProxyClient(new BuyProxyOptions
{
    ApiKey = "bp_key_…",                    // default: BUYPROXY_API_KEY
    BaseUrl = "https://www.buyproxy.org",
    Timeout = TimeSpan.FromSeconds(30),
    MaxRetries = 2,                          // 429s always; 5xx only for safe requests
    HttpClient = httpClientFromFactory,      // bring your own HttpClient
});
```''',
    api=[
        ("Catalog & prices", "`bp.Products.ListAsync()`"), ("Account", "`bp.Account.GetAsync()`"), ("Spendable GB per product", "`bp.Balances.ListAsync()`"),
        ("Plans", "`bp.Plans.ListAsync()`"), ("Generate proxies", "`bp.Plans.GenerateAsync(planId, params)`"),
        ("Card checkout", "`bp.Topup.CardAsync(params)`"), ("Crypto checkout", "`bp.Topup.CryptoAsync(product, gb)`"),
        ("Payments", "`bp.Transactions.ListAsync/GetAsync/WaitAsync`"), ("Create an account", "`bp.Auth.SignupAsync/VerifyOtpAsync/ResendOtpAsync`"),
        ("Reseller summary", "`bp.Reseller.MeAsync()`"), ("Customers", "`bp.Reseller.Customers.ListAsync/CreateAsync/GetAsync/UpdateAsync/UsageAsync/AllocateAsync/GenerateAsync`"),
        ("Reseller pool", "`bp.Reseller.Pool.GetAsync/TopupCardAsync/TopupCryptoAsync`"),
    ],
    dev="```bash\ndotnet build -c Release\ndotnet test\n```",
)

L["rust"] = dict(
    repo="buyproxy-rust", pkg="buyproxy", title="BuyProxy Rust SDK",
    h1="BuyProxy Rust SDK — Residential Proxy API Client Crate",
    pitch="The official **Rust crate** for [BuyProxy](https://www.buyproxy.org): generate **residential, mobile, ISP and datacenter proxies**, check bandwidth, top up by card or crypto, and manage **reseller** customers. Async on `tokio`/`reqwest` with rustls, builder-style params and a typed `Error`.",
    badges=[
        "[![crates.io](https://img.shields.io/crates/v/buyproxy?logo=rust&logoColor=white)](https://crates.io/crates/buyproxy)",
        "[![docs.rs](https://img.shields.io/docsrs/buyproxy)](https://docs.rs/buyproxy)",
        f"[![CI](https://github.com/{GH}/buyproxy-rust/actions/workflows/ci.yml/badge.svg)](https://github.com/{GH}/buyproxy-rust/actions/workflows/ci.yml)",
        "[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)",
    ],
    requires="Rust 1.75+. TLS via rustls — no OpenSSL needed.",
    install="```bash\ncargo add buyproxy tokio --features tokio/full\n```",
    features=["Async, `Clone`-cheap `Client`, safe to share between tasks", "Builder-style `GenerateParams` and a single typed `Error` with `is_*()` helpers", "`Proxy::to_reqwest()` plugs straight into `reqwest`", "Automatic retries with back-off for rate limits and transient errors"],
    quickstart='''```rust
use buyproxy::{Client, GenerateParams};

#[tokio::main]
async fn main() -> buyproxy::Result<()> {
    let client = Client::new(); // reads BUYPROXY_API_KEY — or Client::builder().api_key("bp_key_…").build()

    let plans = client.plans().list().await?;
    let out = client
        .plans()
        .generate(&plans[0].id, &GenerateParams::new().country("US").city("Austin").count(5))
        .await?;

    println!("{}", out.proxies[0].url()); // http://user-country-us-city-austin:pass@gw.buyproxy.org:6969
    Ok(())
}
```

Add `.sticky_minutes(10)` to keep the same IP for ten minutes, or `.protocol(Protocol::Socks5)` for SOCKS5.''',
    frameworks=[
        ("reqwest", '''```rust
let http = reqwest::Client::builder().proxy(out.proxies[0].to_reqwest()?).build()?;
println!("{}", http.get("https://api.ipify.org").send().await?.text().await?);
```'''),
        ("curl & shell", '''```rust
println!("{}", out.proxies[0].curl());   // ready-to-run curl command
println!("{:?}", out.proxies[0].env());  // HTTP_PROXY, HTTPS_PROXY, ALL_PROXY, …
```'''),
    ],
    payments='''```rust
use buyproxy::{BillingInterval, CardCheckoutParams, PaidPlan, ProductKey};

// Buy 10 GB of Core Residential by card — open pay_url in a browser
let checkout = client.topup().card(&CardCheckoutParams::Topup { product_key: ProductKey::Residential, gb: 10 }).await?;
println!("{}", checkout.pay_url);

// Or subscribe to a plan (monthly or yearly)
client.topup().card(&CardCheckoutParams::Plan { plan: PaidPlan::Pro, interval: Some(BillingInterval::Year) }).await?;

// Crypto (pay-as-you-go top-ups only)
client.topup().crypto(ProductKey::Residential, 50).await?;

// Wait for the payment to settle — GB appears on client.balances() right after
let tx = client.transactions().wait(&checkout.transaction_id.unwrap(), Duration::from_secs(3), Duration::from_secs(600)).await?;
```''',
    reseller='''```rust
let reseller = Client::builder().api_key("bp_live_…").build();

reseller.reseller().pool().topup_card(ProductKey::Residential, 500).await?;       // buy into your pool
let customer = reseller.reseller().customers().create("Acme Inc").await?;         // isolated sub-account

reseller.reseller().customers().allocate(&customer.username, &AllocateParams {
    product_key: ProductKey::Residential, gb: 20, idempotency_key: Some("order-1042".into()), // safe to retry
}).await?;

let detail = reseller.reseller().customers().get(&customer.username).await?;
let out = reseller.reseller().customers()
    .generate(&customer.username, &detail.plans[0].plan.id, &GenerateParams::new().country("DE")).await?;

reseller.reseller().customers().update(&customer.username, None, Some(CustomerStatus::Suspended)).await?;
```''',
    errors='''```rust
match client.plans().generate(&plan_id, &GenerateParams::new()).await {
    Ok(out) => println!("{} proxies", out.proxies.len()),
    Err(e) if e.is_insufficient_bandwidth() => println!("Out of GB — top up first"),
    Err(e) if e.is_rate_limited() => println!("Slow down: {e}"),
    Err(e) if e.is_authentication() => println!("Check your API key"),
    Err(e) => return Err(e),
}
```''',
    config='''```rust
let client = Client::builder()
    .api_key("bp_key_…")                         // default: $BUYPROXY_API_KEY
    .base_url("https://www.buyproxy.org")
    .timeout(Duration::from_secs(30))
    .max_retries(2)                               // 429s always; 5xx only for safe requests
    .http_client(my_reqwest_client)               // bring your own reqwest::Client
    .build();
```''',
    api=[
        ("Catalog & prices", "`client.products()`"), ("Account", "`client.account()`"), ("Spendable GB per product", "`client.balances()`"),
        ("Plans", "`client.plans().list()`"), ("Generate proxies", "`client.plans().generate(id, &params)`"),
        ("Card checkout", "`client.topup().card(&params)`"), ("Crypto checkout", "`client.topup().crypto(product, gb)`"),
        ("Payments", "`client.transactions().list/get/wait`"), ("Create an account", "`client.signup()` · `.verify_otp()` · `.resend_otp()`"),
        ("Reseller summary", "`client.reseller().me()`"), ("Customers", "`client.reseller().customers().list/create/get/update/usage/allocate/generate`"),
        ("Reseller pool", "`client.reseller().pool().get/topup_card/topup_crypto`"),
    ],
    dev="```bash\ncargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test\n```",
)

FAQ = """
## FAQ

**How do I get an API key?**
Create a free account at [buyproxy.org](https://www.buyproxy.org/signup), then open **Dashboard → API keys**. Personal keys start with `bp_key_`; reseller keys (Business plan and above) start with `bp_live_`. You can create the *account* from code (`signup` + `verify otp`), but keys are issued from the dashboard.

**What's the difference between a personal and a reseller key?**
A personal key (`bp_key_…`) manages your own bandwidth: balances, plans, generating proxies, top-ups and payments. A reseller key (`bp_live_…`) manages *your customers*: create isolated sub-accounts, buy bandwidth into a pool, allocate it, suspend or reactivate, and generate proxies on their behalf.

**Which proxy types are available?**
Core Residential, Premium Residential, ISP Rotating, Mobile, Datacenter IPv4 and IPv6 — call the catalog endpoint for the live list and per-GB prices (from **$1.99/GB**).

**Do generated proxies expire, and when is bandwidth used?**
Generating a proxy is free and instant; bandwidth is only consumed when traffic flows through it. Lines are on-demand — generate fresh ones rather than storing them.

**What are the rate limits?**
60 requests per minute per API key. The SDK honours `Retry-After` and retries rate-limited requests automatically.

**Is it free to use the SDK?**
Yes — the SDK is MIT-licensed. You pay only for the proxy bandwidth you buy.
"""

def build(key, d):
    rows = "\n".join(f"| {a} | {b} |" for a, b in d["api"])
    fw = "\n\n".join(f"### {t}\n\n{c}" for t, c in d["frameworks"])
    feats = "\n".join(f"- {f}" for f in d["features"])
    badges = "\n".join(d["badges"])
    text = f"""# {d['h1']}

{badges}

{d['pitch']}

**Keywords:** residential proxies · rotating proxies · mobile proxies · ISP proxies · datacenter proxies · SOCKS5 · proxy API · web scraping · proxy reseller

## Features

{feats}

## Installation

{d['install']}

{d['requires']}

## Quick start

{d['quickstart']}

## Using the proxies with your stack

{fw}

## Buy bandwidth (card & crypto)

{d['payments']}

Card payments run through Stripe Checkout; crypto is available for pay-as-you-go top-ups.

## Reseller API

Build a proxy product on top of BuyProxy: buy bandwidth in bulk into a **reseller pool**, create isolated **customers**, and allocate GB to them. Needs a `bp_live_` key on a Business plan or higher.

{d['reseller']}

## Error handling

{d['errors']}

## Configuration

{d['config']}

## API overview

| Capability | Call |
|---|---|
{rows}

Full endpoint reference: <https://www.buyproxy.org/docs/api-reference/introduction> · OpenAPI spec: <https://www.buyproxy.org/openapi.yaml>
{FAQ}
## Other BuyProxy SDKs

[Node.js](https://github.com/{GH}/buyproxy-node) · [Python](https://github.com/{GH}/buyproxy-python) · [Go](https://github.com/{GH}/buyproxy-go) · [PHP](https://github.com/{GH}/buyproxy-php) · [Ruby](https://github.com/{GH}/buyproxy-ruby) · [Java](https://github.com/{GH}/buyproxy-java) · [.NET](https://github.com/{GH}/buyproxy-dotnet) · [Rust](https://github.com/{GH}/buyproxy-rust) · [CLI](https://github.com/{GH}/buyproxy-cli)

All SDKs are checked against the same request log, so behaviour is identical across languages — see [buyproxy-sdks](https://github.com/{GH}/buyproxy-sdks).

## Development

{d['dev']}

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).

## Links

- Website: <https://www.buyproxy.org>
- Documentation: <https://www.buyproxy.org/docs/sdks>
- Pricing: <https://www.buyproxy.org/pricing>
- Support: <support@buyproxy.org>

## License

[MIT](LICENSE) © BuyProxy
"""
    (root / d["repo"] / "README.md").write_text(text)
    print("README", d["repo"], len(text.splitlines()), "lines")

if __name__ == "__main__":
    for k, d in L.items():
        build(k, d)
