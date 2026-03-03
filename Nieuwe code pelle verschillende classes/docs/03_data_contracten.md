# 03 Data Contracten

## 1. Doel

Deze pagina beschrijft exact welke inputbestanden nodig zijn, welke velden verplicht zijn, en hoe de code die gebruikt.

## 2. Verplichte bestanden per datamap

Minimaal:

- `antwoordenblad.json`
- `InputData_Gr<groep>_V<versie>.<sub>.json`
- `MainShipParticulars_Gr<groep>_V<versie>.<sub>.json`
- `Tank1_Diagram_Volume_...csv`
- `Tank2_Diagram_Volume_...csv`
- `Tank3_Diagram_Volume_...csv`
- `Tank1_Diagram_Waterplane_...csv`
- `Tank2_Diagram_Waterplane_...csv`
- `Tank3_Diagram_Waterplane_...csv`
- `HullAreaData_...csv`
- `TankBHD_Data_...csv`

## 3. Kritieke JSON-velden

### 3.1 `antwoordenblad.json`

Gebruikte secties:

- `Project_info`
- `Constructie`
- `Materiaal`
- `Kraan_beladingsconditie`
- `Zwaartepunten_kraanlast`
- `Deklast_transition_pieces`
- `Lading_locaties`

Belangrijke keys:

- `Huid_en_dek_dikte #[mm]`
- `Soortelijk_gewicht_staal #[kg/m3]`
- `Soortelijk_gewicht_zeewater #[kg/m3]`
- `SWLmax_kraan #[N]`
- `Gewicht_per_TP #[N]`
- `Gewicht_per_transition_piece #[N]`

### 3.2 `InputData_...json`

Verplicht:

- `INPUT DATA` blok
- `Filling_Tank_3_%h3`

## 4. Kritieke CSV-kolommen

### 4.1 Tank volume diagram

Vereiste kolommen:

- ` Tankfilling [% of h_tank]`
- ` Tankvolume [m3]`
- ` lcg [m]`
- ` tcg [m]`
- ` vcg [m]`

### 4.2 Tank waterplane diagram

Vereiste kolom:

- ` Inertia_x [m4]`

### 4.3 Hull area data

Vereiste kolommen:

- ` Area [m2]`
- ` lca [m]`
- ` tca [m]`
- ` vca [m]`

### 4.4 Tank bulkhead data

Vereiste kolommen:

- `BHD Area [m2]`
- ` lcg [m]`
- ` tcg [m]`
- ` vcg [m]`

## 5. Validatievoorwaarden

Data-map wordt als bruikbaar gezien als:

1. `MainShipParticulars` bestaat.
2. `Buoyant_Volume_m3 > 0`.
3. `COB_m` en `COV_Total_m` lijsten zijn met minimaal 3 componenten.

## 6. Datatypes en units

- percentages: `float`, [0, 100]
- lengtes: `float`, meter
- massa: `float`, kg (intern)
- gewicht uit antwoordenblad: `float`, Newton

## 7. Foutgedrag

- Ontbrekend bestand -> `DataValidatieFout`.
- Ongeldige structuur -> `DataValidatieFout`.
- Doelwaarde buiten tankrange -> `InfeasibleLoadCaseError`.

## 8. Aanbeveling voor teamgebruik

Gebruik per loadcase een eigen datamap met:

- eigen `antwoordenblad.json`
- eigen `InputData_...json`
- bijbehorende hydro/tank CSV/JSON

en koppel die via `loadcase_config.json`.
