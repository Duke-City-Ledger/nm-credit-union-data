"""Tests for scripts/watch.py ("Worth a look") on small made-up fixtures."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("watch", Path(__file__).resolve().parent.parent / "scripts" / "watch.py")
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)

QS = ["2025-03", "2025-06", "2025-09", "2025-12", "2026-03"]
BASE = {"total_assets": 500_000_000, "members": 10000, "net_worth_ratio": 12.0, "delinquency": 0.5,
        "net_charge_offs_12m": 0.4, "commercial_share": 5.0, "cre_reset_5y": 20.0, "home_reset_5y": 20.0}


def build(**series):
    """One credit union ('1'); series maps a measure to five values. Peers given as peer_<measure>."""
    data = {}
    for i, q in enumerate(QS):
        m = dict(BASE)
        for k, v in series.items():
            if not k.startswith("peer_"):
                m[k] = v[i]
        peers = {k[5:]: {"median": v[i], "n_others": 9} for k, v in series.items() if k.startswith("peer_") and v[i] is not None}
        data[q] = {"1": {"cu_number": "1", "name": "TEST", "measures": m, "peers": peers}}
    return data


def names(data):
    return {s["signal"] for s in watch.signals(data, QS, QS[-1], "1")}


class Signals(unittest.TestCase):
    def test_quiet_credit_union_has_none(self):
        self.assertEqual(names(build()), set())

    def test_net_worth_near_line(self):
        self.assertIn("net worth ratio near 7%", names(build(net_worth_ratio=[7.9] * 5)))
        self.assertIn("net worth ratio near 7%", names(build(net_worth_ratio=[6.2] * 5)))
        self.assertNotIn("net worth ratio near 7%", names(build(net_worth_ratio=[8.5] * 5)))

    def test_net_worth_drop(self):
        self.assertIn("net worth ratio down", names(build(net_worth_ratio=[10.5, 10, 9.5, 9, 8.9])))
        self.assertNotIn("net worth ratio down", names(build(net_worth_ratio=[16, 15, 14, 14, 13])))  # still high
        self.assertNotIn("net worth ratio down", names(build(net_worth_ratio=[10.5, 10, 9.5, 9, 9.1])))  # only 1.4

    def test_net_worth_null_is_not_zero(self):
        n = names(build(net_worth_ratio=[None, 9, 9, 9, None]))
        self.assertFalse({"net worth ratio near 7%", "net worth ratio down"} & n)
        self.assertNotIn("net worth ratio down", names(build(net_worth_ratio=[None, 9, 9, 9, 8])))

    def test_late_loans_rising(self):
        self.assertIn("late loans rising", names(build(delinquency=[0.5, 0.6, 1.0, 1.4, 1.8])))
        self.assertNotIn("late loans rising", names(build(delinquency=[0.5, 0.6, 1.0, 0.9, 1.8])))  # not in a row
        self.assertNotIn("late loans rising", names(build(delinquency=[0.5, 0.6, 0.7, 0.8, 0.9])))  # up under 1 point
        self.assertNotIn("late loans rising", names(build(delinquency=[0.5, None, 1.0, 1.4, 1.8])))

    def test_late_loans_vs_peers(self):
        self.assertIn("late loans above peers", names(build(delinquency=[1] * 4 + [2.5], peer_delinquency=[1] * 4 + [1.0])))
        self.assertNotIn("late loans above peers", names(build(delinquency=[1] * 4 + [1.9], peer_delinquency=[0.5] * 5)))  # under floor
        self.assertNotIn("late loans above peers", names(build(delinquency=[1] * 4 + [2.5], peer_delinquency=[1] * 4 + [None])))  # no peers
        self.assertNotIn("late loans above peers", names(build(delinquency=[1] * 4 + [2.5], peer_delinquency=[1] * 4 + [1.5])))

    def test_charge_offs(self):
        self.assertIn("charge-offs above peers", names(build(net_charge_offs_12m=[0.4] * 4 + [1.6], peer_net_charge_offs_12m=[0.5] * 5)))
        self.assertIn("charge-offs up", names(build(net_charge_offs_12m=[0.4, 0.5, 0.8, 1.2, 1.6])))
        self.assertNotIn("charge-offs up", names(build(net_charge_offs_12m=[None, 0.5, 0.8, 1.2, 1.6])))
        self.assertNotIn("charge-offs above peers", names(build(net_charge_offs_12m=[None] * 4 + [None], peer_net_charge_offs_12m=[0.5] * 5)))

    def test_commercial_share(self):
        self.assertIn("business loans growing fast", names(build(commercial_share=[5, 6, 8, 9, 10.5])))
        self.assertNotIn("business loans growing fast", names(build(commercial_share=[5, 6, 8, 9, 9.9])))
        self.assertNotIn("business loans growing fast", names(build(commercial_share=[None, 6, 8, 9, 15])))

    def test_resets(self):
        self.assertIn("commercial real estate loans resetting soon", names(build(cre_reset_5y=[60, 65, 70, 78, 80])))
        self.assertNotIn("commercial real estate loans resetting soon", names(build(cre_reset_5y=[80, 80, 80, 80, 80])))  # high but flat
        self.assertNotIn("commercial real estate loans resetting soon", names(build(cre_reset_5y=[None] * 5)))
        self.assertIn("home loans resetting soon", names(build(home_reset_5y=[60, 65, 70, 78, 80])))

    def test_shrinking(self):
        self.assertIn("members shrinking", names(build(members=[1000, 950, 900, 880, 850])))
        self.assertNotIn("members shrinking", names(build(members=[1000, 950, 900, 880, 950])))
        self.assertNotIn("members shrinking", names(build(members=[1000, 999, 998, 997, 996])))  # under 10%
        self.assertNotIn("members shrinking", names(build(members=[1000, None, 900, 880, 850])))
        self.assertIn("total assets shrinking", names(build(total_assets=[500e6, 480e6, 450e6, 440e6, 420e6])))

    def test_missing_quarter_history(self):
        data = build(members=[1000, 950, 900, 880, 850])
        del data["2025-06"]
        self.assertNotIn("members shrinking", {s["signal"] for s in watch.signals(data, QS, QS[-1], "1")})

    def test_gap_in_files_is_not_consecutive(self):
        # A quarter file missing from the middle must not let five calendar quarters read as four in a row.
        data = build(members=[1000, 950, 900, 880, 850])
        del data["2025-09"]
        qs = [q for q in QS if q in data]
        self.assertNotIn("members shrinking", {s["signal"] for s in watch.signals(data, qs, qs[-1], "1")})

    def test_short_history_keeps_current_value(self):
        # The first quarter a credit union appears still gets the level check.
        data = {"2026-03": build(net_worth_ratio=[7.5] * 5)["2026-03"]}
        self.assertIn("net worth ratio near 7%", {s["signal"] for s in watch.signals(data, ["2026-03"], "2026-03", "1")})

    def test_shift_by_calendar(self):
        self.assertEqual(watch.shift("2026-03", -1), "2025-12")
        self.assertEqual(watch.shift("2025-12", 1), "2026-03")
        self.assertEqual(watch.shift("2026-06", -4), "2025-06")

    def test_json_inside_repo_refused(self):
        root = Path(__file__).resolve().parent.parent
        self.assertTrue(watch.inside(root / "out" / "leads.json", root))
        self.assertFalse(watch.inside(Path("/tmp/leads.json"), root))

    def test_zero_peer_median_still_flags(self):
        data = build(net_charge_offs_12m=[0.4, 0.4, 0.4, 0.4, 1.62], peer_net_charge_offs_12m=[0.0] * 5)
        found = {s["signal"]: s["detail"] for s in watch.signals(data, QS, QS[-1], "1")}
        self.assertIn("charge-offs above peers", found)
        self.assertIn("against a 0% peer-group median", found["charge-offs above peers"])

    def test_small_credit_union_marked(self):
        data = build(total_assets=[9e6] * 5, net_worth_ratio=[7.5] * 5)
        items = watch.watch(data, QS, QS[-1])
        self.assertTrue(items and all(i["small"] and "Small credit union" in i["detail"] for i in items))
        big = watch.watch(build(net_worth_ratio=[7.5] * 5), QS, QS[-1])
        self.assertFalse(any(i["small"] for i in big))

    def test_markdown_is_neutral(self):
        text = watch.markdown(watch.watch(build(net_worth_ratio=[10.5, 10, 9.5, 9, 7.5], delinquency=[1] * 4 + [2.5], peer_delinquency=[0.5] * 5), QS, QS[-1]), QS[-1])
        for word in ("risky", "failing", "weak", "bad", "—"):
            self.assertNotIn(word, text)
        self.assertIn("fell from 10.5% in Q1 2025 to 7.5% in Q1 2026", text)


if __name__ == "__main__":
    unittest.main()
