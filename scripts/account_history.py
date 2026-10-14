"""Account history: how every account in data/dictionary.json has been described and
carried, quarter by quarter, in NCUA's call report data.

NCUA renumbers, adds and rewords accounts between form revisions, and its dictionary
(AcctDesc.txt) ships fresh in every quarter's zip. This reads the dictionary and the table
headers from each quarter since 2017-12 and writes:

  data/account-history.json   per account: the quarters it exists in, the table that
                              carries it, and each distinct description with the
                              quarters it was used
  docs/account-history.md     the same, for a person to read, with every description
                              change called out

A person reads every change and decides whether the meaning changed. This script only
finds them.

Usage: uv run scripts/account_history.py [--from 2017-12] [--to 2026-06] [ACCT_X ...]
Accounts named on the command line are added to the dictionary's, for an account being
considered before it has an entry. Zips are cached in .cache/ (gitignored), about 8 MB each.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
URL = "https://ncua.gov/files/publications/analysis/call-report-data-{}.zip"


def quarters(start: str, end: str) -> list[str]:
    y, m = map(int, start.split("-"))
    out = []
    while f"{y}-{m:02d}" <= end:
        out.append(f"{y}-{m:02d}")
        m += 3
        if m > 12:
            m, y = m - 12, y + 1
    return out


def zip_for(q: str) -> Path:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"call-report-data-{q}.zip"
    if not path.exists():
        with urllib.request.urlopen(URL.format(q), timeout=120) as r:
            path.write_bytes(r.read())
    return path


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def first_line(z: zipfile.ZipFile, name: str) -> list[str]:
    with z.open(name) as fh:
        line = fh.readline().decode("latin-1").rstrip("\r\n")
    return next(csv.reader([line]))


def read_quarter(q: str):
    with zipfile.ZipFile(zip_for(q)) as z:
        names = z.namelist()
        # Not Acct-DescGrants.txt or Acct-DescTradeNames.txt, which ship alongside it.
        dict_name = next((n for n in names if n.lower() == "acctdesc.txt"), None)
        if dict_name is None:
            raise SystemExit(f"{q}: no AcctDesc file in zip ({', '.join(names)})")
        text = z.read(dict_name).decode("latin-1")
        rows = list(csv.reader(io.StringIO(text)))
        head = [h.lower() for h in rows[0]]

        def col(word, fallback):
            return next((i for i, h in enumerate(head) if word in h), fallback)

        i_code, i_name, i_desc, i_table = col("account", 0), col("name", 1), col("desc", 2), col("table", 3)
        dictionary = {}
        for f in rows[1:]:
            if not f or not f[i_code]:
                continue
            get = lambda i: f[i] if i < len(f) else ""
            dictionary[f[i_code].upper()] = {"name": norm(get(i_name)), "description": norm(get(i_desc)),
                                             "table": get(i_table)}

        # Which data file actually carries each account this quarter.
        carried_by = {}
        for n in names:
            if n.lower().endswith(".txt") and not re.search(r"acct-?desc", n, re.I):
                for c in first_line(z, n):
                    carried_by[c.upper()] = n
    return dictionary, carried_by


def summarize(qs: list[str]) -> str:
    """'2017-12 to 2019-06, 2020-03' from a sorted list of quarters."""
    if not qs:
        return "none"
    runs, start, prev = [], qs[0], qs[0]
    for q in qs[1:]:
        if len(quarters(prev, q)) == 2:
            prev = q
            continue
        runs.append(start if start == prev else f"{start} to {prev}")
        start = prev = q
    runs.append(start if start == prev else f"{start} to {prev}")
    return ", ".join(runs)


def dictionary_accounts() -> list[str]:
    d = json.loads((ROOT / "data/dictionary.json").read_text())
    seen = []
    for a in [a for m in d["measures"] for a in m["accounts"]] + d["not_used"]:
        if a["account"] not in seen:
            seen.append(a["account"])
    return seen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", default="2017-12")
    ap.add_argument("--to", dest="end", default="2026-06")
    ap.add_argument("extra", nargs="*")
    a = ap.parse_args()
    accounts = dictionary_accounts() + [x for x in a.extra if x not in dictionary_accounts()]
    qs = quarters(a.start, a.end)
    history = {x: {"quarters": [], "tables": {}, "descriptions": []} for x in accounts}

    for q in qs:
        print(q, end=" ", file=sys.stderr, flush=True)
        dictionary, carried_by = read_quarter(q)
        for x in accounts:
            h, d, file = history[x], dictionary.get(x), carried_by.get(x)
            if not d and not file:
                continue
            h["quarters"].append(q)
            if file:
                h["tables"].setdefault(file, []).append(q)
            text = f"{d['name']} | {d['description']}" if d else "(in data, not in dictionary)"
            last = h["descriptions"][-1] if h["descriptions"] else None
            if last and last["text"] == text:
                last["to"] = q
            else:
                h["descriptions"].append({"text": text, "from": q, "to": q, "inDictionary": bool(d),
                                          "inData": bool(file)})
    print(file=sys.stderr)

    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/account-history.json").write_text(
        json.dumps({"from": a.start, "to": a.end, "accounts": history}, indent=2, ensure_ascii=False) + "\n")

    md = [f"# Account history, {a.start} to {a.end}", "",
          "Generated by `scripts/account_history.py`. Every description change below needs a person to say whether the",
          "meaning changed (a break in the series) or only the wording.", ""]
    for x, h in history.items():
        missing = [q for q in qs if q not in h["quarters"]]
        md += [f"## {x}", ""]
        md.append(f"- In {len(h['quarters'])} of {len(qs)} quarters" + (f"; missing {summarize(missing)}" if missing else "") + ".")
        for file, lst in h["tables"].items():
            md.append(f"- Carried in `{file}`: {summarize(lst)}.")
        n = len(h["descriptions"])
        md.append("- " + ("One description throughout" if n == 1 else f"**{n} descriptions**") + ":")
        for d in h["descriptions"]:
            md.append(f"  - {d['from']} to {d['to']}: {d['text']}")
        md.append("")
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/account-history.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
