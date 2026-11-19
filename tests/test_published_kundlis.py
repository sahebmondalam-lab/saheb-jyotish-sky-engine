# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Cross-check against published Vedic (Lahiri) charts of well-known people.

Reference values were read from panchangbodh.com chart pages on 2026-11-18. Those pages are themselves software
output, so this proves agreement with an independent program, not with a hand-made manuscript chart. Birth times
of famous people are often disputed; the times below are the ones the reference page used.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jyotish import api

# name: (date, time, place kwargs, lagna sign index, {planet: (sign index, degree in sign)})
CASES = {
    "Gandhi (Porbandar, 7:45 LMT)": ("1869-10-02", "07:45", dict(lat=21.6411, lon=69.6006, tz="Asia/Kolkata"), 6,
        {"Sun": (5, 16.92), "Moon": (3, 28.27), "Mars": (6, 26.38), "Mercury": (6, 11.75), "Jupiter": (0, 28.14),
         "Venus": (6, 24.43), "Saturn": (7, 20.33), "Rahu": (3, 12.15)}),
    "Modi (Vadnagar, 11:00 IST)": ("1950-09-17", "11:00", dict(lat=23.79, lon=72.64, tz="Asia/Kolkata"), 7,
        {"Sun": (5, 0.59), "Moon": (7, 8.81), "Mars": (7, 0.93), "Mercury": (5, 0.78), "Jupiter": (10, 6.59),
         "Venus": (4, 15.69), "Saturn": (4, 29.65), "Rahu": (11, 5.22)}),
    "Tagore (Calcutta, 2:38 LMT)": ("1861-05-07", "02:38", dict(lat=22.5850, lon=88.3592, tz="Asia/Kolkata"), 11,
        {"Sun": (0, 24.33), "Moon": (11, 20.44), "Mars": (2, 0.14), "Mercury": (0, 7.82), "Jupiter": (3, 25.95),
         "Venus": (0, 23.05), "Saturn": (4, 10.74), "Rahu": (8, 24.85)}),
}


class PublishedKundliTests(unittest.TestCase):
    def test_all_planets_within_a_tenth_of_a_degree_and_lagna_sign(self):
        for name, (d, t, pl, lag, ref) in CASES.items():
            k = api.kundli(d, t, years=0, **pl)
            self.assertEqual(k["lagna"]["sign"]["index"], lag, name)
            for g, (sign, deg) in ref.items():
                p = k["planets"][g]
                got = p["sign"]["index"] * 30 + p["degree_in_sign"]
                self.assertLess(abs(got - (sign * 30 + deg)), 0.1, f"{name} {g}")


class HistoricalHinduDateTests(unittest.TestCase):
    """Well-known traditional dates of famous Bengalis (from general knowledge, not fetched)."""

    def test_tagore_25_boishakh_1268(self):
        w = api.hindu_calendar("1861-05-07", place="kolkata")["solar_calendars"]["bengali_west_bengal"]
        self.assertEqual((w["day"], w["month"]["en"], w["year"]), (25, "Boishakh", 1268))

    def test_vivekananda_poush_krishna_saptami_29_poush_1269(self):
        r = api.hindu_calendar("1863-01-12", place="kolkata")
        self.assertEqual(r["lunisolar"]["amanta_month"]["en"], "Pausha")
        self.assertEqual((r["lunisolar"]["paksha"]["index"], r["lunisolar"]["tithi_in_paksha"]), (1, 7))
        w = r["solar_calendars"]["bengali_west_bengal"]
        self.assertEqual((w["day"], w["month"]["en"], w["year"]), (29, "Poush", 1269))

    def test_gandhi_gujarati_vikram_1925(self):
        r = api.hindu_calendar("1869-10-02", place="delhi")
        self.assertEqual(r["lunisolar"]["amanta_month"]["en"], "Bhadrapada")
        self.assertEqual(r["eras"]["vikram_samvat_kartikadi_gujarat"], 1925)


if __name__ == "__main__":
    unittest.main()
