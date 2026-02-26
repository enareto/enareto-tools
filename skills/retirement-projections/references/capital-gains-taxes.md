# Capital Gains Tax Reference

## Why This Matters

The previous model treated all withdrawals as ordinary income. This is correct for traditional 401(k)/IRA withdrawals, but **wrong for taxable account withdrawals**. Taxable accounts are subject to capital gains tax rates, which are substantially lower than ordinary income rates — and can even be **0%** for moderate-income retirees.

Getting this wrong affects:
- **Withdrawal strategy:** Taxable accounts are cheaper to withdraw from than the model assumes, which changes the optimal withdrawal order
- **After-tax income:** A retiree paying 0% capital gains on $50K of gains keeps $50K. At ordinary rates (22%), they'd keep $39K. That's an $11K/year error.
- **Monte Carlo outcomes:** Over-taxing taxable withdrawals depletes the portfolio faster than reality

## Capital Gains Tax Rates (2025)

### Long-Term Capital Gains (held >1 year)

Taxed at preferential rates based on **total taxable income** (not just the gains):

```python
def long_term_capital_gains_tax_mfj(taxable_income, capital_gains):
    """
    Federal tax on long-term capital gains for MFJ.
    taxable_income: ordinary income AFTER standard deduction (includes the gains)
    capital_gains: the portion that is long-term capital gains

    Returns: tax on the capital gains portion only
    """
    # 2025 MFJ brackets for LTCG
    brackets = [
        (96_700, 0.00),    # 0% up to this taxable income
        (553_850, 0.15),   # 15% for this range
        (float('inf'), 0.20),  # 20% above
    ]

    # Where do the gains "sit" in the income stack?
    # Ordinary income fills first, then gains stack on top
    ordinary = taxable_income - capital_gains
    income_before_gains = max(ordinary, 0)

    tax = 0
    remaining_gains = capital_gains
    cumulative = income_before_gains

    for bracket_top, rate in brackets:
        if remaining_gains <= 0:
            break
        room_in_bracket = max(bracket_top - cumulative, 0)
        gains_in_bracket = min(remaining_gains, room_in_bracket)
        tax += gains_in_bracket * rate
        remaining_gains -= gains_in_bracket
        cumulative += gains_in_bracket

    return tax
```

**2025 MFJ Brackets:**
| Taxable Income (including gains) | LTCG Rate |
|----------------------------------|-----------|
| Up to $96,700 | 0% |
| $96,701 - $553,850 | 15% |
| Over $553,850 | 20% |

**2025 Single Brackets:**
| Taxable Income (including gains) | LTCG Rate |
|----------------------------------|-----------|
| Up to $48,350 | 0% |
| $48,351 - $518,900 | 15% |
| Over $518,900 | 20% |

### Net Investment Income Tax (NIIT)

Additional 3.8% surtax on investment income (capital gains, dividends, interest) for high earners:
- MFJ: AGI > $250,000
- Single: AGI > $200,000

```python
def niit(agi, investment_income, filing='mfj'):
    threshold = 250_000 if filing == 'mfj' else 200_000
    excess = max(agi - threshold, 0)
    niit_base = min(excess, investment_income)
    return niit_base * 0.038
```

### Short-Term Capital Gains (held ≤1 year)

Taxed as ordinary income — same progressive brackets as wages. No preferential rate.

## How Taxable Account Withdrawals Work

When selling investments in a taxable brokerage account, you don't pay tax on the full withdrawal — only on the **gain** (appreciation above your cost basis).

```python
def taxable_withdrawal_tax(withdrawal_amount, cost_basis_pct=0.60,
                           holding_period='long',
                           other_taxable_income=0,
                           filing='mfj'):
    """
    withdrawal_amount: total amount sold
    cost_basis_pct: what fraction of the account is original contributions (basis)
        Typical for long-held accounts: 40-60% is basis, rest is gains
        For recently funded accounts: 80-95% is basis
    holding_period: 'long' (>1yr, preferential rates) or 'short' (ordinary rates)
    other_taxable_income: AGI from other sources (SS, trad withdrawals, etc.)
    """
    basis_returned = withdrawal_amount * cost_basis_pct  # Tax-free
    gains = withdrawal_amount * (1 - cost_basis_pct)      # Taxable

    if holding_period == 'short':
        # Taxed as ordinary income — use regular brackets
        return gains  # Return taxable amount; caller applies ordinary rates

    # Long-term: use preferential rates
    total_taxable = other_taxable_income + gains
    tax = long_term_capital_gains_tax_mfj(total_taxable, gains)

    # Add NIIT if applicable
    agi = other_taxable_income + gains + basis_returned  # Approximate
    tax += niit(agi, gains, filing)

    return tax
```

### Cost Basis Estimation

If the user doesn't know their exact cost basis, estimate based on account age and contribution pattern:

| Account Age | Typical Basis % | Gain % |
|-------------|----------------|--------|
| < 3 years | 80-95% | 5-20% |
| 3-10 years | 60-80% | 20-40% |
| 10-20 years | 40-60% | 40-60% |
| 20+ years | 25-40% | 60-75% |

**Better approach if available:** Ask for the account's current value and total contributions. Basis % = total contributions / current value.

## The 0% Capital Gains Bracket — A Major Planning Opportunity

For retirees with moderate income, the 0% LTCG bracket is a powerful tool:

**Example:** Retired couple, $30,000 standard deduction, $60,000 SS (85% taxable = $51,000), no other income.
- Taxable income before gains: $51,000 - $30,000 = $21,000
- Room in 0% bracket: $96,700 - $21,000 = **$75,700**
- They can realize $75,700 in long-term capital gains **tax-free** every year

This is why the bracket-optimized withdrawal strategy specifically checks the 0% LTCG bracket before pulling from traditional accounts. In many cases, early retirement years allow massive tax-free gain harvesting.

```python
def annual_tax_free_gain_harvesting_room(other_taxable_income, filing='mfj'):
    """How much LTCG can be realized at 0% this year?"""
    bracket_top = 96_700 if filing == 'mfj' else 48_350
    return max(bracket_top - other_taxable_income, 0)
```

## Qualified Dividends

Qualified dividends (most US stock dividends, many international) are taxed at the same preferential LTCG rates, not ordinary rates. In a taxable account holding index funds:

- Typical dividend yield: 1.5-2.0% for total market index
- These dividends generate taxable income each year (even if reinvested)
- But they're taxed at LTCG rates, not ordinary rates

Model this as ongoing annual tax drag in taxable accounts:

```python
def annual_taxable_account_tax_drag(balance, dividend_yield=0.018,
                                     other_income=0, filing='mfj'):
    """Annual tax owed on dividends in taxable account."""
    dividends = balance * dividend_yield
    tax = long_term_capital_gains_tax_mfj(other_income + dividends, dividends)
    return tax
```

## Impact on Withdrawal Strategies

The correct tax treatment changes the optimal withdrawal order:

| Scenario | Without CG Rates (old model) | With CG Rates (correct) |
|----------|---------------------------|----------------------|
| Selling $100K from taxable (50% gain) | ~$12,500 tax (25% on $50K) | $0-$7,500 tax (0-15% on $50K) |
| Selling $100K from traditional | ~$15,000 tax (on $100K) | ~$15,000 tax (same — ordinary rates) |
| **Implied preference** | Traditional slightly worse | **Taxable much cheaper** |

This reinforces the conventional wisdom of taxable-first but for the right reason. It also creates tax-gain harvesting opportunities in the 0% bracket that the model should exploit.

## State Capital Gains Treatment

Most states tax capital gains as ordinary income (no preferential rate). Notable exceptions:
- **No income tax states** (FL, TX, etc.): No state CG tax
- **AZ:** 2.5% flat (same as ordinary)
- **Most states:** Same brackets as ordinary income

A few states have small preferential rates or exclusions for long-held assets, but these are minor compared to the federal 0%/15%/20% structure. The federal preferential rate does the heavy lifting.
