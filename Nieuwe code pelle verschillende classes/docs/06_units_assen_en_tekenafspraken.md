# 06 Units, Assen en Tekenafspraken

## 1. Interne units (hard policy)

- Massa: `kg`
- Lengte: `m`
- Moment: `kgm`
- Hoeken in input: graden

## 2. Externe units in antwoordenblad

- Meerdere velden geven gewichten in `N`.
- Conversie wordt direct gedaan bij inlezen:

`massa_kg = gewicht_n / 9.81`

Terugschrijven naar antwoordenblad:

`gewicht_n = massa_kg * 9.81`

## 3. Assenstelsel

- `x`: langsscheeps (LCG)
- `y`: dwarsscheeps (TCG)
- `z`: verticaal (VCG)

## 4. Momentreferenties

Langsscheeps moment gebruikt `(x - x_cov)`.

Dwarsscheeps moment gebruikt `y` t.o.v. centerline.

## 5. Positieve richting

Conventie in code:

- positieve `y` levert positief transversaal moment;
- positieve afwijkingen volgen directe somconventie in arrays.

## 6. Tankpercentages

- Interpreteer als `% of h_tank`.
- Geldig domein: `[0, 100]`.

## 7. Belang van unit-consistentie

Een mix van `N` en `kg` in massabalans leidt direct tot:

- te zware lading;
- tankdoelwaarden buiten bereik;
- kunstmatig negatieve of >100% vullingen.

## 8. Praktische checks

1. Vergelijk `deck_tp_mass_kg` met `deck_tp_weight_n/9.81` in `ship_results.json`.
2. Controleer of `hook_tp_mass_kg` realistisch is.
3. Controleer of `buoyant_mass` qua orde-grootte bij scheepsvolume past.
