# Task: an independent second calculation

Write, from scratch, a Python 3.11+ script `second.py` (standard library only; run with `python3 second.py`) that
reads NCUA 5300 call report quarterly zips in `zips/` (call-report-data-YYYY-MM.zip) and computes, for every
federally insured credit union with STATE = NM in each quarter's FOICU.txt, every measure in
`docs/dictionary.json`, for quarters 2018-03 to 2026-06. 2017-12 may be read only as history for the 12-month
charge-off measure; do not output it.

You are the second, independent reader. Work only from `docs/`: `dictionary.json` (the measures and accounts),
`spec.md` (the design, especially "Calculations, pinned down" and the data quality layers),
`call-report-instructions-september-2025.txt` and `fpr-ratio-formula-guide.txt` (NCUA's own documents). Read the
raw files yourself: find each account's column in whichever FS220*.txt table carries it that quarter (file-name
case varies by quarter), and the roster and NCUA peer group (Peer_Group) in FOICU.txt. CU_TYPE 3 is not federally
insured; leave it out.

Rules:
- An account a quarter's files don't have, or a blank cell, is null. Never turn null into 0.
- A ratio with a 0 or null denominator is null.
- Percents are rounded to 2 decimals, halves rounded up (as NCUA rounds).
- net_charge_offs_12m is the FPR formula in the guide: last 12 months of net charge-offs over the average of
  total loans this quarter and the same quarter a year earlier. Null if a needed quarter is missing.
- Measures with a balance and a guaranteed part (other_gov_guaranteed, sba) output two rows, part = balance and
  part = guaranteed. Dollar and count measures are whole numbers.
- A share (delinquency, commercial_share, cre_reset_5y, home_reset_5y) below 0 or above 100 is impossible: output
  null for it and list it in `withheld.csv` (quarter, cu_number, measure, computed_value).
- Peers, for net_worth_ratio, delinquency, net_charge_offs_12m, commercial_share, cre_reset_5y, home_reset_5y: the
  other New Mexico credit unions in the same peer group that quarter (peer groups 1 to 6 only), the credit union
  itself left out, nulls left out. Output n_others always; median, p25 and p75 only when n_others >= 5, using
  linear interpolation between order statistics (numpy's default), computed on the 2-decimal values, rounded to
  2 decimals with halves up.

Write:
- `out/measures.csv`: quarter,cu_number,measure,part,value (part empty when none; value empty when null)
- `out/peers.csv`: quarter,cu_number,measure,n_others,median,p25,p75
- `out/withheld.csv`
- `NOTES.md`: every judgment call you made reading NCUA's documents, briefly.

Check yourself against these published NCUA figures for 2026-06 (charter: net worth ratio, delinquency, 12-month
net charge-offs): 808: 7.80, 6.91, 0.96. 61559: 24.76, 0.11, 0.70. 66143: 20.88, 0.00, 0.00. 9566: 18.34, 0.00,
0.92. 62783: 16.12, 1.08, 0.27. Run the script and leave its output in out/. Don't read anything outside this
directory except the zips it links to.
