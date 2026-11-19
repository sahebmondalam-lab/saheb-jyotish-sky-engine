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

## Years 1-9999 (v0.3)
- **Planets**: JPL Table 1 (1800-2050) and Table 2a (3000 BC-3000 AD) from the same Standish paper. Where both apply (1810-2050) they agree to
  Mercury/Venus 0.01 deg, Mars 0.03, Jupiter 0.10, Saturn 0.33 deg (tested), which is also the size of the error to expect elsewhere
  in 1600-3000. Beyond 3000 the table is extrapolated and drifts.
- **Sun** checked against Meeus' independent equinox formulas: within 6 minutes in 325 CE, 1000 CE (4 min), 1600 (under 1), 2000 (2),
  and 36 minutes (0.025 deg) by 4000 CE.
- **Moon**: Meeus ch.47 with the Espenak-Meeus Delta-T for 1-1800. The new moon of 9 Aug 1133 (Julian 2 Aug, the day of King Henry I's eclipse) falls on
  the right day; no precise historical Moon timing was checked beyond that, so treat times of tithi/nakshatra changes before 1600 as approximate.
- **Historic events** reproduced on the right day: Mercury transit 1631, Venus transits 1639, 1761, 1769 (1769 within an hour of the published time).
- **Calendar**: before 15 Oct 1582 dates are read as Julian and converted; `calendar=julian|gregorian` overrides. The countries' switch dates differ
  (England 1752, Russia 1918, Greece 1923); the engine cannot know which a source used, so the AI/user must say.
- **Local time**: before 1884 the place's local mean time (longitude/15 h) is used; later the IANA zone rules apply.
- **Not covered**: dates before 1 CE (BCE needs a different date library), historical uncertainty of the birth date itself, fixed stars,
  Uranus/Neptune/Pluto, comets, satellites.

## Input handling (v0.3)
- Dates/times are parsed in many spellings (English/Bengali/Hindi digits and words); an ambiguous `03/04/2001` is read day-first and a note says so.
- Unknown place names are looked up online through Open-Meteo when the machine has internet. This path is tested only with a mocked
  response (the author's sandbox had no internet), so please try it once and report problems. Set `JYOTISH_OFFLINE=1` to disable it.
- Time zone from coordinates (offline): when only latitude/longitude are given, the zone of the nearest reference city of the system
  time-zone database (`zone.tab`, plus about 40 extra anchors around India, Bangladesh, Bhutan, Nepal and China) is used, so daylight saving
  and historical rules apply. Checked on all 96 built-in places and on 26 independent towns (all correct), but this is a nearest-neighbour
  method, not border polygons: a place right on a zone border (for example a town next to the India-Bhutan or India-Bangladesh line) can get
  the neighbour's zone. A note says the zone was found automatically; give `tz` to be certain. If the tz database is missing from the
  machine, India is assumed for places in India, otherwise a longitude-based offset is used with a warning.
- Place names are tried in Open-Meteo, then OpenStreetMap Nominatim; both are tested only with mocked responses.
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


## Hindu calendar and festivals - tested honestly
Method: **Drik** (modern ephemeris, Lahiri), the reckoning drikpanchang.com and most printed panjikas use today.
The Surya Siddhanta / Vakya reckonings are *not* implemented and can differ by a tithi on some days.

What was tested (all numbers below were run, see `tests/test_hindu_calendar.py`, `tests/test_published_kundlis.py`):
- **Adhika Jyeshtha 2026**: engine finds one Adhika month, 16 May 20:01 UTC to 15 Jun 02:54 UTC (published: 17 May - 15 Jun IST). Match.
- **drikpanchang.com 2026, New Delhi**: all 12 Sankrantis, all 13 Purnimas, all 24 Ekadashi dates and 50 of 50 listed festivals match.
  **This is not an independent score**: after the first run only 42 of 50 festivals matched, and the festival rules (Bhadra avoidance for
  Holika Dahan and Raksha Bandhan, aparahna/sayahna windows, Dashami-viddha Ekadashi, Ugadi kshaya fallback) were then fixed
  using this very list. It guards against regressions; it does not prove the rules are right for other years.
- **Out-of-sample check** (2025 list from kundligpt.com, 2027 list from hindupad.com; aggregator sites, not drik): before any rule
  was changed for them, 22 of 23 (2025) and 43 of 50 (2027) matched exactly. Three more rules (Janmashtami at sunrise tithi, Sarva Pitru
  Amavasya at aparahna, Sharad Purnima at pradosha) were then adjusted using those mismatches, so these are also no longer independent.
  Expect roughly 90-95% exact day agreement for the festival list in a new year; the rest are one-day differences, mostly tradition
  choices (Smarta vs Vaishnava, Bhadra handling). The result lists `alternative_dates` for such cases. Always check a printed panjika for a
  ritual date that matters.
- **Known disagreement**: Ganga Dussehra 2026. drikpanchang shows 25 May, which is inside Adhika Jyeshtha; the engine keeps it for the
  Adhika month (and also lists the regular-month date). Rakhi/Holika Dahan dates depend on the Bhadra rule used.
- **Bangladesh revised Bangla calendar**: all 12 month starts of 1433 match the published table exactly.
- **West Bengal calendar**: Poila Boishakh 1433 = 15 April 2026 (matches hindupad.com); month starts follow the Surya-Siddhanta rule
  (before Hindu-day midnight: next day). Historic spot checks from general knowledge: Tagore 7 May 1861 = 25 Boishakh 1268 (match),
  Vivekananda 12 Jan 1863 = Poush Krishna Saptami, 29 Poush 1269 (match). Ramakrishna 18 Feb 1836 = Phalguna Shukla Dwitiya (match) but the
  engine says 7 Falgun 1242 where tradition says 6 Falgun: old panjikas used the Surya Siddhanta, so a one-day gap before ~1900 is expected.
- **Malayalam**: 18 Nov 2026 = day 2 of Vrischikam, Kollam 1202 (matches drikpanchang's Malayalam page). Tamil Puthandu 14 Apr 2026 and Pongal
  14 Jan 2026 follow the sunset rule. The generic month tables on dekhopanchang.com are fixed approximations and disagree by a day in some
  months; they were not used as truth.
- **Samvatsara**: Ugadi 2026 = Parabhava (matches). The name follows the Shaka-year formula; some North-Indian almanacs name years differently.

Published charts (cross-check, Lahiri): Gandhi (7:45 LMT Porbandar), Modi (11:00 IST Vadnagar), Tagore (2:38 LMT Calcutta) from
panchangbodh.com. Every planet (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu) agrees within 0.1 deg (mostly within 0.03 deg) and all three
lagna signs agree. That source is software, so it shows agreement with another program, not with a manuscript chart. Birth times of Gandhi and Modi
are disputed in the literature; the lagna depends on which time you trust.
