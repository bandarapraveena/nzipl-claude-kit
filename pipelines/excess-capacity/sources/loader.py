"""Load per-variable observations from JSON drops and resolve conflicts.

A "drop" is a JSON file under data/public/<source>/ or data/manual/<source>/.
Each row must carry: country, year, sector, variable, value, unit, source.
Optional: is_forecast, notes, priority (higher wins when multiple drops report
the same cell).

Values are unit-normalized to the canonical unit for each sector.
"""
from __future__ import annotations

from typing import Any

from ._common import (
    SECTOR_UNIT,
    canonical_country,
    load_json_drops,
    to_gw,
    to_gwh,
    to_million_units,
)

VARIABLES = ("capacity", "production", "demand")


def _normalize_value(sector: str, variable: str, value: float, unit: str) -> float:
    canonical = SECTOR_UNIT[sector]
    if canonical == "GW":
        return to_gw(value, unit)
    if canonical == "GWh":
        return to_gwh(value, unit)
    if canonical == "million units":
        return to_million_units(value, unit)
    raise ValueError(f"unknown canonical unit for sector {sector!r}")


def _key(row: dict[str, Any]) -> tuple[str, int, str, str] | None:
    country = canonical_country(row.get("country", ""))
    if country is None:
        return None
    try:
        year = int(row["year"])
    except (KeyError, TypeError, ValueError):
        return None
    sector = row.get("sector")
    variable = row.get("variable")
    if sector not in SECTOR_UNIT or variable not in VARIABLES:
        return None
    return country, year, sector, variable


def load_observations() -> dict[tuple[str, int, str, str], dict[str, Any]]:
    """Return a dict keyed by (country, year, sector, variable) → observation.

    Higher-priority drops win ties; within the same priority, manual drops
    (data/manual/) override public ones (data/public/).
    """
    drops: list[dict[str, Any]] = []
    for tier, subdir in (("public", "public"), ("manual", "manual")):
        for row in load_json_drops(subdir):
            row.setdefault("_tier", tier)
            drops.append(row)

    def rank(row: dict[str, Any]) -> tuple[int, int]:
        tier_rank = 1 if row.get("_tier") == "manual" else 0
        return (row.get("priority", 0), tier_rank)

    observations: dict[tuple[str, int, str, str], dict[str, Any]] = {}
    skipped: list[dict[str, Any]] = []
    for row in drops:
        key = _key(row)
        if key is None:
            skipped.append(row)
            continue
        existing = observations.get(key)
        if existing is not None and rank(existing) >= rank(row):
            continue
        country, year, sector, variable = key
        try:
            value = _normalize_value(sector, variable, float(row["value"]), row["unit"])
        except (KeyError, TypeError, ValueError) as exc:
            skipped.append({**row, "_error": str(exc)})
            continue
        observations[key] = {
            "country": country,
            "year": year,
            "sector": sector,
            "variable": variable,
            "value": value,
            "unit": SECTOR_UNIT[sector],
            "source": row.get("source", ""),
            "is_forecast": bool(row.get("is_forecast", False)),
            "notes": row.get("notes", ""),
            "_file": row.get("_file", ""),
            "_tier": row.get("_tier", ""),
        }
    if skipped:
        observations.setdefault("__skipped__", skipped)  # type: ignore[arg-type]
    return observations
