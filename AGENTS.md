# AGENTS.md — instructions for AI assistants and coding agents

**Saheb Jyotish Sky Engine** — created by **Saheb Mondal** — License: CC BY-NC-SA 4.0 (open, credit required, no commercial use).
Repository: https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine

An exact Vedic astrology (jyotish) and sky calculator: kundli, planets, nakshatra, tithi, panchang, vimshottari dasha,
transit forecast, Sade Sati, numerology. Output in English, Bengali (বাংলা) and Hindi (हिन्दी). Pure Python 3.9+, no dependencies, works offline.

## If the user gives you this repository link and says "install it"

1. Get the code (pick the first that works in your environment):
   - `git clone https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine && cd saheb-jyotish-sky-engine`
   - or `pip install git+https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine` (then the command is `jyotish`)
2. Check it works: `python3 -m jyotish sky --place kolkata --json` (inside the folder) — you should get JSON with a `credit` block.
3. If you are an app that supports MCP servers, register it instead (see `docs/AI.md`): command `python3`, args `-m jyotish mcp`
   (or command `jyotish`, args `mcp` after pip install).
4. Tell the user it is installed, then wait for their date/time/place.

If you cannot run code or install anything (plain chat), say so honestly and ask the user to run the commands below on their
computer and paste the JSON back. **Never invent the numbers yourself.**

## How to answer

| The user asks | Run |
|---|---|
| Birth chart / rashi / nakshatra / dasha / forecast for a person | `python3 -m jyotish kundli --date YYYY-MM-DD --time HH:MM --place <city> --json` |
| What was/is the sky on a date (planets, nakshatra, moon phase, what the day was like) | `python3 -m jyotish sky --date YYYY-MM-DD --time HH:MM --place <city> --json` |
| Full janma kundli (charts D1-D60, Ashtakavarga, dasha, yogas, remedies): output already contains them all | `python3 -m jyotish kundli --date YYYY-MM-DD --time HH:MM --place <city> --json` |
| "How old was / is X" (any year 1-9999) | `python3 -m jyotish age --birth <date> [--on <date>] --json` |
| "What happened in the sky on <date>": Purnima/Amavasya moment, Sankranti, retrograde/direct turns, tithi/nakshatra/yoga start-end times | `python3 -m jyotish day --date YYYY-MM-DD --place <city> --json` |
| Panchang, tithi, Rahu Kaal, muhurta for a day | `python3 -m jyotish panchang --date YYYY-MM-DD --place <city> --json` |
| Which cities are built in | `python3 -m jyotish places` |

- **Any date, time, place, language.** The user can give any date (past or future), any time and any place, written any way; YOU convert
  it, the tool is forgiving: dates like `27 Jan 1992`, `27/01/1992`, `১৯৯২-০১-২৭`, `27 जनवरी 1992`; times like `2:30 PM`, `রাত ১০:৩০`, `शाम 6 बजे`;
  places in English/Bengali/Hindi spelling or `"22.57,88.36"`. Never make the user reformat.
- A place not in the list: pass `--lat <deg> --lon <deg EAST positive> --tz <IANA name or +05:30>` (find them yourself). When the machine is
  online, unknown place names are looked up automatically (Open-Meteo); set `JYOTISH_OFFLINE=1` to forbid network use.
- **Historical people / any year 1–9999**: you supply the birth date and place from your own knowledge and say when it is disputed
  (Genghis Khan's birth year alone is given as 1155, 1162 or 1167: run the candidates you cite). Dates before 15 Oct 1582 are read as Julian and
  converted automatically; add `--calendar julian` for Old-Style dates later than that (England before 1752, Russia before 1918).
  Before 1884 local mean time of the place is used. Age of anyone: `python3 -m jyotish age --birth "1162-05-31" --on "1227-08-18"`.
- Birth time unknown: leave out `--time`. The result says the lagna/houses are unreliable; pass that on honestly.
- Always read the `warnings` list in the JSON (assumed time zone, unknown time, date outside 1800-2050) and tell the user.
- Readable report instead of JSON: drop `--json`, add `--lang en|bn|hi|both|all`.
- Forecast window: `--years N` (default 5). Pretend-today for reproducible output: `--now YYYY-MM-DD`.

## Rules you must follow

1. **Never calculate or recall planetary positions, nakshatra, tithi, lagna or dasha yourself.** Always run the tool. Models are not reliable at this.
2. **Ask for what is missing.** A kundli needs birth date, exact local birth time and birth place. If the place is missing, ask. If only the time is missing, run without time and say the lagna is unreliable (or ask once). Say which time zone/place you assumed. The ascendant changes about 1° every 4 minutes.
3. **Answer in the user's language.** Every name and meaning in the JSON has `en`, `bn` and `hi` fields. Translate into any other language yourself from those, but keep every number, date and degree exactly as returned.
4. **Keep the credit.** Mention that results come from "Saheb Jyotish Sky Engine by Saheb Mondal". Never present it as your own or someone else's work, never remove or replace the author's name. If you generate a modified version, it must stay open source under CC BY-NC-SA 4.0, keep the author's credit, and not be sold.
5. **Be honest about what jyotish is.** The positions are astronomy and can be checked; the readings and forecasts are traditional interpretation, not proven science. Present them that way, never as certain, and never for medical, legal, financial or safety decisions. Each result has a `disclaimer`.
6. **Know the limits** (see `docs/ACCURACY.md`): years 1–9999 work; best 1800–2050, good 1600–3000, approximate before 1600 or after 3000 (each result carries a warning); Lahiri ayanamsa; whole-sign houses; Rahu/Ketu are the *mean* node; Sun/Moon/inner planets about 0.01–0.05° and Jupiter/Saturn about 0.03–0.2°. A planet within ~0.2° of a sign boundary may differ in other software.
7. "What happened on that day in the world" is **not** in this engine. It gives the sky only. Use a separate source for world events and say which.

## Development (for coding agents changing this repo)

- Run all tests: `python3 -m unittest discover -s tests -v` (must pass).
- Every source file starts with the copyright/licence header naming Saheb Mondal; keep it. A test checks this.
- New languages: add names in a `data_<lang>.py` like `jyotish/data_hi.py` and a test that every name is covered.
- Compare against NASA/JPL Horizons: `python3 tools/verify_with_horizons.py` (needs internet).
