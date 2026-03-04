# 03 Data Contracten

## 1. Doel

Deze pagina beschrijft welke inputstructuur de code verwacht, welke velden kritisch zijn en welke validaties hard afgedwongen worden.

Belangrijk: de code accepteert alleen bestandsnamen met de verwachte patronen op basis van `file_id`.

## 2. Bestandsset per datamap

Minimaal nodig in elke gebruikte `data_dir`:

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

## 3. Naam- en versieregels

`file_id` wordt afgeleid uit:

- `Project_info -> Groepsversie #[naam/nummer]` in `antwoordenblad.json`.

Parsergedrag:

1. neemt tekst voor een eventuele underscore;
2. splitst op `.`;
3. verwacht minimaal drie numerieke delen.

Voorbeeld:

- `98.1.0` -> `file_id = [98, 1, 0]`
- `98.1.0_Alleskunner` -> ook `file_id = [98, 1, 0]`

## 4. Kritieke JSON-velden

### 4.1 `antwoordenblad.json`

Vereiste secties die door de code gebruikt worden:

- `Project_info`
- `Constructie`
- `Materiaal`
- `Kraan_beladingsconditie`
- `Zwaartepunten_kraanlast`
- `Deklast_transition_pieces`
- `Lading_locaties` (optioneel per TP, met fallback)

Belangrijke keys:

- `Huid_en_dek_dikte #[mm]`
- `Soortelijk_gewicht_staal #[kg/m3]`
- `Soortelijk_gewicht_zeewater #[kg/m3]`
- `SWLmax_kraan #[N]`
- `Gewicht_per_TP #[N]`
- `Gewicht_per_transition_piece #[N]`

### 4.2 `InputData_...json`

Vereist:

- object `INPUT DATA`
- key `Filling_Tank_3_%h3`

## 5. Kritieke CSV-kolommen

### 5.1 Tank volume diagram (`Tank*_Diagram_Volume_...csv`)

Verplicht:

- ` Tankfilling [% of h_tank]`
- ` Tankvolume [m3]`
- ` lcg [m]`
- ` tcg [m]`
- ` vcg [m]`

### 5.2 Tank waterplane diagram (`Tank*_Diagram_Waterplane_...csv`)

Verplicht:

- ` Inertia_x [m4]`

### 5.3 Hull area data (`HullAreaData_...csv`)

Verplicht:

- ` Area [m2]`
- ` lca [m]`
- ` tca [m]`
- ` vca [m]`

### 5.4 Bulkhead data (`TankBHD_Data_...csv`)

Verplicht:

- `BHD Area [m2]`
- ` lcg [m]`
- ` tcg [m]`
- ` vcg [m]`

## 6. Validatiestappen in de code

### 6.1 Vroege datamap-check (`Ship._is_usable_data_dir`)

Controleert minimaal:

1. bestaan van `MainShipParticulars_...json`;
2. `Buoyant_Volume_m3 > 0`;
3. `COB_m` en `COV_Total_m` bestaan als lijsten met minimaal 3 waarden.

Als dit niet klopt:

- zonder fallback -> `DataValidatieFout`;
- met fallback -> poging op fallback map.

### 6.2 Detailchecks tijdens rekenen

Daarna volgen impliciete detailchecks via file-open en kolomtoegang. Ontbrekende bestanden of kolommen geven expliciete fouten.

## 7. Datatypes en units

Aanbevolen types:

- percentages: `float` in `[0, 100]`
- lengtes: `float` in meter
- dichtheden: `float` in `kg/m3`
- massa intern: `kg`
- gewicht in antwoordenblad: `N`

Belangrijk: gewichten uit antwoordenblad worden direct naar `kg` omgezet.

## 8. Foutgedrag bij contractschending

- ontbrekend of ongeldig inputbestand -> `DataValidatieFout`;
- doelwaarde buiten tankdiagram -> `InfeasibleLoadCaseError`;
- tankpercentage buiten `[0,100]` -> `InfeasibleLoadCaseError`.

## 9. Praktische pre-flight checklist

Gebruik deze checklist voordat je rekent:

1. klopt `Groepsversie` met bestandsnamen;
2. staat `antwoordenblad.json` in elke gebruikte `data_dir`;
3. bestaat `MainShipParticulars_...json` en is `Buoyant_Volume_m3 > 0`;
4. bestaan alle tankdiagram-CSV's;
5. klopt `Filling_Tank_3_%h3` in `InputData_...json`.

## 10. Aanbeveling voor teamgebruik

Gebruik per loadcase een aparte datamap met eigen `antwoordenblad.json` en bijbehorende exportbestanden. Koppel die mappen via `loadcase_config.json` zodat verschillen tussen scheepstypen expliciet en traceerbaar blijven.
