# Accuracy and honest limits / নির্ভুলতা ও সীমাবদ্ধতা

## What was checked (automated, `python -m unittest discover -s tests`)
- Makar Sankranti 2025 and 2026: Sun reaches 270.00 deg within 0.01 deg of the published moment.
- Four new/full moons (Sep-Nov 2025): Sun-Moon elongation within 0.01 deg of 0 / 180 deg.
- Saturn into Meena (2025), Jupiter into Karka (2025), Rahu into Kumbha (2025): within 0.03 deg.
- Upcoming ingresses (Jupiter to Simha Oct 2026, Rahu to Makara Dec 2026, Saturn to Mesha Jun 2027) within 3 days.
- Sunrise/sunset: London, summer solstice 2026 within 2.5 minutes of published times; polar night returns "no sunrise".
- India's 1947 independence chart reproduces the commonly published Vrishabha lagna, Karka Moon in Pushya.

The "published" dates above were taken from widely available panchang/almanac data and are
*spot checks, not a full proof*.

## What has NOT been checked yet
- A full numeric comparison against NASA/JPL Horizons. The tool is included
  (`tools/verify_with_horizons.py`) but it needs internet access to ssd.jpl.nasa.gov; it could not be run
  where this code was written. **Please run it and open an issue with the output.**
- Dates before 1800 or after 2050 (the JPL element table is only valid for 1800-2050; outside that
  range errors grow).

## Spot check: 27 January 1992, Kolkata (done by the author's AI assistant, cross-checked with independent public sources)
- Tithi/nakshatra: engine gives Krishna Ashtami until 09:08 IST then Navami; Swati until 11:35 IST then Vishakha.
  vedicmarga.com lists Ashtami/Swati for the sunrise moment; appliedjyotish.com lists Navami/Vishakha (it uses the later-in-day tithi).
  Both agree with the timeline; sites differ only in *which moment of the day* they quote.
- New/Full Moon moments (moonblink.info, UT) matched to within about a minute.
- Planet longitudes at 00:00 GMT vs the ephemeris on signsbystars.com: Sun +0.003, Mercury +0.014, Venus -0.001, Mars +0.010,
  Jupiter -0.054, Saturn -0.056, Rahu +0.008 degrees (worst 0.056 deg).
- Kolkata sunrise 06:17 / sunset 17:20 looks right but was NOT independently verified.
- Other day-events checks (tests/test_events.py): Makar Sankranti 2026 (engine 15:02 IST, published about 15:13: ~11 min apart because
  of ayanamsa/Sun-longitude differences), Full Moon 1992-01-19 21:28 UT, Saturn retrograde turn on 2025-07-13.
- Eclipses are not computed.

## Deeper layers (v0.3)
- Ashtakavarga: the benefit tables from Brihat Parashara Hora Shastra are checked by the classical totals
  (Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56, Venus 52, Saturn 39 = 337); tests fail if any table is off.
- Divisional charts D1-D60 follow Parashara's rules; tests check the classical navamsa starts (fire=Aries, earth=Capricorn, air=Libra, water=Cancer),
  hora, drekkana and trimsamsa boundaries. Some schools use different rules for a few charts (e.g. D60, D30 variants).
- Jaimini karakas use the 7-karaka scheme (no Rahu). Remedies are traditional associations, not evidence.
- Not yet included: Shadbala, Ashtakoota (Guna Milan) matching, Bhava Chalit, Arudha padas, Chara dasha, Yogini dasha.

## Input handling (v0.3)
- Dates/times are parsed in many spellings (English/Bengali/Hindi digits and words); an ambiguous `03/04/2001` is read day-first and a note says so.
- Unknown place names are looked up online through Open-Meteo when the machine has internet. This path is tested only with a mocked
  response (the author's sandbox had no internet), so please try it once and report problems. Set `JYOTISH_OFFLINE=1` to disable it.
- Unknown time zone: India is assumed for places in India, otherwise a longitude-based offset is used and a warning says daylight saving
  and history are ignored. Give an IANA zone for exact results.
- Unknown birth time: noon is used and the lagna/houses are flagged unreliable.
- Years outside 1800-2050 work (1300 and 2100 are tested) but carry a warning: Moon/Sun/tithi stay good, outer planets can be off by degrees.

## Expected error size
| Body | Typical error |
|---|---|
| Sun, Moon, Mercury, Venus, Mars | about 0.01 - 0.05 deg |
| Jupiter, Saturn | about 0.03 - 0.2 deg |
| Rahu/Ketu (mean node) | true node can differ by up to about 1.5 deg |
| Ascendant | changes about 1 deg every 4 minutes: **birth time must be accurate** |
| Sunrise, sunset | about 1-2 minutes (no terrain, standard refraction) |
| Tithi/nakshatra end times | about a few minutes |

## Choices that change results (other software may differ)
- Ayanamsa: Lahiri. Krishnamurti, Raman, etc. give different degrees (a planet near a sign edge can switch sign).
- Mean node vs true node for Rahu/Ketu.
- Whole-sign houses.
- Dasha year length 365.25 days.
- Birth place and time zone must be right (historical zone rules are handled by the system tz database).

## Not science
Positions are astronomy and checkable. The readings and "forecasts" are traditional interpretations;
there is no scientific evidence that they predict events. Use for culture, learning and fun.
