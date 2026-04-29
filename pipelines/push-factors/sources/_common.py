"""Shared helpers for the push-factors pipeline.

stdlib-only. Country list, ISO3 <-> ISO-numeric mapping (WITS uses numeric),
technology <-> HS6 mapping with HS-revision awareness.

Scope: 40 countries — the set that covers both (a) the major home-country
exporters in solar/wind/battery/EV manufacturing and (b) the main destination
markets for LCT FDI. Extend COUNTRIES to widen coverage.
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

# (canonical name, ISO3, ISO numeric 3-digit zero-padded).
# Extend this list to widen coverage; every downstream script iterates it.
COUNTRIES: list[tuple[str, str, str]] = [
    ("China",          "CHN", "156"),
    ("United States",  "USA", "840"),
    ("Germany",        "DEU", "276"),
    ("Japan",          "JPN", "392"),
    ("South Korea",    "KOR", "410"),
    ("India",          "IND", "356"),
    ("Australia",      "AUS", "036"),
    ("United Kingdom", "GBR", "826"),
    ("France",         "FRA", "250"),
    ("Spain",          "ESP", "724"),
    ("Italy",          "ITA", "380"),
    ("Netherlands",    "NLD", "528"),
    ("Belgium",        "BEL", "056"),
    ("Sweden",         "SWE", "752"),
    ("Switzerland",    "CHE", "756"),
    ("Portugal",       "PRT", "620"),
    ("Poland",         "POL", "616"),
    ("Czech Republic", "CZE", "203"),
    ("Romania",        "ROU", "642"),
    ("Turkey",         "TUR", "792"),
    ("Canada",         "CAN", "124"),
    ("Mexico",         "MEX", "484"),
    ("Brazil",         "BRA", "076"),
    ("Chile",          "CHL", "152"),
    ("Argentina",      "ARG", "032"),
    ("South Africa",   "ZAF", "710"),
    ("Morocco",        "MAR", "504"),
    ("Egypt",          "EGY", "818"),
    ("Saudi Arabia",   "SAU", "682"),
    ("United Arab Emirates", "ARE", "784"),
    ("Singapore",      "SGP", "702"),
    ("Malaysia",       "MYS", "458"),
    ("Thailand",       "THA", "764"),
    ("Vietnam",        "VNM", "704"),
    ("Indonesia",      "IDN", "360"),
    ("Philippines",    "PHL", "608"),
    ("Taiwan",         "TWN", "490"),  # WITS uses 490 for "Other Asia, nes" which covers Taiwan
    ("Hong Kong",      "HKG", "344"),
    ("Norway",         "NOR", "578"),
    ("Denmark",        "DNK", "208"),
]

NAME_BY_ISO3 = {iso3: name for name, iso3, _ in COUNTRIES}
ISO_NUM_BY_ISO3 = {iso3: iso_n for _, iso3, iso_n in COUNTRIES}
ISO3_BY_NAME = {name.lower(): iso3 for name, iso3, _ in COUNTRIES}
ISO3_BY_ISO_NUM = {iso_n: iso3 for _, iso3, iso_n in COUNTRIES}

# Used by the IRENA pxweb API which speaks ISO3 already.
IRENA_ISO3_OVERRIDES: dict[str, str] = {
    # pxweb sometimes uses alternate ISO3s; patch here if coverage reports misses.
    # (none required for the default country set — audit with --diag if extended.)
}


# ---- Technology <-> HS6 mapping (paper-defined) -----------------------------
# LCT categories follow Table 4 of the paper:
#   solar PV    -> 854140 (HS 1992–2012 parent), 854142/854143 (HS 2017+ splits)
#   wind        -> 850231 (stable all HS revisions)
#   batteries   -> 850760 (Li-ion; HS 2012+), 850780 (other accumulators; stable)
#   EVs         -> 870380 (pure electric; HS 2017+), 870390 (other incl. hybrid; stable)
#
# HS revision cutovers (WITS nomenclature codes):
#   H0=HS92  H1=HS96  H2=HS02  H3=HS07  H4=HS12  H5=HS17  H6=HS22
#
# For pre-2017 years WITS will often still serve 854142/854143 if the reporter
# used national detail beyond their nominal HS revision, but coverage is thin.
# fetch_wits_tariffs fetches every HS6 every year; hs_for_tech() below selects
# the appropriate code(s) per year when aggregating up to a technology index.

TECHS = ("solar_pv", "wind", "batteries", "evs")

HS_CODES: dict[str, list[str]] = {
    "solar_pv":  ["854140", "854142", "854143"],
    "wind":      ["850231"],
    "batteries": ["850760", "850780"],
    "evs":       ["870380", "870390"],
}

# User-supplied seven-code set (excludes the HS 2012-and-earlier parent 854140).
# Used as the default set fetched from WITS.
USER_HS_CODES: tuple[str, ...] = (
    "854142", "854143",  # solar PV (HS 2017 splits)
    "850231",            # wind turbines
    "850760", "850780",  # batteries
    "870380", "870390",  # EVs
)

# Full set we actually fetch (adds the pre-2017 solar PV parent 854140 so that
# solar PV tariffs are not empty before 2017).
FETCH_HS_CODES: tuple[str, ...] = tuple(sorted(set(USER_HS_CODES) | {"854140"}))


def hs_for_tech(tech: str, year: int) -> list[str]:
    """HS codes to average into the tech-level tariff index for a given year.

    Year-aware because 854142/854143 and 870380 only exist from HS 2017.
    Before 2017 we fall back to parent 854140 (solar) and keep 870390 (EVs).
    """
    if tech == "solar_pv":
        return ["854142", "854143"] if year >= 2017 else ["854140"]
    if tech == "wind":
        return ["850231"]
    if tech == "batteries":
        return ["850760", "850780"] if year >= 2012 else ["850780"]
    if tech == "evs":
        return ["870380", "870390"] if year >= 2017 else ["870390"]
    raise ValueError(f"unknown tech: {tech!r}")


# Year window.
YEAR_START = 2003
YEAR_END = 2025


def years() -> range:
    return range(YEAR_START, YEAR_END + 1)


# ---- HTTP helpers -----------------------------------------------------------

UA = "Mozilla/5.0 (NZIPL push-factors pipeline; contact: netzeropolicylab.com)"


def _ssl_context() -> ssl.SSLContext:
    """WITS + IRENA both serve valid certs that sometimes fail verification on
    macOS default trust stores. Use an unverified context to avoid having to
    ship a CA bundle — acceptable for a read-only research pipeline.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def http_get_json(url: str, *, timeout: int = 120) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, context=_ssl_context(), timeout=timeout) as r:
        return json.loads(r.read())


def http_post_json(url: str, payload: dict, *, timeout: int = 120) -> Any:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, context=_ssl_context(), timeout=timeout) as r:
        return json.loads(r.read())


# ---- JSON I/O --------------------------------------------------------------

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(obj, f, indent=2, default=str)


def read_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def iter_country_years() -> Iterable[tuple[str, str, str, int]]:
    for name, iso3, iso_n in COUNTRIES:
        for y in years():
            yield name, iso3, iso_n, y
