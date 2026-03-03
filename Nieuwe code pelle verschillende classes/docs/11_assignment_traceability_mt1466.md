# 11 Assignment Traceability MT1466

## 1. Doel van deze pagina

Koppelt assignment-eisen aan concrete onderdelen in de code/output.

## 2. Structuur- en programmeereisen

### 2.1 File-organisatie en documentatie

Status: aanwezig.

- Gescheiden modules (`Main`, `Ship`, `Functions`, loadcase classes).
- Uitgebreide docstrings in code.
- Deze `docs/` map toegevoegd.

### 2.2 Onderscheid functies/methoden

Status: aanwezig.

- Orchestration in `Main_pelle.py`.
- Rekenlogica in `Ship_pelle.py`.
- Dataspecifieke utilities in `Functions_pelle.py`.

### 2.3 Gebruik classes

Status: aanwezig.

- `Ship` als generieke kernklasse.
- Subclasses voor drie loadcases.

### 2.4 Grafiek output

Status: aanwezig.

- `output/ship_results_graph.png`

## 3. Inhoudelijke output-eisen

### 3.1 Evenwicht (dwars/langs/verticaal)

Status: berekend en gerapporteerd via residuen/afwijkingen.

### 3.2 G'M

Status: berekend (`GM`) en weggeschreven.

### 3.3 Notatie evenwichtsafwijking

Status: weggeschreven naar antwoordenbladvelden.

## 4. Drie scheepstypen

Status: ondersteund en afzonderlijk configureerbaar via `--loadcase-config`.

## 5. Opmerking

Deze traceability documenteert softwaredekking. Of een specifieke set invoer exact overeenkomt met alle voorbeeldfiles hangt af van de beschikbare GH exports per loadcase.
