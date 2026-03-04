# 01 Snelle Start

## 1. Voorwaarden

Minimaal nodig:

- Python 3.10 of hoger (getest met 3.11).
- Packages:
  - `numpy`
  - `pandas`
  - `matplotlib`

Aanbevolen werkmap:

`C:\Users\Janal\deelopdracht8gr10\Nieuwe code pelle verschillende classes`

## 2. Eenmalige installatie

Open PowerShell in de projectmap en installeer dependencies:

```powershell
python -m pip install numpy pandas matplotlib
```

Controleer Python versie:

```powershell
python --version
```

## 3. Basisrun

Run zonder extra flags:

```powershell
python Main_pelle.py
```

Gedrag van deze run:

1. gebruikt standaard `data/` als primaire datamap;
2. probeert alle drie loadcases;
3. schrijft output naar `output/`.

## 4. Run met expliciete fallback

Alleen gebruiken als je lokale data onvolledig is:

```powershell
python Main_pelle.py --allow-fallback
```

Zonder `--allow-fallback` zal ongeldige primaire data direct een fout geven.

## 5. Run met loadcase-specifieke data

Aanbevolen voor teamwerk:

```powershell
python Main_pelle.py --loadcase-config data/loadcase_config.json
```

Voordelen:

- elke loadcase kan een eigen datafolder gebruiken;
- minder kans op conflict tussen transport-, kraan- en alleskunnerinstellingen.

## 6. Belangrijkste outputbestanden

Na een complete run staan in `output/`:

- `ship_results.json`
- `errors.json`
- `ship_results_graph.png`
- `antwoordenblad_TransportSchip.json`
- `antwoordenblad_KraanSchip.json`
- `antwoordenblad_Alleskunner.json`
- `antwoordenblad.json` (default kopie)

## 7. Eerste controle na run

Controleer direct:

1. zijn alle outputbestanden aangemaakt;
2. staat per loadcase een `status` (`ok` of `infeasible`);
3. zijn tankpercentages plausibel (0 tot 100);
4. is `GM` ingevuld voor alle `ok` cases.

## 8. Snelle interpretatie van status

- `status: "ok"`: loadcase volledig doorgerekend.
- `status: "infeasible"`: input of constraints maken de case fysisch/numeriek onhaalbaar.

Een `infeasible` case is meestal een data- of modelgrensprobleem, niet per se een crash van het programma.

## 9. Veelvoorkomende opstartproblemen

### 9.1 Verkeerde werkdirectory

Symptoom:

- bestanden worden niet gevonden;
- outputmap blijft leeg.

Actie:

- ga naar `Nieuwe code pelle verschillende classes` en run opnieuw.

### 9.2 Onjuiste of ontbrekende inputbestanden

Symptoom:

- `Template ontbreekt ... antwoordenblad.json`;
- `InputData ontbreekt ...`.

Actie:

- controleer bestandsnamen en groepsversie in de gekozen datamap.

### 9.3 Tankdoel buiten bereik

Symptoom:

- `Doelwaarde buiten bereik bij 'tank massa->percentage'`.

Actie:

- controleer lading, tank3 startpercentage en loadcase-specifieke input.

## 10. Regressiecheck

Voor een snelle baseline check:

```powershell
python regressie_check_gr98_v1.py
```

Belangrijk:

- bij `--loadcase-config` wordt de ingebouwde regressiecheck in `Main_pelle.py` bewust overgeslagen.
- gebruik dan bij voorkeur een aparte regressiecontrole per teamdataset.

## 11. Aanbevolen vervolg

Na je eerste succesvolle run:

1. lees [03 Data Contracten](./03_data_contracten.md);
2. configureer [04 Loadcase Configuratie](./04_loadcase_configuratie.md);
3. raadpleeg [08 Output Referentie](./08_output_referentie.md) voor interpretatie.
