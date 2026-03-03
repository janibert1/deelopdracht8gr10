# 04 Loadcase Configuratie

## 1. Waarom `loadcase_config.json`

Met een gedeelde datafolder lopen transport-, kraan- en alleskunnercases vaak door elkaar. `loadcase_config.json` lost dat op door per loadcase een eigen bronconfig te laten instellen.

Typische voordelen:

- eigen `data_dir` per loadcase;
- eigen fallbackbeleid per loadcase;
- eigen keuze voor `tank2_is_movable` en `strict_residuen`.

## 2. Locatie en activering

Aanbevolen locatie:

- `data/loadcase_config.json`

Activeren via CLI:

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json
```

Template beschikbaar:

- `data/loadcase_config.example.json`

## 3. Schema

Top-level keys:

- `TransportSchip`
- `KraanSchip`
- `Alleskunner`

Per key zijn deze velden mogelijk:

- `data_dir` (string)
- `fallback_data_dir` (string)
- `allow_fallback` (bool)
- `tank2_is_movable` (bool)
- `strict_residuen` (bool)

## 4. Resolutie- en prioriteitsregels

### 4.1 Relatieve paden

Relatieve paden worden opgelost ten opzichte van de map waarin `loadcase_config.json` staat, niet ten opzichte van je huidige shell directory.

### 4.2 Overrides

Voor elke loadcase geldt:

1. begin met globale CLI-defaults;
2. pas velden uit de JSON override toe als ze aanwezig zijn;
3. ontbrekende velden erven de globale waarde.

### 4.3 Onbekende loadcase keys

Onbekende keys in JSON worden genegeerd met runtime-waarschuwing.

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

## 6. Minimalistisch voorbeeld met alleen afwijkingen

Je hoeft niet elk veld per loadcase te zetten. Alleen verschillen opnemen is vaak duidelijker:

```json
{
  "KraanSchip": {
    "data_dir": "./data_kraanschip",
    "strict_residuen": true
  }
}
```

In dit voorbeeld gebruiken overige loadcases de globale CLI-settings.

## 7. Diagnostiek

Na een run kun je in `output/ship_results.json` bij `scenarios` per loadcase zien:

- welke `data_dir` actief was;
- of fallback was toegestaan;
- of `tank2_is_movable` en `strict_residuen` aanstonden.

Gebruik `output/errors.json` voor een compacte status per loadcase.

## 8. Veelvoorkomende valkuilen

1. Relatieve paden die vanaf de verkeerde map zijn gedacht.
2. Vergeten dat `allow_fallback=false` harde fouten geeft bij ongeldige primaire data.
3. JSON met syntaxfout of verkeerde booleans (`"true"` als string in plaats van `true`).
4. Verwarring tussen `--tank2-movable` (globaal) en `tank2_is_movable` (per loadcase override).

## 9. Aanbevolen werkwijze in teams

1. Maak een aparte datamap per loadcase.
2. Leg alle drie loadcases expliciet vast in `loadcase_config.json`.
3. Commit config en datafolderstructuur samen.
4. Documenteer afwijkingen in [12 Bijdragen en Onderhoud](./12_bijdragen_en_onderhoud.md).
