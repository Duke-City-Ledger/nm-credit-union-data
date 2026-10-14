"""The measures, worked from the accounts named in data/dictionary.json.

Each measure says which accounts it reads. `check_against_dictionary` fails the build if
that list and the dictionary's (every account whose role isn't "check" or "context")
disagree, so the code and the dictionary can't drift apart.

Percents are rounded to two decimals, as NCUA's Financial Performance Report shows them.
A ratio whose denominator is 0 or missing is None, never 0.
"""

from __future__ import annotations

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
DICTIONARY = ROOT / "data" / "dictionary.json"

Accounts = dict[str, float | None]


def load_dictionary() -> dict:
    return json.loads(DICTIONARY.read_text())


def all_accounts(dictionary: dict) -> set[str]:
    return {a["account"] for m in dictionary["measures"] for a in m["accounts"]}


def round2(x: float) -> float:
    """Two decimals, halves rounded up, as NCUA rounds (Python's round() goes to even)."""
    out = float(Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return out + 0.0  # -0.0 (a tiny negative rounded away) becomes 0.0


def _pct(num: float | None, den: float | None) -> float | None:
    if num is None or den is None or den == 0:
        return None
    return round2(100 * num / den)


def _sum(*xs: float | None) -> float | None:
    return None if any(x is None for x in xs) else sum(xs)


RATE_RANGE = (1, 30)


def plausible_rate(x: float | None) -> bool:
    """A stored rate (times 100) within 1% to 30%, tested before rounding, so the engine,
    its flags and the second calculation all draw the line in the same place."""
    return x is not None and RATE_RANGE[0] * 100 <= x <= RATE_RANGE[1] * 100


def _rate(x: float | None) -> float | None:
    """A rate stored times 100. 0 means none reported, so it's None; so is one outside 1% to
    30% (the build records why in `withheld`)."""
    if x is None or x == 0 or not plausible_rate(x):
        return None
    return round2(x / 100)


def _yes(x: float | None) -> bool | None:
    """1 is yes, 0 is no; anything else, or nothing, is not reported."""
    return {1: True, 0: False}.get(x)


def _either(*xs: float | None) -> bool | None:
    """Yes if any answer is yes; no only if every answer that exists is no."""
    answers = [_yes(x) for x in xs if x is not None]
    if any(answers):
        return True
    return False if answers and all(a is False for a in answers) else None


def _dollars(x: float | None) -> int | None:
    return None if x is None else int(round(x))


# id -> (accounts read, function of one quarter's accounts). The 12-month charge-off
# measure needs earlier quarters and is worked in net_charge_offs_12m below.
SIMPLE: dict[str, tuple[tuple[str, ...], Callable[[Accounts], object]]] = {
    "total_assets": (("ACCT_010",), lambda a: _dollars(a["ACCT_010"])),
    "total_loans": (("ACCT_025B",), lambda a: _dollars(a["ACCT_025B"])),
    "net_worth_ratio": (
        ("ACCT_998",),
        lambda a: None if a["ACCT_998"] is None else round2(a["ACCT_998"] / 100),
    ),
    "delinquency": (("ACCT_041B", "ACCT_025B"), lambda a: _pct(a["ACCT_041B"], a["ACCT_025B"])),
    "commercial_share": (("ACCT_400T1", "ACCT_010"), lambda a: _pct(a["ACCT_400T1"], a["ACCT_010"])),
    "cre_reset_5y": (
        ("ACCT_CM0099", "ACCT_718A3", "ACCT_718A4"),
        lambda a: _pct(a["ACCT_CM0099"], _sum(a["ACCT_718A3"], a["ACCT_718A4"])),
    ),
    "home_reset_5y": (("ACCT_RL0050", "ACCT_RL0047"), lambda a: _pct(a["ACCT_RL0050"], a["ACCT_RL0047"])),
    "other_gov_guaranteed": (
        ("ACCT_691P1", "ACCT_691P2"),
        lambda a: {"balance": _dollars(a["ACCT_691P1"]), "guaranteed": _dollars(a["ACCT_691P2"])},
    ),
    "sba": (
        ("ACCT_691C1", "ACCT_691C2"),
        lambda a: {"balance": _dollars(a["ACCT_691C1"]), "guaranteed": _dollars(a["ACCT_691C2"])},
    ),
    "members": (("ACCT_083",), lambda a: _dollars(a["ACCT_083"])),
    # Offered loan rates, stored times 100. 0 is "not offered or not reported", never 0%.
    "rate_credit_card": (("ACCT_521",), lambda a: _rate(a["ACCT_521"])),
    "rate_new_auto": (("ACCT_523",), lambda a: _rate(a["ACCT_523"])),
    "rate_used_auto": (("ACCT_524",), lambda a: _rate(a["ACCT_524"])),
    "rate_mortgage": (("ACCT_563A",), lambda a: _rate(a["ACCT_563A"])),
    "rate_unsecured": (("ACCT_522",), lambda a: _rate(a["ACCT_522"])),
    # Yes/no answers from the credit union's NCUA profile.
    "free_checking": (("ACCT_879A4",), lambda a: _yes(a["ACCT_879A4"])),
    "bilingual": (("ACCT_879C1",), lambda a: _yes(a["ACCT_879C1"])),
    "credit_builder": (("ACCT_879D1",), lambda a: _yes(a["ACCT_879D1"])),
    # PALs I (879D9) or PALs II (879D10, in the data from 2021-12).
    "payday_alternative": (("ACCT_879D9", "ACCT_879D10"), lambda a: _either(a["ACCT_879D9"], a["ACCT_879D10"])),
    "surcharge_free_atm": (("ACCT_PP0034",), lambda a: _yes(a["ACCT_PP0034"])),
}
RATES = ("rate_credit_card", "rate_new_auto", "rate_used_auto", "rate_mortgage", "rate_unsecured")
NCO_ACCOUNTS = ("ACCT_550", "ACCT_551", "ACCT_025B")


def prior(quarter: str, quarters_back: int) -> str:
    y, m = map(int, quarter.split("-"))
    months = y * 12 + (m - 1) - 3 * quarters_back
    return f"{months // 12}-{months % 12 + 1:02d}"


def net_charge_offs_12m(history: dict[str, Accounts], quarter: str) -> float | None:
    """NCUA's FPR formula (guide v3.3, pp. 7-8): the last 12 months of net charge-offs
    over the average of total loans now and a year earlier.

    history maps quarter -> this credit union's accounts. None if a needed quarter or
    account is missing.
    """
    year_ago = prior(quarter, 4)
    december = f"{int(quarter[:4]) - 1}-12"
    need = [quarter, year_ago, december]
    if any(q not in history for q in need):
        return None

    def net(q: str) -> float | None:
        a = history[q]
        if a["ACCT_550"] is None or a["ACCT_551"] is None:
            return None
        return a["ACCT_550"] - a["ACCT_551"]

    nets = [net(q) for q in need]
    loans = [history[quarter]["ACCT_025B"], history[year_ago]["ACCT_025B"]]
    if any(x is None for x in nets + loans):
        return None
    twelve_months = nets[0] + nets[2] - nets[1]
    return _pct(twelve_months, (loans[0] + loans[1]) / 2)


def check_against_dictionary(dictionary: dict) -> list[str]:
    """Problems where the code's accounts differ from the dictionary's."""
    problems = []
    used = {k: set(v[0]) for k, v in SIMPLE.items()}
    used["net_charge_offs_12m"] = set(NCO_ACCOUNTS)
    for m in dictionary["measures"]:
        listed = {a["account"] for a in m["accounts"] if a["role"] not in ("check", "context")}
        code = used.pop(m["id"], None)
        if code is None:
            problems.append(f"{m['id']}: in the dictionary but not computed")
        elif code != listed:
            problems.append(f"{m['id']}: code reads {sorted(code)}, dictionary lists {sorted(listed)}")
    problems += [f"{k}: computed but not in the dictionary" for k in used]
    return problems
