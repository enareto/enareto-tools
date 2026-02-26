# State Income Tax Reference

## Overview

State income tax varies enormously — from 0% (nine states) to 13.3% (California top bracket). Using a flat 5% default can be off by $10-30K/year depending on the state and income level. This reference provides the complete bracket structure for all 50 states and DC.

**Always ask the user which state they live in.** If they plan to relocate in retirement (common — moving from NY/CA to FL/TX), model both the pre-retirement state and the retirement state.

## How to Use

```python
def state_tax(state, taxable_income, filing_status='mfj'):
    """
    Compute state income tax using progressive brackets.
    taxable_income: after federal standard deduction is NOT applied
                    (states have their own deductions/exemptions)
    filing_status: 'single' or 'mfj'
    """
    config = STATE_TAX_CONFIG[state.upper()]

    if config['type'] == 'none':
        return 0

    if config['type'] == 'flat':
        deduction = config.get('deduction', {}).get(filing_status, 0)
        return max(taxable_income - deduction, 0) * config['rate']

    if config['type'] == 'progressive':
        brackets = config['brackets'][filing_status]
        deduction = config.get('deduction', {}).get(filing_status, 0)
        ti = max(taxable_income - deduction, 0)
        tax = 0
        for bracket_top, rate in brackets:
            if ti <= 0:
                break
            taxable_in_bracket = min(ti, bracket_top)
            tax += taxable_in_bracket * rate
            ti -= taxable_in_bracket
        return tax
```

## Special Considerations for Retirement

- **Social Security taxation by state:** Most states don't tax SS benefits. Some do partially. Noted below.
- **Retirement income exclusions:** Some states exempt part or all of pension/retirement account distributions. Noted where applicable.
- **Property tax:** Not modeled here but matters for obligatory spending. User should provide.

## No Income Tax States

Nine states have no state income tax. Two additional states tax only interest/dividends.

```python
# No income tax at all
NO_TAX_STATES = ['AK', 'FL', 'NV', 'NH', 'SD', 'TN', 'TX', 'WA', 'WY']
# NH and TN: historically taxed interest/dividends but both have fully phased this out
```

## Flat Tax States

These states apply a single rate to all taxable income (after state-specific deductions).

```python
FLAT_TAX_STATES = {
    'AZ': {'rate': 0.025, 'deduction': {'single': 14_600, 'mfj': 29_200}},
    'CO': {'rate': 0.044, 'deduction': {'single': 14_600, 'mfj': 29_200}},  # Matches federal std ded
    'GA': {'rate': 0.0549, 'deduction': {'single': 12_000, 'mfj': 24_000}},  # Transitioning to flat by 2029
    'ID': {'rate': 0.058, 'deduction': {'single': 14_600, 'mfj': 29_200}},
    'IL': {'rate': 0.0495, 'deduction': {'single': 2_775, 'mfj': 5_550}},  # Personal exemption, not std ded
    'IN': {'rate': 0.0305, 'deduction': {'single': 1_000, 'mfj': 2_000}},  # Plus county tax 0.5-3%
    'KY': {'rate': 0.04, 'deduction': {'single': 3_160, 'mfj': 6_320}},
    'MA': {'rate': 0.09, 'deduction': {'single': 8_000, 'mfj': 16_000}},   # 4% surtax on income >$1M
    'MI': {'rate': 0.0405, 'deduction': {'single': 5_600, 'mfj': 11_200}},
    'MS': {'rate': 0.047, 'deduction': {'single': 2_300, 'mfj': 4_600}},   # First $10K exempt
    'NC': {'rate': 0.045, 'deduction': {'single': 12_750, 'mfj': 25_500}},
    'ND': {'rate': 0.0195, 'deduction': {'single': 14_600, 'mfj': 29_200}},  # Effectively near-zero
    'PA': {'rate': 0.0307, 'deduction': {'single': 0, 'mfj': 0}},  # No deductions, but doesn't tax retirement
    'UT': {'rate': 0.0465, 'deduction': {'single': 876, 'mfj': 1_752}},  # Credit-based system
}
```

**Notes:**
- **MA** has a 4% millionaire surtax on income above $1,000,000 (total 9% on income >$1M)
- **IN** has additional county taxes (typically 0.5-3%) — ask user for county
- **PA** does not tax retirement distributions (401k, IRA, pension) or SS — very favorable for retirees
- **IL** does not tax retirement income or SS

## Progressive Tax States (Married Filing Jointly Brackets)

Brackets shown as (amount taxable at this rate, rate). Apply sequentially.

```python
PROGRESSIVE_TAX_STATES = {
    'AL': {
        'deduction': {'single': 2_500, 'mfj': 7_500},
        'brackets': {
            'mfj': [(1_000, 0.02), (5_000, 0.04), (float('inf'), 0.05)],
            'single': [(500, 0.02), (2_500, 0.04), (float('inf'), 0.05)],
        }
    },
    'AR': {
        'deduction': {'single': 2_340, 'mfj': 4_680},
        'brackets': {
            'mfj': [(5_099, 0.02), (5_000, 0.04), (float('inf'), 0.044)],
            'single': [(5_099, 0.02), (5_000, 0.04), (float('inf'), 0.044)],
        }
    },
    'CA': {
        'deduction': {'single': 5_540, 'mfj': 11_080},
        'brackets': {
            'mfj': [
                (21_340, 0.01), (29_146, 0.02), (29_154, 0.04), (30_250, 0.06),
                (30_256, 0.08), (254_250, 0.093), (305_100, 0.103),
                (610_200, 0.113), (float('inf'), 0.123),
            ],
            'single': [
                (10_670, 0.01), (14_573, 0.02), (14_577, 0.04), (15_125, 0.06),
                (15_128, 0.08), (127_125, 0.093), (152_550, 0.103),
                (305_100, 0.113), (float('inf'), 0.123),
            ],
        },
        # Note: additional 1% Mental Health Services Tax on income >$1M
    },
    'CT': {
        'deduction': {'single': 0, 'mfj': 0},  # Uses personal exemptions/credits
        'brackets': {
            'mfj': [
                (20_000, 0.02), (80_000, 0.045), (100_000, 0.055),
                (100_000, 0.06), (200_000, 0.065), (float('inf'), 0.0699),
            ],
            'single': [
                (10_000, 0.02), (40_000, 0.045), (50_000, 0.055),
                (50_000, 0.06), (100_000, 0.065), (float('inf'), 0.0699),
            ],
        }
    },
    'DE': {
        'deduction': {'single': 3_250, 'mfj': 6_500},
        'brackets': {
            'mfj': [
                (2_000, 0.0), (3_000, 0.022), (5_000, 0.039),
                (10_000, 0.048), (5_000, 0.052), (35_000, 0.0555),
                (float('inf'), 0.066),
            ],
            'single': [
                (2_000, 0.0), (3_000, 0.022), (5_000, 0.039),
                (10_000, 0.048), (5_000, 0.052), (35_000, 0.0555),
                (float('inf'), 0.066),
            ],
        }
    },
    'DC': {
        'deduction': {'single': 14_600, 'mfj': 29_200},
        'brackets': {
            'mfj': [
                (10_000, 0.04), (30_000, 0.06), (10_000, 0.065),
                (200_000, 0.085), (750_000, 0.0925), (float('inf'), 0.1075),
            ],
            'single': [
                (10_000, 0.04), (30_000, 0.06), (10_000, 0.065),
                (200_000, 0.085), (750_000, 0.0925), (float('inf'), 0.1075),
            ],
        }
    },
    'HI': {
        'deduction': {'single': 2_200, 'mfj': 4_400},
        'brackets': {
            'mfj': [
                (4_800, 0.014), (4_800, 0.032), (4_800, 0.055),
                (4_800, 0.064), (4_800, 0.068), (4_800, 0.072),
                (7_200, 0.076), (7_200, 0.079), (14_400, 0.0825),
                (142_400, 0.09), (float('inf'), 0.11),
            ],
            'single': [
                (2_400, 0.014), (2_400, 0.032), (2_400, 0.055),
                (2_400, 0.064), (2_400, 0.068), (2_400, 0.072),
                (3_600, 0.076), (3_600, 0.079), (7_200, 0.0825),
                (71_200, 0.09), (float('inf'), 0.11),
            ],
        }
    },
    'IA': {
        'deduction': {'single': 0, 'mfj': 0},
        'brackets': {
            'mfj': [(6_000, 0.044), (24_000, 0.0482), (float('inf'), 0.057)],
            'single': [(6_000, 0.044), (24_000, 0.0482), (float('inf'), 0.057)],
        },
        # Note: Iowa does not tax SS or retirement income for those 55+
    },
    'KS': {
        'deduction': {'single': 3_500, 'mfj': 8_000},
        'brackets': {
            'mfj': [(46_000, 0.031), (16_000, 0.0525), (float('inf'), 0.057)],
            'single': [(15_000, 0.031), (15_000, 0.0525), (float('inf'), 0.057)],
        }
    },
    'LA': {
        'deduction': {'single': 4_500, 'mfj': 9_000},
        'brackets': {
            'mfj': [(25_000, 0.0185), (75_000, 0.035), (float('inf'), 0.0425)],
            'single': [(12_500, 0.0185), (37_500, 0.035), (float('inf'), 0.0425)],
        }
    },
    'ME': {
        'deduction': {'single': 14_600, 'mfj': 29_200},
        'brackets': {
            'mfj': [(49_050, 0.058), (66_250, 0.0675), (float('inf'), 0.0715)],
            'single': [(26_050, 0.058), (35_200, 0.0675), (float('inf'), 0.0715)],
        }
    },
    'MD': {
        'deduction': {'single': 2_550, 'mfj': 5_100},  # Plus personal exemptions
        'brackets': {
            'mfj': [
                (1_000, 0.02), (1_000, 0.03), (1_000, 0.04), (97_000, 0.0475),
                (25_000, 0.05), (25_000, 0.0525), (100_000, 0.055),
                (float('inf'), 0.0575),
            ],
            'single': [
                (1_000, 0.02), (1_000, 0.03), (1_000, 0.04), (97_000, 0.0475),
                (25_000, 0.05), (25_000, 0.0525), (100_000, 0.055),
                (float('inf'), 0.0575),
            ],
        },
        # Note: MD also has county taxes (typically 2.25-3.2%) — must add
    },
    'MN': {
        'deduction': {'single': 14_575, 'mfj': 29_150},
        'brackets': {
            'mfj': [(47_820, 0.0535), (142_390, 0.068), (76_590, 0.0785), (float('inf'), 0.0985)],
            'single': [(32_070, 0.0535), (93_650, 0.068), (45_780, 0.0785), (float('inf'), 0.0985)],
        }
    },
    'MO': {
        'deduction': {'single': 14_600, 'mfj': 29_200},
        'brackets': {
            'mfj': [(1_207, 0.02), (1_207, 0.025), (1_207, 0.03), (1_207, 0.035),
                     (1_207, 0.04), (1_207, 0.045), (1_207, 0.05), (float('inf'), 0.048)],
            'single': [(1_207, 0.02), (1_207, 0.025), (1_207, 0.03), (1_207, 0.035),
                        (1_207, 0.04), (1_207, 0.045), (1_207, 0.05), (float('inf'), 0.048)],
        }
    },
    'MT': {
        'deduction': {'single': 5_540, 'mfj': 11_080},
        'brackets': {
            'mfj': [(20_500, 0.047), (float('inf'), 0.059)],
            'single': [(20_500, 0.047), (float('inf'), 0.059)],
        }
    },
    'NE': {
        'deduction': {'single': 7_900, 'mfj': 15_800},
        'brackets': {
            'mfj': [(7_610, 0.0246), (37_320, 0.0351), (26_780, 0.0501), (float('inf'), 0.0584)],
            'single': [(3_700, 0.0246), (22_170, 0.0351), (10_130, 0.0501), (float('inf'), 0.0584)],
        }
    },
    'NJ': {
        'deduction': {'single': 0, 'mfj': 0},  # NJ uses exemptions
        'brackets': {
            'mfj': [
                (20_000, 0.014), (30_000, 0.0175), (20_000, 0.035),
                (80_000, 0.05525), (350_000, 0.0637), (500_000, 0.0897),
                (float('inf'), 0.1075),
            ],
            'single': [
                (20_000, 0.014), (15_000, 0.0175), (5_000, 0.035),
                (40_000, 0.05525), (75_000, 0.0637), (345_000, 0.0897),
                (float('inf'), 0.1075),
            ],
        }
    },
    'NM': {
        'deduction': {'single': 14_600, 'mfj': 29_200},
        'brackets': {
            'mfj': [(8_000, 0.017), (8_000, 0.032), (8_000, 0.047),
                     (186_000, 0.049), (float('inf'), 0.059)],
            'single': [(5_500, 0.017), (5_500, 0.032), (5_500, 0.047),
                         (193_500, 0.049), (float('inf'), 0.059)],
        }
    },
    'NY': {
        'deduction': {'single': 8_000, 'mfj': 16_050},
        'brackets': {
            'mfj': [
                (17_150, 0.04), (6_850, 0.045), (27_900, 0.0525), (109_950, 0.0585),
                (161_550, 0.0625), (1_880_600, 0.0685), (3_796_000, 0.0965),
                (float('inf'), 0.103),
            ],
            'single': [
                (8_500, 0.04), (3_200, 0.045), (13_900, 0.0525), (55_000, 0.0585),
                (80_650, 0.0625), (942_800, 0.0685), (3_900_950, 0.0965),
                (float('inf'), 0.103),
            ],
        },
        # Note: NYC adds 3.078-3.876% for residents
    },
    'OH': {
        'deduction': {'single': 0, 'mfj': 0},  # Uses personal exemptions
        'brackets': {
            'mfj': [(26_050, 0.0), (20_350, 0.02745), (53_600, 0.03688), (float('inf'), 0.0375)],
            'single': [(26_050, 0.0), (20_350, 0.02745), (53_600, 0.03688), (float('inf'), 0.0375)],
        }
    },
    'OK': {
        'deduction': {'single': 6_350, 'mfj': 12_700},
        'brackets': {
            'mfj': [(2_000, 0.0025), (3_000, 0.0075), (5_250, 0.0175),
                     (2_600, 0.0275), (3_100, 0.0375), (float('inf'), 0.0475)],
            'single': [(1_000, 0.0025), (1_500, 0.0075), (2_625, 0.0175),
                         (1_300, 0.0275), (1_550, 0.0375), (float('inf'), 0.0475)],
        }
    },
    'OR': {
        'deduction': {'single': 2_605, 'mfj': 5_210},
        'brackets': {
            'mfj': [(7_300, 0.0475), (11_000, 0.0675), (231_700, 0.0875), (float('inf'), 0.099)],
            'single': [(4_050, 0.0475), (6_100, 0.0675), (115_850, 0.0875), (float('inf'), 0.099)],
        }
    },
    'RI': {
        'deduction': {'single': 10_550, 'mfj': 21_100},
        'brackets': {
            'mfj': [(77_450, 0.0375), (98_350, 0.0475), (float('inf'), 0.0599)],
            'single': [(77_450, 0.0375), (98_350, 0.0475), (float('inf'), 0.0599)],
        }
    },
    'SC': {
        'deduction': {'single': 14_600, 'mfj': 29_200},
        'brackets': {
            'mfj': [(3_460, 0.0), (3_460, 0.03), (3_460, 0.04),
                     (3_460, 0.05), (3_460, 0.06), (float('inf'), 0.064)],
            'single': [(3_460, 0.0), (3_460, 0.03), (3_460, 0.04),
                         (3_460, 0.05), (3_460, 0.06), (float('inf'), 0.064)],
        },
        # Note: SC has generous retirement income deduction ($10K under 65, all income at 65+)
    },
    'VT': {
        'deduction': {'single': 7_250, 'mfj': 14_500},
        'brackets': {
            'mfj': [(49_194, 0.0335), (70_108, 0.066), (118_398, 0.076), (float('inf'), 0.0875)],
            'single': [(45_400, 0.0335), (64_622, 0.066), (109_178, 0.076), (float('inf'), 0.0875)],
        }
    },
    'VA': {
        'deduction': {'single': 4_500, 'mfj': 9_000},
        'brackets': {
            'mfj': [(3_000, 0.02), (2_000, 0.03), (12_000, 0.05), (float('inf'), 0.0575)],
            'single': [(3_000, 0.02), (2_000, 0.03), (12_000, 0.05), (float('inf'), 0.0575)],
        }
    },
    'WV': {
        'deduction': {'single': 0, 'mfj': 0},  # Uses personal exemptions
        'brackets': {
            'mfj': [(10_000, 0.0236), (15_000, 0.0315), (15_000, 0.0354),
                     (20_000, 0.0472), (float('inf'), 0.0512)],
            'single': [(10_000, 0.0236), (15_000, 0.0315), (15_000, 0.0354),
                         (20_000, 0.0472), (float('inf'), 0.0512)],
        }
    },
    'WI': {
        'deduction': {'single': 12_760, 'mfj': 23_620},
        'brackets': {
            'mfj': [(19_090, 0.035), (24_620, 0.044), (322_970, 0.053), (float('inf'), 0.0765)],
            'single': [(14_320, 0.035), (14_570, 0.044), (232_310, 0.053), (float('inf'), 0.0765)],
        }
    },
}
```

## States That Don't Tax Social Security

Most states don't tax SS benefits. **States that DO tax SS** (partially or fully, often with income thresholds):

CO, CT, KS, MN, MO, MT, NE, NM, RI, UT, VT, WV

The rest either have no income tax or specifically exempt SS. When modeling a state that taxes SS, apply the state's rules for SS inclusion (often different from the federal 85% rule — many have income phase-outs).

## States With Favorable Retirement Income Treatment

| State | Benefit |
|-------|---------|
| PA | No tax on any retirement distributions (401k, IRA, pension) or SS |
| IL | No tax on retirement income or SS |
| MS | No tax on retirement distributions or SS |
| IA | No tax on retirement/SS for age 55+ |
| SC | Full deduction at age 65+ |
| FL, TX, WA, NV, WY, SD, AK, NH, TN | No income tax at all |

## Local Taxes (Must Add Separately)

Some states/cities have additional local income taxes that are significant:

| Location | Additional Tax |
|----------|---------------|
| New York City | 3.078-3.876% (progressive) |
| Yonkers | 16.75% surcharge on NY state tax |
| Maryland counties | 2.25-3.20% (varies by county) |
| Indiana counties | 0.5-3.0% |
| Ohio municipalities | 0.5-3.0% (many cities, notably Columbus 2.5%, Cleveland 2.5%) |
| Detroit, MI | 2.4% residents |
| Portland, OR metro | ~1% additional |

**Always ask:** "Do you live in a city or county with additional local income tax?"

## Implementation Note

The brackets above are approximate for 2025 and should be verified when the model is built. States adjust brackets annually for inflation. The structure (number of brackets, rate levels) changes rarely, but the dollar thresholds shift 1-3% per year.

For the purpose of a 30-year retirement projection, using current brackets with no inflation adjustment is conservative (bracket creep works against the taxpayer). A more accurate approach: inflate bracket thresholds at 2% per year, matching typical state CPI adjustments.
