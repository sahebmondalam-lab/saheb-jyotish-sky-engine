# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
import json
import os
import sys
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jyotish import api, hindu_calendar as H
from jyotish.location import resolve_location
from jyotish.mcp_server import call_tool
from tests.data import drik_2026_reference as REF

DELHI = resolve_location("delhi")
KOL = resolve_location("kolkata")


class LunarMonthTests(unittest.TestCase):
    def test_adhika_jyeshtha_2026(self):
        # published: Adhika Jyeshtha 17 May - 15 Jun 2026
        ms = [m for m in H.lunar_months_of_year(2026) if m["adhika"]]
        self.assertEqual(len(ms), 1)
        self.assertEqual(ms[0]["amanta"], 2)
        c = H.day_calendar(date(2026, 5, 20), DELHI)
        self.assertTrue(c["adhika"])
        self.assertFalse(H.day_calendar(date(2026, 6, 20), DELHI)["adhika"])

    def test_eras_2026(self):
        c = H.day_calendar(date(2026, 11, 18), KOL)
        self.assertEqual((c["shaka"], c["vikram_chaitradi"], c["kali"]), (1948, 2083, 5127))
        self.assertEqual(H.SAMVATSARA[c["samvatsara_index"]][0], "Parabhava")        # Ugadi 2026 = Parabhava
        c = H.day_calendar(date(2026, 3, 10), KOL)                                     # before Ugadi
        self.assertEqual((c["shaka"], c["vikram_chaitradi"]), (1947, 2082))
        self.assertEqual(H.SAMVATSARA[c["samvatsara_index"]][0], "Vishvavasu")
        c = H.day_calendar(date(2026, 10, 1), KOL)
        self.assertEqual((c["vikram_chaitradi"], c["vikram_kartikadi"]), (2083, 2082))

    def test_purnimanta_differs_in_krishna_paksha(self):
        c = H.day_calendar(date(1992, 1, 27), KOL)
        self.assertEqual(H.LUNAR_MONTH[c["amanta_month"]][0], "Pausha")
        self.assertEqual(H.LUNAR_MONTH[c["purnimanta_month"]][0], "Magha")


class Drik2026Tests(unittest.TestCase):
    """The rules were tuned on this published 2026 list (drikpanchang.com, New Delhi); this guards against regressions."""

    @classmethod
    def setUpClass(cls):
        cls.f = H.festivals_for_year(2026, DELHI)

    def _dates(self, key):
        return [str(r["date"]) for r in self.f if r["key"] == key]

    def test_all_sankrantis(self):
        self.assertEqual(self._dates("sankranti"), REF.SANKRANTI)

    def test_purnimas(self):
        self.assertEqual(self._dates("purnima"), REF.PURNIMA)

    def test_ekadashis(self):
        self.assertEqual(self._dates("ekadashi"), REF.EKADASHI)

    def test_festivals(self):
        miss = [k for k, v in REF.REF.items() if not any(d in v for d in self._dates(k))]
        self.assertEqual(miss, [])


class SolarCalendarTests(unittest.TestCase):
    def test_bangladesh_month_starts_match_published_table(self):
        want = ["2026-04-14", "2026-05-15", "2026-06-15", "2026-07-16", "2026-08-16", "2026-09-16", "2026-10-16",
                "2026-11-15", "2026-12-15", "2027-01-14", "2027-02-13", "2027-03-15"]
        got, d = [], date(2026, 4, 14)
        while d <= date(2027, 4, 13):
            if H.bangladesh_bengali_date(d)["day"] == 1:
                got.append(str(d))
            d += timedelta(days=1)
        self.assertEqual(got, want)

    def test_west_bengal_new_year_and_year_number(self):
        self.assertEqual(H.solar_date(date(2026, 4, 15), KOL, "bengali")["day"], 1)
        self.assertEqual(H.solar_date(date(2026, 4, 14), KOL, "bengali")["month_index"], 11)   # still Choitro
        r = api.hindu_calendar("2026-11-18", place="kolkata")
        self.assertEqual(r["solar_calendars"]["bengali_west_bengal"]["year"], 1433)
        self.assertEqual(r["solar_calendars"]["bengali_west_bengal"]["month"]["en"], "Ogrohayon")

    def test_malayalam_vrischikam_and_kollam_year(self):
        # drikpanchang: 18 Nov 2026 = day 2 of Vrischikam, year 1202
        r = api.hindu_calendar("2026-11-18", place="kochi" if "kochi" in api.places().get("places", {}) else "chennai")
        m = r["solar_calendars"]["malayalam_kollam"]
        self.assertEqual((m["month"]["en"], m["day"], m["year"]), ("Vrischikam", 2, 1202))

    def test_tamil_new_year_and_pongal(self):
        chennai = resolve_location("chennai")
        self.assertEqual(H.solar_date(date(2026, 4, 14), chennai, "tamil")["day"], 1)
        self.assertEqual(H.solar_date(date(2026, 1, 14), chennai, "tamil")["day"], 1)

    def test_national_saka(self):
        self.assertEqual(H.national_saka_date(date(2026, 3, 22)), {"year": 1948, "month_index": 0, "day": 1})
        self.assertEqual(H.national_saka_date(date(2028, 3, 21)), {"year": 1950, "month_index": 0, "day": 1})
        self.assertEqual(H.national_saka_date(date(2026, 11, 18))["day"], 27)


class InterfaceTests(unittest.TestCase):
    def test_api_json_and_text(self):
        r = api.hindu_calendar("2026-11-08", place="delhi")
        names = [f["name"]["en"] for f in r["festivals_on_this_day"]]
        self.assertTrue(any("Diwali" in n for n in names))
        t = api.report("calendar", "all", date="2026-11-08", place="delhi")
        self.assertIn("Diwali", t)
        self.assertIn("दीवाली", t)
        self.assertIn("দীপাবলি", t)

    def test_panchang_and_kundli_carry_hindu_calendar(self):
        self.assertIn("hindu_calendar", api.panchang("2026-11-18", place="kolkata"))
        k = api.kundli("1992-01-27", "10:30", place="kolkata")
        self.assertEqual(k["hindu_calendar"]["eras"]["shaka"], 1913)

    def test_mcp_tools(self):
        out = json.loads(call_tool("jyotish_festivals", {"year": 2026, "place": "delhi"}))
        self.assertTrue(any(f["date"] == "2026-11-08" for f in out["festivals"]))
        out = json.loads(call_tool("jyotish_hindu_calendar", {"date": "2026-05-20", "place": "delhi"}))
        self.assertTrue(out["lunisolar"]["amanta_month"]["adhika"])

    def test_edges_do_not_crash(self):
        for d in ("0001-03-01", "9999-12-31"):
            r = api.hindu_calendar(d, place="delhi")
            self.assertIn("kind", r)
        api.report("calendar", "en", date="9999-12-31", place="delhi")


if __name__ == "__main__":
    unittest.main()
