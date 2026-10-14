"""Tests: the formulas on made-up numbers, and the real 2026-06 figures against NCUA's
published ratios and against figures worked by hand from the raw zip.

The real-data tests need .cache/call-report-data-2026-06.zip (and 2025-06, 2025-12 for
charge-offs); they skip without it. Run: uv run python -m unittest discover -s tests
"""

from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace

from nmcu import checks
from nmcu.build import peers, quantile
from nmcu.measures import (
    ROOT,
    SIMPLE,
    all_accounts,
    check_against_dictionary,
    load_dictionary,
    net_charge_offs_12m,
    prior,
    round2,
)
from nmcu.read import read_quarter

CACHE = ROOT / ".cache"


def cu(n, peer_group=3, **measures):
    return SimpleNamespace(cu_number=n, name=n, peer_group=peer_group, measures=measures, withheld={})


class Formulas(unittest.TestCase):
    def test_rounding_is_half_up(self):
        self.assertEqual(round2(2.675), 2.68)
        self.assertEqual(round2(20.875), 20.88)
        self.assertEqual(round2(-0.125), -0.13)
        self.assertEqual(str(round2(-0.001)), "0.0")  # never "-0.0"

    def test_zero_denominator_is_none_not_zero(self):
        a = {"ACCT_041B": 5.0, "ACCT_025B": 0.0}
        self.assertIsNone(SIMPLE["delinquency"][1](a))
        a = {"ACCT_CM0099": 0.0, "ACCT_718A3": 0.0, "ACCT_718A4": 0.0}
        self.assertIsNone(SIMPLE["cre_reset_5y"][1](a))

    def test_missing_account_is_none(self):
        a = {"ACCT_CM0099": None, "ACCT_718A3": 10.0, "ACCT_718A4": 0.0}
        self.assertIsNone(SIMPLE["cre_reset_5y"][1](a))

    def test_prior(self):
        self.assertEqual(prior("2026-06", 4), "2025-06")
        self.assertEqual(prior("2026-03", 1), "2025-12")

    def test_charge_offs_twelve_months(self):
        h = {
            "2025-06": {"ACCT_550": 40.0, "ACCT_551": 10.0, "ACCT_025B": 1000.0},
            "2025-12": {"ACCT_550": 100.0, "ACCT_551": 20.0, "ACCT_025B": 1100.0},
            "2026-06": {"ACCT_550": 50.0, "ACCT_551": 5.0, "ACCT_025B": 1200.0},
        }
        # 45 this year + 80 last year - 30 in last year's first half = 95, over avg loans 1100.
        self.assertEqual(net_charge_offs_12m(h, "2026-06"), round2(100 * 95 / 1100))
        # December is the year's own figure.
        h["2024-12"] = {"ACCT_550": 1.0, "ACCT_551": 0.0, "ACCT_025B": 900.0}
        self.assertEqual(net_charge_offs_12m(h, "2025-12"), round2(100 * 80 / 1000))

    def test_charge_offs_need_the_year_before(self):
        h = {"2026-06": {"ACCT_550": 1.0, "ACCT_551": 0.0, "ACCT_025B": 10.0}}
        self.assertIsNone(net_charge_offs_12m(h, "2026-06"))

    def test_code_matches_dictionary(self):
        self.assertEqual(check_against_dictionary(load_dictionary()), [])

    def test_net_worth_denominator(self):
        a = {"ACCT_010A": 0, "ACCT_010B": 0, "ACCT_010C": 900.0, "ACCT_LC0047": 50.0, "ACCT_NW0004": 10.0,
             "ACCT_NW0010": 1000.0, "ACCT_010": 1000.0}
        self.assertEqual(checks.net_worth_denominator(a)[0], 860.0)
        a["ACCT_010C"] = 0
        self.assertEqual(checks.net_worth_denominator(a)[0], 1000.0)
        a["ACCT_NW0010"] = None
        self.assertEqual(checks.net_worth_denominator(a), (1000.0, "010"))


class Peers(unittest.TestCase):
    def test_leaves_self_out_and_needs_five_others(self):
        group = [cu(str(i), delinquency=float(i)) for i in range(6)]
        p = peers(group[0], group, "delinquency")
        self.assertEqual(p["n_others"], 5)
        self.assertEqual(p["median"], 3.0)  # of 1..5, not 0..5
        small = group[:5]
        p = peers(small[0], small, "delinquency")
        self.assertEqual((p["n_others"], p["median"], p["p25"]), (4, None, None))

    def test_quantiles_round_halves_up(self):
        # 0.78 and 0.79: the median is 0.785 exactly, which floats would round down.
        self.assertEqual(quantile([0.78, 0.79], "0.5"), 0.79)
        self.assertEqual(quantile([1.0, 2.0, 3.0, 4.0, 5.0], "0.25"), 2.0)
        self.assertEqual(quantile([1.0, 2.0, 3.0, 4.0], "0.25"), 1.75)

    def test_unknown_peer_group_gets_no_comparison(self):
        group = [cu(str(i), peer_group=None, delinquency=float(i)) for i in range(7)]
        self.assertEqual(peers(group[0], group, "delinquency"), {"n_others": 0, "median": None, "p25": None, "p75": None})
        group = [cu(str(i), peer_group=99, delinquency=float(i)) for i in range(7)]
        self.assertIsNone(peers(group[0], group, "delinquency")["median"])

    def test_other_peer_groups_and_missing_values_left_out(self):
        group = [cu(str(i), delinquency=float(i)) for i in range(6)]
        group.append(cu("x", peer_group=4, delinquency=99.0))
        group.append(cu("y", delinquency=None))
        self.assertEqual(peers(group[0], group, "delinquency")["n_others"], 5)


class Checks(unittest.TestCase):
    def test_rate_zero_is_none_and_yes_no(self):
        from nmcu.measures import _either, _rate, _yes
        self.assertIsNone(_rate(0.0))
        self.assertIsNone(_rate(None))
        self.assertEqual(_rate(664.0), 6.64)
        self.assertEqual((_yes(1.0), _yes(0.0), _yes(None), _yes(2.0)), (True, False, None, None))
        self.assertEqual((_either(0, 1), _either(0, None), _either(None, None), _either(0, 2)), (True, False, None, None))

    def test_rate_boundaries_are_tested_before_rounding(self):
        from nmcu.measures import _rate
        self.assertEqual((_rate(100.0), _rate(3000.0)), (1.0, 30.0))
        self.assertIsNone(_rate(99.6))  # would round to 1.00%
        self.assertIsNone(_rate(3000.4))

    def test_implausible_rate_is_withheld(self):
        c = cu("1", rate_unsecured=None, rate_new_auto=None, rate_used_auto=6.5)
        c.accounts = {"ACCT_522": 99900.0, "ACCT_523": 9.0, "ACCT_524": 650.0}
        checks.withhold(c)
        self.assertIsNone(c.measures["rate_unsecured"])
        self.assertIsNone(c.measures["rate_new_auto"])
        self.assertEqual(c.measures["rate_used_auto"], 6.5)
        self.assertEqual(set(c.withheld), {"rate_unsecured", "rate_new_auto"})

    def test_impossible_share_is_withheld(self):
        c = cu("1", cre_reset_5y=532.58, delinquency=1.0)
        checks.withhold(c)
        self.assertIsNone(c.measures["cre_reset_5y"])
        self.assertIn("cre_reset_5y", c.withheld)
        self.assertEqual(c.measures["delinquency"], 1.0)

    def test_schema_error_when_an_account_goes_missing(self):
        d = load_dictionary()
        with self.assertRaises(checks.BuildError):
            checks.schema(d, "2026-06", {"ACCT_010": "FS220.TXT"})
        # Before CM0099 existed, its absence is fine.
        available = {a: "X" for a in all_accounts(d) if a not in ("ACCT_CM0099", "ACCT_RL0047", "ACCT_RL0050",
                                                                  "ACCT_LC0047", "ACCT_NW0004", "ACCT_NW0010")}
        checks.schema(d, "2019-03", available)
        # A quarter after the history's last one still needs every ongoing account.
        with self.assertRaises(checks.BuildError):
            checks.schema(d, "2026-09", {})
        checks.schema(d, "2026-09", {a: "X" for a in all_accounts(d) if a != "ACCT_712"})

    def test_net_worth_check_skips_blank_formula_accounts(self):
        a = {"ACCT_997": 100.0, "ACCT_998": 500.0, "ACCT_010": 1000.0, "ACCT_010A": 0, "ACCT_010B": 0,
             "ACCT_010C": 0, "ACCT_LC0047": None, "ACCT_NW0004": None, "ACCT_NW0010": None,
             "ACCT_025B": None, "ACCT_025B1": None, "ACCT_718A3": None, "ACCT_718A4": None, "ACCT_718A5": None,
             "ACCT_CM0099": None, "ACCT_RL0047": None, "ACCT_RL0050": None, "ACCT_691P1": None,
             "ACCT_691P2": None, "ACCT_691C1": None, "ACCT_691C2": None, "ACCT_041B": None}
        c = SimpleNamespace(cu_number="1", name="1", accounts=a, measures={}, not_reported=[])
        self.assertEqual([f["check"] for f in checks.filing("2019-03", c)], ["net worth"])  # 10% vs 5%
        c.not_reported = ["ACCT_NW0010"]
        self.assertEqual(checks.filing("2021-03", c), [])


@unittest.skipUnless((CACHE / "call-report-data-2026-06.zip").exists(), "2026-06 zip not cached")
class EmptyBuild(unittest.TestCase):
    def test_no_quarters_stops_before_writing(self):
        from nmcu import build as b
        before = sorted(p.name for p in (b.OUT / "quarters").glob("*.json"))
        with self.assertRaises(checks.BuildError):
            b.build(offline=True, through="2017-12")
        self.assertEqual(sorted(p.name for p in (b.OUT / "quarters").glob("*.json")), before)


class Real2026(unittest.TestCase):
    """2026-06 figures. The FPR rows are NCUA's own published ratios (docs/research/fpr-2026-06/).
    The rest were worked from the raw zip by a separate, plain csv read (dictionary.json)."""

    @classmethod
    def setUpClass(cls):
        d = load_dictionary()
        accounts = all_accounts(d)
        history = {}
        for q in ("2025-06", "2025-12", "2026-06"):
            quarter = read_quarter(CACHE / f"call-report-data-{q}.zip", q, accounts)
            for c in quarter.credit_unions.values():
                history.setdefault(c.cu_number, {})[q] = c.accounts
        cls.quarter = quarter
        cls.history = history

    def m(self, n, measure):
        a = self.quarter.credit_unions[n].accounts
        if measure == "net_charge_offs_12m":
            return net_charge_offs_12m(self.history[n], "2026-06")
        return SIMPLE[measure][1](a)

    def test_roster(self):
        self.assertEqual(len(self.quarter.credit_unions), 37)
        self.assertEqual(self.quarter.uninsured, [])

    def test_matches_ncua_fpr(self):
        fpr = {  # charter: net worth, delinquency, 12-month net charge-offs
            "808": (7.80, 6.91, 0.96),
            "61559": (24.76, 0.11, 0.70),
            "66143": (20.88, 0.00, 0.00),
            "9566": (18.34, 0.00, 0.92),
            "62783": (16.12, 1.08, 0.27),
        }
        for n, (nw, dq, nco) in fpr.items():
            with self.subTest(charter=n):
                self.assertEqual(self.m(n, "net_worth_ratio"), nw)
                self.assertEqual(self.m(n, "delinquency"), dq)
                self.assertEqual(self.m(n, "net_charge_offs_12m"), nco)

    def test_matches_hand_worked(self):
        hand = {  # charter: commercial share, commercial real estate reset, home reset
            "808": (17.14, 95.86, 20.04),
            "62783": (0.00, None, 0.00),
            "61559": (0.00, None, None),
            "948": (24.39, 83.27, 34.78),
            "11316": (12.78, 52.43, 25.28),
            "65513": (16.85, 91.43, 31.79),
            "68244": (5.81, 0.00, 0.81),
            "16754": (6.10, 0.00, None),
        }
        for n, (comm, cre, home) in hand.items():
            with self.subTest(charter=n):
                self.assertEqual(self.m(n, "commercial_share"), comm)
                self.assertEqual(self.m(n, "cre_reset_5y"), cre)
                self.assertEqual(self.m(n, "home_reset_5y"), home)

    def test_rates_and_services(self):
        # Worked from the raw zip by a separate plain csv read (rates stored times 100).
        hand = {  # charter: card, new car, used car, mortgage, personal; free checking, bilingual, credit builder, PAL, ATM
            "948": (12.50, 6.64, 6.83, 6.35, 13.26, True, True, False, True, True),
            "808": (18.00, 5.24, 5.24, 7.45, 10.90, True, True, True, True, True),
            "62783": (9.90, 6.27, 6.68, 5.30, 10.77, False, True, False, False, False),
            "61559": (None, 6.19, 9.21, None, 11.94, False, False, False, False, False),
            "16754": (None, 2.05, 6.69, None, 22.68, True, True, False, True, True),
        }
        ids = ("rate_credit_card", "rate_new_auto", "rate_used_auto", "rate_mortgage", "rate_unsecured",
               "free_checking", "bilingual", "credit_builder", "payday_alternative", "surcharge_free_atm")
        for n, expected in hand.items():
            with self.subTest(charter=n):
                self.assertEqual(tuple(self.m(n, i) for i in ids), expected)

    def test_sites_before_the_columns_existed(self):
        accounts = all_accounts(load_dictionary())
        old = read_quarter(CACHE / "call-report-data-2018-03.zip", "2018-03", accounts)
        nm = [s for c in old.credit_unions.values() for s in c.sites if s["state"] == "NM"]
        self.assertTrue(nm and all(s["county"] for s in nm), "a county is blank in 2018-03")
        self.assertTrue(all(s["atm"] is None and s["hours"] is None for s in nm), "a missing column reads as no")

    def test_sites(self):
        sites = self.quarter.credit_unions["948"].sites
        self.assertTrue(sites[0]["main_office"])
        self.assertEqual(sites[0]["county"], "Bernalillo")
        in_state = [s for q in self.quarter.credit_unions.values() for s in q.sites if s["state"] == "NM"]
        self.assertEqual(len(in_state), 178)
        self.assertEqual(len({s["county"] for s in in_state}), 26)

    def test_guarantees(self):
        self.assertEqual(self.m("808", "other_gov_guaranteed"), {"balance": 98396773, "guaranteed": 32343829})
        self.assertEqual(self.m("808", "sba"), {"balance": 12375585, "guaranteed": 2588489})
        self.assertEqual(self.m("808", "members"), 98817)


if __name__ == "__main__":
    unittest.main()
