#!/usr/bin/env python3
"""cli_docs.py <out.ts> — the website's CLI documentation data. Sample output is drawn with the same box/table rules as the CLI."""
import sys, json, pathlib

def box(title, lines):
    inner = max([len(title) + 4] + [len(l) for l in lines])
    top = "╭─ " + title + " " + "─" * (inner - len(title) - 1) + "╮"
    rows = ["│ " + l.ljust(inner) + " │" for l in lines]
    return "\n".join([top] + rows + ["╰" + "─" * (inner + 2) + "╯"])

def table(head, rows, align=None):
    align = align or ["l"] * len(head)
    w = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(head)]
    cell = lambda s, i: s.rjust(w[i]) if align[i] == "r" else s.ljust(w[i])
    out = ["  " + "   ".join(cell(h, i) for i, h in enumerate(head)), "  " + "───".join("─" * x for x in w)]
    out += ["  " + "   ".join(cell(c, i) for i, c in enumerate(r)) for r in rows]
    return "\n".join(out)

def bar(f, n=24):
    k = round(max(0, min(1, f)) * n)
    return "█" * k + "░" * (n - k)

GEN_BOX = box("3 proxies · Austin, US · rotating", [
    "http://user-country-us-city-austin:s3cr3tA@gw.buyproxy.org:6969",
    "http://user2-country-us-city-austin:s3cr3tB@gw.buyproxy.org:6969",
    "http://user3-country-us-city-austin:s3cr3tC@gw.buyproxy.org:6969",
])

def opt(flag, desc, arg=None, default=None):
    return {"flag": flag, "arg": arg, "default": default, "desc": desc}

def ex(title, cmd, output=None, note=None):
    return {"title": title, "cmd": cmd, "output": output, "note": note}

GENERATE_OPTS = [
    opt("[product]", "Which plan to use, by product key (`residential`, `premium`, `isp`, `mobile`, `ipv4`, `ipv6`) or a unique part of its name. Optional when you only hold one plan.", None),
    opt("--plan", "Use a specific plan id (from `buyproxy plans`) instead of a product.", "<id>"),
    opt("-c, --country", "Two-letter ISO country code, e.g. `US`, `DE`, `JP`. Omit for a worldwide IP.", "<XX>"),
    opt("--state", "State or region, where the product supports it.", "<name>"),
    opt("--city", "City, where the product supports it.", "<name>"),
    opt("--isp", "Network or carrier, where the product supports it.", "<name>"),
    opt("-n, --count", "How many proxies to return (1–1000).", "<n>", "1"),
    opt("-s, --sticky", "Keep the same IP for this many minutes. Leave it out for a fresh IP on every request.", "<minutes>"),
    opt("--socks5", "Generate SOCKS5 proxies instead of HTTP.", None),
    opt("-f, --format", "How to print the result: `url`, `plain`, `json`, `env`, `curl`, `playwright` or `requests`.", "<format>", "url in a terminal, plain when piped"),
    opt("--copy", "Also copy the printed output to your clipboard.", None),
]

C = []

# ------------------------------------------------------------------ generate
C.append(dict(
    slug="generate", name="generate", aliases=["gen", "g"], group="Proxies",
    summary="Generate proxies — rotating or sticky, geo-targeted, in the format you need.",
    synopsis="buyproxy generate [product] [-c US] [--state S] [--city C] [-n 5] [-s 10] [--socks5] [-f url|plain|json|env|curl|playwright|requests] [--copy]",
    intro="""`generate` is the command you'll use most. It asks BuyProxy for fresh proxy lines against one of your plans and prints them ready to paste: as URLs, as `host:port:user:pass` style lines, as shell exports, as a Playwright config, and more.

Generation costs nothing — bandwidth is only used when traffic flows through a proxy — so it's fine to generate again whenever you need a new IP. Lines are not saved anywhere; generate fresh ones rather than storing them.""",
    options=GENERATE_OPTS,
    howItWorks="""1. The CLI loads your plans and picks one: the `--plan` id if you gave one, otherwise the plan matching `[product]`, otherwise your only plan. With several plans and no hint it shows a menu in a terminal, or exits with a clear error when piped.
2. **Run with no arguments in a terminal and it walks you through it** — country, state and city (only the fields that plan supports), how many, a sticky window (only if the product has sticky sessions), and HTTP or SOCKS5.
3. It asks the API to generate and prints the proxies in the chosen format. In a terminal you get a boxed, colour-coded result (long lists show the first 12 and tell you how many more); when piped you get only the data.
4. If the plan has no bandwidth left it warns you, because new connections will fail until you top up.

Targeting is baked into each line's username, so the same line always means "a US/Austin exit" — you can hand it to any HTTP client.""",
    examples=[
        ex("Guided mode", "buyproxy generate", f"""? Country code (blank = anywhere) US
? State / region (blank = any)
? City (blank = any) Austin
? How many proxies? 3
? Sticky session in minutes (blank = rotate every request, max 60)
? Protocol HTTP / HTTPS
{GEN_BOX}""", "Only the questions your plan supports are asked."),
        ex("Ten US proxies, no questions", "buyproxy generate residential -c US -n 10", None, "Passing any argument skips the guided prompts."),
        ex("Sticky German session for 30 minutes, copied to the clipboard", "buyproxy generate premium -c DE --city Berlin -s 30 --copy", None, "A sticky window keeps the same IP for that long, up to the plan's maximum."),
        ex("SOCKS5", "buyproxy generate isp --socks5 -n 5", None),
        ex("Export into your shell", 'eval "$(buyproxy generate residential -c US -f env)"\ncurl https://api.ipify.org', None, "`env` prints `export HTTP_PROXY=…` / `HTTPS_PROXY` / `ALL_PROXY` for the first proxy, so every tool that honours them uses it."),
        ex("A list for another program", "buyproxy generate -n 100 -f plain > proxies.txt", None, "`plain` prints one `username:password@host:port` per line."),
        ex("Paste straight into code", "buyproxy generate -c US -f playwright --copy\nbuyproxy generate -f requests\nbuyproxy generate -f curl", None, "`playwright` and `requests` print a ready snippet using the first proxy; `curl` prints a command that fetches your exit IP."),
    ],
    json="""With `--json` (or `-f json`) you get an array, one object per proxy:

```json
[
  {
    "host": "gw.buyproxy.org",
    "port": 6969,
    "username": "user-country-us-city-austin",
    "password": "s3cr3tA",
    "protocol": "http",
    "url": "http://user-country-us-city-austin:s3cr3tA@gw.buyproxy.org:6969"
  }
]
```""",
    errors=[
        {"message": "You don't have any bandwidth yet.", "fix": "Buy some with `buyproxy topup`."},
        {"message": "You don't have a plan for \"mobile\".", "fix": "The error lists the products you do have; top up the one you want, or pass `--plan <id>`."},
        {"message": "You have several plans — say which one.", "fix": "Piped output can't show a menu. Pass a product (`buyproxy generate residential`) or `--plan <id>`."},
        {"message": "--country takes a 2-letter ISO code like US or DE.", "fix": "Use the two-letter code, not the country name."},
        {"message": "This plan doesn't support that combination of options.", "fix": "Not every product supports every option. Run `buyproxy plans` to see each plan's protocols, targeting fields and sticky limit."},
    ],
    tips=["Use `-f plain` for files and `-f url` for code — URLs have special characters in the password percent-encoded for you.", "Hitting the 60 requests/minute limit? Ask for more per call: `-n 1000` is one request.", "`buyproxy test` proves a generated proxy actually works end to end."],
    related=["plans", "test", "balance", "topup"],
))

# ------------------------------------------------------------------ test
C.append(dict(
    slug="test", name="test", aliases=[], group="Tools",
    summary="Generate a proxy and prove it works — shows the exit IP, location, network and latency.",
    synopsis="buyproxy test [product] [-c US] [--plan <id>]",
    intro="`test` is the quickest way to check your bandwidth, your plan and a target country are all working. It generates one HTTP proxy, opens a tunnel through it and asks a public IP-information service who it sees — so you find out about a problem before a long job does.",
    options=[
        opt("[product]", "Which plan to test, by product key or part of its name."),
        opt("--plan", "A specific plan id.", "<id>"),
        opt("-c, --country", "Test an exit in this country (two-letter code).", "<XX>"),
    ],
    howItWorks="""1. Picks a plan the same way `generate` does and generates **one HTTP proxy** (SOCKS5 isn't tested).
2. Connects to the proxy, authenticates with its credentials, and tunnels to `ipinfo.io`.
3. Requests `https://ipinfo.io/json` *through the proxy* and times the whole round trip.
4. Prints what the outside world saw.

That request is a few kilobytes of your bandwidth, and it's the only thing sent to a third party — to the IP-information service, from the proxy's address.""",
    examples=[
        ex("Test the default plan", "buyproxy test", box("Proxy check", [
            "Exit IP    203.0.113.42",
            "Location   Austin, Texas, US",
            "Network    AS7922 Comcast Cable Communications, LLC",
            "Latency    842 ms",
            "Product    Core Residential",
        ])),
        ex("Test Japan on Premium", "buyproxy test premium -c JP"),
        ex("Health check in a script", "buyproxy test --json | jq -e '.ok'", None, "Exits non-zero if the proxy fails, so it works in cron jobs and CI."),
    ],
    json="""```json
{
  "ok": true,
  "latencyMs": 842,
  "body": { "ip": "203.0.113.42", "city": "Austin", "region": "Texas", "country": "US", "org": "AS7922 Comcast Cable Communications, LLC" }
}
```
On failure `ok` is `false` and `error` explains why.""",
    errors=[
        {"message": "The proxy didn't answer: proxy rejected the credentials (407)", "fix": "Generate again; if it persists, check `buyproxy whoami` that you're using the right account."},
        {"message": "The proxy didn't answer: timed out", "fix": "Check you have bandwidth left (`buyproxy balance`) and that the product supports the country you asked for."},
        {"message": "You don't have any bandwidth yet.", "fix": "Top up with `buyproxy topup` first."},
    ],
    tips=["A latency over ~1.5 s is shown in amber — normal for some residential routes, worth knowing before a latency-sensitive job.", "Run it right after a top-up to confirm the new bandwidth is live."],
    related=["generate", "balance"],
))

# ------------------------------------------------------------------ balance
bal_rows = [
    f"  Core Residential     {bar(0.85)}  8.50 GB / 10.0 GB",
    f"  Premium Residential  {bar(0.12)}  1.20 GB / 10.0 GB  +5.00 GB arriving",
    f"  ISP Rotating         {bar(0)}  not funded".replace(bar(0), "░" * 24),
]
C.append(dict(
    slug="balance", name="balance", aliases=["bal", "usage"], group="Account",
    summary="Bandwidth left on every product, with usage bars.",
    synopsis="buyproxy balance",
    intro="`balance` shows how much bandwidth you have on each product at a glance — the quickest answer to \"can I run this job?\".",
    options=[],
    howItWorks="""For each product you hold, the bar shows remaining GB against what the plan started with:

- **Green** — more than 40% left.
- **Amber** — 40% to 15%.
- **Red** — under 15%: time to top up.
- `+X GB arriving` — a payment has gone through and the GB is being added; it becomes live within seconds.
- `not funded` — you've never bought that product.

If any plan expires, the soonest expiry is shown underneath.""",
    examples=[
        ex("Check balances", "buyproxy balance", "Bandwidth\n" + "\n".join(bal_rows) + "\n\n  Next expiry: Premium Residential on 11/12/2026\n\n  Need more? buyproxy topup"),
        ex("Find products running low, in a script", "buyproxy balance --json | jq '.balances[] | select(.activeGb < 1) | .productKey'"),
    ],
    json="""```json
{
  "balances": [
    { "productKey": "residential", "productId": "residential-lite", "planId": "plan_9f2a", "activeGb": 8.5, "pendingGb": 0, "totalGb": 8.5, "expiresAt": null }
  ],
  "plans": [ { "id": "plan_9f2a", "productKey": "residential", "dataGbRemaining": 8.5, "dataGbTotal": 10, "...": "..." } ]
}
```""",
    errors=[{"message": "You're not logged in.", "fix": "Run `buyproxy login`, or set `BUYPROXY_API_KEY`."}],
    tips=["Reseller keys see their pool with `buyproxy pool` instead — customer balances are under `buyproxy customers show`."],
    related=["plans", "topup", "pool"],
))

# ------------------------------------------------------------------ plans
C.append(dict(
    slug="plans", name="plans", aliases=[], group="Proxies",
    summary="Your plans and exactly what each one can generate.",
    synopsis="buyproxy plans",
    intro="A *plan* is the bandwidth you hold on one product. `plans` lists them along with the capabilities that decide which options `generate` accepts — useful when a command says an option isn't supported.",
    options=[],
    howItWorks="""Columns:

| Column | Meaning |
|---|---|
| **Plan** | The product name |
| **ID** | What you pass to `--plan` |
| **Left** | GB remaining |
| **Protocols** | `http`, `socks5` or both |
| **Targeting** | Which of `country`, `state`, `city`, `isp` this plan accepts |
| **Sticky** | The longest sticky session in minutes, or `—` if the product has none |""",
    examples=[ex("List plans", "buyproxy plans", "Your plans\n" + table(
        ["Plan", "ID", "Left", "Protocols", "Targeting", "Sticky"],
        [["Core Residential", "plan_9f2a", "8.50 GB", "http/socks5", "country/state/city", "60 min"],
         ["Mobile Proxies", "plan_41c7", "20.0 GB", "http", "country/isp", "—"]]))],
    json="Returns the raw plan list, each with `generate.maxCount`, `generate.maxStickyMinutes`, `generate.protocols` and `generate.targeting`.",
    errors=[{"message": "No plans yet — run buyproxy topup to buy your first GB.", "fix": "You haven't bought bandwidth on any product yet."}],
    tips=[], related=["generate", "balance"],
))

# ------------------------------------------------------------------ topup
ORDER = box("Order", ["Product   Core Residential", "Bandwidth 100 GB  + 10 GB bonus", "Total     $199.00  via card"])
C.append(dict(
    slug="topup", name="topup", aliases=["buy"], group="Billing",
    summary="Buy bandwidth by card or crypto — the CLI opens checkout and waits for your payment.",
    synopsis="buyproxy topup [product] [--gb 25] [--card|--crypto] [--pool] [-y] [--no-open] [--no-wait]",
    intro="`topup` buys pay-as-you-go bandwidth for one product. You see the live price and any volume bonus before anything is charged, pay on a secure hosted page, and the CLI waits for the payment to settle so you know the moment your GB is live.",
    options=[
        opt("[product]", "Product key: `residential`, `premium`, `isp`, `mobile`, `ipv4` or `ipv6`."),
        opt("-g, --gb", "How many GB (a whole number from the product's minimum to 10,000).", "<n>"),
        opt("--card", "Pay by card (Stripe Checkout)."),
        opt("--crypto", "Pay with cryptocurrency (BTC, ETH, USDT and more)."),
        opt("--pool", "**Reseller keys:** buy into your reseller pool instead of your own plan."),
        opt("-y, --yes", "Skip the \"Continue to payment?\" confirmation."),
        opt("--no-open", "Don't open the browser — just print the payment link."),
        opt("--no-wait", "Print the link and return immediately instead of waiting for payment."),
    ],
    howItWorks="""1. **Prices load live** from BuyProxy, so what you see is what you're charged.
2. **Pick a product** and **an amount** (guided prompts, or `[product]` and `--gb`). Each product has a minimum — 1 GB for most, 2 GB for Premium.
3. **Choose card or crypto.** Card payments go through Stripe Checkout; crypto uses an invoice page.
4. **Review the order.** Orders of **100 GB or more get a 10% bonus**, shown before you confirm.
5. **Pay.** The CLI creates the checkout, prints the link and opens your browser.
6. **Wait.** In a terminal the CLI polls every few seconds (up to 15 minutes) and shows a receipt when the payment succeeds. Card payments settle in seconds; crypto waits for network confirmations.

If you press Ctrl-C while waiting nothing is lost — pick it up later with `buyproxy tx <id> --wait`.""",
    examples=[
        ex("Guided", "buyproxy topup", f"""? Which product? Core Residential
? How many GB? (min 1) 100
? Pay with Card
{ORDER}
? Continue to payment? Yes
✔ Checkout ready

  Pay here: https://checkout.stripe.com/c/pay/cs_live_…
⠋ Waiting for your payment — finish checkout in the browser (Ctrl-C to stop waiting)"""),
        ex("One line", "buyproxy topup residential --gb 100 --card -y"),
        ex("Crypto, just give me the link", "buyproxy topup premium -g 20 --crypto --no-open --no-wait"),
        ex("Reseller pool", "buyproxy topup residential -g 500 --card --pool", None, "Needs a `bp_live_…` key. The GB lands in your pool, ready to allocate to customers."),
        ex("Machine-readable", "buyproxy topup residential -g 10 --card -y --json", '{"url":"https://checkout.stripe.com/c/pay/…","transactionId":"st_5b1c…"}'),
    ],
    json="With `--json` the command prints `{ \"url\": …, \"transactionId\": … }` and returns without waiting — poll with `buyproxy tx <transactionId> --json`.",
    errors=[
        {"message": "Say which product to top up. / Say how many GB with --gb. / Choose a payment method: --card or --crypto.", "fix": "Without a terminal there are no prompts, so pass all three."},
        {"message": "Card payment isn't available right now — please use crypto.", "fix": "Card checkout is temporarily unavailable; retry with `--crypto`."},
        {"message": "--gb must be a whole number from 1 to 10 000 for Core Residential.", "fix": "Each product has its own minimum; the maximum per order is 10,000 GB."},
        {"message": "Still pending. Check later with: buyproxy tx <id> --wait", "fix": "The payment hadn't settled in 15 minutes — usually crypto waiting on confirmations."},
    ],
    tips=["Prefer a subscription? See `buyproxy subscribe` — plans include GB every month at a lower per-GB rate.", "Crypto payments are final; card payments follow the refund policy at buyproxy.org/legal/refunds."],
    related=["balance", "transactions", "subscribe", "pool"],
))

# ------------------------------------------------------------------ subscribe
C.append(dict(
    slug="subscribe", name="subscribe", aliases=["upgrade"], group="Billing",
    summary="Subscribe to Pro, Business or Advanced — monthly or yearly.",
    synopsis="buyproxy subscribe [pro|business|advanced] [--yearly] [-y] [--no-open] [--no-wait]",
    intro="Plans are recurring subscriptions billed by card: a monthly bandwidth allowance at a lower per-GB rate than pay-as-you-go, plus features like the Reseller program on Business and above. `subscribe` creates the checkout and waits for it to complete.",
    options=[
        opt("[plan]", "`pro`, `business` or `advanced`."),
        opt("--yearly", "Bill yearly (about 10% cheaper) instead of monthly."),
        opt("-y, --yes", "Skip the confirmation."),
        opt("--no-open", "Print the link without opening a browser."),
        opt("--no-wait", "Return as soon as the link is created."),
    ],
    howItWorks="""1. Loads plan prices and the GB each plan includes.
2. Choose the plan and the billing interval (the menu shows the yearly price).
3. Confirm, then pay on the Stripe Checkout page the CLI opens.
4. The CLI waits for the first payment to settle. Your plan and monthly GB allowance activate immediately; a yearly plan credits twelve months of GB at once.

**Already subscribed?** You can't subscribe twice — the CLI opens your subscription settings instead, where switching plans is prorated and you can cancel or update your card.""",
    examples=[
        ex("Guided", "buyproxy subscribe", """? Which plan? Business  $90.00/mo · 75 GB included
? Billing Yearly   $972.00/yr  (~10% off)
? Subscribe to business (yearly)? Yes
✔ Checkout ready"""),
        ex("One line", "buyproxy subscribe pro --yearly -y"),
    ],
    json="`--json` prints `{ \"payUrl\": …, \"transactionId\": … }`. `transactionId` is `null` when the URL is the subscription settings page.",
    errors=[{"message": "Unknown plan \"team\".", "fix": "Choose `pro`, `business` or `advanced`."}, {"message": "That opened your subscription settings…", "fix": "Not an error — you already have a subscription; change it there."}],
    tips=["Manage, cancel or download invoices any time from Dashboard → Billing → Manage subscription."],
    related=["topup", "products", "transactions"],
))

# ------------------------------------------------------------------ products
C.append(dict(
    slug="products", name="products", aliases=["pricing", "prices"], group="Billing",
    summary="The product catalog with live per-GB prices. No login needed.",
    synopsis="buyproxy products",
    intro="`products` lists everything you can buy with its product key (what other commands take), minimum order, live price per GB, the volume bonus and the plan prices. It works before you've logged in — handy for comparing before you sign up.",
    options=[],
    howItWorks="Prices are fetched live each time, so they're always current. The **Key** column is exactly what `topup`, `generate` and `customers allocate` accept.",
    examples=[ex("See the catalog", "buyproxy products", "Proxy products\n" + table(
        ["Product", "Key", "Per GB", "Min"],
        [["Core Residential", "residential", "$1.99", "1 GB"], ["Premium Residential", "premium", "$3.49", "2 GB"], ["ISP Rotating", "isp", "$2.49", "1 GB"],
         ["Mobile Proxies", "mobile", "$3.99", "1 GB"], ["Datacenter IPv4", "ipv4", "$0.89", "1 GB"], ["IPv6 Proxies", "ipv6", "$0.29", "1 GB"]], ["l", "l", "r", "r"])
        + "\n\nℹ Buy 100 GB or more in one top-up and get 10% extra, free.", "Prices above are illustrative — run the command for today's rates.")],
    json="`--json` returns the full catalog: `products[]` (`productKey`, `name`, `minGb`, `pricePerGbCents`), `volumeBonus` and `plans[]`.",
    errors=[], tips=[], related=["topup", "subscribe"],
))

# ------------------------------------------------------------------ transactions
C.append(dict(
    slug="transactions", name="transactions", aliases=["tx", "payments"], group="Billing",
    summary="Payment history — or the status of one payment, optionally waiting for it to settle.",
    synopsis="buyproxy transactions [id] [-n 10] [--wait]",
    intro="Every top-up and subscription payment is a transaction. List your recent ones, or look one up by id — and with `--wait`, block until it settles, which is what scripts want after creating a checkout.",
    options=[opt("[id]", "A transaction id (from `topup` or `subscribe`). Omit to list recent payments."), opt("-n, --limit", "How many payments to list (up to 100).", "<n>", "10"), opt("--wait", "With an id: keep polling until the payment is `succeeded` or `failed`.")],
    howItWorks="""**Status** is one of `pending` (waiting for payment), `succeeded` (paid and credited) or `failed` (expired or declined — nothing was charged).

A reseller key's pool purchases appear here too, tagged `(pool)`.""",
    examples=[
        ex("Recent payments", "buyproxy transactions -n 3", "Payments\n" + table(
            ["Date", "Item", "Method", "Amount", "Status", "ID"],
            [["10/1/2026", "100 GB residential", "card", "$199.00", "succeeded", "st_5b1c…"], ["9/14/2026", "pro plan (yearly)", "card", "$324.00", "succeeded", "st_77ad…"], ["9/2/2026", "20 GB premium", "crypto", "$69.80", "pending", "crypto_e41b…"]],
            ["l", "l", "l", "r", "l", "l"])),
        ex("Wait for one payment", "buyproxy tx st_5b1c… --wait", box("Payment", ["Item     100 GB residential", "Amount   $199.00 USD via card", "Status   succeeded", "Date     10/1/2026, 3:42:10 PM", "ID       st_5b1c…"])),
    ],
    json="Returns the transaction (or an array of them): `id`, `kind`, `status`, `paymentMethod`, `interval`, `amountCents`, `currency`, `gb`, `productKey`, `plan`, `resellerPool`, `createdAt`.",
    errors=[{"message": "Transaction not found", "fix": "Ids are scoped to your account — check you're using the same key that created it."}],
    tips=["Invoices for succeeded payments are in Dashboard → Billing."], related=["topup", "subscribe"],
))

# ------------------------------------------------------------------ customers
CUST_EX_LIST = "Customers (2)\n" + table(["Label", "Username", "Status", "Created"], [["Acme Inc", "bp_acme_1a2b", "● active", "10/1/2026"], ["Globex", "bp_globex_9c3d", "● suspended", "9/20/2026"]])
C.append(dict(
    slug="customers", name="customers", aliases=["customer", "c"], group="Reseller",
    summary="Manage your reseller customers: create, fund, inspect, suspend and generate for them.",
    synopsis="buyproxy customers [list|new|show|rename|suspend|activate|usage|allocate|generate] …",
    intro="""The reseller commands let you run a proxy business from the terminal. A **customer** is an isolated sub-account with its own plans and credentials; you fund it from your **reseller pool** and generate proxies on its behalf.

These commands need a **reseller key** (`bp_live_…`, Business plan or higher). With a personal key the CLI tells you so and shows where to create one. Anywhere a command needs a customer and you didn't give one, the CLI shows a picker.""",
    options=[],
    howItWorks="""The typical flow:

1. `buyproxy pool topup residential --gb 500 --card` — fund your pool.
2. `buyproxy customers new "Acme Inc"` — create a customer; note the username.
3. `buyproxy customers allocate <username> residential 20` — give them 20 GB.
4. `buyproxy customers generate <username> -c DE -n 5` — generate for them.
5. `buyproxy customers usage <username>` — see how much they've used.
6. `buyproxy customers suspend <username>` — pause them if they stop paying.""",
    subs=[
        {"name": "list", "synopsis": "buyproxy customers [list] [--status active|suspended]", "desc": "Lists your customers. `ls` also works, and `list` is the default, so plain `buyproxy customers` works.",
         "options": [opt("--status", "Only show `active` or `suspended` customers.", "<status>")],
         "examples": [ex("List", "buyproxy customers", CUST_EX_LIST)]},
        {"name": "new", "synopsis": "buyproxy customers new <label…>", "desc": "Creates an isolated sub-account with **no bandwidth**. The label is your own name or reference for them (their company or email); it can be up to 100 characters and spaces are fine. Prints the new username.",
         "options": [], "examples": [ex("Create", 'buyproxy customers new "Acme Inc"', "  Username       bp_acme_1a2b\n\n  Next: buyproxy customers allocate bp_acme_1a2b")]},
        {"name": "show", "synopsis": "buyproxy customers show [username]", "desc": "A card with the customer's status plus a usage bar for each plan they hold. GB you've allocated that is still being added shows as `arriving shortly`.",
         "options": [], "examples": [ex("Show", "buyproxy customers show bp_acme_1a2b", box("Acme Inc", ["Username  bp_acme_1a2b", "Status    ● active", "Created   10/1/2026"]) + "\n\nPlans\n  Core Residential     " + bar(0.9) + "  18.0 GB / 20.0 GB\n  ＋ 5.00 GB premium arriving shortly")]},
        {"name": "rename", "synopsis": "buyproxy customers rename <username> <new label…>", "desc": "Changes the label. Nothing else about the customer changes.", "options": [], "examples": [ex("Rename", 'buyproxy customers rename bp_acme_1a2b "Acme Corporation"')]},
        {"name": "suspend / activate", "synopsis": "buyproxy customers suspend <username>\nbuyproxy customers activate <username>", "desc": "A suspended customer can't generate new proxies (the API returns `403`). **Proxy lines you've already handed out may keep working until they rotate**, so stop distributing them when you suspend. `activate` reverses it instantly.",
         "options": [], "examples": [ex("Suspend", "buyproxy customers suspend bp_acme_1a2b")]},
        {"name": "usage", "synopsis": "buyproxy customers usage [username]", "desc": "How much each plan has used, with remaining and total GB — the numbers to bill from. Current snapshot only (the upstream network refreshes it roughly every 30 minutes); there's no per-request history.",
         "options": [], "examples": [ex("Usage", "buyproxy customers usage bp_acme_1a2b", "Usage\n  residential    " + bar(0.9) + "  2.00 GB used of 20.0 GB")]},
        {"name": "allocate", "synopsis": "buyproxy customers allocate [username] [product] [gb]", "desc": "Moves whole GB of one product from your pool onto a customer. Every call carries an automatically generated **idempotency key**, so a retry after a network blip can never allocate twice. It fails with a clear message if your pool doesn't hold enough — top it up first. Allocated GB can't be moved back to the pool.",
         "options": [], "examples": [ex("Allocate", "buyproxy customers allocate bp_acme_1a2b premium 10", "✔ 10 GB of premium → bp_acme_1a2b   (40.0 GB left in your pool)")]},
        {"name": "generate", "synopsis": "buyproxy customers generate <username> [product] [-c US] [-n 5] [-s 10] [--socks5] [-f format] [--copy]", "desc": "Generates proxies from the customer's plans, with exactly the same options as [`buyproxy generate`](/docs/cli/generate). A suspended customer gets a clear `403`.",
         "options": [], "examples": [ex("Generate for a customer", "buyproxy customers generate bp_acme_1a2b -c DE -n 5 -f plain")]},
    ],
    examples=[],
    json="All subcommands accept `--json` and print the same objects the [reseller API](/docs/api-reference/reseller/customers) returns.",
    errors=[
        {"message": "This needs a reseller API key (bp_live_…).", "fix": "Create one under Dashboard → Reseller → API keys (Business plan or higher), then `buyproxy login`."},
        {"message": "Not enough Core Residential in your reseller pool", "fix": "Top up the pool: `buyproxy pool topup residential --gb 100 --card`."},
        {"message": "This customer is suspended — reactivate it to generate proxies.", "fix": "`buyproxy customers activate <username>`."},
        {"message": "Customer not found", "fix": "Usernames are scoped to your account; copy it from `buyproxy customers`."},
    ],
    tips=["Allocate in the same unit you bill in — allocations are final.", "Script the whole flow with `--json` and your own order ids as the idempotency source via the [API](/docs/api-reference/reseller/customers)."],
    related=["pool", "generate", "topup"],
))

# ------------------------------------------------------------------ pool
C.append(dict(
    slug="pool", name="pool", aliases=[], group="Reseller",
    summary="Your unallocated reseller bandwidth — and how to fill it.",
    synopsis="buyproxy pool\nbuyproxy pool topup [product] [--gb N] [--card|--crypto]",
    intro="The **reseller pool** is bandwidth you've bought but not yet given to a customer, tracked per product. Pool GB is priced like a normal top-up — including the 10% bonus at 100 GB or more — and the price is fixed when you buy, so later price changes don't affect what's already in your pool.",
    options=[opt("topup", "Buy into the pool. Takes the same options as `buyproxy topup` (product, `--gb`, `--card`/`--crypto`, `-y`, `--no-open`, `--no-wait`).")],
    howItWorks="`buyproxy pool` shows one bar per product relative to your largest holding. Empty products say `empty`. `buyproxy pool topup` is `buyproxy topup --pool`: it creates the checkout, opens it, and waits — the GB lands in your pool the moment the payment settles.",
    examples=[
        ex("Look at your pool", "buyproxy pool", "Reseller pool\n  Core Residential     " + bar(1) + "  50.0 GB\n  Premium Residential  " + bar(0.4) + "  20.0 GB\n  ISP Rotating         " + "░" * 24 + "  empty\n\n  Fill it: buyproxy pool topup   Give it out: buyproxy customers allocate"),
        ex("Buy 500 GB into the pool", "buyproxy pool topup residential --gb 500 --card"),
    ],
    json="`buyproxy pool --json` prints `[ { productKey, productId, label, gb } ]`.",
    errors=[{"message": "This needs a reseller API key (bp_live_…).", "fix": "Pool commands are for reseller keys only."}],
    tips=[], related=["customers", "topup"],
))

# ------------------------------------------------------------------ login
C.append(dict(
    slug="login", name="login", aliases=[], group="Account",
    summary="Save your API key so every command just works.",
    synopsis="buyproxy login [--key bp_key_…]",
    intro="`login` stores your API key locally after checking it with BuyProxy, so you don't have to pass it every time. Both personal (`bp_key_…`) and reseller (`bp_live_…`) keys work; the CLI detects which and shows the right menu.",
    options=[opt("--key", "Provide the key non-interactively instead of being prompted.", "<key>")],
    howItWorks="""1. Create a key under [Dashboard → API keys](/dashboard/api-keys) (personal) or Dashboard → Reseller → API keys.
2. Run `buyproxy login` and paste it — the characters are masked as you type.
3. The CLI checks the format, then asks BuyProxy who the key belongs to. If it's rejected, nothing is saved.
4. It's written to `~/.config/buyproxy/config.json` (or `$XDG_CONFIG_HOME/buyproxy/`) with permissions `0600`, readable only by you.

**Prefer not to store a key at all?** Set `BUYPROXY_API_KEY` in your environment instead — it's used automatically.""",
    examples=[
        ex("Interactive", "buyproxy login", "? Paste your API key ••••••••••••\n✔ Key verified\n✔ Logged in as you@example.com (pro plan)\n  Saved to /home/you/.config/buyproxy/config.json"),
        ex("In CI", 'echo "$BUYPROXY_API_KEY" | xargs buyproxy login --key', None, "Or skip `login` entirely and export `BUYPROXY_API_KEY` for the job."),
    ],
    json='`--json` prints `{ "ok": true, "email": …, "label": …, "kind": "personal" | "reseller" }`.',
    errors=[
        {"message": "That doesn't look like a BuyProxy API key.", "fix": "Keys start with `bp_key_` (personal) or `bp_live_` (reseller) followed by hex characters."},
        {"message": "BuyProxy rejected that key.", "fix": "It may have been copied incompletely or revoked — create a fresh one."},
    ],
    tips=["On shared machines, prefer the environment variable and avoid `--key`, because command-line arguments can show up in process listings and shell history."],
    related=["whoami", "logout", "signup"],
))

C.append(dict(
    slug="logout", name="logout", aliases=[], group="Account",
    summary="Forget the saved API key.", synopsis="buyproxy logout",
    intro="Deletes `~/.config/buyproxy/config.json`. It does **not** revoke the key — do that from Dashboard → API keys if it was exposed. A key supplied through `BUYPROXY_API_KEY` or `--key` isn't affected.",
    options=[], howItWorks=None,
    examples=[ex("Log out", "buyproxy logout", "✔ Logged out — saved key removed.")],
    json='`--json` prints `{ "ok": true, "removed": true|false }`.', errors=[], tips=[], related=["login", "whoami"],
))

C.append(dict(
    slug="whoami", name="whoami", aliases=[], group="Account",
    summary="Show the account behind the current key and where the key came from.",
    synopsis="buyproxy whoami",
    intro="Useful when something behaves unexpectedly — it confirms which account and key type you're using, with the key masked.",
    options=[],
    howItWorks="The **Read from** line tells you which source won: `--key flag`, `BUYPROXY_API_KEY`, or the saved config file (the precedence is in that order).",
    examples=[ex("Who am I?", "buyproxy whoami", "Account\n  Email          you@example.com\n  Key type       personal\n  Details        pro plan\n  Key            bp_key_abcde••••••••f3a9\n  Read from      /home/you/.config/buyproxy/config.json")],
    json='`--json` prints `{ "email", "kind", "detail", "key" }` with the key masked.',
    errors=[{"message": "You're not logged in.", "fix": "Run `buyproxy login`."}], tips=[], related=["login", "logout"],
))

C.append(dict(
    slug="signup", name="signup", aliases=[], group="Account",
    summary="Create a BuyProxy account without leaving the terminal.",
    synopsis="buyproxy signup",
    intro="Creates an account with email and password, verified by a six-digit code. API keys are issued from the dashboard, so the last step opens it for you.",
    options=[],
    howItWorks="""1. Enter your email, a password (at least 6 characters) and a name.
2. BuyProxy emails a six-digit code — enter it to verify and create the account.
3. The CLI opens the API keys page; create a key there and run `buyproxy login`.

A new account on a major email provider includes a small free bandwidth trial so you can try `generate` and `test` right away.""",
    examples=[ex("Sign up", "buyproxy signup", "? Email you@example.com\n? Password (min 6 characters) ••••••••\n? Name you\n✔ Code sent — check your inbox\n? 6-digit code 482913\n✔ Account created\n\nNext: create an API key in your dashboard, then run buyproxy login.")],
    json="`--json` prints the verification result.",
    errors=[{"message": "An already-verified account exists for this email.", "fix": "Just `buyproxy login` (or reset your password on the website)."}, {"message": "Too many attempts — request a new code.", "fix": "Run `buyproxy signup` again to get a fresh code."}],
    tips=[], related=["login"],
))

C.append(dict(
    slug="dashboard", name="dashboard", aliases=["open"], group="Tools",
    summary="Open your BuyProxy dashboard in the browser.", synopsis="buyproxy dashboard",
    intro="Opens `https://www.buyproxy.org/dashboard`. The URL is always printed too, so it works over SSH where no browser can open.",
    options=[], howItWorks=None, examples=[ex("Open", "buyproxy dashboard", "Opening https://www.buyproxy.org/dashboard")], json=None, errors=[], tips=[], related=["docs"],
))

C.append(dict(
    slug="docs", name="docs", aliases=[], group="Tools",
    summary="Open the API and SDK documentation.", synopsis="buyproxy docs",
    intro="Opens the API reference at `https://www.buyproxy.org/docs/api-reference/introduction`.",
    options=[], howItWorks=None, examples=[ex("Open the docs", "buyproxy docs")], json=None, errors=[], tips=[], related=["dashboard"],
))

C.append(dict(
    slug="completion", name="completion", aliases=[], group="Tools",
    summary="Print a shell-completion script for bash, zsh or fish.",
    synopsis="buyproxy completion bash|zsh|fish",
    intro="Tab-completes command names. Add the output to your shell's startup once.",
    options=[],
    howItWorks="""```bash
# bash
buyproxy completion bash >> ~/.bashrc

# zsh (put the file on your fpath, then restart the shell)
buyproxy completion zsh > "${fpath[1]}/_buyproxy"

# fish
buyproxy completion fish > ~/.config/fish/completions/buyproxy.fish
```""",
    examples=[], json=None, errors=[], tips=[], related=[],
))

GROUPS = ["Proxies", "Billing", "Account", "Reseller", "Tools"]
header = '''// GENERATED by buyproxy-sdks/tools/cli_docs.py — edit the tool, not this file.
export interface CliOption { flag: string; arg: string | null; default: string | null; desc: string }
export interface CliExample { title: string; cmd: string; output: string | null; note: string | null }
export interface CliSub { name: string; synopsis: string; desc: string; options: CliOption[]; examples: CliExample[] }
export interface CliError { message: string; fix: string }
export interface CliCommand {
  slug: string; name: string; aliases: string[]; group: string; summary: string; synopsis: string; intro: string;
  options: CliOption[]; howItWorks: string | null; subs?: CliSub[]; examples: CliExample[]; json: string | null;
  errors: CliError[]; tips: string[]; related: string[];
}

export const CLI_COMMANDS: CliCommand[] = '''
pathlib.Path(sys.argv[1]).write_text(header + json.dumps(C, indent=2, ensure_ascii=False) + ";\n")
if len(sys.argv) > 2:
    nav = [{"slug": c["slug"], "name": c["name"], "group": c["group"]} for c in C]
    pathlib.Path(sys.argv[2]).write_text("// GENERATED by tools/cli_docs.py — small on purpose: this is imported by client-side search.\nexport const CLI_NAV: { slug: string; name: string; group: string }[] = " + json.dumps(nav, indent=2) + ";\n")
print("wrote", sys.argv[1], len(C), "commands")
