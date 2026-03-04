# 09 Foutcatalogus en Debug

## 1. Doel

Deze pagina helpt je fouten systematisch te herkennen en gericht op te lossen. De focus ligt op de drie hoofdgroepen:

- `DataValidatieFout`
- `InfeasibleLoadCaseError`
- waarschuwingen en regressie/assertion problemen

## 2. `DataValidatieFout`

### 2.1 `Template ontbreekt ... antwoordenblad.json`

Waarschijnlijke oorzaak:

- `antwoordenblad.json` ontbreekt in de actieve `data_dir`.

Actie:

1. plaats bestand in de juiste datamap;
2. controleer `--data-dir` of `loadcase_config`.

### 2.2 `InputData ontbreekt ...`

Waarschijnlijke oorzaak:

- `file_id` uit `Groepsversie` matcht niet met aanwezige `InputData` bestandsnaam.

Actie:

1. controleer `Project_info -> Groepsversie`;
2. controleer naam `InputData_Gr.._V..json`.

### 2.3 `Datamap ongeldig ... Buoyant_Volume_m3`

Waarschijnlijke oorzaak:

- hoofd-hydrostatische data is onvolledig of bevat `Buoyant_Volume_m3 <= 0`.

Actie:

1. herstel/regenereer `MainShipParticulars` export;
2. of zet bewust `--allow-fallback` aan.

## 3. `InfeasibleLoadCaseError`

### 3.1 `Doelwaarde buiten bereik bij 'tank massa->percentage'`

Betekenis:

- vereiste tankmassa ligt buiten de tabellimieten.

Actie:

1. verlaag neerwaartse massa (bijvoorbeeld lading of dikte);
2. herzie tank3-startpercentage;
3. gebruik loadcase-specifieke data.

### 3.2 `Doelwaarde buiten bereik bij 'tank tM->percentage'`

Betekenis:

- dwarsmoment kan met tank1 binnen tabelgrenzen niet gesloten worden.

Actie:

1. controleer TCG's en kraan-/ladingposities;
2. controleer inputunits;
3. test met versimpelde loadcase.

### 3.3 `Vullingspercentage buiten [0,100]`

Betekenis:

- eindoplossing is fysisch ongeldig.

Actie:

1. inspecteer scenario-invoer;
2. controleer of dataset bij de juiste loadcase hoort.

### 3.4 `Berekende tank2_lcg valt buiten geometrisch bereik`

Betekenis:

- alleen relevant als `tank2_is_movable=true`;
- benodigde langsscheepse positie valt buiten wat de tankgeometrie toelaat.

Actie:

1. wijzig inputmassa's of momenten;
2. laat tank2 vast (`tank2_is_movable=false`) als analysevariant.

## 4. Runtime waarschuwingen

### 4.1 `tank2_is_movable=False ... opgelost lcg valt buiten bereik`

Betekenis:

- solver berekent een gewenste `tank2_lcg` buiten bereik, maar past die niet toe omdat tank2 vast staat.

Interpretatie:

- run kan `ok` zijn, maar momentresiduen kunnen groter zijn.

### 4.2 `Residuwaarschuwing ...`

Betekenis:

- residu groter dan tolerantie, maar geen hard fail zolang `strict_residuen=false`.

Actie:

1. run opnieuw met `--strict-residuen`;
2. analyseer componentmomenten.

## 5. Regressie/assertion fout

Melding:

- `Regressiecheck Gr98 V1.0 faalt ...`

Betekenis:

- Alleskunnerresultaat wijkt te veel af van referentiedeltas.

Actie:

1. controleer of onbedoeld defaults of data zijn aangepast;
2. vergelijk `ship_results.json` met vorige baseline;
3. update tolerantie alleen met inhoudelijke motivatie.

## 6. Debugflow in 8 stappen

1. Lees `output/errors.json`.
2. Controleer gebruikte paden in `ship_results.json -> scenarios`.
3. Verifieer units (`N` versus `kg`).
4. Check tank3-startpercentage en ladinginstellingen.
5. Run met een enkele eenvoudige case.
6. Vergelijk met referentie-output.
7. Zet `--strict-residuen` aan voor harde checks.
8. Pas daarna pas volledige configuratie toe.

## 7. Snelle triagetabel

| Symptoom | Waarschijnlijke oorzaak | Eerste actie |
|---|---|---|
| Bestand ontbreekt | Verkeerde data_dir of bestandsnaam | Controleer pad en naamconventie |
| Tank buiten bereik | Inputmassa/moment te groot | Check lading, TP's, tank3 |
| Grote residuen | Inconsistente input of vaste tank2 | Test met strict residuen en movable tank2 |
| Regressiefout | Gedragswijziging of andere data | Vergelijk met eerdere baseline |

## 8. Wanneer hard stoppen verstandig is

Stop de analyse en fix eerst data/code als:

- meerdere loadcases tegelijk infeasible worden;
- `DataValidatieFout` al in basisinvoer zit;
- residuen structureel groot blijven ondanks plausibele input.
