#!/usr/bin/env python3
"""scaffold.py <repo-dir> <repo-name> <human-name>  — writes the community files every SDK repo shares."""
import sys, pathlib, textwrap

repo_dir, repo, human = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
YEAR = "2026"

def w(path, text):
    p = repo_dir / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip("\n"))

w("LICENSE", f"""
    MIT License

    Copyright (c) {YEAR} BuyProxy

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
""")

w("SECURITY.md", f"""
    # Security policy

    ## Reporting a vulnerability

    Please **do not open a public issue** for security problems. Email
    **security@buyproxy.org** with a description and steps to reproduce. We aim to
    acknowledge reports within 2 business days and will keep you updated until the
    issue is resolved.

    ## API keys

    Never commit API keys (`bp_key_…` / `bp_live_…`). If a key is exposed, revoke it
    immediately from your [dashboard](https://www.buyproxy.org/dashboard/api-keys) and
    create a new one.
""")

w("CONTRIBUTING.md", f"""
    # Contributing to {repo}

    Thanks for helping improve the {human}! Bug reports, docs fixes and pull requests are all welcome.

    1. **Open an issue first** for anything bigger than a typo, so we can agree on the approach.
    2. Fork, create a branch, and keep each pull request focused on one change.
    3. Add or update tests — the SDK is checked against the same request log as every other
       BuyProxy SDK, so wire-format changes need to land in all of them.
    4. Run the test suite and linters described in the README before pushing.

    The API itself is documented at <https://www.buyproxy.org/docs/api-reference/introduction>.
    Questions? <support@buyproxy.org>.
""")

w(".github/PULL_REQUEST_TEMPLATE.md", """
    ## What does this change?

    ## How was it tested?

    - [ ] Tests added or updated
    - [ ] README / docs updated if behaviour changed
""")

w(".github/ISSUE_TEMPLATE/config.yml", """
    blank_issues_enabled: false
    contact_links:
      - name: BuyProxy support
        url: https://www.buyproxy.org/contact
        about: Billing, account and proxy-quality questions go to support, not GitHub issues.
      - name: API reference
        url: https://www.buyproxy.org/docs/api-reference/introduction
        about: Endpoint and parameter documentation.
""")

w(".github/ISSUE_TEMPLATE/bug_report.yml", f"""
    name: Bug report
    description: Something in the {human} isn't working as documented
    labels: [bug]
    body:
      - type: textarea
        id: what
        attributes:
          label: What happened?
          description: What did you expect, and what did you get instead?
        validations: {{ required: true }}
      - type: textarea
        id: repro
        attributes:
          label: Minimal reproduction
          description: A short snippet. **Remove API keys and proxy credentials.**
          render: shell
        validations: {{ required: true }}
      - type: input
        id: version
        attributes:
          label: SDK version and runtime
          placeholder: e.g. 1.0.0 on Node 22 / Python 3.12 / Go 1.24
        validations: {{ required: true }}
""")

w(".github/ISSUE_TEMPLATE/feature_request.yml", f"""
    name: Feature request
    description: Suggest an improvement to the {human}
    labels: [enhancement]
    body:
      - type: textarea
        id: problem
        attributes:
          label: What are you trying to do?
        validations: {{ required: true }}
      - type: textarea
        id: idea
        attributes:
          label: What would you like to see?
""")

w(".github/dependabot.yml", """
    version: 2
    updates:
      - package-ecosystem: github-actions
        directory: /
        schedule: { interval: monthly }
""")

w("CHANGELOG.md", """
    # Changelog

    ## 1.0.0

    - Initial release: personal API (catalog, account, balances, plans, proxy generation, card and
      crypto top-ups, transactions), reseller API (customers, pool, allocation) and account creation.
""")
print("scaffolded", repo_dir)
