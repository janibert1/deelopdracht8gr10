# 10 Validatie, Regressie en Teststrategie

## 1. Testdoelen

Deze codebase moet aantoonbaar voldoen op drie assen:

- numerieke consistentie van de kernberekening;
- robuust gedrag bij onvolledige of ongeldige data;
- stabiele outputstructuur voor downstream gebruik.

## 2. Aanbevolen testlagen

### 2.1 Smoke test (altijd)

Doel:

- check dat de volledige run succesvol produceert.

Commando:

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json
```

Controle:

1. alle outputbestanden bestaan;
2. elke loadcase heeft status;
3. JSON's zijn parsebaar.

### 2.2 Baseline regressietest

Doel:

- detecteer ongewenste numerieke drift op bekende referentie.

Commando:

```powershell
python regressie_check_gr98_v1.py
```

Referentiechecks:

- `tank1_percentage` rond `59.322`
- `tank2_percentage` rond `85.1747`
- `GM` rond `1.0585`

### 2.3 Data-validatietests

Doel:

- aantonen dat verkeerde data expliciet faalt.

Voorbeelden:

1. verwijder tijdelijk `MainShipParticulars_...json`;
2. zet `Buoyant_Volume_m3` op `0`;
3. verwijder een verplichte CSV-kolom.

Verwachting:

- duidelijke `DataValidatieFout` en geen stille fallback zonder flag.

### 2.4 Infeasible tests

Doel:

- check gecontroleerd gedrag bij fysisch onhaalbare cases.

Voorbeelden:

1. extreem hoge lading;
2. onrealistische tank3-start;
3. combinatie met strikte residucheck.

Verwachting:

- status `infeasible` met duidelijke fouttekst in output.

### 2.5 Residu- en gevoeligheidstest

Doel:

- inzicht in stabiliteit van oplossing onder kleine inputvariaties.

Aanpak:

1. run standaard;
2. varieer een parameter licht (bijvoorbeeld huiddikte);
3. vergelijk verandering in tankpercentages en GM.

## 3. Acceptatiecriteria voor teamrelease

Minimaal akkoord als:

1. `ship_results.json` parsebaar is;
2. `errors.json` aanwezig en consistent is;
3. antwoordenbladen per loadcase zijn aangemaakt;
4. geen loadcase stil verdwijnt uit output;
5. regressiecheck slaagt of afwijking verklaard is.

## 4. Praktische commandoreeks voor releasecheck

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json
python regressie_check_gr98_v1.py
```

Aanvullend (optioneel): run met strict residuen.

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json --strict-residuen
```

## 5. CI-aanbevelingen

In een eenvoudige CI-pipeline:

1. dependencies installeren;
2. smoke run uitvoeren;
3. regressie script uitvoeren;
4. outputbestanden op aanwezigheid controleren.

## 6. Handmatige reviewchecklist

1. Kloppen bronpaden per loadcase?
2. Zijn units consequent (`N` extern, `kg` intern)?
3. Zijn tankpercentages fysisch plausibel?
4. Is GM-trend logisch tussen loadcases?
5. Zijn foutmeldingen expliciet genoeg voor gebruikers?

## 7. Wanneer tolerantie aanpassen

Pas toleranties alleen aan als:

- de modelwijziging inhoudelijk verklaarbaar is;
- er een gedocumenteerde reden is in commit of changelog;
- update is opgenomen in docs en regressie-aanpak.
