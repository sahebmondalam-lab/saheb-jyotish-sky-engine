# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Place + timezone handling."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Optional
from zoneinfo import ZoneInfo

from .data import PLACES


@dataclass
class Location:
    name: str
    lat: float
    lon: float          # degrees east
    tz: tzinfo
    tz_name: str


def parse_tz(text: str) -> tuple[tzinfo, str]:
    """IANA name ('Asia/Kolkata') or fixed offset ('+05:30', '-4')."""
    m = re.fullmatch(r"([+-])(\d{1,2})(?::?(\d{2}))?", text.strip())
    if m:
        sign = -1 if m.group(1) == "-" else 1
        delta = timedelta(hours=int(m.group(2)), minutes=int(m.group(3) or 0)) * sign
        return timezone(delta), f"UTC{m.group(1)}{int(m.group(2)):02d}:{int(m.group(3) or 0):02d}"
    return ZoneInfo(text.strip()), text.strip()


def resolve_location(place: Optional[str] = None, lat: Optional[float] = None,
                     lon: Optional[float] = None, tz: Optional[str] = None) -> Location:
    if lat is not None and lon is not None:
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError("lat must be -90..90 and lon -180..180 (east positive)")
        tzobj, tzname = parse_tz(tz or "Asia/Kolkata")
        return Location(place or f"{lat:.4f},{lon:.4f}", lat, lon, tzobj, tzname)
    if place:
        key = place.strip().lower()
        if key not in PLACES:
            raise ValueError(f"Unknown place '{place}'. Known: {', '.join(sorted(PLACES))}. "
                             "Or pass --lat --lon --tz.")
        la, lo, tzn = PLACES[key]
        tzobj, tzname = parse_tz(tz or tzn)
        return Location(place.title(), la, lo, tzobj, tzname)
    raise ValueError("Give --place NAME or --lat/--lon (and --tz).")


def make_local_datetime(date_str: str, time_str: str, loc: Location) -> datetime:
    """'1995-08-15' + '14:30' (or '14:30:15') in the place's timezone."""
    d = date.fromisoformat(date_str)
    parts = [int(x) for x in time_str.split(":")]
    while len(parts) < 3:
        parts.append(0)
    return datetime(d.year, d.month, d.day, parts[0], parts[1], parts[2], tzinfo=loc.tz)
