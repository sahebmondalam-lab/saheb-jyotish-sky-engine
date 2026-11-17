# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Compare this engine with NASA/JPL Horizons (the reference ephemeris) on YOUR machine.

    python tools/verify_with_horizons.py                 # default test dates
    python tools/verify_with_horizons.py 2026-11-16T04:30

Needs internet access to https://ssd.jpl.nasa.gov (public, no key). Uses only the standard library.
Horizons quantity 31 = observer ecliptic longitude/latitude (of date). Our values are tropical
ecliptic longitude of date, so the two are directly comparable (differences of a few
thousandths of a degree come from nutation, which this engine does not apply).
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jyotish import astro as A  # noqa: E402

BODIES = {"Sun": "10", "Moon": "301", "Mercury": "199", "Venus": "299", "Mars": "499",
          "Jupiter": "599", "Saturn": "699"}
TOLERANCE = {"Sun": 0.05, "Moon": 0.05, "Mercury": 0.05, "Venus": 0.05, "Mars": 0.05,
             "Jupiter": 0.2, "Saturn": 0.2}
DEFAULT_DATES = ["1947-08-15T00:00", "1995-08-15T09:00", "2000-01-01T12:00", "2026-11-16T04:30", "2040-06-01T00:00"]


def horizons_longitude(command: str, jd_ut: float) -> float:
    params = {
        "format": "json", "COMMAND": f"'{command}'", "OBJ_DATA": "'NO'", "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'", "CENTER": "'500@399'", "TLIST": f"'{jd_ut:.6f}'",
        "QUANTITIES": "'31'", "CSV_FORMAT": "'YES'", "CAL_FORMAT": "'JD'", "ANG_FORMAT": "'DEG'",
    }
    url = "https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as r:
        result = json.load(r)["result"]
    return parse_longitude(result)


def parse_longitude(result_text: str) -> float:
    m = re.search(r"\$\$SOE\s*(.*?)\s*\$\$EOE", result_text, re.S)
    if not m:
        raise RuntimeError("Horizons reply had no data block:\n" + result_text[:500])
    row = m.group(1).splitlines()[0]
    nums = []
    for cell in row.split(","):
        try:
            nums.append(float(cell.strip()))
        except ValueError:
            pass
    if len(nums) < 3:
        raise RuntimeError(f"Could not parse Horizons row: {row!r}")
    return nums[1] % 360.0      # nums = [JD, ecliptic longitude, ecliptic latitude]


def main() -> int:
    dates = sys.argv[1:] or DEFAULT_DATES
    worst_fail = False
    print(f"{'UTC time':17s} {'body':8s} {'engine':>10s} {'NASA':>10s} {'diff(deg)':>10s}  result")
    for text in dates:
        dt = datetime.fromisoformat(text).replace(tzinfo=timezone.utc)
        jd = A.julian_day(dt)
        for name, cmd in BODIES.items():
            ours = A.tropical_longitude(name, jd)
            nasa = horizons_longitude(cmd, jd)
            diff = A.norm180(ours - nasa)
            ok = abs(diff) <= TOLERANCE[name]
            worst_fail |= not ok
            print(f"{text:17s} {name:8s} {ours:10.4f} {nasa:10.4f} {diff:+10.4f}  {'OK' if ok else 'TOO FAR'}")
    return 1 if worst_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
