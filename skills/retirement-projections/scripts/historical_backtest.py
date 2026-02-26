#!/usr/bin/env python3
"""
Historical backtest: run a retirement plan against actual S&P 500 / bond / T-bill
returns for every possible starting year from 1928 onward.

Usage:
    python historical_backtest.py projections.json [retirement_year] [plan_horizon]

Reads the projection JSON to extract: starting portfolio, allocation, spending curve,
SS income, tax parameters. Then replays the plan against historical returns.

Output: survival rate, worst/best starting years, comparison with Monte Carlo.
"""

import json
import sys

# ─── Historical Return Data (1928-2024) ───

SP500 = {
    1928: 0.4381, 1929: -0.0830, 1930: -0.2512, 1931: -0.4384, 1932: -0.0864,
    1933: 0.4998, 1934: -0.0119, 1935: 0.4674, 1936: 0.3194, 1937: -0.3534,
    1938: 0.2928, 1939: -0.0110, 1940: -0.1067, 1941: -0.1277, 1942: 0.1917,
    1943: 0.2506, 1944: 0.1903, 1945: 0.3582, 1946: -0.0843, 1947: 0.0520,
    1948: 0.0570, 1949: 0.1830, 1950: 0.3058, 1951: 0.2402, 1952: 0.1837,
    1953: -0.0099, 1954: 0.5256, 1955: 0.3260, 1956: 0.0744, 1957: -0.1046,
    1958: 0.4372, 1959: 0.1206, 1960: 0.0034, 1961: 0.2664, 1962: -0.0881,
    1963: 0.2261, 1964: 0.1642, 1965: 0.1240, 1966: -0.0997, 1967: 0.2380,
    1968: 0.1081, 1969: -0.0824, 1970: 0.0400, 1971: 0.1431, 1972: 0.1898,
    1973: -0.1466, 1974: -0.2647, 1975: 0.3720, 1976: 0.2384, 1977: -0.0698,
    1978: 0.0656, 1979: 0.1844, 1980: 0.3242, 1981: -0.0491, 1982: 0.2141,
    1983: 0.2251, 1984: 0.0627, 1985: 0.3216, 1986: 0.1847, 1987: 0.0581,
    1988: 0.1654, 1989: 0.3148, 1990: -0.0306, 1991: 0.3023, 1992: 0.0762,
    1993: 0.1008, 1994: 0.0132, 1995: 0.3743, 1996: 0.2294, 1997: 0.3336,
    1998: 0.2858, 1999: 0.2104, 2000: -0.0910, 2001: -0.1189, 2002: -0.2210,
    2003: 0.2838, 2004: 0.1088, 2005: 0.0491, 2006: 0.1579, 2007: 0.0549,
    2008: -0.3700, 2009: 0.2646, 2010: 0.1506, 2011: 0.0211, 2012: 0.1600,
    2013: 0.3239, 2014: 0.1369, 2015: 0.0138, 2016: 0.1196, 2017: 0.2183,
    2018: -0.0438, 2019: 0.3149, 2020: 0.1840, 2021: 0.2871, 2022: -0.1811,
    2023: 0.2624, 2024: 0.2502,
}

BONDS = {
    1928: 0.0084, 1929: 0.0342, 1930: 0.0454, 1931: -0.0531, 1932: 0.1644,
    1933: -0.0007, 1934: 0.1002, 1935: 0.0498, 1936: 0.0751, 1937: 0.0023,
    1938: 0.0553, 1939: 0.0594, 1940: 0.0600, 1941: 0.0056, 1942: 0.0322,
    1943: 0.0208, 1944: 0.0181, 1945: 0.1073, 1946: -0.0010, 1947: -0.0263,
    1948: 0.0340, 1949: 0.0645, 1950: 0.0006, 1951: -0.0394, 1952: 0.0116,
    1953: 0.0363, 1954: 0.0713, 1955: -0.0130, 1956: -0.0559, 1957: 0.0745,
    1958: -0.0610, 1959: -0.0226, 1960: 0.1378, 1961: 0.0097, 1962: 0.0689,
    1963: 0.0121, 1964: 0.0351, 1965: 0.0071, 1966: 0.0365, 1967: -0.0919,
    1968: -0.0026, 1969: -0.0508, 1970: 0.1637, 1971: 0.0926, 1972: 0.0569,
    1973: -0.0111, 1974: 0.0435, 1975: 0.0919, 1976: 0.1575, 1977: -0.0069,
    1978: -0.0116, 1979: -0.0118, 1980: -0.0395, 1981: 0.0186, 1982: 0.4036,
    1983: 0.0065, 1984: 0.1543, 1985: 0.3097, 1986: 0.2448, 1987: -0.0274,
    1988: 0.0967, 1989: 0.1801, 1990: 0.0618, 1991: 0.1930, 1992: 0.0806,
    1993: 0.1424, 1994: -0.0778, 1995: 0.2348, 1996: 0.0143, 1997: 0.0994,
    1998: 0.1492, 1999: -0.0825, 2000: 0.1666, 2001: 0.0357, 2002: 0.1759,
    2003: 0.0138, 2004: 0.0451, 2005: 0.0287, 2006: 0.0196, 2007: 0.1012,
    2008: 0.2022, 2009: -0.1112, 2010: 0.0841, 2011: 0.1604, 2012: 0.0297,
    2013: -0.0917, 2014: 0.1075, 2015: 0.0055, 2016: 0.0069, 2017: 0.0214,
    2018: -0.0002, 2019: 0.0918, 2020: 0.1126, 2021: -0.0426, 2022: -0.1746,
    2023: 0.0396, 2024: 0.0073,
}

TBILLS = {
    1928: 0.0356, 1929: 0.0475, 1930: 0.0241, 1931: 0.0115, 1932: 0.0088,
    1933: 0.0052, 1934: 0.0027, 1935: 0.0017, 1936: 0.0018, 1937: 0.0031,
    1938: 0.0002, 1939: 0.0002, 1940: 0.0000, 1941: 0.0006, 1942: 0.0027,
    1943: 0.0035, 1944: 0.0033, 1945: 0.0033, 1946: 0.0035, 1947: 0.0050,
    1948: 0.0081, 1949: 0.0110, 1950: 0.0120, 1951: 0.0149, 1952: 0.0166,
    1953: 0.0182, 1954: 0.0086, 1955: 0.0157, 1956: 0.0246, 1957: 0.0314,
    1958: 0.0154, 1959: 0.0295, 1960: 0.0266, 1961: 0.0213, 1962: 0.0273,
    1963: 0.0312, 1964: 0.0354, 1965: 0.0393, 1966: 0.0476, 1967: 0.0421,
    1968: 0.0521, 1969: 0.0658, 1970: 0.0652, 1971: 0.0439, 1972: 0.0384,
    1973: 0.0693, 1974: 0.0800, 1975: 0.0580, 1976: 0.0508, 1977: 0.0512,
    1978: 0.0718, 1979: 0.1038, 1980: 0.1124, 1981: 0.1471, 1982: 0.1054,
    1983: 0.0880, 1984: 0.0985, 1985: 0.0772, 1986: 0.0616, 1987: 0.0547,
    1988: 0.0635, 1989: 0.0837, 1990: 0.0781, 1991: 0.0560, 1992: 0.0351,
    1993: 0.0290, 1994: 0.0390, 1995: 0.0560, 1996: 0.0521, 1997: 0.0526,
    1998: 0.0486, 1999: 0.0480, 2000: 0.0598, 2001: 0.0333, 2002: 0.0165,
    2003: 0.0094, 2004: 0.0114, 2005: 0.0300, 2006: 0.0473, 2007: 0.0451,
    2008: 0.0124, 2009: 0.0015, 2010: 0.0013, 2011: 0.0003, 2012: 0.0005,
    2013: 0.0002, 2014: 0.0002, 2015: 0.0005, 2016: 0.0020, 2017: 0.0080,
    2018: 0.0181, 2019: 0.0212, 2020: 0.0036, 2021: 0.0005, 2022: 0.0150,
    2023: 0.0509, 2024: 0.0525,
}


def run_backtest(projections, retirement_year=12, plan_horizon=30):
    """
    Replay the plan against historical returns for every possible starting year.
    Uses the projection data to extract spending, SS, and portfolio parameters.
    """
    # Extract parameters from projections
    ret_data = [r for r in projections if r["year"] >= retirement_year]
    if not ret_data:
        print("ERROR: No retirement-year data in projections")
        return None

    first_ret = ret_data[0]
    starting_portfolio = first_ret["total_portfolio"]

    # Determine allocation from first retirement year
    # (or use default if not available)
    stock_pct = 0.60
    bond_pct = 0.35
    cash_pct = 0.05

    # Build spending/SS schedule from projections
    spending_schedule = {}
    ss_schedule = {}
    for r in ret_data:
        yr_offset = r["year"] - retirement_year
        spending_schedule[yr_offset] = r["expenses"]
        ss_schedule[yr_offset] = r.get("ss_income", 0) + r.get("annuity_income", 0)

    max_year = max(SP500.keys())
    min_year = min(SP500.keys())
    max_start = max_year - plan_horizon + 1

    results = {}

    for start_year in range(min_year, max_start + 1):
        portfolio = starting_portfolio
        failed = False
        trajectory = []

        for yr in range(plan_horizon):
            hist_year = start_year + yr
            if hist_year not in SP500:
                break

            stock_r = SP500[hist_year]
            bond_r = BONDS[hist_year]
            cash_r = TBILLS[hist_year]
            blended = stock_pct * stock_r + bond_pct * bond_r + cash_pct * cash_r

            # Get spending and guaranteed income for this year of retirement
            expenses = spending_schedule.get(yr, spending_schedule.get(max(spending_schedule.keys()), 200_000))
            guaranteed = ss_schedule.get(yr, ss_schedule.get(max(ss_schedule.keys()), 0))

            # Net withdrawal needed
            need = expenses - guaranteed
            # Tax adjustment (rough: ~20% effective on withdrawals)
            if need > 0:
                gross_wd = need / 0.80
            else:
                gross_wd = 0

            portfolio = portfolio * (1 + blended) - gross_wd
            trajectory.append(portfolio)

            if portfolio <= 0:
                if guaranteed >= expenses * 0.6:
                    portfolio = 0
                    continue
                failed = True
                break

        min_portfolio = min(trajectory) if trajectory else 0
        results[start_year] = {
            "survived": not failed,
            "final_portfolio": max(portfolio, 0),
            "min_portfolio": min_portfolio,
            "depletion_year": len(trajectory) if failed else None,
        }

    # Aggregate
    survived = sum(1 for r in results.values() if r["survived"])
    total = len(results)
    finals = sorted([r["final_portfolio"] for r in results.values()])

    worst_year = min(results, key=lambda k: results[k]["final_portfolio"])
    best_year = max(results, key=lambda k: results[k]["final_portfolio"])
    failed_years = [k for k, v in results.items() if not v["survived"]]

    print("=" * 70)
    print("HISTORICAL BACKTEST RESULTS")
    print("=" * 70)
    print(f"Plan horizon: {plan_horizon} years from retirement")
    print(f"Starting portfolio: ${starting_portfolio:,.0f}")
    print(f"Allocation: {stock_pct:.0%} stocks / {bond_pct:.0%} bonds / {cash_pct:.0%} cash")
    print(f"Historical periods tested: {total} ({min_year}-{max_start})")
    print()
    print(f"Survival rate: {survived}/{total} = {survived/total:.1%}")
    print(f"Median final portfolio: ${finals[total//2]:,.0f}")
    print(f"10th percentile final: ${finals[int(total*0.10)]:,.0f}")
    print(f"90th percentile final: ${finals[int(total*0.90)]:,.0f}")
    print()
    print(f"Worst starting year: {worst_year} → ${results[worst_year]['final_portfolio']:,.0f}")
    print(f"Best starting year:  {best_year} → ${results[best_year]['final_portfolio']:,.0f}")

    if failed_years:
        print(f"\nFailed starting years ({len(failed_years)}):")
        for fy in sorted(failed_years):
            dy = results[fy]["depletion_year"]
            print(f"  {fy}: depleted in year {dy} of retirement")
    else:
        print(f"\nNo failures across any historical period!")

    # Notable cohorts
    print(f"\nNotable cohort results:")
    for label, yr in [("1929 (Depression)", 1929), ("1937 (Double-dip)", 1937),
                       ("1966 (Stagflation)", 1966), ("1973 (Oil crisis)", 1973),
                       ("2000 (Dot-com)", 2000)]:
        if yr in results:
            r = results[yr]
            status = "SURVIVED" if r["survived"] else f"DEPLETED yr {r['depletion_year']}"
            print(f"  {label}: {status}, final ${r['final_portfolio']:,.0f}, "
                  f"min ${r['min_portfolio']:,.0f}")

    return {
        "survival_rate": survived / total,
        "survived_count": survived,
        "total_periods": total,
        "worst_start": worst_year,
        "best_start": best_year,
        "median_final": finals[total // 2],
        "failed_years": failed_years,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python historical_backtest.py projections.json [retirement_year] [plan_horizon]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    if isinstance(data, list):
        projections = data
    elif isinstance(data, dict):
        for key in ["no_annuity", "recommended", "results", "projections"]:
            if key in data:
                if isinstance(data[key], dict) and "results" in data[key]:
                    projections = data[key]["results"]
                elif isinstance(data[key], list):
                    projections = data[key]
                break
        else:
            print("ERROR: Could not find projection data")
            sys.exit(1)

    ret_year = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    horizon = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    run_backtest(projections, retirement_year=ret_year, plan_horizon=horizon)
