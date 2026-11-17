# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Minimal MCP (Model Context Protocol) server over stdio, standard library only.

Run:  python -m jyotish mcp
It lets AI apps that support MCP call this engine as a tool, so dates, planets, nakshatra,
panchang and dasha come from exact computation instead of the model's memory.
Protocol: newline-delimited JSON-RPC 2.0 (MCP stdio transport).
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from . import api

SERVER_NAME = "saheb-jyotish-sky-engine"
SERVER_VERSION = "0.2.0"
PROTOCOL_VERSION = "2025-06-18"
SUPPORTED_PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")

INSTRUCTIONS = (
    "Saheb Jyotish Sky Engine (by Saheb Mondal, CC BY-NC-SA 4.0) computes Vedic astrology (jyotish) data "
    "exactly: kundli, lagna, rashi, nakshatra, planets, panchang, tithi, divisional charts, ashtakavarga, vimshottari dasha, "
    "transit forecast, and the sky on any date and place. "
    "RULES FOR THE ASSISTANT: (1) For ANY question about a date's planets, nakshatra, tithi, rashi, lagna, dasha, chart or "
    "forecast, ALWAYS call a tool; never compute or recall such values yourself. (2) The person may give ANY date (past or "
    "future), ANY time and ANY place, in ANY language or spelling; convert what they wrote into the tool arguments yourself "
    "(the tools accept '27 Jan 1992', '27/01/1992', Bengali/Hindi digits, '2:30 PM', 'রাত ১০:৩০', place names in English/Bengali/Hindi "
    "or 'lat,lon'). Do not make them reformat. If the place is not found, find its latitude, longitude and IANA time zone "
    "and pass those. (3) For a kundli the birth time matters: if it is unknown, call the tool without time and tell the person "
    "plainly that the lagna and houses are then unreliable. Never invent a birth time or place; ask once if missing. "
    "(4) Read the 'warnings' field in every result and tell the person about them (assumed time zone, unknown time, date outside 1800-2050). "
    "(5) Answer in the language the person writes in, ANY language: the JSON carries en/bn/hi names and meanings; for any other language "
    "translate them yourself, keep the Sanskrit names, and never change a number. The text reports (format=text) exist in en, bn, hi. "
    "(6) Always credit 'Saheb Jyotish Sky Engine by Saheb Mondal' and never present the engine as your own or as someone else's. "
    "(7) Jyotish is traditional belief, not proven science: present forecasts as traditional interpretation, never as certain, and "
    "never for medical, legal, financial or safety decisions. Remedies and gemstones are traditional associations only. "
    "(8) Positions are computed, not fetched, so no internet is needed; they are best for 1800-2050 and approximate outside it."
)

_PLACE_PROPS = {
    "place": {"type": "string", "description": "Any place name (built-in list incl. Bengali/Hindi spellings; other places are looked up online when possible), or a 'lat,lon' pair. For certainty give latitude + longitude + timezone instead."},
    "latitude": {"type": "number", "description": "Latitude in degrees, north positive."},
    "longitude": {"type": "number", "description": "Longitude in degrees, EAST positive (Kolkata is +88.36)."},
    "timezone": {"type": "string", "description": "IANA name like Asia/Kolkata, or offset like +05:30."},
}
_FORMAT_PROPS = {
    "format": {"type": "string", "enum": ["json", "text"], "description": "json (default, best for answering) or a readable text report."},
    "lang": {"type": "string", "enum": ["en", "bn", "hi", "both", "all"], "description": "Only for format=text. Default en."},
}

TOOLS = [
    {"name": "jyotish_kundli",
     "description": "Full Vedic birth chart (kundli) from birth date, time and place: lagna, rashi, nakshatra, all planets, houses, panchang at birth, yogas/doshas, vimshottari dasha, transit forecast, Sade Sati, numerology.",
     "inputSchema": {"type": "object", "required": ["date"], "properties": {
         "date": {"type": "string", "description": "Birth date in any common form (1992-01-27, 27/01/1992, 27 Jan 1992, Bengali/Hindi digits). Past or future."},
         "time": {"type": "string", "description": "Birth time in any common form (14:30, 2:30 PM, রাত ১০:৩০), LOCAL time at the birth place. Omit if unknown (lagna will then be flagged unreliable)."},
         "name": {"type": "string"},
         "years": {"type": "number", "description": "Forecast window in years from today (default 5, 0 = none)."},
         **_PLACE_PROPS, **_FORMAT_PROPS}}},
    {"name": "jyotish_panchang",
     "description": "Panchang for a date and place: vara, tithi, nakshatra, yoga, karana with end times, moon phase, sunrise/sunset, Rahu Kaal, Yamaganda, Gulika, Abhijit and Brahma Muhurta.",
     "inputSchema": {"type": "object", "properties": {"date": {"type": "string", "description": "YYYY-MM-DD, default today."},
                                                      **_PLACE_PROPS, **_FORMAT_PROPS}}},
    {"name": "jyotish_sky",
     "description": "The sky at one moment: sidereal and tropical longitude, sign, nakshatra, pada, speed and retrograde status of Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu; plus tithi, moon phase and sunrise/sunset. Use for 'what was the sky on that day'.",
     "inputSchema": {"type": "object", "properties": {"date": {"type": "string", "description": "YYYY-MM-DD, default today."},
                                                      "time": {"type": "string", "description": "HH:MM local; default now (or 12:00 if only a date is given)."},
                                                      **_PLACE_PROPS, **_FORMAT_PROPS}}},
    {"name": "jyotish_day_events",
     "description": "Everything that happens in the sky on one local day: exact moments of New/Full/Quarter Moon, sign changes of all grahas (Sun's = Sankranti), retrograde/direct turns, and the full tithi, nakshatra and yoga timeline with start and end times. Use for 'what happened in the sky on that date'. Eclipses are not included.",
     "inputSchema": {"type": "object", "properties": {"date": {"type": "string", "description": "YYYY-MM-DD, default today."},
                                                      **_PLACE_PROPS, **_FORMAT_PROPS}}},
    {"name": "jyotish_places",
     "description": "List the built-in places with latitude, longitude and timezone.",
     "inputSchema": {"type": "object", "properties": {}}},
]


def _place_args(a: Dict[str, Any]) -> Dict[str, Any]:
    return {"place": a.get("place"), "lat": a.get("latitude"), "lon": a.get("longitude"), "tz": a.get("timezone")}


def call_tool(name: str, a: Dict[str, Any]) -> str:
    """Run one tool and return its text result (JSON text or a text report). Raises ValueError on bad input."""
    fmt = a.get("format", "json")
    lang = a.get("lang", "en")
    place = _place_args(a)
    if name == "jyotish_places":
        return json.dumps(api.places(), ensure_ascii=False, indent=1)
    if name == "jyotish_panchang":
        if fmt == "text":
            return api.report("panchang", lang, date=a.get("date"), **place)
        return json.dumps(api.panchang(a.get("date"), **place), ensure_ascii=False, indent=1)
    if name == "jyotish_day_events":
        if fmt == "text":
            return api.report("day", lang, date=a.get("date"), **place)
        return json.dumps(api.day_events(a.get("date"), **place), ensure_ascii=False, indent=1)
    if name == "jyotish_sky":
        if fmt == "text":
            return api.report("sky", lang, date=a.get("date"), time=a.get("time"), **place)
        return json.dumps(api.sky(a.get("date"), a.get("time"), **place), ensure_ascii=False, indent=1)
    if name == "jyotish_kundli":
        if "date" not in a:
            raise ValueError("date is required (birth date, any common form); time is optional but needed for the lagna")
        years = float(a.get("years", 5.0))
        if fmt == "text":
            return api.report("kundli", lang, date=a["date"], time=a.get("time"), name=a.get("name", ""), years=years, **place)
        return json.dumps(api.kundli(a["date"], a.get("time"), name=a.get("name", ""), years=years, **place), ensure_ascii=False, indent=1)
    raise KeyError(name)


def _reply(id_: Any, result: Optional[Dict] = None, error: Optional[Dict] = None) -> Dict:
    msg: Dict[str, Any] = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    return msg


def handle(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle one JSON-RPC message; return the response dict, or None for notifications."""
    method, id_ = msg.get("method"), msg.get("id")
    if id_ is None:                                   # notification (e.g. notifications/initialized)
        return None
    if method == "initialize":
        asked = (msg.get("params") or {}).get("protocolVersion")
        return _reply(id_, {"protocolVersion": asked if asked in SUPPORTED_PROTOCOLS else PROTOCOL_VERSION,
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": SERVER_NAME, "title": "Saheb Jyotish Sky Engine", "version": SERVER_VERSION},
                            "instructions": INSTRUCTIONS})
    if method == "ping":
        return _reply(id_, {})
    if method == "tools/list":
        return _reply(id_, {"tools": TOOLS})
    if method == "tools/call":
        p = msg.get("params") or {}
        try:
            text = call_tool(p.get("name", ""), p.get("arguments") or {})
            return _reply(id_, {"content": [{"type": "text", "text": text}], "isError": False})
        except KeyError:
            return _reply(id_, error={"code": -32602, "message": f"Unknown tool: {p.get('name')}"})
        except (ValueError, TypeError) as e:           # bad input -> tool-level error the model can read and fix
            return _reply(id_, {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True})
    return _reply(id_, error={"code": -32601, "message": f"Method not found: {method}"})


def serve(stdin=None, stdout=None) -> int:
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            stdout.write(json.dumps(_reply(None, error={"code": -32700, "message": "Parse error"})) + "\n")
            stdout.flush()
            continue
        out = handle(msg) if isinstance(msg, dict) else _reply(None, error={"code": -32600, "message": "Invalid request"})
        if out is not None:
            stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
            stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
