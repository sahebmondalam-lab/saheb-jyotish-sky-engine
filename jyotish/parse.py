# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Forgiving input parsing: dates and times as people actually write them, in English, Bengali or Hindi digits and words.

parse_date('27 Jan 1992') / ('27/01/1992') / ('১৯৯২-০১-২৭') / ('27 जनवरी 1992')   -> datetime.date
parse_time('10:30 PM') / ('রাত ১০:৩০') / ('शाम 6 बजे') / ('noon')                  -> (hour, minute, second)
Both raise ValueError with a clear message if the text cannot be understood. Ambiguous day/month order is read
day-first (the Indian convention) unless one number is above 12, and that is reported in the returned notes.
"""
from __future__ import annotations

import re
from datetime import date
from typing import List, Optional, Tuple

_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯०१२३४५६७८९", "01234567890123456789")

_MONTHS = {}
for _i, _names in enumerate([
    ("jan", "january", "জানুয়ারি", "জানুয়ারী", "जनवरी"), ("feb", "february", "ফেব্রুয়ারি", "ফেব্রুয়ারী", "फरवरी"),
    ("mar", "march", "মার্চ", "मार्च"), ("apr", "april", "এপ্রিল", "अप्रैल"), ("may", "মে", "मई"),
    ("jun", "june", "জুন", "जून"), ("jul", "july", "জুলাই", "जुलाई"), ("aug", "august", "আগস্ট", "অগাস্ট", "अगस्त"),
    ("sep", "sept", "september", "সেপ্টেম্বর", "सितंबर", "सितम्बर"), ("oct", "october", "অক্টোবর", "अक्टूबर"),
    ("nov", "november", "নভেম্বর", "नवंबर", "नवम्बर"), ("dec", "december", "ডিসেম্বর", "दिसंबर", "दिसम्बर")], 1):
    for _n in _names:
        _MONTHS[_n] = _i


def normalize(text: str) -> str:
    return str(text).translate(_DIGITS).strip()


def parse_date(text, notes: Optional[List[str]] = None) -> date:
    """Gregorian date as written (see calendars.resolve_date for Julian/old dates)."""
    if isinstance(text, date):
        return text
    y, m, d = parse_ymd(text, notes)
    return _mk(y, m, d, text)


def parse_ymd(text, notes: Optional[List[str]] = None):
    """Year, month, day exactly as written (calendar not checked)."""
    s = normalize(text)
    if not s:
        raise ValueError("date is empty")
    notes = notes if notes is not None else []
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        return _chk(int(m.group(1)), int(m.group(2)), int(m.group(3)), text)
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if b > 12 and a <= 12:
            notes.append(f"Date '{s}' read as MM/DD/YYYY because {b} cannot be a month.")
            return _chk(y, a, b, text)
        if a <= 12 and b <= 12 and a != b:
            notes.append(f"Date '{s}' is ambiguous; read as DD/MM/YYYY (day first). Say so if you meant month first.")
        return _chk(y, b, a, text)
    low = s.lower().replace(",", " ")
    low = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", low)
    tokens = low.split()
    day = month = year = None
    for t in tokens:
        if t in _MONTHS:
            month = _MONTHS[t]
        elif re.fullmatch(r"\d{4}", t):
            year = int(t)
        elif re.fullmatch(r"\d{1,2}", t):
            day = int(t)
    if day and month and year:
        return _chk(year, month, day, text)
    raise ValueError(f"Cannot understand date '{text}'. Use e.g. 1992-01-27, 27/01/1992 or 27 Jan 1992.")


def _chk(y: int, m: int, d: int, original):
    if not (1 <= m <= 12 and 1 <= d <= 31 and 1 <= y <= 9999):
        raise ValueError(f"'{original}' is not a real calendar date.")
    return y, m, d


def _mk(y: int, m: int, d: int, original) -> date:
    try:
        return date(y, m, d)
    except ValueError:
        raise ValueError(f"'{original}' is not a real calendar date.") from None


_UNKNOWN = {"unknown", "dontknow", "don'tknow", "na", "n/a", "none", "?", "অজানা", "জানি না", "জানা নেই", "पता नहीं", "अज्ञात"}


def is_unknown_time(text) -> bool:
    return text is None or str(text).strip().lower().replace(" ", "") in {u.replace(" ", "") for u in _UNKNOWN} or str(text).strip() == ""


def parse_time(text) -> Tuple[int, int, int]:
    s = normalize(text).lower()
    if s in ("noon", "midday", "দুপুর", "दोपहर"):
        return 12, 0, 0
    if s in ("midnight", "মধ্যরাত", "आधी रात"):
        return 0, 0, 0
    period = None
    for words, tag in ((("pm", "p.m.", "p.m", "evening", "সন্ধ্যা", "সন্ধ্যে", "विकেল", "বিকেল", "বিকাল", "शाम"), "eve"),
                       (("am", "a.m.", "a.m", "morning", "সকাল", "सुबह"), "am"),
                       (("রাত", "रात", "night"), "night"), (("দুপুর", "दोपहर", "afternoon"), "noon")):
        for w in words:
            if w in s:
                period = tag if period is None else period
                s = s.replace(w, " ")
    s = re.sub(r"(টায়|টা|बजे|hrs|hours|hour|hr|o'clock|\bh\b)", " ", s).strip()
    m = re.fullmatch(r"(\d{1,2})(?:[:.](\d{1,2}))?(?:[:.](\d{1,2}))?", re.sub(r"\s+", "", s))
    if not m:
        raise ValueError(f"Cannot understand time '{text}'. Use e.g. 14:30, 2:30 PM or 'রাত ১০:৩০'.")
    h, mi, sec = int(m.group(1)), int(m.group(2) or 0), int(m.group(3) or 0)
    if period == "am":
        h = 0 if h == 12 else h
    elif period == "eve":
        h = h + 12 if h < 12 else h
    elif period == "noon":
        h = h + 12 if 1 <= h <= 5 else h
    elif period == "night":
        h = h + 12 if 6 <= h <= 11 else (0 if h == 12 else h)
    if not (0 <= h <= 23 and 0 <= mi <= 59 and 0 <= sec <= 59):
        raise ValueError(f"'{text}' is not a valid time of day.")
    return h, mi, sec


VALID_FROM, VALID_TO = 1800, 2050          # span of the JPL Table 1 elements
LONG_FROM, LONG_TO = 1600, 3000            # span treated as "good" with the long-term table
YEAR_MIN, YEAR_MAX = 1, 9999


def range_note(year: int) -> Optional[str]:
    if VALID_FROM <= year <= VALID_TO:
        return None
    if LONG_FROM <= year <= LONG_TO:
        return (f"Year {year} is outside 1800-2050, so the long-term JPL planetary table is used: Sun, Moon, Mercury, Venus and Mars stay within "
                "about 0.1 degree; Jupiter and Saturn can be off by up to about 0.3 degree (a rashi or nakshatra edge can differ).")
    if year < LONG_FROM:
        return (f"Year {year} is before 1600. Sun and Moon are still good (the Sun matches Meeus' equinox formulas to under 10 minutes back to 325 CE), "
                "but the long-term planet table is rougher (Jupiter and Saturn up to ~0.5 degree), the Earth's spin (Delta-T) is uncertain, "
                "and the calendar and local time of that era are uncertain too. Treat the result as approximate.")
    return (f"Year {year} is beyond 3000, past the range the long-term planet table was fitted to. The Sun stays within about 40 minutes "
            "of exact until 4000 and the Moon is good to a fraction of a degree, but the planets drift further each century. Treat as approximate.")
