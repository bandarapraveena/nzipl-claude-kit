"""Build the pull-factor panels from cached WDI, ILO, JLOP, Eurostat, and IRENA.

Outputs (all in outputs/):
    market_size_panel.{csv,json}          country x year  (one row per cy)
        gdp_usd_current, gdp_usd_constant_2015, gdp_pc_usd_current,
        gdp_pc_ppp_const2021, population, manuf_va_pct_gdp,
        manuf_va_usd_current

    labor_cost_panel.{csv,json}           country x year
        lac_mfg_local_ccy     ILO hourly labour cost (manufacturing, local)
        gdp_per_worker_ppd    WDI SL.GDP.PCAP.EM.KD (global productivity proxy)

    energy_cost_panel.{csv,json}          country x year  (EU/UK only)
        elec_price_ind_eur_per_kwh

    gip_panel.{csv,json}                  country x year x tech
        n_ip_measures_announced    from JLOP_2025 D_IP_bert_3 filter

    recap_panel.{csv,json}                country x year x tech
        capacity_gw                 reuse of IRENA push-factors cache

    pull_factors_master.csv/json          merged country x year (tech-specific
                                          GIP and ReCap encoded as columns
                                          n_ip_{tech}, recap_{tech}_gw)

    coverage.md                           fill-rate table by variable x period
    methodology_summary.md                variable dictionary

stdlib-only.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from sources._common import (
    CACHE_DIR,
    COUNTRIES,
    ISO3S,
    NAME_BY_ISO3,
    YEAR_END,
    YEAR_START,
    load_irena_capacity,
    read_json,
    write_json,
    years,
)

OUTPUTS = Path(__file__).resolve().parent / "outputs"
TECHS = ("solar_pv", "wind", "batteries", "evs")


# ---- Loaders ---------------------------------------------------------------

def _load_wdi() -> dict[tuple[str, int], dict[str, float]]:
    """Returns {(iso3, year): {code: value}} across all WDI indicator caches."""
    out: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    wdi_dir = CACHE_DIR / "wdi"
    if not wdi_dir.exists():
        return out
    for f in sorted(wdi_dir.glob("*.json")):
        code = f.stem
        rows = read_json(f)
        for r in rows:
            iso3 = r.get("countryiso3code") or r.get("country", {}).get("id")
            year_raw = r.get("date")
            val = r.get("value")
            if not iso3 or iso3 not in NAME_BY_ISO3 or year_raw is None or val is None:
                continue
            try:
                year = int(year_raw)
            except (ValueError, TypeError):
                continue
            out[(iso3, year)][code] = float(val)
    return out


def _load_ilo() -> dict[tuple[str, int], float]:
    """Aggregate LAC_XEES_ECO_NB_A for ISIC4 Section C (manufacturing).

    Some reporters have multiple observations per country-year (different
    source identifiers). Take the mean.
    """
    out: dict[tuple[str, int], list[float]] = defaultdict(list)
    f = CACHE_DIR / "ilo" / "LAC_XEES_ECO_NB_A.json"
    if not f.exists():
        return {}
    for r in read_json(f):
        if r.get("classif1") != "ECO_ISIC4_C":
            continue
        iso3 = r["iso3"]
        if iso3 not in NAME_BY_ISO3:
            continue
        out[(iso3, r["year"])].append(r["value"])
    return {k: sum(v) / len(v) for k, v in out.items()}


def _load_eurostat_energy() -> dict[tuple[str, int], float]:
    f = CACHE_DIR / "eurostat" / "energy_price_industrial_annual.json"
    if not f.exists():
        return {}
    return {(r["iso3"], r["year"]): r["price_eur_per_kwh"] for r in read_json(f)}


def _load_gip() -> dict[tuple[str, int, str], int]:
    """Count JLOP green-LCT measures per (iso3, year, tech). A measure that
    covers multiple techs contributes 1 to each tech it covers — already
    encoded in the fetched rows' `techs` list.
    """
    out: dict[tuple[str, int, str], int] = defaultdict(int)
    f = CACHE_DIR / "gip" / "JLOP_green_measures.json"
    if not f.exists():
        return out
    for r in read_json(f):
        iso3 = r["iso3"]
        if iso3 not in NAME_BY_ISO3:
            continue
        for tech in r["techs"]:
            out[(iso3, r["year"], tech)] += 1
    return out


def _load_recap() -> dict[tuple[str, int, str], float]:
    """Reuse push-factors IRENA capacity panel. 'wind' combines onshore+offshore."""
    raw = load_irena_capacity()
    if raw is None:
        return {}
    # The push-factors cache shape: list of {iso3, year, tech, capacity_gw, ...}.
    out: dict[tuple[str, int, str], float] = defaultdict(float)
    wind_components = {"onshore_wind", "offshore_wind"}
    for r in raw:
        iso3 = r.get("iso3")
        if iso3 not in NAME_BY_ISO3:
            continue
        year = r.get("year")
        tech = r.get("tech")
        cap = r.get("capacity_gw")
        if year is None or tech is None or cap is None:
            continue
        if tech == "solar_pv":
            out[(iso3, year, "solar_pv")] += cap
        elif tech in wind_components:
            out[(iso3, year, "wind")] += cap
        elif tech == "wind":
            # If push-factors already emitted a combined 'wind' row, skip
            # to avoid double counting — we sum components ourselves.
            pass
    return out


# ---- Panel builders --------------------------------------------------------

def build_market_size(wdi: dict) -> list[dict]:
    rows: list[dict] = []
    for iso3 in ISO3S:
        for year in years():
            vals = wdi.get((iso3, year), {})
            rows.append({
                "iso3": iso3,
                "country": NAME_BY_ISO3[iso3],
                "year": year,
                "gdp_usd_current":        vals.get("NY.GDP.MKTP.CD"),
                "gdp_usd_constant_2015":  vals.get("NY.GDP.MKTP.KD"),
                "gdp_pc_usd_current":     vals.get("NY.GDP.PCAP.CD"),
                "gdp_pc_ppp_const2021":   vals.get("NY.GDP.PCAP.PP.KD"),
                "population":             vals.get("SP.POP.TOTL"),
                "manuf_va_pct_gdp":       vals.get("NV.IND.MANF.ZS"),
                "manuf_va_usd_current":   vals.get("NV.IND.MANF.CD"),
            })
    return rows


def build_labor_cost(wdi: dict, ilo: dict) -> list[dict]:
    rows: list[dict] = []
    for iso3 in ISO3S:
        for year in years():
            rows.append({
                "iso3": iso3,
                "country": NAME_BY_ISO3[iso3],
                "year": year,
                "lac_mfg_local_ccy":   ilo.get((iso3, year)),
                "gdp_per_worker_ppd":  wdi.get((iso3, year), {}).get("SL.GDP.PCAP.EM.KD"),
            })
    return rows


def build_energy_cost(euro: dict) -> list[dict]:
    rows: list[dict] = []
    for iso3 in ISO3S:
        for year in years():
            rows.append({
                "iso3": iso3,
                "country": NAME_BY_ISO3[iso3],
                "year": year,
                "elec_price_ind_eur_per_kwh": euro.get((iso3, year)),
            })
    return rows


def build_gip(gip: dict) -> list[dict]:
    rows: list[dict] = []
    for iso3 in ISO3S:
        for year in years():
            for tech in TECHS:
                rows.append({
                    "iso3": iso3,
                    "country": NAME_BY_ISO3[iso3],
                    "year": year,
                    "tech": tech,
                    "n_ip_measures_announced": gip.get((iso3, year, tech), 0),
                })
    return rows


def build_recap(recap: dict) -> list[dict]:
    rows: list[dict] = []
    # Only techs that IRENA reports: solar_pv and wind.
    irena_techs = ("solar_pv", "wind")
    for iso3 in ISO3S:
        for year in years():
            for tech in irena_techs:
                rows.append({
                    "iso3": iso3,
                    "country": NAME_BY_ISO3[iso3],
                    "year": year,
                    "tech": tech,
                    "capacity_gw": recap.get((iso3, year, tech)),
                })
    return rows


def build_master(market: list[dict], labor: list[dict], energy: list[dict],
                 gip_map: dict, recap_map: dict) -> list[dict]:
    """Country-year master table. Tech-specific GIP and ReCap get flattened
    into per-tech columns: n_ip_{tech}, recap_{tech}_gw.
    """
    by_cy: dict[tuple[str, int], dict] = {}
    for r in market:
        by_cy[(r["iso3"], r["year"])] = dict(r)
    for r in labor:
        by_cy[(r["iso3"], r["year"])].update({
            "lac_mfg_local_ccy": r["lac_mfg_local_ccy"],
            "gdp_per_worker_ppd": r["gdp_per_worker_ppd"],
        })
    for r in energy:
        by_cy[(r["iso3"], r["year"])]["elec_price_ind_eur_per_kwh"] = r["elec_price_ind_eur_per_kwh"]

    # Flatten tech-specific vars.
    for (iso3, year), row in by_cy.items():
        for tech in TECHS:
            row[f"n_ip_{tech}"] = gip_map.get((iso3, year, tech), 0)
        for tech in ("solar_pv", "wind"):
            row[f"recap_{tech}_gw"] = recap_map.get((iso3, year, tech))

    # Sort by country, year for deterministic output.
    return [by_cy[k] for k in sorted(by_cy)]


# ---- Writers ---------------------------------------------------------------

def write_panel(rows: list[dict], stem: str) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUTS / f"{stem}.json", rows)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with (OUTPUTS / f"{stem}.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def write_coverage(panels: dict[str, list[dict]], master: list[dict]) -> None:
    buckets = [(2003, 2007), (2008, 2012), (2013, 2017), (2018, 2022), (2023, 2025)]

    def fill(rows: list[dict], field: str, bucket: tuple[int, int]) -> tuple[int, int]:
        lo, hi = bucket
        total = 0
        got = 0
        for r in rows:
            if not (lo <= r["year"] <= hi):
                continue
            total += 1
            if r.get(field) not in (None, "", 0) or (
                field == "n_ip_measures_announced" and r.get(field) not in (None, "")
            ):
                got += 1
        return got, total

    lines = ["# Coverage report (pull-factors)", ""]

    # Market size: one row per country-year. Use gdp_usd_current as proxy.
    lines += ["## MarketSize (WDI)  — gdp_usd_current fill rate", ""]
    lines += ["| bucket | fill |", "|---|---|"]
    for b in buckets:
        g, t = fill(panels["market_size"], "gdp_usd_current", b)
        lines.append(f"| {b[0]}-{b[1]} | {g}/{t} ({100*g//max(t,1)}%) |")
    lines.append("")

    # LaborCost: two separate coverage columns.
    lines += ["## LaborCost (ILO ECO_ISIC4_C + WDI proxy)", "",
              "| bucket | lac_mfg_local | gdp_per_worker |",
              "|---|---|---|"]
    for b in buckets:
        g1, t1 = fill(panels["labor_cost"], "lac_mfg_local_ccy", b)
        g2, t2 = fill(panels["labor_cost"], "gdp_per_worker_ppd", b)
        lines.append(f"| {b[0]}-{b[1]} | {g1}/{t1} ({100*g1//max(t1,1)}%) | {g2}/{t2} ({100*g2//max(t2,1)}%) |")
    lines.append("")

    # EnergyCost: EU-only
    lines += ["## EnergyCost (Eurostat nrg_pc_205)  — elec_price_ind_eur_per_kwh fill rate", ""]
    lines += ["| bucket | fill |", "|---|---|"]
    for b in buckets:
        g, t = fill(panels["energy_cost"], "elec_price_ind_eur_per_kwh", b)
        lines.append(f"| {b[0]}-{b[1]} | {g}/{t} ({100*g//max(t,1)}%) |")
    lines += ["",
              "(Eurostat covers ~15 countries in our 40-country set: EU27 members + UK + NO + TR)",
              ""]

    # GIP: tech-level
    lines += ["## GIP (JLOP 2025 green-LCT industrial policy count)  — n measures",
              "",
              "| Tech | 2003-2007 | 2008-2012 | 2013-2017 | 2018-2022 | 2023-2025 |",
              "|---|---|---|---|---|---|"]
    gip_by_tech_bucket: dict[str, list[int]] = {t: [0] * len(buckets) for t in TECHS}
    for r in panels["gip"]:
        yr = r["year"]
        tech = r["tech"]
        for i, b in enumerate(buckets):
            if b[0] <= yr <= b[1]:
                gip_by_tech_bucket[tech][i] += r["n_ip_measures_announced"]
                break
    for tech in TECHS:
        counts = gip_by_tech_bucket[tech]
        lines.append(f"| {tech} | " + " | ".join(str(c) for c in counts) + " |")
    lines.append("")

    # ReCap: from IRENA push-factors cache
    lines += ["## ReCap (IRENA capacity_gw fill rate, reused from push-factors)",
              "",
              "| Tech | 2003-2007 | 2008-2012 | 2013-2017 | 2018-2022 | 2023-2025 |",
              "|---|---|---|---|---|---|"]
    recap_by_tech_bucket: dict[str, list[tuple[int, int]]] = {t: [(0, 0)] * len(buckets) for t in ("solar_pv", "wind")}
    for r in panels["recap"]:
        yr = r["year"]
        tech = r["tech"]
        for i, b in enumerate(buckets):
            if b[0] <= yr <= b[1]:
                g, t = recap_by_tech_bucket[tech][i]
                recap_by_tech_bucket[tech][i] = (g + (1 if r["capacity_gw"] is not None else 0), t + 1)
                break
    for tech in ("solar_pv", "wind"):
        parts = []
        for g, t in recap_by_tech_bucket[tech]:
            pct = 100 * g // max(t, 1)
            parts.append(f"{g}/{t} ({pct}%)")
        lines.append(f"| {tech} | " + " | ".join(parts) + " |")
    lines += ["",
              "Denominators = 40 countries × years in bucket (for MarketSize/LaborCost/EnergyCost/ReCap).",
              "GIP numerator = raw measure count, not fill rate — 0 is a valid observation (no policy announced).",
              ""]

    (OUTPUTS / "coverage.md").write_text("\n".join(lines))


def write_methodology() -> None:
    text = """# Methodology — pull-factor panel

## Panel keys

Country (ISO3) × Year. Tech-specific vars (GIP, ReCap) are pivoted into
per-tech columns on the master panel:
    n_ip_{solar_pv,wind,batteries,evs}        — JLOP 2025 green IP measure counts
    recap_{solar_pv,wind}_gw                  — IRENA installed capacity

Destination-country scope: 40 economies that are jointly the main recipients
of LCT FDI and the main home-country exporters (shared with push-factors).

## Variable definitions

### MarketSize  (WDI)

| Column | WDI code | Definition |
|---|---|---|
| gdp_usd_current       | NY.GDP.MKTP.CD     | GDP, current US$ |
| gdp_usd_constant_2015 | NY.GDP.MKTP.KD     | GDP, constant 2015 US$ |
| gdp_pc_usd_current    | NY.GDP.PCAP.CD     | GDP per capita, current US$ |
| gdp_pc_ppp_const2021  | NY.GDP.PCAP.PP.KD  | GDP per capita, PPP (constant 2021 intl$) |
| population            | SP.POP.TOTL        | Population, total |
| manuf_va_pct_gdp      | NV.IND.MANF.ZS     | Manufacturing value-added (% GDP) |
| manuf_va_usd_current  | NV.IND.MANF.CD     | Manufacturing value-added (US$) |

The paper's Equation 6 specification uses log(GDP) as MarketSize.
gdp_usd_current is the natural baseline; gdp_usd_constant_2015 is the
deflated alternative to absorb global price level drift.

### ReCap  (IRENA IRENASTAT)

Installed renewable generating capacity in GW, by tech:
    recap_solar_pv_gw    IRENA tech code 2 (Solar PV), OnGrid + OffGrid
    recap_wind_gw        Onshore (code 5) + Offshore (code 6)

Reused directly from `../push-factors/data/cache/irena_capacity.json` — no
new API calls.

### GIP  (Juhasz, Lashkaripour, Oehlmair, Protzer 2025)

Annual count of green-LCT industrial policy measures announced by each
country, filtered from JLOP_2025.xlsx to:
    1. D_IP_bert_3 == 1                    (BERT-classified as industrial policy)
    2. MeasureAffectedProducts ∩ {854142, 854143, 850231, 850760, 850780,
                                   870380, 870390, 854140} ≠ ∅
    3. 2003 ≤ AnnouncedYear ≤ 2025

A measure that affects multiple techs (e.g. 850760 AND 870380) is counted
once per hit tech. Supranational measures (EU, Eurasian EU, GCC) are
dropped — they would otherwise overcount member-state GIP. Multi-country
measures expressed as "A & B & C" are attributed to each constituent
country.

### LaborCost  (ILO + WDI)

| Column | Source | Coverage notes |
|---|---|---|
| lac_mfg_local_ccy    | ILO LAC_XEES_ECO_NB_A, ISIC Rev.4 Section C | OECD-heavy; missing CN/IN/JP/KR/VN/ID/PH/etc. |
| gdp_per_worker_ppd   | WDI SL.GDP.PCAP.EM.KD (const 2021 PPP $)    | Global coverage; proxy for wage level |

The ILO series is in local currency — use as a within-country time trend
or ratio. For cross-country comparison, fall back to gdp_per_worker_ppd
which is PPP-adjusted and globally available. See README for upgrade path
to UNIDO INDSTAT (paywalled) for proper manufacturing-specific wage series.

### EnergyCost  (Eurostat nrg_pc_205)

Industrial electricity price, EUR/kWh, excluding taxes, consumption band
MWH2000-19999 (medium-large industrial). Bi-annual observations (2007-S1
onwards) averaged within year.

Coverage: EU27 + UK + NO + TR (≈15 countries in our set). **No coverage
for US, CN, IN, JP, KR, and non-EU LMIC markets.** EnergyCost is null for
those countries — document in paper's Table 4 footnote. Free global
alternatives are narrow (IEA Electricity Information is paywalled; national
regulators publish individual country series). See README "Upgrading" section.

## Years
2003–2025 (inclusive). Eurostat energy begins 2007; JLOP covers full window.

## Output reproducibility
All JSON caches under `data/cache/` are idempotent: `python build_panel.py`
on an existing cache regenerates the outputs without network.
"""
    (OUTPUTS / "methodology_summary.md").write_text(text)


# ---- Main ------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()

    print("[build] loading caches")
    wdi = _load_wdi()
    ilo = _load_ilo()
    euro = _load_eurostat_energy()
    gip = _load_gip()
    recap = _load_recap()
    print(f"  wdi cells: {len(wdi)}, ilo: {len(ilo)}, eurostat: {len(euro)}, "
          f"gip: {len(gip)}, recap: {len(recap)}")

    market = build_market_size(wdi)
    labor = build_labor_cost(wdi, ilo)
    energy = build_energy_cost(euro)
    gip_panel = build_gip(gip)
    recap_panel = build_recap(recap)
    master = build_master(market, labor, energy, gip, recap)

    panels = {
        "market_size": market,
        "labor_cost": labor,
        "energy_cost": energy,
        "gip": gip_panel,
        "recap": recap_panel,
    }
    for name, rows in panels.items():
        write_panel(rows, f"{name}_panel")
        print(f"  wrote {name}_panel.{{csv,json}}  ({len(rows)} rows)")
    write_panel(master, "pull_factors_master")
    print(f"  wrote pull_factors_master.{{csv,json}}  ({len(master)} rows)")

    write_coverage(panels, master)
    write_methodology()
    print("[build] coverage.md and methodology_summary.md written.")


if __name__ == "__main__":
    main()
