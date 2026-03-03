# 07 Code Referentie Modules

## 1. `Main_pelle.py`

### Verantwoordelijkheid

- CLI parsing
- loadcase bronconfig opbouwen
- scenario inlezen
- objecten bouwen per loadcase
- outputbestanden schrijven

### Belangrijkste functies

- `parse_args()`
- `bouw_loadcase_bron_configs(...)`
- `bouw_basis_scenario_config(...)`
- `maak_ship_object(...)`
- `write_results_json(...)`
- `write_errors_json(...)`
- `schrijf_antwoordenbladen(...)`

### Exceptions

- `DataValidatieFout`
- `InfeasibleLoadCaseError`
- `AssertionError` (regressie)

## 2. `Ship_pelle.py`

### Klasse `Ship`

Generieke solverklasse met workflow:

1. data-dir resolutie
2. hoofddata lezen
3. tanken bouwen
4. massabalans oplossen
5. stabiliteit berekenen
6. validatie

### Belangrijke attributen

- `dry_data`, `tank_data`, `ship_data`
- `tank1_percentage`, `tank2_percentage`
- `KB`, `KG`, `BM`, `GM`
- `force_residual_kg`, `long_m_residual_kgm`, `trans_m_residual_kgm`

## 3. `Functions_pelle.py`

### `Tank`

Leest volume/waterplane tabellen, bouwt afgeleide grootheden, levert inverse mapping voor:

- `percentage_uit_tM`
- `percentage_uit_massa`

### `deck(...)`

Bouwt massamatrix voor:

- kraanhuis
- giek
- hook load
- deklading

### `plates(...)`

Berekent staalmassa uit oppervlakken en diktes, inclusief massafactor.

### `matrix_add(...)`, `ZCG(...)`

Hulpfuncties voor matrixopbouw en zwaartepunt.

## 4. Loadcase wrappers

- `TransportschipClass.py`
- `KraanschipClass.py`
- `AlleskunnerClass.py`

Deze subclasses zetten alleen de juiste invoerdefaults; rekenlogica blijft in `Ship`.

## 5. `regressie_check_gr98_v1.py`

Los script dat referentiewaarden checkt voor een vaste baseline case.

Gebruik dit voor snelle sanity checks, niet als volledige acceptatietest voor alle custom loadcase-combinaties.
