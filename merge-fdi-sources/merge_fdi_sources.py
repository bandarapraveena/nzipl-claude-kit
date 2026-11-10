"""Merge a curated FDI source list into FDI_All_ToSource.xlsx, through LCT-FDI/bin/master_io.py.

Auto-detects the input format from the workbook layout:

  * China list  (e.g. China_FDI_Battery.xlsx, sheet = tech name)
      - Match key: HAR* IDs in column 1
      - Source cols 15-22, Capital Investment col 11
      - Empty marker: '\\'

  * Global manual list  (e.g. Globa_FDI_Battery_Manual.xlsx, single sheet)
      - Match key: FDI* IDs in column 1
      - Source cols 18,19,20,21,22,23,24,26 (skips 25 = Tech source)
      - Capital Investment col 13
      - Empty marker: 'NA', '-'

Precedence rules (identical for both inputs):
  1. Column S (Source for Amount) is the priority cell.
  2. An existing master URL beats the curated URL, including '[UNVERIFIED] ...'.
     Only cells equal to 'fDi Markets (FT)' are replaceable, plus the disclosure note in S.
  3. If S is replaced and the curated row has a real Capital Investment value, master L follows.
  4. Empty master cells are not replaced (this skill does not invent sources).

How it writes (since 2026-10-29): this script saves nothing itself. It decides, then hands the
cell edits to the master's own bin/master_io.py (MasterEdit), which backs up the file, refuses
any change not requested, fetches every cited page and refuses a source cell whose page does
not state the value, runs bin/validate_master.py, and logs to data_changes_log.csv and
source_evidence.csv. So that one bad curated URL does not abort a bulk merge, the script first
runs the same page check (bin/source_check.py) on every curated URL it would merge and HOLDS
BACK the cells that fail; they are printed and written to outputs/merge_heldback_<batch>.csv
beside the master, for a reader to fix or tag. --dry-run previews all of it and writes nothing.

The master must sit in its LCT-FDI checkout (bin/master_io.py and bin/source_check.py beside it).
"""
import argparse
import csv
import datetime as dt
import sys
from pathlib import Path

import openpyxl

FALLBACK = "fDi Markets (FT)"
DISCLOSURE_NOTE = "Investment value not publicly disclosed"
L_NAME = "Capital Investment (US$m)"
HELD_NOTE = "(no curated URLs for the replaceable cells, or all held back)"

# Master columns are resolved BY HEADER NAME when the workbook is opened. The letters are logical
# labels only: hard-coded positions broke silently when the master gained Expansion / Phase /
# Joint Venture Local State, and "S" stopped being Source (Amount).
MASTER_COL_NAMES = {
    "P": "Source (Parent company name and HQ)",
    "Q": "Source (Project Status)",
    "R": "Source (Project location, country and city)",
    "S": "Source (Amount)",
    "T": "Source (Ownership share, where available)",
    "U": "Source (Date Announced [MM/DD/YYYY])",
    "V": "Source (Date Completed [MM/DD/YYYY])",
    "W": "Source (Industry Activity)",
}

LAYOUTS = {
    "china": {
        "id_prefix": "HAR",
        "id_col": 1,
        "source_cols": {"P": 15, "Q": 16, "R": 17, "S": 18, "T": 19, "U": 20, "V": 21, "W": 22},
        "l_col": 11,
        "empty_markers": {"\\"},
    },
    "manual": {
        "id_prefix": "FDI",
        "id_col": 1,
        "source_cols": {"P": 18, "Q": 19, "R": 20, "S": 21, "T": 22, "U": 23, "V": 24, "W": 26},
        "l_col": 13,
        "empty_markers": {"NA", "-"},
    },
}


def detect_layout(ws, hint=None):
    """Return ('china'|'manual', layout_dict). Hint overrides auto-detect."""
    if hint in LAYOUTS:
        return hint, LAYOUTS[hint]
    har = fdi = 0
    for r in range(2, min(ws.max_row, 200) + 1):
        v = ws.cell(r, 1).value
        if not v:
            continue
        s = str(v).strip()
        if s.startswith("HAR"):
            har += 1
        elif s.startswith("FDI"):
            fdi += 1
    if har > fdi:
        return "china", LAYOUTS["china"]
    if fdi > 0:
        return "manual", LAYOUTS["manual"]
    sys.exit("Could not auto-detect input layout: no HAR* or FDI* IDs in column 1.")


def is_real_url(v, empty_markers):
    if v is None:
        return False
    s = str(v).strip()
    if not s or s == FALLBACK or s == DISCLOSURE_NOTE:
        return False
    if any(s.upper() == m.upper() for m in empty_markers):
        return False
    return True


def to_number(v, empty_markers):
    if v is None:
        return None
    s = str(v).strip()
    if not s or any(s.upper() == m.upper() for m in empty_markers):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def is_credible_url(v):
    """A 'credible' source cell: anything that is a real URL (incl. [UNVERIFIED])."""
    if v is None:
        return False
    s = str(v).strip()
    if not s or s == FALLBACK or s == DISCLOSURE_NOTE:
        return False
    return True


def s_is_first_best(v):
    """First-best = column S has a credible URL (a real source for the amount)."""
    return is_credible_url(v)


def s_needs_disclosure(v):
    """S is empty: eligible for the disclosure note when Q is credible.

    'fDi Markets (FT)' is NOT eligible: since 2026-09-29 fDi capex estimates are kept as amounts
    labelled 'fDi Markets (FT)' (only the $39.9m placeholder is rejected), so this pass must not
    overwrite that label or clear the amount behind it."""
    if v is None:
        return True
    return str(v).strip() == ""


def replaceable(letter, val):
    """Replaceable cells: 'fDi Markets (FT)' anywhere, plus the disclosure note in S only (a real
    URL upgrades a previously-disclosed row back to first-best)."""
    s = "" if val is None else str(val).strip()
    if s == FALLBACK:
        return True
    return letter == "S" and s == DISCLOSURE_NOTE


def load_master_tools(master_path):
    """Import master_io and source_check from the master's own bin/ (its LCT-FDI checkout)."""
    b = Path(master_path).resolve().parent / "bin"
    if not (b / "master_io.py").exists():
        sys.exit(f"{b / 'master_io.py'} not found: the master must sit in its LCT-FDI checkout, with bin/ beside it.")
    sys.path.insert(0, str(b))
    import master_io  # noqa: E402
    try:
        import source_check  # noqa: E402
    except ImportError as e:
        sys.exit(f"bin/source_check.py could not be imported ({e}); install requests, or pass --no-page-check "
                 "for a batch you verified by hand.")
    return master_io, source_check


class Master:
    """The master workbook, read through openpyxl and changed in memory only, so that stage 2 sees
    stage 1's result. Every change is also recorded as an edit for MasterEdit, the only thing
    that writes the file."""

    def __init__(self, path):
        self.path = Path(path)
        wb = openpyxl.load_workbook(path)
        if "All" not in wb.sheetnames:
            sys.exit(f"Master file missing sheet 'All': {path}")
        self.ws = wb["All"]
        self.hdr = [str(c.value).strip() if c.value is not None else None for c in self.ws[1]]
        col = {h: i + 1 for i, h in enumerate(self.hdr) if h}
        need = list(MASTER_COL_NAMES.values()) + [L_NAME, "Project ID", "Sector", "Joint Venture"]
        missing = [n for n in need if n not in col]
        if missing:
            sys.exit(f"Master is missing columns {missing}; refusing to write by position.")
        self.col = col
        self.index = {}
        for r in range(2, self.ws.max_row + 1):
            pid = self.ws.cell(r, col["Project ID"]).value
            if pid:
                self.index.setdefault(str(pid).strip(), []).append(r)
        self.edits = []  # (pid, column name, value, why)

    def get(self, r, name):
        return self.ws.cell(r, self.col[name]).value

    def row_dict(self, r, **overrides):
        d = {h: self.ws.cell(r, i + 1).value for i, h in enumerate(self.hdr) if h}
        d.update(overrides)
        return d

    def set(self, r, name, value, why):
        pid = str(self.get(r, "Project ID")).strip()
        if len(self.index[pid]) > 1:
            sys.exit(f"Project ID {pid!r} appears {len(self.index[pid])} times in the master; fix that first "
                     "(validator R01), MasterEdit addresses cells by Project ID.")
        self.ws.cell(r, self.col[name]).value = value
        self.edits.append((pid, name, value, why))


class PageCheck:
    """The same check MasterEdit will run, applied here first so that a failing curated URL is
    held back instead of aborting the whole merge."""

    def __init__(self, sc, cache, strict):
        self.sc, self.cache, self.strict = sc, cache, strict
        self.rates = sc.Rates(quiet=True) if sc else None

    def verdicts(self, items):
        """items: [(column name, url, row dict)] -> [Verdict | None] (None when the check is off)."""
        if self.sc is None or not items:
            return [None] * len(items)
        return self.sc.check_many(items, self.cache, self.rates)

    def holds(self, v, row):
        """True when the verdict means the cell must not be merged."""
        if v is None:
            return False
        if v.verdict.startswith("FAIL"):
            return True
        if v.verdict.startswith("SHARE"):  # a share of the page figure is fine on a JV row only
            return row.get("Joint Venture") not in (1, 1.0, "1")
        if v.verdict == "unfetchable":
            return self.strict
        return False


def stage1(M, ws_c, layout, limit, pc, sc, tag):
    """Stage 1: replace 'fDi Markets (FT)' cells with curated URLs that pass the page check."""
    empty = layout["empty_markers"]
    curated = {}
    for r in range(2, ws_c.max_row + 1):
        pid = ws_c.cell(r, layout["id_col"]).value
        if pid:
            curated[str(pid).strip()] = r
    if limit is not None:  # master-row order, so "first N" is reviewer-friendly
        ordered, seen = [], set()
        for r in range(2, M.ws.max_row + 1):
            pid = M.get(r, "Project ID")
            if not pid:
                continue
            pid = str(pid).strip()
            if pid in curated and pid not in seen:
                ordered.append(pid)
                seen.add(pid)
        pids = ordered
    else:
        pids = sorted(curated)

    missing = [pid for pid in pids if pid not in M.index]
    cands, processed = [], 0  # (pid, mrow, [(letter, name, url)], new_l)
    for pid in pids:
        if limit is not None and processed >= limit:
            break
        if pid not in M.index:
            continue
        crow = curated[pid]
        for mrow in M.index[pid]:
            if limit is not None and processed >= limit:
                break
            if not any(replaceable(L, M.get(mrow, n)) for L, n in MASTER_COL_NAMES.items()):
                continue
            processed += 1
            cells = []
            for letter, name in MASTER_COL_NAMES.items():
                if not replaceable(letter, M.get(mrow, name)):
                    continue
                cval = ws_c.cell(crow, layout["source_cols"][letter]).value
                if is_real_url(cval, empty):
                    cells.append((letter, name, str(cval).strip()))
            new_l = None
            if any(L == "S" for L, _, _ in cells):
                new_l = to_number(ws_c.cell(crow, layout["l_col"]).value, empty)
                if new_l is not None and to_number(M.get(mrow, L_NAME), empty) == new_l:
                    new_l = None
            cands.append((pid, mrow, cells, new_l))

    # the page check, in one parallel fetch, against the row as it would be after the edit
    items, where = [], []
    for ci, (pid, mrow, cells, new_l) in enumerate(cands):
        for k, (letter, name, val) in enumerate(cells):
            u = sc.url_of(val) if sc else None
            if u:
                items.append((name, u, M.row_dict(mrow, **({L_NAME: new_l} if new_l is not None else {}))))
                where.append((ci, k))
    V = dict(zip(where, pc.verdicts(items)))

    log, held = [], []
    for ci, (pid, mrow, cells, new_l) in enumerate(cands):
        changes, s_merged = [], False
        for k, (letter, name, val) in enumerate(cells):
            v = V.get((ci, k))
            if pc.holds(v, M.row_dict(mrow)):
                held.append((pid, mrow, letter, name, val, v.verdict))
                continue
            old = M.get(mrow, name)
            marker = "DISCLOSED" if str(old).strip() == DISCLOSURE_NOTE else "FT"
            note = f"; page {v.verdict}" if v else ""
            M.set(mrow, name, val, why=f"{tag}: curated URL replaces {marker}{note}")
            changes.append(f"{letter}: {marker} -> {val[:60]}{note}")
            if letter == "S":
                s_merged = True
        if s_merged and new_l is not None:
            old_l = M.get(mrow, L_NAME)
            M.set(mrow, L_NAME, new_l, why=f"{tag}: L follows the curated S")
            changes.append(f"L: {old_l} -> {new_l}")
        log.append((pid, mrow, changes or [HELD_NOTE]))
    return log, missing, held, processed


def stage2(M, ws_c, layout, sector_filter, pc, sc, tag):
    """Stage 2, after stage 1: (a) relaxed Q fill for rows not at first-best; (b) disclosure note
    on an EMPTY S where Q is credible, clearing L on the same row."""
    empty = layout["empty_markers"]
    curated_q_col = layout["source_cols"]["Q"]
    curated_idx = {}  # any ID in the curated file; the sector is the filter, not the prefix
    for r in range(2, ws_c.max_row + 1):
        pid = ws_c.cell(r, layout["id_col"]).value
        if pid:
            curated_idx[str(pid).strip()] = r
    in_scope = (lambda s: True) if not sector_filter else (
        lambda s: s is not None and sector_filter.lower() in str(s).lower())

    # (a) relaxed Q fill, page-checked
    cands = []
    for r in range(2, M.ws.max_row + 1):
        if not in_scope(M.get(r, "Sector")):
            continue
        if s_is_first_best(M.get(r, "Source (Amount)")):
            continue
        qv = M.get(r, "Source (Project Status)")
        qs = "" if qv is None else str(qv).strip()
        if qs and qs != FALLBACK:
            continue  # Q already credible
        pid = M.get(r, "Project ID")
        if pid is None or str(pid).strip() not in curated_idx:
            continue
        cval = ws_c.cell(curated_idx[str(pid).strip()], curated_q_col).value
        if is_real_url(cval, empty):
            cands.append((r, str(pid).strip(), str(cval).strip()))
    items = [("Source (Project Status)", sc.url_of(v) or v, M.row_dict(r)) for r, _, v in cands] if sc else []
    V = pc.verdicts(items) if items else [None] * len(cands)
    q_filled, held = [], []
    for (r, pid, cval), v in zip(cands, V):
        if pc.holds(v, M.row_dict(r)):
            held.append((pid, r, "Q", "Source (Project Status)", cval, v.verdict))
            continue
        note = f"; page {v.verdict}" if v else ""
        M.set(r, "Source (Project Status)", cval, why=f"{tag} stage 2: relaxed Q fill{note}")
        q_filled.append((r, pid, cval[:60]))

    # (b) disclosure note on S, and clear L (the FT-derived number is no longer credibly sourced)
    s_disclosed = []
    for r in range(2, M.ws.max_row + 1):
        if not in_scope(M.get(r, "Sector")):
            continue
        if not s_needs_disclosure(M.get(r, "Source (Amount)")):
            continue
        if not is_credible_url(M.get(r, "Source (Project Status)")):
            continue
        pid = str(M.get(r, "Project ID")).strip()
        M.set(r, "Source (Amount)", DISCLOSURE_NOTE, why=f"{tag} stage 2: Q credible, S empty")
        old_l = M.get(r, L_NAME)
        cleared = old_l is not None and str(old_l).strip() != ""
        if cleared:
            M.set(r, L_NAME, None, why=f"{tag} stage 2: amount unsourced once S is the disclosure note")
        s_disclosed.append((r, pid, old_l if cleared else None))
    return q_filled, s_disclosed, held


def write_heldback(master_path, batch, held, dry_run):
    out = Path(master_path).resolve().parent / "outputs"
    out.mkdir(exist_ok=True)
    p = out / f"merge_heldback_{batch}{'_dryrun' if dry_run else ''}.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Project ID", "master row", "column", "curated value", "verdict"])
        for pid, r, letter, name, val, verdict in held:
            w.writerow([pid, r, name, val, verdict])
    return p


def merge(a):
    master_io, sc = load_master_tools(a.master) if not a.no_page_check else (load_master_tools(a.master)[0], None)
    M = Master(a.master)
    wb_c = openpyxl.load_workbook(a.curated, data_only=True)
    if a.sheet and a.sheet in wb_c.sheetnames:
        ws_c = wb_c[a.sheet]
    elif a.sheet:
        sys.exit(f"Curated file missing sheet '{a.sheet}'. Available: {wb_c.sheetnames}")
    else:
        ws_c = wb_c.active
    layout_name, layout = detect_layout(ws_c, a.layout)
    print(f"[info] curated layout: {layout_name} (sheet={ws_c.title})")
    batch = a.batch or f"merge_{Path(a.curated).stem}_{dt.date.today():%Y%m%d}"
    tag = f"merge {Path(a.curated).name}"
    cache = Path(a.cache) if a.cache else Path(a.master).resolve().parent / "_source_cache"
    pc = PageCheck(sc, cache, a.strict)
    if sc is None:
        print("[warn] page check OFF: curated URLs are merged unread; MasterEdit will not check them either")

    log, missing, held, processed = stage1(M, ws_c, layout, a.limit, pc, sc, tag)
    q_filled, s_disclosed, held2 = stage2(M, ws_c, layout, a.sector, pc, sc, tag) if a.stage2 else ([], [], [])
    held += held2

    print("\n=== Change log (stage 1) ===")
    if not log:
        print("  (no changes)")
    for pid, row, changes in log:
        print(f"\n{pid} (master row {row}):")
        for c in changes:
            print(f"  {c}")
    if missing:
        print(f"\n=== Curated IDs not found in master ({len(missing)}) ===")
        for pid in missing[:20]:
            print(f"  {pid}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
    updated = sum(1 for _, _, c in log if c[0] != HELD_NOTE)
    print(f"\nStage 1: processed {processed} matched row(s); {updated} updated.")
    if a.stage2:
        scope = f"sector={a.sector}" if a.sector else "all sectors"
        print(f"\n=== Stage 2 ({scope}) ===")
        print(f"Q (Source for Project Status) filled from curated: {len(q_filled)}")
        for r, pid, url in q_filled:
            print(f"  row {r} {pid}: {url}")
        print(f"\nS (Source for Amount) set to disclosure note: {len(s_disclosed)}")
        for r, pid, cleared_l in s_disclosed:
            tail = f" (L cleared: was {cleared_l})" if cleared_l is not None else ""
            print(f"  row {r} {pid}{tail}")
    if held:
        p = write_heldback(a.master, batch, held, a.dry_run)
        print(f"\n=== Held back: the cited page does not state the value ({len(held)}) -> {p} ===")
        for pid, r, letter, name, val, verdict in held:
            print(f"  {pid} row {r} {letter} {verdict}: {val[:80]}")
        print("  Fix the URL in the curated list, or write the cell by hand with '[UNVERIFIED] ' and a why=.")

    if not M.edits:
        print("\nNothing to write.")
        return 0
    print(f"\n=== Writing {len(M.edits)} cell(s) through MasterEdit (batch {batch}{', DRY RUN' if a.dry_run else ''}) ===")
    mode = False if sc is None else ("strict" if a.strict else True)
    try:
        with master_io.MasterEdit(batch=batch, who=a.who, path=a.master, dry_run=a.dry_run, check_sources=mode) as m:
            for pid, name, val, why in M.edits:
                m.set(pid, name, val, why=why, check="merge")
    except master_io.MasterEditError as e:
        print(f"\nmaster_io refused the write, nothing changed:\n{e}")
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description="Merge a curated FDI source list into FDI_All_ToSource.xlsx through MasterEdit")
    ap.add_argument("--master", required=True, help="Path to FDI_All_ToSource.xlsx inside its LCT-FDI checkout")
    ap.add_argument("--curated", required=True, help="Path to China_FDI_<Tech>.xlsx OR Globa_FDI_<Tech>_Manual.xlsx")
    ap.add_argument("--sheet", default=None, help="Sheet name in the curated file (default: active sheet)")
    ap.add_argument("--layout", choices=list(LAYOUTS), default=None, help="Force layout (default: auto-detect from ID prefix)")
    ap.add_argument("--limit", type=int, default=None, help="Process first N matched rows in master-row order")
    ap.add_argument("--stage2", action="store_true",
                    help="After stage-1 merge, run second-stage verification: relaxed Q-fill + disclosure-note pass on S")
    ap.add_argument("--sector", default=None, help="Sector filter for stage 2 (e.g. 'battery'). Default: all sectors")
    ap.add_argument("--dry-run", action="store_true", help="Decide, check and report; write nothing")
    ap.add_argument("--who", default="merge_fdi_sources", help="Name for the change log (who=)")
    ap.add_argument("--batch", default=None, help="Batch name for the change log (default merge_<curated>_<date>)")
    ap.add_argument("--strict", action="store_true", help="Hold back cells whose page cannot be fetched, instead of merging them")
    ap.add_argument("--no-page-check", action="store_true", help="Skip the page check (a batch verified by hand only)")
    ap.add_argument("--cache", default=None, help="Page cache directory (default: _source_cache beside the master)")
    a = ap.parse_args()
    sys.exit(merge(a))


if __name__ == "__main__":
    main()
