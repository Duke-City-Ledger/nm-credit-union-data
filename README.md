# nm-credit-union-data

Figures for every federally insured credit union headquartered in New Mexico, from NCUA call reports,
2018-03 on. Built for Duke City Ledger's credit union tracker. MIT license.

Credit for the data: "Duke City Ledger, from NCUA call reports." NCUA's own data is a U.S. government work.

## What it makes

`out/` (committed; this is what the site installs):

- `quarters/YYYY-MM.json`: for each New Mexico credit union that quarter, its accounts as filed, its measures
  (safety and lending figures, the loan rates it offered, and yes/no services such as checking with no monthly fee), how it
  compares with the other New Mexico credit unions in its NCUA peer group (median and middle half, itself left
  out, shown only when there are at least five others), and its offices from NCUA's branch file (county, hours,
  ATM, drive-through).
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
(cd second && python3 second.py) && uv run scripts/compare_second.py
                                                 # the engine against the blind second calculation
```

Each Monday, `.github/workflows/quarterly.yml` checks NCUA for the next quarter. When it's out, the workflow builds
through that quarter, runs the tests, moves each account's dictionary quarters forward
and their current wording's end date (`check_dictionary.py --sync-quarters`; a gap, a new first quarter or new
wording is left for the check to fail on), and opens a pull request listing that
quarter's flags and any credit union that stopped reporting. A person reads the flags, merges, and tags a release.
If a check fails, the run fails and no pull request opens; the next run tries again, even if a branch was left
behind. When NCUA is two quarters ahead, the next one is built the Monday after the first pull request merges. The build runs with read-only rights and a separate
job pushes. Run it by hand from the Actions tab. It needs Settings, Actions, General, "Allow GitHub Actions to create
and approve pull requests" switched on.

Zips are cached in `.cache/` (gitignored). Downloading and the quarter list come from
[bnovarini/ncua-data-analysis](https://github.com/bnovarini/ncua-data-analysis), pinned to one commit. Reading is
ours: the package stores only non-zero values, and here an account a quarter doesn't have stays null, never 0.

## Rules

- Null means not available (the account didn't exist that quarter) or not reported. 0 means the credit union
  reported 0.
- Percents are rounded to two decimals, halves up, as NCUA's Financial Performance Report shows them.
- Net charge-offs are NCUA's 12-month figure, not year-to-date annualized. They need the December and the
  quarter a year earlier, so 2018-03 to 2018-09 are null; 2018-12 uses 2017-12, read for that and not published.
- A share the filing makes impossible (over 100%), or a loan rate outside 1% to 30%, is withheld, with the reason
  in `withheld`, and flagged.
- Loan rates are the most common rate each credit union offered on the quarter's last day, as it reported it: not
  a quote. A reported 0 (none of those loans on its books) is null, with the reason in `notes`. Savings rates and fees aren't in
  NCUA's public data (`docs/research/consumer-data-in-call-reports.md`).
- Figures are as each quarter's zip has them today. NCUA can revise past quarters.

## Worth a look

`uv run scripts/watch.py [--quarter YYYY-MM]` reads `out/quarters/` and prints a short list of credit unions whose
figures moved in a way worth a reporter's time (`--json <path>` also writes them as JSON, and refuses a path inside
this repository or the data root). The list itself is never
committed here or put in a pull request: the Ledger's desk runs it and keeps it private. These are leads, not findings: never print them on a public page, and
check every one against the filing and the credit union before it becomes a story. A credit union under $10 million in
assets is still listed and marked "small credit union", because one loan can move its figures.

Thresholds (all in `T` at the top of `scripts/watch.py`; change both together). Null never counts as 0: a signal needs
every figure it uses. Runs and year-ago figures count calendar quarters, so a quarter missing from the data breaks
a run instead of joining the quarters on either side, and a level check still runs in a credit union's first quarter.

- Net worth ratio within 1 point of 7% (NCUA's well-capitalized level), either side and not below 0. Or down 1.5 points
  or more over four quarters, ending below 10%. Below 6% NCUA can step in with a plan and limits on the credit union;
  that is context for a reporter, not a per-item label.
- Late loans (delinquency) up three quarters in a row and 1 point or more over the run. Or at least 2 times its peer-group
  median and at least 2%.
- 12-month net charge-offs at least 2 times its peer-group median and at least 1.5%. Or up 1 point or more from a year
  earlier, reaching at least 1.5%.
- Business loans (`commercial_share`) up 5 points or more in a year. Or commercial real estate / home loans resetting
  within five years at 75% or more of the book and up 10 points or more in a year.
- Members, or total assets, down four quarters in a row and 10% or more over the run.

Peer medians come from the quarter files and exist only when at least five other credit unions share the peer group.
`--backtest` prints how many items each quarter produces, from 2018-12 through the latest quarter built. The thresholds were tuned against one
known case, so expect some misses and some false alarms.

Not covered yet: net losses two quarters running. The engine has no net income measure, and adding one means a new
NCUA account through the dictionary process. Also not covered: anything outside the call report (lawsuits, regulator
actions, complaints).

## Research

`docs/research/` holds the evidence for the dictionary. `docs/account-history.md` tracks every account through
every quarter. `docs/profile.md` profiles the output. `docs/package-crosscheck.md` compares our reading with the
package's. `docs/second-calculation.md` compares the engine with `second/`, an independent calculation written
blind by a different model (OpenAI's Codex) from the spec, the dictionary and NCUA's documents only. Its brief is
`second/TASK.md` and its judgment calls are `second/NOTES.md`. The one place the two differ by design: `second/`
keeps a credit union's filings from before it moved its headquarters into New Mexico, so its first year's
12-month charge-offs exist, where the engine reads New Mexico filings only. No credit union moved in from 2018
to 2026; if one does, the comparison flags it.
