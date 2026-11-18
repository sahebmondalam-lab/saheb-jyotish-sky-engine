# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Julian <-> Gregorian calendar conversion and date resolution.

History is written in the Julian calendar before the Gregorian reform of 15 October 1582 (and in many countries long after:
England 1752, Russia 1918, Greece 1923). The sky calculations here run on the proleptic Gregorian calendar, so an old date has to be
translated first. calendar = "auto" (Julian before 1582-10-15, Gregorian after), "julian" or "gregorian".
"""
from __future__ import annotations

from datetime import date
from typing import List, Tuple

from .parse import parse_ymd

REFORM = (1582, 10, 15)
CALENDARS = ("auto", "julian", "gregorian")


def jdn_julian(y: int, m: int, d: int) -> int:
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083


def jdn_gregorian(y: int, m: int, d: int) -> int:
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045


def gregorian_from_jdn(j: int) -> Tuple[int, int, int]:
    a = j + 32044
    b = (4 * a + 3) // 146097
    c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    return 100 * b + d - 4800 + m // 10, m + 3 - 12 * (m // 10), e - (153 * m + 2) // 5 + 1


def julian_from_jdn(j: int) -> Tuple[int, int, int]:
    c = j + 32082
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    return d - 4800 + m // 10, m + 3 - 12 * (m // 10), e - (153 * m + 2) // 5 + 1


def _julian_valid(y: int, m: int, d: int) -> bool:
    dim = [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return 1 <= d <= dim


def resolve_date(text, calendar: str = "auto", notes: List[str] = None) -> date:
    """Parse a date as written and return the matching proleptic-Gregorian date (what the engine works in)."""
    if isinstance(text, date):
        return text
    notes = notes if notes is not None else []
    cal = (calendar or "auto").lower()
    if cal not in CALENDARS:
        raise ValueError("calendar must be auto, julian or gregorian")
    y, m, d = parse_ymd(text, notes)
    use_julian = cal == "julian" or (cal == "auto" and (y, m, d) < REFORM)
    if use_julian:
        if not _julian_valid(y, m, d):
            raise ValueError(f"'{text}' is not a real Julian-calendar date.")
        g = gregorian_from_jdn(jdn_julian(y, m, d))
        if g[0] < 1:
            raise ValueError("Dates before 1 January 1 CE (Gregorian) are not supported yet; this engine covers years 1-9999.")
        notes.append(f"Date {y:04d}-{m:02d}-{d:02d} was read in the Julian calendar (used before 15 Oct 1582, or because you asked); it equals "
                     f"{g[0]:04d}-{g[1]:02d}-{g[2]:02d} in the proleptic Gregorian calendar, which every date in this result uses.")
        return date(*g)
    try:
        out = date(y, m, d)
    except ValueError:
        raise ValueError(f"'{text}' is not a real calendar date (Gregorian).") from None
    if cal == "auto" and 1583 <= y <= 1752:
        notes.append("Dates between 1583 and 1752 are read as Gregorian. If your source is Old Style (England and colonies before 1752, "
                     "Protestant Germany before 1700, Russia before 1918), say calendar=julian.")
    return out
