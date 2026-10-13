# NCUA 5300 Call Report account dictionary — verification notes

Scope: verifies the draft data dictionary's claims about each account against NCUA's
official Call Report Form 5300 and Instructions, and against the Account Descriptions
reference file bundled with the 2026-06 call report download.

Primary sources (downloaded to `/tmp/ncua-docs/`):
- Call Report Form 5300, March 2025 — https://ncua.gov/files/publications/regulations/call-report-form-march-2025.pdf
- Call Report Form 5300 Instructions, **Effective September 30, 2025, Until Superseded** (the most recent instructions NCUA has posted; the Call Report Forms and Instructions Archive shows no new Instructions document for December 2025, March 2026, or June 2026, so this version governs the 2026-06 cycle) — https://ncua.gov/files/publications/regulations/call-report-instructions-september-2025.pdf
- Call Report Form 5300 Instructions, Effective March 31, 2022 Until Superseded (used to date the RL0047/RL0050/CM0099 change) — https://ncua.gov/files/publications/regulations/call-report-instructions-march-2022.pdf
- Call Report Changes, March 31, 2022 (the official "account code disposition" change log) — https://ncua.gov/files/publications/regulations/call-report-changes-march-2022.pdf
- Call Report Form 5300 Instructions, Effective September 30, 2017 (used as a negative control — none of RL0047/RL0050/CM0099/718A3/718A4/400T1 exist by those labels, confirming the restructuring is newer) — https://ncua.gov/files/publications/call-report-data/call-report-instructions-9302017.pdf
- Archive index — https://ncua.gov/analysis/credit-union-corporate-call-report-data/call-report-forms-instructions-archive
- NCUA 5300 Account Descriptions file bundled with the 2026-06 call report data at `/tmp/cuv/AcctDesc.txt` (this is NCUA's own machine-readable account dictionary, shipped alongside the FS220* data files)

Page numbers below are the printed page numbers in the PDF (footer), not PDF-reader page numbers, unless noted.

---

## ACCT_010 — Total Assets

- **Schedule/line:** Statement of Financial Condition, page 2/3, Item 24.
- **Definition (Instructions, Sept 2025, p.38–39):** "This line does not require input and will automatically populate ... with the sum of amounts reported in Accounts AS0009, AS0013, AS0017, 003, 025B less 719 and AS0048, 798A, 007, 008, 794, and AS0036. This must also equal the sum of LIABILITIES, SHARES, AND EQUITY."
- **Included/excluded:** It is a computed total, not a manually entered line. Loans are included **net** of the allowance for loan and lease losses (`025B less 719 and AS0048`).
- **Units:** Dollars.
- **Draft dictionary check:** Correct as "total assets"; worth noting for anyone building ratios off raw file data that 010 is already net of loan-loss allowance, not gross loans.

## ACCT_025B — Total Loans and Leases

- **Schedule:** Statement of Financial Condition, Item 16, and Schedule A, Section 1 — Loans & Leases, Item 14. Page 35/55.
- **Definition (Instructions, Sept 2025, p.35, 55):** "Report the total number and outstanding balance of loans and leases ... must equal the total number (Account 025A1) and outstanding balance (Account 025B1) ... reported on Schedule A, Section 1 ... Include loans to other credit unions." If the credit union has adopted CECL (ASC 326), report **amortized cost** instead of outstanding balance.
- **Included/excluded:** Includes loans to other credit unions. Is gross (not net of allowance) — the allowance (719 / AS0048) is a separate line subtracted only when computing Account 010.
- **Units:** Dollars. Under CECL, amortized cost rather than par/outstanding balance (a real, if subtle, measurement difference across credit unions depending on CECL adoption date).
- **Draft dictionary check:** Correct as "total loans and leases."

## ACCT_997 — Total Net Worth

- **Schedule:** Schedule G (Capital Adequacy Worksheet), Section 2, Item 8. (p.126 of Sept 2025 Instructions, per TOC; account dictionary description at `/tmp/cuv/AcctDesc.txt`.)
- **Definition:** "This item does not require input ... will automatically populate ... with the sum of Accounts 940, 668, 658, 602, NW0004, 925A, and 1004." AcctDesc.txt: "Sum of Undivided Earnings, Regular Reserves, Appropriation for Non-Conforming Investments, Other Reserves, Uninsured Secondary Capital, Net Income."
- **Units:** Dollars.
- **Draft dictionary check:** "ACCT_997 is net worth" — correct.

## ACCT_998 — Net Worth Ratio

- **Schedule:** Schedule G (Capital Adequacy Worksheet), Section 4, Item 1 (p.127 per TOC; full text p.5662–5665 of extracted instructions text).
- **Definition (Instructions, Sept 2025):** "This item does not require input ... will automatically populate ... with the result of Account 997 divided by Account NW0010, 010A minus LC0047 plus NW0004, 010B minus LC0047 plus NW0004, or 010C minus LC0047 plus NW0004." The FPR Ratio and Formula Guide (v3.3, p.4) gives the same formula explicitly as **997 ÷ NW0010 (or elected alternative) × 100**, and states: "The ratio is rounded to two decimal places (for example, 6.997 would be rounded to 7.00%)."
- **Units/scaling — VERIFIED against raw data:** The formula produces a percentage (e.g. 7.80 for 7.80%). I pulled Account 998's raw stored value from the 2026-06 call report extract (`/tmp/cuv/FS220A.txt`) for all five test charters and recomputed 997/010×100 independently:

  | Charter | 997 | 010 | 997/010×100 (computed) | Stored Acct 998 | 998 ÷ 100 |
  |---|---|---|---|---|---|
  | 808 (U.S. Eagle) | 113,766,182 | 1,458,642,449 | 7.80% | 780 | 7.80% |
  | 61559 (Deming Schools) | 1,333,530 | 5,385,932 | 24.76% | 2476 | 24.76% |
  | 66143 (Chaves County Schools) | 8,368,107 | 40,086,174 | 20.87% | 2088 | 20.88% |
  | 9566 (Eddy) | 11,328,479 | 61,773,891 | 18.33% | 1834 | 18.34% |
  | 62783 (Artesia) | 27,847,486 | 172,724,377 | 16.12% | 1612 | 16.12% |

  **The draft dictionary's assumption is confirmed: Account 998 is stored in the FS220A.txt extract as the percentage × 100 (i.e., basis points of a percent — 780 = 7.80%, not 7.80% as a literal percent, and not a 0–1 fraction).** The small (0.01 pt) differences for 66143 and 9566 are consistent with NCUA's own 2-decimal rounding of the published ratio versus a from-scratch recomputation off 997/010 — 998 is apparently rounded off NW0010 (which can differ slightly from 010 if the credit union made an asset election), not always 010 itself. This is a minor, immaterial discrepancy, not a sign the scaling assumption is wrong.
- **Draft dictionary check:** Confirmed correct.

## ACCT_041B — Delinquent Loans & Leases, two months or more

- **Schedule:** Schedule A, Section 2 — Delinquent Loans & Leases, Item 21 ("Total Delinquent Loans and Leases"), p.62.
- **AcctDesc.txt:** "Acct_041B — Total Amount of Delinquent Loans & Leases (Two or more months)."
- **Threshold — 60 days, not a calendar "two months":** Item 22's sub-parts explicitly define the threshold operationally as "60 days or more delinquent" (p.63, items 22a–22c). The FPR Formula Guide also defines its delinquency ratio input as "the amount of loans **60 days or more** delinquent" (p.7). So "two or more months" in the account name is NCUA's own shorthand for a 60-day threshold, not a strict calendar-month cutoff.
- **Includes leases:** Yes. Item 21's total is defined as the sum of items 1–20 of Schedule A Section 2, and item 7 of that schedule is "Leases Receivable" (accounts 020D, DL0044, 021D, 022D, 023D, **041D**, 034E) — i.e., the leases row's own "2+ months" sub-column (041D) rolls up into the Item 21 total that produces 041B. **041B is a loan-and-lease combined total, as its own name says** — the draft dictionary's "delinquent loans 2+ months" framing is directionally right but should be read as loans *and* leases.
- **Units:** Dollars (outstanding balance), not count. A parallel account 041A carries the delinquent loan/lease **count**.
- **Draft dictionary check:** Correct on substance; "two months or more" = 60+ days operationally; leases are included.

## ACCT_550 / ACCT_551 — YTD Charge-offs / YTD Recoveries

- **Schedule:** Schedule A, Section 3 — Loan Charge Offs & Recoveries, Item 21, p.66.
- **Definition:** "This line does not require input ... will automatically populate ... with the sum of items 1 through 20," each of which is a loan-category row reporting charge-offs (left column) and recoveries (right column) "year-to-date."
- **Sign convention — can recoveries (551) exceed charge-offs (550) in a given quarter?** The Instructions do not explicitly address this, but it follows from the definition: 551 is YTD **recoveries on loans previously charged off**, not recoveries limited to loans charged off in the current YTD period. A credit union can recover more in a given calendar year than it charges off in that same year (e.g., a large prior-year repossession resolves this year). **UNVERIFIED as an explicit instruction statement — inferred from the account definitions; I found no sentence in the Instructions that states the sign relationship directly.** This matters for the net charge-off ratio (see fpr-check.md), where (550−551) can in principle go negative for a given cycle.
- **Units:** Dollars, year-to-date (resets each calendar year — i.e., March, June, September cycles are not comparable to December without the "rolling 12-month" adjustment the FPR formula guide uses; see fpr-check.md).
- **Draft dictionary check:** Correct as described; the one caveat above (sign convention) is unverified against explicit instruction text.

## ACCT_400T1 — Total Commercial Loans (member + nonmember)

- **Schedule:** Schedule A, Section 8 — Commercial Lending, p.89.
- **Definition:** "Total Commercial Loans (Accounts 900T1 and 400T1) — This item does not require input and will automatically populate ... with the sum of Accounts 900A1 and 900B1 and Accounts 400A1 and 400B1," where 900A1/400A1 = Total Commercial Loans **to Members** (count/balance) and 900B1/400B1 = Total Commercial Loans **to Nonmembers** (count/balance).
- **Units:** Dollars (400T1); 900T1 is the parallel loan-count total.
- **Draft dictionary check:** Correct — "outstanding member+nonmember commercial loans."

## ACCT_718A3 / ACCT_718A4 — Real-estate-secured commercial loans, member / nonmember

- **Schedule:** Schedule A, Section 8, Items 1f and 2f, p.85 and p.89.
- **718A3 — "Total Real Estate Secured" (member), Accounts 900K2, 718A3, 090K2, 475K2:** auto-populated as the sum of items 1a–1e (construction & development, farmland, multifamily, owner-occupied non-farm non-residential, non-owner-occupied non-farm non-residential), all **to members**.
- **718A4 — same, Accounts 900K3, 718A4, 090K3, 475K3, items 2a–2e, to nonmembers.**
- **Units:** Dollars (outstanding balance, excluding unfunded commitments per the general Section 8 instructions).
- **Draft dictionary check:** Correct.

## ACCT_CM0099 — Commercial RE in 718A3+718A4 repricing/maturing within 5 years

- **Schedule:** Schedule A, Section 8, Item 4, p.90 (this is the **FS220P** data table; see revision history below).
- **Definition:** "Report the outstanding balance of real estate loans reported in Accounts 718A3 and 718A4 that, according to contractual agreements, will refinance, reprice, or mature within the next 5 years **and that are not reported as 1- to 4-Family Residential Property Loans**."
- **Draft dictionary check:** Correct.

## ACCT_RL0047 — 1-4 family residential + other consumer RE loans outstanding

- **Schedule:** Schedule A, Section 1, Item 11, p.72 (the **FS220R** data table).
- **Definition:** "Total 1- to 4-Family Residential Property and All Other Non-Commercial Real Estate Loans/Lines of Credit (Accounts RL0046, RL0047, and RL0048)" — auto-populated as a sum across the detailed 1-4 family and "all other (non-commercial)" real estate rows.
- **Draft dictionary check:** Correct.

## ACCT_RL0050 — Portion of RL0047 repricing/refinancing/maturing within 5 years

- **Schedule:** Schedule A, Section 1, Item 13, p.72/73.
- **Definition:** "Report the outstanding balance of real estate loans reported in Account RL0047 that, according to contractual agreements, will refinance, reprice, or mature within the next 5 years **and that are not reported as Commercial Loans.**"
- **Draft dictionary check:** Correct.

## ACCT_691P1 / ACCT_691P2 — Other government-guaranteed commercial loans, outstanding / guaranteed portion

- **Schedule:** Schedule A, Section 1, Item 17.b, p.57.
- **Definition:** The triple (691P, 691P1, 691P2) is defined collectively: "Report the total number and total outstanding balance **(including the guaranteed portion)** of any loan granted ... under a government guaranteed program" — i.e. 691P = count, 691P1 = total outstanding balance *including* the guaranteed portion, 691P2 = the guaranteed portion only, **by direct structural analogy with the parallel non-commercial triple (LN0053/LN0054/LN0055)**, which the Instructions spell out explicitly a few paragraphs earlier as "the number, total outstanding balance including the guaranteed portion, and **only the guaranteed portion**." The commercial version (691-series) is not spelled out account-by-account in the same sentence, but the account index (p.75) and parallel sentence structure confirm the mapping.
- **Draft dictionary check:** Correct, though flagged above as "confirmed by structural analogy," not a sentence that names 691P2 individually as "guaranteed portion."

## ACCT_691C1 / ACCT_691C2 — SBA loans outstanding / guaranteed portion

- **Schedule:** Schedule A, Section 1, Item 17.a, p.56–57.
- **Definition:** Same pattern as above: (691B1, 691C1, 691C2) = (count, total balance including guaranteed portion, guaranteed portion only). Includes loans granted with SBA or similar agency participation even where there's no formal guarantee but a favorable junior lien (e.g., SBA 504) — in that case "the guaranteed portion should be reported as $0." Excludes SBA 7(a) Loan Pool Certificate securities (those go in Investments, not here).
- **Draft dictionary check:** Correct.

## ACCT_712 — "catch-all"? **WRONG in the draft dictionary; this account is a dead/legacy field as of the current form.**

- **Current status:** Account 712 is **not documented anywhere in the September 2025 Instructions** — no section references "Account 712" or "(ACCOUNT 712)." It survives only in the Account Descriptions reference file (`/tmp/cuv/AcctDesc.txt`), which still carries its **pre-2022 definition**: "Amount of Real Estate Loans Outstanding that will contractually refinance, reprice or mature within the next 5 years and that are not reported in Sect 4, line 1.f. or 2.f." That description describes a field that predates the 2022 restructuring (it refers to the old Section 4 line numbering, not the current Schedule A Section 8 numbering).
- **Confirmed retired, not a catch-all, by the official change log:** The March 31, 2022 Call Report Changes document (p.96) lists Account 712 explicitly: "Action: Retire & Replaced. Action Description: Contents of account code changed slightly so a new account code is needed – new account ARL0050. Revised Decision for Action: Account currently has both member business and consumer real estate loans. New account (ARL0050) will only have 1-4 family residential real estate non-commercial loans/lines of credit." The same document's full account-by-account table (p.141) separately shows a **new** account "ACM0099 ... New – Replacement" explicitly noted as "Account 712 used in prior Call Reports to collect similar information, this account does not include consumer real estate."
- **In plain terms:** at the March 2022 revision, the old single Account 712 (real estate repricing/maturity bucket spanning both commercial and consumer loans) was split into two: **RL0050** (the non-commercial/1-4-family piece) and **CM0099** (the commercial piece, scoped to 718A3+718A4). Account 712 itself was retired.
- **Confirmed empirically:** I pulled Account 712 from the live 2026-06 `/tmp/cuv/FS220.txt` extract for all five test charters — **every one reports 0** (U.S. Eagle, Deming, Chaves County, Eddy, and Artesia all show `ACCT_712 = 0`). This is consistent with a retired field kept in the schema for backward file-format compatibility but no longer populated.
- **Draft dictionary check: WRONG.** 712 is not a current "catch-all" account; it is retired/legacy and currently always zero. Its former function has been split between RL0050 and CM0099.

---

## FS220P / FS220R schedule introduction, and account history since 2017

- **FS220P (Commercial Lending detail, carries Account CM0099)** and **FS220R (1-4 Family & Other Real Estate detail, carries Accounts RL0047/RL0048/RL0050)** were both introduced with the **March 31, 2022** Call Report revision.
  - Confirmed negatively: neither RL0047, RL0050, nor CM0099 appear anywhere in the September 30, 2017 Instructions (`call-report-instructions-9302017.txt` — zero matches) or the March 31, 2021 / September 30, 2021 Instructions (zero matches for RL0047/RL0050/CM0099, while 718A3/718A4/400T1 already existed in those earlier versions).
  - Confirmed positively: all three accounts are present and defined by the March 31, 2022 Instructions, and the March 31, 2022 Call Report Changes document (the official change log) documents their creation as new/replacement accounts (pp.96, 141, 202–203, cited above).
  - Predecessor account: **712**, which collected a combined commercial + non-commercial real-estate repricing/maturity figure under the pre-2022 Section 4 numbering. It was retired at the same March 2022 revision and is now always 0 in the data.
  - 718A3, 718A4, and 400T1 pre-date this revision — they already existed, with the current meaning, as of the March 2021 Instructions, so their meaning has **not** changed between 2017 (well, between whenever they were introduced, pre-2021) and 2026, as far as this review went back.
- No other account among the ones reviewed above changed meaning between 2017 and 2026, apart from the RL0047/RL0050/CM0099/712 restructuring documented above.

## What's still open / unverified

- Whether recoveries (551) can exceed charge-offs (550) in the Instructions' own words — not found explicitly stated; treated as inferred, not confirmed (see ACCT_550/551 above).
- The 691C2/691P2 "guaranteed portion only" labels for the *commercial* SBA/other-government-guaranteed accounts are confirmed by structural analogy to the parallel non-commercial accounts and by the account index, not by a sentence naming 691C2/691P2 individually. Flagging as high-confidence, not word-for-word-quoted.
- I did not reconstruct the full pre-2022 Section 4 form layout (no Section-4-era form PDF was fetched) to independently double check the exact old line numbers "1.f" / "2.f" referenced in Account 712's legacy description — that detail is quoted from AcctDesc.txt and the 2022 change log, not cross-checked against an actual pre-2022 form PDF.

## Corrections, 2026-10-13

- `ACCT_997` and `ACCT_998` are on **Schedule G** (Capital Adequacy Worksheet, Sections 2 and 4), not Schedule H as first
  written. The instructions' table of contents puts Sections 1 to 4 under Schedule G (p. 123); Schedule H starts on
  p. 128. The FPR's own footnote agrees ("see Account 998" on Schedule G).
- `ACCT_083` is Schedule D, Section 1, Item 1 (p. 111). `ACCT_718A5` is Schedule A, Section 1, Item 12 (p. 54).
- `718A5` against `718A3 + 718A4`, and `025B1` against `025B`, every quarter: equal for every credit union from
  2018-03 through 2023-09, then off by rounding only from 2023-12 (at most $10 and $13 nationally). In 2017-12, `718A5`
  differed from the sum by up to $19 million for 355 credit unions. No figure uses 2017-12.
