using BuyProxy;

var baseUrl = "http://127.0.0.1:" + (Environment.GetEnvironmentVariable("PORT") ?? "4010");
var personal = new BuyProxyClient(new BuyProxyOptions { ApiKey = "bp_key_test", BaseUrl = baseUrl });
var reseller = new BuyProxyClient(new BuyProxyOptions { ApiKey = "bp_live_test", BaseUrl = baseUrl });

await personal.Products.ListAsync();
await personal.Account.GetAsync();
await personal.Balances.ListAsync();
await personal.Plans.ListAsync();
var g = await personal.Plans.GenerateAsync("plan_1", new GenerateParams { Protocol = "socks5", Count = 2, Country = "US", City = "Austin", StickyMinutes = 10 });
if (g.Proxies.Count != 2 || g.Proxies[0].Protocol != "socks5") throw new Exception("generate parse");
await personal.Topup.CardAsync(CardCheckoutParams.Topup("residential", 10));
await personal.Topup.CardAsync(CardCheckoutParams.Plan("pro", "year"));
await personal.Topup.CryptoAsync("residential", 5);
await personal.Transactions.ListAsync(5);
await personal.Transactions.GetAsync("st_abc");
await reseller.Reseller.MeAsync();
await reseller.Reseller.Customers.ListAsync("active");
await reseller.Reseller.Customers.CreateAsync("Acme");
await reseller.Reseller.Customers.GetAsync("bp_acme_1");
await reseller.Reseller.Customers.UpdateAsync("bp_acme_1", status: "suspended");
await reseller.Reseller.Customers.UsageAsync("bp_acme_1");
await reseller.Reseller.Customers.AllocateAsync("bp_acme_1", "premium", 10, "order-1");
await reseller.Reseller.Customers.GenerateAsync("bp_acme_1", "plan_1", new GenerateParams { Country = "DE" });
await reseller.Reseller.Pool.GetAsync();
await reseller.Reseller.Pool.TopupCardAsync("residential", 100);
await reseller.Reseller.Pool.TopupCryptoAsync("residential", 100);
var anon = new BuyProxyClient(new BuyProxyOptions { ApiKey = "", BaseUrl = baseUrl });
await anon.Auth.SignupAsync("a@b.co", "hunter22", "A");
await anon.Auth.VerifyOtpAsync("a@b.co", "482913");
await anon.Auth.ResendOtpAsync("a@b.co");
try { await new BuyProxyClient(new BuyProxyOptions { ApiKey = "bad", BaseUrl = baseUrl }).Account.GetAsync(); throw new Exception("expected auth error"); } catch (AuthenticationException) { }
await new BuyProxyClient(new BuyProxyOptions { ApiKey = "ratelimit-once", BaseUrl = baseUrl }).Account.GetAsync();
try { await new BuyProxyClient(new BuyProxyOptions { ApiKey = "broke", BaseUrl = baseUrl }).Reseller.Customers.AllocateAsync("bp_acme_1", "premium", 999); throw new Exception("expected 402"); } catch (InsufficientBandwidthException) { }
Console.WriteLine("dotnet smoke OK");
