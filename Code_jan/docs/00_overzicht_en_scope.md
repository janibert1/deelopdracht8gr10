# 00 Overzicht en Scope

## 1. Context

Deze codebase rekent scheeps-evenwicht en aanvangsstabiliteit door voor drie loadcases uit de opdracht:

- `TransportSchip`
- `KraanSchip`
- `Alleskunner`

De implementatie is class-gebaseerd en combineert:

- invoer uit `antwoordenblad.json`;
- groepsspecifieke JSON/CSV data uit Rhino/Grasshopper exports;
- een vaste rekenworkflow met fysische grenzen en expliciete foutmeldingen.

## 2. Doel van de software

Het doel is niet alleen een numeriek antwoord geven, maar ook een reproduceerbare en controleerbare rekendoorgang bieden. Daarom schrijft de code per run meerdere outputbestanden weg, inclusief foutinformatie per loadcase.

Samengevat levert de software:

1. berekende tankvullingen voor tank 1 en tank 2;
2. stabiliteitsgrootheden (`KB`, `KG`, `BM`, `GM`);
3. balansresiduen voor kracht en momenten;
4. antwoordenblad-output in het gewenste JSON-format.

## 3. Scope: wat zit er wel in

In scope:

- inlezen en valideren van kerninput;
- oplossen van evenwicht binnen tankdiagramgrenzen;
- automatische verwerking van alle drie loadcases in een run;
- wegschrijven van resultaten, statusrapport en grafiek;
- optionele fallback naar voorbeelddata (alleen bij expliciete flag).

## 4. Scope: wat zit er niet in

Out of scope:

- automatische geometrie-optimalisatie;
- ontwerp-iteratie over grote design-spaces;
- uitgebreide structurele sterkteberekeningen;
- databaseopslag of web-API integratie.

## 5. Kernontwerpkeuzes

### 5.1 Interne eenheden zijn hard vastgelegd

De code rekent intern consequent met:

- massa in `kg`;
- lengte in `m`;
- moment in `kgm`.

Deze keuze voorkomt menging van `N` en `kg` in massabalansen.

### 5.2 Gewicht in Newton wordt direct omgezet

Gewichten uit het antwoordenblad die in `N` staan worden direct geconverteerd:

`massa_kg = gewicht_N / 9.81`

Daardoor is de interne rekentrail uniform.

### 5.3 Geen extrapolatie buiten tankdiagrammen

Inverse interpolatie is begrensd. Als een doelwaarde buiten de tabel valt, wordt de loadcase als `infeasible` gemarkeerd in plaats van een niet-fysische waarde te accepteren.

### 5.4 Alle loadcases worden altijd geprobeerd

Een fout in loadcase A stopt loadcases B en C niet direct. Hierdoor blijft de run bruikbaar voor vergelijking en debug.

## 6. Functionele stroom van een run

Per loadcase gebeurt op hoofdlijn:

1. bronconfig opbouwen (data-dir, flags, fallback);
2. `antwoordenblad.json` en `InputData_...json` lezen;
3. ship-object maken met loadcase-specifieke defaults;
4. tank 1 en tank 2 oplossen;
5. stabiliteit en residuen berekenen;
6. resultaat opslaan als `ok` of `infeasible`.

Na alle loadcases:

1. `output/ship_results.json` schrijven;
2. `output/errors.json` schrijven;
3. `output/ship_results_graph.png` schrijven;
4. antwoordenbladen per loadcase schrijven.

## 7. Mappenstructuur (functioneel)

Belangrijkste onderdelen:

- `Main_pelle.py`: entrypoint, CLI, orchestration, output.
- `Ship_pelle.py`: generieke solver voor massa-evenwicht en stabiliteit.
- `Functions_pelle.py`: tankhulpklasse, interpolatie en utilityfuncties.
- `TransportschipClass.py`, `KraanschipClass.py`, `AlleskunnerClass.py`: loadcase wrappers.
- `data/`: invoerbestanden.
- `output/`: run-resultaten.
- `docs/`: deze documentatieset.

## 8. Begrippenlijst

- `COB`: center of buoyancy.
- `COV`: referentiepunt voor momentbalansen in de code.
- `LCG/TCG/VCG`: zwaartepuntlocaties in `x/y/z`.
- `KB`: verticale positie van opwaartse kracht.
- `KG`: verticale positie van totaal zwaartepunt.
- `BM`: metacentric radius inclusief vrije-oppervlakcorrecties.
- `GM`: aanvangsstabiliteit.
- `Residual`: resterende fout in kracht- of momentbalans.

## 9. Aanbevolen startvolgorde

1. Gebruik [01 Snelle Start](./01_snelle_start.md) voor je eerste run.
2. Controleer [03 Data Contracten](./03_data_contracten.md) voordat je data wisselt.
3. Gebruik [04 Loadcase Configuratie](./04_loadcase_configuratie.md) voor teamscenario's.
4. Raadpleeg [09 Foutcatalogus en Debug](./09_foutcatalogus_en_debug.md) bij fouten.
