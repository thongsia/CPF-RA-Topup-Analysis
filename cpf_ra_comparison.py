#!/usr/bin/env python3
"""
CPF Retirement Account (RA) Cash Top-Up: Option 1 vs Option 2 Comparison.

Option 1: Lump-sum deposit at the start of Year 1.
Option 2: Fixed annual deposits for N years; unused funds earn an outside rate.

Rules implemented (verified against IRAS / CPF Board, see research_findings.md):
  1. RA interest for members aged 55+ is tiered on the combined SA/RA balance:
       6% on the first $30,000, 5% on the next $30,000, 4% on the rest
     (4% base rate + 2%/1% "additional interest").  The tiers apply to the
     member's TOTAL balance, so if the existing RA balance already exceeds
     $60,000 (true for any standard 55+ member, minimum BRS = $110,200),
     all top-up dollars earn a flat 4% and the model reduces to the
     flat-rate case.
  2. CPF Cash Top-up Relief (max $8,000/YA for self) is only granted for the
     portion of a top-up that fills the RA up to the Full Retirement Sum
     (FRS).  Top-ups above FRS (up to the Enhanced Retirement Sum, ERS)
     earn interest but generate NO tax relief.  Unused relief cannot be
     carried forward.

Usage:
    python3 cpf_ra_comparison.py                      # default scenario
                                                      # (existing RA at FRS 2026)
    python3 cpf_ra_comparison.py --ra-balance 140400  # your own RA balance

Writes cpf_ra_comparison_report.md next to the script (override with
--out-dir) and prints a summary plus self-verification checks to stdout.
See --help for all options.
"""

import argparse
import os

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

# Representative chargeable incomes: each bracket upper boundary, plus
# $1.5M as a representative point inside the open-ended top bracket.
BRACKET_BOUNDARIES = [
    20_000, 30_000, 40_000, 80_000, 120_000, 160_000,
    200_000, 240_000, 280_000, 320_000, 500_000,
    1_000_000, 1_500_000,
]

# 55+ additional-interest tiers: (band_width, rate).  None = open-ended.
TIERS_55 = [(30_000, 0.06), (30_000, 0.05), (None, 0.04)]

# Known tax liabilities (cumulative at bracket boundaries), from the IRAS
# bracket table — used as checkpoint values in verification.
TAX_CHECKPOINTS = {
    20_000: 0.0, 30_000: 200.0, 40_000: 550.0, 80_000: 3_350.0,
    120_000: 7_950.0, 160_000: 13_950.0, 200_000: 21_150.0,
    240_000: 28_750.0, 280_000: 36_550.0, 320_000: 44_550.0,
    500_000: 84_150.0, 1_000_000: 199_150.0,
}


# ==============================================================================
# Tax
# ==============================================================================
def compute_tax(chargeable_income, brackets=None):
    """Progressive income tax on chargeable income."""
    if brackets is None:
        brackets = TAX_BRACKETS
    if chargeable_income <= 0:
        return 0.0
    tax = 0.0
    remaining = chargeable_income
    for lower, upper, rate in brackets:
        if remaining <= 0:
            break
        if upper is None:
            taxable = remaining
        else:
            taxable = min(remaining, upper - lower)
        tax += taxable * rate
        remaining -= taxable
    return round(tax, 2)


def compute_tax_savings(chargeable_income, relief_amount):
    """Tax saved by `relief_amount` of relief at a given chargeable income.

    Savings = tax(income) - tax(income - relief), with the relief clamped so
    post-relief income never goes negative.
    """
    if chargeable_income <= 0 or relief_amount <= 0:
        return 0.0
    effective = min(relief_amount, chargeable_income)
    return round(
        compute_tax(chargeable_income) - compute_tax(chargeable_income - effective),
        2,
    )


def marginal_rate(income, brackets=None):
    """Marginal rate at exactly `income` (income at a boundary pays the
    next bracket's rate on the next dollar)."""
    if brackets is None:
        brackets = TAX_BRACKETS
    rate = 0.0
    for lower, upper, r in brackets:
        if upper is None:
            if income >= lower:
                rate = r
        elif lower <= income < upper:
            rate = r
    return rate


# ==============================================================================
# Interest (55+ tiers)
# ==============================================================================
def tiered_interest(balance, tiers=None):
    """One year's interest on `balance` under the 55+ tier structure:
    6% on first $30k, 5% on next $30k, 4% on the rest."""
    if tiers is None:
        tiers = TIERS_55
    interest = 0.0
    remaining = balance
    for width, rate in tiers:
        if remaining <= 0:
            break
        taxed = remaining if width is None else min(remaining, width)
        interest += taxed * rate
        remaining -= taxed
    return interest


def split_tiers(balance, tiers=None):
    """Split `balance` across tiers in fill order: (b1, b2, b3...)."""
    if tiers is None:
        tiers = TIERS_55
    parts, remaining = [], balance
    for width, _rate in tiers:
        part = remaining if width is None else min(remaining, width)
        parts.append(part)
        remaining -= part
    return parts


def bucket_simulation(existing, deposits_by_year, years, tiers=None):
    """Independent cross-check of the tiered simulation using explicit
    tier buckets with re-balancing after each year's interest.

    Deposits fill the tiers in order (6% band first, then 5%, then 4%).
    """
    if tiers is None:
        tiers = TIERS_55
    rates = [r for _w, r in tiers]
    caps = [w for w, _r in tiers]
    buckets = split_tiers(existing, tiers)

    def add(dep):
        for i in range(len(buckets)):
            if dep <= 0:
                break
            room = caps[i] - buckets[i] if caps[i] is not None else dep
            put = min(dep, room)
            buckets[i] += put
            dep -= put

    for k in range(years):
        add(deposits_by_year[k])
        for i in range(len(buckets)):
            buckets[i] *= (1 + rates[i])
        # re-balance into the tier structure for next year's interest
        buckets = split_tiers(sum(buckets), tiers)
    return round(sum(buckets), 2)


# ==============================================================================
# Simulations
# ==============================================================================
def simulate_option1(existing, lump, years=10, starting_age=55, tiers=None):
    """Option 1: `lump` deposited at start of Year 1 on top of `existing` RA
    balance.  Tiered interest on the total each year.

    Returns list of dicts: year, age, deposit, interest, ra_total,
    topup_value (the part of the total attributable to the top-up).
    """
    if tiers is None:
        tiers = TIERS_55
    results = []
    ra = float(existing)
    existing_path = float(existing)  # same balance with no top-up
    for year in range(1, years + 1):
        deposit = lump if year == 1 else 0
        ra += deposit
        interest = tiered_interest(ra, tiers)
        ra += interest
        existing_path += tiered_interest(existing_path, tiers)
        results.append({
            "year": year,
            "age": starting_age + year - 1,
            "deposit": deposit,
            "interest": round(interest, 2),
            "ra_total": round(ra, 2),
            # incremental value of the top-up = total minus the existing
            # balance's own growth
            "topup_value": round(ra - existing_path, 2),
        })
    return results


def simulate_option2(existing, annual, years=10, outside_rate=0.025,
                     starting_age=55, tiers=None):
    """Option 2: `annual` deposited at the start of each year on top of
    `existing` RA balance.  Tiered interest on the RA; the unused outside
    pot (total top-up funds minus amounts already deposited) earns
    `outside_rate` on the remainder after each year's deposit.

    Returns list of dicts: year, age, deposit, ra_total, ra_interest,
    topup_value, outside_balance, outside_interest, total_value.
    """
    if tiers is None:
        tiers = TIERS_55
    total_funds = annual * years
    results = []
    ra = float(existing)
    existing_path = float(existing)  # same balance with no top-up
    outside = float(total_funds)
    for year in range(1, years + 1):
        deposit = annual
        outside -= deposit
        ra += deposit
        ra_interest = tiered_interest(ra, tiers)
        ra += ra_interest
        existing_path += tiered_interest(existing_path, tiers)
        outside_interest = outside * outside_rate
        outside += outside_interest
        results.append({
            "year": year,
            "age": starting_age + year - 1,
            "deposit": deposit,
            "ra_total": round(ra, 2),
            "ra_interest": round(ra_interest, 2),
            # incremental value of the top-up = RA top-up portion + outside pot
            "topup_value": round(ra - existing_path + outside, 2),
            "outside_balance": round(outside, 2),
            "outside_interest": round(outside_interest, 2),
            "total_value": round(ra + outside, 2),
        })
    return results


# ==============================================================================
# Tax-relief eligibility (FRS cap)
# ==============================================================================
def frs_headroom(ra_balance, frs):
    """Amount of further top-up that still attracts tax relief
    (= FRS - RA balance, floored at 0)."""
    return max(0.0, frs - ra_balance)


def option1_relief_amount(lump, headroom):
    """Relief-eligible amount for the Option 1 lump sum, subject to the
    $8,000/YA cap."""
    return min(8_000, lump, headroom)


def option2_relief_schedule(annual, headroom, years):
    """Per-year relief-eligible amounts for Option 2: $annual each year
    until the FRS headroom is exhausted, then 0.  Capped at $8,000/yr."""
    schedule = []
    remaining = headroom
    for _ in range(years):
        amt = min(8_000, annual, remaining)
        schedule.append(amt)
        remaining -= amt
    return schedule


def option1_tax_savings(income, relief_amount):
    return compute_tax_savings(income, relief_amount)


def option2_tax_savings(income, schedule):
    return round(sum(compute_tax_savings(income, amt) for amt in schedule), 2)


# ==============================================================================
# Verification
# ==============================================================================
def verify(opt1, opt2, existing, lump, annual, years, outside_rate):
    """Independent checks.  Returns a list of (label, ok, detail)."""
    checks = []

    # 1. Tax checkpoints against the published IRAS cumulative table.
    for income, expected in TAX_CHECKPOINTS.items():
        got = compute_tax(income)
        checks.append((
            f"tax(${income:,}) == ${expected:,.2f}",
            abs(got - expected) < 0.005,
            f"got ${got:,.2f}",
        ))

    # 2. Tiered-interest boundary values (hand-computed).
    for bal, expected in [
        (0, 0.0), (30_000, 1_800.0), (60_000, 3_300.0),
        (100_000, 3_300 + 1_600.0), (220_400, 1_800.0 + 1_500.0 + 6_416.0),
    ]:
        got = tiered_interest(bal)
        checks.append((
            f"tiered_interest(${bal:,}) == ${expected:,.2f}",
            abs(got - expected) < 0.005,
            f"got ${got:,.2f}",
        ))

    # 3. When the existing balance already fills the preferential tiers
    #    (>= $60,000), every top-up dollar grows at a flat 4%: the
    #    top-up value has a clean closed form.
    if existing >= 60_000:
        topup1_closed = lump * (1.04 ** years)
        topup2_closed = (annual * (((1.04 ** years - 1) / 0.04) * 1.04)
                         + annual * years * (1 + outside_rate) ** years
                         - annual * (1 + outside_rate)
                           * ((1 + outside_rate) ** years - 1) / outside_rate)
        sim1 = opt1[-1]["topup_value"]
        sim2 = opt2[-1]["topup_value"]
        checks.append((
            "Option 1 top-up value closed form (flat 4% tier)",
            abs(sim1 - topup1_closed) < 0.01,
            f"sim ${sim1:,.2f} vs formula ${topup1_closed:,.2f}",
        ))
        checks.append((
            "Option 2 top-up value closed form (flat 4% + outside rate)",
            abs(sim2 - topup2_closed) < 0.01,
            f"sim ${sim2:,.2f} vs formula ${topup2_closed:,.2f}",
        ))

    # 4. Independent bucketed cross-check of the full tiered simulation
    #    (explicit tier buckets, re-balanced after each year's interest).
    sim1 = opt1[-1]["ra_total"]
    bkt1 = bucket_simulation(existing, [lump] + [0] * (years - 1), years)
    sim2_ra = opt2[-1]["ra_total"]
    bkt2 = bucket_simulation(existing, [annual] * years, years)
    checks.append((
        "Option 1 tiered bucket cross-check",
        abs(sim1 - bkt1) < 0.01,
        f"sim ${sim1:,.2f} vs buckets ${bkt1:,.2f}",
    ))
    checks.append((
        "Option 2 tiered bucket cross-check",
        abs(sim2_ra - bkt2) < 0.01,
        f"sim ${sim2_ra:,.2f} vs buckets ${bkt2:,.2f}",
    ))

    return checks


# ==============================================================================
# Comparison
# ==============================================================================
def build_comparison_table(opt1_final, opt2_total_final, relief1, schedule2):
    """Per-bracket net-benefit table for the chosen scenario.

    net = final value (RA total + outside pot) + total tax savings over N years.
    """
    table = []
    for income in BRACKET_BOUNDARIES:
        ts1 = option1_tax_savings(income, relief1)
        ts2 = option2_tax_savings(income, schedule2)
        net1 = opt1_final + ts1
        net2 = opt2_total_final + ts2
        diff = round(net2 - net1, 2)
        if net2 > net1:
            winner = "Option 2"
        elif net1 > net2:
            winner = "Option 1"
        else:
            winner = "Tie"
        table.append({
            "income": income,
            "marginal_rate": marginal_rate(income),
            "opt1_final": opt1_final,
            "opt1_tax_savings": ts1,
            "opt1_net": round(net1, 2),
            "opt2_total": opt2_total_final,
            "opt2_tax_savings": ts2,
            "opt2_net": round(net2, 2),
            "difference": diff,
            "winner": winner,
        })
    return table


def crossover_income(opt1_final, opt2_total_final, relief1, schedule2,
                     income_max=5_000_000):
    """Income above which Option 2 wins, or None if Option 1 wins at all
    incomes.  net2-net1 is non-decreasing in income, so bisection applies.
    """
    def diff(income):
        return ((opt2_total_final + option2_tax_savings(income, schedule2))
                - (opt1_final + option1_tax_savings(income, relief1)))

    if diff(income_max) <= 0:
        return None
    lo, hi = 0.0, income_max
    for _ in range(200):
        mid = (lo + hi) / 2
        if diff(mid) <= 0:
            lo = mid
        else:
            hi = mid
    return lo


def headroom_sensitivity(lump, annual, years, frs, ra_balance, outside_rate,
                         tiers=None, starting_age=55):
    """Crossover income for each FRS-headroom level (RA balance = FRS - G).

    Returns list of dicts: headroom, ra_balance, opt1_final, opt2_total,
    balance_gap, relief_years_opt2, crossover (None = Option 1 wins at all
    incomes).
    """
    rows = []
    for g in range(0, 80_001, 8_000):
        ra = frs - g
        if ra < 0:
            break
        sim1 = simulate_option1(ra, lump, years, starting_age, tiers)
        sim2 = simulate_option2(ra, annual, years, outside_rate,
                                starting_age, tiers)
        o1 = sim1[-1]["ra_total"]
        o2 = sim2[-1]["total_value"]
        r1 = option1_relief_amount(lump, g)
        sched = option2_relief_schedule(annual, g, years)
        rows.append({
            "headroom": g,
            "ra_balance": ra,
            "opt1_final": o1,
            "opt2_total": o2,
            "balance_gap": round(o1 - o2, 2),
            "relief_years_opt2": sum(1 for a in sched if a > 0),
            "crossover": crossover_income(o1, o2, r1, sched),
        })
    return rows


def outside_rate_sensitivity(existing, lump, annual, years, tiers=None,
                             starting_age=55,
                             rates=(0.0, 0.01, 0.02, 0.025, 0.03, 0.04, 0.05),
                             search_hi=0.20, tol=1e-6):
    """Option 2's total value for several assumed outside rates, plus the
    exact outside rate at which the two options tie (bisection).

    The gap is monotonically decreasing in the outside rate: higher outside
    rates grow Option 2's parked funds while Option 1 is unaffected.  Returns
    (rows, crossover) where crossover is None if Option 2 never catches up
    below search_hi.
    """
    opt1_final = simulate_option1(existing, lump, years,
                                  starting_age, tiers=tiers)[-1]["ra_total"]

    def opt2_total(r):
        return simulate_option2(existing, annual, years, r,
                                starting_age, tiers=tiers)[-1]["total_value"]

    def gap(r):
        return opt1_final - opt2_total(r)

    rows = [{"outside_rate": r, "opt2_total": opt2_total(r),
             "balance_gap": round(opt1_final - opt2_total(r), 2)}
            for r in rates]

    crossover = None
    if gap(search_hi) <= 0:  # Option 2 catches up inside the search range
        if gap(0.0) <= 0:
            crossover = 0.0
        else:
            lo, hi = 0.0, search_hi
            while hi - lo > tol:
                mid = (lo + hi) / 2
                if gap(mid) > 0:
                    lo = mid
                else:
                    hi = mid
            crossover = (lo + hi) / 2
    return rows, crossover


# ==============================================================================
# Report
# ==============================================================================
def generate_report(cfg, opt1, opt2, checks, comparison, sensitivity,
                    rate_rows=None, rate_crossover=None):
    frs = cfg["frs"]
    ra = cfg["ra_balance"]
    headroom = frs_headroom(ra, frs)
    lines = []
    lines.append("# CPF RA Cash Top-Up: Option 1 vs Option 2 Comparison\n")
    lines.append(f"*Scenario: existing RA balance ${ra:,.0f} "
                 f"(FRS ${frs:,.0f}, headroom to FRS ${headroom:,.0f})*\n")

    lines.append("## 1. Assumptions\n")
    lines.append("| # | Assumption | Details |")
    lines.append("|---|-----------|---------|")
    lines.append(f"| 1 | Existing RA balance | ${ra:,.0f} |")
    tier_note = ("Top-up dollars fall in the flat 4% tier (existing balance "
                 "already fills the preferential tiers)."
                 if ra >= 60_000 else "Top-up dollars fill the 6%/5% tiers.")
    lines.append(f"| 2 | RA interest (age 55+) | Tiered: 6% on first $30,000, 5% on next $30,000, 4% on the rest of the combined SA/RA balance (4% base + 2%/1% additional interest). {tier_note} |")
    lines.append(f"| 3 | Outside interest (Option 2 unused funds) | {cfg['outside_rate'] * 100:.1f}% p.a. |")
    lines.append("| 4 | Tax relief cap | $8,000/YA for self top-up |")
    lines.append(f"| 5 | Relief eligibility | Only the portion of a top-up that fills the RA up to FRS (${frs:,.0f}) attracts relief; top-ups above FRS (up to ERS ${cfg['ers']:,.0f}) earn interest but NO relief |")
    lines.append("| 6 | Carry-forward | Unused relief CANNOT be carried forward |")
    lines.append("| 7 | Discounting | None (nominal comparison) |")
    lines.append(f"| 8 | Chargeable income | Constant across all {cfg['years']} years |")
    lines.append(f"| 9 | Starting age | {cfg['starting_age']} |")
    lines.append("")

    lines.append("## 2. Data Sources\n")
    lines.append("| Source | URL |")
    lines.append("|--------|-----|")
    lines.append("| IRAS Individual Income Tax Rates | https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates |")
    lines.append("| IRAS CPF Cash Top-up Relief (incl. FRS limit on relief) | https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-reliefs-rebates-and-deductions/tax-reliefs/central-provident-fund-(cpf)-cash-top-up-relief |")
    lines.append("| CPF Board RA top-ups (ERS cap, additional interest) | https://www.cpf.gov.sg/member/growing-your-savings/saving-more-with-cpf/top-up-to-enjoy-higher-retirement-payouts |")
    lines.append("")

    lines.append("## 3. Singapore Progressive Income Tax Brackets (YA 2024 onwards)\n")
    lines.append("| Income Band (SGD) | Rate |")
    lines.append("|-------------------|------|")
    for lower, upper, rate in TAX_BRACKETS:
        band = f"${lower:,} and above" if upper is None else f"${lower:,} – ${upper:,}"
        lines.append(f"| {band} | {rate * 100:.1f}% |")
    lines.append("")

    lines.append("## 4. Year-by-Year Balance Comparison\n")
    lines.append("RA totals include the existing balance; 'top-up value' is the part attributable to the new funds.\n")
    lines.append(f"### Option 1: ${cfg['lump']:,.0f} lump sum (Year 1)\n")
    lines.append("| Year | Age | Deposit | Interest | RA Total | Top-up Value |")
    lines.append("|------|-----|---------|----------|----------|--------------|")
    for row in opt1:
        lines.append(f"| {row['year']} | {row['age']} | ${row['deposit']:,.2f} | "
                     f"${row['interest']:,.2f} | ${row['ra_total']:,.2f} | ${row['topup_value']:,.2f} |")
    lines.append("")
    lines.append(f"### Option 2: ${cfg['annual']:,.0f}/year for {cfg['years']} years "
                 f"(unused funds earn {cfg['outside_rate'] * 100:.1f}%)\n")
    lines.append("| Year | Age | Deposit | RA Total | Outside Pot | Total Value |")
    lines.append("|------|-----|---------|----------|-------------|-------------|")
    for row in opt2:
        lines.append(f"| {row['year']} | {row['age']} | ${row['deposit']:,.2f} | "
                     f"${row['ra_total']:,.2f} | ${row['outside_balance']:,.2f} | ${row['total_value']:,.2f} |")
    lines.append("")

    lines.append("## 5. Verification\n")
    for label, ok, detail in checks:
        lines.append(f"- {'PASS' if ok else 'FAIL'}: {label} — {detail}")
    lines.append("")

    lines.append("## 6. Per-Bracket Comparison (chosen scenario)\n")
    lines.append("Net benefit = final value (RA total + outside pot) + total tax savings. "
                 "Figure `net_benefit.png` (Figure 1 in the README) plots these "
                 "net-benefit curves by chargeable income.\n")
    lines.append("| Chargeable Income | Marginal Rate | Opt 1 Final | Opt 1 Tax Savings | Opt 1 Net | "
                 "Opt 2 Total | Opt 2 Tax Savings | Opt 2 Net | Difference (2−1) | Winner |")
    lines.append("|-------------------|--------------|-------------|-------------------|-----------|"
                 "-------------|-------------------|-----------|------------------|--------|")
    for row in comparison:
        lines.append(
            f"| ${row['income']:,.0f} | {row['marginal_rate'] * 100:.1f}% | "
            f"${row['opt1_final']:,.2f} | ${row['opt1_tax_savings']:,.2f} | "
            f"${row['opt1_net']:,.2f} | ${row['opt2_total']:,.2f} | "
            f"${row['opt2_tax_savings']:,.2f} | ${row['opt2_net']:,.2f} | "
            f"${row['difference']:,.2f} | {row['winner']} |")
    lines.append("")

    lines.append("## 7. Sensitivity: Crossover by FRS Headroom\n")
    lines.append("How the winner changes with existing RA balance "
                 "(headroom G = FRS − RA, i.e. how much further top-up still attracts relief). "
                 "Figure `crossover_by_headroom.png` (Figure 2 in the README) plots the "
                 "break-even chargeable income from the table below as a function of "
                 "FRS headroom.\n")
    lines.append("| Headroom G | RA Balance | Opt 1 Final | Opt 2 Total | Balance Gap (1−2) | Opt 2 Relief Years | Crossover Income |")
    lines.append("|------------|------------|-------------|-------------|-------------------|--------------------|------------------|")
    for row in sensitivity:
        cross = (f"Option 2 wins above ${row['crossover']:,.0f}"
                 if row["crossover"] is not None
                 else "Option 1 wins at all incomes")
        lines.append(f"| ${row['headroom']:,.0f} | ${row['ra_balance']:,.0f} | "
                     f"${row['opt1_final']:,.2f} | ${row['opt2_total']:,.2f} | "
                     f"${row['balance_gap']:,.2f} | {row['relief_years_opt2']}/{cfg['years']} | {cross} |")
    lines.append("")

    if rate_rows is not None:
        lines.append("### Crossover by Outside Rate (chosen scenario)\n")
        lines.append(f"The balance gap above assumes the simulated outside rate "
                     f"({cfg['outside_rate'] * 100:.1f}% p.a. on Option 2's unused funds). "
                     f"Option 1 is unaffected by that rate, so the gap shrinks as the "
                     f"assumed outside rate rises:\n")
        lines.append("| Outside rate | Opt 2 Total | Balance Gap (1−2) |")
        lines.append("|--------------|-------------|-------------------|")
        for row in rate_rows:
            lines.append(f"| {row['outside_rate'] * 100:.1f}% | "
                         f"${row['opt2_total']:,.2f} | ${row['balance_gap']:,.2f} |")
        lines.append("")
        if rate_crossover is None:
            lines.append("**Crossover:** Option 2 does not catch up even at 20% p.a. "
                         "outside rate — Option 1 wins on balance at every rate.\n")
        elif rate_crossover == 0.0:
            lines.append("**Crossover:** Option 2 leads even with 0% outside rate.\n")
        else:
            lines.append(f"**Crossover:** Option 2 overtakes Option 1 once the outside "
                         f"rate reaches **{rate_crossover * 100:.2f}%** — in the default "
                         f"scenario that is exactly the 4% rate the top-up itself earns "
                         f"in the RA, so the lump-sum result is robust to any outside "
                         f"rate below it (Option 2 wins only if the parked money "
                         f"credibly out-earns the government-guaranteed CPF base).\n")
    lines.append("")

    lines.append("## 8. Conclusion\n")
    o1 = opt1[-1]["ra_total"]
    o2 = opt2[-1]["total_value"]
    gap = round(o1 - o2, 2)
    relief1 = option1_relief_amount(cfg["lump"], headroom)
    sched2 = option2_relief_schedule(cfg["annual"], headroom, cfg["years"])
    cross_income = crossover_income(o1, o2, relief1, sched2)
    if headroom <= 0:
        lines.append(f"**Scenario result:** Existing RA balance is at/above FRS, so **no tax relief "
                     f"attaches to either option**. Option 1 (lump sum) wins at **every income level**, "
                     f"ahead by **${gap:,.2f}**.")
    elif cross_income is None:
        lines.append(f"**Scenario result:** With only ${headroom:,.0f} of relief headroom, Option 2 "
                     f"collects fewer relief years than needed to close the **${gap:,.2f}** balance gap — "
                     f"**Option 1 wins at every income level**.")
    else:
        lines.append(f"**Scenario result:** **Option 1 wins below ~${cross_income:,.0f}** chargeable income "
                     f"(balance gap ${gap:,.2f} dominates); **Option 2 wins above it** (multi-year tax relief "
                     f"outweighs the balance gap).")
    lines.append("")
    lines.append("**General decision rule (age-55 member, YA 2024+ brackets):**")
    lines.append("")
    lines.append("1. RA at or above FRS (the standard position for most 55-year-olds): the lump sum "
                 "wins outright — no relief on either option, and the full amount compounds from Year 1.")
    lines.append("2. RA below FRS: annual top-ups only become competitive at high marginal brackets, "
                 "and only if enough of the 10 years of $8,000 relief stay below FRS. See the table in section 7.")
    lines.append("3. Check MRSS eligibility before choosing: grant-attracting top-ups lose their "
                 "tax relief (IRAS, from YA 2026); the $2,000/yr matching grant usually beats the "
                 "relief it displaces.")
    lines.append("")
    lines.append("*Caveats: constant income over the horizon; no discounting; the outside rate is an "
                 "assumption, not a guarantee, while the CPF 4% base is a floor; the $80,000 total "
                 "personal tax-relief cap is ignored; top-ups are irreversible.*")
    lines.append("")
    return "\n".join(lines)


# ==============================================================================
# main
# ==============================================================================
def parse_args(argv=None):
    p = argparse.ArgumentParser(description="CPF RA top-up: Option 1 vs Option 2")
    p.add_argument("--ra-balance", type=float, default=220_400,
                   help="Existing RA balance in SGD (default: FRS 2026 = 220,400)")
    p.add_argument("--frs", type=float, default=220_400,
                   help="Full Retirement Sum (default: 220,400 for 2026)")
    p.add_argument("--ers", type=float, default=440_800,
                   help="Enhanced Retirement Sum (default: 440,800 for 2026)")
    p.add_argument("--lump", type=float, default=80_000, help="Option 1 lump sum")
    p.add_argument("--annual", type=float, default=8_000, help="Option 2 annual deposit")
    p.add_argument("--years", type=int, default=10)
    p.add_argument("--start-age", type=int, default=55)
    p.add_argument("--outside-rate", type=float, default=0.025,
                   help="Rate on Option 2's unused funds (default 0.025)")
    p.add_argument("--out-dir", default=None,
                   help="Where to write the report (default: this script's directory)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    cfg = {
        "ra_balance": args.ra_balance, "frs": args.frs, "ers": args.ers,
        "lump": args.lump, "annual": args.annual, "years": args.years,
        "starting_age": args.start_age, "outside_rate": args.outside_rate,
    }

    print("=" * 70)
    print("CPF RA Cash Top-Up: Option 1 vs Option 2")
    print(f"  existing RA ${cfg['ra_balance']:,.0f} | FRS ${cfg['frs']:,.0f} | "
          f"headroom ${max(0, cfg['frs'] - cfg['ra_balance']):,.0f}")
    print("=" * 70)

    headroom = frs_headroom(cfg["ra_balance"], cfg["frs"])
    if cfg["lump"] > cfg["ers"] - cfg["ra_balance"]:
        print(f"WARNING: Option 1 lump sum exceeds ERS headroom "
              f"(${cfg['ers'] - cfg['ra_balance']:,.0f}) — infeasible in practice.")

    print("\n[1] Simulating Option 1 (lump sum)...")
    opt1 = simulate_option1(cfg["ra_balance"], cfg["lump"], cfg["years"],
                            cfg["starting_age"])
    print(f"    Final RA total: ${opt1[-1]['ra_total']:,.2f} "
          f"(top-up value ${opt1[-1]['topup_value']:,.2f})")

    print("\n[2] Simulating Option 2 (annual deposits)...")
    opt2 = simulate_option2(cfg["ra_balance"], cfg["annual"], cfg["years"],
                            cfg["outside_rate"], cfg["starting_age"])
    print(f"    Final RA total: ${opt2[-1]['ra_total']:,.2f} | "
          f"outside pot: ${opt2[-1]['outside_balance']:,.2f} | "
          f"total value: ${opt2[-1]['total_value']:,.2f}")

    print("\n[3] Verification...")
    checks = verify(opt1, opt2, cfg["ra_balance"], cfg["lump"], cfg["annual"],
                    cfg["years"], cfg["outside_rate"])
    for label, ok, detail in checks:
        print(f"    {'PASS' if ok else 'FAIL'}: {label} — {detail}")
    if not all(ok for _l, ok, _d in checks):
        raise SystemExit("Verification failed.")

    relief1 = option1_relief_amount(cfg["lump"], headroom)
    sched2 = option2_relief_schedule(cfg["annual"], headroom, cfg["years"])
    print(f"\n[4] Relief: Option 1 eligible ${relief1:,.0f} (Year 1) | "
          f"Option 2 eligible amounts: {[f'{a:,.0f}' for a in sched2]}")

    print("\n[5] Per-bracket comparison...")
    comparison = build_comparison_table(opt1[-1]["ra_total"],
                                        opt2[-1]["total_value"], relief1, sched2)
    for row in comparison:
        print(f"    ${row['income']:>12,} | Opt1 net ${row['opt1_net']:>12,.2f} | "
              f"Opt2 net ${row['opt2_net']:>12,.2f} | {row['winner']}")

    print("\n[6] FRS-headroom sensitivity...")
    sensitivity = headroom_sensitivity(cfg["lump"], cfg["annual"], cfg["years"],
                                       cfg["frs"], cfg["ra_balance"],
                                       cfg["outside_rate"], None,
                                       cfg["starting_age"])
    for row in sensitivity:
        cross = (f"Option 2 wins above ${row['crossover']:,.0f}"
                 if row["crossover"] is not None else "Option 1 wins at all incomes")
        print(f"    headroom ${row['headroom']:>7,}: {cross}")

    print("\n[7] Outside-rate sensitivity...")
    rate_rows, rate_cross = outside_rate_sensitivity(
        cfg["ra_balance"], cfg["lump"], cfg["annual"], cfg["years"], None,
        cfg["starting_age"])
    for row in rate_rows:
        print(f"    outside rate {row['outside_rate'] * 100:>5.1f}%: "
              f"Opt 2 total ${row['opt2_total']:>12,.2f} | "
              f"gap ${row['balance_gap']:>10,.2f}")
    if rate_cross is None:
        print("    crossover: Option 2 never catches up below 20% outside rate")
    else:
        print(f"    crossover: Option 2 overtakes Option 1 at "
              f"{rate_cross * 100:.2f}% outside rate")

    print("\n[8] Writing report...")
    report = generate_report(cfg, opt1, opt2, checks, comparison, sensitivity,
                             rate_rows=rate_rows, rate_crossover=rate_cross)
    out_dir = args.out_dir or os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "cpf_ra_comparison_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"    Report written ({len(report)} chars) -> {report_path}")

    o1, o2 = opt1[-1]["ra_total"], opt2[-1]["total_value"]
    cross = crossover_income(o1, o2, relief1, sched2)
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Option 1 final RA total:      ${o1:>12,.2f}")
    print(f"  Option 2 total value:         ${o2:>12,.2f}")
    print(f"  Balance gap (1-2):            ${o1 - o2:>12,.2f}")
    if cross is None:
        print("  Winner: Option 1 at ALL income levels")
    else:
        print(f"  Crossover: Option 1 below ${cross:,.0f}, Option 2 above")
    print("\nDone.")


if __name__ == "__main__":
    main()
