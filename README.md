# nm-credit-union-data

Figures for every federally insured credit union headquartered in New Mexico, from NCUA call reports,
2018-03 on. Built for Duke City Ledger's credit union tracker. MIT license.

Credit for the data: "Duke City Ledger, from NCUA call reports." NCUA's own data is a U.S. government work.

## What it makes

`out/` (committed; this is what the site installs):

- `quarters/YYYY-MM.json`: for each New Mexico credit union that quarter, its accounts as filed, its measures, and
  how it compares with the other New Mexico credit unions in its NCUA peer group (median and middle half, itself
  left out, shown only when there are at least five others).
- `credit-unions.csv`: every figure, one row each.
- `flags.json`: what the automated checks found, for a person to read before a quarter is released.
- `manifest.json`: the quarters, the package pin, and the dictionary's check date.

The measures are defined in `data/dictionary.json`: NCUA's accounts, its wording, the form line, the instructions
page, and how each was checked against NCUA's own published ratios. The code reads its accounts from there and
refuses to build if the two disagree.

## Run it

```
uv run nmcu build                                # downloads any missing quarter, builds out/
uv run python -m unittest discover -s tests      # formulas, and 2026-06 against NCUA and hand-worked figures
uv run scripts/check_dictionary.py               # dictionary against the account history
uv run scripts/account_history.py                # rereads every quarter's AcctDesc.txt
uv run ncua-data --data .cache/package ingest && uv run scripts/crosscheck_package.py
                                                 # our reading against the package's, eight accounts
```

Zips are cached in `.cache/` (gitignored). Downloading and the quarter list come from
[bnovarini/ncua-data-analysis](https://github.com/bnovarini/ncua-data-analysis), pinned to one commit. Reading is
ours: the package stores only non-zero values, and here an account a quarter doesn't have stays null, never 0.

## Rules

- Null means not available (the account didn't exist that quarter) or not reported. 0 means the credit union
  reported 0.
- Percents are rounded to two decimals, halves up, as NCUA's Financial Performance Report shows them.
- Net charge-offs are NCUA's 12-month figure, not year-to-date annualized, so they start in 2019-03.
- A share the filing makes impossible (over 100%) is withheld, with the reason in `withheld`, and flagged.
- Figures are as each quarter's zip has them today. NCUA can revise past quarters.

## Research

`docs/research/` holds the evidence for the dictionary. `docs/account-history.md` tracks every account through
every quarter. `docs/profile.md` profiles the output. `docs/package-crosscheck.md` compares our reading with the
package's.
