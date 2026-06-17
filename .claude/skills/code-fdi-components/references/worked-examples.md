# Worked examples

Twelve real rows coded end-to-end (the `data/_sample_batch.json` set), spanning all four technologies and every hard case. Each shows the coded output and the lesson it teaches. These are the regression set: if a future taxonomy change breaks one of these, re-examine the change.

## Solar

**HARSOL127 — TBEA, Ain Sokhna, Egypt** → `Inverters` / `850440` / capacity **null** / tier 3
The headline "$11.5bn solar manufacturing complex" tags the whole Ain Sokhna site, but this row's actor (TBEA + JV Kemet) makes **only inverters** — GCL's 5 GW cells and Cornex's 5 GWh storage belong to *other companies* and must not be attached. Image HS6 `854129` is wrong (telephony parts); inverters are static converters → `850440`. Bonus data-quality catch: the row's `Amount` source URL actually points at the unrelated Xinyi Indonesia glass project, so `InvestM=11500` is unverified for Egypt.
*Lesson: in an integrated complex, map the actor to the component; never inherit a partner's capacity.*

**HARSOL144 — Xinyi, Rempang (Batam), Indonesia** → `Other / out-of-shortlist` (`700991`) / capacity **null** / tier 2
Xinyi's anchor product is solar **glass** (HS 700991), which is outside the 5-item shortlist, even though the same complex hosts a separate 2 GW module line (854143). Don't force it onto Modules just because Modules is admissible. Capacity in the source is 2,400 tonnes/**day** melting — a per-day unit, left un-annualized and noted.
*Lesson: code the actual anchor product, even when it falls out of the shortlist; watch per-day vs per-year units.*

**HARSOL64 — Hongshi Group, Indonesia** → `Other / out-of-shortlist` (`280461`, polysilicon) / capacity **null** / tier 3
Integrated silicon→polysilicon→cell→module complex; coded to the upstream anchor (polysilicon). Parent Hongshi is a *cement* maker — the Solar tag is correct only via its Asia Silicon stake, so don't reject the row on the parent's name. The "capacity" numbers in the sources (90,000 t Asia Silicon; 250,000 t / 15 GW Qinghai) are for **existing China plants**, not this Indonesia site; the "2 GW" is a captive power station.
*Lesson: don't borrow a parent's other-site capacity onto this row; don't misread a captive power figure as product capacity.*

## Battery

**EV1 (Battery row) — Toyota, Liberty NC, USA** → `Lithium-ion battery (cell/pack)` / `850760` / **30 GWh/year** / tier 1
"30 GWh annually at full capacity" stated in Toyota's PR. Correctly tagged Battery (cells live under Battery, not EV). $13.9B is capex, not capacity.
*Lesson: the clean Tier-1 shape — component + capacity both in a primary source, GWh for finished cells.*

**Battery 15.1 — Hon Hai (Foxconn), Batang, Indonesia** → `Lithium-ion battery (cell/pack)` / `850760` / capacity **null** / tier 3
Foxconn/IBC/Indika/Gogoro MoU: integrated ecosystem (cells + cathode precursor + 2W/4W EVs + ESS + recycling). Primary = Li-ion cell. $8B is total ecosystem capex across five parties. A nearby CATL 15 GWh Batang plant and an IBC-LG plant are *different projects at the same estate* — do not borrow their figures.
*Lesson: MoU-stage ecosystems rarely publish facility throughput; null beats a borrowed number.*

**HAR0010 — CATL, Debrecen, Hungary** → `Lithium-ion battery (cell/pack)` / `850760` / **100 GWh/year** / tier 1
"100 GWh battery plant", cells + modules (multi-component, cells primary). EUR 7.34B (~$7.5B) is capex, not capacity. CATL builds Li-ion (NMC/LFP) → `850760`, never Ni-MH.
*Lesson: default integrated gigafactories to the Li-ion cell; the InvestM field is the capex, the GWh is separate.*

## Wind

**New_MY_UK1 — Mingyang, Ardersier, UK** → `Nacelles` / `841290` / capacity **null** / tier 3
"Fully integrated" plant: Phase 1 makes nacelles + blades (both map to 841290), later phases add electronics → multi-component. Only capex (≤£1.5B) and ~1,500 jobs disclosed; no annual throughput. Status soft (UK government reportedly not backing Mingyang turbines).
*Lesson: nacelle+blade plants are inherently multi-component on one HS6; early-stage rows give capex/jobs but not capacity.*

**FDI148696 — Acciona, Escobedo, Mexico** → `Towers` / `730820` / capacity **null** / tier 3
Makes **concrete** wind tower segments. The shortlist routes Towers → `730820` (iron/steel), so flag the material mismatch (concrete ≈ 6810). The $650M is the Ventika I+II **wind-farm** cost (252 MW, 84 turbines), not the plant's capex or capacity.
*Lesson: never read a downstream wind-farm $/MW as a component-plant capacity; flag concrete-under-steel-code.*

**FDI188773 — Nordex, Piauí, Brazil** → `Towers` / `730820` / **80 towers/year** / tier 1
"Capacity to construct 80 towers a year able to support 250 MW" — 80 towers/year primary, ~250 MW/year equivalent noted. $416M is the 195 MW complex cost, not the plant. A separate developer pour-yard ("1,500 concrete components") must not be conflated with the Nordex factory.
*Lesson: a tower plant has two valid units (towers/year and MW/year) — pick the count, note the MW; isolate the specific factory's figure.*

## EV

**EV1 (EV row) — Toyota, Liberty NC, USA** → `Other / out-of-shortlist` (`850760`) / **30 GWh/year** / tier 2
This EV-tagged row is the *same Liberty NC battery plant*. Batteries belong under Battery, not EV → out-of-shortlist for EV, with a re-tag recommendation. The `GWh` unit is the giveaway and triggers the validator's re-tag warning.
*Lesson: a GWh capacity on an EV row means a misfiled battery plant — flag for re-tag, don't force an EV code.*

**EV2 — Honda, Alliston, Canada** → `Finished EV / vehicle assembly` / `870380` / **240,000 vehicles/year** / tier 1
"240,000 EVs per year". The co-located 36 GWh battery + CAM/pCAM + separator JVs (named in `JV_company`) are Battery-tech and belong there, not on this EV row.
*Lesson: don't let prominent battery-JV names pull a battery capacity onto the vehicle row; code the assembly line in vehicles/year.*

**New_MarutiSuzuki_IN1 — Maruti Suzuki, Hansalpur, India** → `Finished EV / vehicle assembly` / `870380` / **67,000 vehicles/year** / tier 2
e-Vitara BEV line. The codeable capacity is the EV throughput (~67k/yr planned, ~110k at peak), **not** the plant's 750k–1M total (mostly ICE) capacity. Production target vs export volume (50–100k) vs peak-line capacity are three different numbers in the same press cycle.
*Lesson: code the component line's throughput, not the whole multi-model plant; separate target / export / peak figures.*
