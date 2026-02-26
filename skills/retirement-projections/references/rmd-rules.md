# Required Minimum Distributions (RMDs) Reference

## Why This Matters

RMDs force you to withdraw from traditional retirement accounts starting at age 73 (SECURE Act 2.0), whether you need the money or not. These forced withdrawals are taxed as ordinary income and can:

- Push you into a higher tax bracket unexpectedly
- Increase the taxable portion of Social Security from 50% to 85%
- Trigger the NIIT (3.8% surtax) on investment income
- Increase Medicare premiums (IRMAA surcharges)
- Make the annuity or Roth conversion strategy moot if RMDs already fill the bracket

A couple with $3M in traditional accounts at age 73 faces RMDs of ~$113K/year growing to ~$190K by age 85. Combined with SS, that's $300K+ of taxable income without touching a single discretionary dollar. This can mean 24-32% marginal rates on income they didn't even choose to take.

**This is why Roth conversions in the gap years matter so much** — every dollar converted before 73 is a dollar that never generates an RMD.

## SECURE Act 2.0 Rules (Current Law)

| Birth Year | RMD Start Age |
|-----------|--------------|
| 1950 or earlier | 72 (already started) |
| 1951-1959 | 73 |
| 1960 or later | 75 |

**Roth IRAs:** No RMDs for the original owner (spouse beneficiaries also exempt). Roth 401(k)s required RMDs until 2024; starting 2024, Roth 401(k)s are also exempt. This is another reason to convert to Roth.

**First-year exception:** The first RMD can be delayed until April 1 of the year after reaching RMD age. But this means two RMDs in one year (year 1 deferred + year 2 on time), which can cause a tax bracket spike. Generally better to take the first RMD on time.

## Uniform Lifetime Table (Table III)

Used when spouse is NOT more than 10 years younger. This is the most common table.

The distribution period (divisor) determines what fraction of the account must be withdrawn:
`RMD = Prior Year-End Balance / Distribution Period`

```python
# Uniform Lifetime Table (IRS Table III) — SECURE Act 2.0 updated
# Age: Distribution Period
RMD_TABLE = {
    72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9,
    78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7,
    84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9,
    90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9,
    96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4, 101: 6.0,
    102: 5.6, 103: 5.2, 104: 4.9, 105: 4.6, 106: 4.3, 107: 4.1,
    108: 3.9, 109: 3.7, 110: 3.5, 111: 3.4, 112: 3.3, 113: 3.1,
    114: 3.0, 115: 2.9, 116: 2.8, 117: 2.7, 118: 2.5, 119: 2.3,
    120: 2.0,
}

def calculate_rmd(age, prior_year_end_balance):
    """
    Calculate Required Minimum Distribution.
    age: owner's age as of Dec 31 of the distribution year
    prior_year_end_balance: total traditional IRA + 401(k) balance on Dec 31 of prior year
    """
    if age < 73:  # Born 1951-1959; use 75 for born 1960+
        return 0

    period = RMD_TABLE.get(age, 2.0)  # Default to 2.0 for ages beyond table
    return prior_year_end_balance / period
```

## Joint Life Table (Table II)

Used when spouse is **sole beneficiary** AND more than 10 years younger. Produces smaller RMDs (longer distribution period).

```python
# Selected entries from Joint Life Table — full table is much larger
# Format: (owner_age, spouse_age): distribution_period
JOINT_LIFE_SELECTED = {
    (73, 60): 34.1, (73, 55): 37.1, (73, 50): 40.0,
    (75, 60): 32.2, (75, 55): 35.2, (75, 50): 38.2,
    (80, 65): 29.1, (80, 60): 30.9, (80, 55): 33.3,
    (85, 70): 24.0, (85, 65): 26.0, (85, 60): 28.4,
    (90, 75): 19.3, (90, 70): 21.6, (90, 65): 23.6,
}
# If needed for a specific age combo, look up IRS Publication 590-B Table II
```

## RMD Impact Over Time

Example: Couple with $3,000,000 in traditional accounts at age 73, growing at 5%/year after withdrawals:

```python
def project_rmds(starting_balance, start_age=73, end_age=95, growth_rate=0.05):
    """Project RMDs and remaining balance over time."""
    balance = starting_balance
    results = []
    for age in range(start_age, end_age + 1):
        rmd = calculate_rmd(age, balance)
        results.append({
            'age': age,
            'balance_before': balance,
            'rmd': rmd,
            'rmd_pct': rmd / balance * 100 if balance > 0 else 0,
        })
        balance = (balance - rmd) * (1 + growth_rate)
    return results
```

**Example trajectory ($3M at 73, 5% growth):**

| Age | Balance | RMD | RMD % | Cumulative RMDs |
|-----|---------|-----|-------|-----------------|
| 73 | $3,000,000 | $113,208 | 3.8% | $113K |
| 75 | $3,040,000 | $123,469 | 4.1% | $349K |
| 80 | $3,090,000 | $152,970 | 5.0% | $1,029K |
| 85 | $2,960,000 | $185,000 | 6.3% | $1,848K |
| 90 | $2,580,000 | $211,475 | 8.2% | $2,788K |
| 95 | $1,920,000 | $215,730 | 11.2% | $3,763K |

Note: the RMD percentage increases every year even if the balance doesn't grow, because the divisor shrinks. By 95, you're withdrawing 11%+ of the account annually.

## Tax Bracket Impact of RMDs

RMDs stack on top of other income. For a couple with $140K SS (with COLA):

| Age | SS Income | RMD | Total Income | Marginal Bracket |
|-----|-----------|-----|-------------|-----------------|
| 73 | $140K | $113K | $253K | 24% federal |
| 80 | $165K | $153K | $318K | 24% federal |
| 85 | $185K | $185K | $370K | 32% federal |
| 90 | $203K | $211K | $414K | 32% federal |

Without RMDs (if converted to Roth), the couple would be in the 22% bracket on just their SS. The RMDs push them 10+ percentage points higher.

**Lifetime tax cost of NOT doing Roth conversions:** If the couple converts $500K during gap years at 12% ($60K tax), they avoid paying 24-32% on those dollars later via RMDs. Net savings: $60-100K over 20 years.

## Integration with the Model

### In the Year-by-Year Projection:

```python
def compute_year(year, trad_balance, age, ...):
    # Calculate RMD first — it's mandatory, not optional
    rmd = calculate_rmd(age, trad_balance)

    # The RMD counts as a traditional withdrawal for tax purposes
    # But the client may need MORE than the RMD for spending
    spending_need = expenses - ss_income - other_income
    trad_withdrawal = max(rmd, spending_need_from_trad)

    # If RMD exceeds spending need, the excess gets reinvested in taxable
    excess_rmd = max(rmd - spending_need_from_trad, 0)
    # This excess is still taxed as ordinary income, then invested after-tax
    after_tax_excess = excess_rmd * (1 - marginal_rate)
    taxable_balance += after_tax_excess

    # Tax the full traditional withdrawal (including RMD) as ordinary income
    taxable_income += trad_withdrawal
```

### In Roth Conversion Analysis:

```python
def roth_conversion_value(trad_balance, conversion_amount, current_rate, future_rate):
    """
    Compare: convert now at current_rate vs. pay RMDs later at future_rate.
    """
    tax_now = conversion_amount * current_rate
    # Future RMD tax on same dollars (grown and then distributed)
    years_to_rmd = 73 - current_age  # or 75 if born 1960+
    grown = conversion_amount * (1.05 ** years_to_rmd)  # Approximate growth
    tax_later = grown * future_rate  # Will be higher rate due to RMD stacking

    return {
        'tax_now': tax_now,
        'tax_later_pv': tax_later / (1.05 ** years_to_rmd),  # Present value
        'savings': tax_later / (1.05 ** years_to_rmd) - tax_now,
    }
```

### RMD Aggregation Rules:

- **Multiple IRAs:** RMDs are calculated separately for each IRA, but can be taken from any one IRA
- **Multiple 401(k)s:** Each 401(k) must satisfy its own RMD (can't aggregate)
- **After rollover to IRA:** All traditional IRAs aggregate for RMD purposes

For modeling purposes, treat all traditional balances as one pool (assuming rollover at retirement, which is standard practice).

## Penalty for Missing RMDs

25% excise tax on the amount not withdrawn (reduced to 10% if corrected within 2 years). The model should never allow this — always compute and enforce the minimum withdrawal.

## Key Interactions with Other Model Components

| Component | How RMDs Interact |
|-----------|------------------|
| **SS taxation** | RMDs count as "other income" for SS taxation threshold. Large RMDs push SS to 85% taxable. |
| **IRMAA** | RMDs can push income above Medicare premium surcharge thresholds ($206K+ MFJ). Not modeled here but worth noting. |
| **Capital gains bracket** | RMDs as ordinary income stack first, pushing capital gains into 15%+ bracket. Reduces 0% CG harvesting room. |
| **Dynamic guardrails** | RMD may exceed spending need. Excess gets reinvested in taxable (after tax). The portfolio shifts from traditional to taxable over time. |
| **Roth conversions** | Every dollar converted before RMD age is a dollar that avoids forced distribution. Gap years at 12% rate vs. RMD years at 24%+. |
| **Annuity** | Annuity from traditional balance reduces the balance subject to RMDs. But the annuity income is still ordinary income. Net effect depends on whether the annuity rate exceeds the RMD rate. |
