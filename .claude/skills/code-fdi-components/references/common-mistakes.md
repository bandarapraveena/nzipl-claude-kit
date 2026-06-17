# Common mistakes

A pre-write checklist. Every item here was hit by at least one of the 12 worked examples. Append new recurring errors as they surface.

## Capacity

1. **Investment dollars coded as capacity.** `Capital Investment (US$m)` is capex. If that is the only large number, `Capacity Value` is blank and the row is tier 3. (Hit by HARSOL127, Battery 15.1, New_MY_UK1, FDI148696, EV2.)
2. **"Supports / powers N vehicles" treated as capacity.** Not a production figure. Note it; don't back-convert to GWh or units.
3. **GW vs GWh.** Solar/wind components are GW/MW (power); battery cells are GWh (energy). A plain "GW" for a cell plant is almost certainly GWh; a GWh on a Solar or EV row is almost certainly a misfiled battery plant → flag for re-tag.
4. **Cumulative / installed-base / order-book figures.** Capacity is annual nameplate throughput. Reject to-date and fleet-installed numbers.
5. **Whole-plant total vs component line.** A mixed ICE+EV plant's total is not the EV throughput (Maruti: 1M total ≠ 67k EV). A co-located cell line's GWh is not the vehicle plant's capacity (Honda).
6. **Borrowing another site's number.** Don't put a parent's China-plant tonnage on its new Indonesia site (Hongshi), or a different company's plant at the same industrial estate (Battery 15.1, CATL-Batang).
7. **Per-day vs per-year units.** Solar-glass melting is often tonnes/**day**; only annualize if a clean figure is stated, else leave blank and note (Xinyi).
8. **Phase-1 vs full-ramp.** Announcements quote the larger full build-out. Record the stated figure and say which.

## Component classification

9. **Trusting the HS6 over the text.** The image assigns `850780` to six battery materials, and `850780` is really "other accumulators". Read the project description; classify cathode/anode/separator/electrolyte/foil by name.
10. **Wind 850231 vs 841290.** Complete turbine assembly = 850231; nacelle/blade/hub fabrication = 841290. And 841290 cannot tell a nacelle from a blade — use the text.
11. **EV 850440 collision.** Inverter, charger, and DC-DC all share 850440 — disambiguate by description.
12. **Forcing a row onto the shortlist.** Solar glass, polysilicon, wafer, EVA film, concrete towers, lead-acid, capacitors, generic auto parts, charging-network rollouts are out-of-shortlist. Code `Other / out-of-shortlist` and explain; do not jam them into the nearest admissible bucket (Xinyi glass ≠ Modules).
13. **Rejecting a row on the parent's name.** A cement company (Hongshi) or a contract manufacturer (Foxconn) can still run a real solar/battery plant — check what the *plant* makes.
14. **Wrong technology tag.** Battery cells/materials are always `Battery`, never `EV`. An EV-tagged row with GWh capacity is a misfiled battery plant → out-of-shortlist + re-tag recommendation.

## Multi-component sites

15. **Splitting one row into many, or summing stages.** One row = one primary component + a multi-component note. Don't add cell GW + module GW (one throughput, not additive).
16. **Attaching a partner's capacity.** In a complex, only the row's actor's component capacity belongs on the row (TBEA inverter row ≠ GCL's 5 GW cells).

## HS / material mismatches

17. **Image HS errors.** Solar inverter `854129 → 850440`; wind gearbox `870840 → 848340`. The taxonomy carries the correction; the validator accepts either the customs code or the image key.
18. **Material-substrate mismatch.** `730820` (towers) and `730890` (foundations) are iron/steel only — concrete towers fall outside. Flag in `Coding Notes` rather than silently coding.
19. **Battery-grade gate.** Generic aluminium foil, copper foil, graphite, glass, and lithium-refining plants are out-of-shortlist unless the source says battery-grade / solar-grade.

## Process

20. **Hand-editing the workbook.** Always go through `fdi_coding.py` (it backs up and validates). Never type coding cells directly.
21. **Skipping the validator.** Run `validate` after every `apply`; treat violations as blocking, warnings as a re-check prompt.
22. **Duplicate Project IDs.** `EV1` exists as both a Battery and an EV row — include `"technology"` in the batch entry so `apply` targets the right one.
