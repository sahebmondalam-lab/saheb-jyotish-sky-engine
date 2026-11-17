# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Build a Vedic birth chart (rashi chart, whole-sign houses, Lahiri ayanamsa)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from . import astro as A
from . import dasha, extras, panchang, yogas
from .data import DEBIL, EXALT, OWN
from .location import Location

NAK_LEN = 360.0 / 27.0


def _dignity(planet: str, sign: int) -> str:
    if planet not in EXALT:
        return "neutral"
    if EXALT[planet] == sign:
        return "exalted"
    if DEBIL[planet] == sign:
        return "debilitated"
    if sign in OWN[planet]:
        return "own"
    return "neutral"


def _nak_info(lon: float) -> Dict:
    idx = int(lon // NAK_LEN) % 27
    pada = int((lon % NAK_LEN) // (NAK_LEN / 4.0)) + 1
    return {"nakshatra": idx, "pada": pada}


def build_chart(local_dt: datetime, loc: Location, name: str = "") -> Dict:
    utc = local_dt.astimezone(timezone.utc)
    jd = A.julian_day(utc)
    ay = A.ayanamsa_lahiri(A.jd_to_tt(jd))
    pos = A.all_positions(jd)

    asc = A.ascendant_sidereal(jd, loc.lat, loc.lon)
    lagna_sign = int(asc // 30) % 12

    planets: Dict[str, Dict] = {}
    for g, p in pos.items():
        s = p["sidereal"]
        sign = int(s // 30) % 12
        info = _nak_info(s)
        planets[g] = {
            "sidereal": s, "tropical": p["tropical"], "sign": sign, "degree": s % 30,
            "house": (sign - lagna_sign) % 12 + 1, "retrograde": p["retrograde"], "speed": p["speed"],
            "dignity": _dignity(g, sign), "navamsa": int(s / (30.0 / 9.0)) % 12, **info,
        }

    houses = {h: {"sign": (lagna_sign + h - 1) % 12, "planets": []} for h in range(1, 13)}
    for g, p in planets.items():
        houses[p["house"]]["planets"].append(g)

    # Vara: the Vedic day starts at sunrise
    d = local_dt.date()
    times = panchang.day_times(d, loc)
    wd = times["weekday"]
    if times.get("sunrise_jd") and jd < times["sunrise_jd"]:
        wd = (wd - 1) % 7
    pc = panchang.panchang_at(jd)
    pc["vara_index"] = wd

    moon = planets["Moon"]
    periods = dasha.vimshottari(moon["sidereal"], jd)

    chart = {
        "meta": {
            "name": name, "local_time": local_dt.isoformat(), "utc_time": utc.isoformat(),
            "jd_ut": jd, "place": loc.name, "lat": loc.lat, "lon": loc.lon, "tz": loc.tz_name,
            "ayanamsa": ay, "ayanamsa_system": "Lahiri (Chitrapaksha), mean",
        },
        "lagna": {"sidereal": asc, "sign": lagna_sign, "degree": asc % 30, **_nak_info(asc)},
        "planets": planets,
        "houses": houses,
        "moon_sign": moon["sign"],
        "panchang": pc,
        "day_times": times,
        "dasha": {"periods": periods, "balance": dasha.balance_at_birth(moon["sidereal"])},
        "yogas": yogas.detect(planets, lagna_sign),
        "numerology": extras.numerology(d),
        "western": extras.western_signs(jd, loc.lat, loc.lon),
    }
    return chart
