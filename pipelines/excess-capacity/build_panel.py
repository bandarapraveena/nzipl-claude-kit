"""Build the clean-tech excess-capacity country-year panel.

Reads every *.json file under data/public/ and data/manual/, resolves the
(country, year, sector, variable) observations, computes both the OECD-standard
and user-specified excess-capacity metrics, and emits:

  outputs/excess_capacity_panel.json   long-format panel
  outputs/excess_capacity_panel.csv    same data as CSV
  outputs/coverage.md                  sector × decade cell-fill report
  outputs/anchor_checks.md             sanity checks against published totals

Usage:
    python build_panel.py
    python build_panel.py --sector solar_pv
    python build_panel.py --country CHN

stdlib-only: json, argparse, csv, collections, pathlib.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from sources._common import (
    COUNTRIES,
    NAME_BY_ISO3,
    SECTOR_UNIT,
    SECTOR_YEAR_START,
    SECTORS,
    YEAR_END,
    iter_country_years,
)
from sources.loader import load_observations

PIPELINE_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PIPELINE_ROOT / "outputs"

PANEL_COLUMNS = [
    "country",
    "iso3",
    "year",
    "sector",
    "unit",
    "capacity",
    "capacity_source",
    "production",
    "production_source",
    "demand",
    "demand_source",
    "net_imports_proxy",
    "excess_capacity_oecd",
    "excess_capacity_user",
    "utilization",
    "is_forecast",
    "notes",
]


def _iso3(name: str) -> str:
    for n, iso in COUNTRIES:
        if n == name:
            return iso
    raise KeyError(name)


def build_rows(
    observations: dict[tuple[str, int, str, str], dict[str, Any]],
    sectors: tuple[str, ...],
    country_filter: set[str] | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sector in sectors:
        for country, year in iter_country_years(sector):
            if country_filter and country not in country_filter:
                continue
            obs = {
                var: observations.get((country, year, sector, var))
                for var in ("capacity", "production", "demand")
            }
            cap = obs["capacity"]["value"] if obs["capacity"] else None
            prod = obs["production"]["value"] if obs["production"] else None
            dem = obs["demand"]["value"] if obs["demand"] else None

            net_imports_proxy = (
                (dem - prod) if (dem is not None and prod is not None) else None
            )
            excess_oecd = (
                (cap - prod) if (cap is not None and prod is not None) else None
            )
            excess_user = (
                (cap - (dem - prod))
                if (cap is not None and prod is not None and dem is not None)
                else None
            )
            utilization = (
                (prod / cap) if (cap not in (None, 0) and prod is not None) else None
            )

            is_forecast = any(
                bool(o and o.get("is_forecast")) for o in obs.values()
            )
            note_bits = [o["notes"] for o in obs.values() if o and o.get("notes")]

            rows.append(
                {
                    "country": country,
                    "iso3": _iso3(country),
                    "year": year,
                    "sector": sector,
                    "unit": SECTOR_UNIT[sector],
                    "capacity": cap,
                    "capacity_source": obs["capacity"]["source"] if obs["capacity"] else "",
                    "production": prod,
                    "production_source": obs["production"]["source"] if obs["production"] else "",
                    "demand": dem,
                    "demand_source": obs["demand"]["source"] if obs["demand"] else "",
                    "net_imports_proxy": net_imports_proxy,
                    "excess_capacity_oecd": excess_oecd,
                    "excess_capacity_user": excess_user,
                    "utilization": utilization,
                    "is_forecast": is_forecast,
                    "notes": "; ".join(note_bits),
                }
            )
    return rows


def write_json(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(rows, f, indent=2, default=str)


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PANEL_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in PANEL_COLUMNS})


def coverage_report(rows: list[dict[str, Any]]) -> str:
    """Null-density matrix per sector × decade × variable."""
    def bucket(year: int) -> str:
        if year < 2010:
            return "2002–2009"
        if year < 2015:
            return "2010–2014"
        if year < 2020:
            return "2015–2019"
        return "2020–2025"

    counts: dict[tuple[str, str, str], list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        for var in ("capacity", "production", "demand"):
            key = (r["sector"], bucket(r["year"]), var)
            counts[key][0] += 1
            if r[var] is not None:
                counts[key][1] += 1

    lines = ["# Coverage report (filled cells / total cells)", ""]
    lines.append("| Sector | Decade | Capacity | Production | Demand |")
    lines.append("|---|---|---|---|---|")
    for sector in SECTORS:
        for dec in ("2002–2009", "2010–2014", "2015–2019", "2020–2025"):
            row_vals = []
            any_cell = False
            for var in ("capacity", "production", "demand"):
                total, filled = counts.get((sector, dec, var), (0, 0))
                if total == 0:
                    row_vals.append("—")
                else:
                    any_cell = True
                    pct = 100 * filled / total if total else 0
                    row_vals.append(f"{filled}/{total} ({pct:.0f}%)")
            if any_cell:
                lines.append(f"| {sector} | {dec} | {row_vals[0]} | {row_vals[1]} | {row_vals[2]} |")
    return "\n".join(lines) + "\n"


def anchor_checks(rows: list[dict[str, Any]]) -> str:
    """Totals vs known published headline numbers (documented in methodology.md)."""
    totals: dict[tuple[str, int], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    counts: dict[tuple[str, int], int] = defaultdict(int)
    for r in rows:
        key = (r["sector"], r["year"])
        counts[key] += 1
        for v in ("capacity", "production", "demand"):
            if r[v] is not None:
                totals[key][v] += r[v]

    lines = ["# Anchor checks (20-country totals vs global headline figures)", ""]
    lines.append("These are advisory — the panel covers 20 countries, not the full world.")
    lines.append("")
    lines.append("| Sector | Year | Capacity (sum) | Production (sum) | Demand (sum) | Unit | Notes |")
    lines.append("|---|---|---|---|---|---|---|")
    hint = {
        ("solar_pv", 2024): "IEA: global module mfg capacity >1,100 GW",
        ("batteries", 2024): "IEA: global Li-ion cell capacity ~3,000 GWh",
        ("evs", 2024): "IEA: global EV sales ~17 (million units)",
        ("wind", 2024): "GWEC: global installations ~117 GW",
    }
    for sector in SECTORS:
        for year in (2010, 2015, 2020, 2024):
            if year < SECTOR_YEAR_START[sector]:
                continue
            agg = totals.get((sector, year), {})
            if not agg:
                continue
            lines.append(
                f"| {sector} | {year} | "
                f"{agg.get('capacity', 0):.1f} | "
                f"{agg.get('production', 0):.1f} | "
                f"{agg.get('demand', 0):.1f} | "
                f"{SECTOR_UNIT[sector]} | "
                f"{hint.get((sector, year), '')} |"
            )
    lines.append("")
    lines.append("Sanity bounds check:")
    bad = [r for r in rows if r["utilization"] is not None and (r["utilization"] < 0 or r["utilization"] > 1.05)]
    lines.append(f"- utilization outside [0, 1.05]: **{len(bad)} rows**")
    neg = [r for r in rows if r["excess_capacity_oecd"] is not None and r["excess_capacity_oecd"] < 0]
    lines.append(f"- excess_capacity_oecd negative: **{len(neg)} rows** (production > capacity)")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sector", choices=list(SECTORS), action="append",
                        help="Restrict to one or more sectors (repeatable).")
    parser.add_argument("--country", action="append",
                        help="ISO3 or canonical name; restrict rows to these countries.")
    args = parser.parse_args()

    sectors = tuple(args.sector) if args.sector else SECTORS
    country_filter: set[str] | None = None
    if args.country:
        resolved: set[str] = set()
        for c in args.country:
            up = c.strip().upper()
            if up in NAME_BY_ISO3:
                resolved.add(NAME_BY_ISO3[up])
            else:
                resolved.add(c)
        country_filter = resolved

    observations = load_observations()
    skipped = observations.pop("__skipped__", [])  # type: ignore[arg-type]

    rows = build_rows(observations, sectors, country_filter)

    write_json(rows, OUTPUT_DIR / "excess_capacity_panel.json")
    write_csv(rows, OUTPUT_DIR / "excess_capacity_panel.csv")
    (OUTPUT_DIR / "coverage.md").write_text(coverage_report(rows))
    (OUTPUT_DIR / "anchor_checks.md").write_text(anchor_checks(rows))

    print(f"wrote {len(rows)} rows to {OUTPUT_DIR / 'excess_capacity_panel.json'}")
    print(f"      {OUTPUT_DIR / 'excess_capacity_panel.csv'}")
    print(f"coverage report: {OUTPUT_DIR / 'coverage.md'}")
    print(f"anchor checks:   {OUTPUT_DIR / 'anchor_checks.md'}")
    filled = sum(1 for r in rows if any(r[v] is not None for v in ("capacity", "production", "demand")))
    print(f"rows with >=1 observation: {filled}/{len(rows)}")
    if skipped:
        print(f"skipped {len(skipped)} drop rows (see observations['__skipped__'])")


if __name__ == "__main__":
    main()
