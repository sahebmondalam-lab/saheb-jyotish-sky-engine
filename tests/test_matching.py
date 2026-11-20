# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Guna Milan (Ashtakoota): table invariants and hand-checked cases."""
import unittest

from jyotish import matching as M

NAK = 360.0 / 27.0


def nak_lon(i, frac=0.4):
    return (i + frac) * NAK


def score(res, key):
    return [k for k in res["kootas"] if k["key"] == key][0]["score"]


class Guna(unittest.TestCase):
    def test_maxima_add_to_36(self):
        self.assertEqual(sum(M.MAX_POINTS.values()), 36)
        for a in range(0, 360, 17):
            for b in range(0, 360, 23):
                r = M.match_from_moon_longitudes(float(a), float(b))
                self.assertTrue(0 <= r["total"] <= 36, (a, b))
                for k in r["kootas"]:
                    self.assertTrue(0 <= k["score"] <= k["max"], (a, b, k["key"]))
                self.assertAlmostEqual(sum(k["score"] for k in r["kootas"]), r["total"])

    def test_nadi(self):
        same = M.match_from_moon_longitudes(nak_lon(0), nak_lon(0, 0.6))
        self.assertEqual(score(same, "nadi"), 0)
        self.assertEqual(score(M.match_from_moon_longitudes(nak_lon(0), nak_lon(1)), "nadi"), 8)     # Aadi vs Madhya
        self.assertEqual(score(M.match_from_moon_longitudes(nak_lon(0), nak_lon(5)), "nadi"), 0)     # Ashwini, Ardra: both Aadi

    def test_yoni_enemies_and_same(self):
        self.assertEqual(score(M.match_from_moon_longitudes(nak_lon(0), nak_lon(12)), "yoni"), 0)    # horse vs buffalo
        self.assertEqual(score(M.match_from_moon_longitudes(nak_lon(0), nak_lon(23)), "yoni"), 4)    # horse vs horse (Shatabhisha)

    def test_gana(self):
        self.assertEqual(score(M.match_from_moon_longitudes(nak_lon(0), nak_lon(4)), "gana"), 6)     # Deva, Deva
        self.assertEqual(score(M.match_from_moon_longitudes(nak_lon(0), nak_lon(1)), "gana"), 5)     # Deva, Manushya
        self.assertEqual(score(M.match_from_moon_longitudes(nak_lon(0), nak_lon(2)), "gana"), 0)     # Deva, Rakshasa

    def test_bhakoot(self):
        # Moon signs 6/8 apart (Aries & Virgo) is the classical dosha unless the lords are friends
        r = M.match_from_moon_longitudes(10.0, 5 * 30 + 10.0)
        self.assertIn(score(r, "bhakoot"), (0, 7))
        r = M.match_from_moon_longitudes(10.0, 40.0)       # same sign family check: 1/2 relation
        self.assertIn(score(r, "bhakoot"), (0, 7))
        self.assertEqual(score(M.match_from_moon_longitudes(10.0, 100.0), "bhakoot"), 7)   # 4/10 apart is fine

    def test_graha_maitri_scale(self):
        self.assertEqual(M.graha_maitri_points("Sun", "Sun"), 5.0)
        self.assertEqual(M.graha_maitri_points("Sun", "Moon"), 5.0)       # mutual friends
        self.assertEqual(M.graha_maitri_points("Sun", "Saturn"), 0.0)     # mutual enemies
        self.assertEqual(M.graha_maitri_points("Sun", "Venus"), M.graha_maitri_points("Venus", "Sun"))

    def test_role_swap_keeps_symmetric_kootas(self):
        a, b = 77.0, 200.0
        r1 = M.match_from_moon_longitudes(a, b)
        r2 = M.match_from_moon_longitudes(b, a)
        for k in ("nadi", "bhakoot"):
            self.assertEqual(score(r1, k), score(r2, k))

    def test_manglik(self):
        r = M.match_from_moon_longitudes(10.0, 100.0, mars_house_a=7, mars_house_b=2)
        self.assertTrue(r["manglik"])

    def test_verdict_and_note(self):
        r = M.match_from_moon_longitudes(10.0, 100.0)
        self.assertIn("verdict", r)
        self.assertIn("en", r["method_note"])

    def test_render_all_languages(self):
        r = M.match_from_moon_longitudes(10.0, 100.0)
        for lang in ("en", "bn", "hi", "both", "all"):
            self.assertTrue(M.render(r, lang))


if __name__ == "__main__":
    unittest.main()
