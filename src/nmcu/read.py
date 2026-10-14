"""Read one quarter's NCUA zip: the New Mexico roster and the dictionary's accounts.

Downloading is the package's (`ncua_data.download`, which finds the links on NCUA's
quarterly data page). Reading is ours, because the package keeps non-zero values only
and fills the rest with 0. Here an account a quarter doesn't have is None ("not
available"), a blank cell is None ("not reported"), and 0 is stored only when the
file says 0. None of our accounts has a blank cell in 2017-12 to 2026-06, but the
rule holds if NCUA starts leaving them.
"""

from __future__ import annotations

import csv
import io
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

STATE = "NM"


@dataclass
class CreditUnion:
    cu_number: str
    name: str
    city: str
    peer_group: int | None
    federally_insured: bool
    accounts: dict[str, float | None] = field(default_factory=dict)
    # Accounts present as a column this quarter but blank for this credit union.
    not_reported: list[str] = field(default_factory=list)
    # Filled in by the build: measure id -> value.
    measures: dict[str, object] = field(default_factory=dict)
    # Measures set to None because the filing gives an impossible value: id -> reason.
    withheld: dict[str, str] = field(default_factory=dict)
    # Why a measure is None when the reason isn't a missing account: id -> words for the page.
    notes: dict[str, str] = field(default_factory=dict)
    # Its offices from NCUA's branch file, every state (the page filters to New Mexico).
    sites: list[dict] = field(default_factory=list)


@dataclass
class Quarter:
    quarter: str
    credit_unions: dict[str, CreditUnion]
    # Accounts that exist as a column in this quarter's files, and which file holds each.
    available: dict[str, str]
    # Credit unions with STATE = NM that NCUA doesn't insure (left out of everything).
    uninsured: list[str]
    # Credit unions in the country this quarter.
    national_count: int


def _rows(z: zipfile.ZipFile, name: str):
    # NCUA's files are Windows-1252, as the package notes.
    raw = z.read(name)
    if raw.startswith(b"\xef\xbb\xbf"):  # a UTF-8 byte-order mark on some files
        raw = raw[3:]
    text = raw.decode("cp1252", errors="replace")
    for row in csv.DictReader(io.StringIO(text)):
        yield {k.strip().upper(): (v if v is None else v.strip()) for k, v in row.items() if k}


def _flag(text: str | None) -> bool | None:
    return {"1": True, "0": False}.get(text)


def _number(text: str | None) -> float | None:
    if text is None or text == "":
        return None
    return float(text)


def read_quarter(zip_path: Path, quarter: str, accounts: set[str]) -> Quarter:
    with zipfile.ZipFile(zip_path) as z:
        names = {n.lower(): n for n in z.namelist()}
        roster: dict[str, CreditUnion] = {}
        uninsured: list[str] = []
        national = 0
        for r in _rows(z, names["foicu.txt"]):
            national += 1
            if r.get("STATE") != STATE:
                continue
            insured = r.get("CU_TYPE") != "3"
            if not insured:
                uninsured.append(r["CU_NUMBER"])
                continue
            pg = r.get("PEER_GROUP")
            roster[r["CU_NUMBER"]] = CreditUnion(
                cu_number=r["CU_NUMBER"],
                name=r.get("CU_NAME", ""),
                city=r.get("CITY", ""),
                peer_group=int(pg) if pg and pg.isdigit() else None,
                federally_insured=insured,
            )

        available: dict[str, str] = {}
        for lower, name in sorted(names.items()):
            if not (lower.startswith("fs220") and lower.endswith(".txt")):
                continue
            rows = _rows(z, name)
            first = next(rows, None)
            if first is None:
                continue
            here = accounts & set(first)
            if not here:
                continue
            for a in here:
                available[a] = name.upper()
            for r in [first, *rows]:
                cu = roster.get(r["CU_NUMBER"])
                if cu is None:
                    continue
                for a in here:
                    v = _number(r.get(a))
                    cu.accounts[a] = v
                    if v is None:
                        cu.not_reported.append(a)

    # NCUA's site list: every office, with county, hours and what it offers.
    site_file = names.get("credit union branch information.txt")
    if site_file:
        with zipfile.ZipFile(zip_path) as z:
            for r in _rows(z, site_file):
                cu = roster.get(r["CU_NUMBER"])
                if cu is None:
                    continue
                cu.sites.append({
                    "name": r.get("SITENAME", ""),
                    "type": r.get("SITETYPENAME", ""),
                    "main_office": r.get("MAINOFFICE", "").lower() == "yes",
                    "address": " ".join(x for x in (r.get("PHYSICALADDRESSLINE1", ""), r.get("PHYSICALADDRESSLINE2", "")) if x),
                    "city": r.get("PHYSICALADDRESSCITY", ""),
                    "state": r.get("PHYSICALADDRESSSTATECODE", ""),
                    "zip": r.get("PHYSICALADDRESSPOSTALCODE", ""),
                    # NCUA renamed the column in 2025-03.
                    "county": r.get("PHYSICALADDRESSCOUNTYNAME2") or r.get("PHYSICALADDRESSCOUNTYNAME") or None,
                    "phone": r.get("PHONENUMBER") or None,
                    # Hours and the three services are in the file from 2020-12 only. A column the
                    # file lacks, or a value other than 0 or 1, is None (not reported), never "no".
                    "hours": r.get("HOURSOFOPERATION") or None,
                    "member_services": _flag(r.get("MEMBERSERVICES")),
                    "atm": _flag(r.get("ATM")),
                    "drive_through": _flag(r.get("DRIVETHRU")),
                })
        for cu in roster.values():
            cu.sites.sort(key=lambda x: (not x["main_office"], x["state"] != STATE, x["county"] or "", x["city"], x["name"]))

    for cu in roster.values():
        for a in accounts:
            if a not in available:
                cu.accounts[a] = None  # not available this quarter
            elif a not in cu.accounts:
                cu.accounts[a] = None  # the credit union has no row in that file
                cu.not_reported.append(a)
    return Quarter(quarter, roster, available, uninsured, national)
