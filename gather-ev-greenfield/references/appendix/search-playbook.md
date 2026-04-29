# Search playbook

Query templates by country and source type. Copy-paste into your search engine of choice (prefer the country's native engine when it exists — Naver for Korea, Baidu for China, Google.de for Germany, etc.).

## Query primitives

Every search starts from one of these primitives, combined with quotation marks for the company name:

1. `"<Company>" <project-type> <city> <country>`
2. `"<Company>" <project-type> factory site:<company-domain>`
3. `"<Company>" <project-type> "<city>" -site:wikipedia.org`
4. `"<Company>" <project-type> permit <state/province>`
5. `"<Company>" <project-type> groundbreaking <year>`
6. `"<Company>" <project-type> announcement <year>` (limit to a year to filter stale coverage)

Project-type keywords: `battery`, `cell`, `gigafactory`, `EV`, `cathode`, `anode`, `separator`, `electrolyte`, `recycling`, `assembly`, `motor`, `inverter`, `charger`.

## Country playbooks

### United States

Start with Atlas EV Hub. Then:

```
site:energy.gov "<Company>" "<State>"
site:selectusa.gov "<Company>"
site:<state>.gov "<Company>" tax incentive
"<Company>" "<City>" permit application
```

Key state agency domains:
- `gadc.georgia.gov` (Georgia)
- `michiganbusiness.org` (Michigan)
- `tnecd.com` (Tennessee)
- `texaswideopenforbusiness.com` (Texas)
- `ided.state.ia.us` (Iowa)
- `thinkkentucky.com` (Kentucky)

### Mexico

Start with `nzipl_bnef_projects.json` — 37 Mexican records already in hand. Then:

```
site:gob.mx/se "<Empresa>"
site:gob.mx "<Ciudad>" inversión
"<Company>" planta <ciudad> México
"<Empresa>" "<Estado>" nave industrial
```

The Secretaría de Economía publishes press releases on `gob.mx/se/prensa`. State-level: Nuevo León's `nl.gob.mx`, Coahuila's `coahuila.gob.mx`. Industrial parks: AMPIP `ampip.org.mx`.

### Germany

```
site:bmwk.de "<Company>"
site:gtai.de "<Company>"
"<Company>" Werk "<Stadt>"
"<Company>" Batteriewerk OR Zellfertigung "<Stadt>"
site:brandenburg.de OR site:sachsen.de OR site:nrw.de "<Company>"
```

Tier A German sources: BMWK, GTAI (Germany Trade & Invest), state economy ministries. Tier B: Handelsblatt, Süddeutsche, Tagesschau, Electrive.de, Battery-News.de.

### Hungary

```
site:kormany.hu "<Company>"
site:hipa.hu "<Company>"
"<Company>" gyár "<Város>"
```

HIPA (Hungarian Investment Promotion Agency) is the authoritative source. CATL Debrecen, BYD Szeged, Samsung SDI Göd all appear there first.

### Poland

```
site:paih.gov.pl "<Company>"
"<Company>" fabryka "<Miasto>"
"<Company>" Wrocław OR Gliwice OR Poznań
```

PAIH (Polish Investment and Trade Agency) is the national source.

### Spain

```
site:investinspain.org "<Company>"
"<Company>" fábrica "<Ciudad>"
"<Company>" planta baterías "<Región autónoma>"
```

### France

```
site:businessfrance.fr "<Company>"
"<Company>" usine "<Ville>"
"<Company>" gigafactory "<Région>"
```

### Turkey

```
site:invest.gov.tr "<Company>"
"<Company>" fabrika "<Şehir>"
"<Company>" elektrikli araç tesisi
```

### South Korea

Outbound investments (Korean firms building overseas) — always check Korean-language sources first.

```
site:motie.go.kr "<Company>" "<Country>"
site:investkorea.org "<Company>"
"<Company-hangul>" 배터리 공장
"<Company-hangul>" 셀 공장 "<City-transliteration>"
```

The Elec (`thelec.net`) is the best English-language source. Names to translate: LG에너지솔루션 (LG Energy Solution), 삼성SDI (Samsung SDI), SK온 (SK On), 포스코퓨처엠 (POSCO Future M), 에코프로 (Ecopro).

### Japan

```
site:meti.go.jp "<Company>"
site:jetro.go.jp "<Company>"
"<Company-kanji>" 工場 "<Prefecture>"
"<Company-kanji>" EV 工場
```

Nikkei Asia is the English source. Local press in Japanese: NHK, Asahi, Nikkei Japan. Companies to translate: パナソニック (Panasonic), トヨタ (Toyota), ホンダ (Honda), 日産 (Nissan), デンソー (Denso), AESC.

### China

```
site:miit.gov.cn "<Company-hanzi>"
site:ndrc.gov.cn "<Company-hanzi>"
"<Company-hanzi>" 工厂 "<City-hanzi>"
"<Company-hanzi>" 电池 新基地
```

CnEVPost is the best English-language aggregator. Transliteration traps: 比亚迪 (BYD), 宁德时代 (CATL), 亿纬锂能 (EVE Energy), 国轩高科 (Gotion), 蜂巢能源 (SVOLT), 孚能科技 (Farasis).

### India

```
site:investindia.gov.in "<Company>"
site:heavyindustries.gov.in "<Company>"
"<Company>" plant "<City>" battery OR EV
"<Company>" gigafactory India
```

PLI (Production Linked Incentive) scheme notifications on `heavyindustries.gov.in` are the authoritative source for Indian battery investments. Key names: Tata, Ola Electric, Mahindra, Ather, Reliance, Amara Raja, Exide.

### Brazil

```
site:gov.br/mdic "<Company>"
site:apexbrasil.com.br "<Company>"
"<Company>" fábrica "<Cidade>"
"<Company>" planta "<Estado>"
```

BYD São Paulo, Great Wall Motor Iracemápolis, Stellantis Betim. Valor Econômico and Automotive Business are the best trade press.

### Canada

```
site:ised-isde.canada.ca "<Company>"
site:invest.gc.ca "<Company>"
"<Company>" "<City>" battery plant
"<Company>" strategic innovation fund
```

Federal Strategic Innovation Fund disclosures are authoritative. Key locations: Windsor (Stellantis–LGES NextStar), Bécancour (Quebec battery cluster).

## Query anti-patterns

Avoid these:

- **Date-bounded "<Company> 2024"** alone — too noisy. Pair with project-type and geography.
- **Generic "battery plant <country>"** — returns aggregator listicles. Start with the company.
- **Relying on Wikipedia infobox numbers** — they lag real announcements by months and often cite the largest announced figure, not the current one.
- **Using the first result uncritically** — the first hit is usually a press release repackaged by a wire service. Check the original company domain.

## Dead-end recovery

When a search returns nothing useful:

1. **Switch language.** If the company is Asian or European, try the native-language query.
2. **Narrow on permits.** `"<Company>" "<State/Province>" "permit" OR "incentive" OR "grant"`.
3. **Widen to the parent.** If the facility operator is a subsidiary, search the parent company.
4. **Check supplier announcements.** Equipment vendors (Manz, Wuxi Lead, Schuler) announce plant orders. These often confirm a plant exists even when the operator hasn't publicized it.
5. **Check construction contractor announcements.** Bechtel, M+W Group, Exyte regularly announce battery-plant contracts.
6. **Check city-level economic development news.** "Site selection" trade press (areadevelopment.com, businessfacilities.com) covers announcements the company doesn't heavily promote.
7. **Last resort: log the candidate at Tier 3** with the single source and revisit in 30 days.

## Logging searches

When you find a genuinely new source type or a useful query pattern — especially a local-language query that unlocked a difficult record — append it to `discoveries.md`. The playbook gets smarter over time. Significant patterns get promoted into this file via PR.
