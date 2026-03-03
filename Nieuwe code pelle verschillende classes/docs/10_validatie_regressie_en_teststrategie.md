# 10 Validatie, Regressie en Teststrategie

## 1. Testdoelen

- numerieke juistheid van kernformules;
- robuust foutgedrag bij slechte input;
- consistentie van outputstructuur.

## 2. Testniveaus

### 2.1 Smoke test

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json
```

Check:

- alle outputbestanden bestaan;
- alle loadcases hebben status (`ok`/`infeasible`).

### 2.2 Regressietest (baseline)

```powershell
python regressie_check_gr98_v1.py
```

Checkt vaste referentie voor alleskunner.

### 2.3 Data-validatie test

- verwijder tijdelijk een required bestand;
- verwacht expliciete `DataValidatieFout`.

### 2.4 Infeasible test

- zet extreem lage tank3 of hoge lading;
- verwacht `status: infeasible` en duidelijke fouttekst.

## 3. Acceptatiecriteria voor teamrelease

1. `ship_results.json` parsebaar.
2. `errors.json` aanwezig en consistent.
3. antwoordenbladen per loadcase aanwezig.
4. geen stille drop van loadcases.
5. unitconversies zichtbaar in scenario-output.

## 4. Aanbevolen CI-checks

- run smoke command;
- run regressie_check;
- check aanwezigheid output files;
- optioneel: JSON schema validation.

## 5. Handmatige review checklist

1. Kloppen bronpaden per loadcase?
2. Kloppen huiddiktes per loadcase?
3. Klopt kraanhoek/pivot per loadcase?
4. Zijn tankpercentages fysisch plausibel?
5. Is GM trend logisch tussen loadcases?
