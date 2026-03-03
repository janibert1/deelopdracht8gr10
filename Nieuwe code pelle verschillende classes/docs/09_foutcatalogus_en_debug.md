# 09 Foutcatalogus en Debug

## 1. DataValidatieFout

### 1.1 `Template ontbreekt ... antwoordenblad.json`

Oorzaak:

- datamap bevat geen antwoordenblad.

Actie:

1. plaats `antwoordenblad.json` in de juiste datamap;
2. controleer pad in `--data-dir` of `--loadcase-config`.

### 1.2 `InputData ontbreekt ...`

Oorzaak:

- file_id uit template matcht niet met aanwezige InputData file.

Actie:

- hernoem bestand of corrigeer `Groepsversie` in antwoordenblad.

### 1.3 `Datamap ongeldig ... Buoyant_Volume_m3`

Oorzaak:

- hydrostatische export onvolledig (`Buoyant_Volume_m3 <= 0`).

Actie:

- exporteer opnieuw uit GH;
- of gebruik fallback bewust.

## 2. InfeasibleLoadCaseError

### 2.1 `Doelwaarde buiten bereik bij 'tank massa->percentage'`

Oorzaak:

- required tankmassa buiten tabelbereik.

Actie:

1. verlaag totale neerwaartse massa (bijv. huiddikte/lading);
2. verhoog bestaande ballastpositie/instellingen;
3. gebruik loadcase-specifieke input in `loadcase_config`.

### 2.2 `Vullingspercentage buiten [0,100]`

Oorzaak:

- berekende oplossing fysisch ongeldig.

Actie:

- inspecteer tM/mass balances en invoerunits.

## 3. Runtime warnings

### 3.1 `tank2_is_movable=False ... opgelost lcg valt buiten bereik`

Betekenis:

- evenwicht vraagt andere tank2-locatie, maar model houdt vaste tank2-locatie aan.

Actie:

- overweeg `--tank2-movable` voor analyse;
- of pas loadcase-invoer aan.

### 3.2 `Residuwaarschuwing ...`

Betekenis:

- oplossingsresidu boven tolerantie.

Actie:

1. run met `--strict-residuen` om hard-failing gedrag te forceren tijdens debug;
2. inspecteer massa- en momenttermen per component.

## 4. Debugflow in 7 stappen

1. Check `errors.json`.
2. Check `ship_results.json` -> `scenarios`.
3. Verifieer units (`N` vs `kg`).
4. Verifieer tank3 startpercentage.
5. Run met 1 loadcase en simpele input.
6. Vergelijk met referentiewaarden.
7. Zet pas daarna volledige set aan.
