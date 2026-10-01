#!/usr/bin/env python3
"""ci_gen.py <sdks-dir> — writes .gitignore + GitHub Actions workflows into every SDK repo."""
import sys, pathlib, textwrap
root = pathlib.Path(sys.argv[1])

def w(repo, path, text):
    p = root / repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip("\n"))

W = {}

# ---------------------------------------------------------------- node
w("buyproxy-node", ".gitignore", "node_modules\ndist\n*.tgz\n.DS_Store\ncoverage\n")
w("buyproxy-node", ".github/workflows/ci.yml", """
    name: CI
    on:
      push: { branches: [main] }
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix: { node: [18, 20, 22] }
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-node@v4
            with: { node-version: "${{ matrix.node }}" }
          - run: npm install --no-audit --no-fund
          - run: npm run typecheck
          - run: npm test
          - run: npm run build
          - name: ESM and CJS entry points both load
            run: |
              node --input-type=module -e "import('./dist/index.js').then(m => { if (typeof m.BuyProxy !== 'function') process.exit(1) })"
              node -e "if (typeof require('./dist/index.cjs').BuyProxy !== 'function') process.exit(1)"
""")
w("buyproxy-node", ".github/workflows/release.yml", """
    name: Release
    # Push a tag vX.Y.Z (matching package.json) to publish to npm with provenance.
    on:
      push: { tags: ["v*"] }
    permissions:
      contents: write
      id-token: write
    jobs:
      publish:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-node@v4
            with: { node-version: 22, registry-url: "https://registry.npmjs.org" }
          - run: test "v$(node -p "require('./package.json').version")" = "${GITHUB_REF_NAME}"
          - run: npm install --no-audit --no-fund
          - run: npm run typecheck && npm test && npm run build
          - run: npm publish --provenance --access public
            env: { NODE_AUTH_TOKEN: "${{ secrets.NPM_TOKEN }}" }
          - uses: softprops/action-gh-release@v2
            with: { generate_release_notes: true }
""")

# ---------------------------------------------------------------- python
w("buyproxy-python", ".gitignore", ".venv\n__pycache__\n*.egg-info\ndist\nbuild\n.mypy_cache\n.ruff_cache\n.pytest_cache\n.DS_Store\n")
w("buyproxy-python", ".github/workflows/ci.yml", """
    name: CI
    on:
      push: { branches: [main] }
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix: { python: ["3.9", "3.10", "3.11", "3.12", "3.13"] }
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with: { python-version: "${{ matrix.python }}" }
          - run: pip install -e ".[dev]"
          - run: ruff check src tests
          - run: mypy src
          - run: pytest
""")
w("buyproxy-python", ".github/workflows/release.yml", """
    name: Release
    # Push a tag vX.Y.Z to publish to PyPI via Trusted Publishing (no token stored).
    # One-time setup: PyPI → your project → Publishing → add a trusted publisher
    #   owner DishantSinghDev2 · repo buyproxy-python · workflow release.yml · environment pypi
    on:
      push: { tags: ["v*"] }
    jobs:
      publish:
        runs-on: ubuntu-latest
        environment: pypi
        permissions:
          id-token: write
          contents: write
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with: { python-version: "3.12" }
          - run: pip install build && python -m build
          - uses: pypa/gh-action-pypi-publish@release/v1
          - uses: softprops/action-gh-release@v2
            with: { generate_release_notes: true, files: dist/* }
""")

# ---------------------------------------------------------------- go
w("buyproxy-go", ".gitignore", "*.test\n*.out\n.DS_Store\n")
w("buyproxy-go", ".github/workflows/ci.yml", """
    name: CI
    on:
      push: { branches: [main] }
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix: { go: ["1.21", "1.22", "1.23", "1.24"] }
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-go@v5
            with: { go-version: "${{ matrix.go }}" }
          - run: test -z "$(gofmt -l .)"
          - run: go vet ./...
          - run: go test -race ./...
""")
w("buyproxy-go", ".github/workflows/release.yml", """
    name: Release
    # Go modules are published by the git tag itself. This workflow cuts the GitHub release
    # and asks the Go proxy to index the version so pkg.go.dev picks it up immediately.
    on:
      push: { tags: ["v*"] }
    permissions: { contents: write }
    jobs:
      release:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-go@v5
            with: { go-version: "1.24" }
          - run: go vet ./... && go test ./...
          - uses: softprops/action-gh-release@v2
            with: { generate_release_notes: true }
          - name: Warm the Go proxy / pkg.go.dev
            run: GOPROXY=https://proxy.golang.org GO111MODULE=on go list -m "github.com/DishantSinghDev2/buyproxy-go@${GITHUB_REF_NAME}"
""")

# ---------------------------------------------------------------- php
w("buyproxy-php", ".gitignore", "vendor\ncomposer.lock\n.phpunit.cache\n.phpunit.result.cache\n.DS_Store\n")
w("buyproxy-php", ".github/workflows/ci.yml", """
    name: CI
    on:
      push: { branches: [main] }
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix: { php: ["8.1", "8.2", "8.3", "8.4"] }
        steps:
          - uses: actions/checkout@v4
          - uses: shivammathur/setup-php@v2
            with: { php-version: "${{ matrix.php }}", extensions: curl, json, coverage: none }
          - run: composer install --no-interaction --prefer-dist
          - run: vendor/bin/phpunit
""")
w("buyproxy-php", ".github/workflows/release.yml", """
    name: Release
    # Packagist updates itself from GitHub tags once the package is submitted (packagist.org → Submit).
    # This workflow only cuts the GitHub release.
    on:
      push: { tags: ["v*"] }
    permissions: { contents: write }
    jobs:
      release:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: shivammathur/setup-php@v2
            with: { php-version: "8.3", extensions: curl, json }
          - run: composer install --no-interaction && vendor/bin/phpunit
          - uses: softprops/action-gh-release@v2
            with: { generate_release_notes: true }
""")

# ---------------------------------------------------------------- ruby
w("buyproxy-ruby", ".gitignore", "*.gem\nGemfile.lock\n.bundle\ncoverage\n.DS_Store\n")
w("buyproxy-ruby", ".github/workflows/ci.yml", """
    name: CI
    on:
      push: { branches: [main] }
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix: { ruby: ["3.0", "3.1", "3.2", "3.3", "3.4"] }
        steps:
          - uses: actions/checkout@v4
          - uses: ruby/setup-ruby@v1
            with: { ruby-version: "${{ matrix.ruby }}", bundler-cache: true }
          - run: bundle exec rake test
""")
w("buyproxy-ruby", ".github/workflows/release.yml", """
    name: Release
    # Push a tag vX.Y.Z to publish to RubyGems via Trusted Publishing (no API key stored).
    # One-time setup: rubygems.org → your gem → Trusted publishers → add
    #   owner DishantSinghDev2 · repo buyproxy-ruby · workflow release.yml · environment rubygems
    # (for the very first release, create a pending trusted publisher on rubygems.org)
    on:
      push: { tags: ["v*"] }
    permissions:
      contents: write
      id-token: write
    jobs:
      publish:
        runs-on: ubuntu-latest
        environment: rubygems
        steps:
          - uses: actions/checkout@v4
          - uses: ruby/setup-ruby@v1
            with: { ruby-version: "3.3", bundler-cache: true }
          - run: bundle exec rake test
          - uses: rubygems/release-gem@v1
          - uses: softprops/action-gh-release@v2
            with: { generate_release_notes: true }
""")

# ---------------------------------------------------------------- java
w("buyproxy-java", ".gitignore", "target\n*.class\n.idea\n*.iml\n.DS_Store\n")
w("buyproxy-java", ".github/workflows/ci.yml", """
    name: CI
    on:
      push: { branches: [main] }
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix: { java: [17, 21] }
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-java@v4
            with: { distribution: temurin, java-version: "${{ matrix.java }}", cache: maven }
          - run: mvn -B verify
""")
w("buyproxy-java", ".github/workflows/release.yml", """
    name: Release
    # Push a tag vX.Y.Z to publish to Maven Central through the Sonatype Central Portal.
    # Secrets: MAVEN_CENTRAL_USERNAME, MAVEN_CENTRAL_PASSWORD (a Central Portal user token),
    #          GPG_PRIVATE_KEY (armored), GPG_PASSPHRASE.
    # One-time: verify the org.buyproxy namespace on central.sonatype.com (DNS TXT record on buyproxy.org).
    on:
      push: { tags: ["v*"] }
    permissions: { contents: write }
    jobs:
      publish:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-java@v4
            with:
              distribution: temurin
              java-version: 17
              cache: maven
              server-id: central
              server-username: MAVEN_USERNAME
              server-password: MAVEN_PASSWORD
              gpg-private-key: ${{ secrets.GPG_PRIVATE_KEY }}
              gpg-passphrase: MAVEN_GPG_PASSPHRASE
          - run: test "v$(mvn -q help:evaluate -Dexpression=project.version -DforceStdout)" = "${GITHUB_REF_NAME}"
          - run: mvn -B -Prelease deploy
            env:
              MAVEN_USERNAME: ${{ secrets.MAVEN_CENTRAL_USERNAME }}
              MAVEN_PASSWORD: ${{ secrets.MAVEN_CENTRAL_PASSWORD }}
              MAVEN_GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
          - uses: softprops/action-gh-release@v2
            with: { generate_release_notes: true }
""")

# ---------------------------------------------------------------- dotnet
w("buyproxy-dotnet", ".gitignore", "bin\nobj\n*.nupkg\n*.snupkg\n.vs\n.idea\n.DS_Store\n")
w("buyproxy-dotnet", ".github/workflows/ci.yml", """
    name: CI
    on:
      push: { branches: [main] }
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-dotnet@v4
            with:
              dotnet-version: |
                6.0.x
                8.0.x
          - run: dotnet build -c Release
          - run: dotnet test -c Release --no-build
""")
w("buyproxy-dotnet", ".github/workflows/release.yml", """
    name: Release
    # Push a tag vX.Y.Z to publish the NuGet package. Secret: NUGET_API_KEY (nuget.org → API keys).
    on:
      push: { tags: ["v*"] }
    permissions: { contents: write }
    jobs:
      publish:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-dotnet@v4
            with:
              dotnet-version: |
                6.0.x
                8.0.x
          - run: dotnet test -c Release
          - run: dotnet pack src/BuyProxy/BuyProxy.csproj -c Release -o out
          - run: dotnet nuget push "out/*.nupkg" --api-key "${{ secrets.NUGET_API_KEY }}" --source https://api.nuget.org/v3/index.json --skip-duplicate
          - uses: softprops/action-gh-release@v2
            with: { generate_release_notes: true, files: out/* }
""")

# ---------------------------------------------------------------- rust
w("buyproxy-rust", ".gitignore", "target\nCargo.lock\n.DS_Store\n")
w("buyproxy-rust", ".github/workflows/ci.yml", """
    name: CI
    on:
      push: { branches: [main] }
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: dtolnay/rust-toolchain@stable
            with: { components: "rustfmt, clippy" }
          - uses: Swatinem/rust-cache@v2
          - run: cargo fmt --check
          - run: cargo clippy --all-targets -- -D warnings
          - run: cargo test
""")
w("buyproxy-rust", ".github/workflows/release.yml", """
    name: Release
    # Push a tag vX.Y.Z (matching Cargo.toml) to publish to crates.io. Secret: CARGO_REGISTRY_TOKEN.
    on:
      push: { tags: ["v*"] }
    permissions: { contents: write }
    jobs:
      publish:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: dtolnay/rust-toolchain@stable
          - run: test "v$(cargo metadata --no-deps --format-version 1 | python3 -c 'import sys,json; print(json.load(sys.stdin)["packages"][0]["version"])')" = "${GITHUB_REF_NAME}"
          - run: cargo test
          - run: cargo publish
            env: { CARGO_REGISTRY_TOKEN: "${{ secrets.CARGO_REGISTRY_TOKEN }}" }
          - uses: softprops/action-gh-release@v2
            with: { generate_release_notes: true }
""")

# ---------------------------------------------------------------- cli + tap
w("buyproxy-cli", ".gitignore", "node_modules\ndist\n*.tgz\n.DS_Store\n")
w("homebrew-tap", ".gitignore", ".DS_Store\n")
print("workflows written")
