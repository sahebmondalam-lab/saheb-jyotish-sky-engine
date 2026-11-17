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
    if isinstance(text, date):
        return text
    s = normalize(text)
    if not s:
        raise ValueError("date is empty")
    notes = notes if notes is not None else []
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        return _mk(int(m.group(1)), int(m.group(2)), int(m.group(3)), text)
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if b > 12 and a <= 12:
            notes.append(f"Date '{s}' read as MM/DD/YYYY because {b} cannot be a month.")
            return _mk(y, a, b, text)
        if a <= 12 and b <= 12 and a != b:
            notes.append(f"Date '{s}' is ambiguous; read as DD/MM/YYYY (day first). Say so if you meant month first.")
        return _mk(y, b, a, text)
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
        return _mk(year, month, day, text)
    raise ValueError(f"Cannot understand date '{text}'. Use e.g. 1992-01-27, 27/01/1992 or 27 Jan 1992.")


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


VALID_FROM, VALID_TO = 1800, 2050


def range_note(year: int) -> Optional[str]:
    if VALID_FROM <= year <= VALID_TO:
        return None
    return (f"Year {year} is outside 1800-2050, the span the built-in JPL planetary elements are fitted to. "
            "Moon, Sun and the tithi/nakshatra are still good, but outer-planet positions can be off by degrees; treat them as approximate.")
