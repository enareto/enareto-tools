# Financial Modeling Standards — Technical Reference

This document contains the exact formulas and implementation patterns for retirement financial models. Everything here was derived from real modeling failures that produced materially wrong results.

## Table of Contents
1. Social Security with COLA
2. Federal Tax Calculation (Progressive, MFJ)
3. FICA Taxes
4. Social Security Benefit Taxation
5. 401(k) and Retirement Contributions
6. Realistic Spending Curve
7. Dynamic Spending Guardrails
8. Roth Conversion Strategy
9. Monte Carlo Simulation
10. Withdrawal Sequencing
11. Annuity Modeling (SPIA)
12. State Income Tax Calculation
13. Capital Gains Tax (Taxable Account Withdrawals)
14. Required Minimum Distributions (RMDs)

---

## 1. Social Security with COLA

**The most commonly omitted factor, and often the single largest source of error.**

Social Security benefits receive annual Cost-of-Living Adjustments (COLA). These apply:
- Every year from today, even before the person starts claiming
- Every year after claiming begins
- To both spouses independently

The SSA statement shows an estimate in today's dollars at Full Retirement Age (FRA). By the time a 55-year-old claims at 67 (12 years later), the actual benefit will be:

```python
def ss_benefit(base_today, start_year, current_year, cola=0.025):
    """
    base_today: SSA's current FRA estimate (today's dollars)
    start_year: year number when claiming begins (relative to model start)
    current_year: year number being calculated
    cola: annual COLA rate (default 2.5%, historical avg ~2.6%)
    """
    if current_year < start_year:
        return 0
    # COLA compounds every year from model start, including pre-claiming years
    return base_today * (1 + cola) ** (current_year - 1)
```

**Example:** George's FRA estimate today = $48,420. He claims at year 13 (age 67).
- Without COLA: $48,420 at year 13
- With COLA at 2.5%: $48,420 × 1.025^12 = **$65,120** at year 13
- At year 30 (age 84): $48,420 × 1.025^29 = **$99,143**

For a couple, combined SS at year 30 can easily exceed $200,000 — typically more than late-life spending.

**Default COLA:** 2.5%/year. Range for sensitivity: 2.0-3.0%.

---

## 2. Federal Tax Calculation (Progressive, MFJ 2025)

Never use a flat effective tax rate. Always compute progressive brackets.

```python
def federal_tax_mfj(taxable_income):
    """2025 MFJ brackets. Update annually."""
    brackets = [
        (23_850, 0.10),
        (73_150, 0.12),
        (109_700, 0.22),
        (187_900, 0.24),
        (106_450, 0.32),
        (250_550, 0.35),
        (float('inf'), 0.37),
    ]
    tax = 0
    remaining = max(taxable_income, 0)
    for bracket_size, rate in brackets:
        if remaining <= 0:
            break
        taxable_in_bracket = min(remaining, bracket_size)
        tax += taxable_in_bracket * rate
        remaining -= taxable_in_bracket
    return tax
```

**Standard deduction (MFJ 2025):** ~$30,000. Always subtract before computing tax.

**State tax:** Ask for the user's state. Look up the correct brackets in `references/state-taxes.md`. Never use a flat rate as placeholder.

---

## 3. FICA Taxes

Only applies to W-2 wages (stops at retirement):

```python
def fica_tax(w2_wages):
    ss_tax = min(w2_wages, 168_600) * 0.062  # SS cap for 2025
    medicare = w2_wages * 0.0145
    additional_medicare = max(w2_wages - 250_000, 0) * 0.009  # MFJ threshold
    return ss_tax + medicare + additional_medicare
```

**In retirement:** FICA = 0 on all distributions, SS income, and annuity income. This means the effective tax rate drops meaningfully at retirement even at the same income level.

---

## 4. Social Security Benefit Taxation

SS benefits are partially taxable based on "combined income":

```python
def ss_taxable_fraction(other_income, ss_income):
    """
    other_income: AGI excluding SS (W-2 + trad withdrawals + Roth conversions + taxable annuity)
    ss_income: total SS benefits received
    Returns: fraction of SS that is taxable (0, 0.50, or 0.85)
    """
    combined = other_income + ss_income * 0.5
    if combined > 44_000:
        return 0.85
    elif combined > 32_000:
        return 0.50
    else:
        return 0.0
```

Most retirees with meaningful other income will be at 85%. During Roth conversion gap years (low other income), this fraction may drop — which is an additional benefit of the conversion strategy.

---

## 5. 401(k) and Retirement Contributions

**Pre-tax 401(k) reduces W-2 taxable income:**

```python
# 2025 limits
MAX_401K_CONTRIBUTION = 23_500  # Under age 50
MAX_401K_CATCHUP = 30_500       # Age 50+ (includes extra catch-up)

employee_contrib = MAX_401K_CATCHUP  # per person, if 50+
employer_match = gross_salary * match_pct  # typically 3-6%

w2_taxable = gross_salary - employee_contrib  # This is the key line
total_annual_savings = (employee_contrib + employer_match) * num_workers
```

**Common error:** Treating 401(k) contributions as post-tax savings. This overtaxes by $15-20K/year for a high-income couple, compounding to $200-400K of missing portfolio at retirement.

---

## 6. Realistic Spending Curve

**Do not use flat inflation-adjusted spending.** Use the go-go/slow-go/no-go framework:

```python
def realistic_spending(year, retiree_age, retirement_year,
                       go_go_base=260_000,    # Starting annual spend in retirement
                       go_go_growth=0.02,      # Annual growth during go-go
                       slow_go_decline=0.02,   # Average annual decline during slow-go
                       no_go_floor=160_000,    # Minimum spending floor
                       pre_retire_expense=300_000,
                       pre_retire_inflation=0.03):
    """
    Spending phases based on retirement research:
    - Go-go (65-74): Active years, peak spending
    - Slow-go (75-84): Gradual decline in activity
    - No-go (85+): Healthcare + basics, floor spending
    """
    if year < retirement_year:
        return pre_retire_expense * (1 + pre_retire_inflation) ** (year - 1)

    if retiree_age <= 69:
        return go_go_base * (1 + go_go_growth) ** (retiree_age - 65)
    elif retiree_age <= 74:
        peak = go_go_base * (1 + go_go_growth) ** 4
        return peak * (0.99 ** (retiree_age - 69))  # Slight decline
    elif retiree_age <= 79:
        v74 = go_go_base * (1 + go_go_growth) ** 4 * (0.99 ** 5)
        return v74 * (0.97 ** (retiree_age - 74))  # Moderate decline
    elif retiree_age <= 84:
        v79 = go_go_base * (1 + go_go_growth) ** 4 * (0.99 ** 5) * (0.97 ** 5)
        return v79 * (0.96 ** (retiree_age - 79))  # Steeper decline
    else:
        v84 = (go_go_base * (1 + go_go_growth) ** 4 *
               (0.99 ** 5) * (0.97 ** 5) * (0.96 ** 5))
        return max(v84 * (0.97 ** (retiree_age - 84)), no_go_floor)
```

**Go-go base calibration:** Typically 80-90% of pre-retirement household spending. Two people now have more time for discretionary spending, but some work-related costs disappear.

**No-go floor:** Primarily healthcare, housing, food, utilities. Typically $120K-$180K depending on location and housing situation.

---

## 7. Dynamic Spending Guardrails

Real people adjust spending when markets move. Model this:

```python
def apply_guardrails(base_expense, portfolio_value,
                     cut_threshold=15,     # Cut if portfolio < Nx expenses
                     boost_threshold=35,   # Boost if portfolio > Nx expenses
                     cut_pct=0.15,         # How much to cut
                     boost_pct=0.15,       # How much to boost
                     floor=150_000,        # Absolute minimum
                     ceiling=300_000):     # Absolute maximum
    if portfolio_value < base_expense * cut_threshold:
        return max(base_expense * (1 - cut_pct), floor)
    elif portfolio_value > base_expense * boost_threshold:
        return min(base_expense * (1 + boost_pct), ceiling)
    return base_expense
```

This typically adds 10-20 percentage points to Monte Carlo success without requiring a lower base spending level.

---

## 8. Roth Conversion Strategy

During gap years between retirement and SS, taxable income drops sharply. Use this window:

```python
def roth_conversion_amount(year, traditional_balance, other_taxable_income,
                           target_bracket_top=127_000,  # Top of 12% bracket + std deduction
                           max_pct_of_trad=0.05):
    """Convert enough to fill the 12% bracket without going higher."""
    room = max(target_bracket_top - other_taxable_income, 0)
    max_convert = traditional_balance * max_pct_of_trad
    return min(room, max_convert)
```

**Window:** Typically retirement year through ~2 years after last SS starts.
**Target:** Top of 12% bracket for MFJ (~$95,000-$127,000 taxable income).
**Cap:** 5% of traditional balance/year to avoid bracket creep.

---

## 9. Monte Carlo Simulation

```python
import random

def monte_carlo(params, num_sims=2000, seed=42):
    """
    Run MC simulation with stochastic returns.
    Returns: success_rate, median_final, percentiles.
    """
    random.seed(seed)
    RETURN_PARAMS = {
        'stocks': (0.07, 0.16),   # mean, vol
        'bonds':  (0.04, 0.06),
        'cash':   (0.02, 0.01),
    }

    finals = []
    successes = 0

    for _ in range(num_sims):
        portfolio = params['starting_portfolio']
        failed = False

        for year in range(1, params['total_years'] + 1):
            # Stochastic returns
            stock_r = random.gauss(*RETURN_PARAMS['stocks'])
            bond_r = random.gauss(*RETURN_PARAMS['bonds'])
            cash_r = random.gauss(*RETURN_PARAMS['cash'])
            blended = (params['stock_pct'] * stock_r +
                       params['bond_pct'] * bond_r +
                       params['cash_pct'] * cash_r)

            # ... compute income, expenses, taxes, withdrawals ...
            # ... apply dynamic guardrails ...

            portfolio = portfolio * (1 + blended) + net_savings - net_withdrawals

            if portfolio <= 0:
                guaranteed = ss_income + annuity_income
                if guaranteed >= expenses * 0.6:
                    portfolio = 0  # Depleted but survivable on guaranteed income
                    continue
                failed = True
                break

        if not failed:
            successes += 1
        finals.append(max(portfolio, 0))

    finals.sort()
    n = num_sims
    return {
        'success_rate': successes / n * 100,
        'median': finals[n // 2],
        'pct_10': finals[int(n * 0.10)],
        'pct_25': finals[int(n * 0.25)],
        'pct_75': finals[int(n * 0.75)],
        'pct_90': finals[int(n * 0.90)],
    }
```

**Minimum simulations:** 2,000.
**Success definition:** Portfolio never hits zero, OR guaranteed income covers 60%+ of expenses at depletion.
**Always report:** Success rate, median, 10th and 25th percentile final portfolio.

---

## 10. Withdrawal Sequencing

Order of withdrawals in retirement:

1. **Taxable accounts first** — lowest tax cost (capital gains rates, basis recovery)
2. **Traditional (pre-tax) accounts** — taxed as ordinary income, manage RMDs
3. **Roth accounts last** — tax-free growth, no RMDs, best for late-life and estate

During Roth conversion years, the traditional account gets drawn down by conversions (not withdrawals), and spending is funded from taxable + some traditional.

After SS starts, if SS covers most expenses, minimize traditional withdrawals (just enough for RMDs) and let the portfolio compound.

---

## 11. Annuity Modeling (SPIA)

Single Premium Immediate Annuity, joint-life with 100% survivor benefit:

```python
def annuity_income(premium, payout_rate=0.055, taxable_pct=0.75):
    """
    premium: lump sum used to purchase annuity (from traditional or taxable)
    payout_rate: annual payout as % of premium (5-6% typical for mid-60s couple)
    taxable_pct: portion taxable as ordinary income (exclusion ratio)
    """
    gross_income = premium * payout_rate
    taxable_income = gross_income * taxable_pct
    return gross_income, taxable_income
```

**When to recommend:** Only if the plan needs additional guaranteed income floor and SS + pension don't provide it. If SS with COLA already exceeds late-life spending, the annuity is optional insurance, not a necessity. State this clearly.

**Premium source:** Usually from traditional balance at retirement. This reduces the investment portfolio but creates guaranteed income.

**Sensitivity:** Test at 0, $250K, $500K, $750K premium levels and show the tradeoff.

---

## 12. State Income Tax Calculation

Never use a flat "5% state tax" estimate. Look up the user's state in `references/state-taxes.md` and apply the correct structure.

```python
def state_tax(state, taxable_income, filing='mfj'):
    """
    Calculate state income tax using real brackets.
    See references/state-taxes.md for full bracket tables.

    Categories:
    - No-tax states (FL, TX, NV, WA, WY, SD, AK, TN, NH): return 0
    - Flat-tax states (AZ, CO, GA, ID, IL, IN, KY, MI, MS, NC, OK, PA, UT):
      rate × (taxable_income - state_deduction)
    - Progressive states (CA, NY, NJ, etc.): apply state brackets
    """
    NO_TAX = {'FL','TX','NV','WA','WY','SD','AK','TN','NH'}
    if state in NO_TAX:
        return 0

    # Example: California (progressive, 9 brackets)
    # brackets = [(22_106, 0.01), (30_260, 0.02), (22_232, 0.04), ...]
    # Apply same progressive logic as federal_tax_mfj()

    # Always check state-taxes.md for:
    # 1. Correct bracket amounts for the filing status
    # 2. State standard deduction (differs from federal)
    # 3. Whether SS is taxed at state level
    # 4. Any retirement income exclusions
    # 5. Local/city taxes (NYC, Portland, etc.)
    pass
```

**Key interactions:**
- Some states don't tax SS at all (most don't). Check the state-taxes.md reference.
- Some states exempt retirement income up to a threshold (e.g., GA: $65K/person for 62+)
- State tax changes the Roth conversion math — converting in a no-tax state is cheaper
- SALT deduction cap ($10,000 MFJ) limits federal deductibility of state taxes

**For the model:** State taxes are added to federal + FICA for total tax liability. They do NOT reduce federal AGI (except through the limited SALT deduction).

---

## 13. Capital Gains Tax (Taxable Account Withdrawals)

Taxable account withdrawals are NOT ordinary income. Only the **gain** is taxed, and at preferential rates.

```python
def capital_gains_tax_on_withdrawal(withdrawal, cost_basis_pct,
                                      ordinary_taxable_income, filing='mfj'):
    """
    withdrawal: total amount sold from taxable account
    cost_basis_pct: fraction that is original contributions (not taxable)
    ordinary_taxable_income: other taxable income (SS taxable + trad withdrawals)
        AFTER standard deduction
    """
    basis_return = withdrawal * cost_basis_pct  # Tax-free
    gains = withdrawal * (1 - cost_basis_pct)    # Subject to LTCG rates

    # LTCG brackets (2025 MFJ)
    brackets = [
        (96_700, 0.00),     # 0% up to this total taxable income
        (553_850, 0.15),    # 15%
        (float('inf'), 0.20),  # 20%
    ]

    # Gains stack ON TOP of ordinary income
    tax = 0
    remaining = gains
    cumulative = ordinary_taxable_income

    for bracket_top, rate in brackets:
        if remaining <= 0:
            break
        room = max(bracket_top - cumulative, 0)
        in_bracket = min(remaining, room)
        tax += in_bracket * rate
        remaining -= in_bracket
        cumulative += in_bracket

    # NIIT: 3.8% surtax if AGI > $250K MFJ
    agi = ordinary_taxable_income + gains + basis_return  # approximate
    niit_excess = max(agi - 250_000, 0)
    niit = min(niit_excess, gains) * 0.038

    return tax + niit
```

**Cost basis estimation** (if user doesn't know exact basis):

| Account Age | Typical Basis % |
|-------------|----------------|
| < 3 years | 80-95% |
| 3-10 years | 60-80% |
| 10-20 years | 40-60% |
| 20+ years | 25-40% |

**0% bracket opportunity:** A couple with ~$21K ordinary taxable income after deductions has $75K+ of room in the 0% LTCG bracket. Use this for tax-gain harvesting in early retirement.

**Qualified dividends:** Taxable accounts generate ongoing dividend income (1.5-2% yield) taxed at LTCG rates. Model as annual tax drag:

```python
annual_dividend_tax = taxable_balance * 0.018 * ltcg_rate_at_income_level
```

**Impact on withdrawal ordering:** Taxable withdrawals are cheaper than the old model assumed. This reinforces taxable-first but for the right reason — effective tax rate on a $100K taxable withdrawal (50% gain) can be 0-7.5%, vs 12-22% on a traditional withdrawal.

---

## 14. Required Minimum Distributions (RMDs)

Traditional IRA/401(k) owners must take minimum withdrawals starting at age 73 (born 1951-1959) or 75 (born 1960+). These are taxed as ordinary income whether needed or not.

```python
# Uniform Lifetime Table (IRS Table III) — SECURE Act 2.0
RMD_TABLE = {
    72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9,
    78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7,
    84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9,
    90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9,
    96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4,
}

def calculate_rmd(age, prior_year_end_trad_balance, birth_year):
    """
    age: owner's age as of Dec 31 of distribution year
    prior_year_end_trad_balance: combined traditional IRA+401(k) Dec 31 prior year
    birth_year: to determine RMD start age (73 vs 75)
    """
    rmd_start = 75 if birth_year >= 1960 else 73
    if age < rmd_start:
        return 0
    period = RMD_TABLE.get(age, 2.0)
    return prior_year_end_trad_balance / period
```

**In the year-by-year projection:**

```python
def compute_year_withdrawal(age, trad_balance, spending_need, birth_year, ...):
    rmd = calculate_rmd(age, trad_balance, birth_year)

    # Traditional withdrawal is at LEAST the RMD
    trad_withdrawal = max(rmd, spending_need_from_trad)

    # If RMD exceeds spending need, excess gets reinvested in taxable (after tax)
    excess_rmd = max(rmd - spending_need_from_trad, 0)
    after_tax_excess = excess_rmd * (1 - marginal_rate)
    taxable_balance += after_tax_excess

    # Full RMD is taxed as ordinary income regardless
    ordinary_income += trad_withdrawal
```

**Key interactions:**
- RMDs count toward SS taxation thresholds (push SS to 85% taxable)
- RMDs count toward NIIT threshold ($250K AGI)
- RMDs count toward IRMAA Medicare surcharges (not modeled but noted)
- Roth conversions before RMD age reduce future RMDs dollar-for-dollar
- Roth IRAs have NO RMDs (another reason to convert)
- Excess RMDs shift money from traditional to taxable over time
- Penalty for missing RMDs: 25% excise tax (model must always enforce minimum)

**Example impact ($3M traditional at 73, 5% growth):**
RMDs start at $113K/yr and grow to $211K by age 90. Combined with SS, this can push a couple from 22% to 32% marginal bracket on income they didn't choose to take.
