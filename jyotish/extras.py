# Saheb Jyotish Sky Engine - Copyright (c) Saheb Mondal
# Licensed under CC BY-NC-SA 4.0 (see LICENSE and NOTICE). Credit to "Saheb Mondal" must be kept.
"""Extra add-ons: numerology, Western tropical signs."""
from __future__ import annotations

from datetime import date
from typing import Dict

from . import astro as A


def reduce_digit(n: int) -> int:
    """Reduce to a single digit 1-9 (no master-number exceptions)."""
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def numerology(d: date) -> Dict[str, int]:
    mulank = reduce_digit(d.day)                       # "psychic / birth number"
    bhagyank = reduce_digit(sum(int(c) for c in f"{d.day}{d.month}{d.year}"))  # "destiny / life-path number"
    return {"mulank": mulank, "bhagyank": bhagyank}


def western_signs(jd_ut: float, lat: float, lon: float) -> Dict[str, int]:
    """Tropical (Western) sign indexes 0..11 for Sun, Moon and Ascendant."""
    return {
        "sun": int(A.tropical_longitude("Sun", jd_ut) // 30) % 12,
        "moon": int(A.tropical_longitude("Moon", jd_ut) // 30) % 12,
        "ascendant": int(A.ascendant_tropical(jd_ut, lat, lon) // 30) % 12,
    }
