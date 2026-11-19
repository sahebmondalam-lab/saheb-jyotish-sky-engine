# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Tests for forgiving input: dates, times, places, unknown birth time, out-of-range years, name syllables."""
import os
import unittest
from datetime import date
from unittest import mock

from jyotish import api, location
from jyotish.parse import is_unknown_time, parse_date, parse_time, range_note
from jyotish.report_deep import namakshar


class DateTimeParsing(unittest.TestCase):
    def test_many_date_spellings_same_day(self):
        want = date(1992, 1, 27)
        for t in ("1992-01-27", "27/01/1992", "27-01-1992", "27.01.1992", "27 Jan 1992", "January 27th, 1992", "Jan 27, 1992",
                  "১৯৯২-০১-২৭", "২৭ জানুয়ারি ১৯৯২", "27 जनवरी 1992", "२७/०१/१९९२"):
            self.assertEqual(parse_date(t), want, t)

    def test_ambiguous_and_impossible_dates(self):
        notes = []
        self.assertEqual(parse_date("03/04/2001", notes), date(2001, 4, 3))      # day first
        self.assertTrue(notes)
        notes = []
        self.assertEqual(parse_date("04/25/2001", notes), date(2001, 4, 25))     # 25 cannot be a month
        for bad in ("31/02/2001", "hello", ""):
            with self.assertRaises(ValueError):
                parse_date(bad)

    def test_time_spellings(self):
        cases = {"14:30": (14, 30, 0), "2:30 PM": (14, 30, 0), "12 AM": (0, 0, 0), "12:15 am": (0, 15, 0), "noon": (12, 0, 0),
                 "রাত ১০:৩০": (22, 30, 0), "রাত ১২টা": (0, 0, 0), "রাত ২টা": (2, 0, 0), "সকাল ৬টা": (6, 0, 0),
                 "দুপুর ২টা": (14, 0, 0), "বিকেল ৪:৩০": (16, 30, 0), "शाम 6 बजे": (18, 0, 0), "सुबह 5:45": (5, 45, 0), "10.30": (10, 30, 0)}
        for t, want in cases.items():
            self.assertEqual(parse_time(t), want, t)
        for bad in ("25:00", "abc"):
            with self.assertRaises(ValueError):
                parse_time(bad)

    def test_unknown_time_words(self):
        for t in (None, "", "unknown", "অজানা", "पता नहीं"):
            self.assertTrue(is_unknown_time(t), t)
        self.assertFalse(is_unknown_time("10:30"))


class PlaceTests(unittest.TestCase):
    def test_bengali_hindi_and_old_names(self):
        for name in ("কলকাতা", "कोलकाता", "Calcutta", "Kolkata, West Bengal, India", "  KOLKATA "):
            self.assertEqual(location.resolve_location(name).tz_name, "Asia/Kolkata", name)
            self.assertAlmostEqual(location.resolve_location(name).lon, 88.3639, 3)
        self.assertEqual(location.resolve_location("ঢাকা").tz_name, "Asia/Dhaka")

    def test_lat_lon_string_and_missing_tz_notes(self):
        loc = location.resolve_location("22.57, 88.36")
        self.assertEqual(loc.tz_name, "Asia/Kolkata")
        self.assertTrue(loc.notes)                                   # says IST was assumed
        paris = location.resolve_location(lat=48.85, lon=2.35)
        self.assertEqual(paris.tz_name, "Europe/Paris")              # zone (with daylight saving) found from coordinates
        self.assertTrue(any("automatically" in n for n in paris.notes))

    def test_unknown_place_offline_gives_helpful_error(self):
        with mock.patch.dict(os.environ, {"JYOTISH_OFFLINE": "1"}):
            with self.assertRaises(ValueError) as cm:
                location.resolve_location("Nowheresville")
        self.assertIn("latitude", str(cm.exception))

    def test_online_geocoder_is_used_for_unknown_place(self):
        fake = {"results": [{"name": "Tezpur", "admin1": "Assam", "country": "India", "latitude": 26.6528, "longitude": 92.7926,
                             "timezone": "Asia/Kolkata"}]}
        with mock.patch.object(location, "_http_get_json", return_value=fake):
            loc = location.resolve_location("Tezpur")
        self.assertEqual((loc.tz_name, round(loc.lat, 2)), ("Asia/Kolkata", 26.65))
        self.assertTrue(any("geocoder" in n for n in loc.notes))

    def test_geocoder_failure_is_not_a_crash(self):
        with mock.patch.object(location, "_http_get_json", side_effect=OSError("no network")):
            with self.assertRaises(ValueError):
                location.resolve_location("Tezpur")


class ApiInputTests(unittest.TestCase):
    def test_same_birth_written_two_ways_gives_same_chart(self):
        a = api.kundli("1992-01-27", "22:30", place="kolkata", years=0)
        b = api.kundli("২৭ জানুয়ারি ১৯৯২", "রাত ১০:৩০", place="কলকাতা", years=0)
        self.assertEqual(a["lagna"], b["lagna"])
        self.assertEqual(a["planets"]["Moon"]["sidereal_longitude"], b["planets"]["Moon"]["sidereal_longitude"])

    def test_unknown_time_is_flagged(self):
        k = api.kundli("1992-01-27", None, place="kolkata", years=0)
        self.assertFalse(k["birth_time_known"])
        self.assertTrue(any("not known" in w for w in k["warnings"]))
        text = api.report("kundli", "en", date="1992-01-27", time="unknown", place="kolkata", years=0)
        self.assertIn("NOTES ON ASSUMPTIONS", text)

    def test_far_past_and_future_dates_work_with_warning(self):
        for d in ("1750-06-01", "2100-03-21", "1300-01-01"):
            k = api.kundli(d, "06:00", place="kolkata", years=0)
            self.assertEqual(len(k["planets"]), 9, d)
            self.assertTrue(any(d[:4] in w and "Year" in w for w in k["warnings"]), d)
        self.assertIsNone(range_note(1992))
        s = api.sky("2027-01-27", "10:00", place="delhi")          # near future: fine, no warning
        self.assertNotIn("warnings", s)

    def test_all_commands_accept_loose_input(self):
        self.assertIn("panchang", api.panchang("27 Jan 1992", place="Calcutta")["kind"])
        self.assertEqual(api.day_events("27/01/1992", place="কলকাতা")["date"], "1992-01-27")
        self.assertIn("1992-01-27", api.report("day", "en", date="27 Jan 1992", place="kolkata"))


class NameSyllableTests(unittest.TestCase):
    def test_classical_syllables(self):
        self.assertEqual(namakshar(0, 1), ("Chu", "चु"))        # Ashwini pada 1
        self.assertEqual(namakshar(14, 4), ("Ta", "ता"))        # Swati pada 4
        self.assertEqual(namakshar(26, 4), ("Chi", "ची"))       # Revati pada 4

    def test_in_kundli(self):
        k = api.kundli("1992-01-27", "10:30", place="kolkata", years=0)
        self.assertEqual(k["name_syllable"]["pada_syllable"]["latin"], "Ta")     # Moon in Swati pada 4
        self.assertIn("Ta", api.report("kundli", "en", date="1992-01-27", time="10:30", place="kolkata", years=0))


if __name__ == "__main__":
    unittest.main()
