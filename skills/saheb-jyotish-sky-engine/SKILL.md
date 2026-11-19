---
name: saheb-jyotish-sky-engine
description: Exact Vedic astrology (jyotish) and sky calculations from a birth date, time and place or any date: kundli, rashi, nakshatra, panchang, tithi, vimshottari dasha, transit forecast, Sade Sati, planet positions. English, Bengali, Hindi. Use whenever the user asks about their kundli, rashi, nakshatra, dasha, panchang, muhurta, or what the sky/planets were on a date.
---

# Saheb Jyotish Sky Engine (by Saheb Mondal, CC BY-NC-SA 4.0)

Never compute planetary positions, nakshatra, tithi, lagna or dasha from memory. Run the engine.

## Setup (once)
Clone `https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine` (or `pip install git+https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine`). Pure Python 3.9+, no dependencies. Check: `python3 -m jyotish sky --place kolkata --json`.
If this skill sits inside the cloned repository, run commands from the repository root.

## Commands (add `--json` for exact structured data)
- Kundli: `python3 -m jyotish kundli --date YYYY-MM-DD --time HH:MM --place <city> --json`
- Sky on a date/time: `python3 -m jyotish sky --date YYYY-MM-DD --time HH:MM --place <city> --json`
- Any date/time/place/language is fine: pass what the user wrote (the parser accepts many spellings, Bengali/Hindi digits and words); leave out `--time` if unknown; read `warnings`.
- Panchang: `python3 -m jyotish panchang --date YYYY-MM-DD --place <city> --json`
- Hindu calendar of a day (lunar month, Adhika, paksha, tithi, Vikram/Shaka/Kali, Samvatsara, Bengali/Tamil/Malayalam/Odia dates, festivals): `python3 -m jyotish calendar --date YYYY-MM-DD --place <city> --json`
- Festival dates of a year: `python3 -m jyotish festivals --year YYYY --place <city> --json` (if `alternative_dates` is shown, tell the user other almanacs may use that day)
- Events of a day (Purnima/Amavasya time, Sankranti, retrograde turns, full tithi/nakshatra/yoga timeline): `python3 -m jyotish day --date YYYY-MM-DD --place <city> --json`
- Cities: `python3 -m jyotish places`. Any other place: the name is looked up online; if that fails give `--lat <deg> --lon <deg east-positive>` yourself (from your knowledge or a web search) - the time zone is found automatically offline (`--tz` optional)

## Rules
1. Ask for missing birth date, exact local birth time and birth place; say which place/time zone you assumed.
2. Answer in the user's language. JSON names and meanings have `en`, `bn`, `hi`; keep all numbers exactly as returned.
3. Credit "Saheb Jyotish Sky Engine by Saheb Mondal"; never claim it as your own or remove the author's name.
4. Positions are checkable astronomy; readings and forecasts are traditional interpretation, not proven science. Never use for medical, legal, financial or safety decisions.
5. Valid 1800–2050; Lahiri ayanamsa; mean node for Rahu/Ketu. The engine does not know world events of a day, only the sky.

Full details: `AGENTS.md` and `docs/AI.md` in the repository.
