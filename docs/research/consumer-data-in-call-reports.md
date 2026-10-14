# What NCUA's public data can tell someone choosing a credit union

Checked 2026-10-14 against the quarterly zips (2022-06 to 2026-06) and the Call Report instructions effective
Sept. 30, 2025. Counts are credit unions nationally with a non-zero value.

## Loan rates: yes

The instructions (Schedule A, Section 1, "Interest Rates," p. 50): "Report loan interest rates being offered as
of the reporting period for each loan category. Report the actual rate ... If more than one rate applies, report
the most common rate in each loan category." So each is the credit union's most common *offered* rate on the
last day of the quarter, self-reported. The files store it times 100 (`664` is 6.64%).

| Product | Account | Table | Non-zero, 2026-06 | New Mexico, 2026-06 |
|---|---|---|---|---|
| Credit card | `ACCT_521` | FS220 | 2,821 | 23 of 37 (0 means no cards offered) |
| New vehicle | `ACCT_523` | FS220 | 4,137 | 37 of 37, median 5.74% |
| Used vehicle | `ACCT_524` | FS220 | 4,178 | 37 of 37 |
| First-lien 1-4 family (mortgage) | `ACCT_563A` | FS220L | 3,214 | 25 of 37; account from 2022-03 |
| Junior lien (home equity) | `ACCT_562A` | FS220L | 3,016 | from 2022-03 |
| Other unsecured | `ACCT_522` | FS220 | 4,263 | 37 of 37 |

`ACCT_563` (total first mortgage) is zero for everyone from 2022; `563A` replaced it. Before 2022 a mortgage rate
needs the older account (not checked yet).

Caveats a reader needs: one day's rate, the most common one, not the rate a given borrower gets (that depends
on credit score and term); self-reported and not audited by NCUA. A 0 means the product isn't offered or wasn't
reported, never a 0% rate, and must print as "not offered/not reported," never 0%.

## Savings, checking and certificate rates: no

`ACCT_552` (regular shares), `553` (share drafts), `547` (1-year certificates), `532` (money market) and `554`
(IRA) are zero for every credit union in every quarter checked, 2022-06 to 2026-06. NCUA no longer collects
them. Savings rates have to come from each credit union's own rate sheet, which is a different kind of source
(web pages that change without notice).

## Fees: only a rough total

- `ACCT_131` fee income (year-to-date dollars) is reported by nearly all. Fee income per member is computable,
  annualized, but it mixes every fee (interchange, loan fees, overdraft) and reflects the members' behavior as
  much as the price list.
- `ACCT_IS0048` overdraft fee income and `IS0049` NSF fee income were collected for 2024 only (426 and 406
  credit unions nationally, the largest ones) and are zero from 2025-03. Not usable for a current comparison.

## Branches, ATMs, hours: yes

- `Credit Union Branch Information.txt` in each zip: every site with address, county, phone, hours, and flags
  for member services, ATM, drive-through and shared-branch network. That answers "is there a branch in my
  county" without geocoding (the county is a column).
- `ATM Locations.txt`: the credit union's own ATMs with address and county.
- New Mexico's 37, 2026-06: 189 listed sites (144 typed "Branch Office," 45 "Corporate Office"), 178 of
  them in New Mexico, in 26 of the state's 33 counties.
- `ACCT_566`: number of branches. `ACCT_PP0034`: whether it offers a surcharge-free ATM network, and
  `ACCT_PP0035` its name.

## Who can join: partly

FOICU.txt has `TOM_CODE` (field-of-membership type, e.g. community, employer group, association) and
`LIMITED_INC` (low-income designation: 31 of New Mexico's 37 in 2026-06). The `TOM_CODE` values need NCUA's
code list (12 different codes among the 37; 18 are code 99) before they can be printed. The actual eligibility wording ("anyone who lives, works, worships or
attends school in Bernalillo County") isn't in the data. It's in each credit union's charter and website and
would be a hand-checked crosswalk, like the Lender Lens one.

## Safety: yes (the current spec)

Federal insurance (all 37), net worth ratio against the 7% level, delinquency and charge-offs, from the dictionary.
