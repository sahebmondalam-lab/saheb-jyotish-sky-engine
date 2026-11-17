# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Panchang: tithi, nakshatra, yoga, karana, vara, sunrise/sunset and inauspicious periods."""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Callable, Dict, Optional

from . import astro as A
from .location import Location

NAK_LEN = 360.0 / 27.0


def _angles(jd_ut: float):
    ay = A.ayanamsa_lahiri(A.jd_to_tt(jd_ut))
    sun_t = A.tropical_longitude("Sun", jd_ut)
    moon_t = A.tropical_longitude("Moon", jd_ut)
    return A.norm360(sun_t - ay), A.norm360(moon_t - ay)


def _tithi_angle(jd): s, m = _angles(jd); return A.norm360(m - s)
def _nak_angle(jd): return _angles(jd)[1]
def _yoga_angle(jd): s, m = _angles(jd); return A.norm360(s + m)


def next_boundary(jd_ut: float, f: Callable[[float], float], unit: float, max_days: float = 3.0) -> Optional[float]:
    """First time after jd_ut when floor(f/unit) changes (f is an angle in 0..360)."""
    base = int(f(jd_ut) // unit)
    step = 0.02
    t0, t1 = jd_ut, jd_ut
    while t1 - jd_ut < max_days:
        t1 = t0 + step
        if int(f(t1) // unit) != base:
            lo, hi = t0, t1
            for _ in range(40):
                mid = (lo + hi) / 2
                if int(f(mid) // unit) != base:
                    hi = mid
                else:
                    lo = mid
            return hi
        t0 = t1
    return None


def vedic_weekday(local_dt: datetime) -> int:
    """0=Sunday ... 6=Saturday for a civil date."""
    return (local_dt.weekday() + 1) % 7


def panchang_at(jd_ut: float, with_end_times: bool = True) -> Dict:
    sun_s, moon_s = _angles(jd_ut)
    diff = A.norm360(moon_s - sun_s)
    t_idx = int(diff // 12.0)                       # 0..29
    karana_idx = int(diff // 6.0)                   # 0..59
    yoga_total = A.norm360(sun_s + moon_s)
    y_idx = int(yoga_total // NAK_LEN)
    n_idx = int(moon_s // NAK_LEN)
    pada = int((moon_s % NAK_LEN) // (NAK_LEN / 4.0)) + 1
    elong = A.norm360(A.tropical_longitude("Moon", jd_ut) - A.tropical_longitude("Sun", jd_ut))
    illum = (1.0 - math.cos(math.radians(elong))) / 2.0
    out = {
        "tithi_index": t_idx,                       # 0..29 (0 = Shukla Pratipada)
        "tithi_number": t_idx + 1,
        "paksha": "shukla" if t_idx < 15 else "krishna",
        "tithi_in_paksha": t_idx % 15,              # 0..14
        "tithi_percent_elapsed": (diff % 12.0) / 12.0 * 100.0,
        "karana_index": karana_idx,
        "yoga_index": y_idx,
        "nakshatra_index": n_idx,
        "nakshatra_pada": pada,
        "moon_sign": int(moon_s // 30),
        "sun_sign": int(sun_s // 30),
        "elongation": elong,
        "moon_illumination": illum,
        "moon_phase_index": int(((elong + 22.5) % 360) // 45),
    }
    if with_end_times:
        out["tithi_end_jd"] = next_boundary(jd_ut, _tithi_angle, 12.0)
        out["karana_end_jd"] = next_boundary(jd_ut, _tithi_angle, 6.0)
        out["nakshatra_end_jd"] = next_boundary(jd_ut, _nak_angle, NAK_LEN)
        out["yoga_end_jd"] = next_boundary(jd_ut, _yoga_angle, NAK_LEN)
    return out


# Part (1..8 of daytime) for each weekday, 0=Sunday
_RAHU = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}
_YAMA = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}
_GULIKA = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}


def local_midnight_jd(d: date, loc: Location) -> float:
    return A.julian_day(datetime(d.year, d.month, d.day, tzinfo=loc.tz))


def day_times(d: date, loc: Location) -> Dict:
    """Sunrise, sunset and the traditional daily periods (all as UT Julian days)."""
    jd0 = local_midnight_jd(d, loc)
    rise, sset = A.sunrise_sunset(jd0, loc.lat, loc.lon)
    out: Dict = {"sunrise_jd": rise, "sunset_jd": sset, "weekday": (datetime(d.year, d.month, d.day).weekday() + 1) % 7}
    if rise is None or sset is None:
        return out
    wd = out["weekday"]
    part = (sset - rise) / 8.0
    def span(k): return (rise + (k - 1) * part, rise + k * part)
    out["rahu_kaal"] = span(_RAHU[wd])
    out["yamaganda"] = span(_YAMA[wd])
    out["gulika"] = span(_GULIKA[wd])
    muhurta = (sset - rise) / 15.0
    out["abhijit"] = (rise + 7 * muhurta, rise + 8 * muhurta)
    out["brahma_muhurta"] = (rise - 96.0 / 1440.0, rise - 48.0 / 1440.0)
    out["solar_noon_jd"] = (rise + sset) / 2.0
    return out


def day_panchang(d: date, loc: Location) -> Dict:
    """Panchang for a civil date, evaluated at local sunrise (the traditional reference moment)."""
    times = day_times(d, loc)
    ref = times["sunrise_jd"] if times.get("sunrise_jd") else local_midnight_jd(d, loc) + 0.25
    p = panchang_at(ref)
    p.update(times)
    p["reference_jd"] = ref
    p["vara_index"] = times["weekday"]
    return p
