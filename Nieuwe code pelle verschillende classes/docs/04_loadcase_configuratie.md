# 04 Loadcase Configuratie

## 1. Waarom deze file

`loadcase_config.json` maakt het mogelijk om voor elke loadcase eigen inputdata en gedrag te kiezen.

Dit is essentieel omdat:

- transportschip, kraanschip en alleskunner vaak niet dezelfde tank- en kraancondities hebben;
- een enkele shared `antwoordenblad.json` tot infeasible cases kan leiden.

## 2. Locatie

Aanbevolen:

- `data/loadcase_config.json`

Voorbeeldtemplate:

- `data/loadcase_config.example.json`

## 3. JSON-schema

Top-level keys:

- `TransportSchip`
- `KraanSchip`
- `Alleskunner`

Per key:

- `data_dir` (string, pad)
- `fallback_data_dir` (string, pad)
- `allow_fallback` (bool)
- `tank2_is_movable` (bool)
- `strict_residuen` (bool)

## 4. Padresolutie

- Relatieve paden worden opgelost t.o.v. de map waar `loadcase_config.json` staat.
- Absolute paden worden direct gebruikt.

## 5. Volledig voorbeeld

```json
{
  "TransportSchip": {
    "data_dir": "./data_transport",
    "fallback_data_dir": "../../Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps",
    "allow_fallback": false,
    "tank2_is_movable": false,
    "strict_residuen": false
  },
  "KraanSchip": {
    "data_dir": "./data_kraanschip",
    "fallback_data_dir": "../../Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps",
    "allow_fallback": false,
    "tank2_is_movable": false,
    "strict_residuen": false
  },
  "Alleskunner": {
    "data_dir": "./data_alleskunner",
    "fallback_data_dir": "../../Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps",
    "allow_fallback": false,
    "tank2_is_movable": false,
    "strict_residuen": false
  }
}
```

## 6. Bekende valkuilen

1. BOM in JSON door editor/powershell.
   - Status: reader ondersteunt `utf-8-sig`.
2. Verkeerde relatieve paden (`./data/...` vs `./...`).
3. `allow_fallback=false` met ongeldige lokale hydrodata.

## 7. Diagnostiek

Controleer na run:

- `output/errors.json`
- `output/ship_results.json` -> blok `scenarios` en `results`.

Daarin zie je exact welke data-dir per loadcase gebruikt is.
