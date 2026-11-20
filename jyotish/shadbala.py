# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Shadbala: the six-fold strength of the seven planets (Sun ... Saturn) after Brihat Parashara Hora Shastra ch. 27.

Components (all in virupas, 60 virupas = 1 rupa):
  Sthana (position): Uccha, Saptavargaja, Ojhayugma, Kendradi, Drekkana
  Dig (direction), Kala (time): Natonnata, Paksha, Tribhaga, Abda, Masa, Vara, Hora, Ayana  (Yuddha is not computed)
  Cheshta (motion), Naisargika (natural), Drik (aspect)
The minimum totals for a planet to count as strong are 390, 360, 300, 420, 390, 330, 300 virupas (Sun ... Saturn).

Honest status: the formulas follow the classical text and its common translations, but I could not compare the totals with a
commercial program. Where translations or programs differ (Abda/Masa lord, Cheshta Kendra, Mercury as benefic, Sun's Ayana bala doubling,
Yuddha) the choice made is written in docs/ACCURACY.md. Use the numbers to compare planets within one chart, not as exact values.
"""
from __future__ import annotations

import math
from datetime import timedelta
from typing import Dict, List, Optional

from . import astro as A
from . import data as D
from . import deep
from . import hindu_calendar as H
from . import panchang as P

PLANETS7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
MIN_VIRUPA = {"Sun": 390.0, "Moon": 360.0, "Mars": 300.0, "Mercury": 420.0, "Jupiter": 390.0, "Venus": 330.0, "Saturn": 300.0}
NAISARGIKA = {"Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29, "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}
COMPONENTS = ("sthana", "dig", "kala", "cheshta", "naisargika", "drik")

_DEBIL_POINT = {"Sun": 190.0, "Moon": 213.0, "Mars": 118.0, "Mercury": 345.0, "Jupiter": 275.0, "Venus": 177.0, "Saturn": 20.0}
_MOOLA = {"Sun": (4, 0, 20), "Moon": (1, 3, 30), "Mars": (0, 0, 12), "Mercury": (5, 16, 20), "Jupiter": (8, 0, 10),
          "Venus": (6, 0, 15), "Saturn": (10, 0, 20)}      # sign, from degree, to degree
_FRIEND = {"Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"}, "Mars": {"Sun", "Moon", "Jupiter"},
           "Mercury": {"Sun", "Venus"}, "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"}, "Saturn": {"Mercury", "Venus"}}
_ENEMY = {"Sun": {"Venus", "Saturn"}, "Moon": set(), "Mars": {"Mercury"}, "Mercury": {"Moon"},
          "Jupiter": {"Mercury", "Venus"}, "Venus": {"Sun", "Moon"}, "Saturn": {"Sun", "Moon", "Mars"}}
_SAPTA_POINTS = {"adhi_mitra": 22.5, "mitra": 15.0, "sama": 7.5, "shatru": 3.75, "adhi_shatru": 1.875}
_SAPTA_VARGAS = (1, 2, 3, 7, 9, 12, 30)
_BENEFICS = {"Jupiter", "Venus"}
_HORA_SEQ = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]    # descending order of the planetary spheres


def _arc(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return 360.0 - d if d > 180.0 else d


def _compound(p: str, q_sign: int, planets: Dict[str, Dict]) -> str:
    """Compound (natural + temporary) relation of planet p to the lord of a sign."""
    lord = D.RASHI_LORD[q_sign]
    nat = "friend" if lord in _FRIEND[p] else "enemy" if lord in _ENEMY[p] else "neutral"
    d = (planets[lord]["sign"] - planets[p]["sign"]) % 12 + 1
    temp = "friend" if d in (2, 3, 4, 10, 11, 12) else "enemy"
    return {("friend", "friend"): "adhi_mitra", ("friend", "enemy"): "sama", ("neutral", "friend"): "mitra",
            ("neutral", "enemy"): "shatru", ("enemy", "friend"): "sama", ("enemy", "enemy"): "adhi_shatru"}[(nat, temp)]


# ------------------------------------------------------------------------------------------------------------------ sthana
def _saptavargaja(p: str, planets: Dict[str, Dict]) -> float:
    lon = planets[p]["sidereal"]
    tot = 0.0
    for n in _SAPTA_VARGAS:
        s = deep.varga_sign(lon, n)
        if D.RASHI_LORD[s] == p:
            ms, a, b = _MOOLA[p]
            tot += 45.0 if (n == 1 and s == ms and a <= lon % 30 < b) else 30.0
        elif p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
            tot += _SAPTA_POINTS[_compound(p, s, planets)]
    return tot


def _sthana(p: str, planets: Dict[str, Dict]) -> Dict[str, float]:
    pl = planets[p]
    lon = pl["sidereal"]
    uccha = _arc(lon, _DEBIL_POINT[p]) / 3.0
    sapta = _saptavargaja(p, planets)
    even_strong = p in ("Moon", "Venus")
    odd_rashi = pl["sign"] % 2 == 0
    odd_nav = pl["navamsa"] % 2 == 0
    oy = (15.0 if (odd_rashi != even_strong) else 0.0) + (15.0 if (odd_nav != even_strong) else 0.0)
    kendradi = {1: 60.0, 4: 60.0, 7: 60.0, 10: 60.0, 2: 30.0, 5: 30.0, 8: 30.0, 11: 30.0}.get(pl["house"], 15.0)
    dr = int((lon % 30.0) // 10)
    want = 0 if p in ("Sun", "Mars", "Jupiter") else 1 if p in ("Mercury", "Saturn") else 2
    drekkana = 15.0 if dr == want else 0.0
    return {"uccha": uccha, "saptavargaja": sapta, "ojhayugma": oy, "kendradi": kendradi, "drekkana": drekkana,
            "total": uccha + sapta + oy + kendradi + drekkana}


# --------------------------------------------------------------------------------------------------------------------- dig
def _dig(p: str, asc: float, mc: float, planets: Dict[str, Dict]) -> float:
    lon = planets[p]["sidereal"]
    if p in ("Jupiter", "Mercury"):
        weak = asc + 180.0           # strong in the 1st house, powerless at the 7th cusp
    elif p in ("Sun", "Mars"):
        weak = mc + 180.0            # strong in the 10th, powerless at the 4th cusp
    elif p == "Saturn":
        weak = asc                   # strong in the 7th, powerless at the lagna
    else:
        weak = mc                    # Moon, Venus: strong in the 4th, powerless at the 10th cusp
    return _arc(lon, weak % 360.0) / 3.0


# --------------------------------------------------------------------------------------------------------------------- kala
def _is_benefic(p: str, planets: Dict[str, Dict]) -> bool:
    if p in _BENEFICS:
        return True
    if p == "Moon":
        return (planets["Moon"]["sidereal"] - planets["Sun"]["sidereal"]) % 360.0 < 180.0     # bright half
    if p == "Mercury":
        return not any(planets[m]["sign"] == planets["Mercury"]["sign"] for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu"))
    return False


def _paksha(p: str, planets: Dict[str, Dict]) -> float:
    d = _arc(planets["Moon"]["sidereal"], planets["Sun"]["sidereal"]) / 3.0
    return d if (p == "Moon" or _is_benefic(p, planets)) else 60.0 - d      # the Moon is strongest at full moon, weakest at new moon


def _declination(lon_trop: float, lat: float, eps: float) -> float:
    sd = (math.sin(math.radians(lat)) * math.cos(math.radians(eps))
          + math.cos(math.radians(lat)) * math.sin(math.radians(eps)) * math.sin(math.radians(lon_trop)))
    return math.degrees(math.asin(max(-1.0, min(1.0, sd))))


def _ayana(p: str, planets: Dict[str, Dict], T: float) -> float:
    eps = 23.0 + 27.0 / 60.0
    lat = 0.0
    if p == "Moon":
        from .eclipses import moon_lat_dist
        lat = moon_lat_dist(T)[0]
    dec = _declination(planets[p]["tropical"], lat, eps)
    if p in ("Moon", "Saturn"):
        v = 30.0 * (eps - dec) / eps
    elif p == "Mercury":
        v = 30.0 * (eps + abs(dec)) / eps
    else:
        v = 30.0 * (eps + dec) / eps
    return max(0.0, min(60.0, v))


def _weekday_after(jd_start: float, loc) -> int:
    d0 = A.datetime_from_jd(jd_start).astimezone(loc.tz).date()
    for k in (0, 1, 2):
        t = P.day_times(d0 + timedelta(days=k), loc)
        if t.get("sunrise_jd") and t["sunrise_jd"] >= jd_start:
            return t["weekday"]
    return P.day_times(d0, loc)["weekday"]


def _year_and_month_lords(jd: float, loc) -> Dict[str, str]:
    m = H.lunar_month_at(jd)
    month_lord = D.VARA_LORD[_weekday_after(m["start_jd"], loc)]
    cur = m
    for _ in range(16):
        if cur["amanta"] == 0 and not cur["adhika"]:
            break
        cur = H.lunar_month_at(cur["start_jd"] - 1.0)
    year_lord = D.VARA_LORD[_weekday_after(cur["start_jd"], loc)]
    return {"abda": year_lord, "masa": month_lord}


def _kala(p: str, chart: Dict, planets: Dict[str, Dict], T: float, ctx: Dict) -> Dict[str, float]:
    jd = chart["meta"]["jd_ut"]
    nat = ctx["natonnata"][p]
    pak = _paksha(p, planets)
    trib = 60.0 if p == "Jupiter" or p == ctx["tribhaga_lord"] else 0.0
    abda = 15.0 if p == ctx["abda"] else 0.0
    masa = 30.0 if p == ctx["masa"] else 0.0
    vara = 45.0 if p == ctx["vara"] else 0.0
    hora = 60.0 if p == ctx["hora"] else 0.0
    ay = _ayana(p, planets, T)
    ay_used = ay * 2.0 if p == "Sun" else ay
    total = nat + pak + trib + abda + masa + vara + hora + ay_used
    return {"natonnata": nat, "paksha": pak, "tribhaga": trib, "abda": abda, "masa": masa, "vara": vara, "hora": hora,
            "ayana": ay_used, "yuddha": 0.0, "total": total, "_ayana_plain": ay}


def _time_context(chart: Dict, loc) -> Dict:
    jd = chart["meta"]["jd_ut"]
    local_dt = A.datetime_from_jd(jd).astimezone(loc.tz)
    d = local_dt.date()
    t = P.day_times(d, loc)
    rise, sset = t.get("sunrise_jd"), t.get("sunset_jd")
    if rise is None or sset is None:
        raise ValueError("no sunrise/sunset at this latitude and date (polar day or night): Shadbala needs them")
    if jd < rise:                       # before today's sunrise: the Vedic day is yesterday's
        t = P.day_times(d - timedelta(days=1), loc)
        prev_rise, prev_set = t["sunrise_jd"], t["sunset_jd"]
        next_rise = rise
        day_rise, day_set, wd = prev_rise, prev_set, t["weekday"]
    else:
        t_next = P.day_times(d + timedelta(days=1), loc)
        next_rise = t_next["sunrise_jd"]
        day_rise, day_set, wd = rise, sset, t["weekday"]
    is_day = day_rise <= jd < day_set
    noon = (day_rise + day_set) / 2.0
    midnight = (day_set + next_rise) / 2.0
    # hours from the nearest midnight
    h = min(abs(jd - midnight), abs(jd - (midnight - 1.0)), abs(jd - (midnight + 1.0))) * 24.0
    h = min(h, 12.0)
    night_planets = ("Moon", "Mars", "Saturn")
    nat = {}
    for p in PLANETS7:
        if p == "Mercury":
            nat[p] = 60.0
        elif p in night_planets:
            nat[p] = (12.0 - h) * 5.0
        else:
            nat[p] = h * 5.0
    # tribhaga: day / night split in three equal parts
    if is_day:
        part = int((jd - day_rise) / ((day_set - day_rise) / 3.0))
        lord = ("Mercury", "Sun", "Saturn")[min(part, 2)]
    else:
        n0 = day_set
        n1 = next_rise
        part = int((jd - n0) / ((n1 - n0) / 3.0))
        lord = ("Moon", "Venus", "Mars")[min(max(part, 0), 2)]
    # hora: 24 equal hours counted from sunrise, the first belonging to the weekday lord
    hours_from_rise = (jd - day_rise) * 24.0
    k = int(hours_from_rise)
    hora = _HORA_SEQ[(_HORA_SEQ.index(D.VARA_LORD[wd]) + k) % 7]
    lords = _year_and_month_lords(jd, loc)
    return {"natonnata": nat, "tribhaga_lord": lord, "vara": D.VARA_LORD[wd], "hora": hora, "is_day": is_day, **lords}


# ------------------------------------------------------------------------------------------------------------------ cheshta
def _mean_helio_trop(name: str, T: float) -> float:
    long_term = not (A.TABLE1_T0 <= T <= A.TABLE1_T1)
    el = (A._ELEMENTS_LONG if long_term else A._ELEMENTS)[name]
    return A.norm360(el[6] + el[7] * T + A.precession_deg(T))


def _cheshta(p: str, planets: Dict[str, Dict], T: float, ay_plain: float, paksha: float) -> float:
    if p == "Sun":
        return ay_plain                 # Sun: equal to his own (undoubled) Ayana bala
    if p == "Moon":
        return paksha
    mean_sun = A.norm360(280.46646 + 36000.76983 * T)
    helio = _mean_helio_trop(p, T)
    true = planets[p]["tropical"]
    if p in ("Mars", "Jupiter", "Saturn"):
        seeghra, madhya = mean_sun, helio
    else:                                # Mercury, Venus
        seeghra, madhya = helio, mean_sun
    mid = (true + madhya) / 2.0
    if abs(true - madhya) > 180.0:       # average across the 0/360 wrap
        mid += 180.0
    return _arc(seeghra, mid % 360.0) / 3.0


# --------------------------------------------------------------------------------------------------------------------- drik
_SPECIAL = {"Mars": (90.0, 210.0), "Jupiter": (120.0, 240.0), "Saturn": (60.0, 270.0)}


def _drishti(d: float, p: str) -> float:
    """Drishti (aspect) value in virupas of planet p on a point d degrees ahead of it: the classical piecewise-linear curve
    (0 below 30 deg, 15 at 60, 45 at 90, 30 at 120, 0 at 150, 60 at 180, 0 at 300) plus the special full aspects of Mars (4th, 8th),
    Jupiter (5th, 9th) and Saturn (3rd, 10th), modelled as a peak of 60 falling to 0 over 30 degrees."""
    d %= 360.0
    if d < 30:
        v = 0.0
    elif d < 60:
        v = (d - 30) / 2.0
    elif d < 90:
        v = d - 45.0
    elif d < 120:
        v = 30.0 + (120.0 - d) / 2.0
    elif d < 150:
        v = 150.0 - d
    elif d < 180:
        v = (d - 150.0) * 2.0
    elif d < 300:
        v = (300.0 - d) / 2.0
    else:
        v = 0.0
    for sp in _SPECIAL.get(p, ()):
        dd = abs((d - sp + 180.0) % 360.0 - 180.0)
        if dd < 30.0:
            v = max(v, 60.0 - 2.0 * dd)
    return v


def _drik(p: str, planets: Dict[str, Dict]) -> float:
    tot = 0.0
    target = planets[p]["sidereal"]
    for q in PLANETS7:
        if q == p:
            continue
        val = _drishti((target - planets[q]["sidereal"]) % 360.0, q)
        tot += val if _is_benefic(q, planets) else -val
    return tot / 4.0


# ------------------------------------------------------------------------------------------------------------------- public
def shadbala(chart: Dict, loc) -> Dict:
    """Shadbala of the seven planets for a chart made by chart.build_chart (needs the birth Location for sunrise and the hora)."""
    planets = chart["planets"]
    jd = chart["meta"]["jd_ut"]
    T = A.centuries(A.jd_to_tt(jd))
    asc = chart["lagna"]["sidereal"]
    ay = A.ayanamsa_lahiri(A.jd_to_tt(jd))
    mc = A.norm360(A.midheaven_tropical(jd, loc.lon) - ay)
    ctx = _time_context(chart, loc)
    rows = []
    for p in PLANETS7:
        st = _sthana(p, planets)
        dg = _dig(p, asc, mc, planets)
        kl = _kala(p, chart, planets, T, ctx)
        ch = _cheshta(p, planets, T, kl["_ayana_plain"], kl["paksha"])
        nai = NAISARGIKA[p]
        dk = _drik(p, planets)
        total = st["total"] + dg + kl["total"] + ch + nai + dk
        need = MIN_VIRUPA[p]
        kl.pop("_ayana_plain")
        rows.append({
            "planet": p, "sthana": st, "dig": dg, "kala": kl, "cheshta": ch, "naisargika": nai, "drik": dk,
            "total_virupa": total, "total_rupa": total / 60.0, "required_virupa": need, "required_rupa": need / 60.0,
            "ratio": total / need, "strong": total >= need,
        })
    order = sorted(rows, key=lambda r: -r["ratio"])
    return {
        "unit": "virupa (60 virupa = 1 rupa)",
        "planets": rows,
        "ranking": [r["planet"] for r in order],
        "strongest": order[0]["planet"], "weakest": order[-1]["planet"],
        "context": {"day_birth": ctx["is_day"], "vara_lord": ctx["vara"], "hora_lord": ctx["hora"], "tribhaga_lord": ctx["tribhaga_lord"],
                    "abda_lord": ctx["abda"], "masa_lord": ctx["masa"]},
        "note": ("Classical Shadbala (BPHS ch.27). Yuddha bala is not included; Abda/Masa lords use the real lunar year/month start; "
                 "Cheshta uses the mean/true Seeghrochcha method. Not checked against a commercial program: treat as a comparison of the "
                 "planets within one chart. Traditional belief system, not science."),
    }
