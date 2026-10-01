$LOAD_PATH.unshift File.expand_path('../buyproxy-ruby/lib', __dir__)
require 'buyproxy'

base = "http://127.0.0.1:#{ENV.fetch('PORT', '4010')}"
personal = BuyProxy::Client.new(api_key: 'bp_key_test', base_url: base)
reseller = BuyProxy::Client.new(api_key: 'bp_live_test', base_url: base)

personal.products.list
personal.account.get
personal.balances.list
personal.plans.list
g = personal.plans.generate('plan_1', protocol: 'socks5', count: 2, country: 'US', city: 'Austin', sticky_minutes: 10)
raise 'generate parse' unless g.size == 2 && g.first.protocol == 'socks5'
personal.topup.card(product_key: 'residential', gb: 10)
personal.topup.card(plan: 'pro', interval: 'year')
personal.topup.crypto(product_key: 'residential', gb: 5)
personal.transactions.list(limit: 5)
personal.transactions.get('st_abc')
reseller.reseller.me
reseller.reseller.customers.list(status: 'active')
reseller.reseller.customers.create(label: 'Acme')
reseller.reseller.customers.get('bp_acme_1')
reseller.reseller.customers.update('bp_acme_1', status: 'suspended')
reseller.reseller.customers.usage('bp_acme_1')
reseller.reseller.customers.allocate('bp_acme_1', product_key: 'premium', gb: 10, idempotency_key: 'order-1')
reseller.reseller.customers.generate('bp_acme_1', plan_id: 'plan_1', country: 'DE')
reseller.reseller.pool.get
reseller.reseller.pool.topup_card(product_key: 'residential', gb: 100)
reseller.reseller.pool.topup_crypto(product_key: 'residential', gb: 100)
anon = BuyProxy::Client.new(api_key: '', base_url: base)
anon.auth.signup(email: 'a@b.co', password: 'hunter22', name: 'A')
anon.auth.verify_otp(email: 'a@b.co', code: '482913')
anon.auth.resend_otp(email: 'a@b.co')
begin
  BuyProxy::Client.new(api_key: 'bad', base_url: base).account.get
  raise 'expected auth error'
rescue BuyProxy::AuthenticationError
end
BuyProxy::Client.new(api_key: 'ratelimit-once', base_url: base).account.get
begin
  BuyProxy::Client.new(api_key: 'broke', base_url: base).reseller.customers.allocate('bp_acme_1', product_key: 'premium', gb: 999)
  raise 'expected 402'
rescue BuyProxy::InsufficientBandwidthError
end
puts 'ruby smoke OK'
