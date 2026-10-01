package main

import (
	"context"
	"errors"
	"fmt"
	"os"

	bp "github.com/DishantSinghDev2/buyproxy-go"
)

func must(err error) {
	if err != nil {
		fmt.Println("FAIL:", err)
		os.Exit(1)
	}
}

func main() {
	ctx := context.Background()
	base := bp.WithBaseURL("http://127.0.0.1:" + os.Getenv("PORT"))
	personal := bp.New(bp.WithAPIKey("bp_key_test"), base)
	reseller := bp.New(bp.WithAPIKey("bp_live_test"), base)

	_, err := personal.Products.List(ctx); must(err)
	_, err = personal.Account.Get(ctx); must(err)
	_, err = personal.Balances.List(ctx); must(err)
	_, err = personal.Plans.List(ctx); must(err)
	g, err := personal.Plans.Generate(ctx, "plan_1", &bp.GenerateParams{Protocol: bp.SOCKS5, Count: 2, Country: "US", City: "Austin", StickyMinutes: 10}); must(err)
	if len(g.Proxies) != 2 || g.Proxies[0].Protocol != bp.SOCKS5 { must(errors.New("generate parse")) }
	_, err = personal.Topup.Card(ctx, bp.TopupCardParams(bp.ProductResidential, 10)); must(err)
	_, err = personal.Topup.Card(ctx, bp.PlanCardParams(bp.PlanPro, bp.Yearly)); must(err)
	_, err = personal.Topup.Crypto(ctx, bp.ProductResidential, 5); must(err)
	_, err = personal.Transactions.List(ctx, 5); must(err)
	_, err = personal.Transactions.Get(ctx, "st_abc"); must(err)
	_, err = reseller.Reseller.Me(ctx); must(err)
	_, err = reseller.Reseller.Customers.List(ctx, bp.CustomerActive); must(err)
	_, err = reseller.Reseller.Customers.Create(ctx, "Acme"); must(err)
	_, err = reseller.Reseller.Customers.Get(ctx, "bp_acme_1"); must(err)
	_, err = reseller.Reseller.Customers.Update(ctx, "bp_acme_1", bp.CustomerUpdate{Status: bp.CustomerSuspended}); must(err)
	_, err = reseller.Reseller.Customers.Usage(ctx, "bp_acme_1"); must(err)
	_, err = reseller.Reseller.Customers.Allocate(ctx, "bp_acme_1", bp.AllocateParams{ProductKey: bp.ProductPremium, GB: 10, IdempotencyKey: "order-1"}); must(err)
	_, err = reseller.Reseller.Customers.Generate(ctx, "bp_acme_1", bp.CustomerGenerateParams{PlanID: "plan_1", GenerateParams: bp.GenerateParams{Country: "DE"}}); must(err)
	_, err = reseller.Reseller.Pool.Get(ctx); must(err)
	_, err = reseller.Reseller.Pool.TopupCard(ctx, bp.PoolTopupParams{ProductKey: bp.ProductResidential, GB: 100}); must(err)
	_, err = reseller.Reseller.Pool.TopupCrypto(ctx, bp.PoolTopupParams{ProductKey: bp.ProductResidential, GB: 100}); must(err)
	anon := bp.New(bp.WithAPIKey(""), base)
	_, err = anon.Auth.Signup(ctx, bp.SignupParams{Email: "a@b.co", Password: "hunter22", Name: "A"}); must(err)
	_, err = anon.Auth.VerifyOTP(ctx, "a@b.co", "482913"); must(err)
	must(anon.Auth.ResendOTP(ctx, "a@b.co"))
	if _, err = bp.New(bp.WithAPIKey("bad"), base).Account.Get(ctx); !errors.Is(err, bp.ErrAuthentication) { must(errors.New("expected auth error")) }
	_, err = bp.New(bp.WithAPIKey("ratelimit-once"), base).Account.Get(ctx); must(err)
	if _, err = bp.New(bp.WithAPIKey("broke"), base).Reseller.Customers.Allocate(ctx, "bp_acme_1", bp.AllocateParams{ProductKey: bp.ProductPremium, GB: 999}); !errors.Is(err, bp.ErrInsufficientBandwidth) { must(errors.New("expected 402")) }
	fmt.Println("go smoke OK")
}
