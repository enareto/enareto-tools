# Asset Allocation Strategy Reference

## Why This Matters

Asset allocation is the single largest determinant of long-term portfolio volatility and return. The difference between 40% stocks and 80% stocks over 30 years can mean a $3-5M difference in final portfolio — but also the difference between sleeping at night and panic-selling in a crash.

The right strategy depends on the client's income structure, not just their "risk tolerance questionnaire" score.

## Key Insight: Allocation Should Match Income Structure

A retiree with $200K/year in SS + pension income and $180K/year in spending has a *very different* risk profile than a retiree with $0 guaranteed income and $180K spending.

The first retiree's portfolio is surplus money — they don't need it for decades. They can tolerate 80% stocks because a 40% crash doesn't affect their lifestyle at all. The second retiree depends on the portfolio for daily expenses. A 40% crash means they're selling stocks at the worst time.

**Rule:** The more guaranteed income covers spending, the more aggressive the portfolio can be.

```python
def suggested_equity_range(guaranteed_income, total_expenses):
    coverage = guaranteed_income / total_expenses
    if coverage >= 1.0:    return (0.70, 0.90)  # Portfolio is surplus
    elif coverage >= 0.60: return (0.50, 0.70)  # Moderate reliance on portfolio
    elif coverage >= 0.30: return (0.40, 0.60)  # Heavy reliance
    else:                  return (0.30, 0.50)  # Portfolio is lifeline
```

This coverage ratio changes over time as SS COLA grows and spending declines. The allocation strategy should adapt.

## Strategy Implementations

### Strategy 1: Static Allocation

Fixed allocation, rebalanced annually.

```python
def static_allocation(stock_pct=0.60, bond_pct=0.35, cash_pct=0.05):
    """Returns allocation for any year."""
    return stock_pct, bond_pct, cash_pct
```

**Common presets:**
| Name | Stocks | Bonds | Cash | Expected Return | Volatility |
|------|--------|-------|------|----------------|-----------|
| Conservative | 30% | 55% | 15% | 3.95% | 6.2% |
| Moderate-Conservative | 40% | 50% | 10% | 4.50% | 7.8% |
| Moderate | 50% | 40% | 10% | 5.10% | 9.4% |
| Moderate-Growth | 60% | 35% | 5% | 5.70% | 11.0% |
| Growth | 70% | 25% | 5% | 6.25% | 12.6% |
| Aggressive | 80% | 15% | 5% | 6.80% | 14.2% |

**Pros:** Simple, easy to implement, well-understood.
**Cons:** Doesn't adapt to changing risk profile over retirement.

### Strategy 2: Age-Based Glide Path (Declining Equity)

Traditional approach: reduce stocks as you age.

```python
def age_based_glide(age, base_rule=120):
    """
    base_rule: '100 minus age' or '120 minus age' for stock %.
    120 is more aggressive and generally recommended for modern longevity.
    """
    stock_pct = max(min(base_rule - age, 90), 20) / 100
    cash_pct = 0.05
    bond_pct = 1.0 - stock_pct - cash_pct
    return stock_pct, bond_pct, cash_pct
```

**Example trajectory:**
| Age | Stocks | Bonds | Cash |
|-----|--------|-------|------|
| 55 | 65% | 30% | 5% |
| 65 | 55% | 40% | 5% |
| 75 | 45% | 50% | 5% |
| 85 | 35% | 60% | 5% |
| 95 | 25% | 70% | 5% |

**Pros:** Intuitive. Reduces volatility as time horizon shrinks.
**Cons:** Kitces/Pfau research shows this may be suboptimal for retirees — it has the most equity when sequence-of-returns risk is highest (early retirement) and the least when the portfolio is most insulated (late retirement when SS covers spending).

### Strategy 3: Rising Equity Glide Path (Kitces/Pfau)

Start conservative, gradually increase equity. Based on research by Michael Kitces and Wade Pfau showing that for retirees, sequence-of-returns risk is front-loaded.

```python
def rising_glide(years_in_retirement,
                 start_equity=0.30,    # Conservative start
                 end_equity=0.70,      # Growth finish
                 ramp_years=15,        # Transition period
                 min_equity=0.25,
                 max_equity=0.80):
    """
    Linearly increase equity from start to end over ramp_years.
    After ramp, hold at end_equity.
    """
    t = min(years_in_retirement / ramp_years, 1.0)
    stock_pct = start_equity + (end_equity - start_equity) * t
    stock_pct = max(min(stock_pct, max_equity), min_equity)
    cash_pct = 0.05
    bond_pct = 1.0 - stock_pct - cash_pct
    return stock_pct, bond_pct, cash_pct
```

**Example trajectory:**
| Years Retired | Age (if 65 start) | Stocks | Bonds | Cash |
|--------------|-------------------|--------|-------|------|
| 0 | 65 | 30% | 65% | 5% |
| 5 | 70 | 43% | 52% | 5% |
| 10 | 75 | 57% | 38% | 5% |
| 15 | 80 | 70% | 25% | 5% |
| 20 | 85 | 70% | 25% | 5% |

**Why this works:**
1. In early retirement, withdrawals are large relative to portfolio. A crash hurts badly. Low equity protects.
2. By year 15, SS COLA has grown to cover most spending. Withdrawals are tiny or zero. The portfolio can absorb volatility.
3. Higher equity in later years generates more growth exactly when the portfolio is "house money."

**Research basis:** Kitces & Pfau (2014), "Reducing Retirement Risk with a Rising Equity Glide Path." In their analysis, a 30→70% rising path improved worst-case outcomes by 10-15% vs. the traditional declining path, and improved median outcomes by 20-30%.

**Cons:** Counterintuitive — clients may resist "more stocks as I get older." Requires explanation.

### Strategy 4: Bucket Strategy

Divide portfolio into time-horizon buckets.

```python
def bucket_allocation(portfolio, years_in_retirement,
                      bucket1_years=3, bucket2_years=7):
    """
    Bucket 1: Cash/short bonds. Near-term spending.
    Bucket 2: Intermediate bonds + div stocks. Medium-term.
    Bucket 3: Growth equities. Long-term.
    """
    annual_spending = estimate_annual_spending(years_in_retirement)

    bucket1_target = annual_spending * bucket1_years
    bucket2_target = annual_spending * bucket2_years
    bucket3_target = portfolio - bucket1_target - bucket2_target

    return {
        'bucket1': {'target': max(bucket1_target, 0),
                    'allocation': (0.0, 0.30, 0.70)},  # stocks, bonds, cash
        'bucket2': {'target': max(bucket2_target, 0),
                    'allocation': (0.30, 0.60, 0.10)},
        'bucket3': {'target': max(bucket3_target, 0),
                    'allocation': (0.90, 0.10, 0.0)},
    }
```

**Refill rules:**
- At year-end, refill Bucket 1 from Bucket 2 (always — even in down years, there's enough for 3 years)
- Refill Bucket 2 from Bucket 3 only when Bucket 3 is above target (don't sell stocks in a crash)
- If Bucket 3 is below target, let it recover; Bucket 1+2 have 10 years of buffer

**Effective portfolio allocation** (when fully funded):
- At inception: ~45% stocks, 40% bonds, 15% cash — conservative
- After 10 years (Bucket 1+2 drawn down, Bucket 3 has grown): effectively 60-70% stocks

**Pros:** Psychologically powerful — "you have 3 years of cash, don't panic." Natural implementation of sequence-of-returns protection. Easy to explain to clients.
**Cons:** Tax-inefficient if implemented across multiple accounts. Refill decisions add complexity. Mathematically, it's approximately equivalent to a rising glide path with less precision.

## Comparison Framework

Run each strategy through Monte Carlo and historical backtest with identical client parameters:

| Metric | Static 60/40 | Age-Based | Rising Glide | Bucket |
|--------|-------------|-----------|--------------|--------|
| MC success rate | | | | |
| Median final portfolio | | | | |
| 10th percentile final | | | | |
| Worst historical cohort result | | | | |
| Max drawdown (worst MC sim) | | | | |
| Avg equity exposure over plan | | | | |

For the client report, recommend one strategy with rationale, but show the comparison so the client (or their advisor) can make an informed decision.
