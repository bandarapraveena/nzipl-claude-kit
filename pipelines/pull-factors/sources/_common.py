"""Shared helpers for the pull-factors pipeline.

stdlib-only. Reuses the 40-country set from the push-factors pipeline — these
are simultaneously exporter home countries (push factors) and destination
markets where LCT FDI can land (pull factors).

Pull-factor variables in paper's Equation 6 (Table 4), excluding IndusBase:
    MarketSize   — GDP, GDP per capita, population (WDI)
    ReCap        — renewable generation capacity (IRENA; reused from push-factors)
    GIP          — green industrial policy count (Juhasz et al. 2025 JLOP dataset)
    LaborCost    — manufacturing labour cost / GDP per employed person (ILO + WDI)
    EnergyCost   — industrial electricity price (Eurostat EU; IEA fallback)
"""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

PIPELINE_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PIPELINE_ROOT / "data"
CACHE_DIR = DATA_ROOT / "cache"

# Matches pipelines/push-factors/sources/_common.COUNTRIES.
# ISO2 column added for Eurostat queries (uses ISO 3166-1 alpha-2, with "EL"=GR, "UK"=GB).
COUNTRIES: list[tuple[str, str, str, str]] = [
    ("China",              "CHN", "156", "CN"),
    ("United States",      "USA", "840", "US"),
    ("Germany",            "DEU", "276", "DE"),
    ("Japan",              "JPN", "392", "JP"),
    ("South Korea",        "KOR", "410", "KR"),
    ("India",              "IND", "356", "IN"),
    ("Australia",          "AUS", "036", "AU"),
    ("United Kingdom",     "GBR", "826", "UK"),
    ("France",             "FRA", "250", "FR"),
    ("Spain",              "ESP", "724", "ES"),
    ("Italy",              "ITA", "380", "IT"),
    ("Netherlands",        "NLD", "528", "NL"),
    ("Belgium",            "BEL", "056", "BE"),
    ("Sweden",             "SWE", "752", "SE"),
    ("Switzerland",        "CHE", "756", "CH"),
    ("Portugal",           "PRT", "620", "PT"),
    ("Poland",             "POL", "616", "PL"),
    ("Czech Republic",     "CZE", "203", "CZ"),
    ("Romania",            "ROU", "642", "RO"),
    ("Turkey",             "TUR", "792", "TR"),
    ("Canada",             "CAN", "124", "CA"),
    ("Mexico",             "MEX", "484", "MX"),
    ("Brazil",             "BRA", "076", "BR"),
    ("Chile",              "CHL", "152", "CL"),
    ("Argentina",          "ARG", "032", "AR"),
    ("South Africa",       "ZAF", "710", "ZA"),
    ("Morocco",            "MAR", "504", "MA"),
    ("Egypt",              "EGY", "818", "EG"),
    ("Saudi Arabia",       "SAU", "682", "SA"),
    ("United Arab Emirates","ARE","784", "AE"),
    ("Singapore",          "SGP", "702", "SG"),
    ("Malaysia",           "MYS", "458", "MY"),
    ("Thailand",           "THA", "764", "TH"),
    ("Vietnam",            "VNM", "704", "VN"),
    ("Indonesia",          "IDN", "360", "ID"),
    ("Philippines",        "PHL", "608", "PH"),
    ("Taiwan",             "TWN", "490", "TW"),
    ("Hong Kong",          "HKG", "344", "HK"),
    ("Norway",             "NOR", "578", "NO"),
    ("Denmark",            "DNK", "208", "DK"),
]

NAME_BY_ISO3 = {iso3: name for name, iso3, _, _ in COUNTRIES}
ISO3S = [iso3 for _, iso3, _, _ in COUNTRIES]
ISO2_BY_ISO3 = {iso3: iso2 for _, iso3, _, iso2 in COUNTRIES}
ISO3_BY_ISO2 = {iso2: iso3 for _, iso3, _, iso2 in COUNTRIES}

# Year window (matches push-factors).
YEAR_START = 2003
YEAR_END = 2025


def years() -> range:
    return range(YEAR_START, YEAR_END + 1)


def iter_country_years() -> Iterable[tuple[str, str, int]]:
    for name, iso3, _, _ in COUNTRIES:
        for y in years():
            yield name, iso3, y


# ---- HTTP helpers (shared pattern with push-factors) ------------------------

UA = "Mozilla/5.0 (NZIPL pull-factors pipeline; contact: netzeropolicylab.com)"


def _ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def http_get_json(url: str, *, timeout: int = 120) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, context=_ssl_context(), timeout=timeout) as r:
        return json.loads(r.read())


def http_get_bytes(url: str, *, timeout: int = 180) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=_ssl_context(), timeout=timeout) as r:
        return r.read()


def http_get_text(url: str, *, timeout: int = 120, encoding: str = "utf-8") -> str:
    return http_get_bytes(url, timeout=timeout).decode(encoding)


# ---- JSON I/O --------------------------------------------------------------

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(obj, f, indent=2, default=str)


def read_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


# ---- Cross-pipeline: IRENA cache from push-factors -------------------------

PUSH_FACTORS_CACHE = PIPELINE_ROOT.parent / "push-factors" / "data" / "cache"


def load_irena_capacity() -> list[dict] | None:
    """Load the IRENA capacity cache produced by ../push-factors/fetch_irena.py."""
    p = PUSH_FACTORS_CACHE / "irena_capacity.json"
    if not p.exists():
        return None
    return read_json(p)
