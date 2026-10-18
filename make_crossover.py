#!/usr/bin/env python3
"""
Generate the two figures for the CPF RA top-up analysis from the model
in cpf_ra_comparison.py.

Figure 1 (net_benefit.png): net benefit vs chargeable income for the
chosen scenario (--ra-balance), Option 1 vs Option 2, with the
break-even income marked if one exists in the plotted range.

Figure 2 (crossover_by_headroom.png): break-even chargeable income as
a function of FRS headroom (how much further top-up still attracts tax
relief), i.e. the two-dimensional decision rule.

Requires matplotlib.  Usage:
    python3 make_crossover.py [--ra-balance 220400] [other options as
    for cpf_ra_comparison.py] [--out-dir DIR]
"""

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cpf_ra_comparison as m

NET_BENEFIT_PNG = "net_benefit.png"
CROSSOVER_PNG = "crossover_by_headroom.png"


def net_curves(incomes, opt1_final, opt2_total, relief1, sched2):
    n1 = [opt1_final + m.option1_tax_savings(i, relief1) for i in incomes]
    n2 = [opt2_total + m.option2_tax_savings(i, sched2) for i in incomes]
    return n1, n2


def plot_net_benefit(out, args, headroom, incomes, n1, n2, cross):
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    ax.plot([i / 1000 for i in incomes], n1, color="tab:blue", lw=2,
            label=f"Option 1 net (${args.lump:,.0f} lump sum)")
    ax.plot([i / 1000 for i in incomes], n2, color="tab:orange", lw=2,
            label=f"Option 2 net (${args.annual:,.0f}/yr)")
    ax.set_xlabel("Chargeable income (SGD, thousands)")
    ax.set_ylabel("Net benefit (SGD)\n= final total value + tax savings\n"
                  "from CPF top-up relief")
    ax.set_title(
        f"Option 1 vs Option 2: net benefit by chargeable income\n"
        f"Scenario: existing RA balance ${args.ra_balance:,.0f} "
        f"(relief headroom to FRS: ${headroom:,.0f})\n"
        f"{args.years}-year horizon, tiered 55+ interest, FRS-capped relief",
        fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    if cross is not None and cross <= args.income_max:
        y_c = n1[incomes.index(min(
            incomes, key=lambda i: abs(i - cross)))]
        ax.axvline(cross / 1000, color="red", ls="--", lw=1.5)
        ax.plot([cross / 1000], [y_c], "o", color="red", ms=6)
        ax.annotate(f"Break-even at ~${cross:,.0f}",
                    xy=(cross / 1000, y_c),
                    xytext=(cross / 1000 + 40, y_c + 400),
                    arrowprops=dict(arrowstyle="->", color="red"),
                    color="red", fontsize=10)
        ax.fill_between([i / 1000 for i in incomes], n1, n2,
                        where=[a >= b for a, b in zip(n1, n2)],
                        alpha=0.08, color="tab:blue", label="Option 1 better")
        ax.fill_between([i / 1000 for i in incomes], n1, n2,
                        where=[b > a for a, b in zip(n1, n2)],
                        alpha=0.08, color="tab:orange", label="Option 2 better")
    else:
        ax.text(0.5, 0.05, "Option 1 wins at all incomes\n"
                "(no relief headroom to FRS)",
                transform=ax.transAxes, ha="center",
                bbox=dict(boxstyle="round", fc="lightyellow",
                          ec="gray", alpha=0.9), fontsize=10)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Figure 1 written -> {out}")


def plot_crossover_by_headroom(out, args, sensitivity):
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    gs = [row["headroom"] / 1000 for row in sensitivity]
    xs = [row["crossover"] / 1000 if row["crossover"] is not None else None
          for row in sensitivity]
    # shade the region where Option 1 always wins
    always1 = [g for g, x in zip(gs, xs) if x is None]
    ax.axvspan(0, max(always1) if always1 else 0, color="tab:blue", alpha=0.10)
    pts = [(g, x) for g, x in zip(gs, xs) if x is not None]
    if pts:
        ax.plot([g for g, _ in pts], [x for _, x in pts], "o-",
                color="tab:orange", lw=2, ms=6,
                label="Break-even: Option 2 wins above this income")
        for idx, (g, x) in enumerate(pts):
            dy = 6 if idx % 2 == 0 else -14
            ax.annotate(f"${x * 1000:,.0f}", (g, x),
                        textcoords="offset points", xytext=(8, dy), fontsize=8)
    if always1:
        ax.set_ylim(0, 600)
        ax.text(max(always1) / 2, 300, "Option 1 wins\nat all incomes",
                ha="center", fontsize=9, color="tab:blue")
    ax.set_xlim(0, 80)
    ax.set_xlabel("FRS headroom = FRS − existing RA balance "
                  "(SGD, thousands)")
    ax.set_ylabel("Break-even chargeable income (SGD, thousands)")
    ax.set_title(
        "Break-even chargeable income by FRS headroom\n"
        f"Above this income, Option 2 (${args.annual:,.0f}/yr) beats "
        f"Option 1 (${args.lump:,.0f} lump sum)\n"
        f"Members turning {args.start_age} in 2026, FRS ${args.frs:,.0f}",
        fontsize=11)
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Figure 2 written -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra-balance", type=float, default=220_400)
    ap.add_argument("--frs", type=float, default=220_400)
    ap.add_argument("--ers", type=float, default=440_800)
    ap.add_argument("--lump", type=float, default=80_000)
    ap.add_argument("--annual", type=float, default=8_000)
    ap.add_argument("--years", type=int, default=10)
    ap.add_argument("--start-age", type=int, default=55)
    ap.add_argument("--outside-rate", type=float, default=0.025)
    ap.add_argument("--income-max", type=float, default=1_500_000)
    ap.add_argument("--out-dir", default=os.path.dirname(
        os.path.abspath(__file__)))
    args = ap.parse_args()

    headroom = m.frs_headroom(args.ra_balance, args.frs)
    sim1 = m.simulate_option1(args.ra_balance, args.lump, args.years,
                              args.start_age)
    sim2 = m.simulate_option2(args.ra_balance, args.annual, args.years,
                              args.outside_rate, args.start_age)
    o1, o2 = sim1[-1]["ra_total"], sim2[-1]["total_value"]
    r1 = m.option1_relief_amount(args.lump, headroom)
    sched = m.option2_relief_schedule(args.annual, headroom, args.years)

    incomes = [i * 1000 for i in range(0, int(args.income_max // 1000) + 1)]
    n1, n2 = net_curves(incomes, o1, o2, r1, sched)
    cross = m.crossover_income(o1, o2, r1, sched)

    sensitivity = m.headroom_sensitivity(args.lump, args.annual, args.years,
                                         args.frs, args.ra_balance,
                                         args.outside_rate, None,
                                         args.start_age)

    plot_net_benefit(os.path.join(args.out_dir, NET_BENEFIT_PNG), args,
                     headroom, incomes, n1, n2, cross)
    plot_crossover_by_headroom(os.path.join(args.out_dir, CROSSOVER_PNG),
                               args, sensitivity)


if __name__ == "__main__":
    main()
