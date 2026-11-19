# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Time zone found automatically from latitude/longitude (offline), and the online-geocoder fallbacks (mocked)."""
import os
import unittest
from unittest import mock

from jyotish import location
from jyotish.data import PLACES

# Independent check points (not used as anchors): well-known towns, including ones close to borders.
POINTS = [
    ("Lakshmikantapur", 22.10, 88.30, "Asia/Kolkata"), ("Siliguri", 26.72, 88.43, "Asia/Kolkata"),
    ("Agartala", 23.83, 91.28, "Asia/Kolkata"), ("Imphal", 24.82, 93.94, "Asia/Kolkata"), ("Leh", 34.15, 77.58, "Asia/Kolkata"),
    ("Rajshahi", 24.37, 88.60, "Asia/Dhaka"), ("Barisal", 22.70, 90.37, "Asia/Dhaka"), ("Comilla", 23.46, 91.18, "Asia/Dhaka"),
    ("Peshawar", 34.01, 71.52, "Asia/Karachi"), ("Birgunj", 27.00, 84.87, "Asia/Kathmandu"),
    ("Kunming", 25.04, 102.70, "Asia/Shanghai"), ("Lhasa", 29.65, 91.10, "Asia/Shanghai"), ("Busan", 35.18, 129.08, "Asia/Seoul"),
    ("Osaka", 34.69, 135.50, "Asia/Tokyo"), ("Vladivostok", 43.12, 131.89, "Asia/Vladivostok"), ("London", 51.50, -0.12, "Europe/London"),
    ("Cairo", 30.04, 31.24, "Africa/Cairo"), ("Lagos", 6.52, 3.38, "Africa/Lagos"), ("Sao Paulo", -23.55, -46.63, "America/Sao_Paulo"),
    ("Los Angeles", 34.05, -118.24, "America/Los_Angeles"), ("Toronto", 43.65, -79.38, "America/Toronto"),
    ("Moscow", 55.75, 37.62, "Europe/Moscow"), ("Auckland", -36.85, 174.76, "Pacific/Auckland"), ("Tehran", 35.69, 51.39, "Asia/Tehran"),
    ("Jakarta", -6.20, 106.85, "Asia/Jakarta"), ("Sydney", -33.87, 151.21, "Australia/Sydney"),
]


class AutoTimezone(unittest.TestCase):
    def test_points(self):
        for name, la, lo, z in POINTS:
            self.assertEqual(location.nearest_zone(la, lo), z, name)

    def test_all_builtin_places_resolve_to_their_own_zone(self):
        for k, (la, lo, z) in PLACES.items():
            self.assertEqual(location.nearest_zone(la, lo), z, k)

    def test_lat_lon_only_gives_ist_and_a_note(self):
        loc = location.resolve_location(lat=22.1, lon=88.3)
        self.assertEqual(loc.tz_name, "Asia/Kolkata")
        self.assertTrue(any("automatically" in n for n in loc.notes))

    def test_dst_is_handled_for_automatic_zone(self):
        loc = location.resolve_location(lat=48.85, lon=2.35)       # Paris, no tz given
        dt = location.make_local_datetime("2020-07-01", "12:00", loc)
        self.assertEqual(dt.utcoffset().total_seconds(), 7200)      # CEST
        dt = location.make_local_datetime("2020-01-01", "12:00", loc)
        self.assertEqual(dt.utcoffset().total_seconds(), 3600)      # CET

    def test_explicit_tz_still_wins(self):
        loc = location.resolve_location(lat=22.1, lon=88.3, tz="+06:00")
        self.assertEqual(loc.tz.utcoffset(None).total_seconds(), 21600)

    def test_geocoder_falls_back_to_osm_and_finds_zone_offline(self):
        os.environ.pop("JYOTISH_OFFLINE", None)
        with mock.patch.object(location, "geocode", return_value=None), \
                mock.patch.object(location, "geocode_osm", return_value={"name": "Lakshmikantapur", "lat": 22.1, "lon": 88.32, "tz": None}):
            loc = location.resolve_location(place="Lakshmikantapur")
        self.assertEqual(loc.tz_name, "Asia/Kolkata")
        self.assertTrue(any("OpenStreetMap" in n for n in loc.notes))

    def test_unknown_place_offline_message_asks_for_coordinates(self):
        with mock.patch.dict(os.environ, {"JYOTISH_OFFLINE": "1"}):
            with self.assertRaises(ValueError) as cm:
                location.resolve_location(place="Nowhereville Xyz")
        self.assertIn("latitude and longitude", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
