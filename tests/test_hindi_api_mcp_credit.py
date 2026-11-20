# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Tests for Hindi output, the JSON API, the MCP server, and the author-credit protections."""
import io
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from jyotish import api
from jyotish import data as D
from jyotish import data_hi as H
from jyotish import mcp_server as M
from jyotish.cli import main as cli_main

ROOT = Path(__file__).resolve().parent.parent
BENGALI = re.compile("[ঀ-৿]")
# the danda (U+0964/0965) is shared by Bengali and Hindi, so it must not count as "Hindi"
DEVANAGARI = re.compile("[ऀ-ॣ०-ॿ]")
KW = dict(date="1995-08-15", time="14:30", place="kolkata", years=2, now="2026-11-16")


class HindiTests(unittest.TestCase):
    def test_every_name_has_hindi(self):
        pairs = (list(D.RASHI) + list(D.PLANET.values()) + list(D.NAKSHATRA) + list(D.TITHI) + [D.TITHI_FULL, D.TITHI_NEW]
                 + list(D.PAKSHA.values()) + list(D.YOGA) + list(D.KARANA_MOVABLE) + list(D.KARANA_FIXED.values())
                 + list(D.VARA) + list(D.MOON_PHASE))
        for p in pairs:
            self.assertIn(p[0], H.HI, p)
            self.assertRegex(H.HI[p[0]], DEVANAGARI)

    def test_hindi_report_is_hindi_only(self):
        for kind, extra in (("kundli", KW), ("panchang", dict(date="2026-11-16", place="kolkata")),
                            ("sky", dict(date="2026-11-16", time="10:00", place="kolkata"))):
            text = api.report(kind, "hi", **extra)
            self.assertRegex(text, DEVANAGARI, kind)
            self.assertIsNone(BENGALI.search(text), f"Bengali leaked into Hindi {kind}")
            self.assertIn("Saheb Mondal", text)                      # credit survives in Hindi

    def test_english_and_bengali_stay_clean(self):
        for kind, extra in (("kundli", KW), ("sky", dict(date="2026-11-16", time="10:00", place="kolkata"))):
            en = api.report(kind, "en", **extra)
            bn = api.report(kind, "bn", **extra)
            self.assertIsNone(DEVANAGARI.search(en))
            self.assertIsNone(BENGALI.search(en))
            self.assertIsNone(DEVANAGARI.search(bn))

    def test_all_languages_together(self):
        text = api.report("kundli", "all", **KW)
        self.assertRegex(text, DEVANAGARI)
        self.assertRegex(text, BENGALI)
        self.assertIn("Created by Saheb Mondal", text)

    def test_no_untranslated_markers_left(self):
        for lang in ("en", "bn", "hi", "all"):
            text = api.report("kundli", lang, **KW)
            self.assertNotRegex(text, "[\x01\x02\x03\x04]")


class ApiTests(unittest.TestCase):
    def test_kundli_json(self):
        k = api.kundli(**KW)
        json.dumps(k, ensure_ascii=False)
        self.assertEqual(k["lagna"]["sign"]["en"].split()[0], "Dhanu")
        self.assertEqual(k["moon_sign"]["sign"]["hi"], "मीन")
        self.assertEqual(k["birth_nakshatra"]["bn"], "রেবতী")
        self.assertEqual(len(k["planets"]), 9)
        self.assertIn("current", k["dasha"])
        self.assertIn("forecast", k)

    def test_published_1947_chart_through_api(self):
        k = api.kundli("1947-08-15", "00:00", place="delhi", years=0)
        self.assertEqual(k["lagna"]["sign"]["en"].split()[0], "Vrishabha")
        self.assertEqual(k["birth_nakshatra"]["en"], "Pushya")
        self.assertNotIn("forecast", k)

    def test_sky_and_panchang(self):
        s = api.sky("2026-11-16", "10:00", place="kolkata")
        self.assertEqual(len(s["planets"]), 9)
        self.assertTrue(s["planets"]["Saturn"]["retrograde"])
        p = api.panchang("2026-11-16", place="kolkata")
        self.assertEqual(p["vara"]["en"].split()[0], "Monday")
        self.assertIn("rahu_kaal", p["day_times"])

    def test_every_result_carries_credit(self):
        for r in (api.kundli(**KW), api.sky("2026-11-16", "10:00", place="kolkata"),
                  api.panchang("2026-11-16", place="kolkata"), api.places()):
            self.assertEqual(r["credit"]["author"], "Saheb Mondal")
            self.assertEqual(r["credit"]["project"], "Saheb Jyotish Sky Engine")
            self.assertIn("CC BY-NC-SA 4.0", r["credit"]["license"])

    def test_bad_input_is_value_error(self):
        with self.assertRaises(ValueError):
            api.kundli("1995-08-15", "14:30", place="atlantis")
        with self.assertRaises(ValueError):
            api.kundli("1995-13-45", "14:30", place="kolkata")


class McpTests(unittest.TestCase):
    def rpc(self, method, params=None, id_=1):
        return M.handle({"jsonrpc": "2.0", "id": id_, "method": method, **({"params": params} if params is not None else {})})

    def test_initialize_and_rules(self):
        r = self.rpc("initialize", {"protocolVersion": "2025-06-18"})["result"]
        self.assertEqual(r["serverInfo"]["name"], "saheb-jyotish-sky-engine")
        self.assertIn("Saheb Mondal", r["instructions"])
        self.assertIn("ALWAYS call a tool", r["instructions"])

    def test_unknown_protocol_falls_back(self):
        r = self.rpc("initialize", {"protocolVersion": "1999-01-01"})["result"]
        self.assertEqual(r["protocolVersion"], M.PROTOCOL_VERSION)

    def test_notification_gets_no_reply(self):
        self.assertIsNone(M.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_tools_list(self):
        names = [t["name"] for t in self.rpc("tools/list")["result"]["tools"]]
        self.assertEqual(sorted(names), ["jyotish_age", "jyotish_day_events", "jyotish_eclipses", "jyotish_festivals", "jyotish_hindu_calendar", "jyotish_kundli", "jyotish_match", "jyotish_panchang", "jyotish_places", "jyotish_shadbala", "jyotish_sky"])

    def test_call_kundli(self):
        r = self.rpc("tools/call", {"name": "jyotish_kundli", "arguments": {"date": "1995-08-15", "time": "14:30", "place": "kolkata", "years": 1}})["result"]
        self.assertFalse(r["isError"])
        data = json.loads(r["content"][0]["text"])
        self.assertEqual(data["moon_sign"]["sign"]["en"].split()[0], "Meena")
        self.assertEqual(data["credit"]["author"], "Saheb Mondal")

    def test_call_text_report_in_hindi(self):
        r = self.rpc("tools/call", {"name": "jyotish_sky", "arguments": {"date": "2026-11-16", "time": "10:00", "place": "kolkata", "format": "text", "lang": "hi"}})["result"]
        self.assertRegex(r["content"][0]["text"], DEVANAGARI)

    def test_missing_argument_is_tool_error_not_crash(self):
        r = self.rpc("tools/call", {"name": "jyotish_kundli", "arguments": {"date": "1995-08-15"}})["result"]
        self.assertTrue(r["isError"])
        self.assertIn("time", r["content"][0]["text"])

    def test_bad_place_is_tool_error(self):
        r = self.rpc("tools/call", {"name": "jyotish_sky", "arguments": {"place": "atlantis"}})["result"]
        self.assertTrue(r["isError"])

    def test_unknown_tool_and_method(self):
        self.assertEqual(self.rpc("tools/call", {"name": "nope", "arguments": {}})["error"]["code"], -32602)
        self.assertEqual(self.rpc("whatever")["error"]["code"], -32601)

    def test_serve_loop_over_streams(self):
        lines = [json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}), "", "garbage",
                 json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"})]
        out = io.StringIO()
        M.serve(io.StringIO("\n".join(lines) + "\n"), out)
        replies = [json.loads(x) for x in out.getvalue().splitlines()]
        self.assertEqual(len(replies), 3)
        self.assertEqual(replies[1]["error"]["code"], -32700)

    def test_real_subprocess_stdio(self):
        req = "\n".join(json.dumps(m) for m in (
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})) + "\n"
        p = subprocess.run([sys.executable, "-m", "jyotish", "mcp"], input=req, capture_output=True, text=True, cwd=ROOT, timeout=60)
        replies = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2])


class CliTests(unittest.TestCase):
    def test_new_commands_exit_zero(self):
        for argv in (["sky", "--date", "2026-11-16", "--time", "10:00", "--place", "kolkata", "--lang", "hi"],
                     ["sky", "--place", "delhi", "--json"], ["panchang", "--place", "kolkata", "--json"], ["places"]):
            self.assertEqual(cli_main(argv), 0, argv)

    def test_bad_lang_rejected(self):
        with self.assertRaises(SystemExit):
            cli_main(["sky", "--place", "kolkata", "--lang", "fr"])


class AuthorCreditTests(unittest.TestCase):
    """The author's name must stay everywhere. If someone strips it, these tests fail."""

    def test_every_source_file_has_copyright_header(self):
        files = [p for d in ("jyotish", "tests", "tools") for p in (ROOT / d).rglob("*.py")]
        self.assertGreater(len(files), 10)
        for f in files:
            head = "\n".join(f.read_text(encoding="utf-8").splitlines()[:3])
            self.assertIn("Copyright (c) Saheb Mondal", head, f)
            self.assertIn("CC BY-NC-SA 4.0", head, f)

    def test_credit_files_exist_and_name_the_author(self):
        for name in ("AUTHORS", "NOTICE", "README.md", "CITATION.cff", "AGENTS.md", "llms.txt"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("Saheb Mondal", text, name)
        self.assertIn("Mondal", (ROOT / "CITATION.cff").read_text(encoding="utf-8"))

    def test_license_is_cc_by_nc_sa(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Attribution-NonCommercial-ShareAlike 4.0 International", text)
        self.assertNotIn("GNU AFFERO", text)

    def test_project_name_and_license_in_packaging(self):
        t = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("saheb-jyotish-sky-engine", t)
        self.assertIn("CC-BY-NC-SA-4.0", t)
        self.assertIn("Saheb Mondal", t)

    def test_cli_help_credits_author(self):
        p = subprocess.run([sys.executable, "-m", "jyotish", "--help"], capture_output=True, text=True, cwd=ROOT, timeout=60)
        self.assertIn("Saheb Mondal", p.stdout)


if __name__ == "__main__":
    unittest.main()
