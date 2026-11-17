# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Tests for divisional charts, Ashtakavarga, karakas and the deeper kundli sections."""
import json
import re
import unittest

from jyotish import api, deep

BENGALI = re.compile("[ঀ-৿]")
DEVANAGARI = re.compile("[ऀ-ॣ०-ॿ]")
KW = dict(date="1992-01-27", time="10:30", place="kolkata", years=0)


class DeepTests(unittest.TestCase):
    def test_ashtakavarga_tables_match_classical_totals(self):
        for g, rows in deep._BAV.items():
            self.assertEqual(sum(len(v) for v in rows.values()), deep.BAV_TOTALS[g], g)
        self.assertEqual(sum(deep.BAV_TOTALS.values()), 337)
        for g, n in (("Sun", 8), ("Jupiter", 9)):
            self.assertEqual(len(deep._BAV[g]), 8)               # 7 planets + Lagna

    def test_ashtakavarga_of_a_chart(self):
        k = api.kundli(**KW)["ashtakavarga"]
        self.assertEqual(k["total"], 337)
        for g, total in deep.BAV_TOTALS.items():
            self.assertEqual(sum(k["bhinna"][g]), total)
        self.assertEqual(sum(k["sarva"]), 337)
        self.assertEqual(k["sarva"], [25, 28, 32, 27, 30, 29, 31, 32, 22, 29, 23, 29])

    def test_navamsa_rules(self):
        # first navamsa of every sign: fire->Aries, earth->Capricorn, air->Libra, water->Cancer
        self.assertEqual([deep.varga_sign(s * 30 + 1, 9) for s in range(12)], [0, 9, 6, 3] * 3)
        self.assertEqual(deep.varga_sign(29.9, 9), 8)             # last navamsa of Aries = Sagittarius

    def test_other_vargas_basic_rules(self):
        self.assertEqual(deep.varga_sign(1, 2), 4)                # Aries first half hora = Sun's Leo
        self.assertEqual(deep.varga_sign(16, 2), 3)               # second half = Moon's Cancer
        self.assertEqual(deep.varga_sign(30 + 1, 2), 3)           # Taurus (even) first half = Moon
        self.assertEqual([deep.varga_sign(d, 3) for d in (1, 11, 21)], [0, 4, 8])
        self.assertEqual([deep.varga_sign(d, 30) for d in (1, 6, 12, 20, 27)], [0, 10, 8, 2, 6])     # Aries trimsamsa
        self.assertEqual([deep.varga_sign(30 + d, 30) for d in (1, 6, 14, 22, 28)], [1, 5, 11, 9, 7])  # Taurus trimsamsa
        for n in deep.VARGAS:                                     # every chart always yields a valid sign
            for lon in range(0, 360, 7):
                self.assertIn(deep.varga_sign(lon + 0.3, n), range(12))

    def test_karakas_ranked_by_degree(self):
        k = api.kundli(**KW)["jaimini_karakas"]
        self.assertEqual([k[x]["key"] for x in ("AK", "AmK", "BK", "MK", "PK", "GK", "DK")],
                         ["Jupiter", "Mars", "Moon", "Saturn", "Sun", "Venus", "Mercury"])

    def test_house_lords_and_json(self):
        j = api.kundli(**KW)
        json.dumps(j, ensure_ascii=False)
        h1 = j["bhava_table"][0]
        self.assertEqual((h1["lord"]["key"], h1["lord_in_house"]), ("Mars", 9))
        self.assertEqual(len(j["divisional_charts"]), 16)
        self.assertEqual(j["credit"]["author"], "Saheb Mondal")
        self.assertIn("Mercury", [x["key"] for x in j["vargottama_planets"]])


class DeepReportTests(unittest.TestCase):
    def test_sections_in_all_languages(self):
        en, bn, hi = (api.report("kundli", lg, **KW) for lg in ("en", "bn", "hi"))
        for t in (en, bn, hi):
            self.assertIn("Sarvashtakavarga", t) if t is en else None
            self.assertNotRegex(t, "[\x01\x02\x03\x04]")
        self.assertIn("Ashtakavarga", en)
        self.assertIn("অষ্টকবর্গ", bn)
        self.assertIn("अष्टकवर्ग", hi)
        self.assertIsNone(BENGALI.search(en)); self.assertIsNone(DEVANAGARI.search(en))
        self.assertIsNone(DEVANAGARI.search(bn))
        self.assertIsNone(BENGALI.search(hi))

    def test_north_indian_chart_places_planets_in_right_house(self):
        from jyotish.report_deep import north_indian_grid
        c = api.kundli(**KW)
        txt = "\n".join(north_indian_grid(0, {"Ketu": {"sign": 2, "retrograde": True}}))
        self.assertIn("Ke", txt)
        self.assertIn("1*", txt)
        self.assertEqual(c["lagna"]["sign"]["en"].split()[0], "Mesha")


if __name__ == "__main__":
    unittest.main()
