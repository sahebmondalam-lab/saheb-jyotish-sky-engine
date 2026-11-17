# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Vimshottari dasha (120-year cycle) from the Moon's nakshatra."""
from __future__ import annotations

from typing import Dict, List, Optional

from .data import DASHA_ORDER, DASHA_YEARS

YEAR_DAYS = 365.25  # common convention; some schools use 360 or 365.2422
NAK_LEN = 360.0 / 27.0


def vimshottari(moon_sid: float, birth_jd_ut: float, span_years: float = 120.0) -> List[Dict]:
    idx = int(moon_sid // NAK_LEN)
    elapsed = (moon_sid % NAK_LEN) / NAK_LEN
    first = idx % 9
    start = birth_jd_ut - elapsed * DASHA_YEARS[DASHA_ORDER[first]] * YEAR_DAYS
    end_limit = birth_jd_ut + span_years * YEAR_DAYS
    periods: List[Dict] = []
    i, t = first, start
    while t < end_limit:
        lord = DASHA_ORDER[i % 9]
        dur = DASHA_YEARS[lord] * YEAR_DAYS
        antars, ta = [], t
        for k in range(9):
            sub = DASHA_ORDER[(i + k) % 9]
            ad = DASHA_YEARS[lord] * DASHA_YEARS[sub] / 120.0 * YEAR_DAYS
            antars.append({"lord": sub, "start": ta, "end": ta + ad})
            ta += ad
        periods.append({"lord": lord, "start": t, "end": t + dur, "antar": antars})
        t += dur
        i += 1
    return periods


def find_period(periods: List[Dict], jd: float) -> Optional[Dict]:
    for p in periods:
        if p["start"] <= jd < p["end"]:
            for a in p["antar"]:
                if a["start"] <= jd < a["end"]:
                    return {"maha": p, "antar": a}
    return None


def balance_at_birth(moon_sid: float) -> Dict:
    idx = int(moon_sid // NAK_LEN)
    elapsed = (moon_sid % NAK_LEN) / NAK_LEN
    lord = DASHA_ORDER[idx % 9]
    return {"lord": lord, "years_left": DASHA_YEARS[lord] * (1.0 - elapsed)}
