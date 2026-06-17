# Coding protocol

How to turn one FDI row into a `(Component, Component HS6, Capacity Value, Capacity Unit, Capacity Source, Coding Tier, Coding Notes)` tuple. The taxonomy is `component_taxonomy.json`; this file is the decision procedure that uses it.

## Step 1 — Read the sources that are already in the row

Every row carries `Source (...)` columns. Read them before searching the open web:

- **Company PR / press release** — usually states the product and often the capacity. Most reliable for *what* the plant makes.
- **Trade-press article** (pv-magazine, electrive, offshorewind.biz, renewablesnow, Reuters, etc.) — usually corroborates and often carries the capacity figure.
- The `Industry Activity` source frequently names the specific product line.

Only run a targeted web search (company + city + `capacity` / `GWh` / `GW` / `tonnes` / `units per year`) when the row's own sources don't yield the component or the capacity.

## Step 2 — Classify the component (from text, never from an HS6)

Match the plant's product to the admissible shortlist for the row's `Technology` in `component_taxonomy.json` → `technologies.<Tech>.components`. Use the `aliases` list to recognize wording. Then:

- **Fits one admissible component** → use that canonical name and its `hs6`.
- **Integrated / multi-component site** (cell+module, ingot+wafer, "ecosystem", "fully integrated") → code the **primary** component the row's *actor* builds; set a multi-component note listing the others. Do **not** split one row into many, and do **not** attach a co-located partner's capacity.
- **Real plant type, but outside the shortlist** (polysilicon, wafer, solar glass, EVA film, concrete tower, lead-acid, capacitor, generic auto parts, charging-network rollout) → `Component = "Other / out-of-shortlist"`; name what it makes and the likely code in `Coding Notes`. Check the technology's `out_of_shortlist` list for the standard handling.
- **Wrong technology tag** → if an `EV` row is really a battery plant (GWh capacity, cells/materials), code `Other / out-of-shortlist` and recommend re-tagging to `Battery` in `Coding Notes`. Battery cells/materials are always `Battery`, never `EV`.

### Disambiguation rules (where one HS6 hides several components)

| Situation | Rule |
|-----------|------|
| Wind `850231` vs `841290` | `850231` = a complete generating set (final turbine assembly/integration). `841290` = wind-engine *parts*. A plant doing final nacelle+hub mating → Wind Turbine (850231); a plant fabricating a nacelle/blade/hub → the component (841290). |
| Wind Nacelles vs Blades | Both are `841290`. The code cannot tell them apart — pick the component by the row's text; if it makes both, code Nacelles primary and list Blades in notes. |
| Battery materials | Image key `850780` covers cathode, anode, electrolyte, both current collectors, NiMH cathode — and `850780` is really "other accumulators". A genuine `850780`-coded cell is far more likely a non-shortlist chemistry. **Always classify the material by name** (CAM/NMC, graphite anode, separator film, LiPF6, Cu/Al foil). |
| EV `850440` | Shared by traction inverter, EV charger, and on-board DC-DC. Disambiguate by description; if a row only says "power electronics", default to the inverter and note the ambiguity. |
| EV e-axle | No native HS6. Default `870850` (drive-axle) for a marketed e-axle/drive unit; `870840` if clearly just a gearbox; `850153` if clearly just a motor. |
| EV motor | `8501` codes are power-rated, not EV-labeled. >75 kW AC → `850153` (default for traction motors). |
| Solar `854149` | Weak residual. Most "PV semiconductor" rows are really cells (854142) or modules (854143) — re-bucket before using 854149. |

## Step 3 — Extract the annual capacity (value + unit)

Find the component's **annual production capacity** — its nameplate throughput per year. Capacity-unit cheat sheet (full list per component in the taxonomy):

| Component family | Unit |
|------------------|------|
| Solar module / cell / inverter | `GW/year` (or `MW/year`) — **power, never GWh** |
| Solar mounting | `tonnes/year` or `units/year` |
| Solar glass / film / polysilicon (out-of-shortlist) | `tonnes/year` (watch tonnes/**day** melting figures) |
| Wind turbine assembly | `MW/year` or `turbines/year` |
| Wind blade | `blades/year` or `blade-sets/year` (3 blades = 1 set) |
| Wind tower | `towers/year` |
| Wind nacelle / gearbox / generator | `units/year` (or `MW/year`) |
| Battery cell / pack | `GWh/year` (**energy, not GW**) |
| Battery materials (cathode/anode/electrolyte/current collector) | `tonnes/year` |
| Battery separator | `million-m2/year` or `tonnes/year` |
| Battery recycling | `tonnes/year` (note input-feedstock vs recovered-output basis) |
| EV vehicle assembly | `vehicles/year` |
| EV motor / inverter / e-axle / charger | `units/year` |

Hard constraints:

- **Per-year only.** Reject cumulative, installed-base, and order-book figures. Annualize a per-day/per-month figure only if a clean annualization is stated; otherwise leave blank and note the as-stated number.
- **Investment is not capacity.** If the only number is `Capital Investment (US$m)` or "supports N vehicles", leave `Capacity Value` blank.
- **Code the component line, not the whole plant.** A mixed ICE+EV plant's total ≠ the EV throughput; a co-located cell line's GWh ≠ the vehicle plant's capacity.
- **GW vs GWh.** A plain "GW" for a cell plant is almost always GWh; a GWh on a solar/EV row is almost always a misfiled battery plant.

Record `Capacity Source` = the single URL the figure came from (must be http(s), not a forbidden domain).

## Step 4 — Tier and note

| Tier | Test |
|------|------|
| 1 | Component **and** capacity both explicitly stated in a primary/independent source. Requires `Capacity Value` + `Unit` + `Source`. |
| 2 | Component clear; capacity inferred, single-source, or denominator-ambiguous. |
| 3 | Component uncertain, or no annual capacity findable. |

`Coding Notes` should capture: multi-component (and the secondary components), out-of-shortlist reason, ramp stage (phase-1 vs full-ramp), material/HS mismatch (e.g. concrete tower under steel code 730820), and any re-tag recommendation.

## Step 5 — Apply and validate

Append the row to the batch JSON, then:

```bash
python3 data/fdi_coding.py apply <batch.json>   # validates, backs up, merges by Project ID
python3 data/fdi_coding.py validate              # whole-workbook check + coverage
```

If a Project ID is duplicated (e.g. `EV1` exists as both a Battery and an EV row), include `"technology"` in the batch entry so `apply` writes to the right row.
