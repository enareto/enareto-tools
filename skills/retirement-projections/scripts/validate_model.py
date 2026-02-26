#!/usr/bin/env python3
"""
Validate a retirement financial model's output for common errors.

Usage:
    python validate_model.py projections.json

Input: JSON file with array of year-by-year projection records.
Each record must have: year, george_age (or retiree_age), expenses, ss_income,
total_portfolio, effective_rate, withdrawal_rate, gross_salary (if working years).

Output: PASS/FAIL for each check with explanations.
"""

import json
import sys

def validate(projections, retirement_year=12):
    results = []
    passed = 0
    failed = 0

    # 1. Effective tax rate sanity
    for r in projections:
        if r.get("gross_salary", 0) > 300_000:
            rate = r.get("effective_rate", 0)
            if rate < 0.18 or rate > 0.38:
                results.append(("FAIL", f"Tax rate sanity",
                    f"Year {r['year']}: Effective rate {rate:.1%} on ${r['gross_salary']:,.0f} salary. "
                    f"Expected 18-38%. Check: standard deduction applied? 401k reducing taxable income? FICA included?"))
                failed += 1
                break
    else:
        results.append(("PASS", "Tax rate sanity", "Working-year effective rates within expected range"))
        passed += 1

    # 2. SS COLA check — use individual SS (george_ss) if available, else combined
    ss_key = "george_ss" if any(r.get("george_ss") for r in projections) else "ss_income"
    ss_years = [r for r in projections if r.get(ss_key, 0) > 0]
    if len(ss_years) >= 6:
        # Compare years 1 and 5 of claiming (skip the first to avoid entry noise)
        yr1 = ss_years[1]
        yr5 = [r for r in ss_years if r["year"] >= yr1["year"] + 4]
        if yr5:
            growth = yr5[0][ss_key] / yr1[ss_key]
            span = yr5[0]["year"] - yr1["year"]
            annual_growth = growth ** (1/span) - 1
            if annual_growth < 0.015:
                results.append(("FAIL", "SS COLA check",
                    f"SS ({ss_key}) grew only {annual_growth*100:.1f}%/yr over {span} years. "
                    f"Expected ≥2%/yr with COLA. Is COLA being applied after claiming?"))
                failed += 1
            else:
                results.append(("PASS", "SS COLA check",
                    f"SS ({ss_key}) growing at {annual_growth*100:.1f}%/yr — COLA is applied"))
                passed += 1
        else:
            results.append(("SKIP", "SS COLA check", "Not enough post-SS years to verify"))
    elif ss_years:
        results.append(("SKIP", "SS COLA check", "Need ≥6 years of SS data to verify COLA"))
    else:
        results.append(("SKIP", "SS COLA check", "No SS income in projections"))

    # 3. Portfolio growth during accumulation
    working = [r for r in projections if r["year"] <= retirement_year - 1]
    if len(working) >= 5:
        start_port = working[0]["total_portfolio"]
        end_port = working[-1]["total_portfolio"]
        growth_factor = end_port / start_port if start_port > 0 else 0
        years = len(working)
        if growth_factor < 1.5:
            results.append(("FAIL", "Accumulation growth",
                f"Portfolio grew only {growth_factor:.2f}x over {years} working years. "
                f"Expected ≥1.5x with 401k contributions + returns. "
                f"Check: are 401k contributions being added? Is employer match included?"))
            failed += 1
        else:
            results.append(("PASS", "Accumulation growth",
                f"Portfolio grew {growth_factor:.2f}x over {years} working years"))
            passed += 1

    # 4. Late-life SS coverage
    late_life = [r for r in projections if r.get("george_age", r.get("retiree_age", 0)) >= 85]
    if late_life:
        for r in late_life[:1]:
            ss = r.get("ss_income", 0)
            exp = r.get("expenses", 1)
            coverage = ss / exp if exp > 0 else 0
            if coverage < 0.5:
                results.append(("WARN", "Late-life SS coverage",
                    f"At age {r.get('george_age', r.get('retiree_age', '?'))}: "
                    f"SS ${ss:,.0f} covers only {coverage:.0%} of ${exp:,.0f} expenses. "
                    f"Check: Is SS COLA applied? Is spending realistically declining?"))
                failed += 1
            else:
                results.append(("PASS", "Late-life SS coverage",
                    f"At age {r.get('george_age', r.get('retiree_age', '?'))}: "
                    f"SS covers {coverage:.0%} of expenses"))
                passed += 1

    # 5. Withdrawal rate trajectory
    retired = [r for r in projections if r["year"] >= retirement_year + 5]
    high_wd = [r for r in retired if r.get("withdrawal_rate", 0) > 10
               and r.get("george_age", r.get("retiree_age", 0)) >= 75]
    if high_wd:
        r = high_wd[0]
        results.append(("WARN", "Withdrawal rate",
            f"Year {r['year']} (age {r.get('george_age', '?')}): "
            f"Withdrawal rate {r['withdrawal_rate']:.1f}%. "
            f"Expected <5% after SS starts. Check income sources."))
        failed += 1
    elif retired:
        results.append(("PASS", "Withdrawal rate", "Post-SS withdrawal rates within expected range"))
        passed += 1

    # 6. Spending curve check
    retired_spending = [(r.get("george_age", r.get("retiree_age", 0)), r["expenses"])
                        for r in projections if r["year"] >= retirement_year]
    if len(retired_spending) >= 15:
        early = [s for a, s in retired_spending if 65 <= a <= 70]
        late = [s for a, s in retired_spending if a >= 85]
        if early and late:
            avg_early = sum(early) / len(early)
            avg_late = sum(late) / len(late)
            if avg_late >= avg_early * 0.95:
                results.append(("WARN", "Spending curve",
                    f"Late-life spending (${avg_late:,.0f}) is ≥95% of early retirement (${avg_early:,.0f}). "
                    f"Real spending typically declines 30-50% by age 85+. "
                    f"Is a realistic spending curve being used?"))
                failed += 1
            else:
                ratio = avg_late / avg_early
                results.append(("PASS", "Spending curve",
                    f"Spending declines from ${avg_early:,.0f} (early) to ${avg_late:,.0f} (late), "
                    f"ratio {ratio:.0%}. Realistic."))
                passed += 1

    # 7. Capital gains differentiation check
    # If projections have taxable_withdrawal and taxable_tax fields, verify CG rates
    cg_records = [r for r in projections if r.get("taxable_withdrawal", 0) > 0
                  and r.get("taxable_withdrawal_tax") is not None]
    if cg_records:
        for r in cg_records[:3]:
            wd = r["taxable_withdrawal"]
            tax = r["taxable_withdrawal_tax"]
            eff = tax / wd if wd > 0 else 0
            if eff > 0.20:  # Even with 100% gains and 15% rate + NIIT, max ~18.8%
                results.append(("FAIL", "Capital gains tax rate",
                    f"Year {r['year']}: Taxable withdrawal ${wd:,.0f} taxed at {eff:.1%}. "
                    f"Max should be ~18.8% (15% LTCG + 3.8% NIIT). "
                    f"Are ordinary rates being applied to capital gains?"))
                failed += 1
                break
        else:
            results.append(("PASS", "Capital gains tax rate",
                "Taxable withdrawal tax rates within expected LTCG range"))
            passed += 1
    else:
        results.append(("SKIP", "Capital gains tax rate",
            "No taxable_withdrawal + taxable_withdrawal_tax fields in projections"))

    # 8. RMD enforcement check
    rmd_age_start = 73  # Default; would be 75 for born 1960+
    # Check if birth_year info is available
    birth_year_records = [r for r in projections if r.get("birth_year")]
    if birth_year_records:
        by = birth_year_records[0]["birth_year"]
        rmd_age_start = 75 if by >= 1960 else 73

    rmd_eligible = [r for r in projections
                    if r.get("george_age", r.get("retiree_age", 0)) >= rmd_age_start]
    if rmd_eligible:
        # Check that traditional withdrawals exist when there's a traditional balance
        trad_zero_wd = [r for r in rmd_eligible
                        if r.get("traditional_balance", 0) > 100_000
                        and r.get("traditional_withdrawal", 0) < 1_000]
        if trad_zero_wd:
            r = trad_zero_wd[0]
            results.append(("FAIL", "RMD enforcement",
                f"Age {r.get('george_age', r.get('retiree_age', '?'))}: "
                f"Traditional balance ${r.get('traditional_balance', 0):,.0f} but withdrawal "
                f"${r.get('traditional_withdrawal', 0):,.0f}. RMD is mandatory."))
            failed += 1
        else:
            results.append(("PASS", "RMD enforcement",
                "Traditional withdrawals present in all RMD-eligible years with balance"))
            passed += 1
    else:
        results.append(("SKIP", "RMD enforcement",
            "No records at RMD-eligible age found"))

    # 9. State tax check — verify it's not a flat 5% everywhere
    state_tax_records = [r for r in projections if r.get("state_tax") is not None]
    if state_tax_records:
        # Check for suspiciously uniform rate
        rates = []
        for r in state_tax_records:
            income = r.get("taxable_income", r.get("gross_salary", 0))
            if income > 0 and r["state_tax"] > 0:
                rates.append(r["state_tax"] / income)
        if rates and len(set(round(r, 4) for r in rates)) <= 2:
            # All the same rate — might be flat placeholder
            avg_rate = sum(rates) / len(rates)
            if 0.045 < avg_rate < 0.055:  # Suspiciously close to 5%
                results.append(("WARN", "State tax specificity",
                    f"State tax rate appears to be flat ~{avg_rate:.1%} across all years. "
                    f"Is this the user's actual state rate or a placeholder? "
                    f"Use real brackets from state-taxes.md."))
                failed += 1
            else:
                results.append(("PASS", "State tax specificity",
                    f"State tax rate {avg_rate:.1%} appears intentional (not a 5% placeholder)"))
                passed += 1
        else:
            results.append(("PASS", "State tax specificity",
                "State tax rates vary across income levels (progressive brackets in use)"))
            passed += 1
    else:
        results.append(("SKIP", "State tax specificity",
            "No state_tax field in projections"))

    # Summary
    print("=" * 70)
    print("MODEL VALIDATION RESULTS")
    print("=" * 70)
    for status, check, detail in results:
        icon = "✓" if status == "PASS" else ("✗" if status == "FAIL" else ("⚠" if status == "WARN" else "○"))
        print(f"\n{icon} [{status}] {check}")
        print(f"  {detail}")

    print(f"\n{'─' * 70}")
    print(f"Results: {passed} passed, {failed} failed/warned, {len(results)} total")

    if failed > 0:
        print("\n⚠ FIX THE FAILING CHECKS BEFORE PRESENTING RESULTS TO THE USER.")
        return False
    else:
        print("\n✓ All checks passed. Model appears sound.")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_model.py projections.json [retirement_year]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    # Handle both raw array and nested structure
    if isinstance(data, list):
        projections = data
    elif isinstance(data, dict):
        # Try common keys
        for key in ["recommended", "no_annuity", "results", "projections"]:
            if key in data:
                if isinstance(data[key], dict) and "results" in data[key]:
                    projections = data[key]["results"]
                elif isinstance(data[key], list):
                    projections = data[key]
                break
        else:
            print("ERROR: Could not find projection data in JSON. Expected array or dict with 'results' key.")
            sys.exit(1)

    ret_year = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    ok = validate(projections, retirement_year=ret_year)
    sys.exit(0 if ok else 1)
