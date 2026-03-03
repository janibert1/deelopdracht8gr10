# 00 Overzicht en Scope

## 1. Context

Deze codebase rekent scheeps-evenwicht en aanvangsstabiliteit door voor drie verplichte loadcases uit de opdracht:

- `TransportSchip`
- `KraanSchip`
- `Alleskunner`

De code is class-gebaseerd opgezet en gebruikt gestructureerde input uit CSV/JSON bestanden van Rhino/Grasshopper plus het antwoordenblad-format.

## 2. Wat de code nu doet

1. Leest inputdata per loadcase.
2. Bouwt massa-overzicht op uit:
   - staalplaten en schotten;
   - kraancomponenten;
   - gehesen TP;
   - deklading TP's.
3. Lost tankpercentages op voor evenwicht binnen begrensde tankdiagrammen.
4. Berekent stabiliteitsgrootheden (`KB`, `KG`, `BM`, `GM`).
5. Schrijft outputbestanden:
   - `output/ship_results.json`
   - `output/errors.json`
   - `output/ship_results_graph.png`
   - `output/antwoordenblad_*.json`

## 3. Wat de code expliciet niet doet

- Geen automatische geometrie-optimalisatie.
- Geen automatische design-space search.
- Geen volledige deelopdracht 9 spanningsberekeningen.
- Geen externe database-opslag.

## 4. Ontwerpkeuzes

### 4.1 Interne eenheden

Interne rekeneenheden zijn consequent:

- massa: `kg`
- lengte: `m`
- moment: `kgm`

### 4.2 Invoer in Newton

Velden in antwoordenbladen die als gewicht in `N` zijn opgegeven worden direct omgerekend naar `kg` met:

`massa_kg = gewicht_N / 9.81`

### 4.3 Geen extrapolatie buiten tankdiagram

Interpolatie voor tank-oplossing is begrensd. Als een doelwaarde buiten bereik valt, wordt de loadcase `infeasible` in plaats van een fysisch ongeldige waarde te genereren.

## 5. Mappenstructuur

Belangrijkste onderdelen:

- `Main_pelle.py`: entrypoint, orchestration, output schrijven.
- `Ship_pelle.py`: generieke Ship-berekening.
- `Functions_pelle.py`: tank-, interpolatie- en hulpfuncties.
- `TransportschipClass.py`, `KraanschipClass.py`, `AlleskunnerClass.py`: loadcase-specifieke wrappers.
- `data/`: invoerbestanden.
- `output/`: resultaatbestanden.
- `docs/`: deze documentatie.

## 6. Begrippenlijst

- `COB`: center of buoyancy.
- `COV`: referentiepunt gebruikt voor momentbalans.
- `LCG/TCG/VCG`: zwaartepuntlocaties langs lengte/dwars/verticaal.
- `KB`: verticale locatie van opwaartse kracht.
- `KG`: verticale locatie van totaal zwaartepunt.
- `BM`: metacentric radius inclusief vrije-oppervlakcorrectie.
- `GM`: aanvangsstabiliteit.
- `Residual`: resterende fout in kracht/momentbalans na oplossen.

## 7. Aanbevolen workflow

1. Start met [01 Snelle Start](./01_snelle_start.md).
2. Check inputregels in [03 Data Contracten](./03_data_contracten.md).
3. Stel per-loadcase config in via [04 Loadcase Configuratie](./04_loadcase_configuratie.md).
4. Gebruik [09 Foutcatalogus en Debug](./09_foutcatalogus_en_debug.md) bij problemen.
