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
