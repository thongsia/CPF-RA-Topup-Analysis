# CPF RA Top-Up Analysis

Comparing two strategies to fund a CPF Retirement Account (RA) at age 55 over a 10-year horizon.

## Options Compared

| | Option 1: Lump Sum | Option 2: Annual Top-ups |
|---|---|---|
| **Deposit** | $80,000 at Year 1 start | $8,000/year for 10 years |
| **CPF RA interest** | 4% p.a. on full balance | 4% p.a. on deposited amounts |
| **Outside interest** | — | 2.5% p.a. on unused funds |
| **Tax relief** | $8,000 in Year 1 only | $8,000 each year (10× total) |

## Key Results

| | Option 1 | Option 2 |
|---|---|---|
| RA balance at Year 10 | **$118,419.54** | $99,890.81 |
| Outside pot at Year 10 | — | $10,539.03 |
| **Total value** | **$118,419.54** | **$110,429.84** |

Option 1 earns **$7,990 more** in CPF balance because the full $80K compounds at 4% from Year 1. But Option 2 captures **10× the tax relief** ($80K total vs $8K), since unused relief cannot be carried forward.

### Crossover Point

The winner depends on your marginal tax bracket:

- **Income below ~$87,297** → Option 1 wins (compound interest advantage dominates)
- **Income above ~$87,297** → Option 2 wins (tax savings outweigh the balance gap)

![Crossover](crossover.png)

## Assumptions

- CPF RA interest rate: 4% p.a.
- Outside interest rate (Option 2 unused funds): 2.5% p.a.
- CPF Cash Top-up Relief: $8,000/YA cap for self top-up; **cannot be carried forward**
- Chargeable income constant across all 10 years
- No discounting (nominal comparison)
- Singapore progressive tax brackets (YA 2024 onwards)

## Files

- [`cpf_ra_comparison.py`](cpf_ra_comparison.py) — Python script (stdlib only)
- [`cpf_ra_comparison_report.md`](cpf_ra_comparison_report.md) — Full report with tables
- [`crossover.png`](crossover.png) — Net benefit crossover graph
- [`research_findings.md`](research_findings.md) — IRAS/CPF source research

## Sources

- [IRAS Individual Income Tax Rates](https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates)
- [IRAS CPF Cash Top-up Relief](https://www.iras.gov.sg/taxes/individuals/resident-individuals/rates-and-reliefs/cash-top-up-relief)
- [CPF Full Retirement Sum](https://www.cpf.gov.sg/education/cpf-101/how-much-i-need-for-retirement/retirement-adequacy/full-retirement-sum)
