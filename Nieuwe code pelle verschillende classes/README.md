## Overzicht

Deze map bevat de class-gebaseerde implementatie voor de MT1463/MT1466
workflow voor stabiliteit en evenwicht.

De code is gestructureerd volgens:
`Tips om een Python code te organiseren`

Belangrijkste ontwerpdoelen:
- één herbruikbare generieke scheepsklasse gebruiken;
- hulpfuncties scheiden van scenario-orchestratie;
- alle drie verplichte scheepstypen ondersteunen via subklassen;
- consistente naamgeving en documentatie aanhouden.

## Mappenstructuur

- `Main_pelle.py`
  - Hoofdingangspunt.
  - Definieert één scenario, rekent alle drie scheepstypen door en print een samenvatting.
  - Schrijft uitvoerbestanden:
    - `output/ship_results.json`
    - `output/ship_results_graph.png`
- `Ship_pelle.py`
  - Generieke `Ship`-klasse.
  - Verwerkt data-inlees, tankinterpolatie, evenwichtsoplossing en GM.
- `Functions_pelle.py`
  - Herbruikbare hulpfuncties:
    - `Tank`-interpolatieklasse
    - `deck(...)`
    - `plates(...)`
    - `ZCG(...)`
    - `matrix_add(...)`
- `TransportschipClass.py`
  - `TransportSchip`: alleen deklading, geen kraan.
- `KraanschipClass.py`
  - `KraanSchip`: kraanconditie, geen deklading.
- `AlleskunnerClass.py`
  - `Alleskunner`: kraanconditie plus deklading.
- `data/`
  - Invoer-CSV/JSON gegenereerd door Rhino/Grasshopper.
- `output/`
  - Gegenereerde JSON- en grafiekbestanden (ontstaan na run van `Main_pelle.py`).

## Rekenworkflow

1. Lees hydrostatische scheepsdata (`MainShipParticulars_...json`).
2. Bouw 3 tankobjecten op basis van tankdiagram-CSV's.
3. Bouw de droge-lastmatrix uit:
   - dek-/kraanlasten
   - staalgewicht van huid en schotten
4. Los evenwicht op:
   - Tank 1 vulling uit dwarsscheeps momentevenwicht
   - Tank 2 massa uit verticaal krachtevenwicht
   - Tank 2 langsscheepse locatie uit langsscheeps momentevenwicht
5. Bereken stabiliteit:
   - `KB` uit opwaarts aangrijpingspunt
   - `KG` uit massaverdeling
   - `BM` uit waterplane-traagheid met vrije-oppervlakcorrectie
   - `GM = KB - KG + BM`

## Invoeraannames in deze code

- Soortelijk gewicht staal: `7850 kg/m3`
- Soortelijk gewicht water (buiten + ballast): `1025 kg/m3`
- Plaat+verstijver-factor: `2.1`
- Kraanmassamodel:
  - kraanhuis = `0.34 * SWL`
  - giek = `0.17 * SWL`
  - `SWL = TP_mass / 0.94`

Deze waarden zijn nog steeds instelbaar in `Main_pelle.py`.

## Datapadgedrag

De `Ship`-klasse probeert eerst lokale `data/`.
Als die map een onbruikbare `MainShipParticulars` heeft (bijvoorbeeld drijfvolume
gelijk aan 0), dan valt de code automatisch terug op:

`../Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps`

Hierdoor blijft het project uitvoerbaar als lokale exports onvolledig zijn.

## Uitvoeren

Voer uit vanuit deze map:

```bash
python Main_pelle.py
```

Verwachte terminaluitvoer:
- één samenvattingsblok per scheepstype (`TransportSchip`, `KraanSchip`, `Alleskunner`)
- paden van opgeslagen JSON- en PNG-uitvoer

## Gegenereerde uitvoer

Na een succesvolle run:

- `output/ship_results.json`
  - Scenarioconstanten + berekende waarden per schip (`tank1_percentage`,
    `tank2_percentage`, `tank2_lcg`, `KB`, `KG`, `BM`, `GM`)
- `output/ship_results_graph.png`
  - Figuur met:
    - GM-staafdiagram per scheepstype
    - Tankvullingspercentages per scheepstype

## Opmerkingen voor vervolgstappen

- Deze code focust nu op evenwicht/stabiliteit en rapportage-uitvoer.
- `Main_pelle.py` kan worden uitgebreid met:
  - mapping/schrijven naar antwoordenblad.json
  - officiële puntentelling zodra alle formules vastliggen
  - vergelijkingslijsten voor meerdere ontwerpen/varianten
