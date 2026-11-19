# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Readable (English / Bengali / Hindi) text for the Hindu calendar and festival list."""
from __future__ import annotations

from datetime import date

from . import hindu_calendar as H
from .location import Location


def T(en: str, bn: str, hi: str) -> str:
    return f"\x01{en}\x02{bn}\x04{hi}\x03"


def _nm(kind: str, idx: int) -> str:
    return T(*H.name3(kind, idx))


def calendar_block(o, d: date, loc: Location, title: bool = True) -> None:
    """Add the Hindu-calendar section for one civil day to Out `o`."""
    from .report import _title
    if title:
        _title(o, "Hindu calendar (panchang-makers' reckoning)", "হিন্দু পঞ্জিকা (পঞ্জিকাকারদের হিসাব)", "हिंदू कैलेंडर (पंचांगकारों की गणना)")
    try:
        c = H.day_calendar(d, loc)
    except (OverflowError, ValueError):
        o.add("(Hindu calendar not available at the very edge of the supported years.)", "(সমর্থিত বছরের একেবারে প্রান্তে হিন্দু পঞ্জিকা পাওয়া যায় না।)", "(समर्थित वर्षों के सिरे पर हिंदू कैलेंडर उपलब्ध नहीं।)")
        return
    sol = c["solar"]
    bd = H.bangladesh_bengali_date(d)
    nat = H.national_saka_date(d)
    adh = T(" (Adhika - extra month)", " (অধিক মাস)", " (अधिक मास)") if c["adhika"] else ""
    padh = T(" (Adhika)", " (অধিক)", " (अधिक)") if c["purnimanta_adhika"] else ""
    o.add(f"Lunar month (Amanta): {_nm('lunar', c['amanta_month'])}{adh}  |  (Purnimanta): {_nm('lunar', c['purnimanta_month'])}{padh}",
          f"চান্দ্র মাস (অমান্ত): {_nm('lunar', c['amanta_month'])}{adh}  |  (পূর্ণিমান্ত): {_nm('lunar', c['purnimanta_month'])}{padh}",
          f"चांद्र मास (अमांत): {_nm('lunar', c['amanta_month'])}{adh}  |  (पूर्णिमांत): {_nm('lunar', c['purnimanta_month'])}{padh}")
    o.add(f"Paksha: {_nm('paksha', c['paksha'])}  |  Tithi (at sunrise): {c['tithi_in_paksha']} of the paksha (overall no. {c['tithi_number']}/30)",
          f"পক্ষ: {_nm('paksha', c['paksha'])}  |  তিথি (সূর্যোদয়ে): পক্ষের {c['tithi_in_paksha']} নম্বর (মোট {c['tithi_number']}/৩০)",
          f"पक्ष: {_nm('paksha', c['paksha'])}  |  तिथि (सूर्योदय पर): पक्ष की {c['tithi_in_paksha']} (कुल {c['tithi_number']}/30)")
    if c["tithi_repeated_from_yesterday"]:
        o.add("  * This tithi was also running at yesterday's sunrise (tithi vriddhi).",
              "  * এই তিথি গতকালের সূর্যোদয়েও ছিল (তিথি বৃদ্ধি)।", "  * यही तिथि कल सूर्योदय पर भी थी (तिथि वृद्धि)।")
    if c["skipped_tithi"]:
        o.add(f"  * Tithi no. {c['skipped_tithi']} will not touch any sunrise (tithi kshaya).",
              f"  * {c['skipped_tithi']} নম্বর তিথি কোনো সূর্যোদয় ছোঁবে না (তিথি ক্ষয়)।",
              f"  * तिथि संख्या {c['skipped_tithi']} किसी सूर्योदय को नहीं छुएगी (तिथि क्षय)।")
    if c["kshaya_month_warning"]:
        o.add("  * This lunar month is a Kshaya (lost) month - very rare; almanacs may differ.",
              "  * এটি ক্ষয় মাস (খুব বিরল) - পঞ্জিকাভেদে মতভেদ থাকতে পারে।", "  * यह क्षय मास है (बहुत दुर्लभ) - पंचांगों में अंतर हो सकता है।")
    o.add(f"Vikram Samvat {c['vikram_chaitradi']} (Gujarat/Kartikadi: {c['vikram_kartikadi']})  |  Shaka {c['shaka']}  |  Kali Yuga {c['kali']}",
          f"বিক্রম সংবৎ {c['vikram_chaitradi']} (গুজরাট/কার্তিকাদি: {c['vikram_kartikadi']})  |  শকাব্দ {c['shaka']}  |  কলিযুগ {c['kali']}",
          f"विक्रम संवत {c['vikram_chaitradi']} (गुजरात/कार्तिकादि: {c['vikram_kartikadi']})  |  शक {c['shaka']}  |  कलियुग {c['kali']}")
    o.add(f"Samvatsara (60-year cycle, Shaka rule): {_nm('samvatsara', c['samvatsara_index'])} (no. {c['samvatsara_index'] + 1})",
          f"সংবৎসর (৬০ বছরের চক্র, শক নিয়ম): {_nm('samvatsara', c['samvatsara_index'])} ({c['samvatsara_index'] + 1} নম্বর)",
          f"संवत्सर (60 वर्ष का चक्र, शक नियम): {_nm('samvatsara', c['samvatsara_index'])} (क्रमांक {c['samvatsara_index'] + 1})")
    o.add(f"Ritu: {_nm('ritu', c['ritu_lunar'])} (by lunar month) / {_nm('ritu', c['ritu_solar'])} (by Sun)  |  Ayana: {_nm('ayana', c['ayana'])}",
          f"ঋতু: {_nm('ritu', c['ritu_lunar'])} (চান্দ্র মাসে) / {_nm('ritu', c['ritu_solar'])} (সূর্য অনুযায়ী)  |  অয়ন: {_nm('ayana', c['ayana'])}",
          f"ऋतु: {_nm('ritu', c['ritu_lunar'])} (चांद्र मास से) / {_nm('ritu', c['ritu_solar'])} (सूर्य से)  |  अयन: {_nm('ayana', c['ayana'])}")
    o.raw()
    o.add("Solar (Sauramana) calendars:", "সৌর পঞ্জিকা:", "सौर पंचांग:")
    ty = sol["tamil"]["month_start"].year + (31 if sol["tamil"]["month_start"].month >= 4 else 30)
    rows = [
        (T("Bengali - West Bengal", "বাংলা - পশ্চিমবঙ্গ", "बंगाली - पश्चिम बंगाल"), sol["bengali"]["day"], _nm("bengali", sol["bengali"]["month_index"]), f"{T('Bangabda', 'বঙ্গাব্দ', 'बंगाब्द')} {sol['bengali']['year']}"),
        (T("Bengali - Bangladesh", "বাংলা - বাংলাদেশ", "बंगाली - बांग्लादेश"), bd["day"], _nm("bengali", bd["month_index"]), f"{T('Bangabda', 'বঙ্গাব্দ', 'बंगाब्द')} {bd['year']}"),
        (T("Tamil", "তামিল", "तमिल"), sol["tamil"]["day"], _nm("tamil", sol["tamil"]["month_index"]), f"{T('Thiruvalluvar year', 'তিরুভাল্লুভর বর্ষ', 'तिरुवल्लुवर वर्ष')} {ty}"),
        (T("Malayalam", "মালয়ালম", "मलयालम"), sol["malayalam"]["day"], _nm("malayalam", sol["malayalam"]["month_index"]), f"{T('Kollam year', 'কোল্লাম বর্ষ', 'कोल्लम वर्ष')} {sol['malayalam']['year']}"),
        (T("Odia", "ওড়িয়া", "ओड़िया"), sol["odia"]["day"], _nm("odia", sol["odia"]["month_index"]), ""),
        (T("Indian National (Saka)", "ভারতীয় জাতীয় (শক)", "भारतीय राष्ट्रीय (शक)"), nat["day"], _nm("saka", nat["month_index"]), f"{T('Saka', 'শক', 'शक')} {nat['year']}"),
    ]
    for label, day, month, year in rows:
        o.add(f"   {label}: {day} {month} {year}".rstrip(), f"   {label}: {day} {month} {year}".rstrip(), f"   {label}: {day} {month} {year}".rstrip())
    o.add("(Method: modern ephemeris 'Drik' with Lahiri ayanamsa; the older Surya Siddhanta/Vakya reckonings can differ by a tithi on some days.)",
          "(পদ্ধতি: আধুনিক এফেমেরিস 'দৃক' ও লাহিড়ি অয়নাংশ; প্রাচীন সূর্যসিদ্ধান্ত/বাক্য গণনায় কোনো কোনো দিন এক তিথির তফাত হতে পারে।)",
          "(विधि: आधुनिक एफेमेरिस 'दृक' व लाहिड़ी अयनांश; पुराने सूर्य सिद्धांत/वाक्य गणना में कुछ दिन एक तिथि का अंतर हो सकता है।)")


def hindu_day_of_birth(chart) -> date:
    """The Hindu day (sunrise to sunrise) of a chart's moment: before local sunrise it still belongs to the previous civil date."""
    from datetime import datetime, timedelta
    d = datetime.fromisoformat(chart["meta"]["local_time"]).date()
    sr = (chart.get("day_times") or {}).get("sunrise_jd")
    if sr is not None and chart["meta"]["jd_ut"] < sr:
        d -= timedelta(days=1)
    return d


def festivals_on(d: date, loc: Location):
    return [f for f in H.festivals_for_year(d.year, loc) if f["date"] == d or d in f.get("alternative_dates", [])]


def render_calendar(d: date, loc: Location, lang: str) -> str:
    from .report import Out, _credit, _disclaimer, _notes
    o = Out(lang)
    o.add(f"HINDU CALENDAR for {d.isoformat()} - {loc.name}", f"হিন্দু পঞ্জিকা {d.isoformat()} - {loc.name}", f"हिंदू कैलेंडर {d.isoformat()} - {loc.name}")
    _notes(o, loc)
    calendar_block(o, d, loc, title=False)
    try:
        fs = festivals_on(d, loc)
    except (OverflowError, ValueError):
        fs = []
    if fs:
        o.raw()
        o.add("Festivals / observances on this day:", "এই দিনের উৎসব/ব্রত:", "इस दिन के पर्व/व्रत:")
        for f in fs:
            alt = "" if f["date"] == d else T(" (alternative date; main date " + f["date"].isoformat() + ")", " (বিকল্প তারিখ; প্রধান তারিখ " + f["date"].isoformat() + ")", " (वैकल्पिक तिथि; मुख्य तिथि " + f["date"].isoformat() + ")")
            o.add(f"   - {f['en']}{alt}", f"   - {f['bn']}{alt}", f"   - {f['hi']}{alt}")
    o.raw()
    _disclaimer(o)
    _credit(o)
    return o.text()


def render_festivals(year: int, loc: Location, lang: str) -> str:
    from .report import Out, _credit, _notes
    o = Out(lang)
    o.add(f"HINDU FESTIVALS {year} - {loc.name}", f"হিন্দু উৎসব {year} - {loc.name}", f"हिंदू पर्व {year} - {loc.name}")
    _notes(o, loc)
    for f in H.festivals_for_year(year, loc):
        alts = f.get("alternative_dates") or []
        extra = ""
        if alts:
            s = ", ".join(a.isoformat() for a in alts)
            extra = T(f"  (some almanacs: {s})", f"  (অন্য পঞ্জিকায়: {s})", f"  (अन्य पंचांगों में: {s})")
        o.add(f"{f['date'].isoformat()}  {f['en']}{extra}", f"{f['date'].isoformat()}  {f['bn']}{extra}", f"{f['date'].isoformat()}  {f['hi']}{extra}")
    o.raw()
    o.add("Dates follow the Drik method for the chosen place; where almanacs differ by a day the other date is shown.",
          "তারিখ নির্বাচিত স্থানের 'দৃক' পদ্ধতিতে; পঞ্জিকাভেদে এক দিনের তফাত থাকলে অন্য তারিখও দেখানো হয়েছে।",
          "तिथियाँ चुने हुए स्थान के 'दृक' तरीके से; पंचांगों में एक दिन का अंतर हो तो दूसरी तिथि भी दिखाई गई है।")
    _credit(o)
    return o.text()
