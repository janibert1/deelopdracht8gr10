# 07 Code Referentie Modules

## 1. Architectuuroverzicht

De code is opgesplitst in orchestration, rekenkern en loadcase-wrappers:

- `Main_pelle.py`: orchestratie, CLI, runloop, output.
- `Ship_pelle.py`: generieke rekenworkflow.
- `Functions_pelle.py`: tankhulpklasse en utilityfuncties.
- `TransportschipClass.py`, `KraanschipClass.py`, `AlleskunnerClass.py`: dunne subklassen met case-defaults.

## 2. `Main_pelle.py`

### Verantwoordelijkheden

- argumenten parsen (`parse_args`);
- bronconfigs per loadcase opbouwen (`bouw_loadcase_bron_configs`);
- basisscenario uit data lezen (`bouw_basis_scenario_config`);
- juiste shipklasse instantiëren (`maak_ship_object`);
- resultaten en fouten structureren;
- outputbestanden schrijven;
- optionele regressiecheck uitvoeren.

### Belangrijke dataclasses

- `BasisScenarioConfig`
- `LoadCaseConfig`
- `LoadCaseBronConfig`

Deze maken het gedrag expliciet en serialiseerbaar naar output.

### Outputhelpers

- `write_results_json(...)`
- `write_errors_json(...)`
- `write_results_graph(...)`
- `schrijf_antwoordenbladen(...)`

## 3. `Ship_pelle.py`

### Klasse `Ship`

`Ship.__init__` voert direct de volledige pipeline uit:

1. `_resolve_data_dir`
2. `_load_main_data`
3. `_read_main_dimensions`
4. `_build_tanks`
5. `_calculate_mass_balance`
6. `_calculate_stability`
7. `_validate_solution`

### Belangrijke attributen

- invoer/bron: `data_dir`, `allow_fallback`, `tank2_is_movable`, `strict_residuen`
- tussenresultaten: `dry_data`, `tank_data`, `ship_data`
- outputs: `tank1_percentage`, `tank2_percentage`, `KB`, `KG`, `BM`, `GM`
- kwaliteitsmaten: `force_residual_kg`, `long_m_residual_kgm`, `trans_m_residual_kgm`

### Foutpaden

- dataproblemen -> `DataValidatieFout`
- fysische/numerieke onhaalbaarheid -> `InfeasibleLoadCaseError`
- residuoverschrijding bij strict mode -> `InfeasibleLoadCaseError`

## 4. `Functions_pelle.py`

### Exceptions

- `DataValidatieFout`
- `InfeasibleLoadCaseError`

### Klasse `Tank`

Belangrijkste methodes:

- `percentage_filled(percentage)`
- `percentage_uit_tM(target_tM)`
- `percentage_uit_massa(target_mass)`

`Tank` leest volume- en waterplane-tabellen, berekent afgeleiden (`mass`, `lM`, `tM`, `GG`) en ondersteunt begrensde inverse interpolatie.

### Utilityfuncties

- `deck(...)`: massa/zwaartepunten van kraan + deklast.
- `plates(...)`: huid- en schottenmassa uit oppervlakken en diktes.
- `matrix_add(...)`: concateneert componentmatrices.
- `ZCG(...)`: gecombineerde verticale zwaartepuntsberekening.

## 5. Loadcase-subclasses

### `TransportschipClass.py`

- forceert geen kraan;
- gebruikt alleen dekladingcomponenten.

### `KraanschipClass.py`

- forceert deklading op nul;
- gebruikt kraan + hook load.

### `AlleskunnerClass.py`

- combineert kraanbelasting en deklading.

## 6. Regressie script

`regressie_check_gr98_v1.py`:

- draait `Main_pelle.py --allow-fallback`;
- leest `output/ship_results.json`;
- checkt `Alleskunner` tegen referenties voor tank1, tank2 en GM.

Gebruik dit als baseline sanity check, niet als volledige testdekking voor alle datasets.

## 7. Uitbreiden van de code

Als je een nieuwe loadcase toevoegt:

1. maak een subclass vergelijkbaar met bestaande wrappers;
2. voeg loadcase toe in `bouw_loadcases(...)`;
3. update `maak_ship_object(...)`;
4. update documentatie (`00`, `04`, `08`, `11`).

Als je output wijzigt:

1. pas write-functies in `Main_pelle.py` aan;
2. update [08 Output Referentie](./08_output_referentie.md);
3. draai regressie/smoke tests.
