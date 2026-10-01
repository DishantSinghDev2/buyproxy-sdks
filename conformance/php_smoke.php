<?php
require __DIR__ . '/../buyproxy-php/vendor/autoload.php';

use BuyProxy\Client;
use BuyProxy\Exceptions\AuthenticationException;
use BuyProxy\Exceptions\InsufficientBandwidthException;

$base = 'http://127.0.0.1:' . (getenv('PORT') ?: '4010');
$personal = new Client(apiKey: 'bp_key_test', baseUrl: $base);
$reseller = new Client(apiKey: 'bp_live_test', baseUrl: $base);

$personal->products->list();
$personal->account->get();
$personal->balances->list();
$personal->plans->list();
$g = $personal->plans->generate('plan_1', protocol: 'socks5', count: 2, country: 'US', city: 'Austin', stickyMinutes: 10);
assert(count($g) === 2 && $g->proxies[0]->protocol === 'socks5');
$personal->topup->card(productKey: 'residential', gb: 10);
$personal->topup->card(plan: 'pro', interval: 'year');
$personal->topup->crypto('residential', 5);
$personal->transactions->list(limit: 5);
$personal->transactions->get('st_abc');
$reseller->reseller->me();
$reseller->reseller->customers->list(status: 'active');
$reseller->reseller->customers->create('Acme');
$reseller->reseller->customers->get('bp_acme_1');
$reseller->reseller->customers->update('bp_acme_1', status: 'suspended');
$reseller->reseller->customers->usage('bp_acme_1');
$reseller->reseller->customers->allocate('bp_acme_1', 'premium', 10, idempotencyKey: 'order-1');
$reseller->reseller->customers->generate('bp_acme_1', 'plan_1', country: 'DE');
$reseller->reseller->pool->get();
$reseller->reseller->pool->topupCard('residential', 100);
$reseller->reseller->pool->topupCrypto('residential', 100);
$anon = new Client(apiKey: '', baseUrl: $base);
$anon->auth->signup('a@b.co', 'hunter22', 'A');
$anon->auth->verifyOtp('a@b.co', '482913');
$anon->auth->resendOtp('a@b.co');
try { (new Client(apiKey: 'bad', baseUrl: $base))->account->get(); throw new Exception('expected auth error'); } catch (AuthenticationException) {}
(new Client(apiKey: 'ratelimit-once', baseUrl: $base))->account->get();
try { (new Client(apiKey: 'broke', baseUrl: $base))->reseller->customers->allocate('bp_acme_1', 'premium', 999); throw new Exception('expected 402'); } catch (InsufficientBandwidthException) {}
echo "php smoke OK\n";
