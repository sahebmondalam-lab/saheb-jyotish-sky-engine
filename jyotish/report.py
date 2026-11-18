# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Plain-text reports in English (en), Bengali (bn), Hindi (hi), en+bn (both) or all three (all)."""
from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Dict, List, Optional

from . import astro as A
from . import dasha as D
from . import data_hi as HIN
from . import transits as TR
from .data import *  # noqa: F401,F403
from .location import Location
from .panchang import day_panchang, day_times, panchang_at

LANGS = ("en", "bn", "hi", "both", "all")
_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
SIGN_ABBR = ["Mes", "Vri", "Mit", "Kar", "Sim", "Kan", "Tul", "Vrs", "Dha", "Mak", "Kum", "Mee"]

_SENT = re.compile("\x01(.*?)\x02(.*?)\x04(.*?)\x03", re.S)


def _resolve(s: str, which: int) -> str:
    return _SENT.sub(lambda m: m.group(which), s)


class Out:
    """Collects lines. For several languages each line is printed once per language (en, then bn, then hi)."""

    def __init__(self, lang: str):
        if lang not in LANGS:
            raise ValueError(f"lang must be one of {', '.join(LANGS)}")
        self.lang = lang
        self.lines: List[str] = []

    def add(self, en: str = "", bn: Optional[str] = None, hi: Optional[str] = None, indent: int = 0) -> None:
        pad = " " * indent
        bn = en if bn is None else bn
        hi = en if hi is None else hi
        if self.lang in ("en", "both", "all"):
            self.lines.append(pad + _resolve(en, 1))
        if self.lang in ("bn", "both", "all"):
            line = _resolve(bn, 2).translate(_BN_DIGITS)
            self.lines.append(pad + line.replace("CC BY-NC-SA ৪.০", "CC BY-NC-SA 4.0"))
        if self.lang in ("hi", "all"):
            self.lines.append(pad + _resolve(hi, 3))

    def raw(self, text: str = "") -> None:
        self.lines.append(text)

    def nm(self, pair) -> str:
        """A name that becomes its English, Bengali or Hindi form depending on the line's language."""
        return f"\x01{pair[0]}\x02{pair[1]}\x04{HIN.h(pair)}\x03"

    def text(self) -> str:
        return "\n".join(self.lines) + "\n"


def dms(deg: float) -> str:
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(round(((deg - d) * 60 - m) * 60))
    if s == 60:
        s, m = 0, m + 1
    if m == 60:
        m, d = 0, d + 1
    return f"{d}°{m:02d}'{s:02d}\""


def fmt_jd(jd: Optional[float], tz) -> str:
    if jd is None:
        return "-"
    return A.format_jd(jd, tz, "%Y-%m-%d %H:%M")


def fmt_day(jd: float, tz) -> str:
    return A.format_jd(jd, tz, "%Y-%m-%d")


def _title(o: Out, en: str, bn: str, hi: str) -> None:
    o.raw()
    o.add(f"== {en} ==", f"== {bn} ==", f"== {hi} ==")


def _notes(o: "Out", loc) -> None:
    """Show assumptions made for this report (unknown time, approximate zone, out-of-range year...)."""
    if not getattr(loc, "notes", None):
        return
    o.raw()
    o.add("NOTES ON ASSUMPTIONS:", "ধরে নেওয়া বিষয়গুলো (সতর্কতা):", "मानी गई बातें (सावधानी):")
    for n in loc.notes:
        o.add("  * " + n, "  * " + n, "  * " + n)     # notes are written in English


def _tithi_name(idx: int):
    n = idx % 15
    if n == 14:
        return TITHI_FULL if idx == 14 else TITHI_NEW
    return TITHI[n]


def _karana_name(k: int):
    if k in KARANA_FIXED:
        return KARANA_FIXED[k]
    return KARANA_MOVABLE[(k - 1) % 7]


def _credit(o: Out) -> None:
    o.add(CREDIT[0], CREDIT[1], HIN.CREDIT_HI)


def _disclaimer(o: Out) -> None:
    o.add(DISCLAIMER[0], DISCLAIMER[1], HIN.DISCLAIMER_HI)


def south_indian_grid(chart: Dict) -> List[str]:
    cells = {s: [] for s in range(12)}
    cells[chart["lagna"]["sign"]].append("Asc")
    for g, p in chart["planets"].items():
        cells[p["sign"]].append(PLANET_ABBR[g] + ("(R)" if p["retrograde"] and g not in ("Rahu", "Ketu") else ""))
    layout = [[11, 0, 1, 2], [10, None, None, 3], [9, None, None, 4], [8, 7, 6, 5]]
    w = 13
    sep = "+" + "+".join(["-" * w] * 4) + "+"
    out = [sep]
    for row in layout:
        blocks = []
        for s in row:
            if s is None:
                blocks.append([""])
                continue
            lines = [SIGN_ABBR[s]]
            items = cells[s]
            for i in range(0, len(items), 3):
                lines.append(" ".join(items[i:i + 3]))
            blocks.append(lines)
        h = max(3, max(len(b) for b in blocks))
        for k in range(h):
            out.append("|" + "|".join((b[k] if k < len(b) else "").center(w) for b in blocks) + "|")
        out.append(sep)
    return out


def render_kundli(chart: Dict, fc: Optional[Dict], lang: str, now_jd: float, loc: Location) -> str:
    o = Out(lang)
    tz = loc.tz
    meta, lag, pl = chart["meta"], chart["lagna"], chart["planets"]
    name = meta["name"] or "-"
    nm = o.nm

    o.add("KUNDLI (Vedic birth chart)  |  Saheb Jyotish Sky Engine",
          "কুণ্ডলী (বৈদিক জন্মছক)  |  সাহেব জ্যোতিষ স্কাই ইঞ্জিন",
          "कुंडली (वैदिक जन्म-पत्रिका)  |  साहेब ज्योतिष स्काई इंजन")
    o.add("Created by Saheb Mondal - CC BY-NC-SA 4.0", "নির্মাতা সাহেব মন্ডল - CC BY-NC-SA 4.0",
          "निर्माता साहेब मंडल (Saheb Mondal) - CC BY-NC-SA 4.0")
    _notes(o, loc)

    _title(o, "Birth details", "জন্মের তথ্য", "जन्म विवरण")
    o.add(f"Name: {name}", f"নাম: {name}", f"नाम: {name}")
    lt = meta["local_time"][:16].replace("T", " ")
    o.add(f"Local time: {lt} ({meta['tz']})", f"স্থানীয় সময়: {lt} ({meta['tz']})", f"स्थानीय समय: {lt} ({meta['tz']})")
    o.add(f"Place: {meta['place']}  (lat {meta['lat']:.4f}, lon {meta['lon']:.4f})",
          f"স্থান: {meta['place']}  (অক্ষাংশ {meta['lat']:.4f}, দ্রাঘিমা {meta['lon']:.4f})",
          f"स्थान: {meta['place']}  (अक्षांश {meta['lat']:.4f}, देशांतर {meta['lon']:.4f})")
    o.add(f"Ayanamsa: {dms(meta['ayanamsa'])} ({meta['ayanamsa_system']})",
          f"অয়নাংশ: {dms(meta['ayanamsa'])} (লাহিড়ী/চিত্রপক্ষ)",
          f"अयनांश: {dms(meta['ayanamsa'])} (लाहिड़ी/चित्रपक्ष)")

    _title(o, "Your core signs", "আপনার মূল রাশি ও নক্ষত্র", "आपकी मुख्य राशियाँ और नक्षत्र")
    moon, sun = pl["Moon"], pl["Sun"]
    o.add(f"Lagna (Ascendant): {nm(RASHI[lag['sign']])} {dms(lag['degree'])}",
          f"লগ্ন: {nm(RASHI[lag['sign']])} {dms(lag['degree'])}",
          f"लग्न: {nm(RASHI[lag['sign']])} {dms(lag['degree'])}")
    o.add(f"   {RASHI_TEXT[lag['sign']][0]}", f"   {RASHI_TEXT[lag['sign']][1]}", f"   {HIN.RASHI_TEXT_HI[lag['sign']]}")
    o.add(f"Moon sign (Janma Rashi): {nm(RASHI[moon['sign']])} {dms(moon['degree'])}",
          f"জন্মরাশি (চন্দ্ররাশি): {nm(RASHI[moon['sign']])} {dms(moon['degree'])}",
          f"जन्मराशि (चंद्र राशि): {nm(RASHI[moon['sign']])} {dms(moon['degree'])}")
    o.add(f"   {RASHI_TEXT[moon['sign']][0]}", f"   {RASHI_TEXT[moon['sign']][1]}", f"   {HIN.RASHI_TEXT_HI[moon['sign']]}")
    lord = DASHA_ORDER[moon["nakshatra"] % 9]
    mn = moon["nakshatra"]
    o.add(f"Birth star (Janma Nakshatra): {nm(NAKSHATRA[mn])}, pada {moon['pada']}, ruled by {nm(PLANET[lord])}",
          f"জন্মনক্ষত্র: {nm(NAKSHATRA[mn])}, পাদ {moon['pada']}, অধিপতি {nm(PLANET[lord])}",
          f"जन्म नक्षत्र: {nm(NAKSHATRA[mn])}, चरण {moon['pada']}, स्वामी {nm(PLANET[lord])}")
    o.add(f"   {NAKSHATRA_TEXT[mn][0]}", f"   {NAKSHATRA_TEXT[mn][1]}", f"   {HIN.NAKSHATRA_TEXT_HI[mn]}")
    o.add(f"Sun sign (Surya Rashi, sidereal): {nm(RASHI[sun['sign']])}",
          f"সূর্যরাশি (নিরয়ন): {nm(RASHI[sun['sign']])}",
          f"सूर्य राशि (निरयण): {nm(RASHI[sun['sign']])}")
    w = chart["western"]
    o.add(f"Western (tropical) signs - Sun: {WESTERN[w['sun']]}, Moon: {WESTERN[w['moon']]}, Rising: {WESTERN[w['ascendant']]}",
          f"পাশ্চাত্য (সায়ন) রাশি - সূর্য: {RASHI[w['sun']][1]}, চন্দ্র: {RASHI[w['moon']][1]}, লগ্ন: {RASHI[w['ascendant']][1]}",
          f"पाश्चात्य (सायन) राशियाँ - सूर्य: {HIN.h(RASHI[w['sun']])}, चंद्र: {HIN.h(RASHI[w['moon']])}, लग्न: {HIN.h(RASHI[w['ascendant']])}")

    _title(o, "Planet positions (sidereal, Lahiri)", "গ্রহস্থিতি (নিরয়ন, লাহিড়ী)", "ग्रह स्थिति (निरयण, लाहिड़ी)")
    for g in A.GRAHAS:
        p = pl[g]
        e_en, e_bn, e_hi = [], [], []
        if p["retrograde"]:
            e_en.append("retrograde"); e_bn.append("বক্রী"); e_hi.append("वक्री")
        if g in ("Rahu", "Ketu"):
            e_en.append("mean node"); e_bn.append("গড় নোড"); e_hi.append("औसत नोड")
        if p["dignity"] != "neutral":
            e_en.append(DIGNITY[p["dignity"]][0]); e_bn.append(DIGNITY[p["dignity"]][1]); e_hi.append(HIN.DIGNITY_HI[p["dignity"]])
        nk = p["nakshatra"]
        o.add(f"{PLANET[g][0]:20s} {RASHI_SHORT[p['sign']]:10s} {dms(p['degree']):>10s} | {NAKSHATRA[nk][0]} pada {p['pada']} | house {p['house']}"
              + (f" | {', '.join(e_en)}" if e_en else ""),
              f"{PLANET[g][1]}: {RASHI[p['sign']][1]} {dms(p['degree'])} | {NAKSHATRA[nk][1]} পাদ {p['pada']} | {p['house']} নম্বর ভাব"
              + (f" | {', '.join(e_bn)}" if e_bn else ""),
              f"{nm(PLANET[g])}: {nm(RASHI[p['sign']])} {dms(p['degree'])} | {nm(NAKSHATRA[nk])} चरण {p['pada']} | भाव {p['house']}"
              + (f" | {', '.join(e_hi)}" if e_hi else ""))
    o.raw()
    o.add("Rashi chart (South-Indian style, fixed signs; Asc = Lagna, (R) = retrograde)",
          "রাশিচক্র (দক্ষিণ ভারতীয় ধরন; Asc = লগ্ন, (R) = বক্রী)",
          "राशि चक्र (दक्षिण भारतीय शैली; Asc = लग्न, (R) = वक्री)")
    for ln in south_indian_grid(chart):
        o.raw(ln)

    pc = chart["panchang"]
    _title(o, "Panchang at birth", "জন্মক্ষণের পঞ্চাঙ্গ", "जन्म-क्षण का पंचांग")
    tn = _tithi_name(pc["tithi_index"])
    pk = PAKSHA[pc["paksha"]]
    o.add(f"Tithi: {nm(tn)} - {nm(pk)} ({pc['tithi_percent_elapsed']:.0f}% elapsed; ends {fmt_jd(pc.get('tithi_end_jd'), tz)})",
          f"তিথি: {nm(tn)} - {nm(pk)} ({pc['tithi_percent_elapsed']:.0f}% অতিক্রান্ত; শেষ {fmt_jd(pc.get('tithi_end_jd'), tz)})",
          f"तिथि: {nm(tn)} - {nm(pk)} ({pc['tithi_percent_elapsed']:.0f}% बीत चुकी; समाप्त {fmt_jd(pc.get('tithi_end_jd'), tz)})")
    pn = NAKSHATRA[pc["nakshatra_index"]]
    o.add(f"Nakshatra: {nm(pn)} (ends {fmt_jd(pc.get('nakshatra_end_jd'), tz)})",
          f"নক্ষত্র: {nm(pn)} (শেষ {fmt_jd(pc.get('nakshatra_end_jd'), tz)})",
          f"नक्षत्र: {nm(pn)} (समाप्त {fmt_jd(pc.get('nakshatra_end_jd'), tz)})")
    py = YOGA[pc["yoga_index"]]
    o.add(f"Yoga: {nm(py)} (ends {fmt_jd(pc.get('yoga_end_jd'), tz)})",
          f"যোগ: {nm(py)} (শেষ {fmt_jd(pc.get('yoga_end_jd'), tz)})",
          f"योग: {nm(py)} (समाप्त {fmt_jd(pc.get('yoga_end_jd'), tz)})")
    kn = _karana_name(pc["karana_index"])
    o.add(f"Karana: {nm(kn)}", f"করণ: {nm(kn)}", f"करण: {nm(kn)}")
    vi = pc["vara_index"]
    o.add(f"Vara (weekday, from sunrise): {nm(VARA[vi])}, lord {nm(PLANET[VARA_LORD[vi]])}",
          f"বার (সূর্যোদয় থেকে): {nm(VARA[vi])}, অধিপতি {nm(PLANET[VARA_LORD[vi]])}",
          f"वार (सूर्योदय से): {nm(VARA[vi])}, स्वामी {nm(PLANET[VARA_LORD[vi]])}")
    mp = MOON_PHASE[pc["moon_phase_index"]]
    il = pc["moon_illumination"] * 100
    o.add(f"Moon: {mp[0]}, {il:.0f}% lit", f"চাঁদ: {mp[1]}, {il:.0f}% আলোকিত", f"चंद्रमा: {HIN.h(mp)}, {il:.0f}% प्रकाशित")
    dt_ = chart["day_times"]
    if dt_.get("sunrise_jd"):
        sr, ss = fmt_jd(dt_["sunrise_jd"], tz)[11:], fmt_jd(dt_["sunset_jd"], tz)[11:]
        o.add(f"Sunrise {sr}  Sunset {ss}  (local)", f"সূর্যোদয় {sr}  সূর্যাস্ত {ss}  (স্থানীয়)", f"सूर्योदय {sr}  सूर्यास्त {ss}  (स्थानीय)")

    _title(o, "Yogas and doshas found (classical rules)", "প্রাপ্ত যোগ ও দোষ (ক্লাসিক্যাল নিয়ম)", "प्राप्त योग और दोष (शास्त्रीय नियम)")
    if not chart["yogas"]:
        o.add("None of the rules checked here were triggered.", "এখানে যাচাই করা কোনো নিয়ম মেলেনি।",
              "यहाँ जाँचा गया कोई नियम नहीं मिला।")
    for key in chart["yogas"]:
        nm_pair, tx = YOGA_TEXT[key]
        hn, ht = HIN.YOGA_TEXT_HI[key]
        o.add(f"* {nm_pair[0]}", f"* {nm_pair[1]}", f"* {hn}")
        o.add(f"    {tx[0]}", f"    {tx[1]}", f"    {ht}")

    _title(o, "Vimshottari Dasha (planetary periods)", "বিংশোত্তরী দশা (গ্রহের কালচক্র)", "विंशोत्तरी दशा (ग्रहों के कालखंड)")
    bal = chart["dasha"]["balance"]
    o.add(f"Balance at birth: {nm(PLANET[bal['lord']])} dasha, {bal['years_left']:.2f} years left",
          f"জন্মকালে অবশিষ্ট: {nm(PLANET[bal['lord']])} দশা, {bal['years_left']:.2f} বছর বাকি",
          f"जन्म के समय शेष: {nm(PLANET[bal['lord']])} दशा, {bal['years_left']:.2f} वर्ष बाकी")
    cur = D.find_period(chart["dasha"]["periods"], now_jd)
    if cur:
        m, a = cur["maha"], cur["antar"]
        ms_, me_, as_, ae_ = fmt_day(m["start"], tz), fmt_day(m["end"], tz), fmt_day(a["start"], tz), fmt_day(a["end"], tz)
        o.add(f"Running now: {nm(PLANET[m['lord']])} Mahadasha ({ms_} to {me_}), {nm(PLANET[a['lord']])} Antardasha ({as_} to {ae_})",
              f"এখন চলছে: {nm(PLANET[m['lord']])} মহাদশা ({ms_} থেকে {me_}), {nm(PLANET[a['lord']])} অন্তর্দশা ({as_} থেকে {ae_})",
              f"अभी चल रही: {nm(PLANET[m['lord']])} महादशा ({ms_} से {me_}), {nm(PLANET[a['lord']])} अंतर्दशा ({as_} से {ae_})")
        o.add(f"   Mahadasha theme: {DASHA_TEXT[m['lord']][0]}", f"   মহাদশার বিষয়: {DASHA_TEXT[m['lord']][1]}",
              f"   महादशा का विषय: {HIN.DASHA_TEXT_HI[m['lord']]}")
        o.add(f"   Antardasha flavour: {DASHA_TEXT[a['lord']][0]}", f"   অন্তর্দশার আভাস: {DASHA_TEXT[a['lord']][1]}",
              f"   अंतर्दशा का आभास: {HIN.DASHA_TEXT_HI[a['lord']]}")
    horizon = now_jd + (fc["end"] - fc["start"] if fc else 5 * 365.25)
    o.add("Upcoming sub-periods in the forecast window:", "পূর্বাভাস-সময়ের মধ্যে আসন্ন উপ-দশা:",
          "पूर्वानुमान अवधि की आगामी उप-दशाएँ:")
    for p in chart["dasha"]["periods"]:
        for a in p["antar"]:
            if a["end"] > now_jd and a["start"] < horizon:
                s_, e_ = fmt_day(max(a["start"], now_jd), tz), fmt_day(a["end"], tz)
                line = f"   {s_} -> {e_}  {nm(PLANET[p['lord']])} / {nm(PLANET[a['lord']])}"
                o.add(line, line, line)

    if fc:
        ms = chart["moon_sign"]
        fs, fe = fmt_day(fc["start"], tz), fmt_day(fc["end"], tz)
        _title(o, f"Forecast window {fs} -> {fe} (transits counted from your Moon sign)",
               f"পূর্বাভাস {fs} -> {fe} (গোচর, আপনার জন্মরাশি থেকে গণনা)",
               f"पूर्वानुमान {fs} -> {fe} (गोचर, आपकी जन्मराशि से गिना गया)")
        o.add("Where planets are today (house counted from Moon):", "আজ গ্রহগুলো কোথায় (চন্দ্র থেকে ভাব):",
              "आज ग्रह कहाँ हैं (चंद्र से भाव):")
        for g, v in TR.current_gochar(now_jd, ms).items():
            o.add(f"   {PLANET[g][0]:20s} {RASHI_SHORT[v['sign']]:10s} {v['degree']:5.1f}°  house {v['house_from_moon']}",
                  f"   {PLANET[g][1]}: {RASHI[v['sign']][1]} {v['degree']:.1f}° - {v['house_from_moon']} নম্বর ভাব",
                  f"   {nm(PLANET[g])}: {nm(RASHI[v['sign']])} {v['degree']:.1f}° - भाव {v['house_from_moon']}")
        o.raw()
        for g in ("Saturn", "Jupiter", "Rahu"):
            o.add(f"{PLANET[g][0]} sign changes:", f"{PLANET[g][1]}-এর রাশি পরিবর্তন:", f"{HIN.h(PLANET[g])} की राशि बदल:")
            for s in fc["timelines"][g]:
                tag, htag = GOCHAR_TEXT[s["favourable"]], HIN.GOCHAR_TEXT_HI[s["favourable"]]
                a_, b_ = fmt_day(s["start"], tz), fmt_day(s["end"], tz)
                o.add(f"   {a_} -> {b_}  {RASHI_SHORT[s['sign']]:10s} house {s['house_from_moon']:2d}  {tag[0]}",
                      f"   {a_} -> {b_}  {RASHI[s['sign']][1]} - {s['house_from_moon']} নম্বর ভাব - {tag[1]}",
                      f"   {a_} -> {b_}  {nm(RASHI[s['sign']])} - भाव {s['house_from_moon']} - {htag}")
            if g == "Rahu":
                o.add("   (Ketu is always exactly opposite Rahu.)", "   (কেতু সর্বদা রাহুর ঠিক বিপরীতে।)",
                      "   (केतु हमेशा राहु के ठीक सामने रहता है।)")
        o.raw()
        o.add("Sade Sati / Dhaiya windows in this period:", "এই সময়ে সাড়েসাতি / ঢাইয়ার সময়সীমা:",
              "इस अवधि में साढ़ेसाती / ढैया का समय:")
        if not fc["saturn_phases"]:
            o.add("   none", "   নেই", "   कोई नहीं")
        for ph in fc["saturn_phases"]:
            tx = SADE_SATI_TEXT[ph["house"]]
            a_, b_ = fmt_day(ph["start"], tz), fmt_day(ph["end"], tz)
            o.add(f"   {a_} -> {b_}: {tx[0]}", f"   {a_} -> {b_}: {tx[1]}", f"   {a_} -> {b_}: {HIN.SADE_SATI_TEXT_HI[ph['house']]}")

    from .report_deep import render_deep
    render_deep(o, chart)

    _title(o, "Numerology", "সংখ্যাতত্ত্ব", "अंक ज्योतिष")
    nu = chart["numerology"]
    for key, en_l, bn_l, hi_l in (("mulank", "Birth number (Mulank)", "মূলাঙ্ক", "मूलांक"),
                                   ("bhagyank", "Destiny number (Bhagyank)", "ভাগ্যাঙ্ক", "भाग्यांक")):
        n = nu[key]
        planet, en_t, bn_t = NUMEROLOGY[n]
        o.add(f"{en_l}: {n} ({nm(PLANET[planet])}) - {en_t}", f"{bn_l}: {n} ({nm(PLANET[planet])}) - {bn_t}",
              f"{hi_l}: {n} ({nm(PLANET[planet])}) - {HIN.NUMEROLOGY_HI[n]}")

    _title(o, "Please read", "অনুগ্রহ করে পড়ুন", "कृपया पढ़ें")
    _disclaimer(o)
    o.raw()
    _credit(o)
    return o.text()


def render_panchang(d: date, loc: Location, lang: str) -> str:
    o = Out(lang)
    nm = o.nm
    tz = loc.tz
    p = day_panchang(d, loc)
    o.add(f"PANCHANG for {d.isoformat()} - {loc.name}", f"পঞ্চাঙ্গ {d.isoformat()} - {loc.name}",
          f"पंचांग {d.isoformat()} - {loc.name}")
    _notes(o, loc)
    o.add("(Tithi/nakshatra/yoga/karana are those running at local sunrise.)",
          "(তিথি/নক্ষত্র/যোগ/করণ স্থানীয় সূর্যোদয়ের সময়ের।)",
          "(तिथि/नक्षत्र/योग/करण स्थानीय सूर्योदय के समय के हैं।)")
    o.raw()
    tn = _tithi_name(p["tithi_index"])
    pk = PAKSHA[p["paksha"]]
    te, ne, ye = fmt_jd(p.get("tithi_end_jd"), tz), fmt_jd(p.get("nakshatra_end_jd"), tz), fmt_jd(p.get("yoga_end_jd"), tz)
    o.add(f"Vara: {nm(VARA[p['vara_index']])}", f"বার: {nm(VARA[p['vara_index']])}", f"वार: {nm(VARA[p['vara_index']])}")
    tn2 = _tithi_name((p["tithi_index"] + 1) % 30)
    o.add(f"Tithi: {nm(tn)} - {nm(pk)}  (until {te}, then {nm(tn2)})", f"তিথি: {nm(tn)} - {nm(pk)}  (শেষ {te}, তারপর {nm(tn2)})",
          f"तिथि: {nm(tn)} - {nm(pk)}  (तक {te}, फिर {nm(tn2)})")
    nk = NAKSHATRA[p["nakshatra_index"]]
    nk2 = NAKSHATRA[(p["nakshatra_index"] + 1) % 27]
    o.add(f"Nakshatra: {nm(nk)} pada {p['nakshatra_pada']}  (until {ne}, then {nm(nk2)})",
          f"নক্ষত্র: {nm(nk)} পাদ {p['nakshatra_pada']}  (শেষ {ne}, তারপর {nm(nk2)})",
          f"नक्षत्र: {nm(nk)} चरण {p['nakshatra_pada']}  (तक {ne}, फिर {nm(nk2)})")
    yg = YOGA[p["yoga_index"]]
    yg2 = YOGA[(p["yoga_index"] + 1) % 27]
    o.add(f"Yoga: {nm(yg)}  (until {ye}, then {nm(yg2)})", f"যোগ: {nm(yg)}  (শেষ {ye}, তারপর {nm(yg2)})", f"योग: {nm(yg)}  (तक {ye}, फिर {nm(yg2)})")
    kr = _karana_name(p["karana_index"])
    o.add(f"Karana: {nm(kr)}", f"করণ: {nm(kr)}", f"करण: {nm(kr)}")
    o.add(f"Moon in {nm(RASHI[p['moon_sign']])}, Sun in {nm(RASHI[p['sun_sign']])} (sidereal)",
          f"চন্দ্র {nm(RASHI[p['moon_sign']])} রাশিতে, সূর্য {nm(RASHI[p['sun_sign']])} রাশিতে (নিরয়ন)",
          f"चंद्र {nm(RASHI[p['moon_sign']])} राशि में, सूर्य {nm(RASHI[p['sun_sign']])} राशि में (निरयण)")
    mp = MOON_PHASE[p["moon_phase_index"]]
    il = p["moon_illumination"] * 100
    o.add(f"Moon phase: {mp[0]} ({il:.0f}% lit)", f"চাঁদের দশা: {mp[1]} ({il:.0f}% আলোকিত)", f"चंद्रमा की कला: {HIN.h(mp)} ({il:.0f}% प्रकाशित)")
    o.raw()
    if p.get("sunrise_jd") is None or p.get("sunset_jd") is None:
        o.add("Sun does not rise/set on this date at this latitude.", "এই অক্ষাংশে এই তারিখে সূর্য ওঠে/অস্ত যায় না।",
              "इस अक्षांश पर इस तारीख को सूर्य उदय/अस्त नहीं होता।")
    else:
        def span(k):
            a, b = p[k]
            return f"{fmt_jd(a, tz)[11:]} - {fmt_jd(b, tz)[11:]}"
        sr, ss = fmt_jd(p["sunrise_jd"], tz)[11:], fmt_jd(p["sunset_jd"], tz)[11:]
        o.add(f"Sunrise {sr}   Sunset {ss}", f"সূর্যোদয় {sr}   সূর্যাস্ত {ss}", f"सूर्योदय {sr}   सूर्यास्त {ss}")
        o.add(f"Rahu Kaal: {span('rahu_kaal')}   (avoid starting new work)", f"রাহুকাল: {span('rahu_kaal')}   (নতুন কাজ শুরু এড়ানো হয়)",
              f"राहुकाल: {span('rahu_kaal')}   (नया काम शुरू करने से बचा जाता है)")
        o.add(f"Yamaganda: {span('yamaganda')}", f"যমগণ্ড: {span('yamaganda')}", f"यमगंड: {span('yamaganda')}")
        o.add(f"Gulika Kaal: {span('gulika')}", f"গুলিকা কাল: {span('gulika')}", f"गुलिका काल: {span('gulika')}")
        o.add(f"Abhijit Muhurta: {span('abhijit')}   (traditionally auspicious)", f"অভিজিৎ মুহূর্ত: {span('abhijit')}   (ঐতিহ্যগতভাবে শুভ)",
              f"अभिजित मुहूर्त: {span('abhijit')}   (परंपरा में शुभ)")
        o.add(f"Brahma Muhurta: {span('brahma_muhurta')}", f"ব্রাহ্ম মুহূর্ত: {span('brahma_muhurta')}", f"ब्रह्म मुहूर्त: {span('brahma_muhurta')}")
    o.raw()
    _disclaimer(o)
    o.raw()
    _credit(o)
    return o.text()


def render_sky(local_dt: datetime, loc: Location, lang: str) -> str:
    """Snapshot of the sky at one moment: every planet (sidereal + tropical), Moon phase, panchang, sunrise/sunset."""
    o = Out(lang)
    nm = o.nm
    tz = loc.tz
    utc = local_dt.astimezone(timezone.utc)
    jd = A.julian_day(utc)
    pos = A.all_positions(jd)
    ay = A.ayanamsa_lahiri(A.jd_to_tt(jd))
    pc = panchang_at(jd)
    times = day_times(local_dt.date(), loc)
    lt = local_dt.strftime("%Y-%m-%d %H:%M")

    o.add(f"SKY at {lt} ({loc.tz_name}) - {loc.name}", f"আকাশের অবস্থা {lt} ({loc.tz_name}) - {loc.name}",
          f"आकाश की स्थिति {lt} ({loc.tz_name}) - {loc.name}")
    o.add(f"UTC {utc.strftime('%Y-%m-%d %H:%M')}  |  Julian Day {jd:.5f}  |  Ayanamsa (Lahiri) {dms(ay)}",
          f"UTC {utc.strftime('%Y-%m-%d %H:%M')}  |  জুলিয়ান দিন {jd:.5f}  |  অয়নাংশ (লাহিড়ী) {dms(ay)}",
          f"UTC {utc.strftime('%Y-%m-%d %H:%M')}  |  जूलियन दिन {jd:.5f}  |  अयनांश (लाहिड़ी) {dms(ay)}")
    _notes(o, loc)

    _title(o, "Planets: sidereal (Vedic) and tropical (Western) longitude", "গ্রহ: নিরয়ন (বৈদিক) ও সায়ন (পাশ্চাত্য) দ্রাঘিমা",
           "ग्रह: निरयण (वैदिक) और सायन (पाश्चात्य) देशांतर")
    for g in A.GRAHAS:
        p = pos[g]
        sid, trop = p["sidereal"], p["tropical"]
        ss, ts = int(sid // 30) % 12, int(trop // 30) % 12
        nk = int(sid // (360.0 / 27.0)) % 27
        pada = int((sid % (360.0 / 27.0)) // (360.0 / 108.0)) + 1
        sp = p["speed"]
        r_en = "  retrograde" if p["retrograde"] else ""
        r_bn = "  বক্রী" if p["retrograde"] else ""
        r_hi = "  वक्री" if p["retrograde"] else ""
        o.add(f"{PLANET[g][0]:20s} sidereal {RASHI_SHORT[ss]:10s} {dms(sid % 30):>10s} | tropical {WESTERN[ts]:11s} {dms(trop % 30):>10s} | {NAKSHATRA[nk][0]} pada {pada} | {sp:+.3f} deg/day{r_en}",
              f"{PLANET[g][1]}: নিরয়ন {RASHI[ss][1]} {dms(sid % 30)} | সায়ন {RASHI[ts][1]} {dms(trop % 30)} | {NAKSHATRA[nk][1]} পাদ {pada} | {sp:+.3f}°/দিন{r_bn}",
              f"{nm(PLANET[g])}: निरयण {nm(RASHI[ss])} {dms(sid % 30)} | सायन {nm(RASHI[ts])} {dms(trop % 30)} | {nm(NAKSHATRA[nk])} चरण {pada} | {sp:+.3f}°/दिन{r_hi}")

    _title(o, "Panchang and Moon", "পঞ্চাঙ্গ ও চাঁদ", "पंचांग और चंद्रमा")
    tn, pk = _tithi_name(pc["tithi_index"]), PAKSHA[pc["paksha"]]
    te, ne = fmt_jd(pc.get("tithi_end_jd"), tz), fmt_jd(pc.get("nakshatra_end_jd"), tz)
    o.add(f"Tithi: {nm(tn)} - {nm(pk)}  (until {te})", f"তিথি: {nm(tn)} - {nm(pk)}  (শেষ {te})", f"तिथि: {nm(tn)} - {nm(pk)}  (तक {te})")
    nk = NAKSHATRA[pc["nakshatra_index"]]
    o.add(f"Nakshatra: {nm(nk)} pada {pc['nakshatra_pada']}  (until {ne})", f"নক্ষত্র: {nm(nk)} পাদ {pc['nakshatra_pada']}  (শেষ {ne})",
          f"नक्षत्र: {nm(nk)} चरण {pc['nakshatra_pada']}  (तक {ne})")
    yg, kr = YOGA[pc["yoga_index"]], _karana_name(pc["karana_index"])
    o.add(f"Yoga: {nm(yg)}   Karana: {nm(kr)}", f"যোগ: {nm(yg)}   করণ: {nm(kr)}", f"योग: {nm(yg)}   करण: {nm(kr)}")
    wd = (local_dt.weekday() + 1) % 7
    if times.get("sunrise_jd") and jd < times["sunrise_jd"]:
        wd = (wd - 1) % 7
    o.add(f"Vara (Vedic day starts at sunrise): {nm(VARA[wd])}", f"বার (বৈদিক দিন সূর্যোদয়ে শুরু): {nm(VARA[wd])}",
          f"वार (वैदिक दिन सूर्योदय से शुरू): {nm(VARA[wd])}")
    mp = MOON_PHASE[pc["moon_phase_index"]]
    il = pc["moon_illumination"] * 100
    o.add(f"Moon: {mp[0]}, {il:.0f}% lit, {pc['elongation']:.1f} deg ahead of the Sun",
          f"চাঁদ: {mp[1]}, {il:.0f}% আলোকিত, সূর্যের চেয়ে {pc['elongation']:.1f}° এগিয়ে",
          f"चंद्रमा: {HIN.h(mp)}, {il:.0f}% प्रकाशित, सूर्य से {pc['elongation']:.1f}° आगे")
    if times.get("sunrise_jd") and times.get("sunset_jd"):
        sr, ssn = fmt_jd(times["sunrise_jd"], tz)[11:], fmt_jd(times["sunset_jd"], tz)[11:]
        o.add(f"Sunrise {sr}   Sunset {ssn}  (that day, local)", f"সূর্যোদয় {sr}   সূর্যাস্ত {ssn}  (সেই দিন, স্থানীয়)",
              f"सूर्योदय {sr}   सूर्यास्त {ssn}  (उस दिन, स्थानीय)")
    else:
        o.add("Sun does not rise/set on this date at this latitude.", "এই অক্ষাংশে এই তারিখে সূর্য ওঠে/অস্ত যায় না।",
              "इस अक्षांश पर इस तारीख को सूर्य उदय/अस्त नहीं होता।")
    o.raw()
    _disclaimer(o)
    o.raw()
    _credit(o)
    return o.text()


def render_day(d: date, loc: Location, lang: str) -> str:
    """Everything that changes in the sky during one local civil day (00:00-24:00)."""
    from .events import day_events
    o = Out(lang)
    nm = o.nm
    tz = loc.tz
    ev = day_events(d, loc)

    def hm(jd):
        if jd is None:
            return "-"
        dt = A.datetime_from_jd(jd).astimezone(tz)
        return dt.strftime("%H:%M") if dt.date() == d else dt.strftime("%m-%d %H:%M")

    def none():
        o.add("none today", "আজ নেই", "आज कोई नहीं")

    o.add(f"EVENTS IN THE SKY on {d.isoformat()} - {loc.name} (local time)", f"{d.isoformat()} তারিখের আকাশের ঘটনা - {loc.name} (স্থানীয় সময়)",
          f"{d.isoformat()} के आकाश की घटनाएँ - {loc.name} (स्थानीय समय)")
    _notes(o, loc)
    _title(o, "Moon phase moments", "চাঁদের দশার মুহূর্ত", "चंद्र कला के क्षण")
    for e in ev["moon_phases"]:
        pe = PHASE_EVENT[e["phase_index"]]
        o.add(f"{hm(e['jd'])}  {nm(pe)}")
    if not ev["moon_phases"]:
        none()
    _title(o, "Sign changes (sidereal)", "রাশি পরিবর্তন (নিরয়ন)", "राशि परिवर्तन (निरयण)")
    for e in ev["ingresses"]:
        sun = e["planet"] == "Sun"
        o.add(f"{hm(e['jd'])}  {nm(PLANET[e['planet']])}: {nm(RASHI[e['from_sign']])} -> {nm(RASHI[e['to_sign']])}" + ("  = SANKRANTI" if sun else ""),
              f"{hm(e['jd'])}  {nm(PLANET[e['planet']])}: {nm(RASHI[e['from_sign']])} -> {nm(RASHI[e['to_sign']])}" + ("  = সংক্রান্তি" if sun else ""),
              f"{hm(e['jd'])}  {nm(PLANET[e['planet']])}: {nm(RASHI[e['from_sign']])} -> {nm(RASHI[e['to_sign']])}" + ("  = संक्रांति" if sun else ""))
    if not ev["ingresses"]:
        none()
    _title(o, "Retrograde / direct turns", "বক্রী / মার্গী পরিবর্তন", "वक्री / मार्गी परिवर्तन")
    for e in ev["stations"]:
        pl, r = nm(PLANET[e["planet"]]), e["turns"] == "retrograde"
        o.add(f"{hm(e['jd'])}  {pl} turns {'retrograde' if r else 'direct'}", f"{hm(e['jd'])}  {pl} {'বক্রী' if r else 'মার্গী'} হয়",
              f"{hm(e['jd'])}  {pl} {'वक्री' if r else 'मार्गी'} होता है")
    if not ev["stations"]:
        none()

    def seg(title, rows, name):
        _title(o, *title)
        for e in rows:
            n = nm(name(e["index"]))
            a, b = hm(e["start"]), hm(e["end"])
            o.add(f"{n}: {a} to {b}", f"{n}: {a} থেকে {b}", f"{n}: {a} से {b}")

    seg(("Tithi through the day", "দিনভর তিথি", "दिन भर तिथि"), ev["tithi"], _tithi_name)
    seg(("Nakshatra through the day", "দিনভর নক্ষত্র", "दिन भर नक्षत्र"), ev["nakshatra"], lambda i: NAKSHATRA[i])
    seg(("Yoga through the day", "দিনভর যোগ", "दिन भर योग"), ev["yoga"], lambda i: YOGA[i])
    o.raw()
    o.add("Not included: eclipses (this engine does not compute the Moon's latitude).", "অন্তর্ভুক্ত নয়: গ্রহণ (এই ইঞ্জিন চাঁদের অক্ষাংশ হিসাব করে না)।",
          "शामिल नहीं: ग्रहण (यह इंजन चंद्रमा का अक्षांश नहीं निकालता)।")
    o.raw()
    _disclaimer(o)
    o.raw()
    _credit(o)
    return o.text()
