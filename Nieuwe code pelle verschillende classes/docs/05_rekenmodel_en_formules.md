# 05 Rekenmodel en Formules

## 1. Rekenstappen op hoofdlijn

Voor elke loadcase:

1. Lees hydrostatische data en tankdiagramdata.
2. Bouw droge massa (`dry_data`) uit dek/kraan/lading + staal.
3. Zet tank 3 op initiieel percentage.
4. Los tank 1 op uit dwarsscheeps momentevenwicht.
5. Los tank 2 op uit verticaal krachtevenwicht.
6. Bepaal tank 2 langsscheepse oplossing (`tank2_lcg_solved`).
7. Bereken `KB`, `KG`, `BM`, `GM`.
8. Controleer residuen en grenzen.

## 2. Massa- en momentdefinities

Notatie:

- `m_i`: massa van post `i` [kg]
- `x_i, y_i, z_i`: LCG, TCG, VCG [m]
- `x_cov`: COV x-coordinaat [m]
- `x_cob`: COB x-coordinaat [m]
- `m_b`: buoyant mass [kg]

Langsscheeps moment van post `i`:

`M_long,i = m_i * (x_i - x_cov)`

Dwarsscheeps moment van post `i`:

`M_trans,i = m_i * y_i`

Buoyancy-term in langsscheeps balans:

`M_long,buoy = m_b * (x_cov - x_cob)`

## 3. Tank 1 oplossing

Doel: sluit dwarsscheeps balans met tank 1.

`target_tM_tank1 = - (sum(M_trans,dry) + M_trans,tank3)`

Tankdiagram gebruikt interpolatie:

`percentage_tank1 = f_inv_tM(target_tM_tank1)`

waar `f_inv_tM` begrensde inverse mapping is op basis van tabeldata.

## 4. Tank 2 oplossing

Doel: sluit krachtevenwicht in massa.

`m_tank2,target = m_b - (m_dry + m_tank1 + m_tank3)`

`percentage_tank2 = f_inv_mass(m_tank2,target)`

Als `m_tank2,target` buiten tabelrange valt -> loadcase infeasible.

## 5. Tank 2 LCG-oplossing

`target_lM_tank2 = - (M_long,dry + M_long,buoy + M_long,tank1 + M_long,tank3)`

`x_tank2,solved = target_lM_tank2 / m_tank2 + x_cov`

Gedrag:

- `tank2_is_movable=false`: geometrische tank-LCG blijft actief.
- `tank2_is_movable=true`: opgeloste waarde wordt gebruikt (met range-check).

## 6. Stabiliteit

`KB = COB_z`

`KG = sum(m_i * z_i) / sum(m_i)`

`BM = I_wp_x / V_buoyant - (GG_t1 + GG_t2 + GG_t3)`

`GM = KB - KG + BM`

Waar:

- `I_wp_x`: waterplane inertia x [m4]
- `V_buoyant`: buoyant volume [m3]
- `GG_t*`: vrije-oppervlakcorrectie per tank [m]

## 7. Residucontrole

Na oplossen:

- `force_residual_kg`
- `long_m_residual_kgm`
- `trans_m_residual_kgm`

Toleranties zijn functie van buoyant mass en hoofdafmetingen.

## 8. Fysische begrenzingen

- Tankpercentages moeten binnen [0,100] liggen.
- Inverse interpolatie buiten range is niet toegestaan.
- Indien geactiveerd: `tank2_lcg_solved` binnen tank-geometriebereik.

## 9. Numerieke methoden

De huidige inverse interpolatie gebruikt begrensde lineaire interpolatie (`np.interp`) op gesorteerde, unieke assen.

Gevolg:

- robuuster dan vrije spline-extrapolatie;
- voorspelbaar foutgedrag;
- minder kans op niet-fysische negatieve percentages.
