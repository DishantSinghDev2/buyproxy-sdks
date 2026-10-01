import os, asyncio
from buyproxy import BuyProxy, AsyncBuyProxy, AuthenticationError, InsufficientBandwidthError

base = "http://127.0.0.1:" + os.environ.get("PORT", "4010")
personal = BuyProxy("bp_key_test", base_url=base)
reseller = BuyProxy("bp_live_test", base_url=base)

personal.products.list()
personal.account.get()
personal.balances.list()
personal.plans.list()
g = personal.plans.generate("plan_1", protocol="socks5", count=2, country="US", city="Austin", sticky_minutes=10)
assert len(g.proxies) == 2 and g.proxies[0].protocol == "socks5"
personal.topup.card(product_key="residential", gb=10)
personal.topup.card(plan="pro", interval="year")
personal.topup.crypto(product_key="residential", gb=5)
personal.transactions.list(limit=5)
personal.transactions.get("st_abc")
reseller.reseller.me()
reseller.reseller.customers.list(status="active")
reseller.reseller.customers.create("Acme")
reseller.reseller.customers.get("bp_acme_1")
reseller.reseller.customers.update("bp_acme_1", status="suspended")
reseller.reseller.customers.usage("bp_acme_1")
reseller.reseller.customers.allocate("bp_acme_1", product_key="premium", gb=10, idempotency_key="order-1")
reseller.reseller.customers.generate("bp_acme_1", plan_id="plan_1", country="DE")
reseller.reseller.pool.get()
reseller.reseller.pool.topup_card(product_key="residential", gb=100)
reseller.reseller.pool.topup_crypto(product_key="residential", gb=100)
anon = BuyProxy(api_key="", base_url=base)
anon.auth.signup("a@b.co", "hunter22", "A")
anon.auth.verify_otp("a@b.co", "482913")
anon.auth.resend_otp("a@b.co")
try:
    BuyProxy("bad", base_url=base).account.get(); raise SystemExit("expected AuthenticationError")
except AuthenticationError:
    pass
BuyProxy("ratelimit-once", base_url=base).account.get()
try:
    BuyProxy("broke", base_url=base).reseller.customers.allocate("bp_acme_1", product_key="premium", gb=999); raise SystemExit("expected 402")
except InsufficientBandwidthError:
    pass

# the async client must be a faithful twin — a quick pass over it too (not part of the logged sequence)
async def twin() -> None:
    import httpx
    async with AsyncBuyProxy("bp_key_test", base_url=base) as bp:
        assert (await bp.account.get()).plan == "pro"
if not os.environ.get("CONFORMANCE_LOG_ONLY"):
    pass
asyncio.run(twin(), debug=False) if os.environ.get("RUN_ASYNC") else None
print("python smoke OK")
