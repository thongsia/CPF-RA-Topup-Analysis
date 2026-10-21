# CPF RA Top-Up Analysis

_Disclaimer: This analysis was prompted by a human, then initially designed and carried out by an AI agent (Hermes + Qwen3.8-27B), and finally shaped and edited collaboratively between the two._

A 55-year-old has **$80,000** to put into the CPF Retirement Account (RA) over the next 10 years. Two ways to do it: one **$80,000 lump sum**, or **$8,000 a year**. Which is better? This repo answers that under the current IRAS/CPF rules, including the two that dominate the answer:

1. **FRS-capped tax relief** — CPF Cash Top-up Relief (max $8,000/YA) is only granted for the portion of a top-up that fills the RA up to the Full Retirement Sum (FRS, $220,400 in 2026). Top-ups above FRS (up to ERS $440,800) earn interest but no relief.
2. **Tiered 55+ interest** — RA interest is 6% on the first $30,000, 5% on the next $30,000, 4% on the rest of the combined SA/RA balance (4% base + 2%/1% additional interest). If the existing RA balance already exceeds $60,000 (true for any member who met the minimum requirement — the BRS alone, $110,200, is well above $60,000), all top-up dollars earn a flat 4%.

_This README is the executive summary and stands on its own. The detail behind the numbers — derivations, year-by-year balances, full tables, the outside-rate sweep, and the caveats — is in [the full report](cpf_ra_comparison_report.md), which `cpf_ra_comparison.py` regenerates; "report §N" references below point to sections of that file._

## 1. Short Answer

**If your RA is already at the FRS — a common position for 55-year-olds: in 2025, 73.4% of members turning 55 had met the FRS, or the BRS while owning one property, up from 70.5% in 2024 ([Straits Times, 3 Jul 2026](https://www.straitstimes.com/business/more-hitting-cpf-retirement-targets-at-the-milestone-age-of-55)) — put the full $80,000 in now (lump sum).** It beats the $8,000/year schedule at *every* income level, by **$7,989.70** over 10 years. With the RA at FRS, no top-up earns tax relief at all, so the decision is pure interest: the lump sum compounds at 4% for the full decade, while each year's $8,000 is split between the RA and a pot parked outside at an assumed 2.5%. The result holds for any outside rate below **4.00%** — the rate the top-up itself earns in the RA, so Option 2 wins only if the parked money credibly out-earns the government-guaranteed CPF base.

**If your RA is still below the FRS, the answer depends on your income.** Annual top-ups earn up to 10 years of tax relief the lump sum never gets, so at high enough income they win; the break-even income falls as your headroom to FRS grows (Table 3, Figure 1; the rising-FRS caveat in report §9 would push these break-evens lower).

## 2. Options Compared

Two ways to do it, summarised in Table 1:

**Table 1: The two top-up strategies**

| | Option 1: Lump Sum | Option 2: Annual Top-ups |
|---|---|---|
| **Deposit** | $80,000 at Year 1 start | $8,000/year for 10 years |
| **CPF RA interest** | Tiered 55+ rates on total balance | Tiered 55+ rates on total balance |
| **Outside interest** | — | 2.5% p.a. on unused funds (assumption, pegged to the prevailing CPF OA rate) |
| **Tax relief** | $8,000 in Year 1 only, **if below FRS** | $8,000/year while below FRS |

## 3. Key Results

The decision turns on two dimensions: the existing RA balance relative to FRS, and the member's marginal tax bracket.

### Key Result 1 — RA at FRS on day one: Option 1 (lump sum) wins

Top-up dollars earn a flat 4% in both options, and **no tax relief attaches to either option** (RA already at FRS). Table 2 shows the 10-year values:

**Table 2: 10-year value of the $80,000 top-up — RA at FRS on day one**

| | Option 1 | Option 2 |
|---|---|---|
| Top-up value at Year 10 | **$118,419.54** | $99,890.81 in RA + $10,539.03 outside = **$110,429.84** |
| Total incl. existing balance | **$455,470.88** | **$447,481.18** |
| **Balance gap** | **+$7,989.70 to Option 1** | |

(The existing $220,400 grows to $337,051.34 on its own in both options; the decision rests entirely on the top-up rows.)

**Option 1 (lump sum) wins at every income level, by $7,989.70.** The gap is income-independent; only the tax side varies with the member's position relative to FRS. With the RA at FRS, no top-up in either option attracts relief, so both net-benefit curves are flat across the income range — Option 1 a constant $455,470.88, Option 2 a constant $447,481.18 at every chargeable income, a gap of $7,989.70 (about 1.8%) that does not depend on the bracket.

*Robustness:* the gap above assumes the unused funds earn 2.5%; the options are exactly equal once the outside rate reaches **4.00%** — the rate the top-up itself earns in the RA — so the lump-sum conclusion holds for any outside rate below it (full sweep: report §8).

### Key Result 2 — RA below FRS: break-even income $87,283–$287,587 depending on headroom (Option 1 wins below it, Option 2 above it)

With the RA below the FRS, annual top-ups earn up to 10 years of tax relief that the lump sum never gets (relief attaches only while top-ups fill the gap to FRS). The winner now depends on income, and the break-even income falls as the headroom to FRS grows (Table 3):

**Table 3: Break-even chargeable income by FRS headroom**

| Headroom to FRS (G = FRS − RA) | RA Balance (2026 FRS $220,400) | Break-even chargeable income |
|---|---|---|
| $0 – $40,000 | $180,400 – $220,400 | none — **Option 1 wins at all incomes** |
| $48,000 | $172,400 | Option 2 wins only above $287,587 |
| $56,000 | $164,400 | Option 2 wins only above $164,387 |
| $64,000 | $156,400 | Option 2 wins only above $126,325 |
| $72,000 | $148,400 | Option 2 wins only above $122,249 |
| $80,000 – $168,400 | $52,000 – $140,400 | Option 2 wins only above $87,283 |

For headroom beyond $168,400 (RA below $52,000), top-up dollars reach the preferential 6%/5% tiers, which widens Option 1's balance gap and pushes the break-even up — e.g. with a $40,000 existing balance the gap is **$8,178.29** and the break-even **$87,749** (outside-rate crossover **4.03%**); with $30,000 the gap is **$8,478.66** and the break-even **$120,631**.

![Figure 1 — break-even chargeable income by FRS headroom; the shaded region is where Option 1 wins at all incomes](crossover_by_headroom.png)

## 4. Assumptions

- FRS $220,400 / ERS $440,800 (members turning 55 in 2026)
- CPF Cash Top-up Relief: $8,000/YA cap for self top-up; **cannot be carried forward**; FRS-capped
- Outside interest rate (Option 2 unused funds): 2.5% p.a. — an assumption pegged to the prevailing CPF OA interest rate, not a guarantee; the CPF 4% base is a floor
- Chargeable income constant across all 10 years; no discounting (nominal comparison)
- Singapore progressive tax brackets (YA 2024 onwards)
- $80,000 total personal tax-relief cap ignored; MRSS grant interaction noted in the report

Second-level detail — year-by-year balances, closed-form verification, per-bracket tax tables, the outside-rate sweep — is in [the full report](cpf_ra_comparison_report.md) (§5–§8).

## 5. Caveats — which way the simplifications push

The model is deliberately simple, and each simplification below pushes the comparison in a known direction. None overturns the broad picture, but they matter for how far to trust the exact numbers (full treatment: report §9).

- **Tax savings are counted at face value** — no compounding, no discounting. Option 2's savings arrive in Years 2–10, so reinvested they would grow by age 65: Option 2 is, if anything, stronger than shown, i.e. the true break-evens in Table 3 are likely a bit lower than printed. The at-FRS case is unaffected, since neither option earns any relief.
- **The outside pot's 2.5% is modelled pre-tax.** CPF interest is tax-free; the outside pot's is not. A high-bracket member's 2.5% outside investment nets only about 1.9% after tax, so the 4.00% crossover in Key Result 1 is optimistic for high earners — the lump sum is, if anything, more robust than shown.
- **The relief-applicable FRS is frozen at $220,400.** In reality it rises every January (about 3.5%/year: $213,000 in 2025 → $220,400 in 2026 → $228,200 in 2027). That rise nearly offsets the $8,000/yr headroom drain, so members with $48,000–$72,000 of headroom likely keep relief on all 10 years of top-ups rather than the 6–9 the model counts. This is the largest bias, and it pushes the Table 3 break-evens down as well.
- **The model stops at age 65.** After 65 the RA converts to CPF LIFE payouts while the outside pot stays liquid, and top-ups are irreversible. These are real considerations the numbers do not capture.

**Net effect:** the at-FRS headline is at least as robust as shown; the below-FRS break-evens are, if anything, too high — Option 2's winning region is, if anything, larger than shown.

## 6. Files

Usage examples for both scripts live in their docstrings (or run either with `--help`).

- [`cpf_ra_comparison.py`](cpf_ra_comparison.py) — analysis script (stdlib only, self-verifying)
- [`make_crossover.py`](make_crossover.py) — Figure 1 generator (matplotlib); the net-benefit chart is optional (`--net-benefit`) and uninformative for the default at-FRS scenario, which the text states instead
- [`cpf_ra_comparison_report.md`](cpf_ra_comparison_report.md) — full report with all tables
- [`crossover_by_headroom.png`](crossover_by_headroom.png) — Figure 1: break-even chargeable income by FRS headroom
- [`research_findings.md`](research_findings.md) — IRAS/CPF source research

## 7. Sources

- [IRAS Individual Income Tax Rates](https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates)
- [IRAS CPF Cash Top-up Relief (incl. FRS limit on relief)](https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-reliefs-rebates-and-deductions/tax-reliefs/central-provident-fund-(cpf)-cash-top-up-relief)
- [CPF Board RA top-ups (ERS cap, additional interest)](https://www.cpf.gov.sg/member/growing-your-savings/saving-more-with-cpf/top-up-to-enjoy-higher-retirement-payouts)
- [CPF Board MRSS eligibility (RA below BRS, income and property criteria)](https://www.cpf.gov.sg/member/growing-your-savings/government-support/matching-grant-for-retirement)
- Straits Times, "More hit CPF retirement targets at 55" (3 Jul 2026) — 73.4% of 2025's 55-year-olds met the FRS or the BRS with one property, up from 70.5% in 2024: https://www.straitstimes.com/business/more-hitting-cpf-retirement-targets-at-the-milestone-age-of-55
- MOM written reply to Parliamentary Question (Feb 2023) — about 33% of active members turning 55 in 2022 had not set aside the FRS in cash: https://www.mom.gov.sg/newsroom/parliament-questions-and-replies/2023/0222-written-answer-to-pq-on-data-on-cpf-members-who-are-unable-to-set-aside-cpf-frs
