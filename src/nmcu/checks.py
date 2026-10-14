"""Automated checks. An error stops the build; a flag goes in out/flags.json for a person
to close before the quarter's release is tagged.

Errors:
- an account the dictionary says exists in a quarter is missing from that quarter's files.

Flags (each says why in its `detail`):
- identity: 025B1 against 025B, 718A5 against 718A3 + 718A4, more than $20 apart
  (NCUA's own rounding gaps are at most $13 nationally; see dictionary.json).
- part over total: a part larger than the total it belongs to.
- net worth: 998 more than 0.01 point from the instructions' own formula (997 over the
  elected asset total less LC0047 plus NW0004, else NW0010, else 010). It matches all
  1,359 New Mexico filings 2018-03 to 2026-06, so a flag is worth reading.
- swing: a percent moved more than SWINGS[measure] points from the quarter before. The
  limits sit above the 99th percentile of New Mexico's quarterly changes, 2018 to 2026.
- impossible: a share below 0 or above 100 (net charge-offs can be below 0). The build
  withholds that figure from the page (None, with the reason in `withheld`).
- zero reset, latest quarter only: CM0099 or RL0050 is 0 while the balance it is part of
  is over $1 million. It can be true (all long fixed-rate loans), and many small credit
  unions report it every quarter, so it's raised once, for the quarter the page shows.
- assets moved more than 25% in a quarter (often a merger).
- rate: an offered loan rate under 1% or over 30% (not 0, which means not offered). The
  federal credit union usury ceiling is 18%, so a value past 30% is almost surely a typo.
- yes/no: a profile answer that is neither 0 nor 1.
- no sites: a credit union with no office in NCUA's branch file.
- roster: a credit union joins or leaves New Mexico's list, or NCUA doesn't insure it.
"""

from __future__ import annotations

from .measures import plausible_rate, round2

PEER_GROUP_CODES = range(1, 7)  # NCUA peer groups 1 to 6, by assets

IDENTITY_TOLERANCE = 20
ASSET_JUMP = 0.25
SWINGS = {"net_worth_ratio": 3, "delinquency": 5, "net_charge_offs_12m": 2, "commercial_share": 3,
          "cre_reset_5y": 25, "home_reset_5y": 25}
PARTS = [
    ("ACCT_CM0099", ("ACCT_718A3", "ACCT_718A4")),
    ("ACCT_RL0050", ("ACCT_RL0047",)),
    ("ACCT_691P2", ("ACCT_691P1",)),
    ("ACCT_691C2", ("ACCT_691C1",)),
    ("ACCT_041B", ("ACCT_025B",)),
]
IDENTITIES = [
    ("ACCT_025B1", ("ACCT_025B",)),
    ("ACCT_718A5", ("ACCT_718A3", "ACCT_718A4")),
]
ZERO_RESET_FLOOR = 1_000_000
ZERO_RESETS = [("ACCT_CM0099", ("ACCT_718A3", "ACCT_718A4")), ("ACCT_RL0050", ("ACCT_RL0047",))]
CHARGE_OFF_ACCOUNTS = ("ACCT_550", "ACCT_551", "ACCT_025B")
SHARES = ["delinquency", "commercial_share", "cre_reset_5y", "home_reset_5y"]
PERCENTS = ["net_worth_ratio", "delinquency", "net_charge_offs_12m", "commercial_share", "cre_reset_5y", "home_reset_5y"]


class BuildError(Exception):
    pass


def flag(quarter, cu, check, detail):
    return {"quarter": quarter, "cu_number": cu.cu_number if cu else None, "name": cu.name if cu else None,
            "check": check, "detail": detail}


def required_accounts(dictionary: dict, quarter: str) -> set[str]:
    """Accounts the dictionary says this quarter has. An account still present in the last
    quarter the history read is treated as ongoing, so a new quarter that drops it fails."""
    entries = [a for m in dictionary["measures"] for a in m["accounts"] if a.get("quarters")]
    newest = max(a["quarters"]["to"] for a in entries)
    out = set()
    for a in entries:
        q = a["quarters"]
        if q["from"] <= quarter and (quarter <= q["to"] or q["to"] == newest):
            out.add(a["account"])
    return out


def schema(dictionary: dict, quarter: str, available: dict[str, str]) -> None:
    missing = sorted(required_accounts(dictionary, quarter) - set(available))
    if missing:
        raise BuildError(f"{quarter}: the dictionary says these accounts exist but the files lack them: {missing}")


def _total(a, codes):
    xs = [a[c] for c in codes]
    return None if any(x is None for x in xs) else sum(xs)


RATE_CODES = ("ACCT_521", "ACCT_522", "ACCT_523", "ACCT_524", "ACCT_563A")
YES_NO_CODES = ("ACCT_879A4", "ACCT_879C1", "ACCT_879D1", "ACCT_879D9", "ACCT_879D10", "ACCT_PP0034")
# Questions many credit unions leave blank rather than answer no: payday alternative loans are
# for federal credit unions only, and most leave PALs II empty. A blank there is null, unflagged.
BLANK_EXPECTED = {"ACCT_879D9", "ACCT_879D10"}
RATE_FOR = {"rate_credit_card": "ACCT_521", "rate_new_auto": "ACCT_523", "rate_used_auto": "ACCT_524",
            "rate_mortgage": "ACCT_563A", "rate_unsecured": "ACCT_522"}


def filing(quarter: str, cu, previous_cu=None, latest: bool = False) -> list[dict]:
    a = cu.accounts
    out = []
    for code in RATE_CODES:
        v = a.get(code)
        if v and not plausible_rate(v):
            out.append(flag(quarter, cu, "rate", f"{code} is stored as {v:g} ({v / 100:g}%), outside 1% to 30%; withheld"))
    for code in YES_NO_CODES:
        v = a.get(code)
        if v is not None and v not in (0, 1):
            out.append(flag(quarter, cu, "yes/no", f"{code} is {v}, not 0 or 1"))
    if hasattr(cu, "sites") and not cu.sites:
        out.append(flag(quarter, cu, "no sites", "no office in NCUA's branch file"))
    for code, codes in IDENTITIES:
        total = _total(a, codes)
        if a[code] is not None and total is not None and abs(a[code] - total) > IDENTITY_TOLERANCE:
            out.append(flag(quarter, cu, "identity", f"{code} is {a[code]:,.0f}; {' + '.join(codes)} is {total:,.0f}"))
    for part, codes in PARTS:
        total = _total(a, codes)
        if a[part] is not None and total is not None and a[part] > total + IDENTITY_TOLERANCE:
            out.append(flag(quarter, cu, "part over total", f"{part} {a[part]:,.0f} is more than {' + '.join(codes)} {total:,.0f}"))
    for part, codes in ZERO_RESETS if latest else []:
        total = _total(a, codes)
        if a[part] == 0 and total is not None and total > ZERO_RESET_FLOOR:
            out.append(flag(quarter, cu, "zero reset", f"{part} is 0 with {' + '.join(codes)} at {total:,.0f}"))
    den, how = net_worth_denominator(a)
    # A blank in any account of the formula is already flagged "not reported"; don't guess.
    formula = {"ACCT_997", "ACCT_998", "ACCT_010", "ACCT_010A", "ACCT_010B", "ACCT_010C", "ACCT_LC0047",
               "ACCT_NW0004", "ACCT_NW0010"}
    if formula & set(cu.not_reported):
        den = None
    if a["ACCT_997"] is not None and a["ACCT_998"] is not None and den:
        mine = round2(100 * a["ACCT_997"] / den)
        if abs(mine - a["ACCT_998"] / 100) > 0.011:
            out.append(flag(quarter, cu, "net worth", f"998 says {a['ACCT_998'] / 100:.2f}%; 997 / {how} is {mine:.2f}%"))
    for m in SHARES:
        v = cu.measures.get(m)
        if v is not None and not 0 <= v <= 100:
            out.append(flag(quarter, cu, "impossible", f"{m} is {v}%; withheld from the page"))
    if previous_cu is not None:
        now, then = a["ACCT_010"], previous_cu.accounts["ACCT_010"]
        if now and then and abs(now / then - 1) > ASSET_JUMP:
            out.append(flag(quarter, cu, "asset jump", f"total assets {then:,.0f} to {now:,.0f} in a quarter"))
        for m, limit in SWINGS.items():
            v, before = cu.measures.get(m), previous_cu.measures.get(m)
            if isinstance(v, float) and isinstance(before, float) and abs(v - before) > limit:
                out.append(flag(quarter, cu, "swing", f"{m} {before} to {v} in a quarter (limit {limit} points)"))
    return out


def net_worth_denominator(a) -> tuple[float | None, str]:
    """998's denominator per the instructions (Schedule G, Section 4, p. 127).

    LC0047 and NW0010 start in 2020-06 and NW0004 in 2023-03; before then they are None
    (not available) and count as 0 or fall back to 010, which is what the form did then.
    The caller skips the check when one is blank in a quarter that has it."""
    for code in ("ACCT_010A", "ACCT_010B", "ACCT_010C"):
        if a.get(code):
            return a[code] - (a.get("ACCT_LC0047") or 0) + (a.get("ACCT_NW0004") or 0), f"{code} - LC0047 + NW0004"
    if a.get("ACCT_NW0010") is not None:
        return a["ACCT_NW0010"], "NW0010"
    return a.get("ACCT_010"), "010"


RATE_MEASURES = ("rate_credit_card", "rate_new_auto", "rate_used_auto", "rate_mortgage", "rate_unsecured")


def withhold(cu) -> None:
    """Set impossible shares and implausible rates to None and say why, so the page never prints them."""
    for m in SHARES:
        v = cu.measures.get(m)
        if v is not None and not 0 <= v <= 100:
            cu.withheld[m] = f"{v}% from the filing, which can't be right"
            cu.measures[m] = None
    accounts = getattr(cu, "accounts", {})
    for m in RATE_MEASURES:
        raw = accounts.get(RATE_FOR[m])
        if raw and not plausible_rate(raw):
            cu.withheld[m] = f"{raw / 100:g}% as filed, outside 1% to 30%, most likely a typo in the filing"
            cu.measures[m] = None


def roster(quarter: str, now: dict, before: dict | None, uninsured: list[str]) -> list[dict]:
    out = [flag(quarter, None, "roster", f"credit union {n} is in New Mexico but not federally insured; left out")
           for n in uninsured]
    out += [flag(quarter, c, "roster", "no NCUA peer group (1 to 6) this quarter; no peer comparison")
            for c in now.values() if c.peer_group not in PEER_GROUP_CODES]
    if before is None:
        return out
    for n in sorted(set(now) - set(before)):
        out.append(flag(quarter, now[n], "roster", "joins New Mexico's list this quarter"))
    for n in sorted(set(before) - set(now)):
        out.append(flag(quarter, before[n], "roster", "not in New Mexico's list this quarter; stopped reporting after the last"))
    return out
