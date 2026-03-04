# Enareto Tools

A plugin marketplace for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Claude Cowork](https://claude.com/cowork) providing specialized financial planning skills. Each skill encodes domain expertise, modeling standards, and validation tooling that prevent common errors in financial modeling.

*** DISCLAIMER ***: The skill just allows an AI to create a more structured plan. This is by no means financial advice. AI can make
mistakes. Use the output to discuss with a financial advisor or other professional. Use at your own risk. 

## Installation

Add the marketplace:

```bash
/plugin marketplace add enareto/enareto-tools
```

Install the financial skills plugin:

```bash
/plugin install financial-skills@enareto-tools
```

Once installed, the skill activates automatically when Claude detects a relevant retirement planning question.

## Available Plugins

### financial-skills

Comprehensive retirement financial planning with cash flow projections, Monte Carlo analysis, tax-optimized withdrawal strategies, and historical backtesting.

What it covers:

- 12 non-negotiable modeling requirements (Social Security COLA, progressive tax brackets, FICA, RMDs, capital gains, state taxes, and more)
- 4 withdrawal strategy comparisons (conventional, tax-bracket optimized, proportional, Roth-bridge)
- 4 asset allocation approaches (static, age-based glide path, rising equity, bucket strategy)
- Monte Carlo simulation (2,000+ runs) and historical backtesting (1928-present)
- Roth conversion analysis and annuity modeling
- Automated model validation scripts

Trigger phrases: "can I retire", "retirement plan", "financial plan", "withdrawal strategy", "Roth conversion", "4% rule", "Monte Carlo", "how much do I need to retire", and more.

## Structure

```
enareto-tools/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace definition
├── plugins/
│   └── financial-skills/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest
│       └── skills/
│           └── retirement-projections/
│               ├── SKILL.md      # Skill definition and workflow
│               ├── references/   # Tax rules, strategies, return data
│               └── scripts/      # Model validation and backtesting
├── LICENSE
└── README.md
```

## License

MIT — see [LICENSE](LICENSE) for details.
