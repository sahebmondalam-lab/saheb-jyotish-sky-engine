# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Grahan (eclipses): solar and lunar eclipses found from the real Sun and Moon positions, offline.

Method: every new moon (solar) and full moon (lunar) is found from the Sun/Moon longitudes; the minimum geocentric
angular separation (Moon-Sun, or Moon-antisolar point) is then searched with Meeus ch.47 Moon longitude, latitude and
distance. Eclipse limits use the apparent radii and horizontal parallaxes (solar: partial if d < s_sun + s_moon +
pi_moon - pi_sun, central if gamma < 0.9972; lunar: Danjon rule, shadow enlarged by 1/50).

Accuracy: the greatest-eclipse time is normally within a few minutes of the NASA value for 1800-2050 and the type and
date are right for every eclipse checked (see tests/test_eclipses.py). Magnitudes are good to a few hundredths.
Far from the present (before ~1000 or after ~3000) the Moon's secular acceleration and Delta T are uncertain, so
times can be off by hours and borderline (very small partial / penumbral) eclipses may be missed or invented.
Dates are UTC on the proleptic Gregorian calendar. The Rahu/Ketu node is the mean node.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Tuple

from . import astro as A
from . import data as D
from .data_hi import h as _hi

SYNODIC = 29.530588
MOON_RATE = 12.1907            # mean elongation gain, degrees per day
RE_KM = 6378.14
R_MOON_KM = 1737.4
R_SUN_KM = 695700.0
AU_KM = 149597870.7
DEG = math.pi / 180.0


# ------------------------------------------------------------------ Moon latitude and distance (Meeus ch.47, tables 47.A/47.B)
# (D, M, M', F, coefficient of cos for distance in 0.001 km)
_MOON_R = [
    (0, 0, 1, 0, -20905355), (2, 0, -1, 0, -3699111), (2, 0, 0, 0, -2955968), (0, 0, 2, 0, -569925),
    (0, 1, 0, 0, 48888), (0, 0, 0, 2, -3149), (2, 0, -2, 0, 246158), (2, -1, -1, 0, -152138),
    (2, 0, 1, 0, -170733), (2, -1, 0, 0, -204586), (0, 1, -1, 0, -129620), (1, 0, 0, 0, 108743),
    (0, 1, 1, 0, 104755), (2, 0, 0, -2, 10321), (0, 0, 1, -2, 79661), (4, 0, -1, 0, -34782),
    (0, 0, 3, 0, -23210), (4, 0, -2, 0, -21636), (2, 1, -1, 0, 24208), (2, 1, 0, 0, 30824),
    (1, 0, -1, 0, -8379), (1, 1, 0, 0, -16675), (2, -1, 1, 0, -12831), (2, 0, 2, 0, -10445),
    (4, 0, 0, 0, -11650), (2, 0, -3, 0, 14403), (0, 1, -2, 0, -7003), (2, -1, -2, 0, 10056),
    (1, 0, 1, 0, 6322), (2, -2, 0, 0, -9884), (0, 1, 2, 0, 5751), (2, -2, -1, 0, -4950),
    (2, 0, 1, -2, 4130), (4, -1, -1, 0, -3958), (3, 0, -1, 0, 3258), (2, 1, 1, 0, 2616),
    (4, -1, -2, 0, -1897), (0, 2, -1, 0, -2117), (2, 2, -1, 0, 2354), (4, 0, 1, 0, -1423),
    (0, 0, 4, 0, -1117), (4, -1, 0, 0, -1571), (1, 0, -2, 0, -1739), (0, 0, 2, -2, -4421),
    (0, 2, 1, 0, 1165), (2, 0, -1, -2, 8752),
]
# (D, M, M', F, coefficient of sin for latitude in 1e-6 degree)
_MOON_B = [
    (0, 0, 0, 1, 5128122), (0, 0, 1, 1, 280602), (0, 0, 1, -1, 277693), (2, 0, 0, -1, 173237),
    (2, 0, -1, 1, 55413), (2, 0, -1, -1, 46271), (2, 0, 0, 1, 32573), (0, 0, 2, 1, 17198),
    (2, 0, 1, -1, 9266), (0, 0, 2, -1, 8822), (2, -1, 0, -1, 8216), (2, 0, -2, -1, 4324),
    (2, 0, 1, 1, 4200), (2, 1, 0, -1, -3359), (2, -1, -1, 1, 2463), (2, -1, 0, 1, 2211),
    (2, -1, -1, -1, 2065), (0, 1, -1, -1, -1870), (4, 0, -1, -1, 1828), (0, 1, 0, 1, -1794),
    (0, 0, 0, 3, -1749), (0, 1, -1, 1, -1565), (1, 0, 0, 1, -1491), (0, 1, 1, 1, -1475),
    (0, 1, 1, -1, -1410), (0, 1, 0, -1, -1344), (1, 0, 0, -1, -1335), (0, 0, 3, 1, 1107),
    (4, 0, 0, -1, 1021), (4, 0, -1, 1, 833), (0, 0, 1, -3, 777), (4, 0, -2, 1, 671),
    (2, 0, 0, -3, 607), (2, 0, 2, -1, 596), (2, -1, 1, -1, 491), (2, 0, -2, 1, -451),
    (0, 0, 3, -1, 439), (2, 0, 2, 1, 422), (2, 0, -3, -1, 421), (2, 1, -1, 1, -366),
    (2, 1, 0, 1, -351), (4, 0, 0, 1, 331), (2, -1, 1, 1, 315), (2, -2, 0, -1, 302),
    (0, 0, 1, 3, -283), (2, 1, 1, -1, -229), (1, 1, 0, -1, 223), (1, 1, 0, 1, 223),
    (0, 1, -2, -1, -220), (2, 1, -1, -1, -220), (1, 0, 1, 1, -185), (2, -1, -2, -1, 181),
    (0, 1, 2, 1, -177), (4, 0, -2, -1, 176), (4, -1, -1, -1, 166), (1, 0, 1, -1, -164),
    (4, 0, 1, -1, 132), (1, 0, -1, -1, -119), (4, -1, 0, -1, 115), (2, -2, 0, 1, 107),
]


def moon_lat_dist(T: float) -> Tuple[float, float]:
    """Geocentric Moon ecliptic latitude (degrees) and distance (km), T = Julian centuries (TT) from J2000."""
    sind, cosd = A.sind, A.cosd
    Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + T**3 / 538841.0 - T**4 / 65194000.0
    D_ = 297.8501921 + 445267.1114034 * T - 0.0018819 * T * T + T**3 / 545868.0 - T**4 / 113065000.0
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T**3 / 24490000.0
    Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T**3 / 69699.0 - T**4 / 14712000.0
    F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T * T - T**3 / 3526000.0 + T**4 / 863310000.0
    A1 = 119.75 + 131.849 * T
    A3 = 313.45 + 481266.484 * T
    E = 1.0 - 0.002516 * T - 0.0000074 * T * T
    sb = 0.0
    for d, m, mp, f, c in _MOON_B:
        sb += c * (E ** abs(m)) * sind(d * D_ + m * M + mp * Mp + f * F)
    sb += (-2235.0 * sind(Lp) + 382.0 * sind(A3) + 175.0 * sind(A1 - F) + 175.0 * sind(A1 + F)
           + 127.0 * sind(Lp - Mp) - 115.0 * sind(Lp + Mp))
    sr = 0.0
    for d, m, mp, f, c in _MOON_R:
        sr += c * (E ** abs(m)) * cosd(d * D_ + m * M + mp * Mp + f * F)
    return sb / 1.0e6, 385000.56 + sr / 1000.0


def _earth_sun_au(T: float) -> float:
    ex, ey, ez = A._helio_xyz("Earth", T)
    return math.sqrt(ex * ex + ey * ey + ez * ez)


def _state(jd: float) -> Dict[str, float]:
    T = A.centuries(A.jd_to_tt(jd))
    beta, dist = moon_lat_dist(T)
    return {"T": T, "sun": A.sun_longitude(T), "moon": A.moon_longitude(T), "beta": beta,
            "dist": dist, "rs": _earth_sun_au(T)}


def _elong(jd: float) -> float:
    return A.norm360(A.tropical_longitude("Moon", jd) - A.tropical_longitude("Sun", jd))


def _syzygy_near(guess: float, target: float) -> float:
    """UT Julian day at which the Moon-Sun elongation equals `target` (0 new, 180 full), found from the guess."""
    jd = guess
    for _ in range(30):
        diff = A.norm180(_elong(jd) - target)
        jd -= diff / MOON_RATE
        if abs(diff) < 1e-5:
            break
    return jd


def _sep(jd: float, kind: str) -> float:
    """Geocentric angular separation in degrees: Moon from Sun (solar) or from the antisolar point (lunar)."""
    T = A.centuries(A.jd_to_tt(jd))
    beta, _ = moon_lat_dist(T)
    dl = A.norm180(A.moon_longitude(T) - A.sun_longitude(T) - (180.0 if kind == "lunar" else 0.0)) * DEG
    b = beta * DEG
    return math.degrees(math.atan2(math.hypot(math.cos(b) * math.sin(dl), math.sin(b)), math.cos(b) * math.cos(dl)))


def _golden_min(f, a: float, b: float, tol: float = 2e-6) -> float:
    g = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    while b - a > tol:
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = f(d)
    return (a + b) / 2.0


# ------------------------------------------------------------------ names (English, Bengali, Hindi)
_TITLES = {
    ("solar", "total"): ("Total solar eclipse (Surya Grahan)", "পূর্ণ সূর্যগ্রহণ", "पूर्ण सूर्य ग्रहण"),
    ("solar", "annular"): ("Annular solar eclipse (ring of fire)", "বলয়গ্রাস সূর্যগ্রহণ", "वलयाकार सूर्य ग्रहण"),
    ("solar", "hybrid"): ("Hybrid (annular-total) solar eclipse", "সংকর (বলয়-পূর্ণ) সূর্যগ্রহণ", "संकर (वलय-पूर्ण) सूर्य ग्रहण"),
    ("solar", "partial"): ("Partial solar eclipse", "আংশিক সূর্যগ্রহণ", "आंशिक सूर्य ग्रहण"),
    ("lunar", "total"): ("Total lunar eclipse (Chandra Grahan)", "পূর্ণ চন্দ্রগ্রহণ", "पूर्ण चंद्र ग्रहण"),
    ("lunar", "partial"): ("Partial lunar eclipse", "আংশিক চন্দ্রগ্রহণ", "आंशिक चंद्र ग्रहण"),
    ("lunar", "penumbral"): ("Penumbral lunar eclipse", "উপচ্ছায়া চন্দ্রগ্রহণ", "उपच्छाया चंद्र ग्रहण"),
}


def _n3(pair) -> Dict[str, str]:
    return {"en": pair[0], "bn": pair[1], "hi": _hi(pair)}


def _sid_info(lon: float) -> Dict:
    rashi = int(lon // 30) % 12
    nk = int(lon / (360.0 / 27.0)) % 27
    pada = int((lon % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
    return {"sidereal_longitude": round(lon, 3), "rashi": {"index": rashi, **_n3(D.RASHI[rashi])},
            "nakshatra": {"index": nk, "pada": pada, **_n3(D.NAKSHATRA[nk])}}


def _node_link(jd: float, kind: str) -> Dict:
    lum = "Sun" if kind == "solar" else "Moon"
    lon = A.sidereal_longitude(lum, jd)
    rahu = A.sidereal_longitude("Rahu", jd)
    ketu = A.norm360(rahu + 180.0)
    dr, dk = abs(A.norm180(lon - rahu)), abs(A.norm180(lon - ketu))
    node, dist = ("Rahu", dr) if dr <= dk else ("Ketu", dk)
    return {"luminary": lum, "node": node, "node_name": _n3(D.PLANET[node]), "distance_deg": round(dist, 2),
            "rahu_sidereal": round(rahu, 3), "ketu_sidereal": round(ketu, 3),
            "note": "Mean node. At an eclipse the eclipsed Sun (new moon) or Moon (full moon) sits close to Rahu or Ketu."}


# ------------------------------------------------------------------ the eclipse search
def _solar(jd_new: float) -> Optional[Dict]:
    T = A.centuries(A.jd_to_tt(jd_new))
    if abs(moon_lat_dist(T)[0]) > 1.85:
        return None
    jd = _golden_min(lambda t: _sep(t, "solar"), jd_new - 0.125, jd_new + 0.125)
    st = _state(jd)
    d = _sep(jd, "solar")
    s_s = 959.63 / 3600.0 / st["rs"]
    s_m = math.degrees(math.asin(R_MOON_KM / st["dist"]))
    pi_m = math.degrees(math.asin(RE_KM / st["dist"]))
    pi_s = 8.794 / 3600.0 / st["rs"]
    if d >= s_s + s_m + pi_m - pi_s:
        return None
    gamma = d / (pi_m - pi_s)
    hybrid = False
    if gamma < 0.9972:                       # central: the axis of the shadow crosses the Earth
        near = st["dist"] - RE_KM * math.sqrt(max(0.0, 1.0 - gamma * gamma))
        s_obs = math.degrees(math.asin(R_MOON_KM / near))
        if s_obs >= s_s:
            kind_t = "total"
            hybrid = s_m < s_s
        else:
            kind_t = "annular"
        mag = s_obs / s_s
        if hybrid:
            kind_t = "hybrid"
    else:
        kind_t = "partial"
        mag = (s_s + s_m - (d - (pi_m - pi_s))) / (2.0 * s_s)
    return {"kind": "solar", "type": kind_t, "jd_ut": jd, "magnitude": round(mag, 4), "gamma": round(gamma, 4),
            "separation_deg": round(d, 4), "sun_semidiameter_deg": round(s_s, 5), "moon_semidiameter_deg": round(s_m, 5),
            "moon_distance_km": round(st["dist"]), "hybrid": hybrid}


def _lunar_radii(st: Dict) -> Tuple[float, float, float]:
    s_s = 959.63 / 3600.0 / st["rs"]
    s_m = math.degrees(math.asin(R_MOON_KM / st["dist"]))
    pi_m = math.degrees(math.asin(RE_KM / st["dist"]))
    pi_s = 8.794 / 3600.0 / st["rs"]
    umbra = 1.02 * (pi_m + pi_s - s_s)
    penumbra = 1.02 * (pi_m + pi_s + s_s)
    return umbra, penumbra, s_m


def _lunar(jd_full: float) -> Optional[Dict]:
    T = A.centuries(A.jd_to_tt(jd_full))
    if abs(moon_lat_dist(T)[0]) > 1.85:
        return None
    jd = _golden_min(lambda t: _sep(t, "lunar"), jd_full - 0.125, jd_full + 0.125)
    st = _state(jd)
    d = _sep(jd, "lunar")
    umbra, penumbra, s_m = _lunar_radii(st)
    if d >= penumbra + s_m:
        return None
    um = (umbra + s_m - d) / (2.0 * s_m)
    pm = (penumbra + s_m - d) / (2.0 * s_m)
    if d < umbra - s_m:
        kind_t = "total"
    elif d < umbra + s_m:
        kind_t = "partial"
    else:
        kind_t = "penumbral"
    out = {"kind": "lunar", "type": kind_t, "jd_ut": jd, "magnitude": round(um if um > 0 else pm, 4),
           "umbral_magnitude": round(um, 4), "penumbral_magnitude": round(pm, 4), "separation_deg": round(d, 4),
           "umbra_radius_deg": round(umbra, 4), "penumbra_radius_deg": round(penumbra, 4),
           "moon_semidiameter_deg": round(s_m, 5), "moon_distance_km": round(st["dist"])}
    out["contacts_jd"] = _lunar_contacts(jd, umbra, penumbra, s_m, kind_t)
    return out


def _lunar_contacts(jd: float, umbra: float, penumbra: float, s_m: float, kind_t: str) -> Dict[str, float]:
    """Penumbral (P1,P4), partial (U1,U4) and total (U2,U3) contact times, UT Julian days (shadow radii held at the greatest-eclipse value)."""
    def cross(level: float, sign: int) -> Optional[float]:
        a, b = jd, jd + sign * 0.2
        if _sep(b, "lunar") <= level:
            return None
        for _ in range(40):
            m = (a + b) / 2.0
            if _sep(m, "lunar") < level:
                a = m
            else:
                b = m
        return (a + b) / 2.0
    out: Dict[str, float] = {}
    for name, level, sign in (("P1", penumbra + s_m, -1), ("P4", penumbra + s_m, 1)):
        v = cross(level, sign)
        if v is not None:
            out[name] = v
    if kind_t in ("partial", "total"):
        for name, level, sign in (("U1", umbra + s_m, -1), ("U4", umbra + s_m, 1)):
            v = cross(level, sign)
            if v is not None:
                out[name] = v
    if kind_t == "total":
        for name, level, sign in (("U2", umbra - s_m, -1), ("U3", umbra - s_m, 1)):
            v = cross(level, sign)
            if v is not None:
                out[name] = v
    return out


def _finish(e: Dict) -> Dict:
    jd = e["jd_ut"]
    t = _TITLES[(e["kind"], e["type"])]
    e["title"] = {"en": t[0], "bn": t[1], "hi": t[2]}
    e["utc"] = A.format_jd(jd, fmt="%Y-%m-%d %H:%M")
    e["date_utc"] = A.format_jd(jd, fmt="%Y-%m-%d")
    e["sun"] = _sid_info(A.sidereal_longitude("Sun", jd))
    e["moon"] = _sid_info(A.sidereal_longitude("Moon", jd))
    e["node_link"] = _node_link(jd, e["kind"])
    if "contacts_jd" in e:
        e["contacts_utc"] = {k: A.format_jd(v, fmt="%Y-%m-%d %H:%M") for k, v in e["contacts_jd"].items()}
    return e


def _to_jd(x) -> float:
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, datetime):
        return A.julian_day(x if x.tzinfo else x.replace(tzinfo=timezone.utc))
    if isinstance(x, date):
        return A.julian_day(datetime(x.year, x.month, x.day, tzinfo=timezone.utc))
    if isinstance(x, str):
        s = x.strip().replace("T", " ")
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return A.julian_day(datetime.strptime(s, fmt).replace(tzinfo=timezone.utc))
            except ValueError:
                pass
    raise ValueError("give an ISO date/datetime (UTC), a date/datetime object, or a Julian day number")


def eclipses_between(jd0, jd1, kind: Optional[str] = None, loc=None) -> List[Dict]:
    """All eclipses with greatest-eclipse time in [jd0, jd1] (UT Julian days, or dates). kind = 'solar' | 'lunar' | None.
    With loc (a Location) every eclipse also carries a `visibility` block for that place."""
    jd0, jd1 = _to_jd(jd0), _to_jd(jd1)
    out: List[Dict] = []
    elong = _elong(jd0 - 1.0)
    # first syzygy of either kind at or after jd0 - 1 day
    phase = 0.0 if A.norm360(180.0 - elong) > A.norm360(360.0 - elong) else 180.0
    to_next = A.norm360(phase - elong)
    jd = _syzygy_near(jd0 - 1.0 + to_next / MOON_RATE, phase)
    while jd <= jd1 + 1.0:
        if phase == 0.0 and kind in (None, "solar"):
            e = _solar(jd)
        elif phase == 180.0 and kind in (None, "lunar"):
            e = _lunar(jd)
        else:
            e = None
        if e is not None and jd0 <= e["jd_ut"] <= jd1:
            _finish(e)
            if loc is not None:
                e["visibility"] = visibility(e, loc)
            out.append(e)
        phase = 180.0 if phase == 0.0 else 0.0
        jd = _syzygy_near(jd + SYNODIC / 2.0, phase)
    return out


def eclipses_in_year(year: int, kind: Optional[str] = None, loc=None) -> List[Dict]:
    """All eclipses of a (proleptic Gregorian, UTC) year, 1-9999."""
    if not 1 <= int(year) <= 9999:
        raise ValueError("year must be 1..9999")
    j0 = A.julian_day(datetime(int(year), 1, 1, tzinfo=timezone.utc))
    j1 = A.julian_day(datetime(int(year), 12, 31, 23, 59, 59, tzinfo=timezone.utc))
    return eclipses_between(j0, j1, kind, loc)


def next_eclipses(when, count: int = 4, kind: Optional[str] = None, loc=None) -> List[Dict]:
    """The next `count` eclipses after a date/datetime (UTC) or Julian day."""
    jd = _to_jd(when)
    out: List[Dict] = []
    for _ in range(80):                         # at most ~40 years ahead
        out.extend(e for e in eclipses_between(jd, jd + 182.0, kind, loc) if e["jd_ut"] > _to_jd(when))
        jd += 182.0
        if len(out) >= count:
            break
    out.sort(key=lambda e: e["jd_ut"])
    seen, uniq = set(), []
    for e in out:
        if e["utc"] + e["kind"] not in seen:
            seen.add(e["utc"] + e["kind"])
            uniq.append(e)
    return uniq[:count]


# ------------------------------------------------------------------ local visibility
def _vec_geo(jd: float) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """Geocentric equatorial position vectors (km) of the Moon and the Sun."""
    st = _state(jd)
    eps = A.mean_obliquity(st["T"]) * DEG
    ce, se = math.cos(eps), math.sin(eps)

    def eq(lon, lat, r):
        lo, la = lon * DEG, lat * DEG
        xe, ye, ze = r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la)
        return xe, ye * ce - ze * se, ye * se + ze * ce
    return eq(st["moon"], st["beta"], st["dist"]), eq(st["sun"], 0.0, st["rs"] * AU_KM)


def _observer(jd: float, lat: float, lon_east: float):
    """Observer position (km, equatorial) and the local vertical (unit), sea level."""
    th = (A.gmst(jd) + lon_east) * DEG
    phi = lat * DEG
    u = math.atan(0.99664719 * math.tan(phi))
    rs_, rc_ = 0.99664719 * math.sin(u), math.cos(u)
    pos = (RE_KM * rc_ * math.cos(th), RE_KM * rc_ * math.sin(th), RE_KM * rs_)
    up = (math.cos(phi) * math.cos(th), math.cos(phi) * math.sin(th), math.sin(phi))
    return pos, up


def _norm(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def _topo(jd: float, lat: float, lon_east: float) -> Dict[str, float]:
    mv, sv = _vec_geo(jd)
    pos, up = _observer(jd, lat, lon_east)
    tm = (mv[0] - pos[0], mv[1] - pos[1], mv[2] - pos[2])
    ts = (sv[0] - pos[0], sv[1] - pos[1], sv[2] - pos[2])
    dm, ds = _norm(tm), _norm(ts)
    cr = (tm[1] * ts[2] - tm[2] * ts[1], tm[2] * ts[0] - tm[0] * ts[2], tm[0] * ts[1] - tm[1] * ts[0])
    dot = tm[0] * ts[0] + tm[1] * ts[1] + tm[2] * ts[2]
    sep = math.degrees(math.atan2(_norm(cr), dot))
    alt_m = math.degrees(math.asin((tm[0] * up[0] + tm[1] * up[1] + tm[2] * up[2]) / dm))
    alt_s = math.degrees(math.asin((ts[0] * up[0] + ts[1] * up[1] + ts[2] * up[2]) / ds))
    return {"sep": sep, "alt_moon": alt_m, "alt_sun": alt_s,
            "s_moon": math.degrees(math.asin(R_MOON_KM / dm)), "s_sun": math.degrees(math.asin(R_SUN_KM / ds))}


def _obscuration(sep: float, rs: float, rm: float) -> float:
    """Fraction of the Sun's disc covered (rs, rm = apparent radii, sep = centre separation, same units)."""
    if sep >= rs + rm:
        return 0.0
    if sep <= abs(rs - rm):
        return 1.0 if rm >= rs else (rm * rm) / (rs * rs)
    a = rs * rs * math.acos((sep * sep + rs * rs - rm * rm) / (2 * sep * rs))
    b = rm * rm * math.acos((sep * sep + rm * rm - rs * rs) / (2 * sep * rm))
    c = 0.5 * math.sqrt((-sep + rs + rm) * (sep + rs - rm) * (sep - rs + rm) * (sep + rs + rm))
    return (a + b - c) / (math.pi * rs * rs)


_HORIZON = -0.8333        # Sun's centre at sunrise/sunset (refraction + semi-diameter)


def _fmt_local(jd: float, loc) -> str:
    return A.format_jd(jd, loc.tz, "%Y-%m-%d %H:%M")


def visibility(ecl: Dict, loc) -> Dict:
    """Is this eclipse visible from the place `loc` (a Location)? Solar: full topocentric circumstances (parallax included).
    Lunar: whether the Moon is above the horizon during the phases. Times are given in UTC and in the place's local time."""
    if ecl["kind"] == "lunar":
        return _lunar_visibility(ecl, loc)
    return _solar_visibility(ecl, loc)


def _solar_visibility(ecl: Dict, loc) -> Dict:
    jd0 = ecl["jd_ut"]
    step = 5.0 / 1440.0
    n = int(0.3 / step)
    rows = []
    for i in range(-n, n + 1):
        t = jd0 + i * step
        r = _topo(t, loc.lat, loc.lon)
        r["t"] = t
        rows.append(r)
    occurs = [r for r in rows if r["sep"] < r["s_sun"] + r["s_moon"]]
    if not occurs:
        return {"visible": False, "occurs_at_place": False,
                "summary": {"en": "No eclipse at all from this place (the Moon's shadow does not reach it).",
                            "bn": "এই জায়গা থেকে কোনো গ্রহণ দেখা যাবে না (চাঁদের ছায়া এখানে পৌঁছায় না)।",
                            "hi": "इस स्थान से कोई ग्रहण नहीं दिखेगा (चंद्रमा की छाया यहाँ नहीं पहुँचती)।"}}
    up_rows = [r for r in occurs if r["alt_sun"] > _HORIZON]
    allmin = min(occurs, key=lambda r: r["sep"])

    def refine(center):
        f = lambda t: _topo(t, loc.lat, loc.lon)["sep"]
        t = _golden_min(f, center["t"] - step, center["t"] + step, 1e-6)
        r = _topo(t, loc.lat, loc.lon)
        r["t"] = t
        return r
    true_max = refine(allmin)
    first, last = occurs[0]["t"], occurs[-1]["t"]

    def edge(lo, hi, want_in):          # bisection for first/last contact between a sample outside and one inside
        for _ in range(30):
            m = (lo + hi) / 2.0
            r = _topo(m, loc.lat, loc.lon)
            inside = r["sep"] < r["s_sun"] + r["s_moon"]
            if inside == want_in:
                hi = m
            else:
                lo = m
        return (lo + hi) / 2.0
    c1 = edge(first - step, first, True) if first > rows[0]["t"] else None
    c4 = edge(last, last + step, False) if last < rows[-1]["t"] else None

    def block(r):
        mag = max(0.0, (r["s_sun"] + r["s_moon"] - r["sep"]) / (2.0 * r["s_sun"]))
        return {"time_utc": A.format_jd(r["t"], fmt="%Y-%m-%d %H:%M"), "time_local": _fmt_local(r["t"], loc),
                "magnitude": round(mag, 3), "obscuration": round(_obscuration(r["sep"], r["s_sun"], r["s_moon"]), 3),
                "sun_altitude_deg": round(r["alt_sun"], 1)}
    out: Dict = {"occurs_at_place": True, "visible": bool(up_rows)}
    out["greatest_at_place"] = block(true_max)
    out["sun_up_at_greatest"] = true_max["alt_sun"] > _HORIZON
    if c1 is not None:
        out["first_contact_utc"] = A.format_jd(c1, fmt="%Y-%m-%d %H:%M")
        out["first_contact_local"] = _fmt_local(c1, loc)
    if c4 is not None:
        out["last_contact_utc"] = A.format_jd(c4, fmt="%Y-%m-%d %H:%M")
        out["last_contact_local"] = _fmt_local(c4, loc)
    if up_rows and not out["sun_up_at_greatest"]:
        vis = refine(min(up_rows, key=lambda r: r["sep"]))
        out["best_visible"] = block(vis)
        out["note"] = "The Sun is below the horizon at the local maximum; only part of the eclipse is visible (around sunrise or sunset)."
    if not up_rows:
        out["note"] = "The eclipse happens here while the Sun is below the horizon, so it cannot be seen."
    if out["visible"]:
        m = out["greatest_at_place"] if out["sun_up_at_greatest"] else out["best_visible"]
        mg = m["magnitude"]
        out["summary"] = {"en": f"Visible here; about {round(m['obscuration'] * 100)}% of the Sun covered at its best (magnitude {mg}).",
                          "bn": f"এখান থেকে দেখা যাবে; সর্বোচ্চ প্রায় {round(m['obscuration'] * 100)}% সূর্য ঢাকা পড়বে (ম্যাগনিটিউড {mg})।",
                          "hi": f"यहाँ से दिखेगा; अधिकतम लगभग {round(m['obscuration'] * 100)}% सूर्य ढका होगा (परिमाण {mg})।"}
    else:
        out["summary"] = {"en": "Not visible from this place (the Sun is below the horizon during the eclipse).",
                          "bn": "এই জায়গা থেকে দেখা যাবে না (গ্রহণের সময় সূর্য দিগন্তের নিচে)।",
                          "hi": "इस स्थान से नहीं दिखेगा (ग्रहण के समय सूर्य क्षितिज के नीचे रहेगा)।"}
    return out


def _lunar_visibility(ecl: Dict, loc) -> Dict:
    jd = ecl["jd_ut"]
    contacts = ecl.get("contacts_jd") or {}
    t_start = contacts.get("P1", jd - 0.1)
    t_end = contacts.get("P4", jd + 0.1)
    alt_max = _topo(jd, loc.lat, loc.lon)["alt_moon"]
    step = 5.0 / 1440.0
    n = int((t_end - t_start) / step) + 1
    ups = [_topo(t_start + i * step, loc.lat, loc.lon)["alt_moon"] > 0.0 for i in range(n + 1)]
    phases = {}
    for k, v in contacts.items():
        phases[k] = {"time_utc": A.format_jd(v, fmt="%Y-%m-%d %H:%M"), "time_local": _fmt_local(v, loc),
                     "moon_up": _topo(v, loc.lat, loc.lon)["alt_moon"] > 0.0}
    vis_max = alt_max > 0.0
    any_up = any(ups)
    all_up = all(ups)
    out = {"visible": any_up, "moon_up_at_greatest": vis_max, "moon_altitude_at_greatest_deg": round(alt_max, 1),
           "greatest_local": _fmt_local(jd, loc), "moon_up_all_the_time": all_up,
           "moon_rises_or_sets_during_eclipse": any_up and not all_up, "phases": phases}
    if all_up:
        s = ("Entire eclipse visible (Moon above the horizon throughout).", "পুরো গ্রহণ দেখা যাবে (পুরো সময় চাঁদ দিগন্তের উপরে)।",
             "पूरा ग्रहण दिखेगा (पूरे समय चंद्रमा क्षितिज के ऊपर)।")
    elif any_up:
        s = ("Partly visible: the Moon rises or sets during the eclipse.", "আংশিক দেখা যাবে: গ্রহণ চলাকালীন চাঁদ উঠবে বা ডুববে।",
             "आंशिक दिखेगा: ग्रहण के दौरान चंद्रमा उगेगा या अस्त होगा।")
    else:
        s = ("Not visible from this place (the Moon is below the horizon).", "এই জায়গা থেকে দেখা যাবে না (চাঁদ দিগন্তের নিচে)।",
             "इस स्थान से नहीं दिखेगा (चंद्रमा क्षितिज के नीचे है)।")
    out["summary"] = {"en": s[0], "bn": s[1], "hi": s[2]}
    return out


# ------------------------------------------------------------------ kundli helpers
def grahan_dosha(sun: float, moon: float, rahu: float, ketu: Optional[float] = None, orb: float = 12.0) -> Dict:
    """Classical Grahan yoga/dosha from SIDEREAL longitudes: Sun (Surya Grahan) or Moon (Chandra Grahan) joined with Rahu or Ketu.
    `present` = within `orb` degrees (default 12); `same_sign` = in the same rashi (the broader traditional rule)."""
    ketu = A.norm360(rahu + 180.0) if ketu is None else ketu

    def check(lon):
        best = None
        for name, nl in (("Rahu", rahu), ("Ketu", ketu)):
            dist = abs(A.norm180(lon - nl))
            same = int(lon // 30) % 12 == int(nl // 30) % 12
            if best is None or dist < best["distance_deg"]:
                best = {"node": name, "distance_deg": round(dist, 2), "same_sign": same}
        best["within_orb"] = best["distance_deg"] <= orb
        return best
    s, m = check(sun), check(moon)
    present = s["within_orb"] or m["within_orb"]
    kinds = []
    if s["within_orb"]:
        kinds.append("Surya Grahan dosha (Sun with %s)" % s["node"])
    if m["within_orb"]:
        kinds.append("Chandra Grahan dosha (Moon with %s)" % m["node"])
    return {"present": present, "sun": s, "moon": m, "orb_deg": orb, "kinds": kinds,
            "same_sign_only": (not present) and (s["same_sign"] or m["same_sign"]),
            "note": {"en": "Traditional yoga: Sun or Moon conjunct Rahu/Ketu. Its effects are a matter of tradition, not proven science.",
                     "bn": "ঐতিহ্যগত যোগ: সূর্য বা চন্দ্র রাহু/কেতুর সাথে যুক্ত। এর ফল ঐতিহ্যের কথা, প্রমাণিত বিজ্ঞান নয়।",
                     "hi": "पारंपरिक योग: सूर्य या चंद्र राहु/केतु के साथ। इसके फल परंपरा की बात हैं, प्रमाणित विज्ञान नहीं।"}}


def eclipse_near_birth(jd_birth: float, loc=None) -> Dict:
    """The eclipse just before and just after a birth (any type), with days apart and the rashi/nakshatra of the eclipsed luminary."""
    jd = _to_jd(jd_birth)
    span = 200.0
    ecl: List[Dict] = []
    for _ in range(4):
        ecl = eclipses_between(jd - span, jd + span, None, loc)
        if any(e["jd_ut"] < jd for e in ecl) and any(e["jd_ut"] >= jd for e in ecl):
            break
        span += 100.0
    before = [e for e in ecl if e["jd_ut"] < jd]
    after = [e for e in ecl if e["jd_ut"] >= jd]
    out: Dict = {}
    if before:
        e = before[-1]
        out["before"] = {**e, "days_before_birth": round(jd - e["jd_ut"], 1)}
    if after:
        e = after[0]
        out["after"] = {**e, "days_after_birth": round(e["jd_ut"] - jd, 1)}
    near = min((out[k] for k in out), key=lambda x: abs(x["jd_ut"] - jd), default=None)
    out["born_within_15_days_of_eclipse"] = bool(near and abs(near["jd_ut"] - jd) <= 15.0)
    return out
