# Verification protocol

`verificationTier` is the most load-bearing field. Tier inflation is the most common failure. The validator enforces the matrix below.

## Tier matrix

| Tier | Required evidence | Min distinct citation URLs |
|------|-------------------|----|
| 1 Confirmed | Primary (company PR / govt filing / SEC) + corroborator (permit / named-author trade coverage) + independent news | 3 |
| 2 Likely | Company announcement + one top-tier independent, OR two independent top-tier named-authors | 2 |
| 3 Announced-only | Single source | 1 |

Syndication of one press release = one source, not three.

## Status × tier (enforced)

| Status | Required tier |
|--------|--------------|
| Operating | 1 |
| Under Construction | 1 |
| Closed | 1 |
| Rumored | 3 |
| Planned / Announced / Paused / Cancelled | any |

Invalid pair → fix tier (add sources) or status (downgrade), not both.

## Disambiguation

Every source must distinguish the specific facility — by city, permit ID, groundbreaking date, or assigned product line. Drop a tier when sources conflate sister plants. High-ambiguity operators: Ford+SK On BlueOval cluster, GM+LGES Ultium cluster, Stellantis+Samsung SDI StarPlus, BYD (dozens globally), CATL (25+ globally).

## Paywalls

Tier-1 citations allowed only if a free mirror exists. Cite the mirror URL. No mirror = source is invisible.

## Conflicting sources

| Disagreement | Resolution |
|--------------|-----------|
| Two investment figures | Most recent → `investmentM`; earlier → `investmentM_history`. |
| Company says "Operating", independent says "delayed" | Trust independent; downgrade status. |
| Company says "Cancelled", independent says "Paused" | Trust company. |
| Different dates | Use most precise; note ambiguity. |

Never silently average.

## Re-verification

Records decay. On every re-touch:
- Update `verifiedDate`.
- Evidence stronger → upgrade tier, add URLs.
- Evidence weaker → downgrade tier or status.
- Value changed → append to `investmentM_history`; update `investmentM` headline.
