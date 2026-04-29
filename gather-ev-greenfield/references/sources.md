# Source catalog

Priority: Tier A → Tier B. Skip Tier C and below — the validator hard-rejects the worst offenders.

## Forbidden (validator blocks)

The validator rejects any `sources.*` URL from:
- `wikipedia.org`, `grokipedia.com` — tertiary summaries, not sources
- `linkedin.com`, `reddit.com`, `twitter.com`, `x.com`, `facebook.com`, `instagram.com` — social
- `medium.com` — self-published

Use Wikipedia for lead generation only. Never cite.

## Tier A — Primary (start here)

**Company channels.** Newsroom / investor relations on the company's own domain. Every OEM and battery maker has one: `tesla.com`, `lgensol.com`, `catl.com/en/news`, `byd.com/en/news`, `stellantis.com/en/news`, `volkswagen-group.com/en/press`, `ford.com/media`, `samsungsdi.com`, `gotion.com.cn`. SEC 10-K/20-F, annual reports, investor-day decks.

**Government channels.**
- US: `energy.gov/lpo`, `selectusa.gov`, state econ-dev agencies (`michiganbusiness.org`, `tnecd.com`, `thinkkentucky.com`)
- Germany: `bmwk.de`, `gtai.de`, state ministries
- Korea: `motie.go.kr/eng`, `investkorea.org`
- Japan: `meti.go.jp/english`, `jetro.go.jp/en`
- China: `miit.gov.cn`, `ndrc.gov.cn`
- Mexico: `gob.mx/se`
- India: `heavyindustries.gov.in`, `investindia.gov.in`
- Canada: `ised-isde.canada.ca`
- Hungary: `hipa.hu`
- Poland: `paih.gov.pl`
- Spain: `investinspain.org`
- France: `businessfrance.fr`
- Turkey: `invest.gov.tr`
- Brazil: `gov.br/mdic`

**Open facility databases.**
- `atlasevhub.com` — US battery/EV facilities (free, public, 300+)
- `openinframap.org` — coordinate verification

## Tier B — Named-author trade press (use to corroborate)

English: Electrive, Battery-News, InsideEVs, Electrek, CleanTechnica, Reuters Autos.
Regional: The Elec (Korea), CnEVPost (China), Nikkei Asia (Japan, paywall), Handelsblatt (Germany, paywall), L'Argus (France), Valor Econômico (Brazil).

Paywalled sources allowed **only when a free mirror exists** — cite the mirror (Reuters syndication, Yahoo Finance, local-language wire).

## Tier D — Dedup only (never citation)

- `nzipl_bnef_projects.json` — BloombergNEF snapshot, Mexico-only. Dedup receipt via `sources.bnef_origin`.

## Language-first rule

Asian and European parents often announce in local language weeks before English. Search local first; machine translation suffices for dates, numbers, coordinates.

| Parent | Engine + query |
|--------|----------------|
| Korean | Naver: `<company hangul> 배터리 공장 <city>` |
| Japanese | Google.co.jp: `<company kanji> EV 工場 <city>` |
| Chinese | Baidu: `<company hanzi> 电池工厂 <city>` |
| German | Handelsblatt / Tagesschau: `<company> Werk <Stadt>` |
| French | Le Monde / Les Échos: `<company> usine <ville>` |
| Spanish | Reuters.es / El País: `<company> planta <ciudad>` |
| Portuguese | Valor Econômico: `<company> fábrica <cidade>` |

Detailed country templates: `appendix/search-playbook.md`.

## When to extend this file

Append a new Tier A source (government portal, open database) when you discover one. Log a one-liner in `../../discoveries.md` so others know. Tier B churn (newsrooms renaming, URLs changing) — update in place.
