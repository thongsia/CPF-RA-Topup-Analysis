# CPF RA Top-Up Analysis

_Disclaimer: This analysis was prompted by a human, then initially designed and carried out by an AI agent (Hermes + Qwen3.8-27B + [AIOS skillset](https://github.com/thongsia/aios)), and finally shaped and edited collaboratively between the two._

A 55-year-old has **$80,000** to put into the CPF Retirement Account (RA) over the next 10 years. Two ways to do it: one **$80,000 lump sum**, or **$8,000 a year**. Which is better? This repo answers that under the current IRAS/CPF rules, including the two that dominate the answer:

1. **FRS-capped tax relief** — CPF Cash Top-up Relief (max $8,000/YA) is only granted for the portion of a top-up that fills the RA up to the Full Retirement Sum (FRS, $220,400 in 2026). Top-ups above FRS (up to ERS $440,800) earn interest but no relief.
2. **Tiered 55+ interest** — RA interest is 6% on the first $30,000, 5% on the next $30,000, 4% on the rest of the combined SA/RA balance (4% base + 2%/1% additional interest). If the existing RA balance already exceeds $60,000 (true for any standard 55+ member; minimum BRS is $110,200), all top-up dollars earn a flat 4%.

## 1. Short Answer

**If your RA is already at the FRS — the normal position for most 55-year-olds — put the full $80,000 in now (lump sum).** It beats the $8,000/year schedule at *every* income level, by **$7,989.70** over 10 years. With the RA at FRS, no top-up earns tax relief at all, so the decision is pure interest: the lump sum compounds at 4% for the full decade, while each year's $8,000 is split between the RA and a pot parked outside at an assumed 2.5%. The result holds for any outside rate below **4.00%** — the rate the top-up itself earns in the RA, so Option 2 wins only if the parked money credibly out-earns the government-guaranteed CPF base.

**If your RA is still below the FRS, the answer depends on your income.** Annual top-ups earn up to 10 years of tax relief the lump sum never gets, so at high enough income they win; the break-even income falls as your headroom to FRS grows (Table 3, Figure 2).

## 2. Options Compared

**Table 1: The two top-up strategies**

| | Option 1: Lump Sum | Option 2: Annual Top-ups |
|---|---|---|
| **Deposit** | $80,000 at Year 1 start | $8,000/year for 10 years |
| **CPF RA interest** | Tiered 55+ rates on total balance | Tiered 55+ rates on total balance |
| **Outside interest** | — | 2.5% p.a. on unused funds |
| **Tax relief** | $8,000 in Year 1 only, **if below FRS** | $8,000/year while below FRS |

## 3. Key Results

### Key Result 1 — RA at FRS on day one: Option 1 (lump sum) wins

Top-up dollars earn a flat 4% in both options, and **no tax relief attaches to either option** (RA already at FRS). Table 2 shows the 10-year values:

**Table 2: 10-year value of the $80,000 top-up — RA at FRS on day one**

| | Option 1 | Option 2 |
|---|---|---|
| Top-up value at Year 10 | **$118,419.54** | $99,890.81 in RA + $10,539.03 outside = **$110,429.84** |
| Total incl. existing balance | **$455,470.88** | **$447,481.18** |
| **Balance gap** | **+$7,989.70 to Option 1** | |

(The existing $220,400 grows to $337,051.34 on its own in both options; the decision rests entirely on the top-up rows.)

**Option 1 (lump sum) wins at every income level, by $7,989.70.** The gap is income-independent; only the tax side varies with the member's position relative to FRS (Figure 1 shows the net-benefit curves).

*Robustness:* the gap above assumes the unused funds earn 2.5%; the options are exactly equal once the outside rate reaches **4.00%** — the rate the top-up itself earns in the RA — so the lump-sum conclusion holds for any outside rate below it (full sweep: report §8).

![Figure 1 — Option 1 vs Option 2: net benefit by chargeable income, existing RA at FRS](net_benefit.png)

### Key Result 2 — RA below FRS: break-even income ~$87,283–$287,587 depending on headroom (Option 1 wins below it, Option 2 above it)

With the RA below the FRS, annual top-ups earn up to 10 years of tax relief that the lump sum never gets (relief attaches only while top-ups fill the gap to FRS). The winner now depends on income, and the break-even income falls as the headroom to FRS grows (Table 3):

**Table 3: Break-even chargeable income by FRS headroom**

| Headroom to FRS (G = FRS − RA) | RA Balance (2026 FRS $220,400) | Break-even chargeable income |
|---|---|---|
| $0 – $40,000 | $180,400 – $220,400 | none — **Option 1 wins at all incomes** |
| $48,000 | $172,400 | Option 2 wins only above ~$287,587 |
| $56,000 | $164,400 | Option 2 wins only above ~$164,387 |
| $64,000 | $156,400 | Option 2 wins only above ~$126,325 |
| $72,000 | $148,400 | Option 2 wins only above ~$122,249 |
| $80,000+ | ≤ $140,400 | Option 2 wins above ~$87,283 |

Members with RA below ~$60,000 also get the preferential 6%/5% tiers on the top-up itself, which widens Option 1's balance gap — e.g. with a $40,000 existing balance the gap is **$8,178.29**, the break-even is **~$87,749**, and the outside-rate crossover moves to **4.03%**.

![Figure 2 — break-even chargeable income by FRS headroom; the shaded region is where Option 1 wins at all incomes](crossover_by_headroom.png)

## 4. Decision Rule

The winner depends on two dimensions — the existing RA balance relative to FRS, and the marginal tax bracket:

1. **RA at FRS on day one** (the normal position for most 55-year-olds): **Option 1 (lump sum)** — wins at every income level by $7,989.70, robust to any outside rate below 4.00% (Key Result 1).
2. **RA below FRS:** compare your chargeable income with the break-even in Table 3 (Key Result 2, Figure 2) — **below it, Option 1; above it, Option 2**.

## 5. Assumptions

- FRS $220,400 / ERS $440,800 (members turning 55 in 2026)
- CPF Cash Top-up Relief: $8,000/YA cap for self top-up; **cannot be carried forward**; FRS-capped
- Outside interest rate (Option 2 unused funds): 2.5% p.a. — an assumption, not a guarantee; the CPF 4% base is a floor
- Chargeable income constant across all 10 years; no discounting (nominal comparison)
- Singapore progressive tax brackets (YA 2024 onwards)
- $80,000 total personal tax-relief cap ignored; MRSS grant interaction noted in the report

Second-level detail — year-by-year balances, closed-form verification, per-bracket tax tables, the outside-rate sweep — is in [the full report](cpf_ra_comparison_report.md) (§5–§8).

## 6. Files

Usage examples for both scripts live in their docstrings (or run either with `--help`).

- [`cpf_ra_comparison.py`](cpf_ra_comparison.py) — analysis script (stdlib only, self-verifying)
- [`make_crossover.py`](make_crossover.py) — chart generator (matplotlib)
- [`cpf_ra_comparison_report.md`](cpf_ra_comparison_report.md) — full report with all tables
- [`net_benefit.png`](net_benefit.png) — Figure 1: net benefit by chargeable income for the chosen scenario
- [`crossover_by_headroom.png`](crossover_by_headroom.png) — Figure 2: break-even chargeable income by FRS headroom
- [`research_findings.md`](research_findings.md) — IRAS/CPF source research

## 7. Sources

- [IRAS Individual Income Tax Rates](https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates)
- [IRAS CPF Cash Top-up Relief (incl. FRS limit on relief)](https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-reliefs-rebates-and-deductions/tax-reliefs/central-provident-fund-(cpf)-cash-top-up-relief)
- [CPF Board RA top-ups (ERS cap, additional interest)](https://www.cpf.gov.sg/member/growing-your-savings/saving-more-with-cpf/top-up-to-enjoy-higher-retirement-payouts)
