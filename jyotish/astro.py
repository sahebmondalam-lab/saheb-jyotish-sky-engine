# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""
Pure-Python astronomy core (no third-party packages needed).

Algorithms and data used (all published, open):
  * Sun & inner planets & Jupiter/Saturn : JPL "Keplerian Elements for Approximate
    Positions of the Major Planets" (E.M. Standish): Table 1 for 1800-2050 AD, Table 2a (3000 BC-3000 AD) elsewhere.
  * Moon : Jean Meeus, "Astronomical Algorithms" 2nd ed., chapter 47 (59 longitude terms).
  * Mean lunar node (Rahu) : Meeus chapter 47.
  * Delta-T : Espenak & Meeus polynomial expressions (NASA GSFC).
  * Ayanamsa : Lahiri (Chitrapaksha), ICRC definition, 23 deg 15' 00.658" at 1956-03-21.
  * Ascendant, sunrise/sunset : standard spherical-astronomy formulas (Meeus ch. 12-15).

Accuracy (typical, see docs/ACCURACY.md): Sun/Moon ~0.01-0.05 deg, inner planets
~0.01 deg, Jupiter/Saturn ~0.1 deg. Good for rashi, nakshatra, pada, tithi, dasha.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

J2000 = 2451545.0
DEG = math.pi / 180.0


# ----------------------------------------------------------------- small helpers
def norm360(x: float) -> float:
    return x % 360.0


def norm180(x: float) -> float:
    x = x % 360.0
    return x - 360.0 if x > 180.0 else x


def sind(x: float) -> float:
    return math.sin(x * DEG)


def cosd(x: float) -> float:
    return math.cos(x * DEG)


# ----------------------------------------------------------------- time
def julian_day(dt_utc: datetime) -> float:
    """Julian Day (UT) from an aware or naive-UTC datetime (proleptic Gregorian calendar, years 1-9999)."""
    from .calendars import jdn_gregorian
    if dt_utc.tzinfo is not None:
        dt_utc = dt_utc.astimezone(timezone.utc)
    frac = (dt_utc.hour + (dt_utc.minute + (dt_utc.second + dt_utc.microsecond / 1e6) / 60.0) / 60.0) / 24.0
    return jdn_gregorian(dt_utc.year, dt_utc.month, dt_utc.day) - 0.5 + frac


def datetime_from_jd(jd: float) -> datetime:
    """Aware UTC datetime (proleptic Gregorian) from Julian Day (UT)."""
    from .calendars import gregorian_from_jdn
    x = jd + 0.5
    z = int(math.floor(x))
    y, m, d = gregorian_from_jdn(z)
    secs = (x - z) * 86400.0
    return datetime(y, m, d, tzinfo=timezone.utc) + timedelta(seconds=round(secs))


def format_jd(jd: float, tz=None, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format a Julian Day as local time. Outside Python's year 1-9999 limit it falls back to UTC text with astronomical year numbers."""
    try:
        dt = datetime_from_jd(jd)
        return (dt.astimezone(tz) if tz is not None else dt).strftime(fmt)
    except (ValueError, OverflowError):
        from .calendars import gregorian_from_jdn
        x = jd + 0.5
        z = int(math.floor(x))
        y, m, d = gregorian_from_jdn(z)
        sec = int((x - z) * 86400)
        txt = f"{y:04d}-{m:02d}-{d:02d} {sec // 3600:02d}:{sec % 3600 // 60:02d}"
        return txt[:10] if fmt == "%Y-%m-%d" else txt


def delta_t(year: float) -> float:
    """TT - UT in seconds (Espenak & Meeus, NASA GSFC polynomials)."""
    y = year
    if y < 500:
        u = y / 100.0
        return 10583.6 - 1014.41 * u + 33.78311 * u**2 - 5.952053 * u**3 - 0.1798452 * u**4 + 0.022174192 * u**5 + 0.0090316521 * u**6
    if y < 1600:
        u = (y - 1000.0) / 100.0
        return 1574.2 - 556.01 * u + 71.23472 * u**2 + 0.319781 * u**3 - 0.8503463 * u**4 - 0.005050998 * u**5 + 0.0083572073 * u**6
    if y < 1700:
        t = y - 1600
        return 120.0 - 0.9808 * t - 0.01532 * t**2 + t**3 / 7129.0
    if y < 1800:
        t = y - 1700
        return 8.83 + 0.1603 * t - 0.0059285 * t**2 + 0.00013336 * t**3 - t**4 / 1174000.0
    if 1800 <= y < 1860:
        t = y - 1800
        return 13.72 - 0.332447 * t + 0.0068612 * t**2 + 0.0041116 * t**3 - 0.00037436 * t**4 \
            + 0.0000121272 * t**5 - 0.0000001699 * t**6 + 0.000000000875 * t**7
    if 1860 <= y < 1900:
        t = y - 1860
        return 7.62 + 0.5737 * t - 0.251754 * t**2 + 0.01680668 * t**3 - 0.0004473624 * t**4 + t**5 / 233174.0
    if 1900 <= y < 1920:
        t = y - 1900
        return -2.79 + 1.494119 * t - 0.0598939 * t**2 + 0.0061966 * t**3 - 0.000197 * t**4
    if 1920 <= y < 1941:
        t = y - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    if 1941 <= y < 1961:
        t = y - 1950
        return 29.07 + 0.407 * t - t**2 / 233.0 + t**3 / 2547.0
    if 1961 <= y < 1986:
        t = y - 1975
        return 45.45 + 1.067 * t - t**2 / 260.0 - t**3 / 718.0
    if 1986 <= y < 2005:
        t = y - 2000
        return 63.86 + 0.3345 * t - 0.060374 * t**2 + 0.0017275 * t**3 + 0.000651814 * t**4 + 0.00002373599 * t**5
    if 2005 <= y < 2050:
        t = y - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t**2
    if 2050 <= y < 2150:
        return -20.0 + 32.0 * ((y - 1820.0) / 100.0) ** 2 - 0.5628 * (2150.0 - y)
    u = (y - 1820.0) / 100.0
    return -20.0 + 32.0 * u * u


def jd_to_tt(jd_ut: float) -> float:
    year = 2000.0 + (jd_ut - J2000) / 365.25
    return jd_ut + delta_t(year) / 86400.0


def centuries(jd_tt: float) -> float:
    return (jd_tt - J2000) / 36525.0


# ----------------------------------------------------------------- ayanamsa
LAHIRI_T0_JD = 2435553.5                    # 1956-03-21 0h (ICRC epoch)
LAHIRI_AT_T0 = 23.250182778 - 0.004658035   # ICRC value minus nutation => mean ayanamsa
_PREC_A = 5029.0966                         # IAU 1976 general precession, arcsec / Julian century
_PREC_B = 1.11113


def precession_deg(T: float) -> float:
    """General precession in longitude since J2000, degrees."""
    return (_PREC_A * T + _PREC_B * T * T) / 3600.0


def ayanamsa_lahiri(jd_tt: float) -> float:
    """Mean Lahiri ayanamsa in degrees."""
    T = centuries(jd_tt)
    T0 = (LAHIRI_T0_JD - J2000) / 36525.0
    return LAHIRI_AT_T0 + (_PREC_A * (T - T0) + _PREC_B * (T * T - T0 * T0)) / 3600.0


# ----------------------------------------------------------------- Keplerian elements (JPL, 1800-2050)
# a0, a1, e0, e1, I0, I1, L0, L1, varpi0, varpi1, Omega0, Omega1  (AU, deg; rates per Julian century)
_ELEMENTS = {
    "Mercury": (0.38709927, 0.00000037, 0.20563593, 0.00001906, 7.00497902, -0.00594749,
                252.25032350, 149472.67411175, 77.45779628, 0.16047689, 48.33076593, -0.12534081),
    "Venus": (0.72333566, 0.00000390, 0.00677672, -0.00004107, 3.39467605, -0.00078890,
              181.97909950, 58517.81538729, 131.60246718, 0.00268329, 76.67984255, -0.27769418),
    "Earth": (1.00000261, 0.00000562, 0.01671123, -0.00004392, -0.00001531, -0.01294668,
              100.46457166, 35999.37244981, 102.93768193, 0.32327364, 0.0, 0.0),
    "Mars": (1.52371034, 0.00001847, 0.09339410, 0.00007882, 1.84969142, -0.00813131,
             -4.55343205, 19140.30268499, -23.94362959, 0.44441088, 49.55953891, -0.29257343),
    "Jupiter": (5.20288700, -0.00011607, 0.04838624, -0.00013253, 1.30439695, -0.00183714,
                34.39644051, 3034.74612775, 14.72847983, 0.21252668, 100.47390909, 0.20469106),
    "Saturn": (9.53667594, -0.00125060, 0.05386179, -0.00050991, 2.48599187, 0.00193609,
               49.95424423, 1222.49362201, 92.59887831, -0.41897216, 113.66242448, -0.28867794),
}


# JPL Table 2a (valid 3000 BC - 3000 AD): same layout, plus b, c, s, f for the outer planets:
# M = L - varpi + b*T^2 + c*cos(f*T) + s*sin(f*T)   (T in Julian centuries from J2000, f in degrees per century)
_ELEMENTS_LONG = {
    "Mercury": (0.38709843, 0.00000000, 0.20563661, 0.00002123, 7.00559432, -0.00590158,
                252.25166724, 149472.67486623, 77.45771895, 0.15940013, 48.33961819, -0.12214182),
    "Venus": (0.72332102, -0.00000026, 0.00676399, -0.00005107, 3.39777545, 0.00043494,
              181.97970850, 58517.81560260, 131.76755713, 0.05679648, 76.67261496, -0.27274174),
    "Earth": (1.00000018, -0.00000003, 0.01673163, -0.00003661, -0.00054346, -0.01337178,
              100.46691572, 35999.37306329, 102.93005885, 0.31795260, -5.11260389, -0.24123856),
    "Mars": (1.52371243, 0.00000097, 0.09336511, 0.00009149, 1.85181869, -0.00724757,
             -4.56813164, 19140.29934243, -23.91744784, 0.45223625, 49.71320984, -0.26852431),
    "Jupiter": (5.20248019, -0.00002864, 0.04853590, 0.00018026, 1.29861416, -0.00322699,
                34.33479152, 3034.90371757, 14.27495244, 0.18199196, 100.29282654, 0.13024619),
    "Saturn": (9.54149883, -0.00003065, 0.05550825, -0.00032044, 2.49424102, 0.00451969,
               50.07571329, 1222.11494724, 92.86136063, 0.54179478, 113.63998702, -0.25015002),
}
_EXTRA_LONG = {"Jupiter": (-0.00012452, 0.06064060, -0.35635438, 38.35125000),
               "Saturn": (0.00025899, -0.13434469, 0.87320147, 38.35125000)}
TABLE1_T0, TABLE1_T1 = -2.0, 0.5            # 1800 .. 2050 in Julian centuries from J2000


def _kepler(M_deg: float, e: float) -> float:
    M = norm180(M_deg) * DEG
    E = M + e * math.sin(M)
    for _ in range(30):
        d = (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
        E -= d
        if abs(d) < 1e-12:
            break
    return E


def _helio_xyz(name: str, T: float) -> Tuple[float, float, float]:
    long_term = not (TABLE1_T0 <= T <= TABLE1_T1)
    a0, a1, e0, e1, i0, i1, l0, l1, w0, w1, o0, o1 = (_ELEMENTS_LONG if long_term else _ELEMENTS)[name]
    a = a0 + a1 * T
    e = e0 + e1 * T
    inc = i0 + i1 * T
    L = l0 + l1 * T
    varpi = w0 + w1 * T
    node = o0 + o1 * T
    omega = varpi - node
    M = L - varpi
    if long_term and name in _EXTRA_LONG:
        b, c, sc, f = _EXTRA_LONG[name]
        M += b * T * T + c * cosd(f * T) + sc * sind(f * T)
    E = _kepler(M, e)
    xp = a * (math.cos(E) - e)
    yp = a * math.sqrt(1.0 - e * e) * math.sin(E)
    co, so = cosd(omega), sind(omega)
    cn, sn = cosd(node), sind(node)
    ci, si = cosd(inc), sind(inc)
    x = (co * cn - so * sn * ci) * xp + (-so * cn - co * sn * ci) * yp
    y = (co * sn + so * cn * ci) * xp + (-so * sn + co * cn * ci) * yp
    z = (so * si) * xp + (co * si) * yp
    return x, y, z


# ----------------------------------------------------------------- Sun, planets, Moon, node
def sun_longitude(T: float) -> float:
    """Apparent geocentric Sun longitude, mean equinox of date, degrees."""
    ex, ey, ez = _helio_xyz("Earth", T)
    lon = math.degrees(math.atan2(-ey, -ex))
    r = math.sqrt(ex * ex + ey * ey + ez * ez)
    lon = lon + precession_deg(T) - 0.0056933 / r   # + precession, - aberration
    return norm360(lon)


def planet_longitude(name: str, T: float) -> float:
    """Geocentric ecliptic longitude (mean equinox of date), light-time corrected."""
    ex, ey, ez = _helio_xyz("Earth", T)
    px, py, pz = _helio_xyz(name, T)
    for _ in range(2):
        dx, dy, dz = px - ex, py - ey, pz - ez
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        px, py, pz = _helio_xyz(name, T - dist * 0.0057755183 / 36525.0)
    lon = math.degrees(math.atan2(py - ey, px - ex))
    return norm360(lon + precession_deg(T))


# Meeus table 47.A: (D, M, M', F, coefficient of sin  in 1e-6 degree)
_MOON_L = [
    (0, 0, 1, 0, 6288774), (2, 0, -1, 0, 1274027), (2, 0, 0, 0, 658314), (0, 0, 2, 0, 213618),
    (0, 1, 0, 0, -185116), (0, 0, 0, 2, -114332), (2, 0, -2, 0, 58793), (2, -1, -1, 0, 57066),
    (2, 0, 1, 0, 53322), (2, -1, 0, 0, 45758), (0, 1, -1, 0, -40923), (1, 0, 0, 0, -34720),
    (0, 1, 1, 0, -30383), (2, 0, 0, -2, 15327), (0, 0, 1, 2, -12528), (0, 0, 1, -2, 10980),
    (4, 0, -1, 0, 10675), (0, 0, 3, 0, 10034), (4, 0, -2, 0, 8548), (2, 1, -1, 0, -7888),
    (2, 1, 0, 0, -6766), (1, 0, -1, 0, -5163), (1, 1, 0, 0, 4987), (2, -1, 1, 0, 4036),
    (2, 0, 2, 0, 3994), (4, 0, 0, 0, 3861), (2, 0, -3, 0, 3665), (0, 1, -2, 0, -2689),
    (2, 0, -1, 2, -2602), (2, -1, -2, 0, 2390), (1, 0, 1, 0, -2348), (2, -2, 0, 0, 2236),
    (0, 1, 2, 0, -2120), (0, 2, 0, 0, -2069), (2, -2, -1, 0, 2048), (2, 0, 1, -2, -1773),
    (2, 0, 0, 2, -1595), (4, -1, -1, 0, 1215), (0, 0, 2, 2, -1110), (3, 0, -1, 0, -892),
    (2, 1, 1, 0, -810), (4, -1, -2, 0, 759), (0, 2, -1, 0, -713), (2, 2, -1, 0, -700),
    (2, 1, -2, 0, 691), (2, -1, 0, -2, 596), (4, 0, 1, 0, 549), (0, 0, 4, 0, 537),
    (4, -1, 0, 0, 520), (1, 0, -2, 0, -487), (2, 1, 0, -2, -399), (0, 0, 2, -2, -381),
    (1, 1, 1, 0, 351), (3, 0, -2, 0, -340), (4, 0, -3, 0, 330), (2, -1, 2, 0, 327),
    (0, 2, 1, 0, -323), (1, 1, -1, 0, 299), (2, 0, 3, 0, 294),
]


def moon_longitude(T: float) -> float:
    """Geocentric Moon longitude, mean equinox of date, degrees (Meeus ch.47)."""
    Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + T**3 / 538841.0 - T**4 / 65194000.0
    D = 297.8501921 + 445267.1114034 * T - 0.0018819 * T * T + T**3 / 545868.0 - T**4 / 113065000.0
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T**3 / 24490000.0
    Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T**3 / 69699.0 - T**4 / 14712000.0
    F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T * T - T**3 / 3526000.0 + T**4 / 863310000.0
    A1 = 119.75 + 131.849 * T
    A2 = 53.09 + 479264.290 * T
    E = 1.0 - 0.002516 * T - 0.0000074 * T * T
    s = 0.0
    for d, m, mp, f, c in _MOON_L:
        arg = d * D + m * M + mp * Mp + f * F
        s += c * (E ** abs(m)) * sind(arg)
    s += 3958.0 * sind(A1) + 1962.0 * sind(Lp - F) + 318.0 * sind(A2)
    return norm360(Lp + s / 1.0e6)


def mean_node(T: float) -> float:
    """Mean ascending lunar node (Rahu), mean equinox of date."""
    return norm360(125.0445479 - 1934.1362891 * T + 0.0020754 * T * T + T**3 / 467441.0 - T**4 / 60616000.0)


GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def tropical_longitude(name: str, jd_ut: float) -> float:
    T = centuries(jd_to_tt(jd_ut))
    if name == "Sun":
        return sun_longitude(T)
    if name == "Moon":
        return moon_longitude(T)
    if name == "Rahu":
        return mean_node(T)
    if name == "Ketu":
        return norm360(mean_node(T) + 180.0)
    return planet_longitude(name, T)


def sidereal_longitude(name: str, jd_ut: float) -> float:
    jd_tt = jd_to_tt(jd_ut)
    return norm360(tropical_longitude(name, jd_ut) - ayanamsa_lahiri(jd_tt))


def daily_speed(name: str, jd_ut: float) -> float:
    """Apparent motion in degrees/day (negative = retrograde)."""
    a = tropical_longitude(name, jd_ut - 0.5)
    b = tropical_longitude(name, jd_ut + 0.5)
    return norm180(b - a)


def all_positions(jd_ut: float) -> Dict[str, dict]:
    ay = ayanamsa_lahiri(jd_to_tt(jd_ut))
    out = {}
    for g in GRAHAS:
        trop = tropical_longitude(g, jd_ut)
        sp = -0.0529539 if g in ("Rahu", "Ketu") else daily_speed(g, jd_ut)
        out[g] = {
            "tropical": trop,
            "sidereal": norm360(trop - ay),
            "speed": sp,
            "retrograde": sp < 0 and g not in ("Sun", "Moon"),
        }
    return out


# ----------------------------------------------------------------- ascendant, houses, sunrise
def mean_obliquity(T: float) -> float:
    return 23.0 + 26.0 / 60.0 + 21.448 / 3600.0 - (46.8150 * T + 0.00059 * T * T - 0.001813 * T**3) / 3600.0


def gmst(jd_ut: float) -> float:
    d = jd_ut - J2000
    T = d / 36525.0
    return norm360(280.46061837 + 360.98564736629 * d + 0.000387933 * T * T - T**3 / 38710000.0)


def ascendant_tropical(jd_ut: float, lat: float, lon_east: float) -> float:
    ramc = norm360(gmst(jd_ut) + lon_east)
    eps = mean_obliquity(centuries(jd_to_tt(jd_ut)))
    y = cosd(ramc)
    x = -(sind(ramc) * cosd(eps) + math.tan(lat * DEG) * sind(eps))
    return norm360(math.degrees(math.atan2(y, x)))


def midheaven_tropical(jd_ut: float, lon_east: float) -> float:
    ramc = norm360(gmst(jd_ut) + lon_east)
    eps = mean_obliquity(centuries(jd_to_tt(jd_ut)))
    return norm360(math.degrees(math.atan2(sind(ramc), cosd(ramc) * cosd(eps))))


def ascendant_sidereal(jd_ut: float, lat: float, lon_east: float) -> float:
    ay = ayanamsa_lahiri(jd_to_tt(jd_ut))
    return norm360(ascendant_tropical(jd_ut, lat, lon_east) - ay)


def sun_ra_dec(jd_ut: float) -> Tuple[float, float]:
    T = centuries(jd_to_tt(jd_ut))
    lon = sun_longitude(T)
    eps = mean_obliquity(T)
    ra = math.degrees(math.atan2(cosd(eps) * sind(lon), cosd(lon))) % 360.0
    dec = math.degrees(math.asin(sind(eps) * sind(lon)))
    return ra, dec


def _solve_hour_angle_event(jd_guess: float, lat: float, lon_east: float, rising: bool) -> Optional[float]:
    h0 = -0.8333  # standard refraction + solar semi-diameter
    t = jd_guess
    for _ in range(8):
        ra, dec = sun_ra_dec(t)
        cosH = (sind(h0) - sind(lat) * sind(dec)) / (cosd(lat) * cosd(dec))
        if cosH < -1.0 or cosH > 1.0:
            return None  # polar day / night
        H0 = math.degrees(math.acos(cosH))
        target = -H0 if rising else H0
        H = norm180(gmst(t) + lon_east - ra)
        diff = norm180(H - target)
        t -= diff / 360.985647
        if abs(diff) < 1e-4:
            break
    return t


def sunrise_sunset(jd_local_midnight_ut: float, lat: float, lon_east: float) -> Tuple[Optional[float], Optional[float]]:
    """Sunrise & sunset as UT Julian days for the civil day starting at the given local midnight (as UT JD)."""
    rise = _solve_hour_angle_event(jd_local_midnight_ut + 0.25, lat, lon_east, True)
    sset = _solve_hour_angle_event(jd_local_midnight_ut + 0.75, lat, lon_east, False)
    return rise, sset
