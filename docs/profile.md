# Profile of out/credit-unions.csv

Profiled 2026-10-13 with the `data:explore-data` method, using DuckDB on the built output. Rerun it after each
quarter's build.

## Overview

- 17,667 rows: one per quarter, credit union, measure and part. The key (quarter, `cu_number`, measure, part) is
  unique, with no duplicates.
- 34 quarters, 2018-03 to 2026-06, with no gaps. 41 credit unions in all; 1,359 credit-union quarters.
- New Mexico's roster by quarter: 41 through 2021-06, 40 from 2021-09 (Animas leaves), 39 in 2025-03 (Telco
  Roswell), 38 in 2025-06 (Fort Bayard), and 37 from 2025-09 (Southwest).
- Names: no stray whitespace. Two charters changed name over the period: 5851 (Sandia Laboratory, now Sunward) and
  62841 (Belen Railway Employees, now Railroad Employees). The page should use the latest quarter's name, and
  the method note should say a name can change.

## Measures

| Measure | Nulls | Min | Median | p99 | Max | Zeros | Below 0 |
|---|---|---|---|---|---|---|---|
| total_assets ($) | 0 | 2.0M | 54.0M | 4.42B | 5.10B | 0 | 0 |
| total_loans ($) | 0 | 0.42M | 30.6M | 2.94B | 3.44B | 0 | 0 |
| members | 0 | 229 | 4,803 | 253,495 | 299,021 | 0 | 0 |
| net_worth_ratio (%) | 0 | 2.40 | 12.44 | 26.56 | 33.77 | 0 | 0 |
| delinquency (%) | 0 | 0.00 | 0.49 | 5.94 | 9.94 | 79 | 0 |
| net_charge_offs_12m (%) | 123 | -0.84 | 0.27 | 3.21 | 3.90 | 52 | 84 |
| commercial_share (%) | 0 | 0.00 | 0.00 | 22.55 | 26.33 | 825 | 0 |
| cre_reset_5y (%) | 1,109 | 0.00 | 0.00 | 100 | 100 | 163 | 0 |
| home_reset_5y (%) | 843 | 0.00 | 0.70 | 89.66 | 100 | 245 | 0 |
| other_gov_guaranteed, balance ($) | 0 | 0 | 0 | 112.5M | 135.5M | 1,289 | 0 |
| sba, balance ($) | 0 | 0 | 0 | 19.4M | 32.9M | 1,268 | 0 |

The nulls are all accounted for:
- `net_charge_offs_12m`: null for 2018-03 to 2018-09 only (it needs the quarter a year earlier; 2018-12 uses
  the cached 2017-12 filing). From 2018-12 on, none.
- `cre_reset_5y`, `home_reset_5y`: null before 2022-03, when the accounts didn't exist. From 2022-03 on, they're
  null 455 times for commercial real estate and 189 for home loans. All of those are a 0 denominator, meaning no
  such loans, except four Railroad Employees quarters in 2022, withheld because the filing gives over 100%.

## Shape and odd values

- **Sizes are heavily right-skewed.** Mean assets are $400 million against a median of $54 million. Peer
  comparisons use medians and the middle half, never means.
- **Most credit unions don't lend to businesses.** Commercial share is 0 for 825 of 1,359 credit-union quarters,
  and only 4 New Mexico credit unions hold SBA or other government-guaranteed loans in 2026-06. A strip plot of
  commercial share will be a pile at zero plus a few dots. The page should say how many are at zero rather than
  draw a band.
- **The reset shares are bimodal**, piled at 0 and 100. Small balances flip between them. That's what the swing
  flags show (Jemez Valley, Cuba, Four Corners).
- **Negative charge-offs (84)** are recoveries bigger than charge-offs over the year. That's allowed by the
  definition (dictionary.json), and the page should say so where one shows.
- **Net worth extremes.** At the top, Telco Roswell was at 30 to 34% in 2023-12 to 2024-12 before it left the
  roster in 2025-03. At the bottom, Fort Bayard was at 2.40% in 2025-03 and left after it; Southwest was at
  6.06 to 6.67% before it left in 2025-09. These are real filings, not data errors. A credit union leaving is
  printed only with a sourced reason (spec).
- **Delinquency.** The Florist reached 9.94% in 2020-03, a small credit union, so a few loans move it. U.S.
  Eagle is at 6.6 to 7.3% from 2025, the highest of any New Mexico credit union over $100 million in assets
  (State Employees is next, at up to 5.1%).
- No guaranteed part exceeds its balance. No placeholder values (-1, 999999). No future quarters.

## Follow-ups

1. Read the 12 latest-quarter zero-reset flags against each filing before the reset section ships.
2. Decide how the page shows commercial share when most peers are at zero (count at zero plus dots, no band).
3. Source the four departures (NCUA merger and liquidation notices) before the page says why any of them left.
4. Rerun this profile on each quarter's build, and compare its null counts with this one.
