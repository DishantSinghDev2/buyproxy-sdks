# Releasing the SDKs

Every repo publishes from GitHub Actions when you push a tag `vX.Y.Z`. The tag must match the version in the
package manifest (the workflows check this). Nothing publishes until the secrets / trusted publishers below exist.

```bash
# in any SDK repo, after bumping the version and CHANGELOG.md
git commit -am "Release 1.0.1" && git tag v1.0.1 && git push origin main v1.0.1
```

## One-time setup per registry

| Repo | Registry | What you need | Where |
|---|---|---|---|
| `buyproxy-node` | npm — `buyproxy` | Automation token → secret **`NPM_TOKEN`** | npmjs.com → Access Tokens (type *Automation*, publish rights) |
| `buyproxy-cli` | npm — `buyproxy-cli` | Same **`NPM_TOKEN`**; plus **`TAP_GITHUB_TOKEN`** (contents: write on `homebrew-tap`) to bump the Homebrew formula | GitHub → Settings → Developer settings → fine-grained token |
| `buyproxy-python` | PyPI — `buyproxy` | **Trusted Publisher** (no secret): owner `DishantSinghDev2`, repo `buyproxy-python`, workflow `release.yml`, environment `pypi` | pypi.org → Publishing → *Add a new pending publisher* |
| `buyproxy-ruby` | RubyGems — `buyproxy` | **Trusted Publisher** (no secret): repo `buyproxy-ruby`, workflow `release.yml`, environment `rubygems` | rubygems.org → Trusted publishers → *Create pending publisher* |
| `buyproxy-rust` | crates.io — `buyproxy` | API token → secret **`CARGO_REGISTRY_TOKEN`** | crates.io → Account → API Tokens |
| `buyproxy-dotnet` | NuGet — `BuyProxy` | API key → secret **`NUGET_API_KEY`** | nuget.org → API Keys (glob `BuyProxy*`) |
| `buyproxy-java` | Maven Central — `org.buyproxy:buyproxy` | Verified namespace `org.buyproxy` (DNS TXT record on **buyproxy.org**), Central Portal user token → **`MAVEN_CENTRAL_USERNAME`** / **`MAVEN_CENTRAL_PASSWORD`**, a GPG key → **`GPG_PRIVATE_KEY`** / **`GPG_PASSPHRASE`** | central.sonatype.com → Namespaces / Account |
| `buyproxy-go` | Go proxy / pkg.go.dev | Nothing — the git tag *is* the release | — |
| `buyproxy-php` | Packagist — `buyproxy/buyproxy` | Submit the repo once at packagist.org/packages/submit; it then follows tags automatically | packagist.org |
| `homebrew-tap` | Homebrew | Nothing — `buyproxy-cli`'s release bumps `Formula/buyproxy.rb` | — |

Add repository secrets under **Settings → Secrets and variables → Actions**. Create the `pypi` and `rubygems`
**environments** under **Settings → Environments**.

## Release order

1. `buyproxy-node` (the CLI bundles it).
2. Everything else in any order.
3. `buyproxy-cli` last — its release publishes to npm, attaches `buyproxy.mjs`, and updates the Homebrew tap with the
   new tarball's SHA-256.

## Homebrew formula placeholder

`homebrew-tap/Formula/buyproxy.rb` ships with a placeholder `sha256` of all zeros. `brew install` will fail on it until
`buyproxy-cli` v1.0.0 is published and the release workflow rewrites `url` and `sha256`. To do it by hand:

```bash
curl -fsSL https://registry.npmjs.org/buyproxy-cli/-/buyproxy-cli-1.0.0.tgz | shasum -a 256
```

## Naming checks

Before the first release confirm the names are still free: `npm view buyproxy`, `pip index versions buyproxy`,
`gem list -r buyproxy`, `cargo search buyproxy`, and `nuget.org/packages/BuyProxy`. If one is taken, change the name in
the manifest and the README install line together.
