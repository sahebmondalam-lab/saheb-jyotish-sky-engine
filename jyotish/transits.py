# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Gochar (transit) timeline: when slow planets change sign, Sade Sati, and houses from the natal Moon."""
from __future__ import annotations

from typing import Dict, List

from . import astro as A
from .data import GOCHAR_GOOD

SLOW = ("Saturn", "Jupiter", "Rahu", "Ketu")


def _sign(planet: str, jd: float) -> int:
    return int(A.sidereal_longitude(planet, jd) // 30) % 12


def sign_timeline(planet: str, start_jd: float, end_jd: float, step: float = 2.0) -> List[Dict]:
    """Segments {'start','end','sign'}; boundaries refined by bisection (retrograde re-entries included)."""
    segs: List[Dict] = []
    t = start_jd
    cur = _sign(planet, t)
    seg_start = t
    while t < end_jd:
        nxt = min(t + step, end_jd)
        s2 = _sign(planet, nxt)
        if s2 != cur:
            lo, hi = t, nxt
            for _ in range(30):
                mid = (lo + hi) / 2
                if _sign(planet, mid) == cur:
                    lo = mid
                else:
                    hi = mid
            segs.append({"start": seg_start, "end": hi, "sign": cur})
            seg_start, cur = hi, s2
        t = nxt
    segs.append({"start": seg_start, "end": end_jd, "sign": cur})
    return segs


def house_from_moon(sign: int, moon_sign: int) -> int:
    return (sign - moon_sign) % 12 + 1


def annotate(planet: str, segs: List[Dict], moon_sign: int) -> List[Dict]:
    good = GOCHAR_GOOD.get(planet, set())
    out = []
    for s in segs:
        h = house_from_moon(s["sign"], moon_sign)
        out.append({**s, "house_from_moon": h, "favourable": h in good})
    return out


def saturn_phases(start_jd: float, end_jd: float, moon_sign: int) -> List[Dict]:
    """Sade Sati (12/1/2) and Dhaiya (4/8) windows, merged where consecutive."""
    segs = annotate("Saturn", sign_timeline("Saturn", start_jd, end_jd), moon_sign)
    out: List[Dict] = []
    for s in segs:
        if s["house_from_moon"] in (12, 1, 2, 4, 8):
            kind = "sade_sati" if s["house_from_moon"] in (12, 1, 2) else "dhaiya"
            if out and out[-1]["house"] == s["house_from_moon"] and abs(out[-1]["end"] - s["start"]) < 1e-6:
                out[-1]["end"] = s["end"]
            else:
                out.append({"start": s["start"], "end": s["end"], "house": s["house_from_moon"], "kind": kind})
    return out


def current_gochar(jd: float, moon_sign: int) -> Dict[str, Dict]:
    """Where every planet is right now, as a house from the natal Moon."""
    res = {}
    for g in A.GRAHAS:
        sid = A.sidereal_longitude(g, jd)
        sign = int(sid // 30) % 12
        res[g] = {"sign": sign, "degree": sid % 30, "house_from_moon": house_from_moon(sign, moon_sign)}
    return res


def forecast(moon_sign: int, start_jd: float, years: float) -> Dict:
    end = start_jd + years * 365.25
    lines = {}
    for g in ("Saturn", "Jupiter", "Rahu"):
        lines[g] = annotate(g, sign_timeline(g, start_jd, end), moon_sign)
    return {"start": start_jd, "end": end, "timelines": lines,
            "saturn_phases": saturn_phases(start_jd, end, moon_sign)}
