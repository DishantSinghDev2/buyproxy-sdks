"""Extra per-language material used only by the website docs (not the READMEs)."""

X = {}

X["node"] = dict(
    slug="nodejs", lang="ts", short="Node.js / TypeScript", mono="JS",
    runtime_note="Works on Node.js 18+, Bun, Deno, Cloudflare Workers and browsers (server-side keys only — never ship an API key to a browser). Ships ESM and CommonJS builds and complete `.d.ts` types.",
    auth='''```ts
// 1. Environment variable (recommended) — nothing to pass
const bp = new BuyProxy();

// 2. Explicit key, e.g. from a secrets manager
const bp2 = new BuyProxy({ apiKey: await getSecret("buyproxy") });

// 3. Find out which kind of key you're holding
console.log(bp.keyKind); // "personal" | "reseller" | undefined
```''',
    targeting='''```ts
// Country, state and city — what a plan supports is in plan.generate.targeting
await bp.plans.generate(plan.id, { country: "US", state: "California", city: "Los Angeles" });

// Sticky session: keep one IP for 30 minutes (max is plan.generate.maxStickyMinutes)
await bp.plans.generate(plan.id, { country: "DE", stickyMinutes: 30 });

// SOCKS5 instead of HTTP
await bp.plans.generate(plan.id, { protocol: "socks5", count: 10 });

// Bulk: up to 1000 lines per call
const { lines } = await bp.plans.generate(plan.id, { count: 1000 });
await fs.writeFile("proxies.txt", lines.join("\\n"));
```''',
    account='''```ts
const catalog = await bp.products.list();          // product keys & live prices — no API key needed
const account = await bp.account.get();             // email, plan, lifetime GB
const balances = await bp.balances.list();          // spendable GB per product (+ GB still arriving)
const plans = await bp.plans.list();                // plan ids and what each can generate
const history = await bp.transactions.list({ limit: 20 });
```''',
    testing='''```ts
import { BuyProxy } from "buyproxy";

// Inject a fake fetch — no network, no mocking library
const bp = new BuyProxy({
  apiKey: "bp_key_test",
  fetch: async () =>
    new Response(JSON.stringify({ lines: ["u:p@gw.buyproxy.org:6969"] }), {
      status: 200,
      headers: { "content-type": "application/json" },
    }),
});

const { proxies } = await bp.plans.generate("plan_1");
expect(proxies[0].host).toBe("gw.buyproxy.org");
```''',
    concurrency='''```ts
// Everything is promise-based and safe to run in parallel (mind the 60 requests/minute limit)
const results = await Promise.all(plans.map((p) => bp.plans.generate(p.id, { count: 10 })));
```''',
    errors_table='''| HTTP | Class | Meaning |
|---|---|---|
| 400 | `ValidationError` | A parameter was missing or invalid |
| 401 | `AuthenticationError` | Missing or invalid API key (also thrown locally when no key is set) |
| 402 | `InsufficientBandwidthError` | Empty reseller pool, or a plan with no GB left |
| 403 | `PermissionError` | Suspended account/customer, or the plan doesn't include this endpoint |
| 404 | `NotFoundError` | Plan, customer or transaction not found on this account |
| 429 | `RateLimitError` | Over 60 requests/minute — has `retryAfterSeconds` |
| 5xx | `ServerError` | BuyProxy or an upstream provider is unavailable |
| — | `ConnectionError`, `TimeoutError` | No response (DNS, reset, offline) / exceeded `timeoutMs` |''',
    notes=["Zero runtime dependencies — it uses the platform's `fetch`.", "`ProxyEndpoint` has helpers for Playwright, Puppeteer, Axios, environment variables and curl.", "Every response and request type is exported, e.g. `import type { Plan, Balance, CustomerDetail } from \"buyproxy\"`."],
)

X["python"] = dict(
    slug="python", lang="python", short="Python", mono="Py",
    runtime_note="Python 3.9+. Fully typed (`py.typed`, `mypy --strict` clean). Built on `httpx`, with identical sync (`BuyProxy`) and async (`AsyncBuyProxy`) clients.",
    auth='''```python
# 1. Environment variable (recommended)
bp = BuyProxy()

# 2. Explicit key, e.g. from a secrets manager
bp = BuyProxy(api_key=get_secret("buyproxy"))

# 3. Which kind of key is it?
print(bp.key_kind)  # "personal" | "reseller" | None
```''',
    targeting='''```python
# Country, state and city — what a plan supports is in plan.generate.targeting
bp.plans.generate(plan.id, country="US", state="California", city="Los Angeles")

# Sticky session: keep one IP for 30 minutes (max is plan.generate.max_sticky_minutes)
bp.plans.generate(plan.id, country="DE", sticky_minutes=30)

# SOCKS5 instead of HTTP
bp.plans.generate(plan.id, protocol="socks5", count=10)

# Bulk: up to 1000 lines per call
result = bp.plans.generate(plan.id, count=1000)
open("proxies.txt", "w").write("\\n".join(result.lines))
```''',
    account='''```python
catalog = bp.products.list()           # product keys & live prices — no API key needed
account = bp.account.get()             # email, plan, lifetime GB
balances = bp.balances.list()          # spendable GB per product (+ GB still arriving)
plans = bp.plans.list()                # plan ids and what each can generate
history = bp.transactions.list(limit=20)
```''',
    testing='''```python
import httpx
from buyproxy import BuyProxy

def handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"lines": ["u:p@gw.buyproxy.org:6969"]})

# httpx.MockTransport — no network, no extra library
bp = BuyProxy("bp_key_test", http_client=httpx.Client(transport=httpx.MockTransport(handler)))
assert bp.plans.generate("plan_1").proxies[0].host == "gw.buyproxy.org"
```''',
    concurrency='''```python
import asyncio
from buyproxy import AsyncBuyProxy

async def main() -> None:
    async with AsyncBuyProxy() as bp:
        plans = await bp.plans.list()
        results = await asyncio.gather(*(bp.plans.generate(p.id, count=10) for p in plans))

asyncio.run(main())
```''',
    errors_table='''| HTTP | Exception | Meaning |
|---|---|---|
| 400 | `ValidationError` | A parameter was missing or invalid |
| 401 | `AuthenticationError` | Missing or invalid API key (also raised locally when no key is set) |
| 402 | `InsufficientBandwidthError` | Empty reseller pool, or a plan with no GB left |
| 403 | `PermissionDeniedError` | Suspended account/customer, or the plan doesn't include this endpoint |
| 404 | `NotFoundError` | Plan, customer or transaction not found on this account |
| 429 | `RateLimitError` | Over 60 requests/minute — has `retry_after_seconds` |
| 5xx | `ServerError` | BuyProxy or an upstream provider is unavailable |
| — | `APIConnectionError`, `APITimeoutError` | No response (DNS, reset, offline) / exceeded `timeout` |''',
    notes=["Responses are frozen dataclasses with snake_case attributes; unknown fields from newer API versions are ignored rather than raising.", "Use it as a context manager (`with BuyProxy() as bp:`) to close the HTTP connection pool.", "`ProxyEndpoint` has helpers for requests, httpx, aiohttp, Playwright, Scrapy and environment variables."],
)

X["go"] = dict(
    slug="go", lang="go", short="Go", mono="Go",
    runtime_note="Go 1.21+, standard library only. Every call takes a `context.Context`; the client is safe for concurrent use.",
    auth='''```go
// 1. Environment variable (recommended)
client := buyproxy.New()

// 2. Explicit key, e.g. from a secrets manager
client = buyproxy.New(buyproxy.WithAPIKey(secret))

// 3. Which kind of key is it?
fmt.Println(client.KeyKind()) // "personal" | "reseller" | ""
```''',
    targeting='''```go
// Country, state and city — what a plan supports is in plan.Generate.Targeting
client.Plans.Generate(ctx, plan.ID, &buyproxy.GenerateParams{Country: "US", State: "California", City: "Los Angeles"})

// Sticky session: keep one IP for 30 minutes (max is plan.Generate.MaxStickyMinutes)
client.Plans.Generate(ctx, plan.ID, &buyproxy.GenerateParams{Country: "DE", StickyMinutes: 30})

// SOCKS5 instead of HTTP
client.Plans.Generate(ctx, plan.ID, &buyproxy.GenerateParams{Protocol: buyproxy.SOCKS5, Count: 10})

// Bulk: up to 1000 lines per call
res, _ := client.Plans.Generate(ctx, plan.ID, &buyproxy.GenerateParams{Count: 1000})
os.WriteFile("proxies.txt", []byte(strings.Join(res.Lines, "\\n")), 0o600)
```''',
    account='''```go
catalog, _ := client.Products.List(ctx)       // product keys & live prices — no API key needed
account, _ := client.Account.Get(ctx)         // email, plan, lifetime GB
balances, _ := client.Balances.List(ctx)      // spendable GB per product (+ GB still arriving)
plans, _ := client.Plans.List(ctx)            // plan ids and what each can generate
history, _ := client.Transactions.List(ctx, 20)
```''',
    testing='''```go
srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprint(w, `{"lines":["u:p@gw.buyproxy.org:6969"]}`)
}))
defer srv.Close()

client := buyproxy.New(buyproxy.WithAPIKey("bp_key_test"), buyproxy.WithBaseURL(srv.URL))
res, _ := client.Plans.Generate(ctx, "plan_1", nil)
// res.Proxies[0].Host == "gw.buyproxy.org"
```''',
    concurrency='''```go
// The client is safe for concurrent use (mind the 60 requests/minute limit)
g, ctx := errgroup.WithContext(ctx)
for _, p := range plans {
	p := p
	g.Go(func() error {
		_, err := client.Plans.Generate(ctx, p.ID, &buyproxy.GenerateParams{Count: 10})
		return err
	})
}
err := g.Wait()
```''',
    errors_table='''| HTTP | Check with | Meaning |
|---|---|---|
| 400 | `errors.Is(err, buyproxy.ErrValidation)` | A parameter was missing or invalid |
| 401 | `errors.Is(err, buyproxy.ErrAuthentication)` | Missing or invalid API key (also returned locally when no key is set) |
| 402 | `errors.Is(err, buyproxy.ErrInsufficientBandwidth)` | Empty reseller pool, or a plan with no GB left |
| 403 | `errors.Is(err, buyproxy.ErrForbidden)` | Suspended account/customer, or the plan doesn't include this endpoint |
| 404 | `errors.Is(err, buyproxy.ErrNotFound)` | Plan, customer or transaction not found on this account |
| 429 | `errors.Is(err, buyproxy.ErrRateLimited)` | Over 60 requests/minute — `APIError.RetryAfter` |
| 5xx | `errors.Is(err, buyproxy.ErrServer)` | BuyProxy or an upstream provider is unavailable |
| — | `*buyproxy.ConnectionError` | No response (DNS, reset, offline); context errors are returned as-is |''',
    notes=["Non-2xx responses are `*buyproxy.APIError` with `Status`, `Message` and `Body`; use `errors.As` to read them.", "`Proxy.HTTPClient()` returns an `*http.Client` already routed through the proxy — HTTP and SOCKS5.", "Zero third-party dependencies, so there is nothing to audit but this module."],
)

X["php"] = dict(
    slug="php", lang="php", short="PHP", mono="PHP",
    runtime_note="PHP 8.1+ with `ext-curl` and `ext-json`. Typed `readonly` models, PHP 8 named arguments, and a pluggable HTTP transport.",
    auth='''```php
// 1. Environment variable (recommended)
$bp = new Client();

// 2. Explicit key, e.g. from Laravel config / a secrets manager
$bp = new Client(apiKey: config('services.buyproxy.key'));

// 3. Which kind of key is it?
echo $bp->keyKind(); // "personal" | "reseller" | null
```''',
    targeting='''```php
// Country, state and city — what a plan supports is in $plan->generate->targeting
$bp->plans->generate($plan->id, country: 'US', state: 'California', city: 'Los Angeles');

// Sticky session: keep one IP for 30 minutes (max is $plan->generate->maxStickyMinutes)
$bp->plans->generate($plan->id, country: 'DE', stickyMinutes: 30);

// SOCKS5 instead of HTTP
$bp->plans->generate($plan->id, protocol: 'socks5', count: 10);

// Bulk: up to 1000 lines per call
$result = $bp->plans->generate($plan->id, count: 1000);
file_put_contents('proxies.txt', implode("\\n", $result->lines));
```''',
    account='''```php
$catalog = $bp->products->list();         // product keys & live prices — no API key needed
$account = $bp->account->get();           // email, plan, lifetime GB
$balances = $bp->balances->list();        // spendable GB per product (+ GB still arriving)
$plans = $bp->plans->list();              // plan ids and what each can generate
$history = $bp->transactions->list(limit: 20);
```''',
    testing='''```php
use BuyProxy\\Client;
use BuyProxy\\Http\\Transport;

final class FakeTransport implements Transport
{
    public function send(string $method, string $url, array $headers, ?string $body, float $timeout): array
    {
        return ['status' => 200, 'headers' => [], 'body' => '{"lines":["u:p@gw.buyproxy.org:6969"]}'];
    }
}

$bp = new Client(apiKey: 'bp_key_test', transport: new FakeTransport());
$this->assertSame('gw.buyproxy.org', $bp->plans->generate('plan_1')->proxies[0]->host);
```''',
    concurrency='''```php
// Calls are synchronous. For parallel work, fan out through your queue
// (e.g. Laravel Horizon / Symfony Messenger) — one job per customer or plan —
// and keep the total under 60 requests/minute per API key.
```''',
    errors_table='''| HTTP | Exception | Meaning |
|---|---|---|
| 400 | `ValidationException` | A parameter was missing or invalid |
| 401 | `AuthenticationException` | Missing or invalid API key (also thrown locally when no key is set) |
| 402 | `InsufficientBandwidthException` | Empty reseller pool, or a plan with no GB left |
| 403 | `PermissionDeniedException` | Suspended account/customer, or the plan doesn't include this endpoint |
| 404 | `NotFoundException` | Plan, customer or transaction not found on this account |
| 429 | `RateLimitException` | Over 60 requests/minute — has `->retryAfterSeconds` |
| 5xx | `ServerException` | BuyProxy or an upstream provider is unavailable |
| — | `ConnectionException` | No response (DNS, reset, timeout, offline) |''',
    notes=["All exceptions live in `BuyProxy\\Exceptions` and extend `BuyProxyException` (with `->status` and `->body`).", "Plug in Guzzle, Symfony HttpClient or a framework client by implementing the one-method `BuyProxy\\Http\\Transport` interface.", "`Proxy` has helpers for Guzzle, Laravel's `Http` facade, Symfony HttpClient, raw cURL and environment variables."],
)

X["ruby"] = dict(
    slug="ruby", lang="ruby", short="Ruby", mono="Rb",
    runtime_note="Ruby 3.0+, zero runtime dependencies (`Net::HTTP`). Keyword arguments and snake_case models throughout.",
    auth='''```ruby
# 1. Environment variable (recommended)
bp = BuyProxy::Client.new

# 2. Explicit key, e.g. from Rails credentials
bp = BuyProxy::Client.new(api_key: Rails.application.credentials.dig(:buyproxy, :api_key))

# 3. Which kind of key is it?
puts bp.key_kind # "personal" | "reseller" | nil
```''',
    targeting='''```ruby
# Country, state and city — what a plan supports is in plan.generate.targeting
bp.plans.generate(plan.id, country: "US", state: "California", city: "Los Angeles")

# Sticky session: keep one IP for 30 minutes (max is plan.generate.max_sticky_minutes)
bp.plans.generate(plan.id, country: "DE", sticky_minutes: 30)

# SOCKS5 instead of HTTP
bp.plans.generate(plan.id, protocol: "socks5", count: 10)

# Bulk: up to 1000 lines per call
result = bp.plans.generate(plan.id, count: 1000)
File.write("proxies.txt", result.lines.join("\\n"))
```''',
    account='''```ruby
catalog = bp.products.list          # product keys & live prices — no API key needed
account = bp.account.get            # email, plan, lifetime GB
balances = bp.balances.list         # spendable GB per product (+ GB still arriving)
plans = bp.plans.list               # plan ids and what each can generate
history = bp.transactions.list(limit: 20)
```''',
    testing='''```ruby
# Any object responding to #call(method, uri, headers, body, timeout) is a transport
transport = lambda do |_method, _uri, _headers, _body, _timeout|
  [200, {}, '{"lines":["u:p@gw.buyproxy.org:6969"]}']
end

bp = BuyProxy::Client.new(api_key: "bp_key_test", transport: transport)
assert_equal "gw.buyproxy.org", bp.plans.generate("plan_1").first.host
```''',
    concurrency='''```ruby
# The client holds no mutable state, so it can be shared between threads
threads = plans.map { |p| Thread.new { bp.plans.generate(p.id, count: 10) } }
results = threads.map(&:value)
```''',
    errors_table='''| HTTP | Error | Meaning |
|---|---|---|
| 400 | `BuyProxy::ValidationError` | A parameter was missing or invalid |
| 401 | `BuyProxy::AuthenticationError` | Missing or invalid API key (also raised locally when no key is set) |
| 402 | `BuyProxy::InsufficientBandwidthError` | Empty reseller pool, or a plan with no GB left |
| 403 | `BuyProxy::PermissionDeniedError` | Suspended account/customer, or the plan doesn't include this endpoint |
| 404 | `BuyProxy::NotFoundError` | Plan, customer or transaction not found on this account |
| 429 | `BuyProxy::RateLimitError` | Over 60 requests/minute — has `#retry_after` |
| 5xx | `BuyProxy::ServerError` | BuyProxy or an upstream provider is unavailable |
| — | `BuyProxy::ConnectionError`, `BuyProxy::TimeoutError` | No response (DNS, reset, offline) / timed out |''',
    notes=["Every error inherits from `BuyProxy::Error` and exposes `#status` and `#body`.", "`Proxy` has helpers for Faraday, HTTParty, `Net::HTTP` and environment variables.", "In a Rails app, create one client in an initializer and reuse it."],
)

X["java"] = dict(
    slug="java", lang="java", short="Java", mono="Jv",
    runtime_note="Java 17+. Immutable `record` models with `@Nullable` annotations; built on the JDK's `java.net.http.HttpClient` and Jackson.",
    auth='''```java
// 1. Environment variable (recommended)
BuyProxy bp = BuyProxy.builder().build();

// 2. Explicit key, e.g. from Spring config / a secrets manager
BuyProxy bp = BuyProxy.builder().apiKey(secret).build();

// 3. Which kind of key is it?
System.out.println(bp.keyKind()); // "personal" | "reseller" | null
```''',
    targeting='''```java
// Country, state and city — what a plan supports is in plan.generate().targeting()
bp.plans().generate(plan.id(), GenerateParams.create().country("US").state("California").city("Los Angeles"));

// Sticky session: keep one IP for 30 minutes (max is plan.generate().maxStickyMinutes())
bp.plans().generate(plan.id(), GenerateParams.create().country("DE").stickyMinutes(30));

// SOCKS5 instead of HTTP
bp.plans().generate(plan.id(), GenerateParams.create().protocol("socks5").count(10));

// Bulk: up to 1000 lines per call
GeneratedProxies result = bp.plans().generate(plan.id(), GenerateParams.create().count(1000));
Files.write(Path.of("proxies.txt"), result.lines());
```''',
    account='''```java
Catalog catalog = bp.products().list();            // product keys & live prices — no API key needed
var account = bp.account().get();                   // email, plan, lifetime GB
List<Balance> balances = bp.balances().list();      // spendable GB per product (+ GB still arriving)
List<Plan> plans = bp.plans().list();               // plan ids and what each can generate
List<Transaction> history = bp.transactions().list(20);
```''',
    testing='''```java
HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
server.createContext("/", ex -> {
    byte[] body = "{\\"lines\\":[\\"u:p@gw.buyproxy.org:6969\\"]}".getBytes(StandardCharsets.UTF_8);
    ex.getResponseHeaders().add("Content-Type", "application/json");
    ex.sendResponseHeaders(200, body.length);
    ex.getResponseBody().write(body);
    ex.close();
});
server.start();

BuyProxy bp = BuyProxy.builder().apiKey("bp_key_test")
        .baseUrl("http://127.0.0.1:" + server.getAddress().getPort()).build();
assertEquals("gw.buyproxy.org", bp.plans().generate("plan_1").get(0).host());
```''',
    concurrency='''```java
// The client is thread-safe. On Java 21, virtual threads make fan-out trivial
try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
    var futures = plans.stream()
            .map(p -> pool.submit(() -> bp.plans().generate(p.id(), GenerateParams.create().count(10))))
            .toList();
    for (var f : futures) f.get();
}
```''',
    errors_table='''| HTTP | Exception | Meaning |
|---|---|---|
| 400 | `BuyProxyException.Validation` | A parameter was missing or invalid |
| 401 | `BuyProxyException.Authentication` | Missing or invalid API key (also thrown locally when no key is set) |
| 402 | `BuyProxyException.InsufficientBandwidth` | Empty reseller pool, or a plan with no GB left |
| 403 | `BuyProxyException.PermissionDenied` | Suspended account/customer, or the plan doesn't include this endpoint |
| 404 | `BuyProxyException.NotFound` | Plan, customer or transaction not found on this account |
| 429 | `BuyProxyException.RateLimit` | Over 60 requests/minute — `retryAfterSeconds()` |
| 5xx | `BuyProxyException.Server` | BuyProxy or an upstream provider is unavailable |
| — | `BuyProxyException.Connection` | No response (DNS, reset, timeout, offline) |''',
    notes=["All exceptions are unchecked and extend `BuyProxyException` (with `status()` and `body()`).", "`ProxyEndpoint.httpClientBuilder()` returns a `java.net.http.HttpClient.Builder` already routed through the proxy.", "Models are records, so they work with pattern matching and serialise cleanly with Jackson."],
)

X["dotnet"] = dict(
    slug="dotnet", lang="csharp", short="C# / .NET", mono="C#",
    runtime_note=".NET 6 and later (`net6.0`, `net8.0`). Async-first, nullable reference types enabled, no NuGet dependencies.",
    auth='''```csharp
// 1. Environment variable (recommended)
var bp = new BuyProxyClient();

// 2. Explicit key, e.g. from IConfiguration / Key Vault
var bp2 = new BuyProxyClient(new BuyProxyOptions { ApiKey = config["BuyProxy:ApiKey"] });

// 3. Which kind of key is it?
Console.WriteLine(bp.KeyKind); // "personal" | "reseller" | null
```''',
    targeting='''```csharp
// Country, state and city — what a plan supports is in plan.Generate.Targeting
await bp.Plans.GenerateAsync(plan.Id, new GenerateParams { Country = "US", State = "California", City = "Los Angeles" });

// Sticky session: keep one IP for 30 minutes (max is plan.Generate.MaxStickyMinutes)
await bp.Plans.GenerateAsync(plan.Id, new GenerateParams { Country = "DE", StickyMinutes = 30 });

// SOCKS5 instead of HTTP
await bp.Plans.GenerateAsync(plan.Id, new GenerateParams { Protocol = "socks5", Count = 10 });

// Bulk: up to 1000 lines per call
var result = await bp.Plans.GenerateAsync(plan.Id, new GenerateParams { Count = 1000 });
await File.WriteAllLinesAsync("proxies.txt", result.Lines);
```''',
    account='''```csharp
var catalog = await bp.Products.ListAsync();         // product keys & live prices — no API key needed
var account = await bp.Account.GetAsync();            // email, plan, lifetime GB
var balances = await bp.Balances.ListAsync();         // spendable GB per product (+ GB still arriving)
var plans = await bp.Plans.ListAsync();               // plan ids and what each can generate
var history = await bp.Transactions.ListAsync(limit: 20);
```''',
    testing='''```csharp
sealed class StubHandler : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct) =>
        Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
        {
            Content = new StringContent("""{"lines":["u:p@gw.buyproxy.org:6969"]}""", Encoding.UTF8, "application/json"),
        });
}

var bp = new BuyProxyClient(new BuyProxyOptions { ApiKey = "bp_key_test", HttpClient = new HttpClient(new StubHandler()) });
Assert.Equal("gw.buyproxy.org", (await bp.Plans.GenerateAsync("plan_1")).Proxies[0].Host);
```''',
    concurrency='''```csharp
// Thread-safe — register one instance and share it (mind the 60 requests/minute limit)
var results = await Task.WhenAll(plans.Select(p => bp.Plans.GenerateAsync(p.Id, new GenerateParams { Count = 10 })));
```''',
    errors_table='''| HTTP | Exception | Meaning |
|---|---|---|
| 400 | `ValidationException` | A parameter was missing or invalid |
| 401 | `AuthenticationException` | Missing or invalid API key (also thrown locally when no key is set) |
| 402 | `InsufficientBandwidthException` | Empty reseller pool, or a plan with no GB left |
| 403 | `PermissionDeniedException` | Suspended account/customer, or the plan doesn't include this endpoint |
| 404 | `NotFoundException` | Plan, customer or transaction not found on this account |
| 429 | `RateLimitException` | Over 60 requests/minute — has `RetryAfterSeconds` |
| 5xx | `ServerException` | BuyProxy or an upstream provider is unavailable |
| — | `ConnectionException` | No response (DNS, reset, timeout, offline) |''',
    notes=["Every exception derives from `BuyProxyException` (with `Status` and `Body`). Cancel any call with a `CancellationToken`.", "Pass an `HttpClient` from `IHttpClientFactory` via `BuyProxyOptions.HttpClient` to get pooling, Polly policies and logging.", "`ProxyEndpoint.CreateHttpClient()` returns an `HttpClient` already routed through the proxy."],
)

X["rust"] = dict(
    slug="rust", lang="rust", short="Rust", mono="Rs",
    runtime_note="Rust 1.75+, async on `tokio` and `reqwest` with rustls (no OpenSSL). `Client` is cheap to clone and safe to share between tasks.",
    auth='''```rust
// 1. Environment variable (recommended)
let client = Client::new();

// 2. Explicit key, e.g. from a secrets manager
let client = Client::builder().api_key(secret).build();

// 3. Which kind of key is it?
println!("{:?}", client.key_kind()); // Some("personal") | Some("reseller") | None
```''',
    targeting='''```rust
// Country, state and city — what a plan supports is in plan.generate.targeting
client.plans().generate(&plan.id, &GenerateParams::new().country("US").state("California").city("Los Angeles")).await?;

// Sticky session: keep one IP for 30 minutes (max is plan.generate.max_sticky_minutes)
client.plans().generate(&plan.id, &GenerateParams::new().country("DE").sticky_minutes(30)).await?;

// SOCKS5 instead of HTTP
client.plans().generate(&plan.id, &GenerateParams::new().protocol(Protocol::Socks5).count(10)).await?;

// Bulk: up to 1000 lines per call
let out = client.plans().generate(&plan.id, &GenerateParams::new().count(1000)).await?;
std::fs::write("proxies.txt", out.lines.join("\\n"))?;
```''',
    account='''```rust
let catalog = client.products().await?;            // product keys & live prices — no API key needed
let account = client.account().await?;              // email, plan, lifetime GB
let balances = client.balances().await?;            // spendable GB per product (+ GB still arriving)
let plans = client.plans().list().await?;           // plan ids and what each can generate
let history = client.transactions().list(Some(20)).await?;
```''',
    testing='''```rust
use wiremock::{matchers::path, Mock, MockServer, ResponseTemplate};

let server = MockServer::start().await;
Mock::given(path("/v1/plans/plan_1/generate"))
    .respond_with(ResponseTemplate::new(200).set_body_json(serde_json::json!({ "lines": ["u:p@gw.buyproxy.org:6969"] })))
    .mount(&server)
    .await;

let client = Client::builder().api_key("bp_key_test").base_url(server.uri()).build();
let out = client.plans().generate("plan_1", &GenerateParams::new()).await?;
assert_eq!(out.proxies[0].host, "gw.buyproxy.org");
```''',
    concurrency='''```rust
// Client is Clone + Send + Sync — run calls concurrently (mind the 60 requests/minute limit)
let (a, b) = tokio::try_join!(
    client.plans().generate(&plan_a.id, &GenerateParams::new().count(10)),
    client.plans().generate(&plan_b.id, &GenerateParams::new().count(10)),
)?;
```''',
    errors_table='''| HTTP | Check with | Meaning |
|---|---|---|
| 400 | `err.is_validation()` | A parameter was missing or invalid |
| 401 | `err.is_authentication()` | Missing or invalid API key (`Error::MissingApiKey` is returned locally when none is set) |
| 402 | `err.is_insufficient_bandwidth()` | Empty reseller pool, or a plan with no GB left |
| 403 | `err.is_forbidden()` | Suspended account/customer, or the plan doesn't include this endpoint |
| 404 | `err.is_not_found()` | Plan, customer or transaction not found on this account |
| 429 | `err.is_rate_limited()` | Over 60 requests/minute — `Error::Api { retry_after, .. }` |
| 5xx | `err.is_server_error()` | BuyProxy or an upstream provider is unavailable |
| — | `Error::Connection` | No response (DNS, reset, timeout, offline) |''',
    notes=["A single `Error` enum covers everything: `Api { status, message, body, retry_after }`, `MissingApiKey`, `Connection`, `Decode` and `InvalidProxyLine`.", "`ProductKey` has an `Other` variant so a product added after your SDK version still deserialises.", "`Proxy::to_reqwest()` plugs straight into `reqwest::Client::builder().proxy(…)`."],
)
