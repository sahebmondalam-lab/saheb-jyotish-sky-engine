# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Tests anchored to publicly known events (Sankranti moments, new/full moons, published charts)."""
import json
import re
import unittest
from datetime import datetime, timedelta, timezone

from jyotish import astro as A
from jyotish import dasha, transits
from jyotish.chart import build_chart
from jyotish.cli import main as cli_main
from jyotish.data import DASHA_YEARS, NAKSHATRA, RASHI_SHORT
from jyotish.location import make_local_datetime, resolve_location
from jyotish.report import render_kundli, render_panchang

UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))
BENGALI = re.compile("[ঀ-৿]")


def jd(dt):
    return A.julian_day(dt)


class TimeTests(unittest.TestCase):
    def test_j2000(self):
        self.assertAlmostEqual(jd(datetime(2000, 1, 1, 12, tzinfo=UTC)), 2451545.0, places=6)

    def test_roundtrip(self):
        d = datetime(2026, 11, 16, 4, 30, 15, tzinfo=UTC)
        back = A.datetime_from_jd(jd(d))
        self.assertLess(abs((back - d).total_seconds()), 1.0)

    def test_lahiri_j2000(self):
        # Swiss-Ephemeris style mean Lahiri at J2000 is 23 deg 51' 25.5" = 23.8571
        self.assertAlmostEqual(A.ayanamsa_lahiri(A.J2000), 23.8571, delta=0.002)


class SkyTests(unittest.TestCase):
    def sid(self, g, dt):
        return A.sidereal_longitude(g, jd(dt))

    def test_makar_sankranti_2025(self):
        # Sun enters sidereal Makara (270 deg) on 2025-01-14 about 09:03 IST
        self.assertLess(abs(A.norm180(self.sid("Sun", datetime(2025, 1, 14, 9, 3, tzinfo=IST)) - 270)), 0.05)

    def test_makar_sankranti_2026(self):
        self.assertLess(abs(A.norm180(self.sid("Sun", datetime(2026, 1, 14, 15, 13, tzinfo=IST)) - 270)), 0.05)

    def test_new_and_full_moon(self):
        for dt, target in ((datetime(2025, 10, 21, 12, 25, tzinfo=UTC), 0.0),
                           (datetime(2025, 9, 21, 19, 54, tzinfo=UTC), 0.0),
                           (datetime(2025, 11, 5, 13, 19, tzinfo=UTC), 180.0),
                           (datetime(2025, 9, 7, 18, 9, tzinfo=UTC), 180.0)):
            j = jd(dt)
            el = A.norm360(A.tropical_longitude("Moon", j) - A.tropical_longitude("Sun", j))
            self.assertLess(abs(A.norm180(el - target)), 0.1, dt)

    def test_slow_planet_ingresses(self):
        # Saturn enters Meena 2025-03-29, Jupiter enters Karka 2025-10-18, Rahu enters Kumbha 2025-05-18
        self.assertLess(abs(A.norm180(self.sid("Saturn", datetime(2025, 3, 29, 12, tzinfo=IST)) - 330)), 0.15)
        self.assertLess(abs(A.norm180(self.sid("Jupiter", datetime(2025, 10, 18, 12, tzinfo=IST)) - 90)), 0.15)
        self.assertLess(abs(A.norm180(self.sid("Rahu", datetime(2025, 5, 18, 16, tzinfo=IST)) - 330)), 0.05)

    def test_future_ingress_dates(self):
        # Published transit dates: Jupiter -> Simha 2026-10-31, Rahu -> Makara 2026-12-05, Saturn -> Mesha 2027-06-02
        start = jd(datetime(2026, 11, 16, tzinfo=UTC))
        sat = transits.sign_timeline("Saturn", start, start + 400)
        jup = transits.sign_timeline("Jupiter", jd(datetime(2026, 10, 1, tzinfo=UTC)), start)
        rah = transits.sign_timeline("Rahu", start, start + 60)
        sat_first_mesha = next(s for s in sat if s["sign"] == 0)
        self.assertLess(abs(sat_first_mesha["start"] - jd(datetime(2027, 6, 2, tzinfo=UTC))), 3.0)
        jup_simha = next(s for s in jup if s["sign"] == 4)
        self.assertLess(abs(jup_simha["start"] - jd(datetime(2026, 10, 31, tzinfo=UTC))), 3.0)
        rah_makara = next(s for s in rah if s["sign"] == 9)
        self.assertLess(abs(rah_makara["start"] - jd(datetime(2026, 12, 5, tzinfo=UTC))), 3.0)

    def test_sunrise_london_solstice(self):
        bst = timezone(timedelta(hours=1))
        r, s = A.sunrise_sunset(jd(datetime(2026, 6, 21, tzinfo=bst)), 51.5074, -0.1278)
        rise = A.datetime_from_jd(r).astimezone(bst)
        sset = A.datetime_from_jd(s).astimezone(bst)
        self.assertLess(abs((rise - rise.replace(hour=4, minute=43, second=0)).total_seconds()), 150)
        self.assertLess(abs((sset - sset.replace(hour=21, minute=21, second=0)).total_seconds()), 150)

    def test_polar_night_returns_none(self):
        r, s = A.sunrise_sunset(jd(datetime(2026, 12, 21, tzinfo=UTC)), 78.2, 15.6)  # Svalbard
        self.assertIsNone(r)


class ChartTests(unittest.TestCase):
    def setUp(self):
        self.loc = resolve_location("delhi")
        self.chart = build_chart(make_local_datetime("1947-08-15", "00:00", self.loc), self.loc)

    def test_india_1947_published_chart(self):
        c = self.chart
        self.assertEqual(RASHI_SHORT[c["lagna"]["sign"]], "Vrishabha")
        self.assertEqual(RASHI_SHORT[c["planets"]["Moon"]["sign"]], "Karka")
        self.assertEqual(NAKSHATRA[c["planets"]["Moon"]["nakshatra"]][0], "Pushya")
        self.assertEqual(RASHI_SHORT[c["planets"]["Sun"]["sign"]], "Karka")
        self.assertEqual(RASHI_SHORT[c["planets"]["Saturn"]["sign"]], "Karka")
        self.assertEqual(RASHI_SHORT[c["planets"]["Rahu"]["sign"]], "Vrishabha")
        self.assertEqual(RASHI_SHORT[c["planets"]["Jupiter"]["sign"]], "Tula")

    def test_ketu_opposite_rahu(self):
        p = self.chart["planets"]
        self.assertAlmostEqual(A.norm360(p["Ketu"]["sidereal"] - p["Rahu"]["sidereal"]), 180.0, places=6)

    def test_every_planet_in_exactly_one_house(self):
        placed = [g for h in self.chart["houses"].values() for g in h["planets"]]
        self.assertEqual(sorted(placed), sorted(A.GRAHAS))

    def test_json_serialisable(self):
        json.dumps(self.chart, default=str)


class DashaTests(unittest.TestCase):
    def test_cycle_is_120_years(self):
        self.assertEqual(sum(DASHA_YEARS.values()), 120)

    def test_antardashas_fill_mahadasha(self):
        periods = dasha.vimshottari(123.45, 2450000.0)
        for p in periods:
            self.assertAlmostEqual(p["antar"][-1]["end"], p["end"], places=6)
            self.assertAlmostEqual(p["antar"][0]["start"], p["start"], places=6)

    def test_balance_at_birth(self):
        # Moon exactly at the start of Ashwini: full Ketu dasha (7 years) remains
        self.assertAlmostEqual(dasha.balance_at_birth(0.0)["years_left"], 7.0, places=6)
        # Moon at the very end of Ashwini: almost nothing remains
        self.assertLess(dasha.balance_at_birth(13.33)["years_left"], 0.01)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.loc = resolve_location("kolkata")
        self.chart = build_chart(make_local_datetime("1995-08-15", "14:30", self.loc), self.loc)
        self.now = jd(datetime(2026, 11, 16, tzinfo=UTC))
        self.fc = transits.forecast(self.chart["moon_sign"], self.now, 2)

    def test_english_has_no_bengali(self):
        self.assertIsNone(BENGALI.search(render_kundli(self.chart, self.fc, "en", self.now, self.loc)))

    def test_bengali_is_bengali(self):
        text = render_kundli(self.chart, self.fc, "bn", self.now, self.loc)
        self.assertIsNotNone(BENGALI.search(text))
        self.assertIn("CC BY-NC-SA 4.0", text)          # licence name stays ASCII
        self.assertIn("সাহেব মন্ডল", text)               # credit stays

    def test_both_has_both(self):
        text = render_kundli(self.chart, self.fc, "both", self.now, self.loc)
        self.assertIsNotNone(BENGALI.search(text))
        self.assertIn("Saheb Mondal", text)

    def test_credit_in_every_report(self):
        for lang in ("en", "bn", "both"):
            self.assertTrue(("Saheb Mondal" in render_kundli(self.chart, self.fc, lang, self.now, self.loc))
                            or ("সাহেব মন্ডল" in render_kundli(self.chart, self.fc, lang, self.now, self.loc)))

    def test_panchang_renders(self):
        from datetime import date
        text = render_panchang(date(2026, 11, 16), self.loc, "both")
        self.assertIn("Rahu Kaal", text)
        self.assertIn("রাহুকাল", text)


class CliTests(unittest.TestCase):
    def test_unknown_place_fails_cleanly(self):
        self.assertEqual(cli_main(["kundli", "--date", "2000-01-01", "--time", "10:00", "--place", "atlantis"]), 1)

    def test_bad_date_fails_cleanly(self):
        self.assertEqual(cli_main(["kundli", "--date", "2000-13-01", "--time", "10:00", "--place", "kolkata"]), 1)


if __name__ == "__main__":
    unittest.main()
