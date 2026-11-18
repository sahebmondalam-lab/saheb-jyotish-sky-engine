# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Long-range tests: years 1-9999, Julian/Gregorian calendars, old local time, historical sky events, age."""
import unittest
from datetime import date, datetime, timezone

from jyotish import api, astro as A
from jyotish.calendars import gregorian_from_jdn, jdn_julian, resolve_date


def jd(y, m, d, h=0.0):
    return A.julian_day(datetime(y, m, d, tzinfo=timezone.utc)) + h / 24.0


def lon(g, j):
    T = A.centuries(A.jd_to_tt(j))
    return {"Sun": A.sun_longitude, "Moon": A.moon_longitude}.get(g, lambda t: A.planet_longitude(g, t))(T)


def conjunction_with_sun(g, j0, span=3.0, step_min=2.0):
    best = None
    for k in range(int(span * 2 * 1440 / step_min) + 1):
        j = j0 - span + k * step_min / 1440.0
        d = abs(A.norm180(lon(g, j) - lon("Sun", j)))
        if best is None or d < best[0]:
            best = (d, j)
    return best[1]


def meeus_equinox_jde(year):
    if year < 1000:
        Y = year / 1000.0
        return 1721139.29189 + 365242.13740 * Y + 0.06134 * Y**2 + 0.00111 * Y**3 - 0.00071 * Y**4
    Y = (year - 2000) / 1000.0
    return 2451623.80984 + 365242.37404 * Y + 0.05169 * Y**2 - 0.00411 * Y**3 - 0.00057 * Y**4


def sun_equinox_ut(guess):
    lo, hi = guess - 4, guess + 4
    for _ in range(60):
        mid = (lo + hi) / 2
        if A.norm180(A.sun_longitude(A.centuries(A.jd_to_tt(mid)))) < 0:
            lo = mid
        else:
            hi = mid
    return hi


class CalendarTests(unittest.TestCase):
    def test_julian_to_gregorian(self):
        self.assertEqual(gregorian_from_jdn(jdn_julian(1582, 10, 4)), (1582, 10, 14))
        self.assertEqual(gregorian_from_jdn(jdn_julian(1582, 10, 5)), (1582, 10, 15))      # the day after is the reform day
        self.assertEqual(gregorian_from_jdn(jdn_julian(1133, 8, 2)), (1133, 8, 9))
        self.assertEqual(gregorian_from_jdn(jdn_julian(1752, 9, 2)), (1752, 9, 13))        # England, the day before 14 Sept 1752
        self.assertEqual(gregorian_from_jdn(jdn_julian(1100, 2, 29)), (1100, 3, 7))        # Julian leap year, Gregorian is not

    def test_auto_and_explicit(self):
        self.assertEqual(resolve_date("1162-05-31"), date(1162, 6, 7))
        self.assertEqual(resolve_date("1582-10-14"), date(1582, 10, 24))                  # Julian reading before the reform
        self.assertEqual(resolve_date("1582-10-15"), date(1582, 10, 15))
        self.assertEqual(resolve_date("1900-01-01"), date(1900, 1, 1))
        self.assertEqual(resolve_date("1900-01-01", "julian"), date(1900, 1, 13))
        self.assertEqual(resolve_date("1162-05-31", "gregorian"), date(1162, 5, 31))
        for bad, cal in (("1100-02-30", "auto"), ("1700-02-29", "gregorian"), ("1999-13-01", "auto")):
            with self.assertRaises(ValueError):
                resolve_date(bad, cal)

    def test_before_year_one_is_a_clear_error(self):
        for bad in ("0000-05-01", "-0044-03-15", "0001-01-01"):
            with self.assertRaises(ValueError):
                api.sky(bad, "12:00", place="kolkata")


class HistoricalSkyTests(unittest.TestCase):
    def test_sun_matches_meeus_equinox_over_millennia(self):
        for year, limit_min in ((325, 12), (1000, 12), (1600, 5), (2000, 6), (2500, 20), (3000, 30), (4000, 50)):
            jde = meeus_equinox_jde(year)
            expected_ut = jde - A.delta_t(year + 0.22) / 86400.0
            got = sun_equinox_ut(expected_ut)
            self.assertLess(abs(got - expected_ut) * 1440, limit_min, year)

    def test_historic_transits_land_on_the_right_day(self):
        cases = (("Mercury", (1631, 11, 7)), ("Venus", (1639, 12, 4)), ("Venus", (1761, 6, 6)), ("Venus", (1769, 6, 3)))
        for planet, (y, m, d) in cases:
            j = conjunction_with_sun(planet, jd(y, m, d, 12))
            got = A.datetime_from_jd(j)
            self.assertEqual((got.year, got.month, got.day), (y, m, d), (planet, y))

    def test_venus_transit_1769_within_an_hour(self):
        got = A.datetime_from_jd(conjunction_with_sun("Venus", jd(1769, 6, 3, 22)))
        hours = got.hour + got.minute / 60.0
        self.assertLess(abs(hours - 22.4), 1.0)                  # greatest transit ~22:25 UT

    def test_new_moon_on_the_day_of_henry_I_eclipse(self):
        # total solar eclipse of 2 August 1133 (Julian) = 9 August 1133 proleptic Gregorian
        j = conjunction_with_sun("Moon", jd(1133, 8, 9, 12), span=2.0)
        got = A.datetime_from_jd(j)
        self.assertEqual((got.month, got.day), (8, 9))
        self.assertLess(abs(A.norm180(lon("Moon", j) - lon("Sun", j))), 0.05)

    def test_long_term_table_agrees_with_table_1_where_both_apply(self):
        import jyotish.astro as m
        saved = (m.TABLE1_T0, m.TABLE1_T1)
        worst = {}
        try:
            for g in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
                mx = 0.0
                for yr in range(1810, 2050, 10):
                    j = jd(yr, 6, 1)
                    T = A.centuries(A.jd_to_tt(j))
                    m.TABLE1_T0, m.TABLE1_T1 = saved
                    a = A.planet_longitude(g, T)
                    m.TABLE1_T0, m.TABLE1_T1 = 9e9, -9e9           # force Table 2a
                    b = A.planet_longitude(g, T)
                    mx = max(mx, abs(A.norm180(a - b)))
                worst[g] = mx
        finally:
            m.TABLE1_T0, m.TABLE1_T1 = saved
        self.assertLess(max(worst["Mercury"], worst["Venus"]), 0.03)
        self.assertLess(worst["Mars"], 0.05)
        self.assertLess(worst["Jupiter"], 0.15)
        self.assertLess(worst["Saturn"], 0.4)

    def test_delta_t_is_continuous(self):
        for y in (500, 1600, 1700, 1800, 1860, 1900, 2005, 2050):
            self.assertLess(abs(A.delta_t(y - 1e-6) - A.delta_t(y)), 0.6, y)


class WholeRangeTests(unittest.TestCase):
    def test_every_era_gives_a_chart(self):
        for d in ("0001-06-01", "0100-03-01", "0622-07-16", "1162-05-31", "1564-02-15", "1600-01-01", "2026-11-18", "3500-01-01", "4000-01-01", "9998-06-01", "9999-12-31"):
            k = api.kundli(d, "12:00", place="kolkata", years=0)
            self.assertEqual(len(k["planets"]), 9, d)
            self.assertEqual(len(k["divisional_charts"]), 16, d)

    def test_notes_by_era(self):
        def notes(d):
            return " ".join(api.kundli(d, "12:00", place="kolkata", years=0).get("warnings", []))
        self.assertNotIn("Year", notes("1992-01-27"))
        self.assertIn("long-term", notes("1700-06-01"))
        self.assertIn("before 1600", notes("1162-05-31"))
        self.assertIn("Julian", notes("1162-05-31"))
        self.assertIn("beyond 3000", notes("3500-01-01"))
        self.assertIn("long-term", notes("2500-01-01"))

    def test_genghis_khan_style_query(self):
        # birth year is disputed (1155/1162/1167): the engine takes whatever date it is given
        k = api.kundli("1162-05-31", None, lat=48.9, lon=110.9, tz="Asia/Ulaanbaatar", years=0)
        self.assertFalse(k["birth_time_known"])
        self.assertIn("Julian", " ".join(k["warnings"]))
        self.assertTrue(k["input"]["local_time"].startswith("1162-06-07T12:00:00+07:23"))      # local mean time of 110.9 E, Gregorian-equivalent date
        self.assertEqual(len(k["ashtakavarga"]["sarva"]), 12)

    def test_modern_dates_still_use_the_zone_database(self):
        k = api.kundli("1992-01-27", "10:30", place="kolkata", years=0)
        self.assertTrue(k["input"]["local_time"].endswith("+05:30"))
        p = api.kundli("1995-07-01", "12:00", place="paris", years=0)
        self.assertTrue(p["input"]["local_time"].endswith("+02:00"))                              # daylight saving applied
        old = api.kundli("1700-07-01", "12:00", place="paris", years=0)
        self.assertTrue(old["input"]["local_time"].endswith("+00:09:25"))                            # Paris local mean time (2.3522 E = 9m25s)

    def test_calendar_choice_changes_the_chart(self):
        a = api.sky("1700-03-01", "12:00", place="london", calendar="gregorian")
        b = api.sky("1700-03-01", "12:00", place="london", calendar="julian")
        self.assertNotEqual(a["planets"]["Moon"]["sidereal_longitude"], b["planets"]["Moon"]["sidereal_longitude"])
        self.assertTrue(any("Julian" in w for w in b["warnings"]))


class AgeTests(unittest.TestCase):
    def test_modern_age(self):
        a = api.age("27 Jan 1992", "17 Nov 2026")
        self.assertEqual((a["years"], a["months"], a["days"]), (34, 9, 21))
        self.assertEqual(a["birth_weekday"]["en"].split()[0], "Monday")
        self.assertEqual(a["total_days"], (date(2026, 11, 17) - date(1992, 1, 27)).days)

    def test_historic_age_in_julian_dates(self):
        a = api.age("1162-05-31", "1227-08-18")
        self.assertEqual((a["years"], a["months"], a["days"]), (65, 2, 18))
        self.assertEqual(a["birth_gregorian"], "1162-06-07")

    def test_age_rejects_reversed_dates(self):
        with self.assertRaises(ValueError):
            api.age("2000-01-01", "1999-01-01")

    def test_age_report_and_credit(self):
        t = api.report("age", "en", date="27 Jan 1992", on="17 Nov 2026")
        self.assertIn("34 years, 9 months, 21 days", t)
        self.assertEqual(api.age("27 Jan 1992", "17 Nov 2026")["credit"]["author"], "Saheb Mondal")


if __name__ == "__main__":
    unittest.main()
