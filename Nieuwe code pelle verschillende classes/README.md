## Overzicht

Deze map bevat de class-gebaseerde implementatie voor MT1463/MT1466.

De code volgt de structuur-richtlijnen uit:
`Tips om een Python code te organiseren`

Volledige (zeer uitgebreide) Nederlandstalige documentatie:
- `docs/index.md`

Belangrijkste verbeteringen in deze versie:
- Interne eenheden zijn expliciet en consistent: `kg`, `m`, `kgm`.
- TP-gewichten uit antwoordenblad (`N`) worden expliciet omgezet naar massa (`kg`).
- Tankoplossing is begrensd: geen extrapolatie buiten tankdiagrammen.
- Onmogelijke load cases geven een expliciete foutmelding.
- Tank2 kan expliciet als vast of verplaatsbaar worden gemodelleerd.
- Output wordt geschreven in het antwoordenblad-JSON format.
- Regressiecheckscript toegevoegd voor Gr98 V1.0.

## Bestandsstructuur

- `Main_pelle.py`
  - Hoofdingang.
  - Leest scenario per load case uit `data/antwoordenblad.json` + `InputData_*.json`.
  - Ondersteunt per-loadcase overrides via `--loadcase-config`.
  - Rekent load cases door.
  - Schrijft output:
    - `output/ship_results.json`
    - `output/errors.json`
    - `output/ship_results_graph.png`
    - `output/antwoordenblad.json`
    - `output/antwoordenblad_*.json` (ook voor infeasible load cases)
- `Ship_pelle.py`
  - Generieke scheepsklasse.
  - Data-validatie, massa- en momentbalans, stabiliteit, residuchecks.
- `Functions_pelle.py`
  - Tankklasse met begrensde interpolatie.
  - Hulpfuncties voor dekbelasting en staalmassa.
  - Bevat `DataValidatieFout` en `InfeasibleLoadCaseError`.
- `TransportschipClass.py`
  - Transport load case (deklading, geen kraan).
- `KraanschipClass.py`
  - Kraan load case (wel kraan, geen deklading).
- `AlleskunnerClass.py`
  - Gecombineerde load case (kraan + deklading).
- `regressie_check_gr98_v1.py`
  - Eenvoudige regressiecheck tegen bekende referentiewaarden.

## Unitbeleid

Interne standaard:
- massa: `kg`
- lengte: `m`
- moment: `kgm`

Conventie:
- invoer uit antwoordenblad kan in `N` staan;
- conversie naar `kg` gebeurt direct bij inlezen;
- terugconversie naar `N` gebeurt alleen bij wegschrijven van antwoordenblad.

## Data en validatie

Verplichte bestanden in `data/`:
- `antwoordenblad.json`
- `InputData_Gr<groep>_V<versie>.<subversie>.json`

Hydrostatische/tank-data wordt gelezen uit de gekozen data-map.
Als lokale data ongeldig is (bijv. `Buoyant_Volume_m3 <= 0`), dan:
- standaard: harde fout;
- met `--allow-fallback`: expliciete fallback naar voorbeelddata + waarschuwing.

## Solver-gedrag

- Tank 1 en tank 2 worden opgelost met begrensde interpolatie.
- Doelwaarde buiten diagram-bereik geeft `InfeasibleLoadCaseError`.
- Tank2-locatie:
  - vast (`--tank2-movable` uit): vaste geometrische `lcg` blijft actief;
  - verplaatsbaar (`--tank2-movable` aan): opgeloste `lcg` wordt toegepast.
- Residuen (kracht/moment) worden gecontroleerd:
  - standaard: waarschuwing bij overschrijding;
  - met `--strict-residuen`: fout bij overschrijding.

## Uitvoeren

Standaard (strikte data, geen fallback):

```bash
python Main_pelle.py
```

Met expliciete fallback naar voorbeelddata:

```bash
python Main_pelle.py --allow-fallback
```

Optionele flags:
- `--tank2-movable`
- `--strict-residuen`
- `--skip-regression-check`
- `--data-dir <pad>`
- `--fallback-data-dir <pad>`
- `--loadcase-config <pad>`

Voorbeeld per-loadcase configuratie:
- `data/loadcase_config.example.json`

## Regressiecheck

Run:

```bash
python regressie_check_gr98_v1.py
```

Checkt (Alleskunner, Gr98 V1.0) tegen referentie:
- tank1 ~ 59.322%
- tank2 ~ 85.1747%
- GM ~ 1.0585 m

met tolerantie op deltas.

## Opmerking over infeasible cases

Als een load case fysisch niet haalbaar is met de huidige invoer
(bijvoorbeeld benodigde tankmassa buiten tankdiagram-bereik),
dan wordt dit expliciet gemeld in:
- `output/ship_results.json`
- `output/errors.json`

Het script blijft de andere load cases wel doorrekenen en schrijft voor alle drie
een `antwoordenblad_<loadcase>.json`.
