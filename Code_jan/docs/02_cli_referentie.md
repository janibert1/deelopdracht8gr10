# 02 CLI Referentie

## 1. Overzicht

Entry point:

`Main_pelle.py`

Algemene vorm:

```powershell
python Main_pelle.py [opties]
```

De CLI stuurt alleen configuratie aan. De rekenkern zit in `Ship_pelle.py`.

## 2. Argumenten

### `--data-dir <pad>`

- Type: pad
- Default: `./data` (relatief aan `Main_pelle.py`)
- Gebruik: primaire datamap als je geen `--loadcase-config` gebruikt.

### `--fallback-data-dir <pad>`

- Type: pad
- Default: `../Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps`
- Gebruik: fallback bron voor hydro/tank-data als primaire bron ongeldig is en fallback is toegestaan.

### `--allow-fallback`

- Type: vlag (bool)
- Default: `False`
- Gebruik: sta fallback naar `--fallback-data-dir` expliciet toe.

### `--skip-regression-check`

- Type: vlag (bool)
- Default: `False`
- Gebruik: sla ingebouwde regressiecheck aan het einde van de run over.

### `--tank2-movable`

- Type: vlag (bool)
- Default: `False`
- Gebruik: activeer toepassing van de opgeloste `tank2_lcg` (met bereikcheck).

### `--strict-residuen`

- Type: vlag (bool)
- Default: `False`
- Gebruik: maak overschrijding van residutoleranties hard-failing.

### `--loadcase-config <pad>`

- Type: pad naar JSON
- Default: `None`
- Gebruik: loadcase-specifieke overrides voor data en flags.

## 3. Voorbeeldcommando's

### Standaard run

```powershell
python Main_pelle.py
```

### Run met fallback geactiveerd

```powershell
python Main_pelle.py --allow-fallback
```

### Run met per-loadcase configuratie

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json
```

### Streng residubeleid op globale flags

```powershell
python Main_pelle.py --strict-residuen
```

### Combinatie: loadcase-config + globale defaults

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json --allow-fallback
```

Let op: waarden in `loadcase_config.json` kunnen globale flags per loadcase overschrijven.

## 4. Prioriteitsregels tussen argumenten

1. Zonder `--loadcase-config` gelden globale flags voor alle loadcases.
2. Met `--loadcase-config` start elke loadcase met globale defaults.
3. Als een field in de JSON override staat (`data_dir`, `allow_fallback`, etc.), wint de override.
4. Onbekende loadcase keys in de JSON worden genegeerd met waarschuwing.

## 5. Regressiecheck gedrag

Aan het eind van `main()`:

- met `--skip-regression-check`: altijd overslaan;
- met custom `--loadcase-config`: standaard ook overslaan (expliciet bericht);
- zonder bovenstaande: run regressiecheck op `Alleskunner` als die `ok` is.

## 6. Exitgedrag

Normaal gedrag:

- script probeert alle loadcases af te handelen;
- `infeasible` cases worden als status vastgelegd in output;
- run blijft bruikbaar zolang de fout binnen loadcase-afhandeling valt.

Hard fail op toplevel:

- kritieke configuratiefout (bijvoorbeeld onleesbare config);
- expliciete `AssertionError` uit regressiecheck;
- ongevangen `DataValidatieFout` of `InfeasibleLoadCaseError` buiten case-loop.

## 7. Praktische CLI-adviezen

- Gebruik voor teamwerk altijd `--loadcase-config`.
- Gebruik `--allow-fallback` alleen bewust, zodat je niet ongemerkt op voorbeelddata rekent.
- Zet `--strict-residuen` aan tijdens debug en kwaliteitscontrole.
- Leg gebruikte CLI-commandos vast in je verslag of commitbericht voor reproduceerbaarheid.
