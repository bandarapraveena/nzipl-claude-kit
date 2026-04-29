#!/usr/bin/env python3
"""Validate NZIPL EV greenfield / FDI records against schema, status x tier, and forbidden-domain rules.

Run before every write to nzipl_ev_greenfield_global.json. Exits non-zero on any violation.

Usage:
    python3 validate_ev_record.py path/to/record_or_global.json

Accepts a single record object or a JSON array of records.
"""

import json
import re
import sys
from urllib.parse import urlparse

REGIONS = {
    "North America", "Central America", "South America", "Europe", "MENA",
    "Sub-Saharan Africa", "East Asia", "SE Asia", "South Asia", "Oceania",
}
PROJECT_TYPES = {
    "cell", "pack", "cathode", "anode", "separator", "electrolyte",
    "recycling", "vehicle_assembly", "motor", "inverter", "charger",
}
STATUSES = {
    "Operating", "Under Construction", "Planned", "Announced",
    "Paused", "Cancelled", "Closed", "Rumored",
}
SECTORS = {"Batteries", "EVs", "Charging"}
PRODUCTION_UNITS = {
    "vehicles/year", "GWh/year", "packs/year", "tonnes/year", "chargers/year",
}

FORBIDDEN_DOMAINS = {
    "wikipedia.org", "en.wikipedia.org", "de.wikipedia.org", "es.wikipedia.org",
    "fr.wikipedia.org", "it.wikipedia.org", "pt.wikipedia.org", "ja.wikipedia.org",
    "zh.wikipedia.org", "ko.wikipedia.org",
    "grokipedia.com",
    "linkedin.com", "www.linkedin.com",
    "reddit.com", "www.reddit.com",
    "twitter.com", "x.com",
    "facebook.com", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "medium.com",
}

STATUS_TIER_REQUIRED = {
    "Operating": {1},
    "Under Construction": {1},
    "Closed": {1},
    "Rumored": {3},
}

REQUIRED_FIELDS = [
    "id", "name", "company", "origin", "country", "city",
    "lat", "lng", "sector", "projectType", "status", "announced",
    "investmentM", "verificationTier", "verifiedBy", "verifiedDate", "sources",
]

ID_RE = re.compile(r"^EV-[A-Z]{3}-\d{4}$")
ISO3_RE = re.compile(r"^[A-Z]{3}$")
DATE_RE = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?$")

IRA_DATE = "2022-08-16"

TIER_MIN_SOURCES = {1: 3, 2: 2, 3: 1}
RECEIPT_KEYS = {"bnef_origin"}

# ISO-3 → region lookup. Covers all countries with EV greenfield activity.
ISO3_TO_REGION = {
    # North America
    "USA": "North America", "CAN": "North America", "MEX": "North America",
    # Central America
    "GTM": "Central America", "CRI": "Central America", "PAN": "Central America",
    "SLV": "Central America", "HND": "Central America", "NIC": "Central America",
    "BLZ": "Central America",
    # South America
    "BRA": "South America", "ARG": "South America", "CHL": "South America",
    "COL": "South America", "PER": "South America", "VEN": "South America",
    "URY": "South America", "PRY": "South America", "BOL": "South America",
    "ECU": "South America", "GUY": "South America", "SUR": "South America",
    # Europe
    "DEU": "Europe", "FRA": "Europe", "GBR": "Europe", "ESP": "Europe",
    "ITA": "Europe", "POL": "Europe", "NLD": "Europe", "BEL": "Europe",
    "AUT": "Europe", "CHE": "Europe", "SWE": "Europe", "NOR": "Europe",
    "FIN": "Europe", "DNK": "Europe", "IRL": "Europe", "PRT": "Europe",
    "GRC": "Europe", "CZE": "Europe", "SVK": "Europe", "HUN": "Europe",
    "ROU": "Europe", "BGR": "Europe", "HRV": "Europe", "SVN": "Europe",
    "LTU": "Europe", "LVA": "Europe", "EST": "Europe", "LUX": "Europe",
    "ISL": "Europe", "SRB": "Europe", "BIH": "Europe", "MKD": "Europe",
    "ALB": "Europe", "MNE": "Europe", "UKR": "Europe", "BLR": "Europe",
    "MDA": "Europe",
    # MENA
    "TUR": "MENA", "ISR": "MENA", "SAU": "MENA", "ARE": "MENA",
    "EGY": "MENA", "MAR": "MENA", "DZA": "MENA", "TUN": "MENA",
    "IRN": "MENA", "IRQ": "MENA", "JOR": "MENA", "LBN": "MENA",
    "QAT": "MENA", "KWT": "MENA", "OMN": "MENA", "BHR": "MENA",
    "YEM": "MENA", "LBY": "MENA",
    # Sub-Saharan Africa
    "ZAF": "Sub-Saharan Africa", "NGA": "Sub-Saharan Africa",
    "KEN": "Sub-Saharan Africa", "ETH": "Sub-Saharan Africa",
    "GHA": "Sub-Saharan Africa", "CIV": "Sub-Saharan Africa",
    "SEN": "Sub-Saharan Africa", "TZA": "Sub-Saharan Africa",
    "UGA": "Sub-Saharan Africa", "ZMB": "Sub-Saharan Africa",
    "ZWE": "Sub-Saharan Africa", "BWA": "Sub-Saharan Africa",
    "NAM": "Sub-Saharan Africa", "AGO": "Sub-Saharan Africa",
    "MOZ": "Sub-Saharan Africa", "COD": "Sub-Saharan Africa",
    "CMR": "Sub-Saharan Africa", "RWA": "Sub-Saharan Africa",
    "MDG": "Sub-Saharan Africa", "MUS": "Sub-Saharan Africa",
    # East Asia
    "CHN": "East Asia", "JPN": "East Asia", "KOR": "East Asia",
    "TWN": "East Asia", "HKG": "East Asia", "MNG": "East Asia",
    "PRK": "East Asia",
    # SE Asia
    "THA": "SE Asia", "VNM": "SE Asia", "IDN": "SE Asia",
    "MYS": "SE Asia", "SGP": "SE Asia", "PHL": "SE Asia",
    "MMR": "SE Asia", "KHM": "SE Asia", "LAO": "SE Asia",
    "BRN": "SE Asia", "TLS": "SE Asia",
    # South Asia
    "IND": "South Asia", "PAK": "South Asia", "BGD": "South Asia",
    "LKA": "South Asia", "NPL": "South Asia", "BTN": "South Asia",
    "MDV": "South Asia", "AFG": "South Asia",
    # Oceania
    "AUS": "Oceania", "NZL": "Oceania", "FJI": "Oceania",
    "PNG": "Oceania",
}


def domain_of(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def check_record(r: dict) -> list[str]:
    errs: list[str] = []
    rid = r.get("id", "<no-id>")

    # Required fields
    for f in REQUIRED_FIELDS:
        if f not in r or r[f] in ("", None):
            errs.append(f"{rid}: missing required field '{f}'")

    # ID
    if not ID_RE.match(r.get("id", "")):
        errs.append(f"{rid}: id does not match EV-<ISO3>-<NNNN>")

    # Enums
    if r.get("projectType") not in PROJECT_TYPES:
        errs.append(f"{rid}: projectType '{r.get('projectType')}' not in enum")
    if r.get("status") not in STATUSES:
        errs.append(f"{rid}: status '{r.get('status')}' not in enum")
    if r.get("sector") not in SECTORS:
        errs.append(f"{rid}: sector '{r.get('sector')}' not in enum")

    # ISO-3
    country = r.get("country", "")
    origin = r.get("origin", "")
    for f, v in (("country", country), ("origin", origin)):
        if v and not ISO3_RE.match(v):
            errs.append(f"{rid}: {f} '{v}' is not ISO-3")

    # id prefix must match country
    if ID_RE.match(r.get("id", "")) and country:
        id_iso = r["id"].split("-")[1]
        if id_iso != country:
            errs.append(f"{rid}: id prefix '{id_iso}' does not match country '{country}'")

    # Auto-derived: region
    if country:
        expected_region = ISO3_TO_REGION.get(country)
        if expected_region is None:
            errs.append(f"{rid}: country '{country}' not mapped to a region (add to ISO3_TO_REGION)")
        elif "region" in r and r["region"] != expected_region:
            errs.append(f"{rid}: region='{r['region']}' but country '{country}' implies '{expected_region}'")

    # Auto-derived: isFDI
    if country and origin:
        expected_isFDI = (origin != country)
        if "isFDI" in r and r["isFDI"] != expected_isFDI:
            errs.append(f"{rid}: isFDI={r['isFDI']} but origin='{origin}' country='{country}' implies {expected_isFDI}")

    # Coordinates
    for f in ("lat", "lng"):
        v = r.get(f)
        if not isinstance(v, (int, float)):
            errs.append(f"{rid}: {f} must be a number")

    # Investment
    if not isinstance(r.get("investmentM"), (int, float)):
        errs.append(f"{rid}: investmentM must be a number")

    # Announced date
    ann = r.get("announced", "")
    if not DATE_RE.match(ann):
        errs.append(f"{rid}: announced '{ann}' is not YYYY / YYYY-MM / YYYY-MM-DD")

    # Auto-derived: postIRA
    if isinstance(ann, str) and len(ann) >= 4:
        expected_postIRA = ann >= IRA_DATE
        if "postIRA" in r and r["postIRA"] != expected_postIRA:
            errs.append(f"{rid}: postIRA={r['postIRA']} but announced='{ann}' implies {expected_postIRA}")

    # productionUnits required when production set
    if (r.get("targetProduction") is not None or r.get("realizedProduction") is not None):
        if not r.get("productionUnits"):
            errs.append(f"{rid}: productionUnits required when targetProduction/realizedProduction set")
        elif r["productionUnits"] not in PRODUCTION_UNITS:
            errs.append(f"{rid}: productionUnits '{r['productionUnits']}' not in enum")

    # Tier
    tier = r.get("verificationTier")
    if tier not in (1, 2, 3):
        errs.append(f"{rid}: verificationTier must be 1, 2, or 3")

    # Status x tier
    status = r.get("status")
    if status in STATUS_TIER_REQUIRED and tier not in STATUS_TIER_REQUIRED[status]:
        allowed = "/".join(str(t) for t in sorted(STATUS_TIER_REQUIRED[status]))
        errs.append(f"{rid}: status '{status}' requires Tier {allowed}, has Tier {tier}")

    # Sources
    sources = r.get("sources") or {}
    if not isinstance(sources, dict):
        errs.append(f"{rid}: sources must be an object")
        sources = {}

    for key, url in sources.items():
        if key in RECEIPT_KEYS:
            continue
        if not isinstance(url, str):
            continue
        if not url.startswith(("http://", "https://")):
            errs.append(f"{rid}: sources.{key} must be an http(s) URL (got '{url[:60]}')")
            continue
        d = domain_of(url)
        if d in FORBIDDEN_DOMAINS:
            errs.append(f"{rid}: sources.{key} uses forbidden domain '{d}' ({url})")

    # fdi_origin deprecated
    if "fdi_origin" in sources:
        errs.append(f"{rid}: sources.fdi_origin is deprecated — remove")

    # investmentM_history forbidden-domain check
    for entry in r.get("investmentM_history") or []:
        src = entry.get("source") if isinstance(entry, dict) else None
        if isinstance(src, str) and src.startswith(("http://", "https://")):
            d = domain_of(src)
            if d in FORBIDDEN_DOMAINS:
                errs.append(f"{rid}: investmentM_history source uses forbidden domain '{d}' ({src})")

    # Tier minimum citations
    if tier in TIER_MIN_SOURCES:
        citation_urls = [
            v for k, v in sources.items()
            if k not in RECEIPT_KEYS
            and isinstance(v, str)
            and v.startswith(("http://", "https://"))
        ]
        distinct = len(set(citation_urls))
        need = TIER_MIN_SOURCES[tier]
        if distinct < need:
            errs.append(f"{rid}: Tier {tier} requires ≥{need} distinct citation URLs, has {distinct}")

    # verifiedDate
    vd = r.get("verifiedDate", "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", vd):
        errs.append(f"{rid}: verifiedDate '{vd}' must be YYYY-MM-DD")

    return errs


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_ev_record.py <path/to/record_or_global.json>", file=sys.stderr)
        return 2

    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)

    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        print(f"error: {path} must be a record object or array of records", file=sys.stderr)
        return 2

    all_errs: list[str] = []
    for r in records:
        all_errs.extend(check_record(r))

    if all_errs:
        print(f"FAIL: {len(all_errs)} violation(s) across {len(records)} record(s)")
        for e in all_errs:
            print(f"  - {e}")
        return 1

    print(f"OK: {len(records)} record(s) clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
