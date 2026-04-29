"""Minimal stdlib-only xlsx reader.

Supports the subset of Office Open XML needed for the JLOP_2025 file:
  - shared strings (inline text only; no rich-text formatting preserved)
  - sheet rows with string (t="s") and numeric/inline cells
  - inline strings (t="inlineStr")
  - boolean (t="b") and error (t="e") treated as raw text

We only read the first sheet. Columns are returned as a list keyed by the
header row. Memory strategy: stream sheet rows via iterparse and clear elements
to cap memory at ~10MB even for 50k-row files.
"""
from __future__ import annotations

import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Iterator

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
C_COL = f"{NS}c"
C_VAL = f"{NS}v"
C_INL_IS = f"{NS}is"
C_ROW = f"{NS}row"
C_SI = f"{NS}si"
C_T = f"{NS}t"


def _load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    """<si> elements may contain multiple <t> children (rich-text runs).
    Concatenate them in order.
    """
    try:
        info = zf.getinfo("xl/sharedStrings.xml")
    except KeyError:
        return []
    out: list[str] = []
    with zf.open(info) as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == C_SI:
                parts: list[str] = []
                for t in el.iter(C_T):
                    parts.append(t.text or "")
                out.append("".join(parts))
                el.clear()
    return out


def _cell_value(c: ET.Element, shared: list[str]) -> str:
    t = c.get("t")
    if t == "inlineStr":
        is_el = c.find(C_INL_IS)
        if is_el is None:
            return ""
        parts = [(tt.text or "") for tt in is_el.iter(C_T)]
        return "".join(parts)
    v = c.find(C_VAL)
    raw = (v.text if v is not None else "") or ""
    if t == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            return ""
    # Numeric, boolean, error, or date serial — return raw text.
    return raw


def _col_index(ref: str) -> int:
    """Convert 'A1' -> 0, 'B1' -> 1, 'AA3' -> 26."""
    col = 0
    for ch in ref:
        if ch.isalpha():
            col = col * 26 + (ord(ch.upper()) - ord("A") + 1)
        else:
            break
    return col - 1


def iter_rows(path: Path, sheet: str = "xl/worksheets/sheet1.xml") -> Iterator[list[str]]:
    """Yield one list-of-strings per row. Gaps (empty cells) are filled with ''.

    First yielded row is the header.
    """
    with zipfile.ZipFile(path) as zf:
        shared = _load_shared_strings(zf)
        with zf.open(sheet) as f:
            for _, el in ET.iterparse(f, events=("end",)):
                if el.tag != C_ROW:
                    continue
                cells: list[str] = []
                for c in el.findall(C_COL):
                    ref = c.get("r") or ""
                    idx = _col_index(ref) if ref else len(cells)
                    while len(cells) < idx:
                        cells.append("")
                    cells.append(_cell_value(c, shared))
                yield cells
                el.clear()


def read_rows_as_dicts(path: Path, sheet: str = "xl/worksheets/sheet1.xml") -> Iterator[dict]:
    """Iter rows zipped against the header row."""
    it = iter_rows(path, sheet=sheet)
    header = next(it)
    for row in it:
        # Pad/truncate to header length
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        yield dict(zip(header, row))


def read_bytes_as_dicts(data: bytes, sheet: str = "xl/worksheets/sheet1.xml") -> Iterator[dict]:
    """Convenience: parse from an in-memory xlsx buffer."""
    buf = io.BytesIO(data)
    with zipfile.ZipFile(buf) as zf:
        shared = _load_shared_strings(zf)
        with zf.open(sheet) as f:
            header: list[str] | None = None
            for _, el in ET.iterparse(f, events=("end",)):
                if el.tag != C_ROW:
                    continue
                cells: list[str] = []
                for c in el.findall(C_COL):
                    ref = c.get("r") or ""
                    idx = _col_index(ref) if ref else len(cells)
                    while len(cells) < idx:
                        cells.append("")
                    cells.append(_cell_value(c, shared))
                if header is None:
                    header = cells
                else:
                    if len(cells) < len(header):
                        cells = cells + [""] * (len(header) - len(cells))
                    yield dict(zip(header, cells))
                el.clear()
