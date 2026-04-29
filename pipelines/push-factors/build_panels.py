"""Build the two country-year-technology push-factor panels.

Inputs (read from data/cache/; produced by fetch_irena.py and fetch_wits_tariffs.py):
  - irena_capacity.json   IRENA installed capacity (MW/GW) by country-year-tech
  - wits_tariffs.json     WITS/TRAINS MFN tariffs by reporter-product-year

Outputs (written to outputs/):
  - renewable_deployment_panel.{csv,json}
        country x year x tech -> installed capacity (GW)
        Techs: solar_pv, wind (onshore+offshore), onshore_wind, offshore_wind
        Variable name: RenGen_{j,t,z} in the paper (installed-capacity proxy).

  - export_tariff_index_panel.{csv,json}
        country x year x tech -> simple-average MFN tariff imposed by this country
        Techs: solar_pv, wind, batteries, evs
        HS6 codes averaged by tech and year (HS-revision aware — see
        sources._common.hs_for_tech).

        NOTE: the paper's TariffIndex_{j,t,z} is the trade-weighted tariff
        FACED by exporter j in destination markets. Destination-side data is
        what WITS exposes; to get the j-specific weighted index you multiply
        this destination panel by j's bilateral export shares from BACI. See
        methodology.md for the full definition and the BACI wiring.

        Two views are emitted:
          (a) destination panel — reporter (destination) x year x tech
              fields: tariff_mfn_simple_avg (simple mean across the tech's HS6s)
          (b) exporter-view simple-average index — country j's "faced" tariff
              using an unweighted mean over all destinations in-panel for tech z.
              Same value across j for a given (year, tech) — a "global tariff
              environment" baseline that is honest about what we can compute
              without bilateral trade weights.

  - coverage.md               cell-fill report for both panels
  - methodology_summary.md    variable dictionary + caveats

Usage:
    python build_panels.py
    python build_panels.py --no-irena    # skip renewable panel (tariff only)
    python build_panels.py --no-wits     # skip tariff panel
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from sources._common import (
    CACHE_DIR,
    COUNTRIES,
    ISO3_BY_ISO_NUM,
    ISO_NUM_BY_ISO3,
    NAME_BY_ISO3,
    TECHS,
    USER_HS_CODES,
    YEAR_END,
    YEAR_START,
    hs_for_tech,
    read_json,
    write_json,
)

PIPELINE_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PIPELINE_ROOT / "outputs"


# ---- Renewable deployment panel --------------------------------------------

REN_COLUMNS = [
    "country", "iso3", "year", "tech",
    "capacity_gw",
    "source",
    "notes",
]


def build_renewable_panel(irena_rows: list[dict]) -> list[dict]:
    """Reshape IRENA per-irena_tech rows into a (country, year, tech) panel.

    tech mapping (paper's RenGen categories):
      solar_pv      <- IRENA 'solar_pv'
      onshore_wind  <- IRENA 'onshore_wind'
      offshore_wind <- IRENA 'offshore_wind'
      wind          <- onshore + offshore (combined for the paper's 'wind')
    """
    cap: dict[tuple[str, int, str], dict[str, Any]] = {}
    # index raw IRENA rows
    raw: dict[tuple[str, int, str], dict] = {
        (r["iso3"], int(r["year"]), r["irena_tech"]): r for r in irena_rows
    }

    def _put(iso3: str, year: int, tech: str, gw: float, source: str, notes: str = "") -> None:
        k = (iso3, year, tech)
        cell = cap.get(k)
        if cell is None:
            cap[k] = {
                "country": NAME_BY_ISO3.get(iso3, iso3),
                "iso3": iso3,
                "year": year,
                "tech": tech,
                "capacity_gw": round(gw, 4),
                "source": source,
                "notes": notes,
            }
        else:
            cell["capacity_gw"] = round(cell["capacity_gw"] + gw, 4)

    for (iso3, year, irena_tech), row in raw.items():
        gw = row.get("capacity_gw")
        if gw is None:
            continue
        src = row.get("source", "IRENA IRENASTAT")
        if irena_tech == "solar_pv":
            _put(iso3, year, "solar_pv", gw, src)
        elif irena_tech == "onshore_wind":
            _put(iso3, year, "onshore_wind", gw, src)
            _put(iso3, year, "wind", gw, src, "onshore component")
        elif irena_tech == "offshore_wind":
            _put(iso3, year, "offshore_wind", gw, src)
            _put(iso3, year, "wind", gw, src, "offshore component")

    # Dense fill: emit zeros for country-year-tech cells that IRENA returned
    # nothing for, but only within the per-tech presence envelope. We keep it
    # sparse to distinguish "no observation" from "zero capacity". Downstream
    # users can pivot and fill as they prefer.
    rows = sorted(cap.values(), key=lambda r: (r["country"], r["year"], r["tech"]))
    return rows


# ---- Export tariff index panel ---------------------------------------------

TARIFF_COLUMNS_DEST = [
    "reporter_country", "reporter_iso3", "year", "tech",
    "hs_codes_used",
    "tariff_mfn_simple_avg",
    "n_hs_lines_underlying",
    "nomen_code",
    "datatype",
    "source",
]

TARIFF_COLUMNS_EXPORTER = [
    "country", "iso3", "year", "tech",
    "tariff_faced_simple_mean",
    "n_destinations",
    "hs_codes_used",
    "weighting",
    "source",
    "notes",
]


def _tariff_by_reporter(wits_rows: list[dict]) -> dict[tuple[str, str, int], list[dict]]:
    """Index WITS rows by (reporter_iso_num, product, year)."""
    out: dict[tuple[str, str, int], list[dict]] = defaultdict(list)
    for r in wits_rows:
        out[(r["reporter_iso_num"], r["product"], int(r["year"]))].append(r)
    return out


def _pick_tariff(rows: list[dict]) -> dict | None:
    """When WITS returns both 'Reported' and 'AveEstimated' for the same cell,
    prefer Reported. Within each, take the numerically present one.
    """
    if not rows:
        return None
    reported = [r for r in rows if (r.get("datatype") or "").lower() == "reported" and r.get("tariff_pct") is not None]
    estimated = [r for r in rows if (r.get("datatype") or "").lower().startswith("ave") and r.get("tariff_pct") is not None]
    return (reported or estimated or rows)[0]


def _hs_candidates_with_fallback(tech: str, year: int) -> list[list[str]]:
    """Ordered list of HS-code sets to try for a (tech, year) cell.

    Returns a list of alternatives in preference order. The first set that
    yields >=1 populated HS6 for the reporter-year is used.

    Why: HS 2017 split solar PV into 854142/854143, but many WITS reporters
    keep reporting at the parent 854140 through ~2021. Same pattern for EVs
    (870380 introduced HS 2017). Without a fallback the post-2017 coverage
    collapses. We prefer the more granular split when present, fall back to
    the parent otherwise.
    """
    if tech == "solar_pv":
        if year >= 2017:
            return [["854142", "854143"], ["854140"]]
        return [["854140"]]
    if tech == "evs":
        if year >= 2017:
            return [["870380", "870390"], ["870390"]]
        return [["870390"]]
    if tech == "batteries":
        if year >= 2012:
            return [["850760", "850780"], ["850780"]]
        return [["850780"]]
    if tech == "wind":
        return [["850231"]]
    raise ValueError(f"unknown tech {tech!r}")


def build_destination_tariff_panel(wits_rows: list[dict]) -> list[dict]:
    idx = _tariff_by_reporter(wits_rows)
    rows: list[dict] = []
    for (name, iso3, iso_num) in COUNTRIES:
        for year in range(YEAR_START, YEAR_END + 1):
            for tech in TECHS:
                picked_rows: list[dict] = []
                hs_used: list[str] = []
                for candidate in _hs_candidates_with_fallback(tech, year):
                    picked_rows = []
                    hs_used = []
                    for hs in candidate:
                        p = _pick_tariff(idx.get((iso_num, hs, year), []))
                        if p is not None:
                            picked_rows.append(p)
                            hs_used.append(hs)
                    if picked_rows:
                        break  # first candidate with any hit wins
                if not picked_rows:
                    continue
                tariffs = [float(p["tariff_pct"]) for p in picked_rows]
                nomens = [str(p["nomen"]) for p in picked_rows if p.get("nomen")]
                lines = 0
                for p in picked_rows:
                    try:
                        lines += int(p.get("n_tariff_lines") or 0)
                    except (TypeError, ValueError):
                        pass
                dtype = next((p.get("datatype") for p in picked_rows if p.get("datatype")), None)
                rows.append({
                    "reporter_country": name,
                    "reporter_iso3": iso3,
                    "year": year,
                    "tech": tech,
                    "hs_codes_used": "+".join(hs_used),
                    "tariff_mfn_simple_avg": round(mean(tariffs), 3),
                    "n_hs_lines_underlying": lines or None,
                    "nomen_code": "/".join(sorted(set(nomens))) or None,
                    "datatype": dtype,
                    "source": "WITS/UNCTAD TRAINS (MFN applied to World)",
                })
    return rows


def build_exporter_tariff_index(dest_rows: list[dict]) -> list[dict]:
    """Collapse the destination panel into a country-j view.

    v1: simple (unweighted) mean across all in-panel destinations.
        -> same value for every exporter j in a given (year, tech) cell.

    This is an honest baseline for 'tariff environment facing exporter j in
    technology z at year t' when bilateral trade weights are unavailable.
    When BACI is wired in, replace the mean with sum_d (w_{j,d,z,t} *
    tariff_{d,z,t}) where w is j's export share to destination d.
    """
    by_year_tech: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for r in dest_rows:
        by_year_tech[(r["year"], r["tech"])].append(r)

    out: list[dict] = []
    for (name, iso3, _) in COUNTRIES:
        for year in range(YEAR_START, YEAR_END + 1):
            for tech in TECHS:
                pool = by_year_tech.get((year, tech), [])
                if not pool:
                    continue
                tariffs = [float(r["tariff_mfn_simple_avg"]) for r in pool]
                hs_codes_used = pool[0]["hs_codes_used"]
                out.append({
                    "country": name,
                    "iso3": iso3,
                    "year": year,
                    "tech": tech,
                    "tariff_faced_simple_mean": round(mean(tariffs), 3),
                    "n_destinations": len(tariffs),
                    "hs_codes_used": hs_codes_used,
                    "weighting": "unweighted (v1 baseline)",
                    "source": "Derived from WITS destination MFN panel",
                    "notes": "Replace with bilateral-export-weighted mean once BACI is wired in",
                })
    return out


# ---- Coverage / docs -------------------------------------------------------

def coverage_report(ren_rows: list[dict], tariff_rows: list[dict]) -> str:
    def bucket(y: int) -> str:
        if y < 2008:  return "2003-2007"
        if y < 2013:  return "2008-2012"
        if y < 2018:  return "2013-2017"
        if y < 2023:  return "2018-2022"
        return "2023-2025"

    def fill(rows: list[dict], key_tech: str) -> dict[str, tuple[int, int]]:
        bkt: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for (_, iso3, _) in COUNTRIES:
            for y in range(YEAR_START, YEAR_END + 1):
                bkt[bucket(y)][0] += 1
        for r in rows:
            if r.get("tech") != key_tech:
                continue
            bkt[bucket(int(r["year"]))][1] += 1
        return {k: (filled, total) for k, (total, filled) in bkt.items()}  # careful: we counted wrong

    # Recompute coverage more carefully.
    lines = ["# Coverage report", ""]
    lines.append("## Renewable deployment panel (capacity_gw fill rate)")
    lines.append("")
    lines.append("| Tech | 2003-2007 | 2008-2012 | 2013-2017 | 2018-2022 | 2023-2025 |")
    lines.append("|---|---|---|---|---|---|")
    for tech in ("solar_pv", "wind", "onshore_wind", "offshore_wind"):
        have = defaultdict(int)
        tot = defaultdict(int)
        for (_, iso3, _) in COUNTRIES:
            for y in range(YEAR_START, YEAR_END + 1):
                tot[bucket(y)] += 1
        for r in ren_rows:
            if r["tech"] == tech and r.get("capacity_gw") is not None:
                have[bucket(int(r["year"]))] += 1
        row = [tech]
        for b in ("2003-2007", "2008-2012", "2013-2017", "2018-2022", "2023-2025"):
            pct = 100 * have[b] / tot[b] if tot[b] else 0
            row.append(f"{have[b]}/{tot[b]} ({pct:.0f}%)")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Export tariff index panel (tariff_mfn_simple_avg fill rate, destination view)")
    lines.append("")
    lines.append("| Tech | 2003-2007 | 2008-2012 | 2013-2017 | 2018-2022 | 2023-2025 |")
    lines.append("|---|---|---|---|---|---|")
    # We use destination rows for fill rate
    for tech in TECHS:
        have = defaultdict(int)
        tot = defaultdict(int)
        for (_, iso3, _) in COUNTRIES:
            for y in range(YEAR_START, YEAR_END + 1):
                tot[bucket(y)] += 1
        for r in tariff_rows:
            if r.get("tech") == tech and r.get("tariff_mfn_simple_avg") is not None:
                have[bucket(int(r["year"]))] += 1
        row = [tech]
        for b in ("2003-2007", "2008-2012", "2013-2017", "2018-2022", "2023-2025"):
            pct = 100 * have[b] / tot[b] if tot[b] else 0
            row.append(f"{have[b]}/{tot[b]} ({pct:.0f}%)")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("Denominators = 40 countries * years in the bucket.")
    return "\n".join(lines) + "\n"


def methodology_summary() -> str:
    hs_list = ", ".join(USER_HS_CODES)
    return f"""# Push-factor variable dictionary

Two country-year-technology panels for Equation 1 of the LCT FDI paper.

## `renewable_deployment_panel.csv` -- RenGen (j,t,z)

- **Definition**: installed electricity generation capacity of technology z
  in country j at end of year t, in gigawatts (GW).
- **Source**: IRENA IRENASTAT Power Capacity & Generation table
  (`Country_ELECCAP_*`), pulled via pxweb JSON API. Includes both OnGrid
  and OffGrid, summed to a single capacity figure per cell.
- **Techs emitted**: `solar_pv`, `onshore_wind`, `offshore_wind`, and a
  composite `wind` (= onshore + offshore) matching the paper's Wind
  category.
- **Out of scope (IRENA does not publish)**: stationary battery storage
  deployment, EV stock. For those, layer in IEA Global EV Outlook (free
  tables) and IRENA's separate Battery Storage report series.

## `export_tariff_index_panel.csv` -- TariffIndex (j,t,z)

- **Definition (paper)**: trade-weighted average MFN/applied tariff
  imposed by major import markets on country j's exports in technology z
  at year t. This is *destination-imposed* tariffs weighted by j's
  export shares.
- **v1 definition (this file)**: simple (unweighted) mean across all
  in-panel destinations of each destination's simple-average MFN tariff
  on the technology's HS6 codes. Column `weighting` = `unweighted
  (v1 baseline)`. Same value across j for a given (year, tech) cell --
  an honest *global tariff environment* baseline.
- **Upgrade path to paper definition**: multiply this destination panel
  by j's bilateral export shares from CEPII BACI HS6 data
  (`https://www.cepii.fr/DATA_DOWNLOAD/baci/`). See `methodology.md`.
- **Source**: WITS/UNCTAD TRAINS SDMX (TRN). `partner=000` (World),
  `datatype=reported` (fallback `aveestimated`). HS6 codes follow the
  user-supplied set ({hs_list}).
- **HS revision handling**: HS codes 854142, 854143 and 870380 only
  exist from HS 2017 onward. For years < 2017 the tariff index for
  solar_pv falls back to HS 854140 (parent) and for evs to HS 870390
  alone. The `hs_codes_used` column records which HS6s were averaged
  into each cell.

## Column dictionaries

### renewable_deployment_panel.csv
`country,iso3,year,tech,capacity_gw,source,notes`

### export_tariff_index_panel.csv (exporter-view)
`country,iso3,year,tech,tariff_faced_simple_mean,n_destinations,hs_codes_used,weighting,source,notes`

### export_tariff_index_panel_destinations.csv (destination panel)
`reporter_country,reporter_iso3,year,tech,hs_codes_used,tariff_mfn_simple_avg,n_hs_lines_underlying,nomen_code,datatype,source`
"""


# ---- CSV / JSON writers ----------------------------------------------------

def write_csv(rows: list[dict], path: Path, columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})


# ---- Main ------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-irena", action="store_true", help="Skip renewable panel.")
    ap.add_argument("--no-wits", action="store_true", help="Skip tariff panel.")
    args = ap.parse_args()

    irena_path = CACHE_DIR / "irena_capacity.json"
    wits_path = CACHE_DIR / "wits_tariffs.json"

    ren_rows: list[dict] = []
    dest_tariff_rows: list[dict] = []
    exporter_tariff_rows: list[dict] = []

    if not args.no_irena:
        if not irena_path.exists():
            raise SystemExit(f"missing {irena_path}; run fetch_irena.py first")
        irena_rows = read_json(irena_path)
        ren_rows = build_renewable_panel(irena_rows)
        write_csv(ren_rows, OUTPUT_DIR / "renewable_deployment_panel.csv", REN_COLUMNS)
        write_json(OUTPUT_DIR / "renewable_deployment_panel.json", ren_rows)
        print(f"[panel] renewable_deployment_panel: {len(ren_rows)} rows")

    if not args.no_wits:
        if not wits_path.exists():
            raise SystemExit(f"missing {wits_path}; run fetch_wits_tariffs.py first")
        wits_rows = read_json(wits_path)
        dest_tariff_rows = build_destination_tariff_panel(wits_rows)
        exporter_tariff_rows = build_exporter_tariff_index(dest_tariff_rows)
        write_csv(dest_tariff_rows,
                  OUTPUT_DIR / "export_tariff_index_panel_destinations.csv",
                  TARIFF_COLUMNS_DEST)
        write_json(OUTPUT_DIR / "export_tariff_index_panel_destinations.json", dest_tariff_rows)
        write_csv(exporter_tariff_rows,
                  OUTPUT_DIR / "export_tariff_index_panel.csv",
                  TARIFF_COLUMNS_EXPORTER)
        write_json(OUTPUT_DIR / "export_tariff_index_panel.json", exporter_tariff_rows)
        print(f"[panel] export_tariff_index_panel_destinations: {len(dest_tariff_rows)} rows")
        print(f"[panel] export_tariff_index_panel (exporter view): {len(exporter_tariff_rows)} rows")

    (OUTPUT_DIR / "coverage.md").write_text(coverage_report(ren_rows, dest_tariff_rows))
    (OUTPUT_DIR / "methodology_summary.md").write_text(methodology_summary())
    print(f"[panel] outputs -> {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
