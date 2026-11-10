#!/usr/bin/env python3
"""Validate FDI source citations in columns P-W of an xlsx.

Hard-rejects forbidden-domain URLs (wikipedia, social, medium) and reports
malformed cells. Exit code 0 = clean; non-zero = errors found. URLs carrying a
chat-referral tag (utm_source=chatgpt) are listed as warnings: they were copied,
not read.

This is a format gate. Whether a page states the value it is cited for is checked
by LCT-FDI/bin/source_check.py, which MasterEdit runs before every write.

Usage:
    python3 validate_fdi_sources.py ../LCT-FDI/FDI_All_ToSource.xlsx
"""

from __future__ import annotations  # str | None in signatures; a stock macOS python3 is 3.9

import re
import sys
from urllib.parse import urlparse

import openpyxl

FORBIDDEN_HOSTS = {
    "wikipedia.org",
    "grokipedia.com",
    "linkedin.com",
    "reddit.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "medium.com",
}

# Logical labels -> master header names. Columns are found BY NAME in the header row, because
# positions shift whenever the master gains a column (they moved in 2026-06 and 2026-09).
SOURCE_NAMES = {
    "P": "Source (Parent company name and HQ)",
    "Q": "Source (Project Status)",
    "R": "Source (Project location, country and city)",
    "S": "Source (Amount)",
    "T": "Source (Ownership share, where available)",
    "U": "Source (Date Announced [MM/DD/YYYY])",
    "V": "Source (Date Completed [MM/DD/YYYY])",
    "W": "Source (Industry Activity)",
}
SOURCE_COLUMNS = list(SOURCE_NAMES)
DATE_COLUMNS = {"U", "V"}
FALLBACK_LITERAL = "fDi Markets (FT)"
UNVERIFIED_PREFIX = "[UNVERIFIED] "
YEAR_ONLY_SUFFIX = "(year only)"
AMOUNT_NOT_DISCLOSED = "Investment value not publicly disclosed"  # col S only


def host_of(url: str) -> str | None:
    try:
        host = urlparse(url).hostname
    except ValueError:
        return None
    if not host:
        return None
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def is_forbidden(url: str) -> str | None:
    host = host_of(url)
    if host is None:
        return None
    for bad in FORBIDDEN_HOSTS:
        if host == bad or host.endswith("." + bad):
            return bad
    return None


def extract_url(cell_value: str) -> str | None:
    """Pull the URL out of a cell that may have prefixes / suffixes."""
    body = cell_value
    if body.startswith(UNVERIFIED_PREFIX):
        body = body[len(UNVERIFIED_PREFIX):]
    body = body.strip()
    if body == FALLBACK_LITERAL:
        return None
    match = re.match(r"(https?://\S+)", body)
    return match.group(1) if match else None


def validate_cell(col: str, value) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    if text == FALLBACK_LITERAL or text == UNVERIFIED_PREFIX + FALLBACK_LITERAL:
        return []
    if col == "S" and text == AMOUNT_NOT_DISCLOSED:
        return []

    body = text[len(UNVERIFIED_PREFIX):].strip() if text.startswith(UNVERIFIED_PREFIX) else text

    if col in DATE_COLUMNS and body.endswith(YEAR_ONLY_SUFFIX):
        body = body[: -len(YEAR_ONLY_SUFFIX)].strip()

    if not body.startswith(("http://", "https://")):
        return [f"col {col}: not a URL or recognized fallback: {text!r}"]

    url = extract_url(text)
    if url is None:
        return [f"col {col}: could not parse URL from {text!r}"]

    bad = is_forbidden(url)
    if bad:
        return [f"col {col}: forbidden domain {bad} in {url}"]
    return []


def main(path: str) -> int:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["All"] if "All" in wb.sheetnames else wb.active
    errors: list[str] = []

    header = [None if c is None else str(c).strip() for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
    idx = {label: header.index(name) for label, name in SOURCE_NAMES.items() if name in header}
    if len(idx) < len(SOURCE_NAMES):
        missing = [SOURCE_NAMES[l] for l in SOURCE_NAMES if l not in idx]
        print(f"error: source columns missing from sheet: {missing}", file=sys.stderr)
        return 2

    warnings: list[str] = []
    for r, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        for label, i in idx.items():
            v = row[i] if i < len(row) else None
            for err in validate_cell(label, v):
                errors.append(f"row {r}, [{SOURCE_NAMES[label]}] {err}")
            if v is not None and "utm_source=chatgpt" in str(v):
                warnings.append(f"row {r}, [{SOURCE_NAMES[label]}] chat-referral tag, URL copied not read: {str(v)[:70]}")

    for w in warnings:
        print("warning:", w)
    if warnings:
        print(f"{len(warnings)} warning(s): strip the tag, read the page, then keep or replace the URL.")
    if errors:
        for e in errors:
            print(e)
        print(f"\n{len(errors)} error(s) found in {path}", file=sys.stderr)
        return 1

    print(f"OK: {path} — no forbidden domains or malformed source cells.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
