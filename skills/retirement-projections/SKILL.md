---
name: enareto-financial-plan
description: >
  Build or update a retirement financial plan with cash flow projections, Monte Carlo analysis,
  tax-optimized withdrawal strategies, and historical backtesting. Use whenever the user mentions
  "financial plan", "retirement plan", "can I retire", "retirement projections", "cash flow analysis",
  "withdrawal strategy", "Monte Carlo", "retirement income", "asset allocation", or discusses
  retirement readiness. Also trigger when reviewing existing plans, running scenarios, comparing
  withdrawal strategies, or modeling retirement spending. This skill embeds hard-won modeling
  standards that prevent common errors which can swing results by 60+ percentage points.
  Always use this skill for retirement-related financial modeling.
---

# Financial Plan Skill

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

These are not suggestions. Omitting any one of these can swing Monte Carlo results by 20-60 percentage points.

**1. Social Security COLA (typically the single biggest error when omitted)**

SS benefits grow with COLA every year — including years *before* the person starts claiming. The SSA statement shows today's estimate at FRA, but by the time the person actually claims (potentially 10-15 years from now), the benefit will have compounded by COLA^years.

```
actual_benefit(year) = today_estimate × (1 + COLA)^(year - 1)
```

Use 2.5%/year as COLA default (historical average ~2.6%). This is applied from today, compounding every year, whether or not the person has started claiming.

**Why this matters:** For a couple claiming SS 12-15 years from now, COLA can increase their combined SS by 35-45% vs. the stated estimate. This is often the difference between "can't retire" and "already fine."

**2. Progressive Federal Tax Brackets (MFJ 2025)**

Never use a flat tax rate. The difference between a flat 25% and progressive brackets can be $15-30K/year in tax, compounding over decades.

```
Brackets (MFJ): $23,850 @ 10%, $73,150 @ 12%, $109,700 @ 22%,
$187,900 @ 24%, $106,450 @ 32%, $250,550 @ 35%, remainder @ 37%
```

Standard deduction MFJ: ~$30,000. Always apply it.

**3. 401(k) Contributions Reduce Taxable Income**

Pre-tax 401(k) contributions are not "savings from after-tax income." They reduce W-2 taxable income directly. For a couple maxing 401(k) with catch-up ($30,500/person for 50+), that's $61,000/year of income that never gets taxed at their marginal rate.

```
w2_taxable = gross_salary - employee_401k_contributions
```

Also model employer match as additional savings (typically 3-6% of salary), not additional taxable income to the employee in the contribution year.

**4. FICA Taxes**

- Social Security: 6.2% on wages up to $168,600 (2025 cap)
- Medicare: 1.45% on all wages
- Additional Medicare: 0.9% on wages > $250,000 (MFJ)

These stop in retirement (no FICA on withdrawals or SS income), which is a meaningful tax reduction that the model should reflect.

**5. Social Security Benefit Taxation**

SS benefits are taxed based on "combined income" (AGI + nontaxable interest + 50% of SS):
- Combined < $32,000: 0% of SS taxable
- $32,000-$44,000: up to 50% taxable
- > $44,000: up to 85% taxable

Most retirees with other income sources will have 85% of SS taxable. Model this — don't just add SS as tax-free income.

**6. Salary Growth**

Salaries are not frozen. Use 3%/year (inflation + typical merit). Over 10 pre-retirement years, this means final salary is ~34% higher than current, which means more 401(k) contributions, more savings, and higher SS benefits.

**7. Realistic Retirement Spending Curve (Obligatory vs. Discretionary)**

People do not spend a flat inflation-adjusted amount for 30 years. Research (Blanchett's "retirement spending smile", Bernicke, JP Morgan data) consistently shows spending follows three phases. But you need to model the *composition* of spending, not just the total:

**Obligatory spending** (housing, healthcare, food, utilities, insurance, debt) stays relatively constant in real terms, then shifts: mortgage may pay off (big drop), but healthcare rises with age. Model obligatory as a separate floor that only changes at known events (mortgage payoff, Medicare eligibility, LTC onset).

**Discretionary spending** (travel, dining, hobbies, gifts) is what actually follows the go-go/slow-go/no-go curve:
- **Go-go (65-74):** Peak discretionary — travel, dining, hobbies. This is the spending people actually enjoy.
- **Slow-go (75-84):** Discretionary declines 3-5%/year as activity naturally decreases.
- **No-go (85+):** Discretionary drops to minimal. Mostly obligatory + healthcare.

```
total_spending(year) = obligatory(year) + discretionary(year) + one_time_expenses(year)
```

**Why this separation matters:** It changes how guardrails work (see #8). When markets crash, you cut travel, not the mortgage payment. The spending floor should be obligatory expenses only.

**8. Dynamic Spending Guardrails (Discretionary-Aware)**

When guardrails trigger, they should only cut or boost *discretionary* spending. Obligatory spending is non-negotiable.

```
if portfolio < obligatory_expenses * 20:  # Severe stress
    discretionary = 0  # Eliminate all discretionary
elif portfolio < total_expenses * 15:     # Moderate stress
    discretionary *= 0.70                 # Cut 30% of discretionary
elif portfolio > total_expenses * 35:     # Surplus
    discretionary *= 1.20                 # Boost 20% of discretionary

spending_floor = obligatory_expenses  # Never cut below this
spending_ceiling = obligatory + max_discretionary * 1.3
```

This is more realistic than cutting total spending by 15% — because nobody cuts their mortgage payment by 15% when the market drops.

**9. One-Time Expenses**

Major one-time costs must be modeled as lump-sum withdrawals in specific years, not smoothed into annual spending. They hit the portfolio at a specific point, and if that point coincides with a market downturn, the impact is amplified by sequence-of-returns risk.

```python
one_time_expenses = [
    {"year": 3,  "amount": 50_000,  "description": "Car replacement",  "source": "taxable"},
    {"year": 5,  "amount": 180_000, "description": "Child 1 college (4 yr)", "source": "529_then_taxable"},
    {"year": 8,  "amount": 40_000,  "description": "Home renovation",  "source": "taxable"},
    {"year": 13, "amount": 160_000, "description": "Child 2 college (4 yr)", "source": "529_then_taxable"},
    {"year": 15, "amount": 50_000,  "description": "Car replacement",  "source": "taxable"},
]
```

For each one-time expense, specify the **funding source** — which account it comes from. College from 529 plans (tax-free for education), cars from taxable accounts (capital gains treatment), etc. The tax impact depends on the source.

**In Monte Carlo:** One-time expenses must appear in every simulation at the same year. They are deterministic events, not random. The portfolio state when they hit is what varies across simulations, which is exactly why they matter for risk assessment.

**10. State Income Taxes — Use Real Brackets, Not a Flat Rate**

Never use a flat "5% state tax" assumption. State taxes range from 0% (FL, TX, WA, NV, etc.) to 13.3% (California top bracket). This can swing after-tax retirement income by $15-40K/year.

Read `references/state-taxes.md` for the complete bracket structure of all 50 states + DC. Key points:
- **Always ask the user's state.** If they plan to relocate in retirement, model both states with the transition year.
- Use progressive brackets where applicable (CA, NY, NJ, OR, MN, etc.)
- Many states don't tax SS benefits — check before including SS in state taxable income
- Some states (PA, IL, MS) don't tax retirement distributions at all — huge for traditional 401(k) withdrawals
- Don't forget local/city taxes: NYC adds 3-4%, MD counties add 2-3%, many OH cities add 2.5%

**11. Capital Gains Taxes — Not Everything Is Ordinary Income**

Taxable account withdrawals are NOT taxed as ordinary income. They're subject to capital gains rates, which can be 0%, 15%, or 20% — far lower than the 22-37% ordinary rates the model may be applying.

Read `references/capital-gains-taxes.md` for complete implementation. Critical points:
- Only the *gain* portion of a taxable withdrawal is taxed, not the full amount. The cost basis is returned tax-free.
- **The 0% LTCG bracket** (up to ~$96,700 MFJ taxable income) is a major planning opportunity. Many early retirees can realize tens of thousands in capital gains completely tax-free.
- Qualified dividends in taxable accounts are also taxed at LTCG rates, not ordinary rates.
- Net Investment Income Tax (NIIT) adds 3.8% on investment income above $250K AGI (MFJ).
- Most states tax capital gains as ordinary income — the federal preferential rate is what matters.

**Why this matters for withdrawal strategies:** The correct capital gains treatment makes taxable accounts significantly cheaper to draw from than the model assumes without it. This reinforces taxable-first ordering but also creates tax-gain harvesting opportunities in the 0% bracket.

**12. Required Minimum Distributions (RMDs)**

Starting at age 73 (born 1951-1959) or 75 (born 1960+), the IRS forces annual withdrawals from traditional accounts. These are taxed as ordinary income whether or not the client needs the money.

Read `references/rmd-rules.md` for the full Uniform Lifetime Table and implementation. Critical points:
- `RMD = Prior Year-End Traditional Balance / Distribution Period`
- The distribution period shrinks each year: from 26.5 at age 73 to 12.2 at age 90 to 6.4 at age 100
- A $3M traditional balance at 73 generates ~$113K/year in forced taxable income, growing to $185K+ by 85
- RMDs stack on top of SS income, potentially pushing the client into the 24-32% bracket on income they didn't choose to take
- RMDs interact with SS taxation (push more SS into 85% taxable), IRMAA (Medicare premium surcharges), and capital gains brackets (reduce 0% LTCG room)
- **Every dollar converted to Roth before RMD age is a dollar that never generates forced distributions.** This is the quantitative argument for gap-year Roth conversions.
- Roth IRAs have NO RMDs for the original owner
- If the RMD exceeds spending needs, the excess must still be withdrawn, taxed, and can be reinvested in taxable accounts

The model must compute RMDs each year starting at the applicable age and treat them as the *minimum* traditional withdrawal. If spending needs require more than the RMD, withdraw the larger amount. If the RMD exceeds spending needs, model the excess as after-tax reinvestment into the taxable account.

### Step 3: Withdrawal Strategy Analysis

The order in which you pull from different account types (traditional, Roth, taxable) materially affects lifetime taxes paid and portfolio longevity. Do not assume a single strategy — model and compare at least three.

Read `references/withdrawal-strategies.md` for full implementation. Summary:

**Strategy 1: Conventional (Taxable → Traditional → Roth)**
The textbook approach. Depletes taxable first (lower tax rate on capital gains), then traditional (ordinary income), Roth last (tax-free). Simple but often suboptimal because it ignores bracket management.

**Strategy 2: Tax-Bracket Optimized**
Each year, compute the marginal tax rate and fill brackets optimally:
- First, compute income from SS, pensions, annuities, and any required distributions
- Then withdraw from traditional up to the top of the current bracket (e.g., fill the 12% or 22% bracket)
- Take remaining needs from Roth (tax-free) or taxable (capital gains rate)
- During low-income years, actively convert traditional to Roth to fill low brackets

This typically saves $50-200K in lifetime taxes vs. conventional ordering by keeping the client in lower brackets throughout retirement.

**Strategy 3: Proportional**
Withdraw proportionally from all account types based on their share of total portfolio. Simple, maintains tax diversification, but doesn't optimize brackets.

**Strategy 4: Roth-Bridge (for early retirees)**
If retiring before SS starts (common 2-5 year gap): draw heavily from traditional/taxable during the gap years when taxable income is very low, potentially convert to Roth simultaneously. Then switch to minimal withdrawals once SS provides income. The gap years are a tax optimization gift — don't waste them.

**How to compare:** Run the full projection with each strategy and report:
- Total lifetime taxes paid
- Final portfolio value
- Monte Carlo success rate
- Year-by-year effective tax rate (to verify bracket management is working)

Present the comparison to the user with the recommended strategy highlighted and an explanation of why it wins.

### Step 4: Asset Allocation Strategy

Do not assume a static 60/40. Read `references/allocation-strategies.md` for full implementation. Model and compare at least two approaches.

**Strategy 1: Static Allocation**
Fixed stock/bond/cash split maintained throughout. Simple, easy to implement.
- Conservative: 40/50/10
- Moderate: 60/35/5
- Aggressive: 80/15/5

**Strategy 2: Age-Based Glide Path (declining equity)**
Classic "100 minus age" or "120 minus age" for stocks. Reduces equity exposure as the person ages.
```
stock_pct = max(min(120 - age, 90), 20) / 100
bond_pct = 1 - stock_pct - 0.05  # Keep 5% cash
```
Intuitive but research shows it may not be optimal for retirees (see Strategy 3).

**Strategy 3: Rising Equity Glide Path (Kitces/Pfau research)**
Counterintuitive but mathematically sound: start retirement with *lower* equity (30-40%), then gradually *increase* to 60-70% by age 80+.

The reasoning: sequence-of-returns risk is concentrated in the first 10 years of retirement. If markets crash early, a high equity allocation devastates the portfolio when withdrawals are highest relative to portfolio size. Starting conservative and increasing equity later means:
- Less damage from early crashes (when it matters most)
- More growth exposure later (when SS covers most expenses and withdrawals are minimal)
- The portfolio has already survived the danger zone

```python
def rising_glide(years_in_retirement):
    start_equity = 0.35   # Conservative start
    end_equity = 0.65     # Growth finish
    ramp_years = 15       # Transition period
    t = min(years_in_retirement / ramp_years, 1.0)
    return start_equity + (end_equity - start_equity) * t
```

**Strategy 4: Bucket Strategy**
Divide portfolio into time-based buckets:
- **Bucket 1 (Years 1-3):** Cash/short-term bonds. Covers near-term spending. No market risk.
- **Bucket 2 (Years 4-10):** Intermediate bonds, dividend stocks. Moderate growth.
- **Bucket 3 (Years 11+):** Growth equities. Long time horizon, maximum growth.

Refill Bucket 1 from Bucket 2 annually; refill Bucket 2 from Bucket 3 when markets are up. Skip refill when markets are down (let Bucket 1 absorb the shock).

This is psychologically appealing because the client can see 3 years of cash and never panics. Mathematically similar to a rising glide path with dynamic rebalancing.

**How to compare:** Run Monte Carlo with each strategy on the same client data. Report success rate, median final portfolio, and worst-case (10th percentile). The right strategy depends on the client — a nervous client benefits from buckets; an analytical client may prefer bracket-optimized rising glide path.

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

**2. Excel Workbook (Cash Flow Projections)**
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
