# 11 Assignment Traceability MT1466

## 1. Doel

Deze pagina koppelt assignmentverwachtingen aan concrete implementatiedelen en outputartefacten.

Focus:

- aantonen welke eis door welk codeonderdeel wordt afgedekt;
- zichtbaar maken waar grenzen of aannames liggen.

## 2. Traceability matrix

| Assignmentthema | Implementatie | Bewijs in output |
|---|---|---|
| Modulaire code-opzet | `Main_pelle.py`, `Ship_pelle.py`, `Functions_pelle.py`, loadcase classes | Structuur in repository |
| Gebruik van classes | `Ship` + drie subclasses | Afzonderlijke resultaten per loadcase |
| Drie scheepstypen doorrekenen | `bouw_loadcases(...)` en runloop in `main()` | `results.TransportSchip/KraanSchip/Alleskunner` |
| Evenwichtsberekeningen | `_calculate_mass_balance()` in `Ship` | tankpercentages + residuen |
| Stabiliteit (`GM`) | `_calculate_stability()` in `Ship` | `GM` in `ship_results.json` en antwoordenblad |
| Foutafhandeling | `DataValidatieFout`, `InfeasibleLoadCaseError` | `status` + `error` in output |
| Resultaatrapportage | write-functies in `Main_pelle.py` | `ship_results.json`, `errors.json`, grafiek, antwoordenbladen |

## 3. Structuur- en programmeereisen

### 3.1 Scheiding van verantwoordelijkheden

- orchestration en I/O in `Main_pelle.py`;
- modelberekening in `Ship_pelle.py`;
- dataspecifieke berekenhulpen in `Functions_pelle.py`.

### 3.2 Herbruikbaarheid

Loadcase-subclasses zetten alleen case-defaults. De kernsolver blijft een generieke `Ship`-implementatie.

### 3.3 Transparante foutmelding

Fouten worden niet stil genegeerd. Elke case krijgt expliciet `ok` of `infeasible` met fouttekst.

## 4. Inhoudelijke dekking

### 4.1 Kracht- en momentbalans

Afgedekt via:

- oplossing tank1/tank2;
- residuvelden in output (`force`, `long`, `trans`).

### 4.2 Stabiliteit

Afgedekt via:

- berekening `KB`, `KG`, `BM`, `GM`;
- terugkoppeling in JSON en antwoordenblad.

### 4.3 Rapportage richting assignmentformat

Afgedekt via:

- `antwoordenblad_<LoadCase>.json`;
- default `antwoordenblad.json`.

## 5. Bekende grenzen

Deze traceability zegt iets over softwaredekking, niet automatisch over de kwaliteit van elke externe dataset.

Concreet:

- onjuiste exports kunnen nog steeds infeasible resultaten geven;
- fallbackgedrag moet bewust geactiveerd worden;
- regressiecheck is gericht op een vaste baselinecase.

## 6. Gebruik in beoordeling

Voor review of inlevercontrole:

1. verifieer matrix hierboven tegen actuele code;
2. controleer outputartefacten van een testrun;
3. leg afwijkingen vast in [12 Bijdragen en Onderhoud](./12_bijdragen_en_onderhoud.md).
