use buyproxy::*;

#[tokio::main]
async fn main() {
    let base = format!("http://127.0.0.1:{}", std::env::var("PORT").unwrap_or("4010".into()));
    let personal = Client::builder().api_key("bp_key_test").base_url(&base).build();
    let reseller = Client::builder().api_key("bp_live_test").base_url(&base).build();

    personal.products().await.unwrap();
    personal.account().await.unwrap();
    personal.balances().await.unwrap();
    personal.plans().list().await.unwrap();
    let g = personal.plans().generate("plan_1", &GenerateParams::new().protocol(Protocol::Socks5).count(2).country("US").city("Austin").sticky_minutes(10)).await.unwrap();
    assert!(g.proxies.len() == 2 && g.proxies[0].protocol == Protocol::Socks5);
    personal.topup().card(&CardCheckoutParams::Topup { product_key: ProductKey::Residential, gb: 10 }).await.unwrap();
    personal.topup().card(&CardCheckoutParams::Plan { plan: PaidPlan::Pro, interval: Some(BillingInterval::Year) }).await.unwrap();
    personal.topup().crypto(ProductKey::Residential, 5).await.unwrap();
    personal.transactions().list(Some(5)).await.unwrap();
    personal.transactions().get("st_abc").await.unwrap();
    reseller.reseller().me().await.unwrap();
    reseller.reseller().customers().list(Some(CustomerStatus::Active)).await.unwrap();
    reseller.reseller().customers().create("Acme").await.unwrap();
    reseller.reseller().customers().get("bp_acme_1").await.unwrap();
    reseller.reseller().customers().update("bp_acme_1", None, Some(CustomerStatus::Suspended)).await.unwrap();
    reseller.reseller().customers().usage("bp_acme_1").await.unwrap();
    reseller.reseller().customers().allocate("bp_acme_1", &AllocateParams { product_key: ProductKey::Premium, gb: 10, idempotency_key: Some("order-1".into()) }).await.unwrap();
    reseller.reseller().customers().generate("bp_acme_1", "plan_1", &GenerateParams::new().country("DE")).await.unwrap();
    reseller.reseller().pool().get().await.unwrap();
    reseller.reseller().pool().topup_card(ProductKey::Residential, 100).await.unwrap();
    reseller.reseller().pool().topup_crypto(ProductKey::Residential, 100).await.unwrap();
    let anon = Client::builder().api_key("").base_url(&base).build();
    anon.signup("a@b.co", "hunter22", Some("A")).await.unwrap();
    anon.verify_otp("a@b.co", "482913").await.unwrap();
    anon.resend_otp("a@b.co").await.unwrap();
    assert!(Client::builder().api_key("bad").base_url(&base).build().account().await.unwrap_err().is_authentication());
    Client::builder().api_key("ratelimit-once").base_url(&base).build().account().await.unwrap();
    assert!(Client::builder().api_key("broke").base_url(&base).build().reseller().customers().allocate("bp_acme_1", &AllocateParams { product_key: ProductKey::Premium, gb: 999, idempotency_key: None }).await.unwrap_err().is_insufficient_bandwidth());
    println!("rust smoke OK");
}
