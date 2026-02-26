# Withdrawal Strategy Reference

## Why This Matters

The order in which you withdraw from different account types can save or cost $50-200K+ in lifetime taxes. A $2M traditional IRA withdrawn at 24% marginal rate costs $480K in taxes. The same $2M withdrawn strategically — filling the 10% and 12% brackets each year, converting during gap years — might cost $250K. That $230K difference compounds.

## Account Types and Their Tax Treatment

| Account | Contribution | Growth | Withdrawal |
|---------|-------------|--------|-----------|
| Traditional 401(k)/IRA | Pre-tax (reduces current income) | Tax-deferred | Ordinary income |
| Roth 401(k)/IRA | After-tax | Tax-free | Tax-free (if qualified) |
| Taxable brokerage | After-tax | Taxed annually (dividends, realized gains) | Capital gains rate on appreciation; basis returned tax-free |
| Cash/savings | After-tax | Taxed as interest income | No additional tax |

## Strategy Implementations

### Strategy 1: Conventional (Taxable → Traditional → Roth)

```python
def conventional_withdrawal(need, taxable_bal, trad_bal, roth_bal, cap_gains_rate=0.15):
    """Simple ordering: taxable first, then traditional, Roth last."""
    tax_wd = min(need, taxable_bal)
    # Assume 50% of taxable withdrawal is gain, taxed at cap gains rate
    tax_cost_taxable = tax_wd * 0.5 * cap_gains_rate
    remaining = need - tax_wd + tax_cost_taxable

    trad_wd = 0
    if remaining > 0:
        # Need to gross up for taxes (withdrawn at ordinary income rate)
        trad_wd = min(remaining / 0.75, trad_bal)  # ~25% effective on trad
        remaining -= trad_wd * 0.75

    roth_wd = 0
    if remaining > 0:
        roth_wd = min(remaining, roth_bal)

    return tax_wd, trad_wd, roth_wd
```

**Pros:** Simple, widely understood, depletes taxable (with ongoing tax drag) first.
**Cons:** Can push traditional withdrawals into high brackets in later years when RMDs force large distributions. Misses bracket-filling opportunities.

### Strategy 2: Tax-Bracket Optimized

The key insight: in any given year, you know the client's marginal tax bracket based on their other income (SS, pension, annuity). You should fill cheap tax space with traditional withdrawals and cover the rest from Roth/taxable.

```python
def bracket_optimized_withdrawal(need, other_income, ss_income,
                                  taxable_bal, trad_bal, roth_bal,
                                  target_bracket_top=127_000):
    """
    Fill the target bracket with traditional withdrawals, take rest from Roth/taxable.
    target_bracket_top: top of the bracket you're willing to fill (e.g., 12% bracket + std deduction)
    """
    # How much room in the target bracket?
    ss_taxable_frac = 0.85 if other_income + ss_income * 0.5 > 44_000 else 0.50
    current_taxable_income = other_income + ss_income * ss_taxable_frac
    bracket_room = max(target_bracket_top - current_taxable_income, 0)

    # Fill bracket with traditional withdrawal
    trad_wd = min(bracket_room, trad_bal)
    trad_after_tax = trad_wd * (1 - marginal_rate_at(current_taxable_income + trad_wd))

    remaining = need - trad_after_tax

    # Take rest from Roth (tax-free) or taxable (cap gains)
    roth_wd = 0
    tax_wd = 0
    if remaining > 0:
        # Prefer taxable if in low cap gains bracket (0% if taxable income < ~$89K MFJ)
        if current_taxable_income + trad_wd < 89_000:
            tax_wd = min(remaining, taxable_bal)  # 0% cap gains!
            remaining -= tax_wd
        if remaining > 0:
            roth_wd = min(remaining, roth_bal)
            remaining -= roth_wd
        if remaining > 0:
            tax_wd += min(remaining, taxable_bal - tax_wd)

    # Also consider Roth conversion if bracket room remains
    roth_conversion = 0
    if trad_wd < bracket_room:
        roth_conversion = min(bracket_room - trad_wd, trad_bal - trad_wd, trad_bal * 0.05)

    return tax_wd, trad_wd, roth_wd, roth_conversion
```

**Year-by-year logic:**
1. Calculate all fixed income (SS, pension, annuity) and its tax impact
2. Determine the marginal bracket and how much room remains
3. Fill the bracket with traditional withdrawals
4. Cover remaining needs from Roth (free) and taxable (cap gains rate)
5. If bracket room remains after meeting spending needs, do Roth conversions

**Pros:** Minimizes lifetime taxes by managing bracket exposure year-by-year. Naturally incorporates Roth conversions.
**Cons:** More complex to implement and explain. Requires annual recalculation.

### Strategy 3: Proportional

```python
def proportional_withdrawal(need, taxable_bal, trad_bal, roth_bal):
    """Withdraw proportionally from all accounts based on their share."""
    total = taxable_bal + trad_bal + roth_bal
    if total == 0:
        return 0, 0, 0

    tax_pct = taxable_bal / total
    trad_pct = trad_bal / total
    roth_pct = roth_bal / total

    # Gross up for taxes on traditional portion
    gross_need = need / (1 - trad_pct * 0.25)  # Approximate

    tax_wd = min(gross_need * tax_pct, taxable_bal)
    trad_wd = min(gross_need * trad_pct, trad_bal)
    roth_wd = min(gross_need * roth_pct, roth_bal)

    return tax_wd, trad_wd, roth_wd
```

**Pros:** Maintains tax diversification throughout. Simple. Never accidentally depletes one account type early.
**Cons:** Doesn't optimize brackets at all. Withdraws Roth when it could be growing tax-free.

### Strategy 4: Roth-Bridge

For early retirees with a gap before SS:

```python
def roth_bridge_withdrawal(year, retirement_year, ss_start_year, need,
                           taxable_bal, trad_bal, roth_bal):
    """
    Gap years: heavy traditional + conversions (low bracket).
    Post-SS: minimal traditional, cover shortfall from Roth/taxable.
    """
    if year < ss_start_year:
        # Gap year: fill low brackets aggressively
        # Traditional withdrawal + conversion to fill 12% bracket
        trad_wd = min(need / 0.88, trad_bal)  # ~12% rate
        roth_conversion = min(trad_bal * 0.05, 127_000 - trad_wd)
        return 0, trad_wd, 0, roth_conversion
    else:
        # Post-SS: minimize traditional, lean on Roth
        return bracket_optimized_withdrawal(need, ...)
```

**Pros:** Exploits the low-income gap years aggressively. Can move $200-500K from traditional to Roth at 10-12% rates.
**Cons:** Front-loads tax payments (pays tax now on conversions). Only works if there's a meaningful gap.

## Comparison Framework

Run all strategies on the same client data and report:

| Metric | Conventional | Bracket-Opt | Proportional | Roth-Bridge |
|--------|-------------|-------------|--------------|-------------|
| Lifetime taxes paid | | | | |
| Final portfolio (median) | | | | |
| MC success rate | | | | |
| Effective rate year 1 | | | | |
| Effective rate year 15 | | | | |
| Roth balance at 85 | | | | |
| RMD exposure at 75 | | | | |

The bracket-optimized strategy typically wins on lifetime taxes but loses on simplicity. Present honestly.
