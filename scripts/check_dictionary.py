"""Check data/dictionary.json against data/account-history.json.

Fails if NCUA's wording or an account's quarters in the dictionary don't match what the
account history read from the zips, or if a formula names an account the dictionary doesn't
list. Run after scripts/account-history.mjs: uv run scripts/check_dictionary.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    dictionary = json.loads((ROOT / "data/dictionary.json").read_text())
    history = json.loads((ROOT / "data/account-history.json").read_text())["accounts"]
    errors = []
    entries = [(m["id"], a) for m in dictionary["measures"] for a in m["accounts"]]
    entries += [("not_used", a) for a in dictionary["not_used"]]
    listed = {a["account"] for _, a in entries}

    for measure, a in entries:
        code = a["account"]
        if "see" in a:
            continue
        h = history.get(code)
        if h is None:
            errors.append(f"{measure}: {code} is not in account-history.json; add it to ACCOUNTS")
            continue
        name, desc = h["descriptions"][-1]["text"].split(" | ", 1)
        if (a["ncua_name"], a["ncua_description"]) != (name, desc):
            errors.append(f"{measure}: {code} wording differs from AcctDesc.txt {h['descriptions'][-1]['to']}")
        q = a["quarters"]
        if (q["from"], q["to"], q["count"]) != (h["quarters"][0], h["quarters"][-1], len(h["quarters"])):
            errors.append(f"{measure}: {code} quarters differ from the history")
        if len(h["descriptions"]) > 1 and len(a.get("wording_history", [])) != len(h["descriptions"]):
            errors.append(f"{measure}: {code} has {len(h['descriptions'])} wordings; the dictionary records fewer")

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
