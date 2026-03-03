# 02 CLI Referentie

## 1. Overzicht

Entry point: `Main_pelle.py`

Algemene vorm:

```powershell
python Main_pelle.py [opties]
```

## 2. Argumenten

### `--data-dir <pad>`

- Type: pad
- Default: `./data`
- Betekenis: primaire datamap (als geen `--loadcase-config` gebruikt wordt).

### `--fallback-data-dir <pad>`

- Type: pad
- Default: `../Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps`
- Betekenis: fallback data als primaire data ongeldig is en fallback is toegestaan.

### `--allow-fallback`

- Type: vlag (bool)
- Default: `False`
- Betekenis: sta fallback toe als primaire data ongeldig is.

### `--skip-regression-check`

- Type: vlag
- Default: `False`
- Betekenis: sla ingebouwde regressiecheck over.

### `--tank2-movable`

- Type: vlag
- Default: `False`
- Betekenis: modelleer tank 2 langsscheeps verplaatsbaar; opgeloste `tank2_lcg` wordt actief toegepast.

### `--strict-residuen`

- Type: vlag
- Default: `False`
- Betekenis: overschrijding van residu-toleranties maakt loadcase hard-failing.

### `--loadcase-config <pad>`

- Type: pad naar JSON
- Default: `None`
- Betekenis: overrides per loadcase voor data en flags.

## 3. Voorbeeldcommando's

### Standaard run

```powershell
python Main_pelle.py
```

### Run met fallback

```powershell
python Main_pelle.py --allow-fallback
```

### Run met custom loadcase-config

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json
```

### Run met streng residubeleid

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json --strict-residuen
```

## 4. Interactie tussen argumenten

1. Als `--loadcase-config` gezet is, wordt per loadcase een eigen bronconfig gebruikt.
2. Zonder `--loadcase-config` gelden globale flags voor alle loadcases.
3. Regressiecheck:
   - normaal actief;
   - overgeslagen bij custom `--loadcase-config` tenzij je eigen checkscript gebruikt.

## 5. Exitgedrag

- Script probeert alle loadcases te verwerken.
- Infeasible loadcases worden in output gezet, run stopt niet direct.
- Run faalt alleen op kritieke fouten buiten loadcase-afhandeling (bijv. onleesbare config JSON).
