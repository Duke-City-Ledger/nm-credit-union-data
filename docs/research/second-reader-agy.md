# NCUA 5300 Call Report Account Code Mapping (June 2026 Dictionary)

This document maps thirteen plain-language credit union financial and operational measures to NCUA Form 5300 Call Report account codes based strictly on the June 2026 account dictionary (`AcctDesc.txt`) and associated table header definitions (`header-<TABLE>.txt`).

---

## 1. Summary Mapping Table

| # | Plain-Language Measure | Account Code(s) & Formula | Table File | Exact `AcctDesc` Description | Expected Units / Scaling | Confidence | Alternatives & Ambiguity Flags |
|---|---|---|---|---|---|---|---|
| **1** | Total assets | `Acct_010` | `FS220` (`header-FS220.txt`) | `"TOTAL ASSETS"` | Whole dollars ($ USD) | **High**: Definitive balance sheet asset total line item. | `Acct_010A` (Daily average), `Acct_010B` (3-mo end average), `Acct_010C` (4-qtr end average) in `FS220A`; `Acct_NW0010` (Assets excl. PPP pledged) in `FS220N`. |
| **2** | Total loans and leases | Primary: `Acct_025B`<br>Schedule A: `Acct_025B1` | `FS220` (`header-FS220.txt`)<br>`FS220L` (`header-FS220L.txt`) | `Acct_025B`: `"Total amount of Loans and Leases"`<br>`Acct_025B1`: `"Total Amount of Loans & Leases on Loan Schedule"` | Whole dollars ($ USD) | **High**: Core balance sheet line (`025B`) matches loan schedule total (`025B1`). | `Acct_025B` (Balance Sheet, FS220) vs `Acct_025B1` (Loan Schedule, FS220L). Count counterparts: `Acct_025A` (FS220) and `Acct_025A1` (FS220L). Risk-based capital schedule: `ACCT_RB0079` (FS220R). |
| **3** | Net worth dollars and net worth ratio percent | Dollars: `Acct_997`<br>Ratio: `Acct_998`<br>Formula: `Acct_997 / Acct_010` (or direct `Acct_998`) | `FS220A` (`header-FS220A.txt`) | `Acct_997`: `"Sum of Undivided Earnings, Regular Reserves, Appropriation for Non-Conforming Investments, Other Reserves, Uninsured Secondary Capital, Net Income."`<br>`Acct_998`: `"Net Worth divided by Total Assets"` | Dollars: Whole dollars ($ USD)<br>Ratio: Basis points (percentage $\times$ 100, e.g., $11.64\% = 1164$) | **High**: Statutory definitions under 12 CFR Part 702. Scaling inferable from dictionary rate conventions and verified against Call Report filings. | `Acct_940` (Undivided Earnings alone); `Acct_014` (Total Equity including AOCI, which is excluded from regulatory Net Worth); Alternative RBNW/CCULR metrics: `Acct_999`, `ACCT_LR0001`, `ACCT_RB0172`. |
| **4** | Delinquent loans two months or more past due, as share of total loans | Numerator: `Acct_041B`<br>Denominator: `Acct_025B` (or `Acct_025B1`)<br>Formula: `Acct_041B / Acct_025B` | Numerator: `FS220`<br>Denominator: `FS220` (or `FS220L`) | `Acct_041B`: `"Report the dollar amount of delinquent loans by categories."`<br>(AcctName: `"Total Amount of Delinquent Loans & Leases (Two or more months)"`) | Decimal ratio (e.g., $0.0085$) or percentage ($0.85\%$). Input accounts are whole dollars ($ USD). | **High**: `041B` is the universal $\ge 60$ days delinquent total; no precomputed ratio account exists in Call Report. | Number of delinquent loans: `Acct_041A` (FS220A). Collateral/aging breakdown: `ACCT_DL0141`–`ACCT_DL0147` in `FS220P` (which explicitly cross-reference `Account 041B`). |
| **5** | Net charge-offs year to date | Gross Charge-Offs: `Acct_550`<br>Recoveries: `Acct_551`<br>Formula: `Acct_550 - Acct_551` | `FS220` (`header-FS220.txt`) | `Acct_550`: `"Report the dollar amount of loans charged off year-to-date."`<br>`Acct_551`: `"Report the dollar amount of loan recoveries made year-to-date."` | Whole dollars ($ USD) | **High**: Standard accounting identity; NCUA reports gross charge-offs and recoveries separately. | Taking `Acct_550` alone gives gross charge-offs, not net. Loan loss provision on income statement (`Acct_300` / `Acct_IS0011`) represents accrual expense, not realized charge-offs. Schedule P granular charge-offs/recoveries (`ACCT_CH0007`–`ACCT_CH0048`). |
| **6** | Commercial loans outstanding (member + nonmember) as share of assets | Numerator: `Acct_400T1`<br>(or `Acct_400A1 + Acct_400B1`)<br>Denominator: `Acct_010`<br>Formula: `Acct_400T1 / Acct_010` | Numerator: `FS220L`<br>Denominator: `FS220` | `Acct_400T1`: `"Outstanding balance of all member and non-member commercial loans"`<br>`Acct_400A1`: `"Total outstanding balance of commercial loans to members"`<br>`Acct_400B1`: `"Total outstanding balance of nonmember commercial loans"` | Decimal ratio or percentage. Input accounts are whole dollars ($ USD). | **High**: `Acct_400T1` in `FS220L` is the exact sum of member and nonmember commercial loans under Part 723 rules. | Statutory Member Business Loan cap line: `Acct_400A` (`FS220`, Net MBL Balance) which excludes nonmember commercial loans and certain residential commercial loans; legacy total `Acct_400T` (`FS220H`, retired); RBC schedule `ACCT_RB0068` (`FS220R`). |
| **7** | Commercial real estate loans outstanding (member + nonmember) | Direct total: `Acct_718A5`<br>Component formula: `Acct_718A3 + Acct_718A4` | `FS220L` (`header-FS220L.txt`) | `Acct_718A5`: `"Amount of Commercial Loans/Lines of Credit Real Estate Secured"`<br>`Acct_718A3`: `"Total Outstanding Balance of real estate secured member commercial loans"`<br>`Acct_718A4`: `"Total Outstanding Balance of real estate secured nonmember commercial loans"` | Whole dollars ($ USD) | **High**: `718A5` directly reflects total real estate secured commercial credit, exactly matching `718A3 + 718A4`. | Detailed collateral breakdowns: Owner-occupied (`400H2` + `400H3`), Non-owner occupied (`400J2` + `400J3`), Multifamily (`400M` + `400M1`), Farmland (`042A5` + `042A7`). Inactive legacy accounts: `Acct_718A1`, `Acct_718A2` (FS220H). |
| **8** | Commercial real estate loans repricing, refinancing, or maturing within 5 years | `ACCT_CM0099` | `FS220P` (`header-FS220P.txt`) | `"Amount of real estate loans included in Accounts 718A3 and 718A4 above that contractually refinance, reprice, or mature within the next 5 years."` | Whole dollars ($ USD) | **High**: Text explicitly cites the exact parent accounts (`718A3` and `718A4`) identified in Measure 7. | Located in table `FS220P` rather than `FS220L`. Do not confuse with consumer/residential real estate 5-year repricing (`ACCT_RL0050`) or legacy real estate repricing (`Acct_712`). |
| **9** | Residential 1-4 family and other consumer real estate loans outstanding, and part repricing/refinancing/maturing within 5 years | Total Outstanding: `ACCT_RL0047`<br>$\le 5$ Yr Repricing: `ACCT_RL0050`<br>Component formula: `ACCT_RL0016 + ACCT_RL0030 + ACCT_RL0044` | `FS220R` (`header-FS220R.txt`) | `ACCT_RL0047`: `"Total 1- to 4-Family Residential Property and All Other Consumer Real Estate Loans/Lines of Credit - Amount of Loans Outstanding"`<br>`ACCT_RL0050`: `"Real Estate Loans reported in Account RL0047 that contractually refinance, reprice or mature within the next 5 years"` | Whole dollars ($ USD) | **High**: Literal verbatim match to prompt wording for both total and 5-year repricing tranche. | Schedule A (FS220L) accounts `Acct_703A` (1st Lien 1-4 family) and `Acct_386A` (Junior Lien 1-4 family) capture 1-4 family but exclude other consumer RE and lack maturity tranches. Loan count: `ACCT_RL0046`. Legacy inactive: `Acct_712` (FS220). |
| **10** | Commercial loans with federal guarantee other than SBA (outstanding, guaranteed portion) | Outstanding: `Acct_691P1`<br>Guaranteed Portion: `Acct_691P2`<br>Count: `Acct_691P` | `FS220L` (`header-FS220L.txt`) | `Acct_691P1`: `"Outstanding Balance of Commercial Other Government Guaranteed Loans"`<br>`Acct_691P2`: `"Guaranteed Portion of Commercial Other Government Guaranteed Loans"`<br>`Acct_691P`: `"Number of Commercial Other Government Guaranteed Loans Outstanding"` | Whole dollars ($ USD) for `691P1`, `691P2`; integer count for `691P`. | **High**: Exact isolated category for commercial non-SBA government guaranteed loans. | Non-commercial other government guaranteed loans are in `FS220N`: `Acct_LN0054` (balance) and `Acct_LN0055` (guaranteed portion). Inactive legacy accounts: `Acct_1060A`, `Acct_1060B` (FS220L). |
| **11** | SBA-guaranteed loans (outstanding, guaranteed portion) | **Commercial SBA**:<br>Outstanding: `Acct_691C1`<br>Guaranteed: `Acct_691C2`<br>Count: `Acct_691B1`<br><br>**Non-Commercial SBA**:<br>Outstanding: `Acct_LN0051`<br>Guaranteed: `Acct_LN0052`<br>Count: `Acct_LN0050`<br><br>**Combined Total**:<br>Outstanding: `Acct_691C1 + Acct_LN0051`<br>Guaranteed: `Acct_691C2 + Acct_LN0052` | Commercial: `FS220L` (`header-FS220L.txt`)<br><br>Non-Commercial: `FS220N` (`header-FS220N.txt`) | `Acct_691C1`: `"Outstanding Balance of Commercial Small Business Administration Loans"`<br>`Acct_691C2`: `"Guaranteed Portion of Commercial Small Business Administration Loans"`<br>`Acct_LN0051`: `"Outstanding Balance of Non-Commercial Small Business Administration Loans"`<br>`Acct_LN0052`: `"Guaranteed Portion of Non-Commercial Small Business Administration Loans"` | Whole dollars ($ USD) | **Medium-High**: High confidence on exact accounts, but NCUA bifurcates SBA into Commercial (`FS220L`) and Non-Commercial (`FS220N`). | If the measure intends commercial SBA only, use `691C1` / `691C2`. If total institution SBA, sum `691C1 + LN0051` / `691C2 + LN0052`. SBA PPP loans in `FS220N`: `Acct_LN0057`. Legacy inactive: `Acct_400F` (FS220), `Acct_900F` (FS220A). |
| **12** | USDA-guaranteed loans specifically, if any account isolates USDA | **None** (No dedicated account isolates USDA) | N/A (Pooled in `FS220L` and `FS220N`) | N/A (The string `"USDA"`, `"Rural Development"`, and `"Farm Service Agency"` do not appear in `AcctDesc.txt`) | N/A | **High (Negative determination)**: Dictionary confirmed to contain zero USDA-specific fields. | USDA commercial loans are pooled into Commercial Other Government Guaranteed Loans (`Acct_691P1` / `Acct_691P2` in `FS220L`). USDA residential loans (e.g. Section 502) are pooled into Non-Commercial Other Government Guaranteed Loans (`Acct_LN0054` / `Acct_LN0055` in `FS220N`) or standard 1-4 family mortgages. General agricultural loans (`Acct_042A9`, `FS220L`) do not isolate guarantees. |
| **13** | Number of members | `Acct_083` | `FS220` (`header-FS220.txt`) | `"Report the number of credit union members. Report the actual number of members, not the number of accounts."`<br>(AcctName: `"Number of current members (not number of accounts)"`) | Integer count (actual member count) | **High**: Definitive institutional membership count. | `Acct_084` (`FS220`): `"Number of potential members"` (Field of membership estimate including current members). `Acct_086` (`FS220B`): Members added via streamlined expansion. |

---

## 2. Detailed Technical Notes by Measure

### Measure 1: Total Assets
- **Primary Code**: `Acct_010`
- **Table File**: `FS220.txt` (header: `header-FS220.txt`)
- **Exact Short Name (`AcctName`)**: `TOTAL ASSETS`
- **Exact Description (`AcctDesc`)**: `TOTAL ASSETS`
- **Formula**: `Acct_010`
- **Expected Units / Scaling**: Whole dollars ($ USD).
- **Confidence**: **High**. This is the anchor account of the Statement of Financial Condition (Assets line item 26).
- **Alternatives & Nuances**:
  - `Acct_010A` (Table `FS220A`): Average daily assets over the quarter.
  - `Acct_010B` (Table `FS220A`): Average of three month-end balances.
  - `Acct_010C` (Table `FS220A`): Average of previous four quarter-end balances.
  - `Acct_NW0010` (Table `FS220N`): Total assets excluding SBA PPP loans pledged as collateral to the FRB PPP Liquidity Facility (used for statutory net worth ratio calculations under regulatory relief provisions).
  - CUSO total asset accounts (`Acct_846A` through `Acct_846T` in `FS220G`).

---

### Measure 2: Total Loans and Leases
- **Primary Code**: `Acct_025B` (Balance Sheet) or `Acct_025B1` (Loan Schedule A)
- **Table File**: `FS220.txt` (`Acct_025B`) and `FS220L.txt` (`Acct_025B1`)
- **Exact Short Name (`AcctName`)**:
  - `Acct_025B`: `Total amount of Loans and Leases`
  - `Acct_025B1`: `Total Amount of Loans & Leases on Loan Schedule`
- **Exact Description (`AcctDesc`)**:
  - `Acct_025B`: `Total amount of Loans and Leases`
  - `Acct_025B1`: `Total Amount of Loans & Leases on Loan Schedule`
- **Formula**: `Acct_025B` (or `Acct_025B1`)
- **Expected Units / Scaling**: Whole dollars ($ USD).
- **Confidence**: **High**.
- **Alternatives & Nuances**:
  - Both accounts represent the exact same aggregate portfolio dollar total. In Call Report validation, `Acct_025B` on Page 2 must equal `Acct_025B1` on Schedule A Section 1 Line 27.
  - If a measure requires the **number** of loans rather than dollars:
    - `Acct_025A` in `FS220`: `Total number of Loans and Leases`
    - `Acct_025A1` in `FS220L`: `Total Number of Loans & Leases on Loan Schedule`
  - Risk-Based Capital schedule: `ACCT_RB0079` (`RBC Schedule Total Loans` in `FS220R`).

---

### Measure 3: Net Worth Dollars and Net Worth Ratio Percent
- **Primary Codes**:
  - Net Worth Dollars: `Acct_997`
  - Net Worth Ratio Percent: `Acct_998`
- **Table File**: `FS220A.txt` (header: `header-FS220A.txt`)
- **Exact Short Name (`AcctName`)**:
  - `Acct_997`: `Total Net Worth`
  - `Acct_998`: `Net Worth Ratio`
- **Exact Description (`AcctDesc`)**:
  - `Acct_997`: `Sum of Undivided Earnings, Regular Reserves, Appropriation for Non-Conforming Investments, Other Reserves, Uninsured Secondary Capital, Net Income.`
  - `Acct_998`: `Net Worth divided by Total Assets`
- **Formula**:
  - Net Worth Dollars: `Acct_997`
  - Net Worth Ratio: Reported directly in `Acct_998`, or calculated as `Acct_997 / Acct_010`.
- **Expected Units / Scaling**:
  - Net Worth Dollars: Whole dollars ($ USD).
  - Net Worth Ratio: In the raw Call Report data table (`FS220A.txt`), `Acct_998` is formatted as an integer scaled in **basis points** (percentage multiplied by 100 with no decimal point). For example, a ratio of $11.64\%$ is stored as `1164` (and $9.84\%$ is stored as `984`). To convert to a percentage, divide by 100 ($1164 / 100 = 11.64\%$). To convert to a decimal ratio, divide by 10,000 ($1164 / 10000 = 0.1164$). This aligns with the dictionary's explicit rate convention in accounts `532`, `547`, `552`, and `553` stating: `"Rates should be stated in terms of basis points (i.e., 6.5% = 0650)"`.
- **Confidence**: **High**.
- **Alternatives & Nuances**:
  - Regulatory Net Worth under 12 CFR Part 702 explicitly excludes Accumulated Other Comprehensive Income (AOCI) / unrealized gains/losses on available-for-sale securities. Analysts seeking GAAP Total Equity rather than regulatory net worth would use `Acct_014` (`TOTAL LIABILITIES, SHARES, AND EQUITY`) minus total liabilities and shares.
  - Undivided Earnings alone is `Acct_940` (Table `FS220`).
  - Risk-Based Capital / Complex Credit Union Leverage Ratio (CCULR): `ACCT_LR0001` (election) and `ACCT_RB0172` (`RBC Total Risk Based Capital Ratio` in `FS220R`).

---

### Measure 4: Delinquent Loans ($\ge 2$ Months Past Due) as Share of Total Loans
- **Primary Codes**:
  - Delinquent Loans: `Acct_041B`
  - Total Loans: `Acct_025B` (or `Acct_025B1`)
- **Table Files**:
  - Numerator (`Acct_041B`): `FS220.txt` (header: `header-FS220.txt`)
  - Denominator (`Acct_025B`): `FS220.txt` (header: `header-FS220.txt`)
- **Exact Short Name (`AcctName`)**:
  - `Acct_041B`: `Total Amount of Delinquent Loans & Leases (Two or more months)`
  - `Acct_025B`: `Total amount of Loans and Leases`
- **Exact Description (`AcctDesc`)**:
  - `Acct_041B`: `Report the dollar amount of delinquent loans by categories.`
  - `Acct_025B`: `Total amount of Loans and Leases`
- **Formula**: `Acct_041B / Acct_025B` (or `Acct_041B / Acct_025B1`)
- **Expected Units / Scaling**: Decimal ratio ($0.0085$) or percentage ($0.85\%$). Numerator and denominator are in whole dollars ($ USD).
- **Confidence**: **High**.
- **Alternatives & Nuances**:
  - There is no single precomputed ratio code in the Call Report for total delinquency rate; it must be calculated using this formula.
  - `Acct_041A` (Table `FS220A`): `Number of Total Delinquent Loans & Leases (Two or more months)` provides the delinquency count rather than dollar volume.
  - Detailed delinquency aging by collateral is provided on Schedule B (`FS220P`), where accounts `ACCT_DL0142` and `ACCT_DL0144` explicitly note that their amounts are included in `"Total Delinquent Loans and Leases (Account 041B)"`.

---

### Measure 5: Net Charge-Offs Year to Date
- **Primary Codes**:
  - Gross Charge-Offs YTD: `Acct_550`
  - Recoveries YTD: `Acct_551`
- **Table File**: `FS220.txt` (header: `header-FS220.txt`)
- **Exact Short Name (`AcctName`)**:
  - `Acct_550`: `Total Amount of All Loans Charged Off Year-to-Date`
  - `Acct_551`: `Total Amount of All Year-to-Date Recoveries on Charged-Off Loans`
- **Exact Description (`AcctDesc`)**:
  - `Acct_550`: `Report the dollar amount of loans charged off year-to-date.`
  - `Acct_551`: `Report the dollar amount of loan recoveries made year-to-date.`
- **Formula**: `Acct_550 - Acct_551`
- **Expected Units / Scaling**: Whole dollars ($ USD).
- **Confidence**: **High**.
- **Alternatives & Nuances**:
  - NCUA does not provide a single net charge-offs line item on the Call Report. Failing to subtract recoveries (`Acct_551`) from gross charge-offs (`Acct_550`) is a common pitfall.
  - Loan Loss Provision Expense: Under CECL/GAAP, provision expense on the Statement of Income (`Acct_IS0011` in `FS220N` or legacy `Acct_300` in `FS220`) is an accounting accrual adding to the Allowance for Credit Losses (ACL), not actual cash charge-offs.
  - Schedule P (`FS220P`) provides granular YTD charge-offs and recoveries by loan collateral type (`ACCT_CH0007` through `ACCT_CH0048`), which sum up to `Acct_550` and `Acct_551`.

---

### Measure 6: Commercial Loans Outstanding (Member + Nonmember) as Share of Assets
- **Primary Codes**:
  - Numerator (Commercial Loans Outstanding): `Acct_400T1` (or `Acct_400A1 + Acct_400B1`)
  - Denominator (Total Assets): `Acct_010`
- **Table Files**:
  - Numerator: `FS220L.txt` (header: `header-FS220L.txt`)
  - Denominator: `FS220.txt` (header: `header-FS220.txt`)
- **Exact Short Name (`AcctName`)**:
  - `Acct_400T1`: `Outstanding balance of all member and non-member commercial loans`
  - `Acct_400A1`: `Total outstanding balance of commercial loans to members`
  - `Acct_400B1`: `Total outstanding balance of nonmember commercial loans`
  - `Acct_010`: `TOTAL ASSETS`
- **Exact Description (`AcctDesc`)**:
  - `Acct_400T1`: `Outstanding balance of all member and non-member commercial loans`
  - `Acct_400A1`: `Total outstanding balance of commercial loans to members`
  - `Acct_400B1`: `Total outstanding balance of nonmember commercial loans`
- **Formula**: `Acct_400T1 / Acct_010` (or `(Acct_400A1 + Acct_400B1) / Acct_010`)
- **Expected Units / Scaling**: Decimal ratio or percentage. Input accounts are whole dollars ($ USD).
- **Confidence**: **High**.
- **Alternatives & Nuances**:
  - **Critical Disambiguation (Commercial Loans vs. Member Business Loans)**: Under NCUA Part 723 rules (revised 2017), "Commercial Loans" and "Member Business Loans" (MBL) are distinct concepts.
    - `Acct_400A` (`FS220`): `Net Member Business Loan Balance` is the statutory MBL figure subject to the aggregate cap of $1.75\times$ net worth under 12 U.S.C. § 1757a. It excludes nonmember commercial loans, deducts government guarantees, and excludes 1-4 family commercial loans. Using `Acct_400A` would materially understate total commercial lending.
    - `Acct_400T` (`FS220H`): `Amount of total business loans outstanding` is an obsolete/inactive account (`STATUS="False"`).
    - `ACCT_RB0068` (`FS220R`): `RBC Schedule Total Commercial Loans` is used in Risk-Based Capital risk weighting.

---

### Measure 7: Commercial Real Estate Loans Outstanding (Member + Nonmember)
- **Primary Codes**:
  - Combined Total Account: `Acct_718A5`
  - Component Accounts: `Acct_718A3` (Member) and `Acct_718A4` (Nonmember)
- **Table File**: `FS220L.txt` (header: `header-FS220L.txt`)
- **Exact Short Name (`AcctName`)**:
  - `Acct_718A5`: `Amount of Commercial Loans/Lines of Credit Real Estate Secured`
  - `Acct_718A3`: `Total Outstanding Balance of real estate secured member commercial loans`
  - `Acct_718A4`: `Total Outstanding Balance of real estate secured nonmember commercial loans`
- **Exact Description (`AcctDesc`)**:
  - `Acct_718A5`: `Amount of Commercial Loans/Lines of Credit Real Estate Secured`
  - `Acct_718A3`: `Total Outstanding Balance of real estate secured member commercial loans`
  - `Acct_718A4`: `Total Outstanding Balance of real estate secured nonmember commercial loans`
- **Formula**: `Acct_718A5` (or `Acct_718A3 + Acct_718A4`)
- **Expected Units / Scaling**: Whole dollars ($ USD).
- **Confidence**: **High**.
- **Alternatives & Nuances**:
  - `Acct_718A5` directly consolidates all real estate secured commercial credit, exactly matching the sum of `Acct_718A3` (member) and `Acct_718A4` (nonmember).
  - Together with `Acct_400P` (`Amount of Commercial Loans/Lines of Credit Not Real Estate Secured`), it reconciles to total commercial loans: `Acct_718A5 + Acct_400P = Acct_400T1`.
  - Granular property subcategories in `FS220L`:
    - Construction & Development: `Acct_143A3` / `Acct_691L9`
    - Farmland: `Acct_042A5` (member) + `Acct_042A7` (nonmember)
    - Multifamily: `Acct_400M` (member) + `Acct_400M1` (nonmember)
    - Owner-Occupied Non-Farm Non-Residential: `Acct_400H2` (member) + `Acct_400H3` (nonmember)
    - Non-Owner Occupied Non-Farm Non-Residential: `Acct_400J2` (member) + `Acct_400J3` (nonmember)
  - Inactive legacy accounts: `Acct_718A1` and `Acct_718A2` (Table `FS220H`, `STATUS="False"`).

---

### Measure 8: Commercial Real Estate Loans Repricing, Refinancing, or Maturing Within 5 Years
- **Primary Code**: `ACCT_CM0099`
- **Table File**: `FS220P.txt` (header: `header-FS220P.txt`)
- **Exact Short Name (`AcctName`)**: `Amount of real estate loans included in Accounts 718A3 and 718A4 above that contractually refinance, reprice, or mature within the next 5 years.`
- **Exact Description (`AcctDesc`)**: `Amount of real estate loans included in Accounts 718A3 and 718A4 above that contractually refinance, reprice, or mature within the next 5 years.`
- **Formula**: `ACCT_CM0099`
- **Expected Units / Scaling**: Whole dollars ($ USD).
- **Confidence**: **High**.
- **Alternatives & Nuances**:
  - The dictionary description explicitly identifies this field as the $\le 5$ year maturity/repricing bucket for the exact accounts from Measure 7 (`718A3` and `718A4`).
  - **Structural Quirk**: While parent accounts `718A3`, `718A4`, and `718A5` are housed in Table `FS220L` (Commercial Loan Schedule), this 5-year repricing tranche is housed in Table `FS220P` (Delinquency and Loan Loss Information).
  - Do not confuse with consumer/residential real estate 5-year repricing (`ACCT_RL0050` in `FS220R`), nor with the retired legacy account `Acct_712` in `FS220` (`STATUS="False"`).

---

### Measure 9: Residential 1-4 Family and Other Consumer Real Estate Loans Outstanding, and Part Repricing/Refinancing/Maturing Within 5 Years
- **Primary Codes**:
  - Total Outstanding: `ACCT_RL0047`
  - Part Repricing/Refinancing/Maturing $\le 5$ Years: `ACCT_RL0050`
- **Table File**: `FS220R.txt` (header: `header-FS220R.txt`)
- **Exact Short Name (`AcctName`)**:
  - `ACCT_RL0047`: `Total 1- to 4-Family Residential Property and All Other Consumer Real Estate Loans/Lines of Credit - Amount of Loans Outstanding`
  - `ACCT_RL0050`: `Real Estate Loans reported in Account RL0047 that contractually refinance, reprice or mature within the next 5 years`
- **Exact Description (`AcctDesc`)**:
  - `ACCT_RL0047`: `Total 1- to 4-Family Residential Property and All Other Consumer Real Estate Loans/Lines of Credit - Amount of Loans Outstanding`
  - `ACCT_RL0050`: `Real Estate Loans reported in Account RL0047 that contractually refinance, reprice or mature within the next 5 years`
- **Formula**:
  - Total Outstanding: `ACCT_RL0047` (or component sum `ACCT_RL0016 + ACCT_RL0030 + ACCT_RL0044`)
  - Repricing $\le 5$ Years: `ACCT_RL0050`
- **Expected Units / Scaling**: Whole dollars ($ USD).
- **Confidence**: **High**. Literal verbatim match to the requested measure.
- **Alternatives & Nuances**:
  - `ACCT_RL0047` synthesizes three distinct categories defined in `FS220R`:
    1. `ACCT_RL0016`: 1- to 4-Family 1st Lien total loans outstanding.
    2. `ACCT_RL0030`: 1- to 4-Family Junior Lien total loans outstanding.
    3. `ACCT_RL0044`: All Other (Non-commercial) Real Estate total loans outstanding.
  - Schedule A (`FS220L`) provides:
    - `Acct_703A`: `Amount of Total Loans/Lines of Credit Secured by 1st Lien 1-4 Family Residential Properties`
    - `Acct_386A`: `Amount of Total Loans/Lines of Credit Secured by Junior Lien 1-4 Family Residential Properties`
    - However, summing `703A + 386A` omits "All Other Consumer Real Estate" and does not provide the corresponding 5-year repricing tranche.
  - Number of loans counterpart: `ACCT_RL0046` (Table `FS220R`).
  - Inactive legacy account: `Acct_712` (Table `FS220`, `STATUS="False"`).

---

### Measure 10: Commercial Loans with a Federal Guarantee Other than SBA (Outstanding, Guaranteed Portion)
- **Primary Codes**:
  - Outstanding Balance: `Acct_691P1`
  - Guaranteed Portion: `Acct_691P2`
  - Number of Loans: `Acct_691P`
- **Table File**: `FS220L.txt` (header: `header-FS220L.txt`)
- **Exact Short Name (`AcctName`)**:
  - `Acct_691P1`: `Outstanding Balance of Commercial Other Government Guaranteed Loans`
  - `Acct_691P2`: `Guaranteed Portion of Commercial Other Government Guaranteed Loans`
  - `Acct_691P`: `Number of Commercial Other Government Guaranteed Loans Outstanding`
- **Exact Description (`AcctDesc`)**:
  - `Acct_691P1`: `Outstanding Balance of Commercial Other Government Guaranteed Loans`
  - `Acct_691P2`: `Guaranteed Portion of Commercial Other Government Guaranteed Loans`
  - `Acct_691P`: `Number of Commercial Other Government Guaranteed Loans Outstanding`
- **Formula**:
  - Outstanding: `Acct_691P1`
  - Guaranteed Portion: `Acct_691P2`
- **Expected Units / Scaling**: Whole dollars ($ USD) for `691P1` and `691P2`; integer count for `691P`.
- **Confidence**: **High**.
- **Alternatives & Nuances**:
  - If non-commercial loans are desired, they are reported in Table `FS220N`:
    - `Acct_LN0054`: `Outstanding Balance of Non-Commercial Other Government Guaranteed Loans`
    - `Acct_LN0055`: `Guaranteed Portion of Non-Commercial Other Government Guaranteed Loans`
    - `Acct_LN0053`: `Number of Non-Commercial Other Government Guaranteed Loans`
  - Retired legacy accounts: `Acct_1060`, `Acct_1060A`, `Acct_1060B` (Table `FS220L`, `STATUS="False"`).

---

### Measure 11: SBA-Guaranteed Loans (Outstanding, Guaranteed Portion)
- **Primary Codes**:
  - **Commercial SBA**:
    - Outstanding Balance: `Acct_691C1`
    - Guaranteed Portion: `Acct_691C2`
    - Number of Loans: `Acct_691B1`
    - Table: `FS220L.txt` (header: `header-FS220L.txt`)
  - **Non-Commercial SBA**:
    - Outstanding Balance: `Acct_LN0051`
    - Guaranteed Portion: `Acct_LN0052`
    - Number of Loans: `Acct_LN0050`
    - Table: `FS220N.txt` (header: `header-FS220N.txt`)
  - **Total SBA Portfolio (Commercial + Non-Commercial)**:
    - Total Outstanding: `Acct_691C1 + Acct_LN0051`
    - Total Guaranteed Portion: `Acct_691C2 + Acct_LN0052`
    - Total Count: `Acct_691B1 + Acct_LN0050`
- **Exact Short Name (`AcctName`)**:
  - `Acct_691C1`: `Outstanding Balance of Commercial Small Business Administration Loans`
  - `Acct_691C2`: `Guaranteed Portion of Commercial Small Business Administration Loans`
  - `Acct_691B1`: `Number of Commercial Small Business Administration Loans Outstanding`
  - `Acct_LN0051`: `Outstanding Balance of Non-Commercial Small Business Administration Loans`
  - `Acct_LN0052`: `Guaranteed Portion of Non-Commercial Small Business Administration Loans`
  - `Acct_LN0050`: `Number of Non-Commercial Small Business Administration Loans`
- **Exact Description (`AcctDesc`)**:
  - `Acct_691C1`: `Outstanding Balance of Commercial Small Business Administration Loans`
  - `Acct_691C2`: `Guaranteed Portion of Commercial Small Business Administration Loans`
  - `Acct_691B1`: `Number of Commercial Small Business Administration Loans Outstanding`
  - `Acct_LN0051`: `Outstanding Balance of Non-Commercial Small Business Administration Loans`
  - `Acct_LN0052`: `Guaranteed Portion of Non-Commercial Small Business Administration Loans`
  - `Acct_LN0050`: `Number of Non-Commercial Small Business Administration Loans`
- **Formula**:
  - If commercial only: `Acct_691C1` (outstanding) and `Acct_691C2` (guaranteed).
  - If institution-wide: `Acct_691C1 + Acct_LN0051` (outstanding) and `Acct_691C2 + Acct_LN0052` (guaranteed).
- **Expected Units / Scaling**: Whole dollars ($ USD).
- **Confidence**: **Medium-High**. The accounts are definitive, but the user must choose between the commercial schedule (`FS220L`), the consumer schedule (`FS220N`), or their aggregate.
- **Alternatives & Nuances**:
  - SBA Paycheck Protection Program (PPP) loans in Table `FS220N`:
    - `Acct_LN0057`: `Outstanding Balance of Small Business Administration Paycheck Protection Program Loans`
    - `Acct_LN0056`: `Number of Small Business Administration Paycheck Protection Program Loans`
    - `Acct_LC0047`: PPP loans pledged to Federal Reserve Bank PPP Liquidity Facility.
  - Inactive legacy accounts:
    - `Acct_400F` (Table `FS220`, `STATUS="False"`): `Amount of Small Business Administration Loans Outstanding`
    - `Acct_900F` (Table `FS220A`, `STATUS="False"`): `Number of Small Business Administration Loans Outstanding`

---

### Measure 12: USDA-Guaranteed Loans Specifically (If Any Account Isolates USDA)
- **Primary Code**: **None** (No dedicated account exists).
- **Table File**: N/A (pooled in `FS220L.txt` and `FS220N.txt`).
- **Exact Description (`AcctDesc`)**: N/A
- **Formula**: Not directly available; bundled into general government guarantee line items.
- **Expected Units / Scaling**: N/A
- **Confidence**: **High (Negative Determination)**. A comprehensive search of `AcctDesc.txt` for terms such as `USDA`, `United States Department of Agriculture`, `Farm Service Agency`, `FSA`, `Rural Development`, and `Rural Housing` yields zero matching accounts.
- **Alternatives & Nuances**:
  - USDA-guaranteed commercial loans (e.g., USDA Business & Industry Guaranteed Loans or FSA guaranteed farm operating/ownership loans) are reported under:
    - `Acct_691P1` (`Outstanding Balance of Commercial Other Government Guaranteed Loans`, Table `FS220L`)
    - `Acct_691P2` (`Guaranteed Portion of Commercial Other Government Guaranteed Loans`, Table `FS220L`)
  - USDA-guaranteed non-commercial/residential loans (e.g., USDA Single Family Housing Guaranteed Loan Program under Section 502) are reported under:
    - `Acct_LN0054` (`Outstanding Balance of Non-Commercial Other Government Guaranteed Loans`, Table `FS220N`)
    - `Acct_LN0055` (`Guaranteed Portion of Non-Commercial Other Government Guaranteed Loans`, Table `FS220N`)
  - General agricultural loans in `FS220L` (e.g. `Acct_042A5` farmland, `Acct_042A6` production, and `Acct_042A9` total agricultural commercial loans) capture agricultural purpose, but do not separate guaranteed from unguaranteed debt.

---

### Measure 13: Number of Members
- **Primary Code**: `Acct_083`
- **Table File**: `FS220.txt` (header: `header-FS220.txt`)
- **Exact Short Name (`AcctName`)**: `Number of current members (not number of accounts)`
- **Exact Description (`AcctDesc`)**: `Report the number of credit union members. Report the actual number of members, not the number of accounts.`
- **Formula**: `Acct_083`
- **Expected Units / Scaling**: Integer count.
- **Confidence**: **High**. This is the standard credit union member count field reported on Page 1 (Miscellaneous Information).
- **Alternatives & Nuances**:
  - `Acct_084` (Table `FS220`): `Number of potential members` ("Report the number of potential credit union members. Include current members in this estimate..."). This represents the credit union's field of membership (FOM) potential reach based on census or corporate sponsor data, rather than actual joining members.
  - `Acct_086` (Table `FS220B`, `STATUS="False"`): Historical count of members added through streamlined FOM expansions.
  - `Acct_900A1` / `Acct_025A`: Counts of member commercial loans or total loans, not members themselves.

---

## 3. Confusing, Ambiguous, and Notable Elements in the NCUA Dictionary

Working directly with `AcctDesc.txt` and the `header-<TABLE>.txt` files reveals several systemic architectural quirks, ambiguities, and potential pitfalls:

### 1. Retention of Inactive / Historical Accounts (`STATUS="False"`)
`AcctDesc.txt` contains extensive legacy accounts alongside current accounts. Over a third of accounts in certain tables have `STATUS="False"`.
- If an analyst greps for "Small Business Administration Loans", they find `Acct_400F` ("Amount of Small Business Administration Loans Outstanding" in `FS220`), which looks like an ideal single-line balance sheet total. However, `Acct_400F` is inactive (`STATUS="False"`); the active accounts are `Acct_691C1` (`FS220L`) and `Acct_LN0051` (`FS220N`).
- Similarly, searching for "Total Business Loans" surfaces `Acct_400T` (`FS220H`), which is inactive, while the active line is `Acct_400T1` (`FS220L`).
- `Acct_712` ("Amount of Real Estate Loans Outstanding that will contractually refinance, reprice or mature within the next 5 years") in `FS220` is inactive (`STATUS="False"`), having been superseded by `ACCT_CM0099` (`FS220P`) for commercial real estate and `ACCT_RL0050` (`FS220R`) for consumer real estate.

### 2. Semantic Collision: "Member Business Loans" (MBL) vs. "Commercial Loans"
Following the 2017/2018 NCUA Part 723 overhaul, NCUA transitioned from a framework based solely on Member Business Loans (MBL) to one centered on Commercial Loans. However, the Call Report retains both:
- `Acct_400A` (`FS220`): "Net Member Business Loan Balance" is kept specifically to enforce the statutory aggregate MBL cap (the lesser of $1.75\times$ net worth or $12.25\%$ of total assets). It deducts government guarantees and excludes nonmember business loans.
- `Acct_400T1` (`FS220L`): "Outstanding balance of all member and non-member commercial loans" captures actual total commercial debt.
- In common speech and credit union reporting, people often say "member business loans" when they mean the total commercial lending book. Mapping "commercial loans" to `Acct_400A` will lead to severe undercounting.

### 3. Absence of Agency Granularity for Government Guarantees
NCUA only isolates the **Small Business Administration (SBA)** into its own dedicated account lines.
- All other federal agencies—including the **USDA** (FSA and Rural Development), **FHA**, **VA**, **Department of Energy**, and **Bureau of Indian Affairs**—are lumped together without distinction into "Other Government Guaranteed Loans" (`Acct_691P1` / `Acct_691P2` for commercial; `Acct_LN0054` / `Acct_LN0055` for non-commercial).
- Anyone seeking to monitor USDA agricultural loan exposures or VA mortgage books cannot do so from NCUA Call Report data alone.

### 4. Bizarre Table Fragmentation for Maturity and Repricing Data
There is no centralized Asset-Liability Management (ALM) or maturity table. Instead, $\le 5$-year repricing and maturity data is scattered arbitrarily across separate schedules:
- **Commercial real estate loans repricing within 5 years** (`ACCT_CM0099`) is placed in Table `FS220P`, which is otherwise dedicated to **Delinquency and Loan Loss/Charge-Off Information**.
- **Residential/consumer real estate loans repricing within 5 years** (`ACCT_RL0050`) is placed in Table `FS220R`, which is otherwise dedicated to **Risk-Based Capital (RBC) Risk Weighting Schedules**.
- This creates substantial confusion when building data pipelines, as ALM analysts must extract data from loss and regulatory capital tables to construct interest rate risk models.

### 5. Absence of Explicit Scale / Data-Type Metadata in `AcctDesc.txt`
`AcctDesc.txt` provides no column for data type, decimals, or scaling factor (e.g., Integer, Float, Whole Dollars, Basis Points):
- For certain dividend rate accounts (e.g., `Acct_532`), the text description explicitly documents the scaling convention (`"Rates should be stated in terms of basis points (i.e., 6.5% = 0650)"`).
- However, for calculated ratios such as `Acct_998` ("Net Worth Ratio"), the description simply says `"Net Worth divided by Total Assets"`. Only by inspecting the actual raw values in `FS220A.txt` (or knowing NCUA's legacy 4-digit percentage representation) can one infer that `1164` means $11.64\%$.
- Similarly, count accounts (`Acct_083`, `Acct_025A`) and dollar accounts (`Acct_010`, `Acct_025B`) have no syntactic distinction in the dictionary metadata other than their textual names.

### 6. Missing Net Charge-Offs Summary Account
While Net Charge-Offs is one of the most widely cited credit performance metrics across banking regulators (FDIC, OCC, Fed), NCUA provides no single account code for Net Charge-Offs. Analysts must compute `Acct_550 - Acct_551`.

### 7. Inconsistent Header Casing and Prefixes Across Table Header Files
Column names across `header-<TABLE>.txt` files exhibit inconsistent casing and naming conventions:
- In `header-FS220.txt`, column headers use uppercase prefixes (`"ACCT_010"`, `"ACCT_025B"`, `"ACCT_041B"`), but a few accounts use mixed case (`"Acct_965A"`, `"Acct_1019"`).
- In `header-FS220A.txt`, earlier columns use `"ACCT_001"` through `"ACCT_599"`, but later columns switch to `"Acct_997"`, `"Acct_998"`, and `"Acct_999"`.
- Table `FS220P` uses `"ACCT_CM0099"` and `"Cycle_date"` (mixed case).
- Case-sensitive database ingestion pipelines will fail unless headers are normalized to a consistent case before querying.
