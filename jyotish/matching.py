# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Kundli matching: the North-Indian 36-point Ashtakoota (Guna Milan) and the Manglik (Kuja dosha) comparison.

Everything here is computed from the two Moon positions (sidereal longitudes) - nothing else. Person A is the groom and
person B the bride by default, because Varna and Vashya are not symmetric (use ``a_role="bride"`` to swap).

Ashtakoota tables are traditional and differ slightly between panchangas and software. The choices made here, and the places
where published sources disagree, are written down in docs/ACCURACY.md and in the comments next to each table.
This is a traditional belief system, not science; it must not be used as the only basis for a marriage decision.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from . import data as D
from .data_hi import HI

NAK_LEN = 360.0 / 27.0
MAX_TOTAL = 36
KOOTAS = ("varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi")
MAX_POINTS = {"varna": 1, "vashya": 2, "tara": 3, "yoni": 4, "graha_maitri": 5, "gana": 6, "bhakoot": 7, "nadi": 8}

KOOTA_NAME = {
    "varna": ("Varna", "বর্ণ", "वर्ण"), "vashya": ("Vashya", "বশ্য", "वश्य"), "tara": ("Tara", "তারা", "तारा"),
    "yoni": ("Yoni", "যোনি", "योनि"), "graha_maitri": ("Graha Maitri", "গ্রহমৈত্রী", "ग्रह मैत्री"),
    "gana": ("Gana", "গণ", "गण"), "bhakoot": ("Bhakoot", "ভকূট", "भकूट"), "nadi": ("Nadi", "নাড়ী", "नाड़ी"),
}
KOOTA_MEANING = {
    "varna": ("ego and work temperament", "অহং ও কাজের স্বভাব", "अहं और कर्म-स्वभाव"),
    "vashya": ("mutual attraction and influence", "পারস্পরিক আকর্ষণ ও প্রভাব", "आपसी आकर्षण और प्रभाव"),
    "tara": ("health and luck of the two birth stars", "দুই জন্মনক্ষত্রের স্বাস্থ্য ও ভাগ্য", "दोनों जन्म-नक्षत्रों का स्वास्थ्य व भाग्य"),
    "yoni": ("instinctive and physical harmony", "সহজাত ও শারীরিক সামঞ্জস্য", "सहज व शारीरिक सामंजस्य"),
    "graha_maitri": ("friendship of the two Moon-sign lords (mental harmony)", "দুই চন্দ্ররাশির অধিপতির বন্ধুত্ব (মানসিক মিল)", "दोनों चंद्र-राशि स्वामियों की मित्रता (मानसिक मेल)"),
    "gana": ("temperament (Deva / Manushya / Rakshasa)", "মেজাজ (দেব / মনুষ্য / রাক্ষস)", "स्वभाव (देव / मनुष्य / राक्षस)"),
    "bhakoot": ("emotional and family harmony (distance of the Moon signs)", "মানসিক ও পারিবারিক মিল (চন্দ্ররাশির দূরত্ব)", "भावनात्मक व पारिवारिक मेल (चंद्र-राशियों की दूरी)"),
    "nadi": ("health and children (same Nadi is the classic dosha)", "স্বাস্থ্য ও সন্তান (একই নাড়ী হলে ঐতিহ্যগত দোষ)", "स्वास्थ्य व संतान (एक ही नाड़ी पारंपरिक दोष)"),
}

# ---------------------------------------------------------------------------------------------------------------- Varna
# Moon sign -> class by element: water Brahmin, fire Kshatriya, earth Vaishya, air Shudra (hindutone, dekhopanchang).
VARNA_NAMES = [("Brahmin", "ব্রাহ্মণ", "ब्राह्मण"), ("Kshatriya", "ক্ষত্রিয়", "क्षत्रिय"),
               ("Vaishya", "বৈশ্য", "वैश्य"), ("Shudra", "শূদ্র", "शूद्र")]      # rank 3 (highest) ... 0 below
_VARNA_OF_SIGN = [1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0]   # index into VARNA_NAMES per rashi 0..11
_VARNA_RANK = {0: 3, 1: 2, 2: 1, 3: 0}                  # Brahmin > Kshatriya > Vaishya > Shudra

# --------------------------------------------------------------------------------------------------------------- Vashya
VASHYA_NAMES = [("Chatushpada", "চতুষ্পদ", "चतुष्पद"), ("Manava", "মানব", "मानव"), ("Jalachara", "জলচর", "जलचर"),
                ("Vanachara", "বনচর", "वनचर"), ("Keeta", "কীট", "कीट")]
# Sagittarius 0-15 deg Manava, 15-30 Chatushpada; Capricorn 0-15 Chatushpada, 15-30 Jalachara
# (onlinejyotish, astromedha, dekhopanchang, muthu agree; jagannathhora's article uses a different split - not used).
_VASHYA_OF_SIGN = [0, 0, 1, 2, 3, 1, 1, 4, None, None, 1, 2]
# Score [bride group][groom group], rows/cols in VASHYA_NAMES order. Source: onlinejyotish.com vashya-kootam matrix; cells
# bride-Chatushpada/groom-Manava = 1, bride-Jalachara/groom-Manava = 0.5 and same group = 2 also given by imarriages.com.
# Other panchangas print other values for a few cells (e.g. stevehora.substack, GBP panchanga); this table is the common one.
VASHYA_MATRIX = [
    [2, 1, 1, 0, 1],
    [1, 2, 0.5, 0, 1],
    [1, 0.5, 2, 1, 1],
    [0, 0, 1, 2, 0],
    [1, 0, 1, 0, 2],
]

# ---------------------------------------------------------------------------------------------------------------- Yoni
YONI_NAMES = [("Horse", "ঘোড়া", "घोड़ा"), ("Elephant", "হাতি", "हाथी"), ("Sheep", "ভেড়া", "भेड़"), ("Serpent", "সাপ", "सर्प"),
              ("Dog", "কুকুর", "कुत्ता"), ("Cat", "বিড়াল", "बिल्ली"), ("Rat", "ইঁদুর", "चूहा"), ("Cow", "গরু", "गाय"),
              ("Buffalo", "মহিষ", "भैंस"), ("Tiger", "বাঘ", "बाघ"), ("Deer", "হরিণ", "हिरण"), ("Monkey", "বানর", "बंदर"),
              ("Mongoose", "বেজি", "नेवला"), ("Lion", "সিংহ", "सिंह")]
# nakshatra index 0..26 -> yoni index (aaps.space, astrosight.ai, selfrealisation.net and vedtara all give this same map)
_YONI_OF_NAK = [0, 1, 2, 3, 3, 4, 5, 2, 5, 6, 6, 7, 8, 9, 8, 9, 10, 10, 4, 11, 12, 11, 13, 0, 13, 7, 1]
# 14x14 score matrix (aaps.space). Its seven 0-score pairs are exactly the seven "sworn enemy" pairs listed by jagannathhora,
# onlinejyotish and astrosight (Horse-Buffalo, Elephant-Lion, Sheep-Monkey, Serpent-Mongoose, Dog-Deer, Cat-Rat, Cow-Tiger).
# Other sites use a simplified rule (everything not same/enemy = 2), so intermediate cells can differ from theirs.
YONI_MATRIX = [
    [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1],
    [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
    [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
    [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
    [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
    [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
    [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
    [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
    [3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
    [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
    [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4],
]

# ---------------------------------------------------------------------------------------------------------------- Gana
GANA_NAMES = [("Deva", "দেব", "देव"), ("Manushya", "মনুষ্য", "मनुष्य"), ("Rakshasa", "রাক্ষস", "राक्षस")]
# nakshatra -> gana (onlinejyotish, muthu, hindutone, vedtara all give the same three lists of nine)
_GANA_OF_NAK = [0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0]
# Score rule used (dekhopanchang, ishvaram/toolsarena, hindutone, astromedha): same 6, Deva-Manushya 5, Manushya-Rakshasa 1,
# Deva-Rakshasa 0, the same either way. Some sources print an asymmetric grid (e.g. Manushya groom + Deva bride 3 or 6,
# Deva groom + Rakshasa bride 1): the traditions genuinely disagree, see docs/ACCURACY.md.
_GANA_SCORE = {(0, 0): 6, (1, 1): 6, (2, 2): 6, (0, 1): 5, (1, 0): 5, (1, 2): 1, (2, 1): 1, (0, 2): 0, (2, 0): 0}

# ---------------------------------------------------------------------------------------------------------------- Nadi
NADI_NAMES = [("Aadi (Vata)", "আদি (বাত)", "आदि (वात)"), ("Madhya (Pitta)", "মধ্য (পিত্ত)", "मध्य (पित्त)"),
              ("Antya (Kapha)", "অন্ত্য (কফ)", "अन्त्य (कफ)")]
# zig-zag Aadi, Madhya, Antya, Antya, Madhya, Aadi, Aadi, Madhya, Antya ... (hindutone list; the same pattern in every source)
_NADI_OF_NAK = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2]

# ------------------------------------------------------------------------------------------------------- planet friendship
# Natural (Naisargika) friendship used for the sign lords (Brihat Parashara; onlinejyotish gives the Sun and Moon lines, and the
# 49-cell Graha Maitri matrix printed by onlinejyotish is reproduced exactly by this table + the 5/4/3/1/0.5/0 rule: see tests).
_FRIEND = {
    "Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"}, "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"}, "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
_ENEMY = {
    "Sun": {"Venus", "Saturn"}, "Moon": set(), "Mars": {"Mercury"}, "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"}, "Venus": {"Sun", "Moon"}, "Saturn": {"Sun", "Moon", "Mars"},
}


def _regard(a: str, b: str) -> str:
    return "friend" if b in _FRIEND[a] else ("enemy" if b in _ENEMY[a] else "neutral")


def graha_maitri_points(lord_a: str, lord_b: str) -> float:
    """Points 0-5 for the two Moon-sign lords: same lord or mutual friends 5, friend+neutral 4, both neutral 3,
    friend+enemy 1, neutral+enemy 0.5, mutual enemies 0."""
    if lord_a == lord_b:
        return 5.0
    pair = sorted([_regard(lord_a, lord_b), _regard(lord_b, lord_a)])
    return {("friend", "friend"): 5.0, ("friend", "neutral"): 4.0, ("neutral", "neutral"): 3.0, ("enemy", "friend"): 1.0,
            ("enemy", "neutral"): 0.5, ("enemy", "enemy"): 0.0}[(pair[0], pair[1])]


# --------------------------------------------------------------------------------------------------------------- helpers
def _t(en: str, bn: str, hi: str) -> Dict[str, str]:
    return {"en": en, "bn": bn, "hi": hi}


def _nm(tri) -> Dict[str, str]:
    return {"en": tri[0], "bn": tri[1], "hi": tri[2]}


def _rashi_name(i: int) -> Dict[str, str]:
    en, bn = D.RASHI[i]
    return {"en": en, "bn": bn, "hi": HI[en]}


def _nak_name(i: int) -> Dict[str, str]:
    en, bn = D.NAKSHATRA[i]
    return {"en": en, "bn": bn, "hi": HI[en]}


def _planet_name(p: str) -> Dict[str, str]:
    en, bn = D.PLANET[p]
    return {"en": en, "bn": bn, "hi": HI[en]}


def _moon(lon: float) -> Dict:
    lon = lon % 360.0
    nak = int(lon // NAK_LEN) % 27
    sign = int(lon // 30) % 12
    return {"longitude": lon, "rashi": sign, "degree_in_sign": lon % 30.0, "nakshatra": nak,
            "pada": int((lon % NAK_LEN) // (NAK_LEN / 4.0)) + 1}


def _person(m: Dict) -> Dict:
    return {"moon_longitude": round(m["longitude"], 4), "rashi": {"index": m["rashi"], **_rashi_name(m["rashi"])},
            "nakshatra": {"index": m["nakshatra"], "pada": m["pada"], **_nak_name(m["nakshatra"])},
            "rashi_lord": D.RASHI_LORD[m["rashi"]]}


def _vashya_group(m: Dict) -> int:
    g = _VASHYA_OF_SIGN[m["rashi"]]
    if g is not None:
        return g
    first_half = m["degree_in_sign"] < 15.0
    if m["rashi"] == 8:           # Sagittarius
        return 1 if first_half else 0
    return 0 if first_half else 2  # Capricorn


# ----------------------------------------------------------------------------------------------------------- the 8 kootas
def _varna(g: Dict, b: Dict) -> Dict:
    vg, vb = _VARNA_OF_SIGN[g["rashi"]], _VARNA_OF_SIGN[b["rashi"]]
    score = 1.0 if _VARNA_RANK[vg] >= _VARNA_RANK[vb] else 0.0
    ng, nb = VARNA_NAMES[vg], VARNA_NAMES[vb]
    return {"score": score, "groom": _nm(ng), "bride": _nm(nb),
            "explain": _t(f"Groom {ng[0]}, bride {nb[0]}: the point is given when the groom's class is equal or higher.",
                          f"বর {ng[1]}, কনে {nb[1]}: বরের বর্ণ সমান বা উচ্চ হলে ১ পয়েন্ট।",
                          f"वर {ng[2]}, वधू {nb[2]}: वर का वर्ण बराबर या ऊँचा हो तो १ अंक।")}


def _vashya(g: Dict, b: Dict) -> Dict:
    gg, gb = _vashya_group(g), _vashya_group(b)
    score = float(VASHYA_MATRIX[gb][gg])          # rows = bride group, columns = groom group
    ng, nb = VASHYA_NAMES[gg], VASHYA_NAMES[gb]
    return {"score": score, "groom": _nm(ng), "bride": _nm(nb),
            "explain": _t(f"Groom's Moon sign is {ng[0]}, bride's is {nb[0]}: mutual control/attraction scores {score:g} of 2.",
                          f"বরের রাশি {ng[1]}, কনের রাশি {nb[1]}: পারস্পরিক আকর্ষণে {score:g}/২।",
                          f"वर की राशि {ng[2]}, वधू की {nb[2]}: आपसी आकर्षण में {score:g}/२।")}


def _tara_remainder(n_from: int, n_to: int) -> int:
    count = (n_to - n_from) % 27 + 1
    r = count % 9
    return 9 if r == 0 else r


def _tara(g: Dict, b: Dict) -> Dict:
    r1 = _tara_remainder(b["nakshatra"], g["nakshatra"])   # bride's star to groom's star
    r2 = _tara_remainder(g["nakshatra"], b["nakshatra"])   # groom's star to bride's star
    bad = (3, 5, 7)
    good1, good2 = r1 not in bad, r2 not in bad
    score = 1.5 * (int(good1) + int(good2))
    return {"score": score, "remainder_bride_to_groom": r1, "remainder_groom_to_bride": r2,
            "explain": _t(f"Counting the stars both ways gives remainders {r1} and {r2} (3, 5, 7 are inauspicious): {score:g} of 3.",
                          f"দুই দিকে নক্ষত্র গুনে অবশিষ্ট {r1} ও {r2} (৩, ৫, ৭ অশুভ): {score:g}/৩।",
                          f"दोनों दिशाओं में नक्षत्र गिनने पर शेष {r1} व {r2} (३, ५, ७ अशुभ): {score:g}/३।")}


def _yoni(g: Dict, b: Dict) -> Dict:
    yg, yb = _YONI_OF_NAK[g["nakshatra"]], _YONI_OF_NAK[b["nakshatra"]]
    score = float(YONI_MATRIX[yg][yb])
    ng, nb = YONI_NAMES[yg], YONI_NAMES[yb]
    return {"score": score, "groom": _nm(ng), "bride": _nm(nb),
            "explain": _t(f"Groom's star is a {ng[0]} yoni, bride's a {nb[0]}: {score:g} of 4 (same 4, enemies 0).",
                          f"বরের নক্ষত্রের যোনি {ng[1]}, কনের {nb[1]}: {score:g}/৪ (একই হলে ৪, শত্রু হলে ০)।",
                          f"वर का योनि {ng[2]}, वधू का {nb[2]}: {score:g}/४ (समान ४, शत्रु ०)।")}


def _graha_maitri(g: Dict, b: Dict) -> Dict:
    la, lb = D.RASHI_LORD[g["rashi"]], D.RASHI_LORD[b["rashi"]]
    score = graha_maitri_points(la, lb)
    return {"score": score, "groom_lord": _planet_name(la), "bride_lord": _planet_name(lb),
            "explain": _t(f"Moon-sign lords {la} and {lb} ({_regard(la, lb)} / {_regard(lb, la)}): {score:g} of 5.",
                          f"চন্দ্ররাশির অধিপতি {_planet_name(la)['bn']} ও {_planet_name(lb)['bn']}: {score:g}/৫।",
                          f"चंद्र-राशि स्वामी {_planet_name(la)['hi']} व {_planet_name(lb)['hi']}: {score:g}/५।")}


def _gana(g: Dict, b: Dict, lords_friendly: bool) -> Dict:
    ig, ib = _GANA_OF_NAK[g["nakshatra"]], _GANA_OF_NAK[b["nakshatra"]]
    score = float(_GANA_SCORE[(ig, ib)])
    ng, nb = GANA_NAMES[ig], GANA_NAMES[ib]
    out = {"score": score, "groom": _nm(ng), "bride": _nm(nb),
           "explain": _t(f"Groom {ng[0]}, bride {nb[0]}: {score:g} of 6.", f"বর {ng[1]}, কনে {nb[1]}: {score:g}/৬।",
                         f"वर {ng[2]}, वधू {nb[2]}: {score:g}/६।")}
    if score < 6 and lords_friendly:
        out["note"] = _t("Some texts set a gana difference aside when the two Moon-sign lords are the same or friends (the score is not changed here).",
                         "দুই চন্দ্ররাশির অধিপতি এক বা বন্ধু হলে কিছু শাস্ত্র গণভেদ উপেক্ষা করে (এখানে স্কোর বদলানো হয়নি)।",
                         "दोनों चंद्र-राशि स्वामी एक या मित्र हों तो कुछ ग्रंथ गण-भेद को छोड़ देते हैं (यहाँ अंक नहीं बदला)।")
    return out


def _bhakoot(g: Dict, b: Dict, lords_friendly: bool) -> Dict:
    a_to_b = (b["rashi"] - g["rashi"]) % 12 + 1
    b_to_a = (g["rashi"] - b["rashi"]) % 12 + 1
    pair = tuple(sorted((a_to_b, b_to_a)))
    bad = pair in ((2, 12), (5, 9), (6, 8))
    cancelled = bad and lords_friendly
    raw = 0.0 if bad else 7.0
    score = 7.0 if cancelled else raw
    name = {(2, 12): "2/12", (5, 9): "5/9", (6, 8): "6/8"}.get(pair, f"{pair[0]}/{pair[1]}")
    if not bad:
        ex = _t(f"Moon signs are {name} apart (a good distance): 7 of 7.", f"চন্দ্ররাশির দূরত্ব {name} (শুভ): ৭/৭।",
                f"चंद्र-राशियों की दूरी {name} (शुभ): ७/७।")
    elif cancelled:
        ex = _t(f"Moon signs are {name} apart (Bhakoot dosha) but the sign lords are the same or friends, so the dosha is cancelled: 7 of 7.",
                f"রাশির দূরত্ব {name} (ভকূট দোষ), কিন্তু অধিপতি এক বা বন্ধু হওয়ায় দোষ কেটেছে: ৭/৭।",
                f"राशि-दूरी {name} (भकूट दोष), पर स्वामी एक या मित्र होने से दोष कटा: ७/७।")
    else:
        ex = _t(f"Moon signs are {name} apart: Bhakoot dosha, 0 of 7.", f"রাশির দূরত্ব {name}: ভকূট দোষ, ০/৭।",
                f"राशि-दूरी {name}: भकूट दोष, ०/७।")
    return {"score": score, "raw_score": raw, "distance": name, "dosha": bad, "dosha_cancelled": cancelled, "explain": ex}


def _nadi(g: Dict, b: Dict) -> Dict:
    ng_, nb_ = _NADI_OF_NAK[g["nakshatra"]], _NADI_OF_NAK[b["nakshatra"]]
    same = ng_ == nb_
    cancel_reason = None
    if same:
        same_star, same_sign = g["nakshatra"] == b["nakshatra"], g["rashi"] == b["rashi"]
        if same_star and not same_sign:
            cancel_reason = _t("same birth star but different Moon signs", "একই নক্ষত্র কিন্তু ভিন্ন চন্দ্ররাশি", "एक ही नक्षत्र पर भिन्न चंद्र-राशि")
        elif same_sign and not same_star:
            cancel_reason = _t("same Moon sign but different birth stars", "একই চন্দ্ররাশি কিন্তু ভিন্ন নক্ষত্র", "एक ही चंद्र-राशि पर भिन्न नक्षत्र")
    nm_g, nm_b = NADI_NAMES[ng_], NADI_NAMES[nb_]
    raw = 0.0 if same else 8.0
    cancelled = same and cancel_reason is not None
    score = 8.0 if cancelled else raw
    if not same:
        ex = _t(f"Groom {nm_g[0]}, bride {nm_b[0]}: different Nadis, 8 of 8.", f"বর {nm_g[1]}, কনে {nm_b[1]}: ভিন্ন নাড়ী, ৮/৮।",
                f"वर {nm_g[2]}, वधू {nm_b[2]}: भिन्न नाड़ी, ८/८।")
    elif cancelled:
        ex = _t(f"Same Nadi ({nm_g[0]}) - Nadi dosha - but cancelled ({cancel_reason['en']}): 8 of 8.",
                f"একই নাড়ী ({nm_g[1]}) - নাড়ী দোষ - কিন্তু কেটেছে ({cancel_reason['bn']}): ৮/৮।",
                f"एक ही नाड़ी ({nm_g[2]}) - नाड़ी दोष - पर कटा ({cancel_reason['hi']}): ८/८।")
    else:
        ex = _t(f"Both on {nm_g[0]} Nadi: Nadi dosha, 0 of 8.", f"দুজনেই {nm_g[1]} নাড়ী: নাড়ী দোষ, ০/৮।",
                f"दोनों {nm_g[2]} नाड़ी: नाड़ी दोष, ०/८।")
    return {"score": score, "raw_score": raw, "groom": _nm(nm_g), "bride": _nm(nm_b), "dosha": same,
            "dosha_cancelled": cancelled, "explain": ex}


# ---------------------------------------------------------------------------------------------------------------- Manglik
MANGLIK_HOUSES = (1, 4, 7, 8, 12)   # same set as yogas.py; some traditions also add the 2nd house (reported as "mild" here)


def _manglik_one(h_lagna: Optional[int], h_moon: Optional[int]) -> Dict:
    def hit(h):
        return None if h is None else h in MANGLIK_HOUSES
    return {"mars_house_from_lagna": h_lagna, "mars_house_from_moon": h_moon, "from_lagna": hit(h_lagna), "from_moon": hit(h_moon),
            "mild_second_house": h_lagna == 2,
            "manglik": bool(hit(h_lagna)) or bool(hit(h_moon))}


def manglik_compare(mars_house_a: Optional[int], mars_house_b: Optional[int],
                    moon_house_a: Optional[int] = None, moon_house_b: Optional[int] = None) -> Dict:
    """Mars (Kuja) dosha of both people (Mars in house 1/4/7/8/12 from lagna, and also from the Moon if given) and whether it balances."""
    a, b = _manglik_one(mars_house_a, moon_house_a), _manglik_one(mars_house_b, moon_house_b)
    if mars_house_a is None and mars_house_b is None and moon_house_a is None and moon_house_b is None:
        return {"available": False}
    if a["manglik"] and b["manglik"]:
        status = "both"
        txt = _t("Both have Mars dosha: traditionally it balances out (cancels).", "দুজনেরই মঙ্গল দোষ: ঐতিহ্য অনুযায়ী পরস্পর কাটাকাটি হয়ে যায়।",
                 "दोनों को मंगल दोष: परंपरा के अनुसार आपस में कट जाता है।")
    elif a["manglik"] or b["manglik"]:
        who = "A" if a["manglik"] else "B"
        status = "one"
        txt = _t(f"Only person {who} has Mars dosha: traditionally this needs care (remedies / further chart checks).",
                 f"শুধু {who} ব্যক্তির মঙ্গল দোষ: ঐতিহ্য অনুযায়ী সতর্কতা দরকার (প্রতিকার / চার্ট আরও দেখা)।",
                 f"केवल {who} को मंगल दोष: परंपरा के अनुसार सावधानी चाहिए (उपाय / कुंडली की और जाँच)।")
    else:
        status = "none"
        txt = _t("Neither has Mars dosha.", "কারও মঙ্গল দোষ নেই।", "किसी को मंगल दोष नहीं।")
    return {"available": True, "person_a": a, "person_b": b, "status": status, "balanced": status in ("both", "none"), "explain": txt,
            "note": _t("Method: Mars in houses 1, 4, 7, 8, 12 from the lagna (and from the Moon). Traditions differ (some add the 2nd house, some cancel by sign or by Jupiter's aspect); this is a screening, not a verdict.",
                       "পদ্ধতি: লগ্ন (ও চন্দ্র) থেকে ১, ৪, ৭, ৮, ১২ ভাবে মঙ্গল। মতভেদ আছে (কেউ ২য় ভাব যোগ করেন, কেউ রাশি বা গুরুর দৃষ্টিতে দোষ কাটান); এটা যাচাই, রায় নয়।",
                       "विधि: लग्न (और चंद्र) से १, ४, ७, ८, १२ भाव में मंगल। मतभेद हैं (कुछ २ भाव जोड़ते हैं); यह जाँच है, फैसला नहीं।")}


# ----------------------------------------------------------------------------------------------------------------- verdict
def verdict(total: float) -> Dict:
    """Traditional bands: below 18 not recommended, 18-24.5 average, 25-31.5 good, 32 and above excellent."""
    if total < 18:
        key, txt = "below_minimum", _t("Below the traditional minimum of 18: not recommended by this method alone.", "ঐতিহ্যগত ন্যূনতম ১৮-র নিচে: শুধু এই পদ্ধতিতে সুপারিশযোগ্য নয়।", "पारंपरिक न्यूनतम १८ से कम: केवल इस विधि से अनुशंसित नहीं।")
    elif total < 25:
        key, txt = "average", _t("Average match (18 to 24.5).", "মাঝারি মিল (১৮ থেকে ২৪.৫)।", "मध्यम मेल (१८ से २४.५)।")
    elif total < 32:
        key, txt = "good", _t("Good match (25 to 31.5).", "ভালো মিল (২৫ থেকে ৩১.৫)।", "अच्छा मेल (२५ से ३१.५)।")
    else:
        key, txt = "excellent", _t("Excellent match (32 or more).", "অসাধারণ মিল (৩২ বা তার বেশি)।", "उत्तम मेल (३२ या अधिक)।")
    return {"band": key, "text": txt, "traditional": True}


# ------------------------------------------------------------------------------------------------------------ public API
def match_from_moon_longitudes(lon_a: float, lon_b: float, mars_house_a: Optional[int] = None, mars_house_b: Optional[int] = None,
                               a_role: str = "groom", moon_house_a: Optional[int] = None, moon_house_b: Optional[int] = None) -> Dict:
    """Ashtakoota score from the two sidereal Moon longitudes (degrees). Person A is the groom by default (a_role="bride" swaps).

    mars_house_* / moon_house_* are optional (Mars house counted from the lagna / from the Moon) for the Manglik screening.
    """
    if a_role not in ("groom", "bride"):
        raise ValueError('a_role must be "groom" or "bride"')
    ma, mb = _moon(lon_a), _moon(lon_b)
    groom, bride = (ma, mb) if a_role == "groom" else (mb, ma)
    la, lb = D.RASHI_LORD[groom["rashi"]], D.RASHI_LORD[bride["rashi"]]
    friendly = graha_maitri_points(la, lb) >= 5.0           # same lord or mutual friends
    parts = {
        "varna": _varna(groom, bride), "vashya": _vashya(groom, bride), "tara": _tara(groom, bride), "yoni": _yoni(groom, bride),
        "graha_maitri": _graha_maitri(groom, bride), "gana": _gana(groom, bride, friendly),
        "bhakoot": _bhakoot(groom, bride, friendly), "nadi": _nadi(groom, bride),
    }
    kootas = []
    total = 0.0
    total_raw = 0.0
    for k in KOOTAS:
        p = parts[k]
        total += p["score"]
        total_raw += p.get("raw_score", p["score"])
        kootas.append({"key": k, "name": _nm(KOOTA_NAME[k]), "meaning": _nm(KOOTA_MEANING[k]), "max": MAX_POINTS[k], **p})
    doshas = [k for k in ("bhakoot", "nadi") if parts[k]["dosha"] and not parts[k]["dosha_cancelled"]]
    if parts["gana"]["score"] == 0:
        doshas.append("gana")
    if a_role == "groom":
        mh_g, mh_b, mo_g, mo_b = mars_house_a, mars_house_b, moon_house_a, moon_house_b
    else:
        mh_g, mh_b, mo_g, mo_b = mars_house_b, mars_house_a, moon_house_b, moon_house_a
    out = {
        "system": "Ashtakoota (North Indian 36-point Guna Milan)",
        "roles": {"person_a": a_role, "person_b": "bride" if a_role == "groom" else "groom"},
        "person_a": _person(ma), "person_b": _person(mb),
        "kootas": kootas,
        "total": total, "max": MAX_TOTAL, "total_without_cancellation": total_raw,
        "verdict": verdict(total),
        "doshas": doshas,
        "manglik": manglik_compare(mh_g, mh_b, mo_g, mo_b) if any(v is not None for v in (mh_g, mh_b, mo_g, mo_b)) else {"available": False},
        "method_note": _t("Traditional Moon-based scoring (tables differ slightly between panchangas, see docs/ACCURACY.md). It looks only at the two Moons, "
                          "not at the 7th house, dashas or the rest of the charts; it is a belief system, not a prediction, and no basis for a marriage decision on its own.",
                          "ঐতিহ্যগত চন্দ্রভিত্তিক গণনা (পঞ্জিকাভেদে সারণি সামান্য আলাদা, docs/ACCURACY.md দেখুন)। এতে শুধু দুই চন্দ্র দেখা হয়, সপ্তম ভাব, দশা বা বাকি কুণ্ডলি নয়; এটা বিশ্বাসব্যবস্থা, ভবিষ্যদ্বাণী নয়, একা বিয়ের সিদ্ধান্তের ভিত্তি নয়।",
                          "पारंपरिक चंद्र-आधारित गणना (पंचांगों में सारणियाँ थोड़ी भिन्न, docs/ACCURACY.md देखें)। केवल दोनों चंद्र देखे जाते हैं, सप्तम भाव, दशा या बाकी कुंडली नहीं; यह विश्वास-प्रणाली है, भविष्यवाणी नहीं।"),
    }
    return out


def _chart_inputs(chart: Dict) -> Tuple[float, Optional[int], Optional[int]]:
    pl = chart["planets"]
    moon_lon = pl["Moon"]["sidereal"]
    mars_house = pl["Mars"]["house"] if chart.get("meta", {}).get("birth_time_known", True) else None
    moon_house = (pl["Mars"]["sign"] - pl["Moon"]["sign"]) % 12 + 1
    return moon_lon, mars_house, moon_house


def match(chart_a: Dict, chart_b: Dict, a_role: str = "groom") -> Dict:
    """Guna Milan of two charts made by chart.build_chart (A is the groom unless a_role="bride")."""
    la, ha, hm_a = _chart_inputs(chart_a)
    lb, hb, hm_b = _chart_inputs(chart_b)
    res = match_from_moon_longitudes(la, lb, ha, hb, a_role=a_role, moon_house_a=hm_a, moon_house_b=hm_b)
    res["person_a"]["name"] = chart_a.get("meta", {}).get("name", "")
    res["person_b"]["name"] = chart_b.get("meta", {}).get("name", "")
    return res


# ------------------------------------------------------------------------------------------------------------- rendering
def _sent(d: Dict[str, str]) -> str:
    return f"\x01{d['en']}\x02{d['bn']}\x04{d['hi']}\x03"


def render(result: Dict, lang: str = "both") -> str:
    """Plain-text report in en / bn / hi / both / all (same conventions as the other reports)."""
    from .report import Out
    o = Out(lang)
    o.add("Kundli matching - Ashtakoota Guna Milan | Saheb Jyotish Sky Engine", "কুণ্ডলী মিলান - অষ্টকূট গুণমিলন | সাহেব জ্যোতিষ স্কাই ইঞ্জিন",
          "कुंडली मिलान - अष्टकूट गुण मिलन | साहेब ज्योतिष स्काई इंजन")
    o.add("By Saheb Mondal - CC BY-NC-SA 4.0", "নির্মাতা সাহেব মন্ডল - CC BY-NC-SA 4.0", "निर्माता साहेब मंडल - CC BY-NC-SA 4.0")
    o.add()
    for key, role in (("person_a", result["roles"]["person_a"]), ("person_b", result["roles"]["person_b"])):
        p = result[key]
        who = p.get("name") or ""
        o.add(f"{key[-1].upper()} ({role}) {who}: Moon in {p['rashi']['en']}, {p['nakshatra']['en']} pada {p['nakshatra']['pada']}",
              f"{key[-1].upper()} ({role}) {who}: চন্দ্র {p['rashi']['bn']}, {p['nakshatra']['bn']} পাদ {p['nakshatra']['pada']}",
              f"{key[-1].upper()} ({role}) {who}: चंद्र {p['rashi']['hi']}, {p['nakshatra']['hi']} पाद {p['nakshatra']['pada']}")
    o.add()
    for k in result["kootas"]:
        n = k["name"]
        o.add(f"{n['en']}: {k['score']:g}/{k['max']} - {k['explain']['en']}", f"{n['bn']}: {k['score']:g}/{k['max']} - {k['explain']['bn']}",
              f"{n['hi']}: {k['score']:g}/{k['max']} - {k['explain']['hi']}")
    o.add()
    v = result["verdict"]["text"]
    o.add(f"TOTAL: {result['total']:g} / 36 - {v['en']}", f"মোট: {result['total']:g} / ৩৬ - {v['bn']}", f"कुल: {result['total']:g} / ३६ - {v['hi']}")
    if result["total"] != result["total_without_cancellation"]:
        t = result["total_without_cancellation"]
        o.add(f"(Without dosha cancellations: {t:g})", f"(দোষ কাটানো ছাড়া: {t:g})", f"(दोष-परिहार के बिना: {t:g})")
    mg = result["manglik"]
    if mg.get("available"):
        o.add(f"Manglik: {mg['explain']['en']}", f"মাঙ্গলিক: {mg['explain']['bn']}", f"मांगलिक: {mg['explain']['hi']}")
    o.add()
    m = result["method_note"]
    o.add(m["en"], m["bn"], m["hi"])
    return "\n".join(o.lines)
