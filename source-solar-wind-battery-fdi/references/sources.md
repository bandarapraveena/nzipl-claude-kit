# Source catalog

Priority: Tier A → Tier B. Skip everything else — the validator hard-rejects the worst offenders.

## Forbidden (validator blocks)

The validator rejects any URL written to P–W from:

- `wikipedia.org`, `grokipedia.com` — tertiary summaries, not sources
- `linkedin.com`, `reddit.com`, `twitter.com`, `x.com`, `facebook.com`, `instagram.com` — social
- `medium.com` — self-published

Wikipedia may be used **for lead generation only** — to find the company's IR domain, the city name, the JV partner name. Never as a citation.

## Tier A — Primary (start here)

### Company channels

Newsroom / investor relations on the company's own domain. Press releases, SEC 10-K / 20-F, annual reports, investor-day decks.

**Battery & EV.** `tesla.com`, `byd.com/en/news`, `catl.com/en/news`, `lgensol.com`, `samsungsdi.com`, `skon.com`, `panasonic.com/global/corporate/news`, `gotion.com.cn`, `northvolt.com/news`, `stellantis.com/en/news`, `volkswagen-group.com/en/press`, `ford.com/media`.

**Solar.** `firstsolar.com/News`, `jinkosolar.com/site/newsroom`, `longi.com/en/news`, `trinasolar.com/us/resources/newsroom`, `canadiansolar.com/news`, `qcells.com/us/get-started/newsroom`, `enphase.com/newsroom`, `solaredge.com/newsroom`, `meyerburger.com/en/media`.

**Wind.** `vestas.com/en/media`, `siemensgamesa.com/newsroom`, `ge.com/news`, `goldwind.com/en/news`, `nordex-online.com/en/press`, `mingyang.com/en/news`, `orsted.com/en/media`, `iberdrola.com/press-room`, `enel.com/media`.

### Government / IPA channels

- US: `energy.gov/lpo`, `selectusa.gov`, state econ-dev (`michiganbusiness.org`, `tnecd.com`, `thinkkentucky.com`, `goeda.georgia.gov`)
- Germany: `bmwk.de`, `gtai.de`
- Korea: `motie.go.kr/eng`, `investkorea.org`
- Japan: `meti.go.jp/english`, `jetro.go.jp/en`
- China: `miit.gov.cn`, `ndrc.gov.cn`
- Mexico: `gob.mx/se`, state secretarías de desarrollo económico
- India: `heavyindustries.gov.in`, `investindia.gov.in`, `mnre.gov.in`
- Canada: `ised-isde.canada.ca`, `nrcan.gc.ca`
- Hungary: `hipa.hu`; Poland: `paih.gov.pl`; Spain: `investinspain.org`; France: `businessfrance.fr`; Turkey: `invest.gov.tr`; Brazil: `gov.br/mdic`
- Multilateral: `irena.org/publications`, `iea.org/news`

### Open facility databases

- `atlasevhub.com` — US battery / EV facilities (300+, free)
- `openinframap.org` — coordinate verification (transmission, generators)
- `globalenergymonitor.org` — solar, wind, coal-to-clean transitions; per-project trackers

## Tier B — Named-author trade press (use to corroborate)

**Battery / EV.** Reuters Autos, Electrive, Battery-News, InsideEVs, Electrek, CleanTechnica, S&P Global Commodity Insights.

**Solar.** PV Magazine, PV-Tech, Solar Power World, Renewables Now, BloombergNEF (Solar).

**Wind.** Windpower Monthly, Recharge News, A Word About Wind, Wind Power Engineering, 4C Offshore (offshore wind).

**Cross-sector.** Reuters, Bloomberg, Financial Times, S&P Global, Nikkei Asia (paywall), Handelsblatt (paywall), Le Monde, Valor Econômico (Brazil), El Financiero / El Economista (Mexico), The Hindu BusinessLine (India).

**Regional EV-specific.** The Elec (Korea), CnEVPost (China), L'Argus (France).

### Paywall rule

Paywalled sources allowed **only when a free mirror exists** — Reuters syndication, Yahoo Finance pickup, the company's own reposting, a local-language wire that ran the same wire copy. Cite the mirror URL. No mirror = the source is invisible for citation purposes.

## Language-first rule

Asian and European parents often announce in local language weeks before English. Search local first; machine translation suffices for dates, amounts, coordinates.

| Parent language | Engine + query template |
|-----------------|------------------------|
| Korean | Naver: `<company hangul> 공장 <city>` (factory) or `발전소 <city>` (power plant) |
| Japanese | Google.co.jp: `<company kanji> 工場 <city>` |
| Chinese | Baidu: `<company hanzi> 工厂 <city>` or `电池工厂` (battery) / `光伏工厂` (solar PV) / `风电` (wind) |
| German | Handelsblatt / Tagesschau: `<company> Werk <Stadt>` |
| French | Le Monde / Les Échos: `<company> usine <ville>` |
| Spanish | Reuters.es / El País / El Financiero: `<company> planta <ciudad>` |
| Portuguese | Valor Econômico: `<company> fábrica <cidade>` |

## Search-tightening operators (when forbidden domains dominate results)

If the top WebSearch results are Wikipedia / social / Medium, re-query with one of:

- `site:{company-domain}` — force the company's own newsroom
- `site:reuters.com OR site:bloomberg.com "{company}" "{city}"`
- `"press release" "{company}" "{city}"`
- The local-language form (table above)
- Destination-country IPA: `site:gob.mx "{company}"` / `site:investindia.gov.in "{company}"`

If after all these passes there is no Tier A or Tier B source: write `fDi Markets (FT)` as the fallback. Never substitute a forbidden URL.

## When to extend this file

Append a new Tier A source (government portal, open database, sector-specific tracker) when you discover one. Log a one-liner in `discoveries.md` so others know. Tier B churn (newsrooms renaming, URLs changing) — update in place.
