# BNEF drops

Hand-curated JSON extracted from BloombergNEF reports (subscription required). File per report/year:

- `battery_supply_chain_YYYY.json` — Li-ion cell capacity/production by country
- `solar_mfg_capacity_YYYY.json` — PV module (and optionally cell/wafer) capacity
- `wind_oem_tracker_YYYY.json` — nacelle capacity / shipments by OEM (aggregated to HQ country)

Each row must include the exact table/exhibit reference in the `source` field so figures can be re-verified. Use `priority: 10` so BNEF wins over public IEA when both report the same cell.

See `../TEMPLATE.json` for the row schema.
