# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Command line: python -m jyotish kundli|panchang|sky|places|mcp ..."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from . import api
from .report import LANGS


def _add_place_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--place", help="built-in place name, e.g. kolkata, dhaka, delhi (see: jyotish places)")
    p.add_argument("--lat", type=float, help="latitude, north positive")
    p.add_argument("--lon", type=float, help="longitude, EAST positive")
    p.add_argument("--tz", help="IANA timezone (Asia/Kolkata) or offset (+05:30)")
    p.add_argument("--calendar", choices=["auto", "julian", "gregorian"], default="auto",
                   help="how to read the date: auto = Julian before 15 Oct 1582, Gregorian after (default)")
    p.add_argument("--lang", choices=LANGS, default="both",
                   help="en | bn | hi | both (en+bn, default) | all (en+bn+hi)")
    p.add_argument("--json", action="store_true", help="machine-readable JSON (for programs and AI assistants)")


def _dump(obj) -> None:
    json.dump(obj, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="jyotish",
        description="Saheb Jyotish Sky Engine / সাহেব জ্যোতিষ স্কাই ইঞ্জিন / साहेब ज्योतिष स्काई इंजन "
                    "- created by Saheb Mondal (CC BY-NC-SA 4.0)")
    sub = ap.add_subparsers(dest="cmd")

    k = sub.add_parser("kundli", help="birth chart + panchang + dasha + forecast")
    k.add_argument("--date", required=True, help="birth date, any common form: 1992-01-27, 27/01/1992, '27 Jan 1992', Bengali/Hindi digits")
    k.add_argument("--time", default=None, help="birth time, any common form: 14:30, '2:30 PM', 'রাত ১০:৩০'; leave out if unknown")
    k.add_argument("--name", default="")
    k.add_argument("--years", type=float, default=5.0, help="forecast window in years (default 5, 0 = none)")
    k.add_argument("--now", help="pretend 'today' is this ISO date/time (UTC), for reproducible output")
    _add_place_args(k)

    p = sub.add_parser("panchang", help="panchang for a day")
    p.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD (default today)")
    _add_place_args(p)

    s = sub.add_parser("sky", help="the sky at one moment: all planets, nakshatra, moon phase, panchang")
    s.add_argument("--date", help="YYYY-MM-DD (default today)")
    s.add_argument("--time", help="HH:MM local (default now; 12:00 if only --date is given)")
    _add_place_args(s)

    dy = sub.add_parser("day", help="events of one day: moon-phase moments, sankranti/sign changes, retrograde turns, tithi/nakshatra/yoga timeline")
    dy.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD (default today)")
    _add_place_args(dy)

    ag = sub.add_parser("age", help="age between a birth date and another date (default today); old dates are read as Julian before 1582")
    ag.add_argument("--birth", required=True, help="birth date, any common form, any year 1-9999")
    ag.add_argument("--on", default=None, help="the other date (default today), e.g. the date of death")
    ag.add_argument("--calendar", choices=["auto", "julian", "gregorian"], default="auto")
    ag.add_argument("--lang", choices=LANGS, default="both")
    ag.add_argument("--json", action="store_true")

    hc = sub.add_parser("calendar", help="Hindu calendar of a day: lunar month (adhika), paksha, tithi, Vikram/Shaka/Kali, samvatsara, ritu, Bengali/Tamil/Malayalam/Odia/National dates, festivals")
    hc.add_argument("--date", default=date.today().isoformat(), help="date, any common form (default today)")
    _add_place_args(hc)

    fe = sub.add_parser("festivals", help="Hindu festivals, Ekadashi, Purnima, Amavasya and Sankranti dates of a year")
    fe.add_argument("--year", type=int, default=date.today().year)
    _add_place_args(fe)

    sub.add_parser("places", help="list built-in places (JSON)")
    sub.add_parser("mcp", help="run as an MCP server over stdio, so AI apps can use this engine as a tool")

    args = ap.parse_args(argv)
    if args.cmd is None:
        ap.print_help()
        return 2
    try:
        if args.cmd == "places":
            _dump(api.places())
            return 0
        if args.cmd == "mcp":
            from .mcp_server import serve
            return serve()
        place = dict(place=getattr(args, "place", None), lat=getattr(args, "lat", None), lon=getattr(args, "lon", None),
                     tz=getattr(args, "tz", None), calendar=getattr(args, "calendar", "auto"))
        if args.cmd == "panchang":
            if args.json:
                _dump(api.panchang(args.date, **place))
            else:
                sys.stdout.write(api.report("panchang", args.lang, date=args.date, **place))
            return 0
        if args.cmd == "calendar":
            if args.json:
                _dump(api.hindu_calendar(args.date, **place))
            else:
                sys.stdout.write(api.report("calendar", args.lang, date=args.date, **place))
            return 0
        if args.cmd == "festivals":
            if args.json:
                _dump(api.festivals(args.year, **place))
            else:
                sys.stdout.write(api.report("festivals", args.lang, year=args.year, **place))
            return 0
        if args.cmd == "age":
            if args.json:
                _dump(api.age(args.birth, args.on, args.calendar))
            else:
                sys.stdout.write(api.report("age", args.lang, date=args.birth, on=args.on, calendar=args.calendar))
            return 0
        if args.cmd == "day":
            if args.json:
                _dump(api.day_events(args.date, **place))
            else:
                sys.stdout.write(api.report("day", args.lang, date=args.date, **place))
            return 0
        if args.cmd == "sky":
            if args.json:
                _dump(api.sky(args.date, args.time, **place))
            else:
                sys.stdout.write(api.report("sky", args.lang, date=args.date, time=args.time, **place))
            return 0
        if args.json:
            _dump(api.kundli(args.date, args.time, name=args.name, years=args.years, now=args.now, **place))
        else:
            sys.stdout.write(api.report("kundli", args.lang, date=args.date, time=args.time, name=args.name,
                                        years=args.years, now=args.now, **place))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
