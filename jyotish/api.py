# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""JSON-friendly functions for programs and AI assistants. Every result carries the author credit.

All names come with English, Bengali and Hindi forms so an AI can answer in the user's language
while the numbers stay exactly as computed.
"""
from __future__ import annotations

from datetime import date as _date, datetime, timezone
from typing import Dict, Optional

from . import astro as A
from . import data as D
from . import data_hi as HIN
from . import transits as TR
from .chart import build_chart
from .location import Location, make_local_datetime, resolve_location
from .calendars import resolve_date
from .location import HistoricTZ, LMT_BEFORE
from .parse import is_unknown_time, range_note
from .panchang import day_panchang, panchang_at, day_times
from .report import render_kundli, render_panchang, render_sky, render_day, _tithi_name, _karana_name

PROJECT = "Saheb Jyotish Sky Engine"
AUTHOR = "Saheb Mondal"
REPO = "https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine"


def credit_block() -> Dict:
    return {
        "author": AUTHOR,
        "project": PROJECT,
        "license": "CC BY-NC-SA 4.0 (open, credit required, no commercial use, changes must stay open)",
        "repository": REPO,
        "text": {"en": D.CREDIT[0], "bn": D.CREDIT[1], "hi": HIN.CREDIT_HI},
        "instruction_to_ai": "Always mention that this result was computed by 'Saheb Jyotish Sky Engine' by Saheb Mondal. "
                             "Never present the engine or its output as your own work or attribute it to anyone else.",
        "disclaimer": {"en": D.DISCLAIMER[0], "bn": D.DISCLAIMER[1], "hi": HIN.DISCLAIMER_HI},
    }


def _n(pair) -> Dict:
    return {"en": pair[0], "bn": pair[1], "hi": HIN.h(pair)}


def _sign(i: int) -> Dict:
    return {"index": i, "number": i + 1, **_n(D.RASHI[i]), "western_name": D.WESTERN[i]}


def _nak(i: int) -> Dict:
    return {"index": i, "number": i + 1, **_n(D.NAKSHATRA[i])}


def _grah(g: str) -> Dict:
    return {"key": g, **_n(D.PLANET[g])}


def _iso(jd: Optional[float], tz) -> Optional[str]:
    if jd is None:
        return None
    return A.format_jd(jd, tz, "%Y-%m-%dT%H:%M:%S%z").replace(" ", "T")


def _day(jd: float, tz) -> str:
    return A.format_jd(jd, tz, "%Y-%m-%d")


UNKNOWN_TIME_NOTE = ("Birth time not known: 12:00 noon was used. The lagna (ascendant), houses, divisional charts and the exact Moon "
                     "position can be wrong (the Moon moves about 13 degrees in a day, so even the nakshatra and dasha start can shift). "
                     "Sun sign, planet signs (except the Moon near a sign edge) and slow-planet transits are still fine.")


def _prep(loc: Location, year: int, unknown_time: bool = False) -> Location:
    """Record assumptions (date range, unknown time) on the location so every output can show them."""
    for n in (range_note(year), UNKNOWN_TIME_NOTE if unknown_time else None):
        if n and n not in loc.notes:
            loc.notes.append(n)
    if year < LMT_BEFORE and isinstance(loc.tz, HistoricTZ):
        n = ("Before 1884 there were no standard time zones, so the place's own local mean time (longitude / 15 hours) was used for "
             "all clock times. Give the birth time as local clock time of that place.")
        if n not in loc.notes:
            loc.notes.append(n)
    return loc


def _warnings(loc: Location) -> Dict:
    return {"warnings": list(loc.notes)} if loc.notes else {}


def _today(loc: Location):
    return datetime.now(timezone.utc).astimezone(loc.tz).date()


def now_jd(now: Optional[str] = None) -> float:
    if not now:
        return A.julian_day(datetime.now(timezone.utc))
    d = datetime.fromisoformat(now)
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return A.julian_day(d)


def _panchang_block(pc: Dict, tz) -> Dict:
    tn, kn = _tithi_name(pc["tithi_index"]), _karana_name(pc["karana_index"])
    return {
        "tithi": {"number_in_month": pc["tithi_number"], "paksha": {"key": pc["paksha"], **_n(D.PAKSHA[pc["paksha"]])},
                  **_n(tn), "percent_elapsed": round(pc["tithi_percent_elapsed"], 1), "ends": _iso(pc.get("tithi_end_jd"), tz),
                  "next": _n(_tithi_name((pc["tithi_index"] + 1) % 30))},
        "nakshatra": {**_nak(pc["nakshatra_index"]), "pada": pc["nakshatra_pada"], "ends": _iso(pc.get("nakshatra_end_jd"), tz),
                      "next": _nak((pc["nakshatra_index"] + 1) % 27)},
        "yoga": {**_n(D.YOGA[pc["yoga_index"]]), "ends": _iso(pc.get("yoga_end_jd"), tz),
                 "next": _n(D.YOGA[(pc["yoga_index"] + 1) % 27])},
        "karana": _n(kn),
        "moon_sign": _sign(pc["moon_sign"]),
        "sun_sign": _sign(pc["sun_sign"]),
        "moon_phase": {**_n(D.MOON_PHASE[pc["moon_phase_index"]]), "illumination_percent": round(pc["moon_illumination"] * 100, 1),
                       "elongation_deg": round(pc["elongation"], 3)},
    }


def _times_block(t: Dict, tz) -> Dict:
    out = {"sunrise": _iso(t.get("sunrise_jd"), tz), "sunset": _iso(t.get("sunset_jd"), tz)}
    for k in ("rahu_kaal", "yamaganda", "gulika", "abhijit", "brahma_muhurta"):
        if k in t:
            out[k] = {"start": _iso(t[k][0], tz), "end": _iso(t[k][1], tz)}
    return out


def _loc_block(loc: Location) -> Dict:
    return {"name": loc.name, "latitude": loc.lat, "longitude_east": loc.lon, "timezone": loc.tz_name}


def places() -> Dict:
    return {"credit": credit_block(),
            "built_in_places": {k: {"latitude": v[0], "longitude_east": v[1], "timezone": v[2]} for k, v in sorted(D.PLACES.items())},
            "note": "Any other place: pass latitude, longitude (EAST positive) and timezone (IANA name like Asia/Kolkata, or offset like +05:30)."}


def sky(date: Optional[str] = None, time: Optional[str] = None, place: Optional[str] = None, lat: Optional[float] = None,
        lon: Optional[float] = None, tz: Optional[str] = None, calendar: Optional[str] = None) -> Dict:
    loc = resolve_location(place, lat, lon, tz, calendar)
    if date is None and time is None:
        local_dt = datetime.now(timezone.utc).astimezone(loc.tz)
    else:
        d = date or _today(loc).isoformat()
        local_dt = make_local_datetime(d, time or "12:00", loc)
    _prep(loc, local_dt.year)
    utc = local_dt.astimezone(timezone.utc)
    jd = A.julian_day(utc)
    pos = A.all_positions(jd)
    pl = {}
    for g in A.GRAHAS:
        p = pos[g]
        pl[g] = {**_grah(g), "sidereal_longitude": round(p["sidereal"], 4), "tropical_longitude": round(p["tropical"], 4),
                 "sidereal_sign": _sign(int(p["sidereal"] // 30) % 12), "degree_in_sidereal_sign": round(p["sidereal"] % 30, 4),
                 "tropical_sign": _sign(int(p["tropical"] // 30) % 12),
                 "nakshatra": _nak(int(p["sidereal"] // (360 / 27)) % 27),
                 "pada": int((p["sidereal"] % (360 / 27)) // (360 / 108)) + 1,
                 "speed_deg_per_day": round(p["speed"], 4), "retrograde": p["retrograde"]}
    pc = panchang_at(jd)
    times = day_times(local_dt.date(), loc)
    return {"credit": credit_block(), "kind": "sky", "when_local": local_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "when_utc": utc.strftime("%Y-%m-%dT%H:%M:%SZ"), "julian_day_ut": round(jd, 6), "place": _loc_block(loc),
            "ayanamsa_lahiri_deg": round(A.ayanamsa_lahiri(A.jd_to_tt(jd)), 5), "planets": pl,
            "panchang": _panchang_block(pc, loc.tz), "day_times": _times_block(times, loc.tz),
            "accuracy_note": "Sun/Moon/inner planets ~0.01-0.05 deg, Jupiter/Saturn ~0.03-0.2 deg, mean lunar node. Best for 1800-2050.",
            **_warnings(loc)}


def panchang(date: Optional[str] = None, place: Optional[str] = None, lat: Optional[float] = None,
             lon: Optional[float] = None, tz: Optional[str] = None, calendar: Optional[str] = None) -> Dict:
    loc = resolve_location(place, lat, lon, tz, calendar)
    d = resolve_date(date, loc.calendar, loc.notes) if date else _today(loc)
    _prep(loc, d.year)
    p = day_panchang(d, loc)
    return {"credit": credit_block(), "kind": "panchang", "date": d.isoformat(), "place": _loc_block(loc),
            "note": "Tithi/nakshatra/yoga/karana are those running at local sunrise.", **_warnings(loc),
            "vara": {**_n(D.VARA[p["vara_index"]]), "lord": _grah(D.VARA_LORD[p["vara_index"]])},
            "panchang": _panchang_block(p, loc.tz), "day_times": _times_block(p, loc.tz),
            "hindu_calendar": __import__("jyotish.hindu_calendar", fromlist=["safe_describe"]).safe_describe(d, loc)}


def _fest_json(f: Dict) -> Dict:
    return {"date": f["date"].isoformat(), "name": {"en": f["en"], "bn": f["bn"], "hi": f["hi"]}, "rule": f["rule"],
            "alternative_dates": [a.isoformat() for a in f.get("alternative_dates", [])], "how": f.get("how", "")}


def _safe_fest(d, loc):
    from .report_calendar import festivals_on
    try:
        return [_fest_json(f) for f in festivals_on(d, loc)]
    except (OverflowError, ValueError):
        return []


def hindu_calendar(date: Optional[str] = None, place: Optional[str] = None, lat: Optional[float] = None,
                   lon: Optional[float] = None, tz: Optional[str] = None, calendar: Optional[str] = None) -> Dict:
    """Hindu calendar for one day: lunar month (amanta/purnimanta, adhika), paksha, tithi, Vikram/Shaka/Kali, samvatsara,
    ritu, ayana, Bengali/Tamil/Malayalam/Odia/National solar dates, and the festivals of that day."""
    from . import hindu_calendar as HC
    from .report_calendar import festivals_on
    loc = resolve_location(place, lat, lon, tz, calendar)
    d = resolve_date(date, loc.calendar, loc.notes) if date else _today(loc)
    _prep(loc, d.year)
    return {"credit": credit_block(), "kind": "hindu_calendar", "place": _loc_block(loc), **_warnings(loc),
            **HC.safe_describe(d, loc), "festivals_on_this_day": _safe_fest(d, loc)}


def festivals(year: Optional[int] = None, place: Optional[str] = None, lat: Optional[float] = None,
              lon: Optional[float] = None, tz: Optional[str] = None, calendar: Optional[str] = None) -> Dict:
    """All main Hindu festivals, Ekadashis, Purnimas, Amavasyas and Sankrantis of a Gregorian year."""
    from . import hindu_calendar as HC
    loc = resolve_location(place, lat, lon, tz, calendar)
    y = int(year) if year else _today(loc).year
    _prep(loc, y)
    return {"credit": credit_block(), "kind": "festivals", "year": y, "place": _loc_block(loc), **_warnings(loc),
            "method": "Drik method (modern ephemeris, Lahiri) for the chosen place; alternative_dates lists other days almanacs may use",
            "festivals": [_fest_json(f) for f in HC.festivals_for_year(y, loc)]}


def day_events(date: Optional[str] = None, place: Optional[str] = None, lat: Optional[float] = None,
               lon: Optional[float] = None, tz: Optional[str] = None, calendar: Optional[str] = None) -> Dict:
    """Moon-phase moments, sign changes (sankranti), retrograde/direct turns and tithi/nakshatra/yoga timeline for one local day."""
    from .events import day_events as _ev
    loc = resolve_location(place, lat, lon, tz, calendar)
    d = resolve_date(date, loc.calendar, loc.notes) if date else _today(loc)
    _prep(loc, d.year)
    e = _ev(d, loc)
    z = loc.tz

    def seg(x, namer):
        return {**namer(x["index"]), "starts": _iso(x["start"], z), "ends": _iso(x["end"], z)}
    return {"credit": credit_block(), "kind": "day_events", "date": d.isoformat(), "place": _loc_block(loc),
            "not_included": "eclipses (Moon latitude not computed)", **_warnings(loc),
            "moon_phases": [{**_n(D.PHASE_EVENT[x["phase_index"]]), "at": _iso(x["jd"], z)} for x in e["moon_phases"]],
            "sign_changes": [{"planet": _grah(x["planet"]), "from": _sign(x["from_sign"]), "to": _sign(x["to_sign"]),
                              "at": _iso(x["jd"], z), "is_sankranti": x["planet"] == "Sun"} for x in e["ingresses"]],
            "stations": [{"planet": _grah(x["planet"]), "turns": x["turns"], "at": _iso(x["jd"], z)} for x in e["stations"]],
            "tithi": [seg(x, lambda i: _n(_tithi_name(i))) for x in e["tithi"]],
            "nakshatra": [seg(x, _nak) for x in e["nakshatra"]],
            "yoga": [seg(x, lambda i: _n(D.YOGA[i])) for x in e["yoga"]]}


def age(birth: str, on: Optional[str] = None, calendar: Optional[str] = None, on_calendar: Optional[str] = None) -> Dict:
    """Age between a birth date and another date (default today): years, months, days and exact day count.

    Dates before 15 Oct 1582 are read as Julian (see --calendar). The count is exact; years/months/days are counted in the proleptic
    Gregorian calendar after converting both dates.
    """
    notes: list = []
    b = resolve_date(birth, calendar or "auto", notes)
    o = resolve_date(on, on_calendar or "auto", notes) if on else datetime.now(timezone.utc).date()
    if o < b:
        raise ValueError("The second date is before the birth date.")
    y, m, d = o.year - b.year, o.month - b.month, o.day - b.day
    if d < 0:
        m -= 1
        pm = o.month - 1 or 12
        py = o.year if o.month > 1 else o.year - 1
        d += [31, 29 if (py % 4 == 0 and (py % 100 != 0 or py % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][pm - 1]
    if m < 0:
        y -= 1
        m += 12
    total = (o - b).days
    wd = D.VARA[(b.weekday() + 1) % 7]
    out = {"credit": credit_block(), "kind": "age", "birth_gregorian": b.isoformat(), "on_gregorian": o.isoformat(),
           "years": y, "months": m, "days": d, "total_days": total, "approx_years": round(total / 365.2425, 3),
           "birth_weekday": _n(wd)}
    if notes:
        out["warnings"] = notes
    return out


def kundli(date: str, time: Optional[str] = None, place: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None,
           tz: Optional[str] = None, name: str = "", years: float = 5.0, now: Optional[str] = None,
           calendar: Optional[str] = None) -> Dict:
    loc = resolve_location(place, lat, lon, tz, calendar)
    unknown = is_unknown_time(time)
    local_dt = make_local_datetime(date, "12:00" if unknown else time, loc)
    _prep(loc, local_dt.year, unknown)
    c = build_chart(local_dt, loc, name)
    tzo = loc.tz
    njd = now_jd(now)
    meta = c["meta"]

    planets = {}
    for g, p in c["planets"].items():
        planets[g] = {**_grah(g), "sign": _sign(p["sign"]), "degree_in_sign": round(p["degree"], 4),
                      "sidereal_longitude": round(p["sidereal"], 4), "tropical_longitude": round(p["tropical"], 4),
                      "house": p["house"], "nakshatra": _nak(p["nakshatra"]), "pada": p["pada"],
                      "retrograde": p["retrograde"], "dignity": p["dignity"], "navamsa_sign": _sign(p["navamsa"]),
                      "speed_deg_per_day": round(p["speed"], 4)}
    lag = c["lagna"]
    yogas = []
    for key in c["yogas"]:
        nm_pair, tx = D.YOGA_TEXT[key]
        hn, ht = HIN.YOGA_TEXT_HI[key]
        yogas.append({"key": key, "name": {"en": nm_pair[0], "bn": nm_pair[1], "hi": hn},
                      "meaning": {"en": tx[0], "bn": tx[1], "hi": ht}})

    periods = c["dasha"]["periods"]
    from . import dasha as DS
    cur = DS.find_period(periods, njd)
    dasha_block = {"year_length_days": DS.YEAR_DAYS,
                   "balance_at_birth": {**_grah(c["dasha"]["balance"]["lord"]), "years_left": round(c["dasha"]["balance"]["years_left"], 3)},
                   "mahadashas": [{**_grah(p["lord"]), "start": _day(p["start"], tzo), "end": _day(p["end"], tzo),
                                   "theme": {"en": D.DASHA_TEXT[p["lord"]][0], "bn": D.DASHA_TEXT[p["lord"]][1], "hi": HIN.DASHA_TEXT_HI[p["lord"]]}}
                                  for p in periods[:10]]}
    if cur:
        m, a = cur["maha"], cur["antar"]
        dasha_block["current"] = {
            "mahadasha": {**_grah(m["lord"]), "start": _day(m["start"], tzo), "end": _day(m["end"], tzo)},
            "antardasha": {**_grah(a["lord"]), "start": _day(a["start"], tzo), "end": _day(a["end"], tzo)},
            "theme": {"en": D.DASHA_TEXT[m["lord"]][0], "bn": D.DASHA_TEXT[m["lord"]][1], "hi": HIN.DASHA_TEXT_HI[m["lord"]]}}
    horizon = njd + max(years, 0) * 365.25
    dasha_block["upcoming_antardashas"] = [
        {"mahadasha": _grah(p["lord"])["key"], "antardasha": a["lord"], "start": _day(max(a["start"], njd), tzo), "end": _day(a["end"], tzo)}
        for p in periods for a in p["antar"] if a["end"] > njd and a["start"] < horizon]

    out = {
        "credit": credit_block(), "kind": "kundli", **_warnings(loc), "birth_time_known": not unknown,
        "input": {"name": name, "local_time": meta["local_time"], "utc_time": meta["utc_time"], "place": _loc_block(loc),
                  "house_system": "whole sign", "ayanamsa": meta["ayanamsa_system"], "ayanamsa_deg": round(meta["ayanamsa"], 5),
                  "as_of_for_dasha_and_forecast": A.datetime_from_jd(njd).strftime("%Y-%m-%d")},
        "lagna": {"sign": _sign(lag["sign"]), "degree_in_sign": round(lag["degree"], 4), "nakshatra": _nak(lag["nakshatra"]), "pada": lag["pada"],
                  "meaning": {"en": D.RASHI_TEXT[lag["sign"]][0], "bn": D.RASHI_TEXT[lag["sign"]][1], "hi": HIN.RASHI_TEXT_HI[lag["sign"]]}},
        "moon_sign": {"sign": _sign(c["moon_sign"]),
                      "meaning": {"en": D.RASHI_TEXT[c["moon_sign"]][0], "bn": D.RASHI_TEXT[c["moon_sign"]][1], "hi": HIN.RASHI_TEXT_HI[c["moon_sign"]]}},
        "birth_nakshatra": {**_nak(c["planets"]["Moon"]["nakshatra"]), "pada": c["planets"]["Moon"]["pada"],
                            "lord": _grah(D.DASHA_ORDER[c["planets"]["Moon"]["nakshatra"] % 9]),
                            "meaning": {"en": D.NAKSHATRA_TEXT[c["planets"]["Moon"]["nakshatra"]][0],
                                        "bn": D.NAKSHATRA_TEXT[c["planets"]["Moon"]["nakshatra"]][1],
                                        "hi": HIN.NAKSHATRA_TEXT_HI[c["planets"]["Moon"]["nakshatra"]]}},
        "western_tropical_signs": {"sun": _sign(c["western"]["sun"]), "moon": _sign(c["western"]["moon"]), "ascendant": _sign(c["western"]["ascendant"])},
        "planets": planets,
        "houses": {str(h): {"sign": _sign(v["sign"]), "planets": v["planets"]} for h, v in c["houses"].items()},
        "panchang_at_birth": {**_panchang_block(c["panchang"], tzo), "vara": _n(D.VARA[c["panchang"]["vara_index"]])},
        "day_times": _times_block(c["day_times"], tzo),
        "yogas_and_doshas": yogas,
        "dasha": dasha_block,
        "numerology": {k: {"number": v, "planet": _grah(D.NUMEROLOGY[v][0]),
                           "meaning": {"en": D.NUMEROLOGY[v][1], "bn": D.NUMEROLOGY[v][2], "hi": HIN.NUMEROLOGY_HI[v]}}
                       for k, v in c["numerology"].items()},
    }
    from . import deep as DP
    from .report_deep import BHAVA, KARAKA, NAMAKSHAR, REMEDY, VARGA_NAME, namakshar
    da = DP.analyse(c)
    from . import hindu_calendar as _HC
    from .report_calendar import hindu_day_of_birth
    _hd = hindu_day_of_birth(c)
    out["hindu_calendar"] = {**_HC.safe_describe(_hd, loc), "hindu_day_note": "Hindu day = sunrise to sunrise; a birth before local sunrise belongs to the previous civil date's Hindu day."}
    out["divisional_charts"] = {f"D{n}": {"name": dict(zip(("en", "bn", "hi"), VARGA_NAME[n])), "lagna": _sign(v["lagna"]),
                                          "planets": {g: _sign(sg) for g, sg in v["planets"].items()}} for n, v in da["vargas"].items()}
    mo = c["planets"]["Moon"]
    out["name_syllable"] = {"pada_syllable": dict(zip(("latin", "devanagari"), namakshar(mo["nakshatra"], mo["pada"]))),
                            "all_four": dict(zip(("latin", "devanagari"), NAMAKSHAR[mo["nakshatra"]])),
                            "note": "Traditional first syllable for naming the child, from the Moon's nakshatra pada."}
    out["vargottama_planets"] = [_grah(g) for g in da["vargottama"]]
    out["ashtakavarga"] = {"bhinna": {g: pts for g, pts in da["ashtakavarga"]["bav"].items()}, "sarva": da["ashtakavarga"]["sav"],
                           "total": da["ashtakavarga"]["total"], "sign_order": "Mesha..Meena", "average_per_sign": 28}
    out["jaimini_karakas"] = {k: {**_grah(g), "degree_in_sign": round(c["planets"][g]["degree"], 3),
                                  "meaning": dict(zip(("en", "bn", "hi"), dict(KARAKA)[k]))} for k, g in da["karakas"].items()}
    out["bhava_table"] = [{"house": r["house"], "sign": _sign(r["sign"]), "lord": _grah(r["lord"]), "lord_in_house": r["lord_house"],
                           "occupants": [_grah(g) for g in r["occupants"]], "sarvashtakavarga_points": r["sav"],
                           "signifies": dict(zip(("en", "bn", "hi"), BHAVA[r["house"] - 1]))} for r in da["house_lords"]]
    out["traditional_remedies"] = {"note": "Traditional associations for reflection; no scientific evidence of effect.",
                                   "by_planet": {g: {"gem": dict(zip(("en", "bn", "hi"), r[0])), "day": dict(zip(("en", "bn", "hi"), r[1])),
                                                     "deity": dict(zip(("en", "bn", "hi"), r[2])), "mantra": dict(zip(("en", "bn", "hi"), r[3]))}
                                                 for g, r in REMEDY.items()}}
    if years > 0:
        ms = c["moon_sign"]
        fc = TR.forecast(ms, njd, years)
        tl = {}
        for g in ("Saturn", "Jupiter", "Rahu"):
            tl[g] = [{"start": _day(s["start"], tzo), "end": _day(s["end"], tzo), "sign": _sign(s["sign"]),
                      "house_from_moon": s["house_from_moon"], "traditionally_favourable": s["favourable"]} for s in fc["timelines"][g]]
        out["forecast"] = {
            "window": {"from": _day(fc["start"], tzo), "to": _day(fc["end"], tzo)},
            "method": "Transits (gochar) counted from the natal Moon sign; Vimshottari dasha. Traditional interpretation, not science.",
            "planets_today": {g: {**_grah(g), "sign": _sign(v["sign"]), "degree_in_sign": round(v["degree"], 2), "house_from_moon": v["house_from_moon"]}
                              for g, v in TR.current_gochar(njd, ms).items()},
            "sign_changes": tl,
            "ketu_note": "Ketu is always exactly opposite Rahu.",
            "sade_sati_and_dhaiya": [{"start": _day(p["start"], tzo), "end": _day(p["end"], tzo), "house_from_moon": p["house"], "kind": p["kind"],
                                      "meaning": {"en": D.SADE_SATI_TEXT[p["house"]][0], "bn": D.SADE_SATI_TEXT[p["house"]][1], "hi": HIN.SADE_SATI_TEXT_HI[p["house"]]}}
                                     for p in fc["saturn_phases"]]}
    return out


def report(kind: str, lang: str = "both", **kw) -> str:
    """Readable text report. kind: 'kundli' | 'panchang' | 'sky' | 'day'. lang: en|bn|hi|both|all."""
    if kind == "age":
        a = age(kw["date"], kw.get("on"), kw.get("calendar"))
        from .report import Out
        o = Out(lang)
        o.add(f"Age: {a['years']} years, {a['months']} months, {a['days']} days  ({a['total_days']} days in all; born on a {o.nm(D.VARA[(datetime.fromisoformat(a['birth_gregorian']).weekday() + 1) % 7])})",
              f"বয়স: {a['years']} বছর, {a['months']} মাস, {a['days']} দিন  (মোট {a['total_days']} দিন; জন্ম {o.nm(D.VARA[(datetime.fromisoformat(a['birth_gregorian']).weekday() + 1) % 7])})",
              f"आयु: {a['years']} वर्ष, {a['months']} माह, {a['days']} दिन  (कुल {a['total_days']} दिन; जन्म {o.nm(D.VARA[(datetime.fromisoformat(a['birth_gregorian']).weekday() + 1) % 7])})")
        for n in a.get("warnings", []):
            o.add("  * " + n, "  * " + n, "  * " + n)
        o.add(f"Dates used (Gregorian): {a['birth_gregorian']} -> {a['on_gregorian']}", f"ব্যবহৃত তারিখ (গ্রেগরিয়ান): {a['birth_gregorian']} -> {a['on_gregorian']}",
              f"प्रयुक्त तिथियाँ (ग्रेगोरियन): {a['birth_gregorian']} -> {a['on_gregorian']}")
        return o.text()
    loc = resolve_location(kw.get("place"), kw.get("lat"), kw.get("lon"), kw.get("tz"), kw.get("calendar"))
    if kind == "panchang":
        d = resolve_date(kw["date"], loc.calendar, loc.notes) if kw.get("date") else _today(loc)
        _prep(loc, d.year)
        return render_panchang(d, loc, lang)
    if kind == "sky":
        if kw.get("date") is None and kw.get("time") is None:
            dt = datetime.now(timezone.utc).astimezone(loc.tz)
        else:
            d = kw.get("date") or _today(loc).isoformat()
            dt = make_local_datetime(d, kw.get("time") or "12:00", loc)
        _prep(loc, dt.year)
        return render_sky(dt, loc, lang)
    if kind == "day":
        d = resolve_date(kw["date"], loc.calendar, loc.notes) if kw.get("date") else _today(loc)
        _prep(loc, d.year)
        return render_day(d, loc, lang)
    if kind == "calendar":
        from .report_calendar import render_calendar
        d = resolve_date(kw["date"], loc.calendar, loc.notes) if kw.get("date") else _today(loc)
        _prep(loc, d.year)
        return render_calendar(d, loc, lang)
    if kind == "festivals":
        from .report_calendar import render_festivals
        y = int(kw["year"]) if kw.get("year") else _today(loc).year
        _prep(loc, y)
        return render_festivals(y, loc, lang)
    if kind == "kundli":
        unknown = is_unknown_time(kw.get("time"))
        local_dt = make_local_datetime(kw["date"], "12:00" if unknown else kw["time"], loc)
        _prep(loc, local_dt.year, unknown)
        c = build_chart(local_dt, loc, kw.get("name", ""))
        njd = now_jd(kw.get("now"))
        years = float(kw.get("years", 5.0))
        fc = TR.forecast(c["moon_sign"], njd, years) if years > 0 else None
        return render_kundli(c, fc, lang, njd, loc)
    raise ValueError("kind must be kundli, panchang, sky, day, calendar or festivals")
