# 05 Rekenmodel en Formules

## 1. Rekenketen op hoofdlijn

Per loadcase doorloopt `Ship` in vaste volgorde:

1. hoofddata en tankdata inlezen;
2. droge massa opbouwen (`deck` + `plates`);
3. tank 3 instellen op inputpercentage;
4. tank 1 oplossen uit dwarsscheeps momentevenwicht;
5. tank 2 oplossen uit verticaal krachtevenwicht;
6. tank 2 LCG afleiden uit langsscheeps momentevenwicht;
7. stabiliteit (`KB`, `KG`, `BM`, `GM`) berekenen;
8. residuen en grenzen valideren.

## 2. Notatie en referenties

Gebruikte symbolen:

- `m_i`: massa van component `i` `[kg]`
- `x_i, y_i, z_i`: LCG/TCG/VCG van component `i` `[m]`
- `x_cov`: langsscheepse coordinate van COV `[m]`
- `x_cob`: langsscheepse coordinate van COB `[m]`
- `m_b`: opwaarts verplaatste massa (`buoyant_volume * water_density`) `[kg]`

Momenten in code worden intern in `kgm` behandeld.

## 3. Opbouw van droge massa

### 3.1 Dekcomponenten (`deck(...)`)

Afhankelijk van loadcase bevat dekdata:

- kraanhuismassa (`0.34 * crane_swl_mass_kg`);
- gieksmassa (`0.17 * crane_swl_mass_kg`);
- hook load (`hook_tp_mass_kg`);
- transition pieces op dek (`deck_tp_amount * deck_tp_mass_kg`).

### 3.2 Staalmassa (`plates(...)`)

Huid:

- `volume_hull = area_hull * hull_thickness`
- `mass_hull = volume_hull * material_density * mass_factor`

Schotten:

- `volume_bhd = area_bhd * BHD_thickness`
- `mass_bhd = volume_bhd * material_density * mass_factor`

## 4. Dwarsscheeps balans: oplossing tank 1

De code gebruikt:

- `dry_tM = sum(m_i * y_i)` over droge componenten
- `initial_tM = dry_tM + tank3_tM`
- `tank1_tM_target = -initial_tM`

Daarna inverse interpolatie:

`tank1_percentage = f_inv_tM(tank1_tM_target)`

waar `f_inv_tM` begrensd is op de tabelrange.

## 5. Verticaal krachtevenwicht: oplossing tank 2

Stap 1:

`m_b = buoyant_volume * water_density`

Stap 2:

`m_tank2_target = m_b - (m_dry + m_tank1 + m_tank3)`

Stap 3:

`tank2_percentage = f_inv_mass(m_tank2_target)`

Als `m_tank2_target` buiten de massarange van tank 2 valt, volgt `InfeasibleLoadCaseError`.

## 6. Langsscheeps momentevenwicht: tank 2 LCG

Langsscheeps momenten:

- droog: `dry_lM = sum(m_i * (x_i - x_cov))`
- buoyancyterm: `buoyant_lM = m_b * (x_cov - x_cob)`

Doelmoment tank 2:

`tank2_lM_target = -(dry_lM + buoyant_lM + tank1_lM + tank3_lM)`

Opgeloste positie:

`tank2_lcg_solved = (tank2_lM_target / m_tank2) + x_cov`

Gedrag:

- `tank2_is_movable=false`: gebruik geometrische tank2-LCG uit tabel;
- `tank2_is_movable=true`: gebruik `tank2_lcg_solved` mits binnen `[lcg_min, lcg_max]`.

## 7. Stabiliteitsgrootheden

De code rekent:

- `KB = COB_z`
- `KG = sum(m_i * z_i) / sum(m_i)`
- `BM = I_wp_x / buoyant_volume - (GG_t1 + GG_t2 + GG_t3)`
- `GM = KB - KG + BM`

Waar:

- `I_wp_x` uit `Inertia_WPA_around_COF_m4`;
- `GG_t*` vrije-oppervlakcorrecties uit tank-waterplane data.

## 8. Residucontrole

Berekeningen:

- `force_residual_kg = m_b - sum(m_i)`
- `long_m_residual_kgm = sum(m_i*(x_i-x_cov)) + m_b*(x_cov-x_cob)`
- `trans_m_residual_kgm = sum(m_i*y_i) + m_b*(-y_cob)`

Toleranties:

- `force_tol = max(0.001 * m_b, 25.0)`
- `long_tol = max(0.001 * m_b * max(LOA, 1.0), 250.0)`
- `trans_tol = max(0.001 * m_b * max(width, 1.0), 250.0)`

Bij overschrijding:

- waarschuwing als `strict_residuen=false`;
- `InfeasibleLoadCaseError` als `strict_residuen=true`.

## 9. Interpolatiemethode en grenzen

`Functions_pelle._interpoleer_begrensd(...)`:

1. sorteert en dedupliceert de as;
2. controleert minimaal 2 unieke punten;
3. weigert targets buiten range;
4. gebruikt lineaire interpolatie (`np.interp`) binnen range.

Gevolg: numeriek voorspelbaar gedrag zonder extrapolatie.

## 10. Samenvatting modelaannames

- alle interne berekeningen gebeuren in `kg`, `m`, `kgm`;
- tanktabellen bepalen harde fysische grenzen;
- loadcases worden onafhankelijk opgelost maar in een gezamenlijke run gerapporteerd;
- residuen zijn expliciet zichtbaar voor kwaliteitscontrole.
