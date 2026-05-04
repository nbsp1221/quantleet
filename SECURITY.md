# Security Policy

## Supported Versions

The first supported public beta line is `0.1.0b1`.

## Reporting Vulnerabilities

Report any vulnerability privately.

Do not file secrets, credentials, exploit details, or fund-moving risks in a
public issue. Use GitHub Security Advisories when available, or contact the
maintainer privately before disclosing sensitive details.

Include:

- affected version or commit
- reproduction steps
- potential impact
- whether credentials, secrets, or exchange accounts are involved

## Secrets

Never commit API keys, exchange credentials, wallet material, private account
data, or production secrets. Remove secrets from examples, notebooks, logs, and
test fixtures before opening a pull request.

## Financial Safety

QuantCraft is research and software tooling, not financial advice. Backtest
results do not guarantee future performance. You are responsible for data
quality, assumptions, execution risk, and trading decisions.

Report behavior that could misstate fills, costs, positions, orders, or risk
with enough detail for maintainers to reproduce it. Trading and execution
changes require stricter review because they can affect financial assumptions.
