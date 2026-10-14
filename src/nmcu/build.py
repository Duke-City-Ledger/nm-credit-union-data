"""Build every quarter: read, compute, compare with peers, check, write out/.

out/quarters/YYYY-MM.json   every New Mexico credit union that quarter: its accounts as
                            filed, its measures, and its New Mexico peer comparison
out/credit-unions.csv       one row per figure (quarter, credit union, measure, value)
out/flags.json              what the checks found, for a person to close
out/manifest.json           the quarters, the package pin and the dictionary's check date
"""

from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal
from datetime import date
from pathlib import Path

from ncua_data import download as package_download

from . import checks
from .measures import (
    RATES,
    ROOT,
    SIMPLE,
    all_accounts,
    check_against_dictionary,
    load_dictionary,
    net_charge_offs_12m,
)
from .read import read_quarter

CACHE = ROOT / ".cache"
OUT = ROOT / "out"
FIRST = "2018-03"
# Read for calculation history only, never published: lets 2018-12 have a 12-month
# charge-off figure (it needs the December a year earlier).
HISTORY_ONLY = "2017-12"
URL = "https://ncua.gov/files/publications/analysis/call-report-data-{}.zip"
PACKAGE_PIN = "bnovarini/ncua-data-analysis@a9fcbe50a8e4f6c7cc7599dd74c42b7fa205473d"
PEER_MINIMUM = 5
PEER_GROUPS = {
    1: "under $2 million",
    2: "$2 million to $10 million",
    3: "$10 million to $50 million",
    4: "$50 million to $100 million",
    5: "$100 million to $500 million",
    6: "$500 million or more",
}
PEER_MEASURES = checks.PERCENTS


def quarters_available(offline: bool) -> dict[str, str]:
    """Quarter -> zip URL, from NCUA's page (the package's scraper), or the cache offline."""
    if not offline:
        try:
            found = package_download.list_quarters(int(FIRST[:4]))
            return {q: u for q, u in found.items() if q >= FIRST}
        except OSError as e:
            print(f"NCUA's page didn't answer ({e}); using cached zips", file=sys.stderr)
    cached = sorted(p.stem.removeprefix("call-report-data-") for p in CACHE.glob("call-report-data-*.zip"))
    return {q: URL.format(q) for q in cached if q >= FIRST}


def quantile(values: list[float], p: str) -> float:
    """Linear interpolation between order statistics (the "inclusive" method, numpy's
    default), in decimal so a value that lands on a half rounds up as printed."""
    xs = sorted(Decimal(repr(v)) for v in values)
    pos = (len(xs) - 1) * Decimal(p)
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    exact = xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)
    return float(exact.quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) + 0.0


def peers(cu, cus: list, measure: str) -> dict:
    out = {"n_others": 0, "median": None, "p25": None, "p75": None}
    if cu.peer_group not in PEER_GROUPS:  # missing or a code NCUA doesn't define
        return out
    others = [c.measures[measure] for c in cus
              if c is not cu and c.peer_group == cu.peer_group and c.measures.get(measure) is not None]
    out["n_others"] = len(others)
    if len(others) >= PEER_MINIMUM:
        out.update(median=quantile(others, "0.5"), p25=quantile(others, "0.25"), p75=quantile(others, "0.75"))
    return out


def build(offline: bool = False, through: str | None = None) -> dict:
    dictionary = load_dictionary()
    problems = check_against_dictionary(dictionary)
    if problems:
        raise checks.BuildError("code and dictionary disagree: " + "; ".join(problems))
    accounts = all_accounts(dictionary)

    urls = quarters_available(offline)
    if through:
        urls = {q: u for q, u in urls.items() if q <= through}
    if not urls:
        raise checks.BuildError(f"no quarters from {FIRST} through {through or 'the latest'}; nothing written")
    zips = package_download.download(urls, CACHE)
    history_zip = package_download.download({HISTORY_ONLY: URL.format(HISTORY_ONLY)}, CACHE)[0]

    history: dict[str, dict[str, dict]] = {}  # cu_number -> quarter -> accounts
    quarters = []
    early = read_quarter(history_zip, HISTORY_ONLY, accounts & set(checks.CHARGE_OFF_ACCOUNTS))
    for cu in early.credit_unions.values():
        history.setdefault(cu.cu_number, {})[HISTORY_ONLY] = cu.accounts
    for (q, url), z in zip(urls.items(), zips):
        print(q, end=" ", file=sys.stderr, flush=True)
        quarter = read_quarter(z, q, accounts)
        checks.schema(dictionary, q, quarter.available)
        quarter.url = url
        for cu in quarter.credit_unions.values():
            history.setdefault(cu.cu_number, {})[q] = cu.accounts
        quarters.append(quarter)
    print(file=sys.stderr)

    flags: list[dict] = []
    previous = None
    OUT.mkdir(exist_ok=True)
    (OUT / "quarters").mkdir(exist_ok=True)
    for old in (OUT / "quarters").glob("*.json"):  # a shorter build leaves nothing stale
        old.unlink()
    rows = []
    for quarter in quarters:
        q = quarter.quarter
        cus = list(quarter.credit_unions.values())
        for cu in cus:
            for mid, (_, fn) in SIMPLE.items():
                cu.measures[mid] = fn(cu.accounts)
            cu.measures["net_charge_offs_12m"] = net_charge_offs_12m(history[cu.cu_number], q)
            for mid in RATES:
                (code,), _ = SIMPLE[mid]
                if cu.accounts[code] == 0:
                    cu.notes[mid] = "Not offered or not reported"
        flags += checks.roster(q, quarter.credit_unions, previous.credit_unions if previous else None, quarter.uninsured)
        for cu in cus:
            before = previous.credit_unions.get(cu.cu_number) if previous else None
            flags += checks.filing(q, cu, before, latest=quarter is quarters[-1])
            if cu.not_reported:
                flags.append(checks.flag(q, cu, "not reported", f"blank in the filing: {', '.join(sorted(cu.not_reported))}"))
        for cu in cus:
            checks.withhold(cu)

        records = []
        for cu in sorted(cus, key=lambda c: -(c.accounts["ACCT_010"] or 0)):
            records.append({
                "cu_number": cu.cu_number,
                "name": cu.name,
                "city": cu.city,
                "peer_group": cu.peer_group,
                "peer_group_label": PEER_GROUPS.get(cu.peer_group),
                "measures": cu.measures,
                "peers": {m: peers(cu, cus, m) for m in PEER_MEASURES},
                "not_reported": sorted(cu.not_reported),
                "withheld": cu.withheld,
                "notes": cu.notes,
                "sites": cu.sites,
                "accounts": {k: (None if v is None else int(v) if float(v).is_integer() else v)
                             for k, v in sorted(cu.accounts.items())},
            })
            for mid, v in cu.measures.items():
                if isinstance(v, dict):
                    for part, x in v.items():
                        rows.append([q, cu.cu_number, cu.name, mid, part, x])
                else:
                    rows.append([q, cu.cu_number, cu.name, mid, "", v])
        doc = {
            "quarter": q,
            "source": quarter.url,
            "credit": "Duke City Ledger, from NCUA call reports",
            "count": len(records),
            "accounts_available": dict(sorted(quarter.available.items())),
            "credit_unions": records,
        }
        (OUT / "quarters" / f"{q}.json").write_text(json.dumps(doc, indent=1) + "\n")
        previous = quarter

    with open(OUT / "credit-unions.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quarter", "cu_number", "name", "measure", "part", "value"])
        w.writerows([[*r[:5], "" if r[5] is None else r[5]] for r in rows])
    (OUT / "flags.json").write_text(json.dumps(flags, indent=1) + "\n")
    manifest = {
        "built": date.today().isoformat(),
        "credit": "Duke City Ledger, from NCUA call reports",
        "quarters": [q.quarter for q in quarters],
        "latest": quarters[-1].quarter,
        "credit_unions_latest": len(quarters[-1].credit_unions),
        "package": PACKAGE_PIN,
        "dictionary_checked": dictionary["checked"],
        "flags": len(flags),
        "peer_minimum": PEER_MINIMUM,
        "rules": dictionary["rules"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest
