# 01 Snelle Start

## 1. Voorwaarden

- Python 3.10+ (getest met 3.11).
- Packages:
  - `numpy`
  - `pandas`
  - `matplotlib`
- Werkdirectory:
  - `C:\Users\Janal\deelopdracht8gr10\Nieuwe code pelle verschillende classes`

## 2. Basisrun

In PowerShell, vanuit projectmap:

```powershell
python Main_pelle.py
```

Dit gebruikt standaard `data/`.

## 3. Run met fallback naar voorbeelddata

```powershell
python Main_pelle.py --allow-fallback
```

Gebruik dit alleen als lokale hydrostatische data ongeldig is.

## 4. Run met aparte data per loadcase

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json
```

Dit is de aanbevolen route voor teamgebruik, omdat elke loadcase andere invoer kan hebben.

## 5. Waar output staat

Na een succesvolle run:

- `output/ship_results.json`
- `output/errors.json`
- `output/ship_results_graph.png`
- `output/antwoordenblad_TransportSchip.json`
- `output/antwoordenblad_KraanSchip.json`
- `output/antwoordenblad_Alleskunner.json`
- `output/antwoordenblad.json` (default kopie)

## 6. Interpretatie van status

In `ship_results.json` en `errors.json` staat per loadcase:

- `status: "ok"` -> case is doorgerekend.
- `status: "infeasible"` -> input/constraints maken de case fysisch of numeriek onhaalbaar.

## 7. Snelle checklist bij eerste run

1. Bestaat `antwoordenblad.json` in gebruikte datamap?
2. Bestaat `InputData_Gr.._V..json` voor de juiste `file_id`?
3. Is `Buoyant_Volume_m3 > 0` in `MainShipParticulars_...json`?
4. Zijn tankdiagram CSV's aanwezig?
5. Klopt pad in `--loadcase-config`?

## 8. Veelgemaakte fouten

### 8.1 Verkeerde werkdirectory

Symptoom: bestanden niet gevonden.

Oplossing: run commando vanuit projectmap.

### 8.2 BOM in JSON

Symptoom: `Unexpected UTF-8 BOM`.

Status: opgelost in code door `utf-8-sig` reader.

### 8.3 Infeasible tank-oplossing

Symptoom: `Doelwaarde buiten bereik ... tank massa->percentage`.

Oplossing: check lading/huiddikte/tank3-instelling per loadcase.

## 9. Regressiecheck

```powershell
python regressie_check_gr98_v1.py
```

Let op: bij `--loadcase-config` wordt de standaard regressiecheck in `Main_pelle.py` bewust overgeslagen, omdat die check op een vaste referentie-case gebaseerd is.
