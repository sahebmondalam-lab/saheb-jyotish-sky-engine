# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Place + timezone handling.

A place can be: a built-in name (English, Bengali or Hindi spelling), a 'lat,lon' pair, explicit latitude/longitude, or -
when the machine is online and JYOTISH_OFFLINE is not set - any place name on Earth, looked up through the free
Open-Meteo geocoding service (it returns coordinates and the IANA time zone). Everything else in this engine works offline.
"""
from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import List, Optional
from zoneinfo import ZoneInfo

from .data import PLACES, PLACE_ALIASES
from .calendars import resolve_date
from .parse import normalize, parse_time


LMT_BEFORE = 1884   # before the 1884 Washington conference there were no standard time zones


class HistoricTZ(tzinfo):
    """An IANA zone for modern dates and the place's own local mean time (longitude / 15 hours) before 1884.

    The IANA database only has one early 'LMT' value per zone (for India it is Calcutta's), which would be wrong by up to an hour for
    other places and meaningless in the Middle Ages, so before 1884 the exact local mean time of the longitude is used instead.
    """

    def __init__(self, base: ZoneInfo, lon: float):
        self.base = base
        self.lmt = timedelta(seconds=round(lon * 240.0))
        self.key = getattr(base, "key", str(base))

    def utcoffset(self, dt):
        if dt is None:
            return None
        return self.lmt if dt.year < LMT_BEFORE else dt.replace(tzinfo=self.base).utcoffset()

    def dst(self, dt):
        return timedelta(0) if dt is None or dt.year < LMT_BEFORE else dt.replace(tzinfo=self.base).dst()

    def tzname(self, dt):
        return "LMT" if dt is not None and dt.year < LMT_BEFORE else dt.replace(tzinfo=self.base).tzname()

    def fromutc(self, dt):
        if dt.year < LMT_BEFORE:
            return dt + self.lmt
        return self.base.fromutc(dt.replace(tzinfo=self.base)).replace(tzinfo=self)


def _wrap(tzobj: tzinfo, lon: float) -> tzinfo:
    return HistoricTZ(tzobj, lon) if isinstance(tzobj, ZoneInfo) else tzobj


@dataclass
class Location:
    name: str
    lat: float
    lon: float          # degrees east
    tz: tzinfo
    tz_name: str
    notes: List[str] = field(default_factory=list)   # assumptions made while resolving the place
    calendar: str = "auto"                            # how to read old dates: auto | julian | gregorian


def parse_tz(text: str) -> tuple[tzinfo, str]:
    """IANA name ('Asia/Kolkata') or fixed offset ('+05:30', '-4')."""
    m = re.fullmatch(r"(?:UTC|GMT)?\s*([+-])(\d{1,2})(?::?(\d{2}))?", text.strip())
    if m:
        sign = -1 if m.group(1) == "-" else 1
        delta = timedelta(hours=int(m.group(2)), minutes=int(m.group(3) or 0)) * sign
        return timezone(delta), f"UTC{m.group(1)}{int(m.group(2)):02d}:{int(m.group(3) or 0):02d}"
    try:
        return ZoneInfo(text.strip()), text.strip()
    except Exception:
        raise ValueError(f"Unknown time zone '{text}'. Use an IANA name like Asia/Kolkata or an offset like +05:30.") from None


def _http_get_json(url: str, timeout: float = 8.0):
    req = urllib.request.Request(url, headers={"User-Agent": "saheb-jyotish-sky-engine"})
    with urllib.request.urlopen(req, timeout=timeout) as r:   # noqa: S310 (fixed https URL built below)
        return json.loads(r.read().decode("utf-8"))


def geocode(name: str) -> Optional[dict]:
    """Look a place name up online (Open-Meteo geocoding). Returns None if offline, disabled or not found."""
    if os.environ.get("JYOTISH_OFFLINE"):
        return None
    url = ("https://geocoding-api.open-meteo.com/v1/search?count=1&format=json&name="
           + urllib.parse.quote(name))
    try:
        res = _http_get_json(url).get("results") or []
    except Exception:
        return None
    if not res:
        return None
    r = res[0]
    return {"name": ", ".join(x for x in (r.get("name"), r.get("admin1"), r.get("country")) if x),
            "lat": float(r["latitude"]), "lon": float(r["longitude"]), "tz": r.get("timezone")}


_EXTRA_ANCHORS = [   # zone.tab has one city per zone; these stop border towns of big countries snapping to a neighbour
    (23.83, 91.28, "Asia/Kolkata"), (26.14, 91.74, "Asia/Kolkata"), (24.82, 93.94, "Asia/Kolkata"),
    (27.33, 88.61, "Asia/Kolkata"), (11.62, 92.73, "Asia/Kolkata"),
    (23.46, 91.18, "Asia/Dhaka"), (23.96, 91.11, "Asia/Dhaka"), (23.02, 91.40, "Asia/Dhaka"), (22.82, 91.10, "Asia/Dhaka"),
    (25.75, 89.25, "Asia/Dhaka"), (25.63, 88.64, "Asia/Dhaka"), (26.85, 89.38, "Asia/Thimphu"), (27.47, 89.64, "Asia/Thimphu"), (34.08, 74.80, "Asia/Kolkata"),
    (34.15, 77.58, "Asia/Kolkata"), (28.61, 77.21, "Asia/Kolkata"), (19.08, 72.88, "Asia/Kolkata"),
    (13.08, 80.27, "Asia/Kolkata"), (8.52, 76.94, "Asia/Kolkata"), (22.57, 88.36, "Asia/Kolkata"),
    (26.85, 80.95, "Asia/Kolkata"), (23.26, 77.41, "Asia/Kolkata"), (21.15, 79.09, "Asia/Kolkata"),
    (29.65, 91.10, "Asia/Shanghai"), (29.27, 88.88, "Asia/Shanghai"), (31.48, 92.05, "Asia/Shanghai"), (36.62, 101.78, "Asia/Shanghai"),
    (39.90, 116.40, "Asia/Shanghai"), (45.75, 126.63, "Asia/Shanghai"), (23.13, 113.26, "Asia/Shanghai"),
    (25.04, 102.71, "Asia/Shanghai"), (30.57, 104.07, "Asia/Shanghai"), (34.30, 108.94, "Asia/Shanghai"),
    (31.63, 74.87, "Asia/Kolkata"), (23.02, 72.57, "Asia/Kolkata"), (25.59, 85.14, "Asia/Kolkata"),
    (20.30, 85.82, "Asia/Kolkata"), (15.30, 74.12, "Asia/Kolkata"), (12.97, 77.59, "Asia/Kolkata"),
]
_ZONE_POINTS: Optional[list] = None


def _iso6709(c: str):
    m = re.fullmatch(r"([+-])(\d{2})(\d{2})(\d{2})?([+-])(\d{3})(\d{2})(\d{2})?", c)
    if not m:
        return None
    la = int(m.group(2)) + int(m.group(3)) / 60 + int(m.group(4) or 0) / 3600
    lo = int(m.group(6)) + int(m.group(7)) / 60 + int(m.group(8) or 0) / 3600
    return (-la if m.group(1) == "-" else la), (-lo if m.group(5) == "-" else lo)


def _zone_points() -> list:
    """(lat, lon, IANA zone) reference points from the system tz database (zone.tab), plus a few extra anchors."""
    global _ZONE_POINTS
    if _ZONE_POINTS is not None:
        return _ZONE_POINTS
    pts: list = []
    try:
        import zoneinfo
        paths = list(zoneinfo.TZPATH)
        try:
            import tzdata  # type: ignore  # noqa: F401
        except Exception:
            pass
        for base in paths:
            f = os.path.join(base, "zone.tab")
            if os.path.exists(f):
                with open(f, encoding="utf-8") as fh:
                    for line in fh:
                        if line.startswith("#") or not line.strip():
                            continue
                        parts = line.rstrip("\n").split("\t")
                        if len(parts) >= 3:
                            c = _iso6709(parts[1])
                            if c:
                                pts.append((c[0], c[1], parts[2]))
                break
    except Exception:
        pts = []
    if pts:
        pts.extend(_EXTRA_ANCHORS)
        pts.extend((la, lo, tzn) for (la, lo, tzn) in PLACES.values())   # every built-in place is a known-good anchor too
    _ZONE_POINTS = pts
    return pts


def nearest_zone(lat: float, lon: float) -> Optional[str]:
    """IANA zone of the nearest reference city. Works offline for any coordinates on Earth; can be wrong close to a border."""
    from math import radians, sin, cos, asin, sqrt
    best, bd = None, 1e18
    for (a, o, z) in _zone_points():
        dl = radians(o - lon)
        h = sin(radians(a - lat) / 2) ** 2 + cos(radians(lat)) * cos(radians(a)) * sin(dl / 2) ** 2
        d = 2 * asin(min(1.0, sqrt(h)))
        if d < bd:
            best, bd = z, d
    return best


def geocode_osm(name: str) -> Optional[dict]:
    """Second online geocoder (OpenStreetMap Nominatim) - knows villages and small towns Open-Meteo may miss. No time zone returned."""
    if os.environ.get("JYOTISH_OFFLINE"):
        return None
    url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(name)
    try:
        res = _http_get_json(url)
    except Exception:
        return None
    if not res:
        return None
    r = res[0]
    return {"name": r.get("display_name") or name, "lat": float(r["lat"]), "lon": float(r["lon"]), "tz": None}


def _approx_tz(lat: float, lon: float):
    z = nearest_zone(lat, lon)
    if z:
        try:
            return ZoneInfo(z), z, [
                f"Time zone not given: found automatically from the coordinates ({z}, nearest reference city of the time-zone database, "
                "offline). Correct in almost every case; only a place right on a zone border could differ - give tz= to be certain."]
        except Exception:
            pass
    if 6 <= lat <= 36 and 68 <= lon <= 98:
        return ZoneInfo("Asia/Kolkata"), "Asia/Kolkata", ["Time zone not given: assumed India (IST, UTC+05:30)."]
    hours = round(lon / 15.0 * 2) / 2.0
    sign = "+" if hours >= 0 else "-"
    h = int(abs(hours))
    mi = int(round((abs(hours) - h) * 60))
    name = f"UTC{sign}{h:02d}:{mi:02d}"
    return timezone(timedelta(hours=hours)), name, [
        f"Time zone not given and place not in the built-in list: used {name} from longitude. This ignores daylight saving "
        "and historical rules, so the lagna can be wrong; give the IANA time zone (e.g. Europe/Paris) for an exact chart."]


def _clean(place: str) -> str:
    return re.sub(r"\s+", " ", normalize(place).replace("_", " ")).strip().lower()


def _builtin(place: str) -> Optional[str]:
    full = _clean(place)
    cands = [full] + [c.strip() for c in full.split(",") if c.strip()]
    for c in cands:
        c = PLACE_ALIASES.get(c, c)
        if c in PLACES:
            return c
    return None


def resolve_location(place: Optional[str] = None, lat: Optional[float] = None,
                     lon: Optional[float] = None, tz: Optional[str] = None, calendar: Optional[str] = None) -> Location:
    loc = _resolve(place, lat, lon, tz)
    loc.calendar = (calendar or "auto").lower()
    loc.tz = _wrap(loc.tz, loc.lon)
    return loc


def _resolve(place: Optional[str] = None, lat: Optional[float] = None,
             lon: Optional[float] = None, tz: Optional[str] = None) -> Location:
    if lat is None and lon is None and place:
        m = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*", normalize(place))
        if m:                                   # 'lat,lon' typed as the place
            lat, lon, place = float(m.group(1)), float(m.group(2)), None
    if lat is not None and lon is not None:
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError("lat must be -90..90 and lon -180..180 (east positive)")
        notes: List[str] = []
        if tz:
            tzobj, tzname = parse_tz(tz)
        else:
            tzobj, tzname, notes = _approx_tz(lat, lon)
        return Location(place or f"{lat:.4f},{lon:.4f}", lat, lon, tzobj, tzname, notes)
    if place:
        key = _builtin(place)
        if key:
            la, lo, tzn = PLACES[key]
            tzobj, tzname = parse_tz(tz or tzn)
            return Location(key.title(), la, lo, tzobj, tzname)
        first = normalize(place).split(",")[0]
        g = geocode(normalize(place) if "," in place else first) or geocode(first)
        src = "Open-Meteo"
        if not g:
            g = geocode_osm(normalize(place)) or geocode_osm(first)
            src = "OpenStreetMap"
        if g:
            notes = [f"Place found through the online {src} geocoder; please check it is the right place."]
            if tz or g["tz"]:
                tzobj, tzname = parse_tz(tz or g["tz"])
            else:
                tzobj, tzname, n2 = _approx_tz(g["lat"], g["lon"])
                notes += n2
            return Location(g["name"], g["lat"], g["lon"], tzobj, tzname, notes)
        raise ValueError(f"Unknown place '{place}' (and it could not be looked up online). Give latitude and longitude instead "
                         "(east positive, e.g. lat=22.10 lon=88.30); the time zone is then found automatically. "
                         "An AI assistant should supply the coordinates itself from its own knowledge or a web search.")
    raise ValueError("Give a place name, or latitude and longitude (east positive) and a timezone.")


def make_local_datetime(date_str, time_str, loc: Location) -> datetime:
    """Any common date/time spelling, interpreted in the place's local time zone."""
    d = resolve_date(date_str, loc.calendar, loc.notes)
    h, mi, s = parse_time(time_str)
    return datetime(d.year, d.month, d.day, h, mi, s, tzinfo=loc.tz)
