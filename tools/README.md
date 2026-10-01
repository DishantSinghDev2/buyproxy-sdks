# Maintenance tools

The PHP, Ruby, Java and C# response models are **generated** from one schema, and the READMEs, CI workflows and community
files are generated from shared templates, so the eight SDKs can't drift apart.

| Script | What it does |
|---|---|
| `models_schema.py` | The single source of truth for response models |
| `gen.py <php\|ruby\|java\|csharp> <out>` | Generates the model classes — `python3 tools/gen.py php ../buyproxy-php/src/Models` |
| `readme_gen.py <workspace>` | Rewrites `README.md` in every SDK repo (edit the snippets in this file, not the READMEs) |
| `ci_gen.py <workspace>` | Rewrites `.gitignore` and the CI / release workflows in every SDK repo |
| `scaffold.py <repo> <name> <title>` | LICENSE, SECURITY, CONTRIBUTING, issue/PR templates, dependabot |

`<workspace>` is the folder that contains the `buyproxy-*` repos side by side.
