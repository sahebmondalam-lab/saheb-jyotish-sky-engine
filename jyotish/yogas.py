# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""A deliberately small, classical set of yogas/doshas. Rules are simple and documented."""
from __future__ import annotations

from typing import Dict, List

from .data import EXALT, OWN

KENDRA = {1, 4, 7, 10}


def _house(sign: int, lagna: int) -> int:
    return (sign - lagna) % 12 + 1


def _strong(planet: str, sign: int) -> bool:
    return EXALT.get(planet) == sign or sign in OWN.get(planet, [])


def detect(planets: Dict[str, Dict], lagna_sign: int) -> List[str]:
    """planets: name -> {'sign': int, 'sidereal': float}. Returns a list of yoga keys."""
    found: List[str] = []
    sign = {g: p["sign"] for g, p in planets.items()}

    # Gajakesari: Jupiter in kendra from Moon
    if (sign["Jupiter"] - sign["Moon"]) % 12 + 1 in KENDRA:
        found.append("gajakesari")
    if sign["Sun"] == sign["Mercury"]:
        found.append("budhaditya")
    if sign["Moon"] == sign["Mars"]:
        found.append("chandra_mangala")

    # Pancha Mahapurusha: own/exalted sign AND in a kendra from the Lagna
    for g, key in (("Mars", "ruchaka"), ("Mercury", "bhadra"), ("Jupiter", "hamsa"),
                   ("Venus", "malavya"), ("Saturn", "shasha")):
        if _strong(g, sign[g]) and _house(sign[g], lagna_sign) in KENDRA:
            found.append(key)

    # Kemadruma: no planet (other than Sun, nodes) in the Moon's sign or its 2nd/12th
    near = {sign["Moon"], (sign["Moon"] + 1) % 12, (sign["Moon"] - 1) % 12}
    if not any(sign[g] in near for g in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")):
        found.append("kemadruma")

    # Mangal dosha
    if _house(sign["Mars"], lagna_sign) in {1, 4, 7, 8, 12}:
        found.append("mangal_dosha")

    # Kaal Sarp: all seven planets on one side of the Rahu-Ketu axis
    rahu = planets["Rahu"]["sidereal"]
    sides = [((planets[g]["sidereal"] - rahu) % 360.0) < 180.0
             for g in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")]
    if all(sides) or not any(sides):
        found.append("kaal_sarp")
    return found
