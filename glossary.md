# NZIPL Glossary

## Acronyms

| Term | Meaning | Context |
|------|---------|---------|
| NZIPL | Net Zero Industrial Policy Lab | Johns Hopkins University |
| OEC | Observatory of Economic Complexity | oec.world, primary data platform |
| CICE | Clean Industrial Capabilities Explorer | Lab's interactive platform (cice.netzeropolicylab.com) |
| RCA | Revealed Comparative Advantage | Core economic complexity metric |
| ECI | Economic Complexity Index | Country/location-level complexity measure |
| PCI | Product Complexity Index | Product-level complexity measure |
| HS6 | Harmonized System 6-digit | Trade product classification (finest level) |
| HS4 | Harmonized System 4-digit | Broader product classification |
| HS2 | Harmonized System 2-digit | Chapter-level product classification |
| BACI | Base pour l'Analyse du Commerce International | Reconciled bilateral trade dataset (CEPII) |
| SCIAN | Sistema de Clasificacion Industrial de America del Norte | Mexican NAICS equivalent, 6-digit industry codes |
| CFE | Comision Federal de Electricidad | Mexico's state utility |
| BIS | Bureau of Indian Standards | Certification body (India) |
| DFI | Development Finance Institution | Actor category in constraint maps |
| DENUE | Directorio Estadistico Nacional de Unidades Economicas | INEGI business registry, establishment counts by municipality |
| ENOE | Encuesta Nacional de Ocupacion y Empleo | Mexico labor survey, used for talent mapping |
| EMS | Electronics Manufacturing Services | Contract manufacturing sector |
| CONEVAL | Consejo Nacional de Evaluacion de la Politica de Desarrollo Social | Mexico's poverty measurement body |
| CONAPO | Consejo Nacional de Poblacion | Mexico population projections |
| SENER | Secretaria de Energia | Mexico's energy ministry |
| SEMARNAT | Secretaria de Medio Ambiente y Recursos Naturales | Mexico's environment ministry |
| STPS | Secretaria del Trabajo y Prevision Social | Mexico's labor ministry |
| CONACYT | Consejo Nacional de Humanidades, Ciencias y Tecnologias | Mexico's science/tech council |
| IMPI | Instituto Mexicano de la Propiedad Industrial | Mexico's patent office |
| BANXICO | Banco de Mexico | Mexico's central bank |
| CNI | Catalogo Nacional de Indicadores | INEGI's national indicator catalog |
| SNIEG | Sistema Nacional de Informacion Estadistica y Geografica | Mexico's national statistical system |
| SHCP | Secretaria de Hacienda y Credito Publico | Mexico's finance ministry |
| PuLP | Python Utility for Linear Programming | Solver used in ECI optimization |
| MST | Minimum Spanning Tree | Network backbone for industry space graphs |
| AMPIP | Asociacion Mexicana de Parques Industriales Privados | Industrial parks registry |
| fDi Markets | Financial Times FDI tracking database | Source for FDI_Combined dataset; project IDs prefixed "FDI" |
| BNEF | BloombergNEF | Green manufacturing project pipeline data |
| IBC | Indonesia Battery Corporation | State-owned Indonesian battery consortium; partner in multiple FDI projects |
| GWh | Gigawatt-hour | Battery plant capacity unit |
| JV | Joint Venture | Shared ownership structure; tracked in FDI columns M-O |

## Internal Terms

| Term | Meaning |
|------|---------|
| Play | A value-chain opportunity selected via economic complexity screening |
| Play Cards | Deliverable: 2-3 per country specifying target activities, inputs, standards, sequencing |
| Constraint Maps | Deliverable: ranked bottleneck maps per play with finance annex |
| Chart Packs | Standardized country-level visualization sets for the CICE platform |
| Cross-country Comparators | Visual products comparing indicators across Brazil, India, Mexico |
| Binding constraint | The specific bottleneck that limits feasibility or timing of a play |
| Gating requirement | A prerequisite that must be met before a play can proceed |
| Finance annex | One-page diagnostic per Constraint Map covering cost of capital, instruments, feasibility |
| Scrollytelling | Scroll-driven narrative visualization format for web publications |
| Three failures taxonomy | Coordination failure (motors), thin territorial base (converters), strategic gap (circuits) |
| Sourcing gradient | Pattern: higher input complexity correlates with wider non-regional sourcing deficit |
| Ubiquity | How many locations produce a given activity. Low ubiquity = more complex |
| Diversity | How many activities a location produces. High diversity = more capable |
| Industry Space | Network graph: nodes = industries, edges = shared capabilities (proximity) |
| Proximity matrix | Co-occurrence matrix measuring how often two industries specialize in the same locations |
| Relatedness | How related a non-present industry is to a location's existing capabilities. Higher = easier to develop |
| Relatedness density | Mean proximity of a play's target products to a location's existing exports. Forward-looking complement to RCA |
| Relative relatedness | Relatedness z-scored across all industries for a given location |
| Probit coefficients | BETA_ENTRY and BETA_EXIT from historical industry entry/exit regressions. Estimate effort in ECI optimization |
| Location quotient (LQ) | Ratio of local to national industry concentration. LQ > 1 = specialization |
| TopoJSON | Compressed geographic data format. Used for municipality boundaries |
| Enclave effect | High-ECI location with persistent poverty due to concentrated industry that inflates complexity without distributing welfare |
| Capability dividend | Above-median ECI + below-median poverty. Where productive accumulation has translated into lower deprivation |
