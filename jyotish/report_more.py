# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Readable (English / Bengali / Hindi) text for eclipses (Grahan) and Shadbala, and the extra kundli sections that use them."""
from __future__ import annotations

from typing import Dict, List, Optional

from . import data as D
from . import eclipses as EC
from . import shadbala as SB
from .report_calendar import T


def _t(d: Dict[str, str]) -> str:
    return T(d["en"], d["bn"], d["hi"])


def _pl(o, p: str) -> str:
    return o.nm(D.PLANET[p])


def eclipse_lines(o, e: Dict, with_visibility: bool = True) -> None:
    ti = e["title"]
    mag = e.get("magnitude")
    o.add(f"{ti['en']}  {e['utc']} UTC  (magnitude {mag:.2f})", f"{ti['bn']}  {e['utc']} UTC  (মাত্রা {mag:.2f})", f"{ti['hi']}  {e['utc']} UTC  (परिमाण {mag:.2f})")
    m, s = e["moon"], e["sun"]
    o.add(f"   Sun in {s['rashi']['en']}, Moon in {m['rashi']['en']} ({m['nakshatra']['en']} pada {m['nakshatra']['pada']}); near {e['node_link']['node_name']['en']} ({e['node_link']['distance_deg']}°)",
          f"   সূর্য {s['rashi']['bn']}, চন্দ্র {m['rashi']['bn']} ({m['nakshatra']['bn']} পাদ {m['nakshatra']['pada']}); {e['node_link']['node_name']['bn']}-এর কাছে ({e['node_link']['distance_deg']}°)",
          f"   सूर्य {s['rashi']['hi']}, चंद्र {m['rashi']['hi']} ({m['nakshatra']['hi']} पाद {m['nakshatra']['pada']}); {e['node_link']['node_name']['hi']} के पास ({e['node_link']['distance_deg']}°)")
    v = e.get("visibility") if with_visibility else None
    if v is not None:
        if v.get("visible"):
            gl = v.get("greatest_local") or v.get("local_max") or ""
            o.add(f"   Visible from your place (greatest eclipse about {gl} local time).", f"   আপনার জায়গা থেকে দেখা যাবে (সর্বোচ্চ গ্রাস প্রায় {gl} স্থানীয় সময়ে)।",
                  f"   आपके स्थान से दिखेगा (अधिकतम ग्रहण लगभग {gl} स्थानीय समय)।")
        else:
            o.add("   Not visible from your place.", "   আপনার জায়গা থেকে দেখা যাবে না।", "   आपके स्थान से नहीं दिखेगा।")


def render_eclipses(eclipses: List[Dict], title_en: str, lang: str, loc=None) -> str:
    from .report import Out, _title
    o = Out(lang)
    _title(o, title_en, "গ্রহণ (সূর্য ও চন্দ্র)", "ग्रहण (सूर्य व चंद्र)")
    if not eclipses:
        o.add("No eclipse found.", "কোনো গ্রহণ পাওয়া যায়নি।", "कोई ग्रहण नहीं मिला।")
    for e in eclipses:
        eclipse_lines(o, e, with_visibility=loc is not None)
    o.raw()
    o.add("Times are UTC (greatest eclipse). Computed from the Sun-Moon geometry; accuracy is about a few minutes in 1800-2100 and falls slowly "
          "outside. Traditional sutak/dosha beliefs are not science.",
          "সময় UTC (সর্বোচ্চ গ্রাস)। সূর্য-চন্দ্রের জ্যামিতি থেকে গণনা; ১৮০০-২১০০ সালে কয়েক মিনিটের মধ্যে ঠিক, বাইরে ধীরে কমে। সূতক/দোষের বিশ্বাস বিজ্ঞান নয়।",
          "समय UTC (अधिकतम ग्रहण)। सूर्य-चंद्र ज्यामिति से गणना; 1800-2100 में कुछ मिनट तक सटीक, बाहर धीरे घटती है। सूतक/दोष की मान्यताएँ विज्ञान नहीं।")
    return o.text()


def grahan_block(o, chart: Dict) -> None:
    """Grahan (eclipse) section of a kundli: yoga check and the eclipses closest to the birth."""
    from .report import _title
    pl = chart["planets"]
    _title(o, "Grahan (eclipse) check", "গ্রহণ বিচার", "ग्रहण विचार")
    g = EC.grahan_dosha(pl["Sun"]["sidereal"], pl["Moon"]["sidereal"], pl["Rahu"]["sidereal"], pl["Ketu"]["sidereal"])
    if g["present"]:
        for k in g["kinds"]:
            o.add(f"* {k}", f"* {k}", f"* {k}")
        o.add("  Traditional Grahan yoga: Sun or Moon within 12 degrees of Rahu/Ketu (belief, not science).",
              "  ঐতিহ্যগত গ্রহণ যোগ: সূর্য বা চন্দ্র রাহু/কেতুর ১২° মধ্যে (বিশ্বাস, বিজ্ঞান নয়)।",
              "  पारंपरिक ग्रहण योग: सूर्य या चंद्र राहु/केतु के 12° के भीतर (मान्यता, विज्ञान नहीं)।")
    else:
        o.add("No Grahan yoga: Sun and Moon are not close to Rahu/Ketu.", "গ্রহণ যোগ নেই: সূর্য ও চন্দ্র রাহু/কেতুর কাছে নেই।",
              "ग्रहण योग नहीं: सूर्य व चंद्र राहु/केतु के पास नहीं।")
    try:
        nb = EC.eclipse_near_birth(chart["meta"]["jd_ut"])
    except (OverflowError, ValueError):
        return
    for key, en, bn, hi in (("before", "Eclipse before birth", "জন্মের আগের গ্রহণ", "जन्म से पहले का ग्रहण"),
                            ("after", "Eclipse after birth", "জন্মের পরের গ্রহণ", "जन्म के बाद का ग्रहण")):
        e = nb.get(key)
        if not e:
            continue
        days = e.get("days_before_birth", e.get("days_after_birth"))
        o.add(f"{en} ({days:.0f} days): {e['title']['en']}, {e['date_utc']}", f"{bn} ({days:.0f} দিন): {e['title']['bn']}, {e['date_utc']}",
              f"{hi} ({days:.0f} दिन): {e['title']['hi']}, {e['date_utc']}")
    if nb.get("born_within_15_days_of_eclipse"):
        o.add("  Born within 15 days of an eclipse (traditionally noted).", "  গ্রহণের ১৫ দিনের মধ্যে জন্ম (ঐতিহ্যগতভাবে লক্ষ্য করা হয়)।",
              "  ग्रहण के 15 दिन के भीतर जन्म (परंपरा में नोट किया जाता है)।")


def shadbala_block(o, sb: Dict) -> None:
    from .report import _title
    _title(o, "Shadbala (six-fold planetary strength)", "ষড়বল (গ্রহের ছয় রকম শক্তি)", "षड्बल (ग्रहों का छह प्रकार का बल)")
    for r in sb["planets"]:
        mark = T("strong", "বলবান", "बलवान") if r["strong"] else T("below the minimum", "ন্যূনতমের নিচে", "न्यूनतम से कम")
        o.add(f"{_pl(o, r['planet'])}: {r['total_rupa']:.2f} rupa (needs {r['required_rupa']:.2f}; ratio {r['ratio']:.2f}) - {mark}",
              f"{_pl(o, r['planet'])}: {r['total_rupa']:.2f} রূপা (দরকার {r['required_rupa']:.2f}; অনুপাত {r['ratio']:.2f}) - {mark}",
              f"{_pl(o, r['planet'])}: {r['total_rupa']:.2f} रूपा (आवश्यक {r['required_rupa']:.2f}; अनुपात {r['ratio']:.2f}) - {mark}")
    o.add(f"Strongest: {_pl(o, sb['strongest'])}  |  Weakest: {_pl(o, sb['weakest'])}", f"সবচেয়ে বলবান: {_pl(o, sb['strongest'])}  |  সবচেয়ে দুর্বল: {_pl(o, sb['weakest'])}",
          f"सबसे बलवान: {_pl(o, sb['strongest'])}  |  सबसे दुर्बल: {_pl(o, sb['weakest'])}")
    o.add("(Classical BPHS method; compare planets inside this chart, not exact values: see docs/ACCURACY.md.)",
          "(ক্লাসিক্যাল BPHS পদ্ধতি; এই কুণ্ডলির ভেতরে গ্রহদের তুলনা করুন, সঠিক মান নয়: docs/ACCURACY.md দেখুন।)",
          "(शास्त्रीय BPHS विधि; इसी कुंडली में ग्रहों की तुलना करें, सटीक मान नहीं: docs/ACCURACY.md देखें।)")


def render_shadbala(sb: Dict, lang: str) -> str:
    from .report import Out
    o = Out(lang)
    shadbala_block(o, sb)
    return o.text()
