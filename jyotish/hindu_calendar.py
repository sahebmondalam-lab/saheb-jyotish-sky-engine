# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""The Hindu calendar systems that Indian panchang-makers use, computed from the real Sun and Moon.

Lunisolar (Chandramana): amanta / purnimanta month names from the Sun's sankranti rule, Adhika (extra) and
Kshaya (lost) months, shukla/krishna paksha, udaya tithi with vriddhi/kshaya, Vikram / Shaka / Kali eras,
the 60-year Samvatsara, Ritu and Ayana.
Solar (Sauramana): Bengali (Bangabda), Tamil, Malayalam (Kollam), Odia months by each tradition's own
day-start rule, plus the Indian National (Saka) civil calendar.
Festivals: dates found by the traditional tithi rules (udaya / madhyahna / aparahna / pradosha / nishitha).

Method = "Drik" (modern ephemeris; what drikpanchang.com and most printed panjikas today follow, Lahiri ayanamsa).
The old Surya Siddhanta / Vakya reckonings are NOT used; they can differ by a tithi on some days.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from . import astro as A
from . import calendars as CAL
from .location import Location
from .panchang import day_times, local_midnight_jd

SYNODIC = 29.530588
MOON_RATE = 12.1907       # mean elongation gain, degrees per day

# ---------------------------------------------------------------- names (English, Bengali); Hindi in data_hi
LUNAR_MONTH = [
    ("Chaitra", "চৈত্র"), ("Vaishakha", "বৈশাখ"), ("Jyeshtha", "জ্যৈষ্ঠ"), ("Ashadha", "আষাঢ়"),
    ("Shravana", "শ্রাবণ"), ("Bhadrapada", "ভাদ্র"), ("Ashwina", "আশ্বিন"), ("Kartika", "কার্তিক"),
    ("Margashirsha", "অগ্রহায়ণ"), ("Pausha", "পৌষ"), ("Magha", "মাঘ"), ("Phalguna", "ফাল্গুন"),
]
RITU = [
    ("Vasanta (Spring)", "বসন্ত"), ("Grishma (Summer)", "গ্রীষ্ম"), ("Varsha (Monsoon)", "বর্ষা"),
    ("Sharad (Autumn)", "শরৎ"), ("Hemanta (Pre-winter)", "হেমন্ত"), ("Shishira (Winter)", "শীত"),
]
AYANA = [("Uttarayana (Sun moving north)", "উত্তরায়ণ"), ("Dakshinayana (Sun moving south)", "দক্ষিণায়ন")]
# 60-year Samvatsara cycle (Prabhava ... Akshaya), (English, Bengali)
SAMVATSARA = [
    ("Prabhava", "প্রভব"), ("Vibhava", "বিভব"), ("Shukla", "শুক্ল"), ("Pramoda", "প্রমোদ"), ("Prajapati", "প্রজাপতি"),
    ("Angira", "অঙ্গিরা"), ("Shrimukha", "শ্রীমুখ"), ("Bhava", "ভাব"), ("Yuva", "যুবা"), ("Dhatri", "ধাতা"),
    ("Ishvara", "ঈশ্বর"), ("Bahudhanya", "বহুধান্য"), ("Pramathi", "প্রমাথী"), ("Vikrama", "বিক্রম"), ("Vrisha", "বৃষ"),
    ("Chitrabhanu", "চিত্রভানু"), ("Svabhanu", "স্বভানু"), ("Tarana", "তারণ"), ("Parthiva", "পার্থিব"), ("Vyaya", "ব্যয়"),
    ("Sarvajit", "সর্বজিৎ"), ("Sarvadhari", "সর্বধারী"), ("Virodhi", "বিরোধী"), ("Vikriti", "বিকৃতি"), ("Khara", "খর"),
    ("Nandana", "নন্দন"), ("Vijaya", "বিজয়"), ("Jaya", "জয়"), ("Manmatha", "মন্মথ"), ("Durmukhi", "দুর্মুখী"),
    ("Hevilambi", "হেমলম্বী"), ("Vilambi", "বিলম্বী"), ("Vikari", "বিকারী"), ("Sharvari", "শার্বরী"), ("Plava", "প্লব"),
    ("Shubhakrit", "শুভকৃৎ"), ("Shobhakrit", "শোভকৃৎ"), ("Krodhi", "ক্রোধী"), ("Vishvavasu", "বিশ্বাবসু"), ("Parabhava", "পরাভব"),
    ("Plavanga", "প্লবঙ্গ"), ("Kilaka", "কীলক"), ("Saumya", "সৌম্য"), ("Sadharana", "সাধারণ"), ("Virodhikrit", "বিরোধিকৃৎ"),
    ("Paridhavi", "পরিধাবী"), ("Pramadicha", "প্রমাদী"), ("Ananda", "আনন্দ"), ("Rakshasa", "রাক্ষস"), ("Nala", "নল"),
    ("Pingala", "পিঙ্গল"), ("Kalayukta", "কালযুক্ত"), ("Siddharthi", "সিদ্ধার্থী"), ("Raudra", "রৌদ্র"), ("Durmati", "দুর্মতি"),
    ("Dundubhi", "দুন্দুভি"), ("Rudhirodgari", "রুধিরোদ্গারী"), ("Raktakshi", "রক্তাক্ষী"), ("Krodhana", "ক্রোধন"), ("Akshaya", "অক্ষয়"),
]
# solar month names per tradition, index 0 = month of Mesha sankranti
BENGALI_MONTH = [("Boishakh", "বৈশাখ"), ("Joishtho", "জ্যৈষ্ঠ"), ("Asharh", "আষাঢ়"), ("Srabon", "শ্রাবণ"),
                 ("Bhadro", "ভাদ্র"), ("Ashshin", "আশ্বিন"), ("Kartik", "কার্তিক"), ("Ogrohayon", "অগ্রহায়ণ"),
                 ("Poush", "পৌষ"), ("Magh", "মাঘ"), ("Falgun", "ফাল্গুন"), ("Choitro", "চৈত্র")]
TAMIL_MONTH = [("Chithirai", "চিত্তিরাই"), ("Vaikasi", "বৈকাসি"), ("Aani", "আনি"), ("Aadi", "আদি"),
               ("Aavani", "আবনি"), ("Purattasi", "পুরত্তাসি"), ("Aippasi", "আইপ্পাসি"), ("Karthigai", "কার্তিগাই"),
               ("Margazhi", "মার্গাজি"), ("Thai", "থাই"), ("Maasi", "মাসি"), ("Panguni", "পঙ্গুনি")]
MALAYALAM_MONTH = [("Medam", "মেদম"), ("Edavam", "এডভম"), ("Mithunam", "মিথুনম"), ("Karkidakam", "কর্কিডকম"),
                   ("Chingam", "চিংগম"), ("Kanni", "কন্নি"), ("Thulam", "তুলাম"), ("Vrischikam", "বৃশ্চিকম"),
                   ("Dhanu", "ধনু"), ("Makaram", "মকরম"), ("Kumbham", "কুম্ভম"), ("Meenam", "মীনম")]
ODIA_MONTH = [("Baisakha", "বৈশাখ"), ("Jyestha", "জ্যৈষ্ঠ"), ("Asadha", "আষাঢ়"), ("Srabana", "শ্রাবণ"),
              ("Bhadraba", "ভাদ্র"), ("Aswina", "আশ্বিন"), ("Kartika", "কার্তিক"), ("Margasira", "অগ্রহায়ণ"),
              ("Pausa", "পৌষ"), ("Magha", "মাঘ"), ("Phalguna", "ফাল্গুন"), ("Chaitra", "চৈত্র")]
SAKA_CIVIL_MONTH = [("Chaitra", "চৈত্র"), ("Vaishakha", "বৈশাখ"), ("Jyeshtha", "জ্যৈষ্ঠ"), ("Ashadha", "আষাঢ়"),
                    ("Shravana", "শ্রাবণ"), ("Bhadra", "ভাদ্র"), ("Ashwin", "আশ্বিন"), ("Kartika", "কার্তিক"),
                    ("Agrahayana", "অগ্রহায়ণ"), ("Pausha", "পৌষ"), ("Magha", "মাঘ"), ("Phalguna", "ফাল্গুন")]
PAKSHA = [("Shukla (waxing)", "শুক্ল"), ("Krishna (waning)", "কৃষ্ণ")]


# ---------------------------------------------------------------- astronomy helpers
def _elong(jd: float) -> float:
    return A.norm360(A.tropical_longitude("Moon", jd) - A.tropical_longitude("Sun", jd))


def _sun_sid(jd: float) -> float:
    return A.sidereal_longitude("Sun", jd)


def new_moon_near(guess: float) -> float:
    """Exact conjunction (UT Julian day) nearest to the guess."""
    jd = guess
    for _ in range(12):
        jd -= A.norm180(_elong(jd)) / MOON_RATE
    return jd


def new_moon_before(jd: float) -> float:
    n = new_moon_near(jd - _elong(jd) / MOON_RATE)
    while n > jd:
        n = new_moon_near(n - SYNODIC)
    while new_moon_near(n + SYNODIC) <= jd:
        n = new_moon_near(n + SYNODIC)
    return n


def sankranti_after(jd: float, sign: Optional[int] = None) -> Tuple[float, int]:
    """Next moment (>= jd) the sidereal Sun enters a sign (a given one, or whichever comes next)."""
    lon = _sun_sid(jd)
    s0 = int(lon // 30) % 12
    target_sign = (s0 + 1) % 12 if sign is None else sign
    target = target_sign * 30.0
    jd2 = jd + A.norm360(target - lon) / 0.9856
    for _ in range(12):
        jd2 += A.norm180(target - _sun_sid(jd2)) / 0.9856
    return jd2, target_sign


def sankranti_before(jd: float) -> Tuple[float, int]:
    """Latest moment (<= jd) the sidereal Sun entered its current sign."""
    lon = _sun_sid(jd)
    s0 = int(lon // 30) % 12
    jd2 = jd - (lon - s0 * 30.0) / 0.9856
    for _ in range(12):
        jd2 += A.norm180(s0 * 30.0 - _sun_sid(jd2)) / 0.9856
    return jd2, s0


def _tithi_pos(jd: float) -> float:
    return _elong(jd) / 12.0            # 0..30


def tithi_number(jd: float) -> int:
    """1..30 (1-15 shukla, 16-30 krishna; 15 purnima, 30 amavasya)."""
    return int(_tithi_pos(jd)) % 30 + 1


# ---------------------------------------------------------------- lunar month
def lunar_month_at(jd: float) -> Dict:
    """Amanta lunar month containing this instant."""
    n1 = new_moon_before(jd)
    n2 = new_moon_near(n1 + SYNODIC)
    r1 = int(_sun_sid(n1) // 30) % 12
    r2 = int(_sun_sid(n2) // 30) % 12
    adhika = r1 == r2
    kshaya = (r2 - r1) % 12 == 2
    name = (r1 + 1) % 12
    return {"start_jd": n1, "end_jd": n2, "amanta": name, "adhika": adhika, "kshaya": kshaya, "sun_sign_at_start": r1}


def _month_after_adhika(m: Dict) -> bool:
    return False


# ---------------------------------------------------------------- eras
def era_years(month_idx: int, month_start_jd: float) -> Dict:
    """Shaka / Vikram / Kali year numbers for a lunar month that begins at month_start_jd (amanta index 0 = Chaitra)."""
    approx_chaitra = month_start_jd - month_idx * 29.5306
    yc = A.datetime_from_jd(approx_chaitra).year          # Gregorian year in which this Chaitra falls
    shaka = yc - 78
    vikram = yc + 57
    return {"shaka": shaka, "vikram_chaitradi": vikram,
            "vikram_kartikadi": vikram - 1 if month_idx < 7 else vikram,   # Gujarat: year changes on Kartika Shukla 1
            "kali": yc + 3101,
            "samvatsara_index": (shaka - 1909) % 60}             # 0 = Prabhava; Shaka 1948 (2026-27) -> Parabhava


def ritu_of_lunar_month(m: int) -> int:
    return m // 2


def ayana_of_sun(sid_lon: float) -> int:
    s = int(sid_lon // 30) % 12
    return 0 if s in (9, 10, 11, 0, 1, 2) else 1       # Makara..Mithuna = Uttarayana


def solar_ritu(sid_lon: float) -> int:
    """Sauramana ritu: Vasanta = Meena+Mesha, Grishma = Vrishabha+Mithuna, ... (Sun in sign -> ritu)."""
    s = int(sid_lon // 30) % 12
    return ((s + 1) % 12) // 2


# ---------------------------------------------------------------- solar-calendar day rules
def _local_date(jd: float, loc: Location) -> date:
    dt = A.datetime_from_jd(jd).astimezone(loc.tz)
    return date(dt.year, dt.month, dt.day)


def _tithi_state(d: date, loc: Location) -> Dict:
    t = day_times(d, loc)
    return t


def _solar_month_start(sankranti_jd: float, rule: str, loc: Location) -> date:
    """First civil day of the solar month whose sankranti occurs at sankranti_jd, under a tradition's rule."""
    dt = A.datetime_from_jd(sankranti_jd).astimezone(loc.tz)
    d = date(dt.year, dt.month, dt.day)
    if rule == "odia":                       # the sankranti day itself
        return d
    sr = day_times(d, loc)
    if rule == "tamil":                      # same day if sankranti is before sunset, else next day
        return d if sr.get("sunset_jd") and sankranti_jd < sr["sunset_jd"] else d + timedelta(days=1)
    if rule == "malayalam":                  # same day if before aparahna (3/5 of daytime), else next day
        if sr.get("sunrise_jd") and sr.get("sunset_jd"):
            cut = sr["sunrise_jd"] + 0.6 * (sr["sunset_jd"] - sr["sunrise_jd"])
            return d if sankranti_jd < cut else d + timedelta(days=1)
        return d
    if rule == "bengali":                    # West Bengal (Surya-Siddhanta panjika) rule, by the Hindu day (sunrise to sunrise):
        sr0 = sr.get("sunrise_jd")           # sankranti before the Hindu day's midnight -> next day; after midnight -> day after
        h = d if (sr0 is None or sankranti_jd >= sr0) else d - timedelta(days=1)
        mid = local_midnight_jd(h + timedelta(days=1), loc)
        return h + timedelta(days=1) if sankranti_jd < mid else h + timedelta(days=2)
    raise ValueError(rule)


_SOLAR_RULES = {"bengali": "bengali", "tamil": "tamil", "malayalam": "malayalam", "odia": "odia"}


def solar_date(d: date, loc: Location, tradition: str) -> Dict:
    """Day-of-month and month index (0 = month of Mesha sankranti) in a sauramana calendar."""
    rule = _SOLAR_RULES[tradition]
    probe = local_midnight_jd(d + timedelta(days=1), loc) - 1e-4     # end of the civil day: includes a sankranti that falls late in it
    for _ in range(3):                       # the governing sankranti: latest one whose month-start is on or before d
        sk, sign = sankranti_before(probe)
        start = _solar_month_start(sk, rule, loc)
        if start <= d:
            return {"month_index": sign, "day": (d - start).days + 1, "month_start": start, "sankranti_jd": sk}
        probe = sk - 1.0
    raise RuntimeError("solar month search failed")


def national_saka_date(d: date) -> Dict:
    """Indian National Calendar (Saka civil, adopted 1957): Chaitra 1 = 22 March (21 March in Gregorian leap years)."""
    def leap(y): return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
    gy = d.year if d >= date(d.year, 3, 21 if leap(d.year) else 22) else d.year - 1
    s = date(gy, 3, 21 if leap(gy) else 22)
    lengths = [31 if leap(gy) else 30] + [31] * 5 + [30] * 6
    off = (d - s).days
    m = 0
    while off >= lengths[m]:
        off -= lengths[m]
        m += 1
    return {"year": gy - 78, "month_index": m, "day": off + 1}


def bengali_year(month_start: date) -> int:
    """Bangabda: new year at Boishakh 1 (mid-April). Year = Gregorian year - 593 from April, - 594 from January to March."""
    return month_start.year - (593 if month_start.month >= 4 else 594)


def kollam_year(month_start: date) -> int:
    """Kollam era: new year at Chingam 1 (mid-August). Year = Gregorian year - 824 from August, - 825 before."""
    return month_start.year - (824 if month_start.month >= 8 else 825)


# ---------------------------------------------------------------- one day's full Hindu calendar entry
def _sunrise_ref(d: date, loc: Location) -> Tuple[float, Dict]:
    t = day_times(d, loc)
    ref = t["sunrise_jd"] if t.get("sunrise_jd") else local_midnight_jd(d, loc) + 0.25
    return ref, t


def day_calendar(d: date, loc: Location) -> Dict:
    """Everything the Hindu calendar says about one civil day (evaluated at local sunrise)."""
    ref, t = _sunrise_ref(d, loc)
    lm = lunar_month_at(ref)
    tn = tithi_number(ref)
    paksha = 0 if tn <= 15 else 1
    prev_ref, _ = _sunrise_ref(d - timedelta(days=1), loc)
    next_ref, _ = _sunrise_ref(d + timedelta(days=1), loc)
    tp, tx = tithi_number(prev_ref), tithi_number(next_ref)
    amanta = lm["amanta"]
    if lm["adhika"]:
        purn, purn_adhika = amanta, True
    elif paksha == 1:
        purn, purn_adhika = (amanta + 1) % 12, False
    else:
        purn, purn_adhika = amanta, False
    ey = era_years(amanta, lm["start_jd"])
    # the Shaka/Vikram year is that of the *nija* Chaitra onward; purnimanta year change is two weeks earlier
    sun = _sun_sid(ref)
    out = {
        "date": d, "reference_jd": ref, "tithi_number": tn, "paksha": paksha,
        "tithi_in_paksha": tn if tn <= 15 else tn - 15,
        "amanta_month": amanta, "purnimanta_month": purn, "adhika": lm["adhika"], "purnimanta_adhika": purn_adhika,
        "kshaya_month_warning": lm["kshaya"], "month_start_jd": lm["start_jd"], "month_end_jd": lm["end_jd"],
        "tithi_vriddhi": tx == tn,                   # same tithi at the next sunrise too (it spans two sunrises)
        "tithi_repeated_from_yesterday": tp == tn,
        "tithi_kshaya_next": ((tn % 30) + 1) != tx and tx != tn,   # the tithi after this one never touches a sunrise
        "skipped_tithi": (tn % 30) + 1 if (((tn % 30) + 1) != tx and tx != tn) else None,
        **ey,
        "ritu_lunar": ritu_of_lunar_month(amanta),
        "ritu_solar": solar_ritu(sun),
        "ayana": ayana_of_sun(sun),
        "sun_sign": int(sun // 30) % 12,
    }
    sol = {}
    for k in _SOLAR_RULES:
        sd = solar_date(d, loc, k)
        y = bengali_year(sd["month_start"]) if k == "bengali" else kollam_year(sd["month_start"]) if k == "malayalam" else None
        sol[k] = {"month_index": sd["month_index"], "day": sd["day"], "year": y, "month_start": sd["month_start"]}
    out["solar"] = sol
    out["national"] = national_saka_date(d)
    return out


# ---------------------------------------------------------------- festivals
# (key, English, Bengali, Hindi, amanta month index or None, tithi 1-30, rule, day offset)
# tithi: 1-15 shukla, 16-30 krishna (15 purnima, 30 amavasya).  rule: udaya|madhyahna|aparahna|pradosha|nishitha|arunodaya
FESTIVALS: List[Tuple] = [
    ("vasant_panchami", "Vasant Panchami", "বসন্ত পঞ্চমী", "वसंत पंचमी", 10, 5, "madhyahna", 0),
    ("ratha_saptami", "Ratha Saptami", "রথ সপ্তমী", "रथ सप्तमी", 10, 7, "udaya", 0),
    ("bhishma_ashtami", "Bhishma Ashtami", "ভীষ্ম অষ্টমী", "भीष्म अष्टमी", 10, 8, "madhyahna", 0),
    ("maha_shivaratri", "Maha Shivaratri", "মহাশিবরাত্রি", "महाशिवरात्रि", 10, 29, "nishitha", 0),
    ("holika_dahan", "Holika Dahan", "হোলিকা দহন", "होलिका दहन", 11, 15, "pradosha", 0),
    ("holi", "Holi (Dol Jatra)", "হোলি / দোলযাত্রা", "होली", 11, 15, "pradosha", 1),
    ("ugadi", "Ugadi / Gudi Padwa / Chaitra Navratri begins", "উগাদি / গুড়ি পাড়োয়া / চৈত্র নবরাত্রি শুরু", "उगादि / गुड़ी पड़वा / चैत्र नवरात्रि", 0, 1, "udaya", 0),
    ("ram_navami", "Rama Navami", "রাম নবমী", "राम नवमी", 0, 9, "madhyahna", 0),
    ("hanuman_jayanti", "Hanuman Jayanti", "হনুমান জয়ন্তী", "हनुमान जयंती", 0, 15, "udaya", 0),
    ("akshaya_tritiya", "Akshaya Tritiya", "অক্ষয় তৃতীয়া", "अक्षय तृतीया", 1, 3, "madhyahna", 0),
    ("ganga_saptami", "Ganga Saptami", "গঙ্গা সপ্তমী", "गंगा सप्तमी", 1, 7, "madhyahna", 0),
    ("sita_navami", "Sita Navami", "সীতা নবমী", "सीता नवमी", 1, 9, "madhyahna", 0),
    ("narasimha_jayanti", "Narasimha Jayanti", "নৃসিংহ জয়ন্তী", "नृसिंह जयंती", 1, 14, "sayahna", 0),
    ("buddha_purnima", "Buddha Purnima", "বুদ্ধ পূর্ণিমা", "बुद्ध पूर्णिमा", 1, 15, "udaya", 0),
    ("vat_savitri", "Vat Savitri Vrat / Shani Jayanti", "বট সাবিত্রী ব্রত / শনি জয়ন্তী", "वट सावित्री व्रत / शनि जयंती", 1, 30, "udaya", 0),
    ("ganga_dussehra", "Ganga Dussehra", "গঙ্গা দশহরা", "गंगा दशहरा", 2, 10, "udaya", 0),
    ("rath_yatra", "Jagannath Rath Yatra", "জগন্নাথ রথযাত্রা", "जगन्नाथ रथ यात्रा", 3, 2, "udaya", 0),
    ("guru_purnima", "Guru Purnima", "গুরু পূর্ণিমা", "गुरु पूर्णिमा", 3, 15, "udaya", 0),
    ("hariyali_teej", "Hariyali Teej", "হরিয়ালি তিজ", "हरियाली तीज", 4, 3, "udaya", 0),
    ("nag_panchami", "Nag Panchami", "নাগ পঞ্চমী", "नाग पंचमी", 4, 5, "madhyahna", 0),
    ("raksha_bandhan", "Raksha Bandhan / Jhulan Purnima", "রাখি পূর্ণিমা / ঝুলন পূর্ণিমা", "रक्षा बंधन", 4, 15, "aparahna", 0),
    ("kajari_teej", "Kajari Teej", "কাজরি তিজ", "कजरी तीज", 4, 18, "udaya", 0),
    ("janmashtami", "Krishna Janmashtami", "কৃষ্ণ জন্মাষ্টমী", "कृष्ण जन्माष्टमी", 4, 23, "udaya", 0),
    ("hartalika_teej", "Hartalika Teej", "হরতালিকা তিজ", "हरतालिका तीज", 5, 3, "udaya", 0),
    ("ganesh_chaturthi", "Ganesh Chaturthi", "গণেশ চতুর্থী", "गणेश चतुर्थी", 5, 4, "madhyahna", 0),
    ("rishi_panchami", "Rishi Panchami", "ঋষি পঞ্চমী", "ऋषि पंचमी", 5, 5, "madhyahna", 0),
    ("radha_ashtami", "Radha Ashtami", "রাধাষ্টমী", "राधा अष्टमी", 5, 8, "madhyahna", 0),
    ("anant_chaturdashi", "Anant Chaturdashi / Ganesh Visarjan", "অনন্ত চতুর্দশী", "अनंत चतुर्दशी", 5, 14, "udaya", 0),
    ("pitrupaksha_begins", "Pitrupaksha (Mahalaya period) begins", "পিতৃপক্ষ শুরু", "पितृपक्ष आरंभ", 5, 16, "udaya", 0),
    ("sarva_pitru_amavasya", "Sarva Pitru Amavasya (Mahalaya)", "মহালয়া / সর্ব পিতৃ অমাবস্যা", "सर्वपितृ अमावस्या", 5, 30, "aparahna", 0),
    ("navratri_begins", "Sharad Navratri begins (Durga Puja Pratipada)", "শারদীয় নবরাত্রি শুরু", "शारदीय नवरात्रि आरंभ", 6, 1, "udaya", 0),
    ("durga_ashtami", "Durga Ashtami", "দুর্গাষ্টমী", "दुर्गा अष्टमी", 6, 8, "udaya", 0),
    ("maha_navami", "Maha Navami", "মহানবমী", "महानवमी", 6, 9, "madhyahna", 0),
    ("dussehra", "Vijayadashami / Dussehra", "বিজয়াদশমী / দশেরা", "विजयादशमी / दशहरा", 6, 10, "aparahna", 0),
    ("sharad_purnima", "Sharad Purnima", "শরৎ পূর্ণিমা", "शरद पूर्णिमा", 6, 15, "pradosha", 0),
    ("kojagara_puja", "Kojagara Puja (Kojagari Lakshmi Puja)", "কোজাগরী লক্ষ্মীপূজা", "कोजागरा पूजा", 6, 15, "nishitha", 0),
    ("karwa_chauth", "Karwa Chauth", "করওয়া চৌথ", "करवा चौथ", 6, 19, "pradosha", 0),
    ("ahoi_ashtami", "Ahoi Ashtami", "অহোই অষ্টমী", "अहोई अष्टमी", 6, 23, "pradosha", 0),
    ("dhanteras", "Dhanteras", "ধনতেরস", "धनतेरस", 6, 28, "pradosha", 0),
    ("naraka_chaturdashi", "Naraka Chaturdashi (Choti Diwali)", "নরক চতুর্দশী", "नरक चतुर्दशी", 6, 29, "arunodaya", 0),
    ("diwali", "Diwali / Lakshmi Puja / Kali Puja", "দীপাবলি / লক্ষ্মীপূজা / কালীপূজা", "दीवाली / लक्ष्मी पूजा", 6, 30, "pradosha", 0),
    ("govardhan_puja", "Govardhan Puja", "গোবর্ধন পূজা", "गोवर्धन पूजा", 7, 1, "udaya", 0),
    ("bhai_dooj", "Bhai Dooj / Bhai Phonta", "ভাইফোঁটা", "भाई दूज", 7, 2, "aparahna", 0),
    ("chhath_puja", "Chhath Puja (Sandhya Arghya)", "ছট পূজা", "छठ पूजा", 7, 6, "pradosha", 0),
    ("kartika_purnima", "Kartika Purnima (Dev Deepawali)", "কার্তিক পূর্ণিমা / রাস পূর্ণিমা", "कार्तिक पूर्णिमा", 7, 15, "udaya", 0),
    ("kalabhairav_jayanti", "Kalabhairav Jayanti", "কালভৈরব জয়ন্তী", "कालभैरव जयंती", 7, 23, "pradosha", 0),
    ("vivah_panchami", "Vivah Panchami", "বিবাহ পঞ্চমী", "विवाह पंचमी", 8, 5, "madhyahna", 0),
    ("dattatreya_jayanti", "Dattatreya Jayanti", "দত্তাত্রেয় জয়ন্তী", "दत्तात्रेय जयंती", 8, 15, "pradosha", 0),
    ("sakat_chauth", "Sakat Chauth", "সংকট চতুর্থী", "सकट चौथ", 9, 19, "pradosha", 0),
    ("mauni_amavasya", "Mauni Amavasya", "মৌনী অমাবস্যা", "मौनी अमावस्या", 9, 30, "udaya", 0),
    ("sheetala_ashtami", "Sheetala Ashtami", "শীতলা অষ্টমী", "शीतला अष्टमी", 11, 23, "udaya", 0),
]
# Ekadashi names by purnimanta month (Krishna paksha) and amanta month (Shukla paksha)
_EK_K = ["Varuthini", "Apara", "Yogini", "Kamika", "Aja", "Indira", "Rama", "Utpanna", "Saphala", "Shattila", "Vijaya", "Papamochani"]
_EK_S = ["Kamada", "Mohini", "Nirjala", "Devshayani", "Shravana Putrada", "Parsva", "Papankusha", "Devutthana",
         "Mokshada", "Pausha Putrada", "Jaya", "Amalaki"]
# purnimanta month index: Krishna ekadashi of amanta month m belongs to purnimanta month m+1, whose name is _EK_K[(m+1)%12 - 1]
ADHIKA_OBSERVED = {"ganga_dussehra"}     # drikpanchang and many almanacs keep these even inside an Adhika month
_EK_BN_HI = {
    "Varuthini": ("বরূথিনী", "वरूथिनी"), "Apara": ("অপরা", "अपरा"), "Yogini": ("যোগিনী", "योगिनी"), "Kamika": ("কামিকা", "कामिका"),
    "Aja": ("অজা", "अजा"), "Indira": ("ইন্দিরা", "इंदिरा"), "Rama": ("রমা", "रमा"), "Utpanna": ("উৎপন্না", "उत्पन्ना"),
    "Saphala": ("সফলা", "सफला"), "Shattila": ("ষট্তিলা", "षटतिला"), "Vijaya": ("বিজয়া", "विजया"), "Papamochani": ("পাপমোচনী", "पापमोचनी"),
    "Kamada": ("কামদা", "कामदा"), "Mohini": ("মোহিনী", "मोहिनी"), "Nirjala": ("নির্জলা", "निर्जला"), "Devshayani": ("দেবশয়নী", "देवशयनी"),
    "Shravana Putrada": ("শ্রাবণ পুত্রদা", "श्रावण पुत्रदा"), "Parsva": ("পার্শ্ব (পরিবর্তিনী)", "परिवर्तिनी"), "Papankusha": ("পাপাঙ্কুশা", "पापांकुशा"),
    "Devutthana": ("দেবোত্থান (প্রবোধিনী)", "देवउठनी"), "Mokshada": ("মোক্ষদা", "मोक्षदा"), "Pausha Putrada": ("পৌষ পুত্রদা", "पौष पुत्रदा"),
    "Jaya": ("জয়া", "जया"), "Amalaki": ("আমলকী", "आमलकी"),
    "Padmini (Adhika)": ("পদ্মিনী (অধিক মাস)", "पद्मिनी (अधिक मास)"), "Parama (Adhika)": ("পরমা (অধিক মাস)", "परमा (अधिक मास)"),
}
_PAD = ("Padmini (Adhika)", "Parama (Adhika)")
# Presence windows (fractions of the daytime from sunrise): the day on which the tithi covers the window the most wins
_WINDOWS = {"udaya": (0.0, 0.0), "purvahna": (0.0, 0.2), "madhyahna": (0.4, 0.6), "aparahna": (0.6, 0.8), "sayahna": (0.8, 1.0)}
_PRADOSHA_LEN = 0.1            # 2 h 24 m after sunset
_NISHITHA_HALF = 0.0167        # +- 24 min around the middle of the night
_ARUNA_LEN = 96.0 / 1440.0     # 96 min before sunrise


def _window(rule: str, t_today: Dict, t_next: Dict) -> Optional[Tuple[float, float]]:
    r, s = t_today.get("sunrise_jd"), t_today.get("sunset_jd")
    if r is None or s is None:
        return None
    if rule in _WINDOWS:
        a, b = _WINDOWS[rule]
        return (r + a * (s - r), r + b * (s - r))
    if rule == "pradosha":
        return (s, s + _PRADOSHA_LEN)
    if rule == "nishitha":
        nr = t_next.get("sunrise_jd") or (r + 1.0)
        mid = s + 0.5 * (nr - s)
        return (mid - _NISHITHA_HALF, mid + _NISHITHA_HALF)
    if rule == "arunodaya":
        return (r - _ARUNA_LEN, r)
    raise ValueError(rule)


def _rule_jd(rule: str, t_today: Dict, t_next: Dict) -> Optional[float]:
    w = _window(rule, t_today, t_next)
    return None if w is None else (w[0] + w[1]) / 2.0


def karana_half(jd: float) -> int:
    """0..59: which half-tithi (karana) is running."""
    return int(_elong(jd) // 6.0) % 60


def is_vishti(jd: float) -> bool:
    """Vishti (Bhadra) karana: the 7th of the cycle, avoided for auspicious starts."""
    k = karana_half(jd)
    return 1 <= k <= 56 and (k - 1) % 7 == 6


def karana_end(jd: float) -> float:
    el = _elong(jd)
    target = (int(el // 6.0) + 1) * 6.0
    t = jd + (target - el) / MOON_RATE
    for _ in range(12):
        t -= A.norm180(_elong(t) - target) / MOON_RATE
    return t


def tithi_interval(tn: int, lm: Dict) -> Tuple[float, float]:
    """Exact start and end (UT Julian day) of tithi number tn inside an amanta lunar month."""
    def solve(target: float) -> float:
        jd = lm["start_jd"] + target / MOON_RATE
        for _ in range(12):
            jd -= A.norm180(_elong(jd) - target) / MOON_RATE
        return jd
    s = lm["start_jd"] if tn == 1 else solve((tn - 1) * 12.0)
    e = lm["end_jd"] if tn == 30 else solve(tn * 12.0)
    return s, e


def lunar_months_of_year(year: int) -> List[Dict]:
    """Every amanta lunar month that overlaps the Gregorian year."""
    jd0 = A.julian_day(datetime(year, 1, 1, tzinfo=timezone.utc)) - 1.0
    jd1 = A.julian_day(datetime(year + 1, 1, 1, tzinfo=timezone.utc)) + 1.0
    months = [lunar_month_at(jd0)]
    while months[-1]["end_jd"] < jd1:
        months.append(lunar_month_at(months[-1]["end_jd"] + 0.5))
    return months


def _local_day_times(year: int, loc: Location) -> Dict[date, Dict]:
    times = {}
    d = date(year, 1, 1) - timedelta(days=2)
    while d <= date(year, 12, 31) + timedelta(days=3):
        times[d] = day_times(d, loc)
        d += timedelta(days=1)
    return times


def _find_day(s: float, e: float, rule: str, times: Dict[date, Dict], loc: Location) -> Tuple[Optional[date], str]:
    """Civil day on which the tithi interval [s, e) covers the rule's window the most (ties: the earlier day).
    If it never touches the window (a kshaya tithi) the day on which it mostly falls is used."""
    best, best_d = 0.0, None
    alts: List[date] = []
    for d in sorted(times):
        w = _window(rule, times[d], times.get(d + timedelta(days=1), {}))
        if w is None:
            continue
        if w[0] == w[1]:
            ov = 1.0 if s <= w[0] < e else 0.0
        else:
            ov = max(0.0, min(e, w[1]) - max(s, w[0]))
        if ov > 1e-9:
            alts.append(d)
        if ov > best + 1e-9:
            best, best_d = ov, d
    if best_d is not None:
        for d in sorted(times):                       # the day the tithi is also running at sunrise is a common alternative
            sr = times[d].get("sunrise_jd")
            if sr is not None and s <= sr < e and d not in alts:
                alts.append(d)
        _find_day.last_alts = [a for a in alts if a != best_d]
        return best_d, rule
    _find_day.last_alts = []
    mid = A.datetime_from_jd((s + e) / 2.0).astimezone(loc.tz)
    return date(mid.year, mid.month, mid.day), "kshaya-fallback"


def _bhadra_shift(key: str, day: date, s: float, e: float, times: Dict[date, Dict], loc: Location) -> Tuple[date, str]:
    """Drik-style Bhadra (Vishti) avoidance for Holika Dahan and Raksha Bandhan."""
    t, tn = times[day], times.get(day + timedelta(days=1), {})
    if key in ("holika_dahan", "holi"):
        w = _window("pradosha", t, tn)
        if w and is_vishti(w[0] + 0.01):
            nxt = local_midnight_jd(day + timedelta(days=1), loc)
            if karana_end(w[0] + 0.01) > nxt:                 # Bhadra runs on past midnight: whole night is Bhadra
                return day + timedelta(days=1), "pradosha+bhadra-shift"
    if key == "raksha_bandhan":
        w = _window("aparahna", t, tn)
        if w and is_vishti((w[0] + w[1]) / 2.0):
            nd = day + timedelta(days=1)
            nt = times.get(nd, {})
            if nt.get("sunrise_jd") and s <= nt["sunrise_jd"] + 0.1 < e:    # Purnima still 2h24m after next sunrise
                return nd, "aparahna+bhadra-shift"
    return day, ""


def festivals_for_year(year: int, loc: Location, include_ekadashi: bool = True) -> List[Dict]:
    """Festival dates in a Gregorian year by the traditional tithi rules (Drik method, nija months only)."""
    times = _local_day_times(year, loc)
    months = lunar_months_of_year(year)
    found: List[Dict] = []
    dmin, dmax = date(year, 1, 1), date(year, 12, 31)

    def emit(key, en, bn, hi, m, tn, rule, day, how, off=0, alts=()):
        day = day + timedelta(days=off)
        if dmin <= day <= dmax:
            found.append({"key": key, "date": day, "en": en, "bn": bn, "hi": hi, "rule": rule, "month": m,
                          "tithi": tn, "how": how, "alternative_dates": sorted(a for a in alts if a != day)})

    for lm in months:
        m = lm["amanta"]
        for key, en, bn, hi, fm, tn, rule, off in FESTIVALS:
            if fm != m or (lm["adhika"] and key not in ADHIKA_OBSERVED):
                continue
            s, e = tithi_interval(tn, lm)
            day, how = _find_day(s, e, rule, times, loc)
            alts = list(getattr(_find_day, "last_alts", []))
            if day in times:
                before = day
                day, extra = _bhadra_shift(key, day, s, e, times, loc)
                if extra:
                    how = extra
                    alts = [a for a in alts if a != day] + [before]
            emit(key, en, bn, hi, m, tn, rule, day, how, off, [a + timedelta(days=off) for a in alts])
    if include_ekadashi:
        for lm in months:
            m = lm["amanta"]
            for tn in (11, 26):
                s, e = tithi_interval(tn, lm)
                day, how = _find_day(s, e, "udaya", times, loc)
                w = _window("arunodaya", times.get(day, {}), {})
                if tn in (11, 26) and w and s > w[0]:          # Ekadashi began after arunodaya: Dashami-viddha
                    nd = day + timedelta(days=1)
                    nw = _window("udaya", times.get(nd, {}), {})
                    if nw and s <= nw[0] < e:
                        day, how = nd, "dashami-viddha-shift"
                if lm["adhika"]:
                    nm = _PAD[0] if tn == 11 else _PAD[1]
                elif tn == 11:
                    nm = _EK_S[m]
                else:
                    nm = _EK_K[((m + 1) % 12 - 1) % 12]
                nb, nh = _EK_BN_HI.get(nm, (nm, nm))
                emit("ekadashi", f"{nm} Ekadashi", f"{nb} একাদশী", f"{nh} एकादशी", m, tn, "udaya", day, how)
    # purnima and amavasya of every month
    for lm in months:
        m = lm["amanta"]
        tag = " (Adhika)" if lm["adhika"] else ""
        for tn, kind, bnk, hik in ((15, "Purnima", "পূর্ণিমা", "पूर्णिमा"), (30, "Amavasya", "অমাবস্যা", "अमावस्या")):
            s, e = tithi_interval(tn, lm)
            day, how = _find_day(s, e, "udaya", times, loc)
            nme = LUNAR_MONTH[m]
            emit("purnima" if tn == 15 else "amavasya", f"{nme[0]}{tag} {kind}", f"{nme[1]} {bnk}", f"{nme[0]} {hik}",
                 m, tn, "udaya", day, how)
    # solar festivals: the 12 sankrantis
    jd = A.julian_day(datetime(year - 1, 12, 20, tzinfo=timezone.utc))
    for _ in range(14):
        jd, sign = sankranti_after(jd + 1.0)
        dt = A.datetime_from_jd(jd).astimezone(loc.tz)
        dd = date(dt.year, dt.month, dt.day)
        if dmin <= dd <= dmax:
            found.append({"key": "sankranti", "date": dd, "en": SANKRANTI_NAME[sign][0], "bn": SANKRANTI_NAME[sign][1],
                          "hi": SANKRANTI_NAME[sign][2], "rule": "solar", "month": None, "tithi": None,
                          "sankranti_jd": jd, "how": "solar"})
    seen, out = set(), []
    for r in sorted(found, key=lambda r: (r["date"], r["key"], r["en"])):
        k = (r["date"], r["en"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


SANKRANTI_NAME = [
    ("Mesha Sankranti (Solar New Year / Vaisakhi)", "মেষ সংক্রান্তি", "मेष संक्रांति"),
    ("Vrishabha Sankranti", "বৃষ সংক্রান্তি", "वृषभ संक्रांति"),
    ("Mithuna Sankranti", "মিথুন সংক্রান্তি", "मिथुन संक्रांति"),
    ("Karka Sankranti", "কর্কট সংক্রান্তি", "कर्क संक्रांति"),
    ("Simha Sankranti", "সিংহ সংক্রান্তি", "सिंह संक्रांति"),
    ("Kanya Sankranti (Vishwakarma Puja)", "কন্যা সংক্রান্তি", "कन्या संक्रांति"),
    ("Tula Sankranti", "তুলা সংক্রান্তি", "तुला संक्रांति"),
    ("Vrishchika Sankranti", "বৃশ্চিক সংক্রান্তি", "वृश्चिक संक्रांति"),
    ("Dhanu Sankranti", "ধনু সংক্রান্তি", "धनु संक्रांति"),
    ("Makara Sankranti (Pongal / Poush Sankranti)", "মকর সংক্রান্তি / পৌষ সংক্রান্তি", "मकर संक्रांति / पोंगल"),
    ("Kumbha Sankranti", "কুম্ভ সংক্রান্তি", "कुंभ संक्रांति"),
    ("Meena Sankranti", "মীন সংক্রান্তি", "मीन संक्रांति"),
]


def bangladesh_bengali_date(d: date) -> Dict:
    """Revised Bangla calendar of Bangladesh (Bangla Academy): fixed civil year starting 14 April.
    Boishakh-Bhadro 31 days, Ashwin-Choitro 30, Falgun gets one extra day when the next 29 February falls in the year."""
    def leap(y): return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
    gy = d.year if d >= date(d.year, 4, 14) else d.year - 1
    start = date(gy, 4, 14)
    lengths = [31] * 5 + [30] * 7
    if leap(gy + 1):
        lengths[10] = 31
    off = (d - start).days
    m = 0
    while off >= lengths[m]:
        off -= lengths[m]
        m += 1
    return {"year": gy - 593, "month_index": m, "day": off + 1}


# ---------------------------------------------------------------- Hindi names and trilingual helpers
_HI = {
    "lunar": ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ़", "श्रावण", "भाद्रपद", "आश्विन", "कार्तिक", "मार्गशीर्ष", "पौष", "माघ", "फाल्गुन"],
    "ritu": ["वसंत", "ग्रीष्म", "वर्षा", "शरद", "हेमंत", "शिशिर"],
    "ayana": ["उत्तरायण", "दक्षिणायन"],
    "paksha": ["शुक्ल पक्ष", "कृष्ण पक्ष"],
    "samvatsara": ["प्रभव", "विभव", "शुक्ल", "प्रमोद", "प्रजापति", "अंगिरा", "श्रीमुख", "भाव", "युवा", "धाता", "ईश्वर", "बहुधान्य", "प्रमाथी",
                   "विक्रम", "वृष", "चित्रभानु", "स्वभानु", "तारण", "पार्थिव", "व्यय", "सर्वजित्", "सर्वधारी", "विरोधी", "विकृति", "खर",
                   "नंदन", "विजय", "जय", "मन्मथ", "दुर्मुख", "हेमलंबी", "विलंबी", "विकारी", "शार्वरी", "प्लव", "शुभकृत्", "शोभकृत्",
                   "क्रोधी", "विश्वावसु", "पराभव", "प्लवंग", "कीलक", "सौम्य", "साधारण", "विरोधिकृत्", "परिधावी", "प्रमादी", "आनंद",
                   "राक्षस", "नल", "पिंगल", "कालयुक्त", "सिद्धार्थी", "रौद्र", "दुर्मति", "दुंदुभि", "रुधिरोद्गारी", "रक्ताक्षी", "क्रोधन", "अक्षय"],
    "bengali": ["वैशाख", "ज्येष्ठ", "आषाढ़", "श्रावण", "भाद्र", "आश्विन", "कार्तिक", "अग्रहायण", "पौष", "माघ", "फाल्गुन", "चैत्र"],
    "tamil": ["चित्तिरै", "वैकासी", "आनी", "आडी", "आवणि", "पुरट्टासी", "ऐप्पसी", "कार्तिगै", "मार्गळि", "तै", "मासी", "पंगुनी"],
    "malayalam": ["मेडम", "एडवम", "मिथुनम", "कर्कटकम", "चिंगम", "कन्नि", "तुलाम", "वृश्चिकम", "धनु", "मकरम", "कुंभम", "मीनम"],
    "odia": ["बैशाख", "ज्येष्ठ", "आषाढ़", "श्रावण", "भाद्रव", "आश्विन", "कार्तिक", "मार्गशीर", "पौष", "माघ", "फाल्गुन", "चैत्र"],
    "saka": ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ़", "श्रावण", "भाद्र", "आश्विन", "कार्तिक", "अग्रहायण", "पौष", "माघ", "फाल्गुन"],
}
_PAIRS = {"lunar": LUNAR_MONTH, "ritu": RITU, "ayana": AYANA, "paksha": PAKSHA, "samvatsara": SAMVATSARA,
          "bengali": BENGALI_MONTH, "tamil": TAMIL_MONTH, "malayalam": MALAYALAM_MONTH, "odia": ODIA_MONTH, "saka": SAKA_CIVIL_MONTH}
_HI["ritu"] = ["वसंत", "ग्रीष्म", "वर्षा", "शरद", "हेमंत", "शिशिर"]


def name3(kind: str, idx: int) -> Tuple[str, str, str]:
    """(English, Bengali, Hindi) name of a month / ritu / ayana / paksha / samvatsara."""
    en, bn = _PAIRS[kind][idx]
    return en, bn, _HI[kind][idx]


def _n3(kind: str, idx: int) -> Dict:
    en, bn, hi = name3(kind, idx)
    return {"index": idx, "en": en, "bn": bn, "hi": hi}


def safe_describe(d: date, loc: Location) -> Dict:
    """describe(), but at the very edges of the supported years (1 and 9999) returns a note instead of failing."""
    try:
        return describe(d, loc)
    except (OverflowError, ValueError):
        return {"unavailable": "Hindu calendar needs the neighbouring days; not available at the very edge of the supported years (1 and 9999)."}


def describe(d: date, loc: Location) -> Dict:
    """JSON-ready Hindu calendar entry for one civil day (names in English, Bengali, Hindi)."""
    c = day_calendar(d, loc)
    sol = c["solar"]
    bd = bangladesh_bengali_date(d)
    nat = national_saka_date(d)
    tamil_year = sol["tamil"]["month_start"].year + (31 if sol["tamil"]["month_start"].month >= 4 else 30)
    out = {
        "method": "Drik (modern ephemeris, Lahiri ayanamsa); evaluated at local sunrise",
        "date": d.isoformat(),
        "lunisolar": {
            "amanta_month": {**_n3("lunar", c["amanta_month"]), "adhika": c["adhika"]},
            "purnimanta_month": {**_n3("lunar", c["purnimanta_month"]), "adhika": c["purnimanta_adhika"]},
            "paksha": _n3("paksha", c["paksha"]),
            "tithi_number": c["tithi_number"],
            "tithi_in_paksha": c["tithi_in_paksha"],
            "tithi_spans_two_sunrises": c["tithi_vriddhi"],
            "tithi_repeated_from_previous_sunrise": c["tithi_repeated_from_yesterday"],
            "skipped_tithi_number": c["skipped_tithi"],
            "month_starts": A.format_jd(c["month_start_jd"], loc.tz, "%Y-%m-%d %H:%M"),
            "month_ends": A.format_jd(c["month_end_jd"], loc.tz, "%Y-%m-%d %H:%M"),
            "kshaya_month_warning": c["kshaya_month_warning"],
        },
        "eras": {
            "vikram_samvat_chaitradi": c["vikram_chaitradi"], "vikram_samvat_kartikadi_gujarat": c["vikram_kartikadi"],
            "shaka": c["shaka"], "kali_yuga": c["kali"],
            "samvatsara": {**_n3("samvatsara", c["samvatsara_index"]), "number": c["samvatsara_index"] + 1,
                           "note": "60-year cycle by the Shaka-year rule (Ugadi/South-Indian). Some North-Indian almanacs name the year differently."},
        },
        "ritu_lunar": _n3("ritu", c["ritu_lunar"]), "ritu_solar": _n3("ritu", c["ritu_solar"]),
        "ayana": _n3("ayana", c["ayana"]),
        "solar_calendars": {
            "bengali_west_bengal": {"year": sol["bengali"]["year"], "month": _n3("bengali", sol["bengali"]["month_index"]),
                                    "day": sol["bengali"]["day"], "rule": "Surya-Siddhanta panjika: day after sankranti (before midnight) or the day after that"},
            "bengali_bangladesh": {"year": bd["year"], "month": _n3("bengali", bd["month_index"]), "day": bd["day"],
                                   "rule": "Revised Bangla calendar (Bangla Academy), fixed civil year from 14 April"},
            "tamil": {"year_thiruvalluvar": tamil_year, "month": _n3("tamil", sol["tamil"]["month_index"]), "day": sol["tamil"]["day"],
                      "rule": "month starts the day of sankranti if it falls before sunset, else the next day"},
            "malayalam_kollam": {"year": sol["malayalam"]["year"], "month": _n3("malayalam", sol["malayalam"]["month_index"]),
                                 "day": sol["malayalam"]["day"], "rule": "month starts the day of sankranti if before aparahna, else next day"},
            "odia": {"month": _n3("odia", sol["odia"]["month_index"]), "day": sol["odia"]["day"],
                     "rule": "month starts on the sankranti day"},
            "indian_national_saka": {"year": nat["year"], "month": _n3("saka", nat["month_index"]), "day": nat["day"],
                                     "rule": "civil calendar of India (1957): Chaitra 1 = 22 March, 21 March in leap years"},
        },
    }
    return out
