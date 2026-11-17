# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Report sections for the deeper layers (see deep.py): North-Indian chart, Navamsa, Shodashavarga, bhava table,
Ashtakavarga, Jaimini karakas and traditional remedies. Text is English / Bengali / Hindi."""
from __future__ import annotations

from typing import Dict, List

from . import deep
from .data import NAKSHATRA as NAK, PLANET, PLANET_ABBR, RASHI, RASHI_LORD

SIGN_ABBR = ["Mes", "Vri", "Mit", "Kar", "Sim", "Kan", "Tul", "Vrs", "Dha", "Mak", "Kum", "Mee"]


def T(en: str, bn: str, hi: str) -> str:
    """Inline three-language text; resolved per output language by report.Out."""
    return f"\x01{en}\x02{bn}\x04{hi}\x03"


# house centres on a 25 x 61 canvas: (row, col)
_NORTH_CENTRES = {1: (6, 30), 2: (2, 15), 3: (6, 5), 4: (12, 15), 5: (18, 5), 6: (22, 15),
                  7: (18, 30), 8: (22, 45), 9: (18, 55), 10: (12, 45), 11: (6, 55), 12: (2, 45)}


def north_indian_grid(lagna_sign: int, planets: Dict[str, Dict]) -> List[str]:
    """North-Indian diamond chart: houses are fixed, the number in each house is its rashi (1 = Mesha ... 12 = Meena)."""
    H, W = 25, 61
    cv = [[" "] * W for _ in range(H)]

    def put(r, c, ch):
        if 0 <= r < H and 0 <= c < W:
            cv[r][c] = ch

    for c in range(W):
        put(0, c, "-"); put(H - 1, c, "-")
    for r in range(H):
        put(r, 0, "|"); put(r, W - 1, "|")
    for r in range(1, H - 1):                       # the two diagonals
        c = round(r * (W - 1) / (H - 1))
        put(r, c, "\\"); put(r, W - 1 - c, "/")

    def line(r0, c0, r1, c1):
        n = max(abs(r1 - r0), 1)
        ch = "/" if (c1 - c0) * (r1 - r0) < 0 else "\\"
        for k in range(1, n):
            put(r0 + (r1 - r0) * k // n, round(c0 + (c1 - c0) * k / n), ch)
    line(0, 30, 12, 0); line(12, 0, 24, 30); line(24, 30, 12, 60); line(12, 60, 0, 30)
    put(0, 30, "+"); put(12, 0, "+"); put(24, 30, "+"); put(12, 60, "+"); put(12, 30, "X")

    for h, (r, c) in _NORTH_CENTRES.items():
        sign = (lagna_sign + h - 1) % 12
        tag = str(sign + 1) + ("*" if h == 1 else "")
        items = [PLANET_ABBR[g] + ("(R)" if p["retrograde"] and g not in ("Rahu", "Ketu") else "")
                 for g, p in planets.items() if p["sign"] == sign]
        for k, txt in enumerate([tag] + [" ".join(items[i:i + 2]) for i in range(0, len(items), 2)]):
            if h in (2, 12, 6, 8) and k > 2:
                break
            start = c - len(txt) // 2
            for j, ch in enumerate(txt):
                put(r + k, start + j, ch)
    return ["".join(row).rstrip() for row in cv]


# (gem, weekday, deity, beeja mantra) per graha, as (en, bn, hi) triples. Traditional associations.
REMEDY = {
    "Sun": (("Ruby", "মাণিক্য", "माणिक्य"), ("Sunday", "রবিবার", "रविवार"), ("Surya", "সূর্য", "सूर्य"),
            ("Om Hraam Hreem Hraum Sah Suryaya Namah", "ওঁ হ্রাং হ্রীং হ্রৌং সঃ সূর্যায় নমঃ", "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः")),
    "Moon": (("Pearl", "মুক্তা", "मोती"), ("Monday", "সোমবার", "सोमवार"), ("Shiva", "শিব", "शिव"),
             ("Om Shraam Shreem Shraum Sah Chandramase Namah", "ওঁ শ্রাং শ্রীং শ্রৌং সঃ চন্দ্রমসে নমঃ", "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः")),
    "Mars": (("Red coral", "প্রবাল", "मूंगा"), ("Tuesday", "মঙ্গলবার", "मंगलवार"), ("Hanuman", "হনুমান", "हनुमान"),
             ("Om Kraam Kreem Kraum Sah Bhaumaya Namah", "ওঁ ক্রাং ক্রীং ক্রৌং সঃ ভৌমায় নমঃ", "ॐ क्रां क्रीं क्रौं सः भौमाय नमः")),
    "Mercury": (("Emerald", "পান্না", "पन्ना"), ("Wednesday", "বুধবার", "बुधवार"), ("Vishnu", "বিষ্ণু", "विष्णु"),
                ("Om Braam Breem Braum Sah Budhaya Namah", "ওঁ ব্রাং ব্রীং ব্রৌং সঃ বুধায় নমঃ", "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः")),
    "Jupiter": (("Yellow sapphire", "পোখরাজ", "पुखराज"), ("Thursday", "বৃহস্পতিবার", "गुरुवार"), ("Brihaspati / Vishnu", "বৃহস্পতি / বিষ্ণু", "बृहस्पति / विष्णु"),
                ("Om Graam Greem Graum Sah Gurave Namah", "ওঁ গ্রাং গ্রীং গ্রৌং সঃ গুরবে নমঃ", "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः")),
    "Venus": (("Diamond", "হীরা", "हीरा"), ("Friday", "শুক্রবার", "शुक्रवार"), ("Lakshmi", "লক্ষ্মী", "लक्ष्मी"),
              ("Om Draam Dreem Draum Sah Shukraya Namah", "ওঁ দ্রাং দ্রীং দ্রৌং সঃ শুক্রায় নমঃ", "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः")),
    "Saturn": (("Blue sapphire", "নীলা", "नीलम"), ("Saturday", "শনিবার", "शनिवार"), ("Shani / Hanuman", "শনি / হনুমান", "शनि / हनुमान"),
               ("Om Praam Preem Praum Sah Shanaishcharaya Namah", "ওঁ প্রাং প্রীং প্রৌং সঃ শনৈশ্চরায় নমঃ", "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः")),
    "Rahu": (("Hessonite (gomed)", "গোমেদ", "गोमेद"), ("Saturday", "শনিবার", "शनिवार"), ("Durga", "দুর্গা", "दुर्गा"),
             ("Om Bhraam Bhreem Bhraum Sah Rahave Namah", "ওঁ ভ্রাং ভ্রীং ভ্রৌং সঃ রাহবে নমঃ", "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः")),
    "Ketu": (("Cat's eye (lehsunia)", "বৈদূর্য", "लहसुनिया"), ("Tuesday", "মঙ্গলবার", "मंगलवार"), ("Ganesha", "গণেশ", "गणेश"),
             ("Om Sraam Sreem Sraum Sah Ketave Namah", "ওঁ স্রাং স্রীং স্রৌং সঃ কেতবে নমঃ", "ॐ स्रां स्रीं स्रौं सः केतवे नमः")),
}

BHAVA = [
    ("Self, body, personality", "নিজ, শরীর, ব্যক্তিত্ব", "स्वयं, शरीर, व्यक्तित्व"),
    ("Wealth, family, speech", "ধন, পরিবার, বাক্", "धन, परिवार, वाणी"),
    ("Courage, siblings, effort", "সাহস, ভাইবোন, উদ্যম", "साहस, भाई-बहन, पराक्रम"),
    ("Mother, home, comfort", "মা, গৃহ, সুখ", "माता, घर, सुख"),
    ("Children, intellect, past merit", "সন্তান, বুদ্ধি, পূর্বপুণ্য", "संतान, बुद्धि, पूर्व पुण्य"),
    ("Enemies, debts, illness, service", "শত্রু, ঋণ, রোগ, সেবা", "शत्रु, ऋण, रोग, सेवा"),
    ("Spouse, partnerships", "জীবনসঙ্গী, অংশীদারি", "जीवनसाथी, साझेदारी"),
    ("Longevity, sudden change, secrets", "আয়ু, আকস্মিক পরিবর্তন, গুপ্ত বিষয়", "आयु, अचानक परिवर्तन, गुप्त विषय"),
    ("Fortune, dharma, father, teachers", "ভাগ্য, ধর্ম, পিতা, গুরু", "भाग्य, धर्म, पिता, गुरु"),
    ("Career, status, action", "কর্ম, পদমর্যাদা", "कर्म, पद-प्रतिष्ठा"),
    ("Gains, friends, wishes fulfilled", "লাভ, বন্ধু, ইচ্ছাপূরণ", "लाभ, मित्र, इच्छापूर्ति"),
    ("Expenses, losses, foreign lands, moksha", "ব্যয়, ক্ষতি, বিদেশ, মোক্ষ", "व्यय, हानि, विदेश, मोक्ष"),
]
KARAKA = [
    ("AK", ("Atmakaraka - the soul, the self", "আত্মকারক - আত্মা, নিজস্ব সত্তা", "आत्मकारक - आत्मा, स्वयं")),
    ("AmK", ("Amatyakaraka - career, adviser", "অমাত্যকারক - কর্ম, পরামর্শদাতা", "अमात्यकारक - कर्म, सलाहकार")),
    ("BK", ("Bhratrikaraka - siblings, courage", "ভ্রাতৃকারক - ভাইবোন, সাহস", "भ्रातृकारक - भाई-बहन, साहस")),
    ("MK", ("Matrikaraka - mother, comforts", "মাতৃকারক - মা, সুখ", "मातृकारक - माता, सुख")),
    ("PK", ("Putrakaraka - children, creativity", "পুত্রকারক - সন্তান, সৃজনশীলতা", "पुत्रकारक - संतान, सृजन")),
    ("GK", ("Gnatikaraka - rivals, relatives, obstacles", "জ্ঞাতিকারক - প্রতিদ্বন্দ্বী, আত্মীয়, বাধা", "ज्ञातिकारक - प्रतिद्वंद्वी, रिश्तेदार, बाधा")),
    ("DK", ("Darakaraka - spouse, partner", "দারকারক - জীবনসঙ্গী", "दारकारक - जीवनसाथी")),
]
# Traditional name syllables (namakshar) of the 4 padas of each nakshatra: (Latin, Devanagari)
NAMAKSHAR = [
    ("Chu Che Cho La", "चु चे चो ला"), ("Li Lu Le Lo", "ली लू ले लो"), ("A I U E", "अ ई उ ए"), ("O Va Vi Vu", "ओ वा वी वू"),
    ("Ve Vo Ka Ki", "वे वो का की"), ("Ku Gha Nga Chha", "कू घ ङ छ"), ("Ke Ko Ha Hi", "के को हा ही"), ("Hu He Ho Da", "हू हे हो डा"),
    ("Di Du De Do", "डी डू डे डो"), ("Ma Mi Mu Me", "मा मी मू मे"), ("Mo Ta Ti Tu", "मो टा टी टू"), ("Te To Pa Pi", "टे टो पा पी"),
    ("Pu Sha Na Tha", "पू ष ण ठ"), ("Pe Po Ra Ri", "पे पो रा री"), ("Ru Re Ro Ta", "रू रे रो ता"), ("Ti Tu Te To", "ती तू ते तो"),
    ("Na Ni Nu Ne", "ना नी नू ने"), ("No Ya Yi Yu", "नो या यी यू"), ("Ye Yo Bha Bhi", "ये यो भा भी"), ("Bhu Dha Pha Dha", "भू धा फा ढा"),
    ("Bhe Bho Ja Ji", "भे भो जा जी"), ("Khi Khu Khe Kho", "खी खू खे खो"), ("Ga Gi Gu Ge", "गा गी गू गे"), ("Go Sa Si Su", "गो सा सी सू"),
    ("Se So Da Di", "से सो दा दी"), ("Du Tha Jha Ña", "दू थ झ ञ"), ("De Do Cha Chi", "दे दो चा ची"),
]
assert len(NAMAKSHAR) == 27


def namakshar(nakshatra: int, pada: int) -> tuple:
    """(Latin, Devanagari) name syllable for a nakshatra (0-26) and pada (1-4)."""
    return tuple(x.split()[pada - 1] for x in NAMAKSHAR[nakshatra])


VARGA_NAME = {1: ("Rashi", "রাশি", "राशि"), 2: ("Hora", "হোরা", "होरा"), 3: ("Drekkana", "দ্রেষ্কাণ", "द्रेष्काण"),
              4: ("Chaturthamsa", "চতুর্থাংশ", "चतुर्थांश"), 7: ("Saptamsa", "সপ্তমাংশ", "सप्तमांश"), 9: ("Navamsa", "নবমাংশ", "नवमांश"),
              10: ("Dasamsa", "দশমাংশ", "दशमांश"), 12: ("Dwadasamsa", "দ্বাদশাংশ", "द्वादशांश"), 16: ("Shodasamsa", "ষোড়শাংশ", "षोडशांश"),
              20: ("Vimsamsa", "বিংশাংশ", "विंशांश"), 24: ("Chaturvimsamsa", "চতুর্বিংশাংশ", "चतुर्विंशांश"), 27: ("Bhamsa", "ভাংশ", "भांश"),
              30: ("Trimsamsa", "ত্রিংশাংশ", "त्रिंशांश"), 40: ("Khavedamsa", "খবেদাংশ", "खवेदांश"), 45: ("Akshavedamsa", "অক্ষবেদাংশ", "अक्षवेदांश"),
              60: ("Shashtiamsa", "ষষ্ট্যংশ", "षष्ट्यंश")}
VARGA_USE = {1: ("body, overall life", "শরীর, সামগ্রিক জীবন", "शरीर, समग्र जीवन"), 2: ("wealth", "ধন", "धन"), 3: ("siblings", "ভাইবোন", "भाई-बहन"),
             4: ("property, fortune", "সম্পত্তি, ভাগ্য", "संपत्ति, भाग्य"), 7: ("children", "সন্তান", "संतान"),
             9: ("spouse, dharma, inner strength of planets", "জীবনসঙ্গী, ধর্ম, গ্রহের অন্তর্নিহিত বল", "जीवनसाथी, धर्म, ग्रहों का आंतरिक बल"),
             10: ("career", "কর্মজীবন", "करियर"), 12: ("parents", "পিতামাতা", "माता-पिता"), 16: ("vehicles, comforts", "যানবাহন, সুখ", "वाहन, सुख"),
             20: ("worship, spiritual practice", "উপাসনা, সাধনা", "उपासना, साधना"), 24: ("education", "শিক্ষা", "शिक्षा"), 27: ("strengths and weaknesses", "বল ও দুর্বলতা", "बल और दुर्बलता"),
             30: ("troubles, misfortune", "দুর্ভোগ, অশুভ", "कष्ट, अशुभ"), 40: ("maternal-line results", "মাতৃবংশীয় ফল", "मातृवंश फल"),
             45: ("paternal-line results", "পিতৃবংশীয় ফল", "पितृवंश फल"), 60: ("past-life karma, fine detail", "পূর্বজন্মের কর্ম, সূক্ষ্ম ফল", "पूर्व जन्म कर्म, सूक्ष्म फल")}


def render_deep(o, chart: Dict) -> None:
    """Append the deeper sections to an Out object `o`."""
    from .report import _title, south_indian_grid
    nm = o.nm
    da = deep.analyse(chart)
    pl = chart["planets"]
    lag = chart["lagna"]["sign"]
    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    mn = chart["planets"]["Moon"]
    syl = namakshar(mn["nakshatra"], mn["pada"])
    _title(o, "Name syllable (namakshar)", "নামাক্ষর", "नामाक्षर")
    o.add(f"Birth Moon is in {nm(NAK[mn['nakshatra']])} pada {mn['pada']}: the traditional first syllable for the name is '{syl[0]}' (all four: {NAMAKSHAR[mn['nakshatra']][0]}).",
          f"জন্মের চাঁদ {nm(NAK[mn['nakshatra']])} নক্ষত্রের {mn['pada']} পাদে: নামের ঐতিহ্যগত প্রথম অক্ষর '{syl[0]}' (চারটি: {NAMAKSHAR[mn['nakshatra']][0]})।",
          f"जन्म का चंद्र {nm(NAK[mn['nakshatra']])} नक्षत्र के चरण {mn['pada']} में: नाम का परंपरागत पहला अक्षर '{syl[1]}' (चारों: {NAMAKSHAR[mn['nakshatra']][1]})।")

    _title(o, "Rashi chart (North-Indian style)", "রাশি ছক (উত্তর ভারতীয় ধরন)", "राशि कुंडली (उत्तर भारतीय शैली)")
    o.add("Houses are fixed; the number in a house is its sign (1 = Mesha ... 12 = Meena); * = Lagna house; (R) = retrograde.",
          "ঘর স্থির; ঘরের সংখ্যা হলো রাশি (১ = মেষ ... ১২ = মীন); * = লগ্ন; (R) = বক্রী।",
          "भाव स्थिर हैं; भाव की संख्या राशि है (1 = मेष ... 12 = मीन); * = लग्न; (R) = वक्री।")
    for ln in north_indian_grid(lag, pl):
        o.raw(ln)

    v9 = da["vargas"][9]
    nav = {"lagna": {"sign": v9["lagna"]},
           "planets": {g: {"sign": s, "retrograde": False} for g, s in v9["planets"].items()}}
    _title(o, "Navamsa chart (D9) - spouse, dharma, true strength of planets", "নবমাংশ ছক (D9) - জীবনসঙ্গী, ধর্ম, গ্রহের প্রকৃত বল",
           "नवमांश कुंडली (D9) - जीवनसाथी, धर्म, ग्रहों का वास्तविक बल")
    for ln in south_indian_grid(nav):
        o.raw(ln)
    vg = da["vargottama"]
    if vg:
        names = ", ".join(nm(PLANET[g]) for g in vg)
        o.add(f"Vargottama (same sign in D1 and D9, strengthened): {names}", f"বর্গোত্তম (D1 ও D9-এ একই রাশি, শক্তিশালী): {names}",
              f"वर्गोत्तम (D1 और D9 में एक ही राशि, बलवान): {names}")

    _title(o, "Shodashavarga - the 16 divisional charts (sign of each planet)", "ষোড়শবর্গ - ১৬টি বিভাজিত ছক (প্রতিটি গ্রহের রাশি)",
           "षोडशवर्ग - 16 विभाजित कुंडलियाँ (प्रत्येक ग्रह की राशि)")
    cols = deep.VARGAS
    head = "        " + " ".join(f"D{n:<3d}" for n in cols)
    o.raw(head)
    rows = [("Asc", da["vargas"][1]["lagna"], {n: da["vargas"][n]["lagna"] for n in cols})]
    rows[0] = ("Asc", None, {n: da["vargas"][n]["lagna"] for n in cols})
    for g in order:
        rows.append((PLANET_ABBR[g], None, {n: da["vargas"][n]["planets"][g] for n in cols}))
    for label, _, d in rows:
        o.raw(f"{label:<7s} " + " ".join(f"{SIGN_ABBR[d[n]]:<4s}" for n in cols))
    o.add("Use of each chart (traditional): D2 wealth, D3 siblings, D4 property, D7 children, D9 spouse/dharma, D10 career, D12 parents, "
          "D16 vehicles, D20 worship, D24 education, D27 strength, D30 troubles, D40/D45 family lines, D60 past karma.",
          "প্রতিটি ছকের ব্যবহার (ঐতিহ্যগত): D2 ধন, D3 ভাইবোন, D4 সম্পত্তি, D7 সন্তান, D9 জীবনসঙ্গী/ধর্ম, D10 কর্ম, D12 পিতামাতা, "
          "D16 যানবাহন, D20 উপাসনা, D24 শিক্ষা, D27 বল, D30 দুর্ভোগ, D40/D45 বংশধারা, D60 পূর্বজন্মের কর্ম।",
          "प्रत्येक कुंडली का उपयोग (परंपरागत): D2 धन, D3 भाई-बहन, D4 संपत्ति, D7 संतान, D9 जीवनसाथी/धर्म, D10 करियर, D12 माता-पिता, "
          "D16 वाहन, D20 उपासना, D24 शिक्षा, D27 बल, D30 कष्ट, D40/D45 वंश, D60 पूर्व कर्म।")

    _title(o, "Bhava (house) table", "ভাব (ঘর) তালিকা", "भाव तालिका")
    for r in da["house_lords"]:
        occ = ", ".join(nm(PLANET[g]) for g in r["occupants"]) or "-"
        b = BHAVA[r["house"] - 1]
        o.add(f"House {r['house']:2d} {nm(RASHI[r['sign']])}: lord {nm(PLANET[r['lord']])} sits in house {r['lord_house']}; occupants: {occ}; "
              f"SAV {r['sav']}  [{b[0]}]",
              f"{r['house']} নং ঘর {nm(RASHI[r['sign']])}: অধিপতি {nm(PLANET[r['lord']])} বসে {r['lord_house']} নং ঘরে; অবস্থিত গ্রহ: {occ}; "
              f"SAV {r['sav']}  [{b[1]}]",
              f"भाव {r['house']:2d} {nm(RASHI[r['sign']])}: स्वामी {nm(PLANET[r['lord']])} भाव {r['lord_house']} में; ग्रह: {occ}; "
              f"SAV {r['sav']}  [{b[2]}]")

    ak = da["ashtakavarga"]
    _title(o, "Ashtakavarga (benefic points by sign)", "অষ্টকবর্গ (রাশিভিত্তিক শুভ বিন্দু)", "अष्टकवर्ग (राशि अनुसार शुभ बिंदु)")
    o.raw("        " + " ".join(f"{a:<4s}" for a in SIGN_ABBR) + " Total")
    for g in deep.PLANETS7:
        o.raw(f"{PLANET_ABBR[g]:<7s} " + " ".join(f"{v:<4d}" for v in ak["bav"][g]) + f" {sum(ak['bav'][g])}")
    o.raw(f"{'SAV':<7s} " + " ".join(f"{v:<4d}" for v in ak["sav"]) + f" {ak['total']}")
    strong = [h for h in range(1, 13) if ak["sav"][(lag + h - 1) % 12] >= 28]
    weak = [h for h in range(1, 13) if ak["sav"][(lag + h - 1) % 12] < 25]
    o.add(f"Sarvashtakavarga average is 28 per sign (total 337). Houses with 28+ points (stronger results): {strong or '-'}; below 25 (weaker): {weak or '-'}",
          f"সর্বাষ্টকবর্গে প্রতি রাশির গড় ২৮ (মোট ৩৩৭)। ২৮+ বিন্দুর ঘর (শক্তিশালী ফল): {strong or '-'}; ২৫-এর কম (দুর্বল): {weak or '-'}",
          f"सर्वाष्टकवर्ग में प्रति राशि औसत 28 (कुल 337)। 28+ बिंदु वाले भाव (अधिक बलवान): {strong or '-'}; 25 से कम (कमज़ोर): {weak or '-'}")

    _title(o, "Jaimini chara karakas (by degree)", "জৈমিনি চরকারক (ডিগ্রি অনুযায়ী)", "जैमिनि चर कारक (अंश के अनुसार)")
    for key, desc in KARAKA:
        g = da["karakas"][key]
        o.add(f"{key}: {nm(PLANET[g])} {pl[g]['degree']:.2f}° - {desc[0]}", f"{key}: {nm(PLANET[g])} {pl[g]['degree']:.2f}° - {desc[1]}",
              f"{key}: {nm(PLANET[g])} {pl[g]['degree']:.2f}° - {desc[2]}")

    _title(o, "Traditional remedies (upaya) - for reflection, not medical or financial advice", "ঐতিহ্যগত প্রতিকার (উপায়) - ভাবনার জন্য, চিকিৎসা বা আর্থিক পরামর্শ নয়",
           "परंपरागत उपाय - चिंतन के लिए, चिकित्सा या वित्तीय सलाह नहीं")
    for g in order:
        gem, day, deity, mantra = REMEDY[g]
        o.add(f"{nm(PLANET[g])}: gem {T(*gem)}, day {T(*day)}, deity {T(*deity)}",
              f"{nm(PLANET[g])}: রত্ন {T(*gem)}, বার {T(*day)}, দেবতা {T(*deity)}",
              f"{nm(PLANET[g])}: रत्न {T(*gem)}, वार {T(*day)}, देवता {T(*deity)}")
        o.add(f"    mantra: {T(*mantra)}", f"    মন্ত্র: {T(*mantra)}", f"    मंत्र: {T(*mantra)}")
    o.add("Gemstones are costly and have no scientific evidence of effect; never buy one under pressure. Charity, discipline and service on the planet's day are the traditional low-cost remedies.",
          "রত্ন দামি এবং এর প্রভাবের কোনো বৈজ্ঞানিক প্রমাণ নেই; চাপে পড়ে কখনও কিনবেন না। সংশ্লিষ্ট গ্রহের বারে দান, সংযম ও সেবাই ঐতিহ্যগত স্বল্পখরচের প্রতিকার।",
          "रत्न महँगे हैं और इनके प्रभाव का कोई वैज्ञानिक प्रमाण नहीं; दबाव में कभी न खरीदें। संबंधित ग्रह के वार पर दान, संयम और सेवा परंपरागत कम खर्च वाले उपाय हैं।")
