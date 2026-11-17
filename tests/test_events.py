# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Tests for the one-day events report (moon phases, sankranti, stations, tithi/nakshatra/yoga timeline)."""
import json
import re
import unittest
from datetime import date, timedelta

from jyotish import api, astro as A
from jyotish.cli import main as cli_main
from jyotish.events import day_events
from jyotish.location import resolve_location
from jyotish import mcp_server as M

KOL = resolve_location("kolkata")
BENGALI = re.compile("[ঀ-৿]")
DEVANAGARI = re.compile("[ऀ-ॣ०-ॿ]")


def ist(jd):
    return A.datetime_from_jd(jd).astimezone(KOL.tz)


class DayEventTests(unittest.TestCase):
    def test_27_jan_1992_kolkata(self):
        e = day_events(date(1992, 1, 27), KOL)
        self.assertEqual((e["ingresses"], e["stations"], e["moon_phases"]), ([], [], []))
        t0, t1 = e["tithi"]
        self.assertEqual((t0["index"], t1["index"]), (22, 23))           # Krishna Ashtami -> Navami
        self.assertEqual(ist(t0["end"]).strftime("%H:%M"), "09:08")
        n0, n1 = e["nakshatra"]
        self.assertEqual((n0["index"], n1["index"]), (14, 15))           # Swati -> Vishakha
        self.assertLess(abs((ist(n0["end"]) - ist(n0["end"]).replace(hour=11, minute=35)).total_seconds()), 90)

    def test_makar_sankranti_2026(self):
        e = day_events(date(2026, 1, 14), KOL)
        sun = [x for x in e["ingresses"] if x["planet"] == "Sun"]
        self.assertEqual(len(sun), 1)
        self.assertEqual((sun[0]["from_sign"], sun[0]["to_sign"]), (8, 9))      # Dhanu -> Makara
        mins = ist(sun[0]["jd"]).hour * 60 + ist(sun[0]["jd"]).minute
        self.assertLess(abs(mins - (15 * 60 + 13)), 15)                        # published ~15:13 IST

    def test_full_moon_1992(self):
        e = day_events(date(1992, 1, 20), KOL)
        full = [x for x in e["moon_phases"] if x["phase_index"] == 2]
        self.assertEqual(len(full), 1)
        self.assertEqual(ist(full[0]["jd"]).strftime("%H:%M"), "02:58")         # 1992-01-19 21:28 UT

    def test_saturn_station_2025(self):
        hits = []
        for k in range(10, 17):
            hits += [(date(2025, 7, 10) + timedelta(days=k - 10), s) for s in day_events(date(2025, 7, 10) + timedelta(days=k - 10), KOL)["stations"]]
        sat = [(d, s) for d, s in hits if s["planet"] == "Saturn"]
        self.assertEqual(len(sat), 1)
        self.assertEqual(sat[0][0], date(2025, 7, 13))
        self.assertEqual(sat[0][1]["turns"], "retrograde")

    def test_timeline_is_continuous_and_covers_day(self):
        e = day_events(date(2026, 11, 16), KOL)
        for k in ("tithi", "nakshatra", "yoga"):
            segs = e[k]
            self.assertLessEqual(segs[0]["start"], e["from_jd"])
            self.assertGreaterEqual(segs[-1]["end"], e["to_jd"])
            for a, b in zip(segs, segs[1:]):
                self.assertAlmostEqual(a["end"], b["start"], places=4)


class DayOutputTests(unittest.TestCase):
    def test_panchang_shows_next(self):
        t = api.report("panchang", "en", date="1992-01-27", place="kolkata")
        self.assertIn("then Navami", t)
        self.assertIn("then Vishakha", t)
        p = api.panchang("1992-01-27", place="kolkata")["panchang"]
        self.assertEqual(p["tithi"]["next"]["en"], "Navami")
        self.assertEqual(p["nakshatra"]["next"]["en"], "Vishakha")

    def test_api_json_and_credit(self):
        j = api.day_events("1992-01-20", place="kolkata")
        json.dumps(j, ensure_ascii=False)
        self.assertEqual(j["credit"]["author"], "Saheb Mondal")
        self.assertEqual(j["moon_phases"][0]["en"].split()[0], "Full")

    def test_languages_stay_clean(self):
        en = api.report("day", "en", date="1992-01-20", place="kolkata")
        bn = api.report("day", "bn", date="1992-01-20", place="kolkata")
        hi = api.report("day", "hi", date="1992-01-20", place="kolkata")
        self.assertIsNone(BENGALI.search(en)); self.assertIsNone(DEVANAGARI.search(en))
        self.assertRegex(bn, BENGALI); self.assertIsNone(DEVANAGARI.search(bn))
        self.assertRegex(hi, DEVANAGARI); self.assertIsNone(BENGALI.search(hi))
        for t in (en, bn, hi):
            self.assertNotRegex(t, "[\x01\x02\x03\x04]")
        self.assertIn("Saheb Mondal", en)
        self.assertIn("সাহেব মন্ডল", bn)
        self.assertIn("साहेब", hi)

    def test_cli_and_mcp(self):
        self.assertEqual(cli_main(["day", "--date", "1992-01-27", "--place", "kolkata", "--lang", "all"]), 0)
        self.assertEqual(cli_main(["day", "--date", "1992-01-27", "--place", "kolkata", "--json"]), 0)
        r = M.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                      "params": {"name": "jyotish_day_events", "arguments": {"date": "1992-01-27", "place": "kolkata"}}})["result"]
        self.assertFalse(r["isError"])
        self.assertEqual(json.loads(r["content"][0]["text"])["credit"]["author"], "Saheb Mondal")


if __name__ == "__main__":
    unittest.main()
