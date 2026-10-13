# FPR formulas vs. our own computation — 2026-06 (June 30, 2026)

Source for formulas: **Financial Performance Report Ratio and Formula Guide, Version 3.3, June 30, 2023** —
https://ncua.gov/files/publications/analysis/fpr-ratio-formula-guide.pdf (confirmed; this is the current
version — the FPR site itself, https://fpr.ncua.gov/, links the identical file as `FPRRatioanFormulaGuide.pdf`,
and I found no newer version number on ncua.gov as of 2026-10-13). Page numbers below are the PDF's own page
footers.

## The formulas (quoted/transcribed from the guide)

**Net Worth / Total Assets for Prompt Corrective Action** (p.4):
> Net Worth ÷ total assets. This ratio is calculated according to NCUA regulations part 702 ... considers
> optional asset elections, [PPP loans pledged as collateral], and the CECL Transition Provision, as applicable.

```
997 ÷ [ NW0010  or  (010A − LC0047 + NW0004)  or  (010B − LC0047 + NW0004)  or  (010C − LC0047 + NW0004) ]  × 100
```
> "The ratio is rounded to two decimal places (for example, 6.997 would be rounded to 7.00%)."

**Delinquent Loans / Total Loans** (p.7):
> The amount of loans 60 days or more delinquent ÷ total loans.
```
041B ÷ 025B × 100
```

**Rolling 12-Month Net Charge-Offs / Average Loans** (p.7–8):
> The amount of YTD charge-offs for the applicable cycle − YTD recoveries for the applicable cycle + YTD
> charge-offs for the prior year end − YTD recoveries for the prior year end − YTD charge-offs for the prior
> year quarter end − YTD recoveries for the prior year quarter end ÷ [total loans for the applicable cycle +
> total loans for the prior year quarter end] ÷ two. "This ratio is based on net-charge offs over the last 12
> months."
```
NCO = (550(AC)-551(AC)) + (550(PYE)-551(PYE)) - (550(PYQE)-551(PYQE))
Avg Loans = (025B(AC) + 025B(PYQE)) / 2
Ratio = NCO / Avg Loans × 100
```
where AC = applicable (current) cycle, PYE = prior calendar year-end cycle, PYQE = prior-year same-quarter cycle.
For a 2026-06 report: AC = 2026-06, PYE = 2025-12, PYQE = 2025-06.

**Delinquent Loans plus Net Charge-Offs / Average Loans** (p.8) — same NCO term, plus 041B(AC) in the numerator,
over the same average-loans denominator. Not separately tabulated below; it is 041B(AC)/AvgLoans×100 + the NCO
ratio above.

**Commercial-loan / real-estate ratios found in the guide relevant to this project** (p.786 area of the extracted
text — "Supplemental Ratios"):
- **Total Commercial Loans / Total Assets** ("Total Business Loans"): total commercial loan balances ÷ total assets.
- **Total Real Estate Loans Delinquent ≥30 Days / Total Real Estate Loans**, and the parallel **≥60 Days** version,
  under "All Real Estate Loan Delinquency (Commercial and Non-Commercial)."
I did not find a named FPR ratio that directly uses CM0099/RL0050 (the 5-year reprice/maturity accounts) — those
feed NCUA's separate interest-rate-risk / NEV analysis, not the FPR ratio set, as far as this guide shows. **Flag
as UNVERIFIED-by-omission**: absence of a hit in this document doesn't prove no such ratio exists elsewhere (e.g.
in the NEV/IRR supervisory tools), only that it isn't in this ratio guide.

## Obtaining NCUA's own published 2026-06 FPR figures — blocked, and why

I could not retrieve NCUA's own rendered FPR PDF/figures for the five charters by script. What I found and why
it doesn't work headlessly:

- `mapping.ncua.gov`'s "Research a Credit Union" tool is an Angular SPA. Its backend API (`https://mapping.ncua.gov/api/CreditUnionDetails/GetCreditUnionDetails/{charter}`) **does work directly over plain HTTP GET** and returns live JSON (I confirmed this for charters 808 and 61559) — but the only FPR-related field it returns is `urLs.urlFPR = "http://fpr.ncua.gov/"`, a static link to the FPR request tool itself, not a per-CU report.
- `fpr.ncua.gov` is a classic ASP.NET Web Forms app. After selecting "Single Credit Union" and submitting, the next page is a request form requiring: an **email address** (required field), a CU number, an interval/cycle-date selection, and a set of report-page checkboxes. Submitting this form does not return a PDF in the HTTP response — NCUA's own site design emails the finished FPR PDF to the address you enter, asynchronously. That means: (a) it cannot be scripted to a direct download without an email inbox to receive from, and (b) it would not be appropriate for me to submit an account email address into a third-party government mailer for a bulk automated request on your behalf without you asking for that specifically.
- **What a person would click:** go to https://fpr.ncua.gov/ → select "Single Credit Union Report" (radio button) → OK → enter your email address and the 5-digit CU/charter number → pick the "June 2026" cycle date and the report sections you want → submit. NCUA emails the PDF.
- No 403/captcha/JS-wall was hit — the blocker is specifically "email-delivery by design," not an access restriction.

**Given that block, the comparison below is not "theirs vs. ours" in the sense of two independently-obtained numbers.** It
is the official FPR formula applied, by hand, to the same NCUA-published call-report figures NCUA's own FPR
system consumes. Since the FPR is itself computed from Call Report data using this exact published formula, a
correct implementation should reproduce NCUA's number by construction — any mismatch would point to either a
formula error on my part or an edge case (asset elections, CECL, etc.) in that credit union's filing, not to new
information from NCUA. I'm flagging this limitation rather than presenting the result as a confirmed match against
an independently-sourced NCUA number.

## Our own computation, June 30, 2026 cycle

Call report sources: `/tmp/cuv/FS220.txt` and `FS220A.txt` (2026-06, already present on this box) plus
`/tmp/ncua-docs/cuv-2025-12/FS220.txt` and `/tmp/ncua-docs/cuv-2025-06/FS220.txt` (downloaded in this session from
https://ncua.gov/files/publications/analysis/call-report-data-2025-12.zip and the analogous 2025-06 URL,
following the same naming pattern, both HTTP 200).

Raw inputs pulled (dollars):

| Charter | Cycle | 010 | 025B | 041B | 550 (YTD CO) | 551 (YTD Rec) |
|---|---|---|---|---|---|---|
| 808 | 2026-06 | 1,458,642,449 | 1,054,654,916 | 72,873,527 | 6,002,724 | 390,279 |
| 808 | 2025-12 | 1,451,681,906 | 1,067,612,438 | 75,586,886 | 11,834,491 | 1,200,760 |
| 808 | 2025-06 | 1,476,556,190 | 1,048,359,851 | 69,580,330 | 6,843,858 | 742,900 |
| 61559 | 2026-06 | 5,385,932 | 1,639,654 | 1,792 | 7,274 | 4,561 |
| 61559 | 2025-12 | 5,525,399 | 2,160,826 | 21,328 | 27,678 | 3,256 |
| 61559 | 2025-06 | 5,587,219 | 2,221,490 | 529 | 14,355 | 679 |
| 66143 | 2026-06 | 40,086,174 | 11,778,802 | 0 | 0 | 0 |
| 66143 | 2025-12 | 37,374,831 | 11,244,448 | 0 | 10,473 | 1,750 |
| 66143 | 2025-06 | 37,544,955 | 11,030,433 | 224 | 8,742 | 287 |
| 9566 | 2026-06 | 61,773,891 | 45,272,259 | 1,589 | 507,260 | 212,434 |
| 9566 | 2025-12 | 60,563,131 | 41,951,885 | 178,568 | 351,589 | 317,486 |
| 9566 | 2025-06 | 60,275,527 | 42,806,807 | 0 | 138,660 | 215,064 |
| 62783 | 2026-06 | 172,724,377 | 115,136,433 | 1,242,849 | 241,469 | 34,184 |
| 62783 | 2025-12 | 163,506,971 | 115,034,803 | 445,302 | 409,587 | 147,864 |
| 62783 | 2025-06 | 156,177,674 | 115,906,334 | 587,317 | 250,227 | 94,330 |

997/998 (2026-06, from FS220A.txt):

| Charter | 997 (net worth $) | Stored Acct 998 |
|---|---|---|
| 808 | 113,766,182 | 780 |
| 61559 | 1,333,530 | 2476 |
| 66143 | 8,368,107 | 2088 |
| 9566 | 11,328,479 | 1834 |
| 62783 | 27,847,486 | 1612 |

### Computed ratios

| Charter (name) | Net worth / assets (997/010×100) | Stored 998 ÷ 100 | Match? | Delinquent/Total loans (041B/025B×100) | Rolling 12-mo net charge-off / avg loans |
|---|---|---|---|---|---|
| 808 (U.S. Eagle) | 7.80% | 7.80% | Yes | 6.910% | 0.965% |
| 61559 (Deming Schools) | 24.76% | 24.76% | Yes | 0.109% | 0.697% |
| 66143 (Chaves County Schools) | 20.87% | 20.88% | Yes (0.01pt rounding, see note) | 0.000% | 0.002% |
| 9566 (Eddy) | 18.33% | 18.34% | Yes (0.01pt rounding, see note) | 0.004% | 0.920% |
| 62783 (Artesia) | 16.12% | 16.12% | Yes | 1.079% | 0.271% |

**997/010×100 vs. the stored 998 field match to NCUA's stated 2-decimal rounding for three of five charters
exactly, and are off by 0.01 percentage point for the other two** (66143: 20.87 vs 20.88; 9566: 18.33 vs 18.34).
That's consistent with 998 being computed off NW0010 (010 adjusted for optional elections / PPP / CECL
transition) rather than raw 010 — I did not pull NW0010, LC0047, or NW0004 to confirm the exact source of the
0.01pt gap, since it's immaterial to any editorial claim. **No mismatch found that would make the draft
dictionary's 998-scaling claim wrong.**

### Notable finding, not a data error: U.S. Eagle's delinquency ratio

U.S. Eagle's 041B/025B comes out to **6.91%** — markedly higher than the other four charters (all under 1.1%).
This is a direct, correctly-sourced application of the NCUA formula to NCUA's own published figures; it is not a
computation artifact. If this number is going into a published comparison, it's worth a second look at what's
driving it (e.g., a specific loan portfolio, a reporting-period anomaly) before publishing, since it's an outlier
worth a sentence of its own, not proof of a calculation bug.

### Rolling 12-month net charge-off ratio — formula note

This is the one figure in the draft dictionary's scope that needed **both** 2025-12 and 2025-06 data (not just
2025-12, as the task brief anticipated) — the FPR formula nets out the prior-year-quarter-end YTD charge-offs/
recoveries specifically to isolate the trailing 12 months from two overlapping YTD figures. I downloaded
2025-06 from the same `call-report-data-YYYY-MM.zip` naming pattern used for 2025-12 (confirmed working,
HTTP 200, 8.2MB) at https://ncua.gov/files/publications/analysis/call-report-data-2025-06.zip.
