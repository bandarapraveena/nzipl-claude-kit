"""Shared helpers for the excess-capacity pipeline.

stdlib-only (json, os, pathlib). Keeps country naming, ISO3 mapping, unit
conversion, and JSON drop loading consistent across sector loaders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

PIPELINE_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PIPELINE_ROOT / "data"

COUNTRIES: list[tuple[str, str]] = [
    ("China", "CHN"),
    ("United States", "USA"),
    ("Germany", "DEU"),
    ("Japan", "JPN"),
    ("South Korea", "KOR"),
    ("India", "IND"),
    ("Australia", "AUS"),
    ("United Kingdom", "GBR"),
    ("France", "FRA"),
    ("Spain", "ESP"),
    ("Brazil", "BRA"),
    ("Mexico", "MEX"),
    ("Singapore", "SGP"),
    ("Vietnam", "VNM"),
    ("Thailand", "THA"),
    ("Malaysia", "MYS"),
    ("South Africa", "ZAF"),
    ("Romania", "ROU"),
    ("Poland", "POL"),
    ("Czech Republic", "CZE"),
]

NAME_BY_ISO3: dict[str, str] = {iso: name for name, iso in COUNTRIES}
ISO3_BY_NAME: dict[str, str] = {name.lower(): iso for name, iso in COUNTRIES}

# Common alternate names to the canonical ones above.
NAME_ALIASES: dict[str, str] = {
    "us": "United States",
    "u.s.": "United States",
    "usa": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "great britain": "United Kingdom",
    "korea": "South Korea",
    "korea, republic of": "South Korea",
    "republic of korea": "South Korea",
    "rok": "South Korea",
    "viet nam": "Vietnam",
    "czechia": "Czech Republic",
    "czech rep.": "Czech Republic",
}

SECTORS = ("solar_pv", "wind", "batteries", "evs")

SECTOR_UNIT: dict[str, str] = {
    "solar_pv": "GW",
    "wind": "GW",
    "batteries": "GWh",
    "evs": "million units",
}

# Per-sector year windows (inclusive) — see plan file and methodology.md.
SECTOR_YEAR_START: dict[str, int] = {
    "solar_pv": 2002,
    "wind": 2002,
    "batteries": 2010,
    "evs": 2010,
}
YEAR_END = 2025


def canonical_country(name: str) -> str | None:
    """Return the canonical country name if recognized, else None."""
    if not name:
        return None
    key = name.strip().lower()
    if key in ISO3_BY_NAME:
        return NAME_BY_ISO3[ISO3_BY_NAME[key]]
    if key in NAME_ALIASES:
        return NAME_ALIASES[key]
    # Allow ISO3 direct
    up = name.strip().upper()
    if up in NAME_BY_ISO3:
        return NAME_BY_ISO3[up]
    return None


def iso3(name: str) -> str | None:
    canon = canonical_country(name)
    if canon is None:
        return None
    return ISO3_BY_NAME[canon.lower()]


def to_gw(value: float, unit: str) -> float:
    unit = unit.strip().lower()
    if unit in ("gw", "gw/yr", "gw/year"):
        return value
    if unit in ("mw", "mw/yr"):
        return value / 1000.0
    if unit in ("kw",):
        return value / 1_000_000.0
    raise ValueError(f"unsupported power unit: {unit!r}")


def to_gwh(value: float, unit: str) -> float:
    unit = unit.strip().lower()
    if unit in ("gwh", "gwh/yr"):
        return value
    if unit in ("mwh",):
        return value / 1000.0
    if unit in ("twh",):
        return value * 1000.0
    raise ValueError(f"unsupported energy unit: {unit!r}")


def to_million_units(value: float, unit: str) -> float:
    unit = unit.strip().lower()
    if unit in ("million units", "m units", "m"):
        return value
    if unit in ("thousand units", "k units", "k"):
        return value / 1000.0
    if unit in ("units", "vehicles", "cars"):
        return value / 1_000_000.0
    raise ValueError(f"unsupported vehicle unit: {unit!r}")


def load_json_drops(subdir: str) -> list[dict[str, Any]]:
    """Load all *.json files under data/<subdir>/ recursively.

    Each file is expected to be a list of records OR an object with a "rows" key.
    Every record is expected to carry at minimum: country, year, sector, variable,
    value, unit, source (citation string).
    """
    root = DATA_ROOT / subdir
    if not root.exists():
        return []
    drops: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")):
        with path.open() as f:
            payload = json.load(f)
        rows = payload["rows"] if isinstance(payload, dict) and "rows" in payload else payload
        for row in rows:
            row.setdefault("_file", str(path.relative_to(PIPELINE_ROOT)))
            drops.append(row)
    return drops


def iter_country_years(sector: str) -> Iterable[tuple[str, int]]:
    start = SECTOR_YEAR_START[sector]
    for name, _ in COUNTRIES:
        for year in range(start, YEAR_END + 1):
            yield name, year
