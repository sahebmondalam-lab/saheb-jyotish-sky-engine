# Data sources and algorithms / ডেটা সোর্স ও অ্যালগরিদম

Everything here is computed locally from published, open algorithms. No network is used at run time.
সবকিছু প্রকাশিত ওপেন অ্যালগরিদম থেকে নিজের মেশিনেই গণনা হয়; চালানোর সময় ইন্টারনেট লাগে না।

| What | Source |
|---|---|
| Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn | NASA/JPL, E. M. Standish, *Keplerian Elements for Approximate Positions of the Major Planets*, Table 1 (valid 1800-2050 AD). https://ssd.jpl.nasa.gov/planets/approx_pos.html |
| Moon | Jean Meeus, *Astronomical Algorithms* (2nd ed.), ch. 47, 59 longitude terms (truncated ELP-2000/82) |
| Lunar node (Rahu/Ketu) | Meeus ch. 47, **mean** node |
| Delta-T (TT - UT) | F. Espenak & J. Meeus polynomials, NASA GSFC. https://eclipse.gsfc.nasa.gov/SEhelp/deltatpoly2004.html |
| Precession | IAU 1976 general precession in longitude |
| Ayanamsa | Lahiri / Chitrapaksha (Indian Calendar Reform Committee), 23°15'00.658" on 1956-03-21, mean value |
| Ascendant, sunrise/sunset | Standard spherical astronomy (Meeus ch. 12-15); sunrise uses -0.8333 deg altitude |
| Vimshottari dasha | Classical 120-year cycle; year length 365.25 days |
| Panchang | Tithi = 12 deg of Moon-Sun elongation, karana = 6 deg, yoga = 13°20' of Sun+Moon, nakshatra = 13°20' of Moon (all sidereal) |
| Reference ephemeris for checking | NASA/JPL Horizons. https://ssd.jpl.nasa.gov/horizons/ (see `tools/verify_with_horizons.py`) |

Interpretation texts (rashi, nakshatra, dasha, yoga meanings) are short summaries of widely known
traditional ideas, written for this project in English and Bengali.
ব্যাখ্যার লেখাগুলো ঐতিহ্যগত ধারণার সংক্ষিপ্ত সারাংশ, এই প্রজেক্টের জন্য ইংরেজি ও বাংলায় লেখা।

## Added for years 1-9999 (v0.3)

- Planets outside 1800-2050: JPL Table 2a (3000 BC-3000 AD) of the same Standish paper, including its b, c, s, f terms for Jupiter and Saturn.
- Delta-T for years 1-1800: Espenak & Meeus polynomials (NASA GSFC, *Five Millennium Canon of Solar Eclipses*).
- Past-sky cross-check of the Sun: Meeus, *Astronomical Algorithms*, ch. 27 equinox formulas (independent of the planetary tables).
- Julian/Gregorian conversion: Julian Day Number algorithms (Fliegel & Van Flandern; Meeus ch. 7).
- Name syllables (namakshar), Ashtakavarga tables, divisional-chart rules: classical Parashari texts (Brihat Parashara Hora Shastra), checked by tests.


## Added for the Hindu calendar
- drikpanchang.com: 2026 Hindu festival list for New Delhi, Malayalam calendar page (used as comparison references, fetched 2026-11-18).
- dekhopanchang.com: Bangladesh revised Bangla month table; Tamil month table (approximate, not used as truth).
- hindupad.com: Pohela Boishakh 2026; 2027 festival list. kundligpt.com: 2025 festival list.
- panchangbodh.com: published Lahiri charts of Gandhi, Modi, Tagore.
- Method sources: Dharmashastra rules as summarised by drikpanchang (vyapti of tithi in udaya, madhyahna, aparahna, pradosha, nishitha), Bhadra (Vishti) karana
  rule, Indian National Calendar (Calendar Reform Committee 1957), Bangla Academy revised calendar (1966/1987).
