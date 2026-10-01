import java.time.Duration;
import org.buyproxy.*;

public class JavaSmoke {
    public static void main(String[] a) {
        String base = "http://127.0.0.1:" + System.getenv().getOrDefault("PORT", "4010");
        BuyProxy personal = BuyProxy.builder().apiKey("bp_key_test").baseUrl(base).build();
        BuyProxy reseller = BuyProxy.builder().apiKey("bp_live_test").baseUrl(base).build();

        personal.products().list();
        personal.account().get();
        personal.balances().list();
        personal.plans().list();
        GeneratedProxies g = personal.plans().generate("plan_1", GenerateParams.create().protocol("socks5").count(2).country("US").city("Austin").stickyMinutes(10));
        if (g.size() != 2 || !g.get(0).protocol().equals("socks5")) throw new AssertionError("generate parse");
        personal.topup().card(CardCheckoutParams.topup("residential", 10));
        personal.topup().card(CardCheckoutParams.plan("pro", "year"));
        personal.topup().crypto("residential", 5);
        personal.transactions().list(5);
        personal.transactions().get("st_abc");
        reseller.reseller().me();
        reseller.reseller().customers().list("active");
        reseller.reseller().customers().create("Acme");
        reseller.reseller().customers().get("bp_acme_1");
        reseller.reseller().customers().update("bp_acme_1", null, "suspended");
        reseller.reseller().customers().usage("bp_acme_1");
        reseller.reseller().customers().allocate("bp_acme_1", "premium", 10, "order-1");
        reseller.reseller().customers().generate("bp_acme_1", "plan_1", GenerateParams.create().country("DE"));
        reseller.reseller().pool().get();
        reseller.reseller().pool().topupCard("residential", 100);
        reseller.reseller().pool().topupCrypto("residential", 100);
        BuyProxy anon = BuyProxy.builder().apiKey("").baseUrl(base).build();
        anon.auth().signup("a@b.co", "hunter22", "A");
        anon.auth().verifyOtp("a@b.co", "482913");
        anon.auth().resendOtp("a@b.co");
        try { BuyProxy.builder().apiKey("bad").baseUrl(base).build().account().get(); throw new AssertionError("expected auth error"); } catch (BuyProxyException.Authentication e) {}
        BuyProxy.builder().apiKey("ratelimit-once").baseUrl(base).build().account().get();
        try { BuyProxy.builder().apiKey("broke").baseUrl(base).build().reseller().customers().allocate("bp_acme_1", "premium", 999, null); throw new AssertionError("expected 402"); } catch (BuyProxyException.InsufficientBandwidth e) {}
        System.out.println("java smoke OK");
    }
}
