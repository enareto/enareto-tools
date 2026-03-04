---
name: retirement-projections
description: "This skill should be used when the user asks about building or updating a retirement financial plan, cash flow projections, Monte Carlo analysis, tax-optimized withdrawal strategies, or historical backtesting. It covers scenarios where the user says things like 'can I retire', 'retirement projections', 'financial plan', 'withdrawal strategy', 'Roth conversion', '4% rule', 'safe withdrawal rate', 'how much do I need to retire', 'RMD planning', 'required minimum distributions', 'Social Security optimization', 'asset allocation for retirement', 'sequence of returns risk', 'retirement income', or 'cash flow analysis'. Also applicable when reviewing existing plans, running scenarios, comparing withdrawal strategies, or modeling retirement spending. Embeds modeling standards that prevent common errors which can swing results by 60+ percentage points."
---

# Retirement Projections

## Why This Skill Exists

Financial planning models are dangerous when wrong. A naive model can tell a couple they have a 37% chance of retirement success when the correct answer is 100%. The difference is not in exotic strategies — it's in getting the basics right: tax treatment, salary growth, Social Security COLA, and realistic spending patterns.

This skill exists to prevent those errors. Every requirement below comes from a real mistake that produced a materially wrong result for a real client scenario.

## Your Responsibility

You are not a financial advisor. You are building a quantitative model. But models that look professional and produce precise numbers (like "36.5% Monte Carlo success rate") carry implicit authority. A naive user cannot distinguish a careful model from a broken one — both produce spreadsheets with charts.

This means:
- **Every assumption must be stated explicitly.** No silent defaults.
- **Every model must be validated against sanity checks** before presenting results.
- **Uncertainty must be communicated proportional to model quality.** If you haven't modeled something, say so.
- **Never present a single number without sensitivity context.** Show what changes the result.

---

## Workflow

### Step 1: Gather Client Data

Collect or confirm these inputs. Do not proceed with defaults for anything marked *required* — ask the user.

**Required:**
- Ages (client, spouse if applicable)
- Target retirement age(s)
- Current accounts: type (traditional 401k/IRA, Roth, taxable, cash), balances, current allocation
- Current salaries (both, if couple)
- Social Security estimates from ssa.gov (monthly FRA benefit for each person)

**Required — Spending (gather with enough detail to separate categories):**
- Total current annual spending
- Obligatory expenses: housing (mortgage/rent, property tax, insurance, maintenance), healthcare premiums, utilities, food, transportation, insurance premiums, debt payments. These are non-negotiable — they can't be cut in a downturn.
- Discretionary expenses: travel, dining out, entertainment, hobbies, gifts, charitable giving, clothing beyond basics. These are what get cut when markets crash.
- Ask: "What's your mortgage payoff date?" — this matters because a large obligatory expense dropping off in year X changes the whole picture.

**Required — One-Time Expected Expenses:**
- College funding: children's ages, target schools (public/private), years of funding, current 529 balances
- Major purchases: car replacement cycle and cost, home renovation, second home
- Family events: weddings, elder care obligations
- Any other lump sums with approximate year and amount

**Important but can default if not provided (state default explicitly):**
- Salary growth rate (default: 3%/year — inflation + merit)
- 401(k) contribution level (default: maximum including catch-up if age 50+)
- Employer match (default: ask, or 0% if unknown)
- Inflation assumption (default: 2.5-3%)
- State tax rate (default: ask for state, look up rate)
- Risk tolerance / target allocation

**Don't forget to ask about:**
- Pensions
- Rental income or other passive income
- Existing annuities
- Debt (mortgage payoff date, other loans)

### Step 2: Build the Model

This is where most errors happen. Read `references/modeling-standards.md` for the complete technical specification. The critical requirements are summarized here.

#### Non-Negotiable Modeling Requirements

These are not suggestions. Omitting any one of these can swing Monte Carlo results by 20-60 percentage points. Read `references/modeling-standards.md` for complete formulas and implementation details.

| # | Requirement | Impact if Omitted |
|---|-------------|-------------------|
| 1 | **Social Security COLA** — compound benefits at ~2.5%/year from today, not just from claiming date | 20-40pp MC swing; 35-45% benefit underestimate |
| 2 | **Progressive federal tax brackets** — use MFJ brackets + standard deduction, never a flat rate | $15-30K/year tax error |
| 3 | **401(k) reduces taxable income** — deduct pre-tax contributions from W-2 income | Portfolio 15-25% low at retirement |
| 4 | **FICA taxes** — model SS/Medicare tax on wages; note these stop in retirement | Overstates retirement taxes |
| 5 | **Social Security benefit taxation** — up to 85% of SS is taxable based on combined income | Understates retirement taxes |
| 6 | **Salary growth** — use 3%/year (inflation + merit); final salary ~34% higher over 10 years | Under-saves $200-400K |
| 7 | **Obligatory vs. discretionary spending** — separate spending into non-negotiable floor and flexible discretionary with go-go/slow-go/no-go phases | Underspends early, overspends late |
| 8 | **Dynamic spending guardrails** — cut/boost only discretionary spending; obligatory is the floor | 10-20pp MC swing |
| 9 | **One-time expenses** — model as lump-sum withdrawals in specific years with funding source, not smoothed | Misses sequence-of-returns risk |
| 10 | **State income taxes** — use real progressive brackets from `references/state-taxes.md`, never a flat rate | $15-40K/year swing |
| 11 | **Capital gains taxes** — taxable withdrawals use LTCG rates (0/15/20%), not ordinary income rates; see `references/capital-gains-taxes.md` | Overestimates taxable account cost |
| 12 | **Required Minimum Distributions** — model forced withdrawals from traditional accounts starting at 73/75; see `references/rmd-rules.md` | Misses forced taxable income, bracket creep |

### Step 3: Withdrawal Strategy Analysis

The order of withdrawals from different account types (traditional, Roth, taxable) materially affects lifetime taxes and portfolio longevity. Model and compare at least three strategies. Read `references/withdrawal-strategies.md` for full implementation.

Strategies to compare: **Conventional** (taxable → traditional → Roth), **Tax-Bracket Optimized** (fill low brackets from traditional, remainder from Roth/taxable), **Proportional** (withdraw proportionally from all accounts), and **Roth-Bridge** (heavy traditional/taxable draws during low-income gap years before SS). Tax-bracket optimization typically saves $50-200K in lifetime taxes vs. conventional ordering.

For each strategy, report: total lifetime taxes, final portfolio value, Monte Carlo success rate, and year-by-year effective tax rate. Present the comparison with the recommended strategy highlighted.

### Step 4: Asset Allocation Strategy

Do not assume a static 60/40. Model and compare at least two approaches. Read `references/allocation-strategies.md` for full implementation.

Strategies to compare: **Static Allocation** (fixed split), **Age-Based Glide Path** (declining equity), **Rising Equity Glide Path** (Kitces/Pfau — start conservative at 30-40%, increase to 60-70% by age 80+, reducing sequence-of-returns risk), and **Bucket Strategy** (time-based buckets: cash for years 1-3, bonds for 4-10, equities for 11+).

Run Monte Carlo with each strategy on the same client data. Report success rate, median final portfolio, and worst-case (10th percentile). The right strategy depends on the client.

### Step 5: Validate Before Presenting

**Run these sanity checks before showing any results to the user.** If any check fails, fix the model — don't present caveated garbage.

Read `references/validation-checklist.md` for the full checklist. Also run the automated validation:

```bash
python scripts/validate_model.py projections.json [retirement_year]
```

The critical checks:

1. **Effective tax rate sanity:** Working years should show 22-32% effective rate for $300-500K household income. If you're seeing 15% or 40%, something is wrong.

2. **SS COLA check:** SS at claiming year should be significantly higher than today's stated estimate. If George's SS shows $48,420 at year 13 instead of ~$65,000, COLA is missing.

3. **Portfolio growth during accumulation:** With $400K+ combined salary and max 401(k), the portfolio should roughly double over 10 years even with conservative returns. If it doesn't, check that contributions are actually being added.

4. **Late-life SS vs. spending:** By age 85+, SS with COLA should cover a very large fraction (often 80-120%+) of realistic spending. If the model shows large portfolio withdrawals at age 90, either spending is too high or SS COLA is missing.

5. **Withdrawal strategy comparison:** If all strategies produce identical lifetime taxes, the model probably isn't differentiating account types correctly.

6. **One-time expense impact:** If adding $200K of college expenses doesn't visibly dip the portfolio in that year, they aren't being modeled.

7. **Obligatory floor test:** Spending should never drop below obligatory expenses, even under worst-case guardrails.

### Step 6: Monte Carlo Simulation

Run at minimum 2,000 simulations. Use historical return distributions:
- Stocks: 7% mean, 16% volatility (log-normal or Gaussian)
- Bonds: 4% mean, 6% volatility
- Cash: 2% mean, 1% volatility

Report: success rate, median final portfolio, 10th percentile, 25th percentile.

**"Success" means:** portfolio never reaches zero, OR guaranteed income (SS + annuities) covers at least 60% of expenses at the point of depletion (meaning the person isn't destitute — they just have reduced spending).

**Always run multiple scenarios**, not just one:
- Base case (recommended strategy + allocation)
- Each withdrawal strategy × recommended allocation
- Recommended strategy × each allocation approach
- With/without annuity options
- Early retirement (-2 years)
- One-time expense sensitivity (what if college costs 50% more?)

### Step 7: Historical Backtest

Monte Carlo uses synthetic returns (random draws from a distribution). This misses serial correlation, mean reversion, inflation regimes, and the specific character of real market history. The historical backtest is a complementary validation.

Read `references/historical-returns.md` for the S&P 500 annual total return data (1928-present) and bond/cash return series.

**How to run it:**
- Take the client's projection model (same spending, taxes, SS, withdrawals)
- Instead of random returns, use actual historical S&P 500 returns for stocks, 10-year Treasury returns for bonds, T-bill returns for cash
- Run every possible starting year: "What if they retired in 1929? 1966? 1973? 2000? 2007?"
- Each starting year produces one complete 30-year trajectory using the actual returns that followed

**What to report:**
- Number of historical periods that survived vs. failed
- Worst starting year and its trajectory (usually 1966 or 1929 — stagflation or depression)
- Best starting year
- Median outcome across all starting years
- How the recommended plan performs vs. the conventional plan in the *worst* historical period

**Why this matters:** If Monte Carlo says 100% but the 1966 backtest shows depletion at age 82, there's something wrong — either the MC is using unrealistic return distributions, or the backtest is revealing a regime (prolonged stagflation) that synthetic random draws don't capture well. The two methods should broadly agree. If they don't, investigate why.

**Critical caveat:** The historical record has only ~3 independent 30-year periods. So "8 out of 65 starting years survived" is more informative than "87.7% success" — don't over-precision the backtest.

### Step 8: Roth Conversion Analysis

If there's a gap between retirement and SS claiming (common — 2-5 years with no earned income), this is a Roth conversion opportunity. Model:
- Target: fill the 12% bracket (~$95-127K taxable income for MFJ with standard deduction)
- Cap conversions at 5% of traditional balance per year to avoid bracket creep
- Window: from retirement to ~2 years after last SS starts
- Result: lower future RMDs, tax-free growth, tax diversification

This interacts with the withdrawal strategy: the bracket-optimized strategy naturally includes Roth conversions as part of its year-by-year optimization.

### Step 9: Annuity Analysis (if appropriate)

SPIA (Single Premium Immediate Annuity) analysis should be offered but not forced. Model at 2-3 premium levels. Key parameters:
- Joint-life, 100% survivor benefit
- Payout rate: ~5-5.5% for mid-60s couple
- Taxable portion: ~75% (exclusion ratio for non-qualified) or 100% (qualified/traditional)
- Funded from traditional balance at retirement

**Critical context:** If SS with COLA already provides a guaranteed income floor that exceeds late-life obligatory spending, the annuity adds psychological comfort but not mathematical necessity. State this clearly rather than selling an annuity the numbers don't justify.

### Step 10: Generate Deliverables

Two required outputs:

**1. Word Document (Financial Plan)**
Use the docx skill. Include:
- Executive summary with bottom-line answer ("Can they retire? Yes/No and why")
- Key metrics table (portfolio at retirement, MC success, median final, SS at claiming)
- Why the plan works (or doesn't) — explain the mechanics, not just the numbers
- Spending breakdown: obligatory vs. discretionary, one-time expenses timeline
- Phase-by-phase breakdown (accumulation, distribution by decade)
- Withdrawal strategy comparison (lifetime taxes, final portfolio for each approach)
- Asset allocation recommendation with rationale
- Tax strategy (Roth conversions, withdrawal sequencing)
- Monte Carlo comparison table (multiple scenarios)
- Historical backtest results: worst-case period, survival rate
- Action items (specific, prioritized)
- Disclaimer

**2. Excel Workbook (Interactive Financial Model)**
Use the xlsx skill. Include sheets for:
- Year-by-year projection (primary plan): year, ages, phase, salary, 401k contributions, SS income, obligatory expenses, discretionary expenses, one-time expenses, total expenses, taxes, withdrawals by account type, balances, withdrawal rate, guaranteed income coverage %
- Withdrawal strategy comparison (side-by-side lifetime tax totals)
- Allocation strategy comparison
- Alternative scenario (with annuity, or without dynamic, etc.)
- Historical backtest summary (worst/median/best starting years)
- Monte Carlo summary
- Key milestones
- Assumptions (all inputs, stated explicitly with notes)

Color-code spending phases (go-go green, slow-go blue, no-go pink). Highlight one-time expenses in yellow. Mark the year SS exceeds obligatory spending. Show the withdrawal strategy comparison clearly.

---

## Common Errors and How They Manifest

| Error | Symptom | Impact |
|-------|---------|--------|
| Missing SS COLA | SS shows today's estimate at claiming year | 20-40pp MC swing |
| Flat tax rate | Effective rate doesn't change with income | $10-30K/yr tax error |
| No 401(k) deduction from taxable income | Over-taxation during accumulation | Portfolio 15-25% low at retirement |
| No salary growth | Final salary = starting salary | Under-saves $200-400K |
| Flat retirement spending | Same spend at 65 and 90 | Underspends early, overspends late |
| No dynamic guardrails | No response to market conditions | 10-20pp MC swing |
| No standard deduction | Over-taxes by $6-10K/yr | Cascading over-withdrawal |
| Same withdrawal order always | Traditional-first when in 12% bracket | $50-200K lifetime tax waste |
| Static allocation for 30 years | 80% stocks at age 90, or 40% at age 65 | Suboptimal risk profile |
| One-time expenses smoothed | $200K college spread over 10 years | Misses sequence-of-returns risk |
| Guardrails cut mortgage | Total spending cut 15% including housing | Unrealistic — only discretionary flexes |
| No historical backtest | MC says 100%, 1966 cohort depletes | False confidence |

---

## What to Do When Uncertain

- If you're not sure about a tax rule: **state the assumption explicitly** and flag it for review by a tax professional.
- If you're not sure about an input: **ask the user**, don't default silently.
- If the model produces extreme results (MC < 50% or > 99%): **check your assumptions** before presenting. Extreme results are usually modeling errors, not financial emergencies.
- If two reasonable assumptions produce wildly different results: **show both** and explain which assumption matters more.
- If the historical backtest and Monte Carlo disagree significantly (>10pp on success rate): **investigate which assumptions cause the divergence** and explain it. Don't just present whichever number looks better.

---

## Ethical Boundaries

- This is a projection model, not financial advice. Always include a disclaimer.
- Never recommend specific investment products, funds, or financial institutions.
- Never present Monte Carlo results as guarantees. 100% MC does not mean 100% certainty.
- If the plan genuinely doesn't work (even with optimizations), say so clearly. Don't torture the model to produce a passing grade.
- If you're uncertain whether an optimization is realistic (e.g., "just cut spending 40%"), flag the human cost of the recommendation. A plan that requires misery to succeed is not a good plan.
- When comparing withdrawal strategies, don't just recommend the one with the highest final portfolio. A strategy that saves $150K in taxes but requires annual rebalancing and tax-lot tracking may not suit every client. Present tradeoffs honestly.
