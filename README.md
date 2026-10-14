# nm-credit-union-data

Data on New Mexico's credit unions from NCUA call reports, for Duke City Ledger's credit union tracker. MIT license.

Credit for the data: "Duke City Ledger, from NCUA call reports." NCUA's own data is a U.S. government work.

## What's here

- `data/dictionary.json`: every measure the tracker prints, with the NCUA accounts behind it, NCUA's wording word
  for word, the Call Report form schedule and line, the instructions page, units, and how each was checked
  against NCUA's own published ratios (the Financial Performance Report).
- `data/account-history.json`, `docs/account-history.md`: how each account was described and carried in every
  quarter from 2017-12 to 2026-06.
- `docs/research/`: the evidence: the instructions read line by line, the FPR match for five credit unions, and a
  second, independent reading of the accounts.

## Checks

```
node scripts/account-history.mjs      # rereads every quarter's AcctDesc.txt (zips cached in .cache/)
uv run scripts/check_dictionary.py    # fails if the dictionary drifts from the account history
```

The engine itself (download, New Mexico filter, peer groups, calculations) comes next, built on
[bnovarini/ncua-data-analysis](https://github.com/bnovarini/ncua-data-analysis).
