"""Tests for scripts/check_dictionary.py's --sync-quarters (a new quarter moves quarters forward, nothing else)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("check_dictionary", Path(__file__).resolve().parent.parent / "scripts" / "check_dictionary.py")
cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cd)


def entry(frm="2025-12", to="2026-03", count=2):
    return {"account": "ACCT_1", "quarters": {"from": frm, "to": to, "count": count}}


class Sync(unittest.TestCase):
    def test_new_quarter_extends(self):
        a = entry()
        n = cd.extend(a, {"ACCT_1": {"tables": {"fs220": ["2025-12", "2026-03", "2026-06"]}}})
        self.assertEqual((n, a["quarters"]), (1, {"from": "2025-12", "to": "2026-06", "count": 3}))

    def test_changed_start_is_left_to_fail(self):
        a = entry()
        self.assertEqual(cd.extend(a, {"ACCT_1": {"tables": {"fs220": ["2025-09", "2025-12", "2026-03", "2026-06"]}}}), 0)
        self.assertEqual(a["quarters"]["to"], "2026-03")

    def test_dropped_middle_quarter_is_left_to_fail(self):
        a = entry(frm="2025-09", to="2026-03", count=3)
        self.assertEqual(cd.extend(a, {"ACCT_1": {"tables": {"fs220": ["2025-09", "2026-03", "2026-06"]}}}), 0)

    def test_no_new_quarter_is_unchanged(self):
        a = entry()
        self.assertEqual(cd.extend(a, {"ACCT_1": {"tables": {"fs220": ["2025-12", "2026-03"]}}}), 0)


if __name__ == "__main__":
    unittest.main()
