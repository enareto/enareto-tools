# Validation Checklist

Run these checks **before presenting any results to the user**. If any check fails, fix the model first. Do not present results with a caveat that you know the model is wrong.

## Automated Validation

Run the validation script and the historical backtest:

```bash
python scripts/validate_model.py projections.json [retirement_year]
python scripts/historical_backtest.py projections.json [retirement_year] [plan_horizon]
```

## Critical Checks (must pass)

### 1. Effective Tax Rate Sanity
| Household Income | Expected Effective Rate (Fed + State + FICA) |
|-----------------|----------------------------------------------|
| $200-300K | 20-28% |
| $300-400K | 24-30% |
| $400-600K | 27-33% |
| $100-150K (retirement) | 12-20% |
| $50-80K (Roth conversion year) | 8-14% |

If your model shows rates outside these ranges, check: Are you applying standard deduction? Are 401(k) contributions deducted from taxable income? Are you double-counting FICA in retirement?

### 2. SS COLA Verification
Compare SS at claiming year to today's stated estimate:
- 10 years from now: should be ~28% higher (1.025^10 = 1.28)
- 12 years from now: should be ~34% higher (1.025^12 = 1.34)
- 15 years from now: should be ~45% higher (1.025^15 = 1.45)

If SS at claiming equals today's estimate, COLA is missing.

### 3. Portfolio Growth During Accumulation
With $400K+ combined salary, max 401(k) contributions, and 3% salary growth:
- Portfolio should roughly double over 10 years
- 401(k) contributions alone add ~$700-800K over 10 years (with employer match)
- Investment returns add another $800K-1.2M on a $2M starting portfolio

If the portfolio at retirement is less than 2x the starting portfolio, check that contributions are actually being added each year.

### 4. Late-Life Income vs. Spending
By age 85+:
- SS with COLA should cover 80-120%+ of realistic spending
- Required portfolio withdrawals should be near 0%
- Portfolio should be growing (returns exceed withdrawals)

If the model shows 5%+ withdrawal rates at age 90, either spending is unrealistically high for that age or SS COLA is missing.

### 5. Withdrawal Strategy Comparison
If you've run multiple withdrawal strategies:
- They should produce different lifetime tax totals (typically $50-200K spread)
- If all strategies give identical results, account types aren't being differentiated in the tax calculation
- The bracket-optimized strategy should show lower effective rates in early retirement

### 6. Obligatory Spending Floor
- Spending should never drop below obligatory expenses under any guardrail scenario
- If dynamic guardrails can cut below the mortgage + healthcare + food level, the guardrail floor is set wrong
- Check: minimum spending across all MC simulations ≥ stated obligatory expenses

### 7. One-Time Expense Impact
If one-time expenses were specified:
- The portfolio should show a visible dip in the year of each major expense
- A $200K college expense should reduce the portfolio by $200K+ (plus tax on withdrawal) in that year
- If the projection looks smooth through a year with $200K in college costs, the expenses aren't being modeled

### 8. Historical Backtest vs. Monte Carlo Consistency
Run the backtest and compare:
- If MC says 100% but backtest shows failures in 1966 or 1929 cohorts, investigate
- If they disagree by >10 percentage points, the MC return distribution may not capture real-world regimes
- Acceptable: backtest within ±5pp of MC, or backtest is slightly more conservative (it has serial correlation MC doesn't)

### 9. Allocation Strategy Verification
If testing multiple allocation strategies:
- Rising glide path should outperform static in worst-case scenarios (it protects early)
- Static aggressive (80% equity) should have higher median but worse 10th percentile
- Bucket strategy should show lower volatility in first 10 years
- If all strategies give identical MC results, the allocation isn't actually changing returns

### 10. State Tax Verification
- Confirm the user's state is identified and the correct bracket structure is used
- No-tax states (FL, TX, NV, WA, WY, SD, AK, TN, NH) must show $0 state tax
- Flat-tax states must use the correct flat rate (not a guess)
- Progressive states must use real brackets from `state-taxes.md`
- If the model shows state tax in a no-tax state, or shows 5% flat for California, it's wrong
- Check that SS exemptions at the state level are applied (most states don't tax SS)
- Verify retirement income exclusions (e.g., GA $65K/person for 62+)

### 11. Capital Gains Tax Differentiation
- Taxable account withdrawals must NOT be taxed at ordinary income rates
- Only the **gain portion** (above cost basis) is taxable
- Gains must use LTCG rates (0%/15%/20%), not ordinary brackets
- Check: in early retirement with low ordinary income, taxable withdrawals should show near-0% effective rate on gains
- If a $100K taxable withdrawal (50% basis) shows $12K+ tax, ordinary rates are being applied incorrectly
- NIIT (3.8%) should only appear when AGI > $250K MFJ
- Qualified dividends from taxable accounts should use LTCG rates, not ordinary rates

### 12. RMD Enforcement
- RMDs must start at age 73 (born 1951-1959) or 75 (born 1960+)
- Traditional withdrawals must be ≥ RMD in every year after the start age
- If the model shows $0 traditional withdrawal at age 80 with a $2M+ traditional balance, RMDs are missing
- RMD amounts should increase as a % of balance each year (divisor shrinks)
- At age 73: ~3.8% of balance; at age 85: ~6.3%; at age 95: ~11.2%
- Excess RMDs (above spending need) should be reinvested in taxable after tax
- Roth conversions done before RMD age should be reducing the traditional balance subject to RMDs

## Warning Signs

These don't necessarily mean the model is wrong, but investigate:

- **MC success rate below 50% for a high-income couple with substantial savings:** Usually a modeling error, not a real problem.
- **Portfolio growing indefinitely:** Check that spending is realistic and tax-adjusted.
- **Withdrawal rate spikes above 10%:** Usually means income sources are missing or spending is too high.
- **Effective tax rate identical across all years:** Progressive brackets or income changes aren't being modeled.
- **SS income constant after claiming:** COLA should make it grow every year.
- **Same spending at age 66 and age 92:** Realistic spending curve is missing.
- **One-time expenses not showing in projection:** Check they're in the right year.
- **All withdrawal strategies produce identical after-tax income:** Tax differentiation is broken.
- **1966 backtest cohort survives easily:** Double-check you're using real returns (1966-1982 was brutal).
- **State tax = 5% for every state:** Real brackets are required. A California couple at $400K pays ~9%, not 5%.
- **Taxable withdrawal taxed same as traditional withdrawal:** Capital gains rates apply to gains only.
- **No RMDs appearing after age 73/75:** Forced distributions are mandatory, not optional.
- **Traditional balance stays constant after age 75:** RMDs should be drawing it down.
- **Capital gains rate of 15% on first dollar of gains:** Check if 0% bracket room exists first.

## After Validation

Once all checks pass:
1. Run Monte Carlo (2,000+ simulations, multiple scenarios)
2. Run historical backtest (all starting years)
3. Compare withdrawal strategies (lifetime tax table)
4. Compare allocation strategies (MC + backtest for each)
5. Generate deliverables (Word + Excel)
6. Include assumptions sheet with every input stated explicitly
