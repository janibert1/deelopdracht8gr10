# 06 Units, Assen en Tekenafspraken

## 1. Unitbeleid (hard policy)

Interne eenheden in de code zijn altijd:

- massa: `kg`
- lengte: `m`
- moment: `kgm`

Dit geldt voor alle balansvergelijkingen en residucontroles.

## 2. Externe invoer in Newton

In `antwoordenblad.json` staan meerdere gewichten in `N`. De code zet die direct om:

`massa_kg = gewicht_n / 9.81`

Bij wegschrijven naar antwoordenblad gebeurt de inverse conversie:

`gewicht_n = massa_kg * 9.81`

## 3. Assenstelsel

- `x`: langsscheeps (LCG)
- `y`: dwarsscheeps (TCG)
- `z`: verticaal (VCG)

Voor momenten gebruikt de code:

- langsscheeps balans rond `x_cov`;
- dwarsscheeps balans rond centerline (`y=0`).

## 4. Tekenconventies

Conventie in de rekensommen:

- positief `y` geeft positief transversaal moment `m*y`;
- langsscheeps moment gebruikt `(x - x_cov)`;
- buoyancyterm langsscheeps gebruikt `(x_cov - x_cob)`.

Belangrijk is consistentie: niet het absolute teken op zich, maar dat alle termen dezelfde conventie volgen.

## 5. Tankpercentages

Interpretatie:

- `% of h_tank`

Geldig domein:

- `[0, 100]`

Elke oplossing buiten dit domein wordt als infeasible behandeld.

## 6. Waar unitfouten meestal ontstaan

Typische foutbron:

- `N` direct optellen bij `kg` in een externe berekening of handmatige controle.

Typische symptomen:

- tankdoelwaarden ver buiten range;
- onrealistische `GM`;
- grote residuen ondanks geldige geometrie.

## 7. Praktische controles op unitconsistentie

Gebruik `output/ship_results.json` en controleer:

1. `deck_tp_mass_kg` is ongeveer `deck_tp_weight_n / 9.81`;
2. `hook_tp_mass_kg` is qua orde-grootte realistisch;
3. `buoyant_mass` (impliciet) past bij `Buoyant_Volume_m3 * water_density`;
4. tankpercentages blijven binnen 0-100.

## 8. Aanbevolen teamafspraak

Leg in het team vast:

- alle nieuwe helperfuncties accepteren intern `kg` en `m`;
- elke externe interface benoemt units expliciet in veldnaam of docstring;
- conversiepunten (`N <-> kg`) blijven gecentraliseerd bij in- en output.
