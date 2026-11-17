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
    "exactly: kundli, planet positions, nakshatra, panchang, vimshottari dasha, transit forecast, and the sky on any date. "
    "RULES FOR THE ASSISTANT: (1) For any question about a date's planets, nakshatra, tithi, rashi, lagna, dasha or "
    "forecast, ALWAYS call a tool; never compute or recall such values yourself. (2) For a kundli you need the birth "
    "date, birth time and birth place (or latitude/longitude/timezone); ask the person if anything is missing, and say "
    "which time zone and place you assumed. (3) Answer in the person's own language using the en/bn/hi names and meanings "
    "in the JSON; the numbers must not change. (4) Always credit 'Saheb Jyotish Sky Engine by Saheb Mondal' and never "
    "present the engine as your own or as someone else's. (5) Jyotish is traditional belief, not proven science: "
    "present forecasts as traditional interpretation, never as certain, and never for medical, legal, financial or safety decisions. "
    "(6) The engine is valid for 1800-2050; say so for dates outside it."
)

_PLACE_PROPS = {
    "place": {"type": "string", "description": "Built-in place name such as kolkata, dhaka, delhi (see jyotish_places). Or use latitude/longitude/timezone."},
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
     "inputSchema": {"type": "object", "required": ["date", "time"], "properties": {
         "date": {"type": "string", "description": "Birth date YYYY-MM-DD (local date)."},
         "time": {"type": "string", "description": "Birth time HH:MM or HH:MM:SS, 24-hour, LOCAL time at the birth place."},
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
        if "date" not in a or "time" not in a:
            raise ValueError("date and time are required (birth date YYYY-MM-DD and local birth time HH:MM)")
        years = float(a.get("years", 5.0))
        if fmt == "text":
            return api.report("kundli", lang, date=a["date"], time=a["time"], name=a.get("name", ""), years=years, **place)
        return json.dumps(api.kundli(a["date"], a["time"], name=a.get("name", ""), years=years, **place), ensure_ascii=False, indent=1)
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
