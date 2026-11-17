# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""What happens in the sky during one civil day: Moon-phase moments, sign changes (sankranti),
retrograde/direct stations, and the tithi / nakshatra / yoga timeline. Times are exact moments (UT Julian days).

Not included: eclipses (they need the Moon's latitude, which this engine does not compute).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Callable, Dict, List, Optional

from . import astro as A
from .location import Location
from .panchang import NAK_LEN, _nak_angle, _tithi_angle, _yoga_angle, next_boundary

STATION_BODIES = ("Mercury", "Venus", "Mars", "Jupiter", "Saturn")
_STEP = 1.0 / 24.0          # sample the day hourly, then bisect for the exact moment


def day_bounds(d: date, loc: Location):
    a = datetime(d.year, d.month, d.day, tzinfo=loc.tz)
    n = d + timedelta(days=1)
    b = datetime(n.year, n.month, n.day, tzinfo=loc.tz)
    return A.julian_day(a), A.julian_day(b)


def _bisect(f: Callable[[float], bool], lo: float, hi: float) -> float:
    """f(lo) is False, f(hi) is True; return the first moment f becomes True."""
    for _ in range(45):
        mid = (lo + hi) / 2.0
        if f(mid):
            hi = mid
        else:
            lo = mid
    return hi


def _inst_speed(body: str, jd: float) -> float:
    h = 0.05
    return A.norm180(A.tropical_longitude(body, jd + h) - A.tropical_longitude(body, jd - h)) / (2 * h)


def _elong(jd: float) -> float:
    return A.norm360(A.tropical_longitude("Moon", jd) - A.tropical_longitude("Sun", jd))


def _sign(body: str, jd: float) -> int:
    return int(A.sidereal_longitude(body, jd) // 30) % 12


def _samples(jd0: float, jd1: float) -> List[float]:
    n = int(round((jd1 - jd0) / _STEP))
    return [jd0 + (jd1 - jd0) * i / n for i in range(n + 1)]


def _previous_boundary(jd: float, f: Callable[[float], float], unit: float) -> float:
    base = int(f(jd) // unit)
    t = jd
    for _ in range(400):                       # look back up to 8 days
        t -= 0.02
        if int(f(t) // unit) != base:
            return _bisect(lambda x: int(f(x) // unit) == base, t, t + 0.02)
    return jd - 8.0


def _timeline(jd0: float, jd1: float, f: Callable[[float], float], unit: float, count: int) -> List[Dict]:
    """Segments {'index','start','end'} of tithi/nakshatra/yoga that overlap [jd0, jd1)."""
    idx = int(f(jd0) // unit) % count
    start = _previous_boundary(jd0, f, unit)
    t = jd0
    out = []
    while True:
        end = next_boundary(t, f, unit, max_days=4.0)
        out.append({"index": idx, "start": start, "end": end})
        if end is None or end >= jd1:
            break
        idx = (idx + 1) % count
        start, t = end, end + 1e-6
    return out


def day_events(d: date, loc: Location) -> Dict:
    jd0, jd1 = day_bounds(d, loc)
    pts = _samples(jd0, jd1)
    ev: Dict = {"from_jd": jd0, "to_jd": jd1, "ingresses": [], "stations": [], "moon_phases": []}

    # sign changes (sidereal), including the Moon and the nodes
    for g in A.GRAHAS:
        for a, b in zip(pts, pts[1:]):
            sa, sb = _sign(g, a), _sign(g, b)
            if sa != sb:
                t = _bisect(lambda x, sa=sa, g=g: _sign(g, x) != sa, a, b)
                ev["ingresses"].append({"planet": g, "jd": t, "from_sign": sa, "to_sign": sb,
                                        "backward": sb == (sa - 1) % 12})

    # stations: speed changes sign
    for g in STATION_BODIES:
        for a, b in zip(pts, pts[1:]):
            va, vb = _inst_speed(g, a), _inst_speed(g, b)
            if (va < 0) != (vb < 0):
                t = _bisect(lambda x, va=va, g=g: (_inst_speed(g, x) < 0) != (va < 0), a, b)
                ev["stations"].append({"planet": g, "jd": t, "turns": "retrograde" if vb < 0 else "direct"})

    # Moon quarters: elongation crosses 0, 90, 180, 270
    for a, b in zip(pts, pts[1:]):
        qa, qb = int(_elong(a) // 90) % 4, int(_elong(b) // 90) % 4
        if qa != qb:
            t = _bisect(lambda x, qa=qa: int(_elong(x) // 90) % 4 != qa, a, b)
            ev["moon_phases"].append({"phase_index": qb, "jd": t})        # 0 new, 1 first q, 2 full, 3 last q

    ev["tithi"] = _timeline(jd0, jd1, _tithi_angle, 12.0, 30)
    ev["nakshatra"] = _timeline(jd0, jd1, _nak_angle, NAK_LEN, 27)
    ev["yoga"] = _timeline(jd0, jd1, _yoga_angle, NAK_LEN, 27)
    for k in ("ingresses", "stations", "moon_phases"):
        ev[k].sort(key=lambda e: e["jd"])
    return ev
