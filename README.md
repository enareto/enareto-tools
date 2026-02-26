# Financial Skills

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) providing specialized financial planning skills. Each skill encodes domain expertise, modeling standards, and validation tooling that prevent common errors in financial modeling.

This plugin currently includes one skill, with more planned:

## Available Skills

### Retirement Projections

Comprehensive retirement financial planning with cash flow projections, Monte Carlo analysis, tax-optimized withdrawal strategies, and historical backtesting.

What it covers:

- 12 non-negotiable modeling requirements (Social Security COLA, progressive tax brackets, FICA, RMDs, capital gains, state taxes, and more)
- 4 withdrawal strategy comparisons (conventional, tax-bracket optimized, proportional, Roth-bridge)
- 4 asset allocation approaches (static, age-based glide path, rising equity, bucket strategy)
- Monte Carlo simulation (2,000+ runs) and historical backtesting (1928-present)
- Roth conversion analysis and annuity modeling
- Automated model validation scripts

Trigger phrases: "can I retire", "retirement plan", "financial plan", "withdrawal strategy", "Roth conversion", "4% rule", "Monte Carlo", "how much do I need to retire", and more.

## Installation

```bash
claude plugin add github:enareto/financial-skills
```

Once installed, the skill activates automatically when Claude detects a relevant retirement planning question.

## Structure

```
financial-skills/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── retirement-projections/
        ├── SKILL.md              # Skill definition and workflow
        ├── references/           # Tax rules, strategies, return data
        └── scripts/              # Model validation and backtesting
```

## License

MIT — see [LICENSE](LICENSE) for details.
