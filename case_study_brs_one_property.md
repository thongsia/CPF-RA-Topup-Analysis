# Case Study — at the BRS with one property pledged (age 55)

A worked example from the [CPF RA top-up analysis](README.md): deploying $80,000 (a lump sum, or $8,000 a year) when the Retirement Account sits at the Basic Retirement Sum and one property is pledged. Setup, options, and assumptions live in the README; this document covers only what is specific to this position.

A member who turns 55 in 2026 and pledges a Singapore property (remaining lease to at least age 95) sets aside only the BRS: RA = $110,200, headroom to FRS = $110,200. This is a common position: of the 41,000 active members who turned 55 in 2025, 73.4% had met the BRS or higher — in cash, or with one property pledged — up from 70.5% in 2024 ([Straits Times, 3 Jul 2026](https://www.straitstimes.com/business/more-hitting-cpf-retirement-targets-at-the-milestone-age-of-55)).

## The model's answer

Running the model on this balance (`python3 cpf_ra_comparison.py --ra-balance 110200`) gives the 10-year comparison in Table 1.

**Table 1: Case study — RA $110,200 (BRS, one property pledged), $80,000 over 10 years**

| | Option 1 (lump sum) | Option 2 ($8,000/year) |
|---|---|---|
| Value at Year 10 | $292,347.96 (all in the RA) | $273,819.23 in RA + $10,539.03 outside = $284,358.26 |
| Tax relief | $8,000 (Year 1 only) | $8,000/year for all 10 years — every top-up stays below FRS |
| **Gap** | **+$7,989.70 to Option 1** | |

The break-even chargeable income is **$87,283**: above it, Option 2 wins; below it, Option 1 wins. This is the "plateau" value of the README's Table 3 — the range of headroom over which the break-even stops moving. From $80,000 of headroom up, Option 2's 10 x $8,000 top-ups all still earn relief (a full 10 years), and while the RA is above $52,000 the balance gap stays at $7,989.70; so across all headroom between $80,000 and $168,400 (RA $52,000–$140,400) the break-even holds at $87,283. This member, with $110,200 of headroom, sits squarely in that range. The net bias in the README's caveats (Section 5) pushes this break-even a bit lower, so treat $85,000–$95,000 as a coin-flip zone.

Two notes on the Table 1 figures:

- The gap is exactly the README's Table 2 at-FRS gap: the RA is above $60,000, so every top-up dollar earns a flat 4% either way, and only the not-yet-deployed budget earns the assumed 2.5% outside.
- Option 2 gets full relief for all 10 years (10 x $8,000 = $80,000 < $110,200 of headroom); the lump sum gets one year.

## What is specific to the BRS position

Three considerations the model does not capture:

1. **MRSS does not apply.** The grant requires the RA to be strictly below the BRS (plus average monthly income at most $4,000, residence annual value at most $21,000, at most one property, Singapore citizenship). A member at exactly the BRS is ineligible — so no grant twist, and the figures above stand as computed.
2. **The headroom is tied to the property.** The pledge is what lets the RA sit at the BRS; while the property is held, the member may withdraw RA savings above the BRS (excluding interest and government grants) for personal use, so the top-up plan implicitly gives up that access. If the property is sold, the pledged amount — FRS − BRS = $110,200 — must be refunded into the RA from the sale proceeds; every top-up dollar reduces that future obligation (while earning interest and relief), so if a sale is expected within the decade, top-ups — Option 2's especially, for a high earner — are doubly valuable.
3. **The stake is the lifetime payout.** Setting aside the BRS alone earns about $950/month from 65; the FRS earns about $1,780/month (CPF Board estimates, 2026 cohort, Standard Plan). Top-ups that close the gap roughly double the lifetime monthly income — which is what makes the relief-heavy Option 2 attractive at higher incomes.

## Sources

- [Straits Times, "More hit CPF retirement targets at 55" (3 Jul 2026)](https://www.straitstimes.com/business/more-hitting-cpf-retirement-targets-at-the-milestone-age-of-55) — 73.4% of 2025's 55-year-olds met the BRS or higher (in cash, or with one property), up from 70.5% in 2024
- [CPF Board, "What is the CPF retirement sum?"](https://www.cpf.gov.sg/member/infohub/educational-resources/what-is-the-cpf-retirement-sum) — 2026 retirement sums and estimated CPF LIFE payouts (about $950/month at the BRS, about $1,780 at the FRS, Standard Plan)
- [CPF Board, "Withdrawal of RA savings for property owners"](https://www.cpf.gov.sg/member/infohub/educational-resources/withdrawal-of-ra-savings-for-property-owners-what-you-need-to-know) — withdrawal above the BRS with a pledged property; refund of the pledged amount on sale
- [CPF Board MRSS eligibility](https://www.cpf.gov.sg/member/growing-your-savings/government-support/matching-grant-for-retirement) — RA strictly below the BRS, plus income and property criteria
