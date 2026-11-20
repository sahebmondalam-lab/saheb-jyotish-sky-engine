# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Shadbala invariants and the API / CLI / MCP wiring of eclipses, Guna Milan and Shadbala."""
import json
import unittest

from jyotish import api, mcp_server, shadbala as SB
from jyotish.chart import build_chart
from jyotish.location import make_local_datetime, resolve_location


def chart(date, time, place="kolkata"):
    loc = resolve_location(place)
    return build_chart(make_local_datetime(date, time, loc), loc), loc


class Shadbala(unittest.TestCase):
    def test_constants(self):
        self.assertEqual([SB.MIN_VIRUPA[p] for p in SB.PLANETS7], [390, 360, 300, 420, 390, 330, 300])
        self.assertAlmostEqual(sum(SB.NAISARGIKA.values()), 240.0, delta=0.05)

    def test_drishti_curve(self):
        self.assertEqual(SB._drishti(10, "Sun"), 0)
        self.assertEqual(SB._drishti(60, "Sun"), 15)
        self.assertEqual(SB._drishti(90, "Sun"), 45)
        self.assertEqual(SB._drishti(180, "Sun"), 60)
        self.assertEqual(SB._drishti(300, "Sun"), 0)
        self.assertEqual(SB._drishti(240, "Jupiter"), 60)          # Jupiter's 9th aspect
        self.assertEqual(SB._drishti(210, "Mars"), 60)             # Mars' 8th aspect

    def test_ranges_and_totals(self):
        for d, t in (("2017-05-25", "07:00"), ("1992-01-27", "23:30"), ("2000-03-10", "03:00"), ("1950-08-15", "12:00")):
            c, loc = chart(d, t)
            r = SB.shadbala(c, loc)
            self.assertEqual(len(r["planets"]), 7)
            for x in r["planets"]:
                self.assertTrue(0 <= x["sthana"]["uccha"] <= 60)
                self.assertTrue(0 <= x["dig"] <= 60)
                self.assertTrue(0 <= x["kala"]["paksha"] <= 60)
                self.assertTrue(0 <= x["cheshta"] <= 60)
                parts = x["sthana"]["total"] + x["dig"] + x["kala"]["total"] + x["cheshta"] + x["naisargika"] + x["drik"]
                self.assertAlmostEqual(parts, x["total_virupa"], places=6)
                self.assertTrue(2.0 < x["total_rupa"] < 16.0, (d, x["planet"], x["total_rupa"]))

    def test_day_night_and_mercury(self):
        c, loc = chart("2017-05-25", "12:00")
        r = SB.shadbala(c, loc)
        self.assertTrue(r["context"]["day_birth"])
        by = {x["planet"]: x for x in r["planets"]}
        self.assertEqual(by["Mercury"]["kala"]["natonnata"], 60.0)
        self.assertGreater(by["Sun"]["kala"]["natonnata"], 55)        # noon: Sun at his best
        self.assertLess(by["Moon"]["kala"]["natonnata"], 5)
        c, loc = chart("2017-05-25", "00:10")
        by = {x["planet"]: x for x in SB.shadbala(c, loc)["planets"]}
        self.assertGreater(by["Moon"]["kala"]["natonnata"], 55)       # midnight: Moon, Mars, Saturn at their best

    def test_new_moon_paksha(self):
        c, loc = chart("2017-05-25", "07:00")                         # new moon: benefics weak, malefics strong
        by = {x["planet"]: x for x in SB.shadbala(c, loc)["planets"]}
        self.assertLess(by["Jupiter"]["kala"]["paksha"], 6)
        self.assertGreater(by["Saturn"]["kala"]["paksha"], 54)
        self.assertLess(by["Moon"]["kala"]["paksha"], 6)

    def test_hora_and_vara_lord(self):
        c, loc = chart("2017-05-25", "07:00")                         # Thursday
        self.assertEqual(SB.shadbala(c, loc)["context"]["vara_lord"], "Jupiter")


class Wiring(unittest.TestCase):
    def test_kundli_has_new_blocks(self):
        k = api.kundli("2017-05-25", "07:00", place="kolkata")
        self.assertIn("grahan", k)
        self.assertEqual(len(k["shadbala"]["planets"]), 7)
        k = api.kundli("2017-05-25", None, place="kolkata")
        self.assertNotIn("shadbala", k)

    def test_api_functions(self):
        e = api.eclipses(year=2026)
        self.assertEqual(len(e["eclipses"]), 4)
        s = api.shadbala("2017-05-25", "07:00", place="kolkata")
        self.assertEqual(s["kind"], "shadbala")
        with self.assertRaises(ValueError):
            api.shadbala("2017-05-25", None, place="kolkata")
        g = api.guna_milan({"date": "1992-01-27", "time": "14:30", "place": "kolkata"}, {"date": "1994-08-15", "time": "09:10", "place": "delhi"})
        self.assertEqual(g["max"], 36)
        self.assertEqual(g["credit"]["author"], "Saheb Mondal")

    def test_reports(self):
        for lang in ("en", "bn", "hi", "both", "all"):
            self.assertIn("UTC", api.report("eclipses", lang, year=2026))
        self.assertIn("Shadbala", api.report("kundli", "en", date="2017-05-25", time="07:00", place="kolkata", years=0))
        self.assertIn("TOTAL", api.report("guna_milan", "en", person_a={"date": "1992-01-27", "time": "14:30", "place": "kolkata"},
                                          person_b={"date": "1994-08-15", "time": "09:10", "place": "delhi"}))

    def test_mcp_tools(self):
        names = [t["name"] for t in mcp_server.TOOLS]
        for n in ("jyotish_eclipses", "jyotish_shadbala", "jyotish_match"):
            self.assertIn(n, names)
        r = json.loads(mcp_server.call_tool("jyotish_eclipses", {"year": 2025, "place": "kolkata"}))
        self.assertEqual(len(r["eclipses"]), 4)
        r = json.loads(mcp_server.call_tool("jyotish_match", {"person_a": {"date": "1992-01-27", "time": "14:30", "place": "kolkata"},
                                                              "person_b": {"date": "1994-08-15", "time": "09:10", "place": "delhi"}}))
        self.assertEqual(r["kind"], "guna_milan")
        with self.assertRaises(ValueError):
            mcp_server.call_tool("jyotish_match", {"person_a": {"date": "1992-01-27"}})


if __name__ == "__main__":
    unittest.main()
