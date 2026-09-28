#!/usr/bin/env python3
"""
CPF Retirement Account (RA) Cash Top-Up: Option 1 vs Option 2 Comparison

Option 1: $80,000 lump-sum deposit at start of Year 1
  - Tax relief: $8,000 in Year 1 only (remaining $72K generates zero tax benefit)
  - All $80K earns CPF RA interest at 4% p.a.

Option 2: $8,000/year for 10 years (deposits at start of each year)
  - Tax relief: $8,000 each year for 10 years = $80,000 total relief
  - Deposited funds earn CPF RA interest at 4% p.a.
  - Unused funds (remaining pot) earn 2.5% p.a. outside the RA

Both options start at age 55, over a 10-year horizon.
"""

import os
import sys
from datetime import datetime

# ==============================================================================
# Singapore residential progressive income tax brackets (YA 2024 onwards)
# ==============================================================================
# Source: IRAS – https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates
#
# Format: (lower_bound, upper_bound, rate)
# The marginal rate applies to income within each band.
# For the open-ended top bracket (> $1M), we use None as upper bound and
# represent it with $1,500,000 in comparisons.

TAX_BRACKETS = [
    (0,         20_000,   0.00),
    (20_000,    30_000,   0.02),
    (30_000,    40_000,   0.035),
    (40_000,    80_000,   0.07),
    (80_000,    120_000,  0.115),
    (120_000,   160_000,  0.15),
    (160_000,   200_000,  0.18),
    (200_000,   240_000,  0.19),
    (240_000,   280_000,  0.195),
    (280_000,   320_000,  0.20),
    (320_000,   500_000,  0.22),
    (500_000,   1_000_000, 0.23),
    (1_000_000, None,     0.24),  # > $1,000,000
]

# Bracket boundary values used as representative chargeable incomes
# For the open-ended top bracket, we use $1,500,000 as the representative income.
BRACKET_BOUNDARIES = [
    20_000, 30_000, 40_000, 80_000, 120_000, 160_000,
    200_000, 240_000, 280_000, 320_000, 500_000,
    1_000_000, 1_500_000,
]

# ==============================================================================
# compute_tax(chargeable_income, brackets)
# ==============================================================================
def compute_tax(chargeable_income, brackets):
    """
    Compute progressive income tax given chargeable income and bracket definitions.

    Args:
        chargeable_income: Total chargeable income (after reliefs).
        brackets: List of (lower_bound, upper_bound, rate) tuples.

    Returns:
        Total tax liability (rounded to 2 decimal places).
    """
    if chargeable_income <= 0:
        return 0.0

    tax = 0.0
    remaining = chargeable_income

    for lower, upper, rate in brackets:
        if remaining <= 0:
            break

        if upper is None:
            # Open-ended top bracket
            taxable = remaining
        else:
            band_width = upper - lower
            taxable = min(remaining, band_width)

        tax += taxable * rate
        remaining -= taxable

    return round(tax, 2)


# ==============================================================================
# compute_tax_savings(chargeable_income, relief_amount)
# ==============================================================================
def compute_tax_savings(chargeable_income, relief_amount):
    """
    Compute tax savings from a given relief amount using difference-of-taxes.

    The relief is clamped so that post-relief income never goes negative.

    Args:
        chargeable_income: Original chargeable income (before relief).
        relief_amount: Amount of tax relief.

    Returns:
        Tax savings = tax(before relief) - tax(after relief).
    """
    if chargeable_income <= 0:
        return 0.0

    # Clamp relief so post-relief income >= 0
    effective_relief = min(relief_amount, chargeable_income)
    after_relief = chargeable_income - effective_relief

    tax_before = compute_tax(chargeable_income, TAX_BRACKETS)
    tax_after = compute_tax(after_relief, TAX_BRACKETS)

    return round(tax_before - tax_after, 2)


# ==============================================================================
# compute_tax_savings_option1(chargeable_income)
# ==============================================================================
def compute_tax_savings_option1(chargeable_income):
    """
    Option 1: Single $8,000 relief in Year 1 only.
    Total savings = compute_tax_savings(chargeable_income, 8000).

    The lump sum of $80,000 only qualifies for the first year's $8K cap.
    """
    return compute_tax_savings(chargeable_income, 8_000)


# ==============================================================================
# compute_tax_savings_option2(chargeable_income)
# ==============================================================================
def compute_tax_savings_option2(chargeable_income):
    """
    Option 2: $8,000 relief each year for 10 years.
    Total = 10 * compute_tax_savings(chargeable_income, 8000).

    Assumes chargeable income is constant across all 10 years.
    """
    yearly_savings = compute_tax_savings(chargeable_income, 8_000)
    return round(yearly_savings * 10, 2)


# ==============================================================================
# simulate_option1(principal=80000, rate=0.04, years=10)
# ==============================================================================
def simulate_option1(principal=80_000, rate=0.04, years=10, starting_age=55):
    """
    Option 1: Deposit $80,000 at the start of Year 1. All funds earn CPF RA
    interest at 4% p.a., compounded at year-end. No further deposits.

    Returns:
        List of dicts with keys: year, age, deposit, interest, closing_balance.
    """
    results = []
    balance = principal

    for year in range(1, years + 1):
        deposit = principal if year == 1 else 0
        interest = balance * rate
        balance += interest
        results.append({
            "year": year,
            "age": starting_age + year - 1,
            "deposit": deposit,
            "interest": round(interest, 2),
            "closing_balance": round(balance, 2),
        })

    return results


# ==============================================================================
# simulate_option2(annual_deposit=8000, rate=0.04, outside_rate=0.025, years=10)
# ==============================================================================
def simulate_option2(annual_deposit=8_000, rate=0.04, outside_rate=0.025,
                     years=10, starting_age=55):
    """
    Option 2: Deposit $8,000 at the start of each year into the CPF RA.
    - Deposited funds earn CPF RA interest at 4% p.a.
    - Unused funds (remaining pot) earn 2.5% p.a. outside the RA.

    Each year:
      1. $8,000 is transferred from the outside pot to the RA (at year start).
      2. RA balance earns 4% interest (at year end).
      3. Remaining outside pot earns 2.5% interest (at year end).

    Returns:
        List of dicts with keys: year, age, deposit, ra_balance, ra_interest,
        outside_balance, outside_interest, total_value.
    """
    total_pot = annual_deposit * years  # $80,000
    results = []
    ra_balance = 0.0
    outside_pot = total_pot  # Start with full pot outside

    for year in range(1, years + 1):
        # Deposit at year start
        deposit = annual_deposit
        outside_pot -= deposit
        ra_balance += deposit

        # Interest at year end
        ra_interest = ra_balance * rate
        ra_balance += ra_interest

        outside_interest = outside_pot * outside_rate
        outside_pot += outside_interest

        total_value = ra_balance + outside_pot

        results.append({
            "year": year,
            "age": starting_age + year - 1,
            "deposit": deposit,
            "ra_balance": round(ra_balance, 2),
            "ra_interest": round(ra_interest, 2),
            "outside_balance": round(outside_pot, 2),
            "outside_interest": round(outside_interest, 2),
            "total_value": round(total_value, 2),
        })

    return results


# ==============================================================================
# Closed-form verification
# ==============================================================================
def verify_closed_form(opt1_results, opt2_results):
    """
    Verify simulated balances against closed-form formulas.

    Option 1 final balance:
        80000 * 1.04^10

    Option 2 (original, no outside earnings) RA balance only:
        8000 * ((1.04^10 - 1) / 0.04) * 1.04

    Option 2 with outside earnings:
        After 10 years, outside_pot = 0 (all deposited).
        RA balance = 8000 * ((1.04^10 - 1) / 0.04) * 1.04  (same annuity-due)
        Total value = RA balance + outside_balance
        But outside_balance compounds at 2.5% and depletes as deposits are made.

        Outside pot closed-form:
        Start: 80000
        Each year k (k=1..10): withdraw 8000, remaining earns 2.5%
        This is: 80000 * 1.025^10 - 8000 * sum_{k=1}^{10} 1.025^k
        = 80000 * 1.025^10 - 8000 * 1.025 * (1.025^10 - 1) / 0.025

    Asserts abs(simulated - closed_form) < 0.01 for each.
    """
    rate_ra = 0.04
    rate_out = 0.025
    years = 10

    # Option 1 closed form
    opt1_closed = 80_000 * (1 + rate_ra) ** years
    opt1_simulated = opt1_results[-1]["closing_balance"]
    diff1 = abs(opt1_simulated - opt1_closed)
    assert diff1 < 0.01, (
        f"Option 1 mismatch: simulated={opt1_simulated}, "
        f"closed_form={opt1_closed:.2f}, diff={diff1:.4f}"
    )

    # Option 2 RA balance closed form (annuity-due at 4%)
    opt2_ra_closed = 8_000 * (((1 + rate_ra) ** years - 1) / rate_ra) * (1 + rate_ra)
    opt2_ra_simulated = opt2_results[-1]["ra_balance"]
    diff2_ra = abs(opt2_ra_simulated - opt2_ra_closed)
    assert diff2_ra < 0.01, (
        f"Option 2 RA mismatch: simulated={opt2_ra_simulated}, "
        f"closed_form={opt2_ra_closed:.2f}, diff={diff2_ra:.4f}"
    )

    # Option 2 outside balance closed form
    # 80000 * 1.025^10 - 8000 * 1.025 * (1.025^10 - 1) / 0.025
    opt2_outside_closed = (80_000 * (1 + rate_out) ** years
                          - 8_000 * (1 + rate_out) * ((1 + rate_out) ** years - 1) / rate_out)
    opt2_outside_simulated = opt2_results[-1]["outside_balance"]
    diff2_out = abs(opt2_outside_simulated - opt2_outside_closed)
    assert diff2_out < 0.01, (
        f"Option 2 outside mismatch: simulated={opt2_outside_simulated}, "
        f"closed_form={opt2_outside_closed:.2f}, diff={diff2_out:.4f}"
    )

    return {
        "option1": {
            "simulated": opt1_simulated,
            "closed_form": round(opt1_closed, 2),
        },
        "option2_ra": {
            "simulated": opt2_ra_simulated,
            "closed_form": round(opt2_ra_closed, 2),
        },
        "option2_outside": {
            "simulated": opt2_outside_simulated,
            "closed_form": round(opt2_outside_closed, 2),
        },
        "option2_total": {
            "simulated": opt2_results[-1]["total_value"],
            "closed_form": round(opt2_ra_closed + opt2_outside_closed, 2),
        },
    }


# ==============================================================================
# Build comparison table
# ==============================================================================
def build_comparison_table(opt1_final, opt2_total_final):
    """
    For each bracket upper boundary, compute:
    - Chargeable income at that boundary
    - Option 1 final balance and tax savings
    - Option 2 total final value and tax savings
    - Net benefit (balance/value + tax savings) for each option
    - Difference (Option 2 net benefit - Option 1 net benefit)

    Returns list of dicts.
    """
    table = []
    for income in BRACKET_BOUNDARIES:
        ts1 = compute_tax_savings_option1(income)
        ts2 = compute_tax_savings_option2(income)

        net1 = opt1_final + ts1
        net2 = opt2_total_final + ts2
        difference = round(net2 - net1, 2)

        # Determine which option wins
        if net2 > net1:
            winner = "Option 2"
        elif net1 > net2:
            winner = "Option 1"
        else:
            winner = "Tie"

        # Marginal rate at this income level
        marginal_rate = 0.0
        for lower, upper, rate in TAX_BRACKETS:
            if upper is None:
                if income >= lower:
                    marginal_rate = rate
            else:
                if lower <= income < upper:
                    marginal_rate = rate
                elif income == upper:
                    # At the boundary, next bracket's rate applies
                    marginal_rate = rate

        table.append({
            "income": income,
            "marginal_rate": marginal_rate,
            "opt1_balance": opt1_final,
            "opt1_tax_savings": ts1,
            "opt1_net": round(net1, 2),
            "opt2_total": opt2_total_final,
            "opt2_tax_savings": ts2,
            "opt2_net": round(net2, 2),
            "difference": difference,
            "winner": winner,
        })

    return table


# ==============================================================================
# Generate Markdown report
# ==============================================================================
def generate_report(opt1_results, opt2_results, verification, comparison):
    """
    Generate a comprehensive Markdown report.
    """
    lines = []

    lines.append("# CPF RA Cash Top-Up: Option 1 vs Option 2 Comparison\n")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    # ------------------------------------------------------------------
    # (a) Assumptions
    # ------------------------------------------------------------------
    lines.append("## 1. Assumptions\n")
    lines.append("| # | Assumption | Details |")
    lines.append("|---|-----------|---------|")
    lines.append("| 1 | CPF RA interest rate | 4% p.a., compounded at year-end |")
    lines.append("| 2 | Outside interest rate (Option 2) | 2.5% p.a. on unused funds (remaining pot) |")
    lines.append("| 3 | Tax relief cap | $8,000 per year of assessment (YA) for self top-up |")
    lines.append("| 4 | CPF RA cap | FRS = $220,400; ERS = $440,800 (deposits assumed within remaining cap room) |")
    lines.append("| 5 | Carry-forward | Unused relief CANNOT be carried forward |")
    lines.append("| 6 | Discounting | No discounting applied (nominal comparison) |")
    lines.append("| 7 | Chargeable income | Constant across all 10 years |")
    lines.append("| 8 | Starting age | 55 years old |")
    lines.append("")

    # ------------------------------------------------------------------
    # (b) Data Sources
    # ------------------------------------------------------------------
    lines.append("## 2. Data Sources\n")
    lines.append("| Source | URL |")
    lines.append("|--------|-----|")
    lines.append("| IRAS Individual Income Tax Rates | https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates |")
    lines.append("| IRAS CPF Cash Top-up Relief | https://www.iras.gov.sg/taxes/individuals/resident-individuals/rates-and-reliefs/cash-top-up-relief |")
    lines.append("| CPF RA Full Retirement Sum | https://www.cpf.gov.sg/education/cpf-101/how-much-i-need-for-retirement/retirement-adequacy/full-retirement-sum |")
    lines.append("")

    # ------------------------------------------------------------------
    # (c) Tax brackets table
    # ------------------------------------------------------------------
    lines.append("## 3. Singapore Progressive Income Tax Brackets (YA 2024 onwards)\n")
    lines.append("| Income Band (SGD) | Rate |")
    lines.append("|-------------------|------|")
    for lower, upper, rate in TAX_BRACKETS:
        if upper is None:
            band_str = f"${lower:,.0f} and above"
        else:
            band_str = f"${lower:,.0f} \u2013 ${upper:,.0f}"
        lines.append(f"| {band_str} | {rate * 100:.1f}% |")
    lines.append("")

    # ------------------------------------------------------------------
    # (d) Year-by-year balance tables
    # ------------------------------------------------------------------
    lines.append("## 4. Year-by-Year Balance Comparison\n")

    lines.append("### Option 1: $80,000 Lump Sum (Year 1)\n")
    lines.append("| Year | Age | Deposit | Interest (4%) | Closing Balance |")
    lines.append("|------|-----|---------|---------------|----------------|")
    for row in opt1_results:
        lines.append(
            f"| {row['year']} | {row['age']} | "
            f"${row['deposit']:,.2f} | "
            f"${row['interest']:,.2f} | "
            f"${row['closing_balance']:,.2f} |"
        )
    lines.append("")

    lines.append("### Option 2: $8,000/Year for 10 Years (unused funds earn 2.5%)\n")
    lines.append("| Year | Age | Deposit | RA Balance (4%) | Outside Pot (2.5%) | Total Value |")
    lines.append("|------|-----|---------|-----------------|--------------------|-------------|")
    for row in opt2_results:
        lines.append(
            f"| {row['year']} | {row['age']} | "
            f"${row['deposit']:,.2f} | "
            f"${row['ra_balance']:,.2f} | "
            f"${row['outside_balance']:,.2f} | "
            f"${row['total_value']:,.2f} |"
        )
    lines.append("")

    # ------------------------------------------------------------------
    # (e) Closed-form verification
    # ------------------------------------------------------------------
    lines.append("## 5. Closed-Form Verification\n")
    lines.append(f"- **Option 1**: Simulated = ${verification['option1']['simulated']:,.2f}, "
                 f"Formula = ${verification['option1']['closed_form']:,.2f} \u2713\n")
    lines.append(f"- **Option 2 RA balance**: Simulated = ${verification['option2_ra']['simulated']:,.2f}, "
                 f"Formula = ${verification['option2_ra']['closed_form']:,.2f} \u2713\n")
    lines.append(f"- **Option 2 outside pot**: Simulated = ${verification['option2_outside']['simulated']:,.2f}, "
                 f"Formula = ${verification['option2_outside']['closed_form']:,.2f} \u2713\n")
    lines.append(f"- **Option 2 total value**: Simulated = ${verification['option2_total']['simulated']:,.2f}, "
                 f"Formula = ${verification['option2_total']['closed_form']:,.2f} \u2713\n")
    lines.append("")

    # ------------------------------------------------------------------
    # (f) Per-bracket comparison table
    # ------------------------------------------------------------------
    lines.append("## 6. Per-Bracket Comparison\n")
    lines.append("Net benefit = Final value (RA + outside pot) + Total tax savings over 10 years.\n")
    lines.append("| Chargeable Income | Marginal Rate | Opt 1 Balance | Opt 1 Tax Savings | Opt 1 Net | Opt 2 Total Value | Opt 2 Tax Savings | Opt 2 Net | Difference (2\u22121) | Winner |")
    lines.append("|-------------------|--------------|--------------|-----------------|----------|----------------|-----------------|----------|-----------------|--------|")
    for row in comparison:
        lines.append(
            f"| ${row['income']:,.0f} | {row['marginal_rate']*100:.1f}% | "
            f"${row['opt1_balance']:,.2f} | ${row['opt1_tax_savings']:,.2f} | "
            f"${row['opt1_net']:,.2f} | "
            f"${row['opt2_total']:,.2f} | ${row['opt2_tax_savings']:,.2f} | "
            f"${row['opt2_net']:,.2f} | "
            f"${row['difference']:,.2f} | {row['winner']} |"
        )
    lines.append("")

    # ------------------------------------------------------------------
    # (g) Conclusion
    # ------------------------------------------------------------------
    lines.append("## 7. Conclusion\n")

    # Analyze winners
    opt1_wins = [r for r in comparison if r["winner"] == "Option 1"]
    opt2_wins = [r for r in comparison if r["winner"] == "Option 2"]
    ties = [r for r in comparison if r["winner"] == "Tie"]

    if opt2_wins:
        incomes = opt2_wins
        lines.append(f"**Option 2 wins at {len(opt2_wins)} income level(s):** "
                     f"${min(r['income'] for r in incomes):,.0f} \u2013 "
                     f"${max(r['income'] for r in incomes):,.0f}.\n")

    if opt1_wins:
        incomes = opt1_wins
        lines.append(f"**Option 1 wins at {len(opt1_wins)} income level(s):** "
                     f"${min(r['income'] for r in incomes):,.0f} \u2013 "
                     f"${max(r['income'] for r in incomes):,.0f}.\n")

    if ties:
        lines.append(f"**Tie at {len(ties)} income level(s).**\n")

    opt1_final = opt1_results[-1]['closing_balance']
    opt2_final = opt2_results[-1]['total_value']
    lines.append("---\n")
    if opt2_final > opt1_final:
        lines.append(f"**Key insight:** With unused funds earning 2.5% outside the RA, "
                     f"Option 2 now produces a higher total value (${opt2_final:,.2f} vs "
                     f"${opt1_final:,.2f}). Option 2 also earns more total tax savings "
                     f"($8K relief \u00d7 10 years). Option 2 wins at higher marginal "
                     f"tax brackets where the tax savings advantage is greatest.\n")
    else:
        lines.append(f"**Key insight:** Even with unused funds earning 2.5% outside the RA, "
                     f"Option 1 still produces a higher final CPF balance (${opt1_final:,.2f} vs "
                     f"${opt2_final:,.2f}) because the lump sum earns 4% from Year 1. "
                     f"Option 2 earns greater total tax savings ($8K relief \u00d7 10 years). "
                     f"The winner depends on marginal tax rate.\n")

    return "\n".join(lines)


# ==============================================================================
# main()
# ==============================================================================
def main():
    print("=" * 70)
    print("CPF RA Cash Top-Up: Option 1 vs Option 2 Comparison")
    print("=" * 70)

    # Run simulations
    print("\n[1] Running Option 1 simulation ($80K lump sum, 4% RA interest)...")
    opt1 = simulate_option1()
    print(f"     Final balance: ${opt1[-1]['closing_balance']:,.2f}")

    print("\n[2] Running Option 2 simulation ($8K/yr x 10, 4% RA + 2.5% outside)...")
    opt2 = simulate_option2()
    print(f"     RA balance:     ${opt2[-1]['ra_balance']:,.2f}")
    print(f"     Outside pot:    ${opt2[-1]['outside_balance']:,.2f}")
    print(f"     Total value:    ${opt2[-1]['total_value']:,.2f}")

    # Closed-form verification
    print("\n[3] Verifying closed-form formulas...")
    verification = verify_closed_form(opt1, opt2)
    print(f"     Option 1: ${verification['option1']['simulated']:,.2f} == "
          f"${verification['option1']['closed_form']:,.2f} \u2713")
    print(f"     Option 2 RA: ${verification['option2_ra']['simulated']:,.2f} == "
          f"${verification['option2_ra']['closed_form']:,.2f} \u2713")
    print(f"     Option 2 outside: ${verification['option2_outside']['simulated']:,.2f} == "
          f"${verification['option2_outside']['closed_form']:,.2f} \u2713")
    print(f"     Option 2 total: ${verification['option2_total']['simulated']:,.2f} == "
          f"${verification['option2_total']['closed_form']:,.2f} \u2713")

    # Tax savings at key brackets
    print("\n[4] Computing tax savings across brackets...")
    opt1_final = opt1[-1]['closing_balance']
    opt2_total_final = opt2[-1]['total_value']
    for income in [0, 20_000, 100_000, 320_000, 500_000, 1_000_000]:
        ts1 = compute_tax_savings_option1(income)
        ts2 = compute_tax_savings_option2(income)
        print(f"     Income ${income:>12,}: Opt1 savings ${ts1:>8,.2f} | "
              f"Opt2 savings ${ts2:>8,.2f}")

    # Build comparison table
    print("\n[5] Building comparison table...")
    comparison = build_comparison_table(opt1_final, opt2_total_final)

    # Determine overall winner distribution
    opt1_count = sum(1 for r in comparison if r["winner"] == "Option 1")
    opt2_count = sum(1 for r in comparison if r["winner"] == "Option 2")
    tie_count = sum(1 for r in comparison if r["winner"] == "Tie")

    # Generate report
    print(f"\n[6] Generating report...")
    report = generate_report(opt1, opt2, verification, comparison)
    output_dir = os.path.expanduser("~/workspace/cpf-ra-comparison")
    report_path = os.path.join(output_dir, "cpf_ra_comparison_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"     Report written ({len(report)} chars) -> {report_path}")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Option 1 final CPF balance:     ${opt1_final:>12,.2f}")
    print(f"  Option 2 total value (RA + out): ${opt2_total_final:>12,.2f}")
    balance_diff = opt2_total_final - opt1_final
    if balance_diff > 0:
        print(f"  Value advantage (Opt 2):         ${balance_diff:>12,.2f}")
    else:
        print(f"  Balance advantage (Opt 1):       ${abs(balance_diff):>12,.2f}")
    print()
    print(f"  Winners: Option 1 = {opt1_count}, Option 2 = {opt2_count}, Tie = {tie_count}")
    if opt2_count > opt1_count:
        print(f"\n  Option 2 wins at more income levels.")
    else:
        print(f"\n  Option 1 wins at all bracket levels.")
    print()
    print("Done.")


if __name__ == "__main__":
    main()
