# 08 Output Referentie

## 1. Overzicht van outputmap

Na een run schrijft de code standaard naar:

- `output/ship_results.json`
- `output/errors.json`
- `output/ship_results_graph.png`
- `output/antwoordenblad_TransportSchip.json`
- `output/antwoordenblad_KraanSchip.json`
- `output/antwoordenblad_Alleskunner.json`
- `output/antwoordenblad.json`

## 2. `ship_results.json`

### Structuur op topniveau

- `scenarios`: gebruikte scenario-config per loadcase
- `results`: berekende output per loadcase
- `errors`: fouttekst per loadcase (alleen gevulde entries)

### `results.<LoadCase>.status`

Mogelijke waarden:

- `ok`
- `infeasible`

### Velden bij `status: ok`

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
- `error` (`null`)

### Velden bij `status: infeasible`

Numerieke velden worden `null`, met een gevulde fouttekst in `error`.

## 3. `errors.json`

Compacte status per loadcase:

- `status`
- `error`
- `data_dir`
- `fallback_data_dir`

Gebruik dit bestand voor snelle triage in CI of teamreviews.

## 4. Antwoordenbladbestanden

### Per loadcase

- `antwoordenblad_TransportSchip.json`
- `antwoordenblad_KraanSchip.json`
- `antwoordenblad_Alleskunner.json`

De keystructuur van het template blijft behouden.

### Infeasible gedrag

Als een loadcase infeasible is:

- kritieke resultaatvelden worden `null`;
- `Groepsversie` krijgt suffix `_INFEASIBLE`.

### Default antwoordenblad

`antwoordenblad.json` is een kopie van de Alleskunner-output als die bestaat, anders de eerste beschikbare case-output.

## 5. `ship_results_graph.png`

Grafiek bevat twee panelen:

1. `GM` per loadcase
2. tank1/tank2 percentages per loadcase

Infeasible cases worden grijs gemarkeerd en gelabeld als `infeasible`.

## 6. Interpretatierichtlijnen

### 6.1 Kijk niet alleen naar `status`

`status: ok` betekent dat de solver een geldige oplossing binnen grenzen vond. Controleer aanvullend:

- `force_residual_kg`
- `long_m_residual_kgm`
- `trans_m_residual_kgm`

### 6.2 `tank2_lcg` versus `tank2_lcg_solved`

- `tank2_lcg`: waarde die echt in de eindbalans is gebruikt.
- `tank2_lcg_solved`: theoretische oplossing uit momentevenwicht.

Als `tank2_is_movable=false` kunnen deze waarden verschillen.

### 6.3 GM als kwaliteitsindicator

`GM` is de aanvangsstabiliteitsindicator. Vergelijk tussen loadcases en beoordeel altijd in combinatie met de gekozen invoercondities.

## 7. Praktisch leespad bij analyse

1. begin met `errors.json` voor statusoverzicht;
2. ga naar `ship_results.json` voor details;
3. open daarna `ship_results_graph.png` voor snelle visuele vergelijking;
4. controleer ten slotte het relevante `antwoordenblad_<LoadCase>.json`.
