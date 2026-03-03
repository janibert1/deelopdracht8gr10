# 08 Output Referentie

## 1. `output/ship_results.json`

### Structuur

- `scenarios`: scenario-invoer per loadcase
- `results`: berekende resultaten per loadcase
- `errors`: foutmeldingen per loadcase

### `results.<LoadCase>.status`

- `ok`
- `infeasible`

### `results.<LoadCase>` velden (bij status `ok`)

- `file`
- `tank1_percentage`
- `tank2_percentage`
- `tank2_lcg`
- `tank2_lcg_solved`
- `KB`
- `KG`
- `BM`
- `GM`
- `force_residual_kg`
- `long_m_residual_kgm`
- `trans_m_residual_kgm`
- `status`
- `error`

## 2. `output/errors.json`

Compact overzicht per loadcase:

- status
- error text
- gebruikte `data_dir`
- gebruikte `fallback_data_dir`

## 3. `output/antwoordenblad_<LoadCase>.json`

Per loadcase een ingevulde versie in originele key-structuur.

Bij infeasible cases:

- veldwaarden die niet berekend kunnen worden worden `null`.
- projectversie krijgt suffix `_INFEASIBLE`.

## 4. `output/antwoordenblad.json`

Default kopie voor opdrachtconventie. Momenteel gebaseerd op alleskunner als beschikbaar.

## 5. `output/ship_results_graph.png`

Grafiek met:

- GM per loadcase
- tank vullingspercentages
- markering van infeasible cases

## 6. Interpreteer residuen correct

Een `ok` status betekent:

- tankoplossingen lagen binnen bereik.

Maar residuwaarschuwingen kunnen nog wijzen op model-inconsistenties (bijv. vaste tank2-locatie).

Controleer daarom altijd:

- `long_m_residual_kgm`
- `trans_m_residual_kgm`

in combinatie met gekozen flags.
