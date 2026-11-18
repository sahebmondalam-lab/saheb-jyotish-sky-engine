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


def _approx_tz(lat: float, lon: float):
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
        g = geocode(normalize(place).split(",")[0] if "," not in place else place) or geocode(normalize(place).split(",")[0])
        if g:
            tzobj, tzname = parse_tz(tz or g["tz"]) if (tz or g["tz"]) else _approx_tz(g["lat"], g["lon"])[:2]
            return Location(g["name"], g["lat"], g["lon"], tzobj, tzname, ["Place found through the online Open-Meteo geocoder; please check it is the right place."])
        raise ValueError(f"Unknown place '{place}' (and it could not be looked up online). Give latitude, longitude and "
                         "timezone instead (e.g. lat=26.7271 lon=88.3953 tz=Asia/Kolkata), or pick a built-in place with jyotish_places.")
    raise ValueError("Give a place name, or latitude and longitude (east positive) and a timezone.")


def make_local_datetime(date_str, time_str, loc: Location) -> datetime:
    """Any common date/time spelling, interpreted in the place's local time zone."""
    d = resolve_date(date_str, loc.calendar, loc.notes)
    h, mi, s = parse_time(time_str)
    return datetime(d.year, d.month, d.day, h, mi, s, tzinfo=loc.tz)
