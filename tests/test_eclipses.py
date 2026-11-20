# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Eclipses 2017-2027 against the real list (NASA catalogue), plus visibility and the Grahan yoga helper."""
import unittest

from jyotish import eclipses as E
from jyotish.location import resolve_location

# (kind, type, UTC date, greatest-eclipse hour UTC +-0.6 h)
REAL = [
    ("solar", "annular", "2017-02-26", 14.5), ("solar", "total", "2017-08-21", 18.5), ("lunar", "partial", "2017-08-07", 18.3),
    ("lunar", "total", "2018-01-31", 13.5), ("solar", "total", "2019-07-02", 19.4), ("lunar", "total", "2019-01-21", 5.2),
    ("solar", "annular", "2020-06-21", 6.6), ("solar", "total", "2020-12-14", 16.2), ("lunar", "total", "2021-05-26", 11.2),
    ("solar", "total", "2021-12-04", 7.6), ("lunar", "total", "2022-11-08", 11.0), ("solar", "annular", "2023-10-14", 18.0),
    ("lunar", "partial", "2023-10-28", 20.2), ("lunar", "penumbral", "2024-03-25", 7.2), ("solar", "total", "2024-04-08", 18.3),
    ("lunar", "partial", "2024-09-18", 2.7), ("solar", "annular", "2024-10-02", 18.8), ("lunar", "total", "2025-03-14", 6.9),
    ("solar", "partial", "2025-03-29", 10.8), ("lunar", "total", "2025-09-07", 18.2), ("solar", "partial", "2025-09-21", 19.7),
    ("solar", "annular", "2026-02-17", 12.2), ("lunar", "total", "2026-03-03", 11.5), ("solar", "total", "2026-08-12", 17.8),
    ("lunar", "partial", "2026-08-28", 4.2),
]
COUNT = {2017: 4, 2018: 5, 2019: 5, 2020: 6, 2021: 4, 2022: 4, 2023: 4, 2024: 4, 2025: 4, 2026: 4, 2027: 5}


class Eclipses(unittest.TestCase):
    def test_known_eclipses(self):
        by_year = {}
        for kind, typ, date, hour in REAL:
            y = int(date[:4])
            by_year.setdefault(y, E.eclipses_in_year(y))
            hit = [e for e in by_year[y] if e["date_utc"] == date and e["kind"] == kind]
            self.assertEqual(len(hit), 1, (kind, date))
            self.assertEqual(hit[0]["type"], typ, (kind, date))
            h, m = hit[0]["utc"][11:].split(":")
            self.assertLess(abs(int(h) + int(m) / 60.0 - hour), 0.6, (kind, date, hit[0]["utc"]))

    def test_hybrid_2023(self):
        e = [x for x in E.eclipses_in_year(2023) if x["date_utc"] == "2023-04-20"]
        self.assertEqual(len(e), 1)
        self.assertIn(e[0]["type"], ("hybrid", "total", "annular"))

    def test_counts_per_year(self):
        for y in range(2017, 2028):
            n = len(E.eclipses_in_year(y))
            self.assertGreaterEqual(n, 4, y)
            self.assertLessEqual(n, 7, y)
        self.assertEqual(len(E.eclipses_in_year(2026)), 4)

    def test_solar_only_at_new_moon_lunar_at_full_moon(self):
        for e in E.eclipses_in_year(2025):
            self.assertIn(e["kind"], ("solar", "lunar"))

    def test_next_eclipses(self):
        nxt = E.next_eclipses("2026-11-20", count=3)
        self.assertEqual(len(nxt), 3)
        self.assertEqual(nxt[0]["date_utc"], "2027-02-06")   # annular solar eclipse
        self.assertTrue(nxt[0]["jd_ut"] < nxt[1]["jd_ut"] < nxt[2]["jd_ut"])

    def test_visibility_from_kolkata(self):
        loc = resolve_location("kolkata")
        ev = {e["date_utc"]: e for e in E.eclipses_in_year(2025, loc=loc) + E.eclipses_in_year(2026, loc=loc)}
        self.assertTrue(ev["2025-09-07"]["visibility"]["visible"])        # total lunar eclipse seen all over India
        self.assertFalse(ev["2025-03-14"]["visibility"]["visible"])       # Moon below the horizon
        self.assertFalse(ev["2026-08-12"]["visibility"]["visible"])       # total solar eclipse of Aug 2026: night in India
        self.assertFalse(ev["2026-02-17"]["visibility"]["visible"])

    def test_ancient_and_far_future_do_not_crash(self):
        self.assertTrue(E.eclipses_in_year(1))
        self.assertTrue(E.eclipses_in_year(9999))
        self.assertTrue(E.eclipses_in_year(1192))

    def test_grahan_dosha(self):
        d = E.grahan_dosha(40.0, 100.0, 38.0, 218.0)
        self.assertTrue(d["present"])
        self.assertFalse(E.grahan_dosha(40.0, 100.0, 200.0, 20.0)["present"])


if __name__ == "__main__":
    unittest.main()
