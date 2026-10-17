"""Worth a look: story leads from the quarterly credit union figures. For the editor's desk only.

Reads out/quarters/*.json and prints a Markdown section. With --json PATH it also writes the items there.
The list is never committed to this public repo: the desk runs it and keeps the output private.
Never printed on the public site. Wording is neutral: figures and quarters, no grades.

Run: uv run scripts/watch.py [--quarter YYYY-MM] [--backtest] [--json PATH outside the repo]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "out" / "quarters"

# Every threshold lives here and in the README. Change both together.
T = {
    "nwr_line": 7.0,  # NCUA's well-capitalized level
    "nwr_near": 1.0,  # within this many points of the line, either side, down to the floor below
    "nwr_floor": 0.0,
    "nwr_drop": 1.5,  # points lost over four quarters...
    "nwr_drop_below": 10.0,  # ...ending below this percent (a fall from 15% to 13% is not a lead)
    "delq_rise_quarters": 3,  # rising this many quarters in a row...
    "delq_rise_total": 1.0,  # ...and up at least this many points over the run
    "delq_peer_multiple": 2.0,  # at least this many times the peer median...
    "delq_peer_floor": 2.0,  # ...and at least this percent
    "nco_peer_multiple": 2.0,  # at least this many times the peer median...
    "nco_peer_floor": 1.5,  # ...and at least this percent
    "nco_yoy_rise": 1.0,  # or up this many points from a year earlier...
    "nco_yoy_floor": 1.5,  # ...to at least this percent
    "commercial_rise": 5.0,  # points in a year
    "reset_level": 75.0,  # percent of the book resetting within five years...
    "reset_rise": 10.0,  # ...and up this many points in a year
    "decline_quarters": 4,  # members or assets down this many quarters in a row...
    "decline_total": 10.0,  # ...and down at least this percent over the run
    "small_assets": 10_000_000,
}


def quarters_available(qdir: Path = QDIR) -> list[str]:
    return sorted(p.stem for p in qdir.glob("*.json"))


def load(qdir: Path = QDIR) -> dict[str, dict[str, dict]]:
    """quarter -> cu_number -> credit union record."""
    out = {}
    for q in quarters_available(qdir):
        d = json.loads((qdir / f"{q}.json").read_text())
        out[q] = {c["cu_number"]: c for c in d["credit_unions"]}
    return out


def shift(q: str, k: int) -> str:
    """The quarter k quarters after q (before, when k is negative), by the calendar."""
    y, m = map(int, q.split("-"))
    i = y * 4 + (m // 3 - 1) + k
    return f"{i // 4}-{(i % 4 + 1) * 3:02d}"


def series(data: dict, quarters: list[str], q: str, cu: str, measure: str, n: int) -> list:
    """The values of a measure for the n+1 calendar quarters ending at q (oldest first). None where the
    quarter has no file, the credit union didn't report, or the measure is missing, so a gap in the data
    never reads as consecutive quarters, and the current value stands even when the history is short."""
    vals = []
    for k in range(-n, 1):
        rec = data.get(shift(q, k), {}).get(cu)
        v = rec["measures"].get(measure) if rec else None
        vals.append(v if isinstance(v, (int, float)) and not isinstance(v, bool) else None)
    return vals


def has_all(vals: list) -> bool:
    return all(v is not None for v in vals)


def qlabel(q: str) -> str:
    y, m = q.split("-")
    return f"{ {'03': 'Q1', '06': 'Q2', '09': 'Q3', '12': 'Q4'}[m] } {y}"


def pct(v: float) -> str:
    return f"{v:g}%"


def money(v: float) -> str:
    if v >= 1e9:
        return f"${v / 1e9:.2f} billion"
    return f"${v / 1e6:.1f} million"


def signals(data: dict, quarters: list[str], q: str, cu: str) -> list[dict]:
    rec = data[q][cu]
    out = []

    def add(signal: str, detail: str):
        out.append({"signal": signal, "detail": detail})

    # Net worth ratio
    nw = series(data, quarters, q, cu, "net_worth_ratio", 4)
    now = nw[-1]
    if now is not None:
        line, near = T["nwr_line"], T["nwr_near"]
        if line - near <= now <= line + near and now >= T["nwr_floor"]:
            add("net worth ratio near 7%", f"Net worth ratio is {pct(now)} in {qlabel(q)}, within 1 point of the 7% level NCUA calls well capitalized.")
        if nw[0] is not None and nw[0] - now >= T["nwr_drop"] and now < T["nwr_drop_below"]:
            add("net worth ratio down", f"Net worth ratio fell from {pct(nw[0])} in {qlabel(shift(q, -4))} to {pct(now)} in {qlabel(q)}, down {nw[0] - now:.2f} points over four quarters.")

    # Delinquency
    dq = series(data, quarters, q, cu, "delinquency", T["delq_rise_quarters"])
    if has_all(dq) and all(b > a for a, b in zip(dq, dq[1:])) and dq[-1] - dq[0] >= T["delq_rise_total"]:
        n = T["delq_rise_quarters"]
        add("late loans rising", f"Loans 60 or more days late rose {n} quarters in a row, from {pct(dq[0])} in {qlabel(shift(q, -n))} to {pct(dq[-1])} in {qlabel(q)}.")
    if dq[-1] is not None:
        med = (rec.get("peers") or {}).get("delinquency", {}).get("median")
        if med is not None and med > 0 and dq[-1] >= T["delq_peer_multiple"] * med and dq[-1] >= T["delq_peer_floor"]:
            add("late loans above peers", f"Loans 60 or more days late were {pct(dq[-1])} in {qlabel(q)}, {dq[-1] / med:.1f} times the {pct(med)} median of its peer group.")

    # Net charge-offs
    nc = series(data, quarters, q, cu, "net_charge_offs_12m", 4)
    if nc[-1] is not None:
        med = (rec.get("peers") or {}).get("net_charge_offs_12m", {}).get("median")
        if med is not None and med > 0 and nc[-1] >= T["nco_peer_multiple"] * med and nc[-1] >= T["nco_peer_floor"]:
            add("charge-offs above peers", f"Loans written off, net of recoveries, over 12 months were {pct(nc[-1])} of loans in {qlabel(q)}, {nc[-1] / med:.1f} times the {pct(med)} peer-group median.")
        elif nc[0] is not None and nc[-1] - nc[0] >= T["nco_yoy_rise"] and nc[-1] >= T["nco_yoy_floor"]:
            add("charge-offs up", f"Loans written off, net of recoveries, over 12 months rose from {pct(nc[0])} in {qlabel(shift(q, -4))} to {pct(nc[-1])} in {qlabel(q)}.")

    # Loan mix
    cs = series(data, quarters, q, cu, "commercial_share", 4)
    if cs[0] is not None and cs[-1] is not None and cs[-1] - cs[0] >= T["commercial_rise"]:
        add("business loans growing fast", f"Business loans rose from {pct(cs[0])} of all loans in {qlabel(shift(q, -4))} to {pct(cs[-1])} in {qlabel(q)}.")
    for key, label in (("cre_reset_5y", "commercial real estate"), ("home_reset_5y", "home")):
        rs = series(data, quarters, q, cu, key, 4)
        if rs[0] is not None and rs[-1] is not None and rs[-1] >= T["reset_level"] and rs[-1] - rs[0] >= T["reset_rise"]:
            add(f"{label} loans resetting soon", f"{pct(rs[-1])} of its {label} loans can change rate or come due within five years in {qlabel(q)}, up from {pct(rs[0])} in {qlabel(shift(q, -4))}.")

    # Shrinking
    n = T["decline_quarters"]
    for key, label, fmt in (("members", "Members", lambda v: f"{v:,.0f}"), ("total_assets", "Total assets", money)):
        s = series(data, quarters, q, cu, key, n)
        if has_all(s) and all(b < a for a, b in zip(s, s[1:])) and s[0] > 0 and (s[0] - s[-1]) / s[0] * 100 >= T["decline_total"]:
            add(f"{label.lower()} shrinking", f"{label} fell {n} quarters in a row, from {fmt(s[0])} in {qlabel(shift(q, -n))} to {fmt(s[-1])} in {qlabel(q)}, down {(s[0] - s[-1]) / s[0] * 100:.0f}%.")
    return out


def watch(data: dict, quarters: list[str], q: str) -> list[dict]:
    items = []
    for cu, rec in sorted(data[q].items(), key=lambda kv: kv[1]["name"]):
        assets = rec["measures"].get("total_assets")
        small = isinstance(assets, (int, float)) and assets < T["small_assets"]
        for s in signals(data, quarters, q, cu):
            detail = s["detail"] + (" Small credit union: one loan can move these figures." if small else "")
            items.append({"quarter": q, "cu_number": cu, "name": rec["name"], "signal": s["signal"], "detail": detail, "small": small})
    return items


def markdown(items: list[dict], q: str) -> str:
    lines = [f"### Worth a look, {qlabel(q)}", "", "Leads for the desk, not findings. Not for the page.", ""]
    if not items:
        return "\n".join(lines + ["Nothing met a threshold this quarter.", ""])
    by_cu: dict[str, list[dict]] = {}
    for it in items:
        by_cu.setdefault(it["cu_number"], []).append(it)
    for cu, its in by_cu.items():
        tag = " (small credit union)" if its[0]["small"] else ""
        lines.append(f"- **{its[0]['name']}**{tag}, charter {cu}")
        for it in its:
            lines.append(f"  - {it['signal']}: {it['detail'].replace(' Small credit union: one loan can move these figures.', '')}")
    return "\n".join(lines + [""])


def backtest(root: Path, data: dict, quarters: list[str]) -> int:
    eagle = next((cu for cu, r in data[quarters[-1]].items() if r["name"] == "U.S. EAGLE"), None)
    rows, first = [], None
    for q in quarters:
        if q < "2018-12":
            continue
        items = watch(data, quarters, q)
        cus = {i["cu_number"] for i in items}
        e = sorted({i["signal"] for i in items if i["cu_number"] == eagle})
        if e and first is None:
            first = (q, e)
        rows.append((q, len(items), len(cus), e))
    before = [r for r in rows if r[0] < "2026-05" and r[3]]
    L = ["# Worth a look: backtest", "",
         "Generated by `uv run scripts/watch.py --backtest`. Items are signals; credit unions is how many different credit unions had at least one.", "",
         "## U.S. Eagle (charter %s)" % eagle, ""]
    if before:
        L += [f"Flagged before USDA revoked its lender status in May 2026: yes. The first quarter with a signal was {qlabel(first[0])} ({'; '.join(first[1])}). It had a signal in {len(before)} of the {len([r for r in rows if r[0] < '2026-05'])} quarters before May 2026.", ""]
        L += ["Quarters with a signal, before May 2026:", ""] + [f"- {qlabel(r[0])}: {', '.join(r[3])}" for r in before] + [""]
    else:
        L += ["Flagged before May 2026: no.", ""]
    L += ["## Items per quarter", "", "| Quarter | Items | Credit unions |", "| --- | --- | --- |"]
    L += [f"| {qlabel(q)} | {n} | {c} |" for q, n, c, _ in rows]
    counts = [c for _, _, c, _ in rows]
    L += ["", f"Credit unions flagged per quarter: median {statistics.median(counts)}, range {min(counts)} to {max(counts)}. 2020 and 2021 run high because the pandemic moved loan, member and net worth figures for many credit unions at once.", "",
          "Caveats: a signal is a reason to look, not a finding. This backtest uses only Eagle's known outcome, so it says nothing about false alarms beyond the counts above.", ""]
    print("\n".join(L))
    return 0


def inside(path: Path, root: Path) -> bool:
    """True when path would land in the repository, where it could be committed to this public repo."""
    return path.resolve().is_relative_to(root.resolve())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quarter")
    ap.add_argument("--backtest", action="store_true", help="print the backtest for every quarter from 2018-12")
    ap.add_argument("--json", type=Path, help="also write the items to this file (keep it outside the repo)")
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    qdir = a.root / "out" / "quarters"
    data = load(qdir)
    quarters = sorted(data)
    if a.backtest:
        return backtest(a.root, data, quarters)
    q = a.quarter or quarters[-1]
    if q not in data:
        print(f"No such quarter: {q}", file=sys.stderr)
        return 1
    if a.json and inside(a.json, a.root):
        print(f"{a.json} is inside the repository; the list stays private, so write it somewhere outside {a.root}", file=sys.stderr)
        return 2
    items = watch(data, quarters, q)
    if a.json:
        a.json.write_text(json.dumps({"quarter": q, "items": items}, indent=2) + "\n")
    print(markdown(items, q))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
