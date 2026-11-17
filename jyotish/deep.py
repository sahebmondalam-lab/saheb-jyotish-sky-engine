# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Deeper classical Jyotish layers computed from a built chart:
 - Shodashavarga: the 16 Parashari divisional charts (D1 ... D60)
 - Ashtakavarga: Bhinnashtakavarga (7 planets) and Sarvashtakavarga (tables of Brihat Parashara Hora Shastra)
 - Jaimini chara karakas (7-karaka scheme)
 - Bhava (house) lords and where they sit
Everything is rule-based arithmetic on the sidereal longitudes; the meanings are traditional, not scientific.
"""
from __future__ import annotations

from typing import Dict, List

from .data import RASHI_LORD

PLANETS7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
VARGAS = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]


def _odd(sign: int) -> bool:          # Aries, Gemini, Leo ... are "odd" (masculine) signs
    return sign % 2 == 0


def varga_sign(lon: float, n: int) -> int:
    """Sign (0=Aries) of a sidereal longitude in the Dn divisional chart (Parashara rules)."""
    s = int(lon // 30) % 12
    d = lon % 30.0
    movable, fixed = s % 3 == 0, s % 3 == 1
    elem = s % 4                      # 0 fire, 1 earth, 2 air, 3 water
    if n == 1:
        return s
    if n == 2:                        # hora: odd sign Sun(Leo) then Moon(Cancer); even sign reversed
        first = d < 15
        return 4 if first == _odd(s) else 3
    if n == 3:
        return (s + int(d // 10) * 4) % 12
    if n == 4:
        return (s + int(d // 7.5) * 3) % 12
    if n == 7:
        return ((s if _odd(s) else s + 6) + int(d / (30.0 / 7))) % 12
    if n == 9:
        return ({0: 0, 1: 9, 2: 6, 3: 3}[elem] + int(d / (30.0 / 9))) % 12
    if n == 10:
        return ((s if _odd(s) else s + 8) + int(d // 3)) % 12
    if n == 12:
        return (s + int(d // 2.5)) % 12
    if n == 16:
        return ((0 if movable else 4 if fixed else 8) + int(d / (30.0 / 16))) % 12
    if n == 20:
        return ((0 if movable else 8 if fixed else 4) + int(d // 1.5)) % 12
    if n == 24:
        return ((4 if _odd(s) else 3) + int(d // 1.25)) % 12
    if n == 27:
        return ({0: 0, 1: 3, 2: 6, 3: 9}[elem] + int(d / (30.0 / 27))) % 12
    if n == 30:                       # Trimsamsa (unequal parts)
        if _odd(s):
            for lim, sg in ((5, 0), (10, 10), (18, 8), (25, 2), (30, 6)):
                if d < lim:
                    return sg
        else:
            for lim, sg in ((5, 1), (12, 5), (20, 11), (25, 9), (30, 7)):
                if d < lim:
                    return sg
        return s
    if n == 40:
        return ((0 if _odd(s) else 6) + int(d / 0.75)) % 12
    if n == 45:
        return ((0 if movable else 4 if fixed else 8) + int(d / (30.0 / 45))) % 12
    if n == 60:
        return (s + int(d * 2)) % 12
    raise ValueError(f"unsupported divisional chart D{n}")


def vargas(chart: Dict) -> Dict[int, Dict]:
    out = {}
    for n in VARGAS:
        out[n] = {"lagna": varga_sign(chart["lagna"]["sidereal"], n),
                  "planets": {g: varga_sign(p["sidereal"], n) for g, p in chart["planets"].items()}}
    return out


def vargottama(chart: Dict) -> List[str]:
    """Planets in the same sign in the rashi (D1) and navamsa (D9) charts."""
    return [g for g, p in chart["planets"].items() if varga_sign(p["sidereal"], 9) == p["sign"]]


# Benefic houses counted from each contributor (7 planets + Lagna), Brihat Parashara Hora Shastra.
_BAV = {
    "Sun": {"Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
            "Mercury": [3, 5, 6, 9, 10, 11, 12], "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
            "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [3, 4, 6, 10, 11, 12]},
    "Moon": {"Sun": [3, 6, 7, 8, 10, 11], "Moon": [1, 3, 6, 7, 10, 11], "Mars": [2, 3, 5, 6, 9, 10, 11],
             "Mercury": [1, 3, 4, 5, 7, 8, 10, 11], "Jupiter": [1, 4, 7, 8, 10, 11, 12],
             "Venus": [3, 4, 5, 7, 9, 10, 11], "Saturn": [3, 5, 6, 11], "Lagna": [3, 6, 10, 11]},
    "Mars": {"Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
             "Mercury": [3, 5, 6, 11], "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12],
             "Saturn": [1, 4, 7, 8, 9, 10, 11], "Lagna": [1, 3, 6, 10, 11]},
    "Mercury": {"Sun": [5, 6, 9, 11, 12], "Moon": [2, 4, 6, 8, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
                "Mercury": [1, 3, 5, 6, 9, 10, 11, 12], "Jupiter": [6, 8, 11, 12],
                "Venus": [1, 2, 3, 4, 5, 8, 9, 11], "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
                "Lagna": [1, 2, 4, 6, 8, 10, 11]},
    "Jupiter": {"Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11], "Moon": [2, 5, 7, 9, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
                "Mercury": [1, 2, 4, 5, 6, 9, 10, 11], "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
                "Venus": [2, 5, 6, 9, 10, 11], "Saturn": [3, 5, 6, 12], "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11]},
    "Venus": {"Sun": [8, 11, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12], "Mars": [3, 5, 6, 9, 11, 12],
              "Mercury": [3, 5, 6, 9, 11], "Jupiter": [5, 8, 9, 10, 11], "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
              "Saturn": [3, 4, 5, 8, 9, 10, 11], "Lagna": [1, 2, 3, 4, 5, 8, 9, 11]},
    "Saturn": {"Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11], "Mars": [3, 5, 6, 10, 11, 12],
               "Mercury": [6, 8, 9, 10, 11, 12], "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12],
               "Saturn": [3, 5, 6, 11], "Lagna": [1, 3, 4, 6, 10, 11]},
}
BAV_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54, "Jupiter": 56, "Venus": 52, "Saturn": 39}   # classical totals


def ashtakavarga(chart: Dict) -> Dict:
    base = {g: chart["planets"][g]["sign"] for g in PLANETS7}
    base["Lagna"] = chart["lagna"]["sign"]
    bav: Dict[str, List[int]] = {}
    for target, rows in _BAV.items():
        pts = [0] * 12
        for contributor, houses in rows.items():
            for h in houses:
                pts[(base[contributor] + h - 1) % 12] += 1
        bav[target] = pts
    sav = [sum(bav[g][s] for g in PLANETS7) for s in range(12)]
    return {"bav": bav, "sav": sav, "total": sum(sav)}


def chara_karakas(chart: Dict) -> Dict[str, str]:
    """Jaimini 7-karaka scheme: Sun..Saturn ranked by degree within their sign, highest first."""
    ranked = sorted(PLANETS7, key=lambda g: -(chart["planets"][g]["sidereal"] % 30.0))
    return dict(zip(["AK", "AmK", "BK", "MK", "PK", "GK", "DK"], ranked))


def house_lords(chart: Dict) -> List[Dict]:
    out = []
    lag = chart["lagna"]["sign"]
    for h in range(1, 13):
        sign = (lag + h - 1) % 12
        lord = RASHI_LORD[sign]
        lp = chart["planets"][lord]
        out.append({"house": h, "sign": sign, "lord": lord, "lord_sign": lp["sign"], "lord_house": lp["house"],
                    "occupants": list(chart["houses"][h]["planets"]), "sav": None})
    return out


def analyse(chart: Dict) -> Dict:
    ak = ashtakavarga(chart)
    hl = house_lords(chart)
    for row in hl:
        row["sav"] = ak["sav"][row["sign"]]
    return {"vargas": vargas(chart), "vargottama": vargottama(chart), "ashtakavarga": ak,
            "karakas": chara_karakas(chart), "house_lords": hl}
