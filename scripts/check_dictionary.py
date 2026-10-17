"""Check data/dictionary.json against data/account-history.json.

Fails if NCUA's wording or an account's quarters in the dictionary don't match what the
account history read from the zips, or if a formula names an account the dictionary doesn't
list. Run after scripts/account-history.mjs: uv run scripts/check_dictionary.py

--sync-quarters first moves an account's quarters (and its current wording's end date) forward when the
only change is that it is in newer, back-to-back quarters' data with the same first quarter and wording,
the routine case when a new NCUA quarter is built, and rewrites data/dictionary.json. A gap, a new
first quarter or new wording is not synced, so the check below still reports it.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def in_data_quarters(h: dict) -> list[str]:
    return sorted({x for qs in h["tables"].values() for x in qs})


def sync_quarters(dictionary: dict, history: dict) -> int:
    """Extend each entry's quarters to newer quarters in the data. Returns how many changed."""
    changed = 0
    for m in dictionary["measures"]:
        for a in m["accounts"]:
            changed += extend(a, history)
    for a in dictionary["not_used"]:
        changed += extend(a, history)
    return changed


def next_quarter(q: str) -> str:
    y, m = map(int, q.split("-"))
    return f"{y + 1}-03" if m == 12 else f"{y}-{m + 3:02d}"


def extend(a: dict, history: dict) -> int:
    """Move one entry's quarters forward when its account is in newer, back-to-back quarters with the same
    first quarter and the same wording. Anything else is left for the check to report."""
    if "see" in a or a["account"] not in history:
        return 0
    h = history[a["account"]]
    q, in_data = a["quarters"], in_data_quarters(h)
    newer = [x for x in in_data if x > q["to"]]
    if not newer or in_data[0] != q["from"] or len(in_data) != q["count"] + len(newer):
        return 0
    chain = [q["to"]] + newer
    if any(next_quarter(x) != y for x, y in zip(chain, chain[1:])):
        return 0
    descs = h["descriptions"]
    name, desc = descs[-1]["text"].split(" | ", 1)
    if (a.get("ncua_name"), a.get("ncua_description")) != (name, desc):
        return 0
    recorded = a.get("wording_history", [])
    if recorded:
        same_before = [(w["from"], w["to"], w["text"]) for w in recorded[:-1]] == [(w["from"], w["to"], w["text"]) for w in descs[:-1]]
        last_same = (recorded[-1]["from"], recorded[-1]["text"]) == (descs[-1]["from"], descs[-1]["text"])
        if len(recorded) != len(descs) or not same_before or not last_same:
            return 0
        recorded[-1]["to"] = descs[-1]["to"]
    q["to"], q["count"] = in_data[-1], len(in_data)
    return 1


def main() -> int:
    path = ROOT / "data/dictionary.json"
    dictionary = json.loads(path.read_text())
    history = json.loads((ROOT / "data/account-history.json").read_text())["accounts"]
    if "--sync-quarters" in sys.argv[1:]:
        n = sync_quarters(dictionary, history)
        if n:
            path.write_text(json.dumps(dictionary, indent=2, ensure_ascii=False) + "\n")
        print(f"moved {n} accounts' quarters forward")
    errors = []
    entries = [(m["id"], a) for m in dictionary["measures"] for a in m["accounts"]]
    entries += [("not_used", a) for a in dictionary["not_used"]]
    by_id = {m["id"]: m for m in dictionary["measures"]}
    defined = {a["account"] for _, a in entries if "see" not in a}
    listed = set(defined)

    for measure, a in entries:
        code = a["account"]
        if "see" in a:
            target = by_id.get(a["see"])
            if target is None or code not in {x["account"] for x in target["accounts"] if "see" not in x}:
                errors.append(f"{measure}: {code} points to {a['see']}, which doesn't define it")
            else:
                listed.add(code)
            continue
        h = history.get(code)
        if h is None:
            errors.append(f"{measure}: {code} is not in account-history.json; add it to ACCOUNTS")
            continue
        name, desc = h["descriptions"][-1]["text"].split(" | ", 1)
        if (a["ncua_name"], a["ncua_description"]) != (name, desc):
            errors.append(f"{measure}: {code} wording differs from AcctDesc.txt {h['descriptions'][-1]['to']}")
        # The quarters an account is in the data files, which is what the build reads. NCUA's
        # dictionary can list an account before its column ships (879D10: 2020-03 against 2021-12).
        q = a["quarters"]
        in_data = in_data_quarters(h)
        if not in_data or (q["from"], q["to"], q["count"]) != (in_data[0], in_data[-1], len(in_data)):
            errors.append(f"{measure}: {code} quarters differ from the quarters it is in the data")
        recorded = [(w["from"], w["to"], w["text"]) for w in a.get("wording_history", [])]
        actual = [(w["from"], w["to"], w["text"]) for w in h["descriptions"]]
        if (len(actual) > 1 or recorded) and recorded != actual:
            errors.append(f"{measure}: {code} wording history differs from the account history")

    for m in dictionary["measures"]:
        texts = [m["formula"]] + [c["rule"] for c in m.get("checks", [])]
        for text in texts:
            for n in re.findall(r"\bACCT_([0-9A-Z]+)\b", text):
                if f"ACCT_{n}" not in listed:
                    errors.append(f"{m['id']}: formula or check uses ACCT_{n}, which no entry lists")

    for e in errors:
        print(e, file=sys.stderr)
    print(f"{len(dictionary['measures'])} measures, {len(listed)} accounts, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
