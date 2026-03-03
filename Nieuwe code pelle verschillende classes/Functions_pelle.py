"""Kernfuncties en tankhulpklasse voor scheepsberekeningen.

Alle interne berekeningen gebruiken:
- massa in kilogram [kg]
- lengte in meter [m]
- moment in kilogrammeter [kgm]
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


class DataValidatieFout(ValueError):
    """Fout voor ongeldige of ontbrekende invoerdata."""


class InfeasibleLoadCaseError(ValueError):
    """Fout voor fysisch/onmogelijk load case doelwaarden."""


def _interpoleer_begrensd(x, y, target, label):
    """Lineaire interpolatie met harde grenzen en duidelijke foutmelding."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    if x_arr.size != y_arr.size or x_arr.size < 2:
        raise DataValidatieFout(
            f"Interpolatie '{label}' vereist arrays met gelijke lengte >= 2."
        )

    sort_idx = np.argsort(x_arr)
    x_sorted = x_arr[sort_idx]
    y_sorted = y_arr[sort_idx]

    x_unique, unique_idx = np.unique(x_sorted, return_index=True)
    y_unique = y_sorted[unique_idx]
    if x_unique.size < 2:
        raise DataValidatieFout(
            f"Interpolatie-as voor '{label}' bevat te weinig unieke waarden."
        )

    xmin = float(x_unique[0])
    xmax = float(x_unique[-1])
    if target < xmin or target > xmax:
        raise InfeasibleLoadCaseError(
            f"Doelwaarde buiten bereik bij '{label}': target={target:.6f}, "
            f"toegestaan=[{xmin:.6f}, {xmax:.6f}]."
        )

    return float(np.interp(target, x_unique, y_unique))


class Tank:
    """Hulpklasse voor tankdiagrammen met begrensde interpolatie."""

    def __init__(self, volume_file, waterplane_file, water_density, buoyant_volume, cov):
        self.volume_data = pd.read_csv(volume_file, delimiter=",", skiprows=1)
        self.waterplane_data = pd.read_csv(waterplane_file, delimiter=",", skiprows=1)

        self.percentage = self.volume_data[" Tankfilling [% of h_tank]"].to_numpy(dtype=float)
        self.volume = self.volume_data[" Tankvolume [m3]"].to_numpy(dtype=float)
        self.lcg = self.volume_data[" lcg [m]"].to_numpy(dtype=float)
        self.tcg = self.volume_data[" tcg [m]"].to_numpy(dtype=float)
        self.vcg = self.volume_data[" vcg [m]"].to_numpy(dtype=float)

        # Interne standaard: kg, m, kgm.
        self.mass = self.volume * float(water_density)
        self.lM = self.mass * (self.lcg - float(cov[0]))
        self.tM = self.mass * self.tcg
        self.Ix = self.waterplane_data[" Inertia_x [m4]"].to_numpy(dtype=float)
        self.GG = self.Ix / float(buoyant_volume)

        # Handig voor kwaliteitschecks.
        self.percentage_min = float(np.min(self.percentage))
        self.percentage_max = float(np.max(self.percentage))
        self.lcg_min = float(np.min(self.lcg))
        self.lcg_max = float(np.max(self.lcg))
        self.mass_min = float(np.min(self.mass))
        self.mass_max = float(np.max(self.mass))
        self.tM_min = float(np.min(self.tM))
        self.tM_max = float(np.max(self.tM))

    def percentage_filled(self, percentage):
        """Vul exacte tankeigenschappen voor één vullingspercentage."""
        self.exact_percentage = _interpoleer_begrensd(
            self.percentage,
            self.percentage,
            float(percentage),
            "tank percentage",
        )
        self.exact_lM = _interpoleer_begrensd(
            self.percentage, self.lM, self.exact_percentage, "tank lM"
        )
        self.exact_tM = _interpoleer_begrensd(
            self.percentage, self.tM, self.exact_percentage, "tank tM"
        )
        self.exact_lcg = _interpoleer_begrensd(
            self.percentage, self.lcg, self.exact_percentage, "tank lcg"
        )
        self.exact_tcg = _interpoleer_begrensd(
            self.percentage, self.tcg, self.exact_percentage, "tank tcg"
        )
        self.exact_vcg = _interpoleer_begrensd(
            self.percentage, self.vcg, self.exact_percentage, "tank vcg"
        )
        self.exact_mass = _interpoleer_begrensd(
            self.percentage, self.mass, self.exact_percentage, "tank massa"
        )
        self.exact_Ix = _interpoleer_begrensd(
            self.percentage, self.Ix, self.exact_percentage, "tank Ix"
        )
        self.exact_GG = _interpoleer_begrensd(
            self.percentage, self.GG, self.exact_percentage, "tank GG"
        )

    def percentage_uit_tM(self, target_tM):
        """Bepaal vullingspercentage uit een doelwaarde voor tM."""
        return _interpoleer_begrensd(self.tM, self.percentage, float(target_tM), "tank tM->percentage")

    def percentage_uit_massa(self, target_mass):
        """Bepaal vullingspercentage uit een doelmassa."""
        return _interpoleer_begrensd(
            self.mass, self.percentage, float(target_mass), "tank massa->percentage"
        )


def deck(
    crane_position=None,
    deck_tp_position=None,
    deck_tp_mass_kg=0.0,
    deck_tp_amount=0,
    jib_length=None,
    jib_angle=0.0,
    slewing_angle=0.0,
    pivot_height=0.0,
    hook_tp_mass_kg=0.0,
    crane_swl_mass_kg=0.0,
    hook_position=None,
):
    """Bouw deklastmatrix [massa, lcg, tcg, vcg] in kg en m.

    Semantiek:
    - `crane_swl_mass_kg` bepaalt alleen kraanhuis/giekmassa.
    - `hook_tp_mass_kg` is de werkelijke gehesen TP-massa.
    - `deck_tp_*` is de deklading (aantal TP's op dek).
    """
    def _normaliseer_deck_posities(tp_position, tp_amount):
        if int(tp_amount) <= 0:
            return []
        if tp_position is None:
            raise DataValidatieFout(
                "Deck TP-posities ontbreken terwijl deck_tp_amount > 0."
            )

        pos_arr = np.asarray(tp_position, dtype=float)
        if pos_arr.ndim == 1:
            if pos_arr.size != 3:
                raise DataValidatieFout(
                    "Enkele deck_tp_position moet precies 3 waarden bevatten."
                )
            return [pos_arr.tolist() for _ in range(int(tp_amount))]

        if pos_arr.ndim == 2 and pos_arr.shape[1] == 3:
            if pos_arr.shape[0] < int(tp_amount):
                raise DataValidatieFout(
                    "Aantal deck TP-posities is kleiner dan deck_tp_amount."
                )
            return [pos_arr[i].tolist() for i in range(int(tp_amount))]

        raise DataValidatieFout(
            "deck_tp_position moet vorm [x,y,z] of [[x,y,z], ...] hebben."
        )

    deck_posities = _normaliseer_deck_posities(deck_tp_position, deck_tp_amount)
    deck_cargo_mass = float(deck_tp_mass_kg)

    # Geen kraan: alleen deklading.
    if crane_position is None or jib_length is None:
        if int(deck_tp_amount) <= 0:
            return np.zeros((4, 0), dtype=float)
        mass = np.full(int(deck_tp_amount), deck_cargo_mass, dtype=float)
        lcg = np.array([p[0] for p in deck_posities], dtype=float)
        tcg = np.array([p[1] for p in deck_posities], dtype=float)
        vcg = np.array([p[2] for p in deck_posities], dtype=float)
        return np.array(
            [
                mass,
                lcg,
                tcg,
                vcg,
            ],
            dtype=float,
        )

    # Met kraan: kraanhuis + giek + haaklast + optioneel deklading.
    jib_angle_rad = math.radians(float(jib_angle))
    slewing_angle_rad = math.radians(float(slewing_angle))

    crane_housing_lcg = float(crane_position[0])
    crane_housing_tcg = float(crane_position[1])
    crane_housing_vcg = float(crane_position[2]) + float(pivot_height)

    crane_housing_mass = 0.34 * float(crane_swl_mass_kg)
    jib_mass = 0.17 * float(crane_swl_mass_kg)

    jib_lcg = crane_housing_lcg + ((float(jib_length) / 2.0) * math.cos(jib_angle_rad)) * math.cos(
        slewing_angle_rad
    )
    jib_tcg = crane_housing_tcg + ((float(jib_length) / 2.0) * math.cos(jib_angle_rad)) * math.sin(
        slewing_angle_rad
    )
    jib_vcg = crane_housing_vcg + (float(jib_length) / 2.0) * math.sin(jib_angle_rad)

    geometrische_haak_lcg = crane_housing_lcg + float(jib_length) * math.cos(jib_angle_rad) * math.cos(
        slewing_angle_rad
    )
    geometrische_haak_tcg = crane_housing_tcg + float(jib_length) * math.cos(jib_angle_rad) * math.sin(
        slewing_angle_rad
    )
    geometrische_haak_vcg = crane_housing_vcg + float(jib_length) * math.sin(jib_angle_rad)

    if hook_position is None:
        load_lcg, load_tcg, load_vcg = (
            geometrische_haak_lcg,
            geometrische_haak_tcg,
            geometrische_haak_vcg,
        )
    else:
        load_lcg, load_tcg, load_vcg = map(float, hook_position)

    mass_deck = [crane_housing_mass, jib_mass, float(hook_tp_mass_kg)]
    lcg_deck = [crane_housing_lcg, jib_lcg, load_lcg]
    tcg_deck = [crane_housing_tcg, jib_tcg, load_tcg]
    vcg_deck = [crane_housing_vcg, jib_vcg, load_vcg]

    for pos in deck_posities:
        mass_deck.append(deck_cargo_mass)
        lcg_deck.append(float(pos[0]))
        tcg_deck.append(float(pos[1]))
        vcg_deck.append(float(pos[2]))

    mass_deck = np.asarray(mass_deck, dtype=float)
    lcg_deck = np.asarray(lcg_deck, dtype=float)
    tcg_deck = np.asarray(tcg_deck, dtype=float)
    vcg_deck = np.asarray(vcg_deck, dtype=float)

    # Houd alleen fysiek aanwezige componenten over.
    mask = mass_deck > 0.0
    if not np.any(mask):
        return np.zeros((4, 0), dtype=float)
    return np.array(
        [mass_deck[mask], lcg_deck[mask], tcg_deck[mask], vcg_deck[mask]], dtype=float
    )


def plates(file_id, hull_thickness, BHD_thickness, material_density, mass_factor, data_dir="data"):
    """Bereken staalmassa's en zwaartepunten van huid en schotten."""
    data_dir = Path(data_dir)
    hull_path = data_dir / f"HullAreaData_Gr{file_id[0]}_V{file_id[1]}.{file_id[2]}.csv"
    bhd_path = data_dir / f"TankBHD_Data_Gr{file_id[0]}_V{file_id[1]}.{file_id[2]}.csv"
    if not hull_path.exists():
        raise DataValidatieFout(f"Bestand ontbreekt: {hull_path}")
    if not bhd_path.exists():
        raise DataValidatieFout(f"Bestand ontbreekt: {bhd_path}")

    hull_data = pd.read_csv(hull_path, delimiter=",", skiprows=1)
    bhd_data = pd.read_csv(bhd_path, delimiter=",", skiprows=1)

    area_hull = hull_data[" Area [m2]"].to_numpy(dtype=float)
    lcg_hull = hull_data[" lca [m]"].to_numpy(dtype=float)
    tcg_hull = hull_data[" tca [m]"].to_numpy(dtype=float)
    vcg_hull = hull_data[" vca [m]"].to_numpy(dtype=float)

    hull_thickness_arr = np.asarray(hull_thickness, dtype=float)
    if hull_thickness_arr.size == 1:
        hull_thickness_arr = np.full_like(area_hull, float(hull_thickness_arr), dtype=float)
    if hull_thickness_arr.size != area_hull.size:
        raise DataValidatieFout(
            "hull_thickness moet 1 waarde bevatten of evenveel waarden als Area [m2]."
        )

    volume_hull = area_hull * hull_thickness_arr
    mass_hull = volume_hull * float(material_density) * float(mass_factor)

    area_bhd = bhd_data["BHD Area [m2]"].to_numpy(dtype=float)
    lcg_bhd = bhd_data[" lcg [m]"].to_numpy(dtype=float)
    tcg_bhd = bhd_data[" tcg [m]"].to_numpy(dtype=float)
    vcg_bhd = bhd_data[" vcg [m]"].to_numpy(dtype=float)

    volume_bhd = area_bhd * float(BHD_thickness)
    mass_bhd = volume_bhd * float(material_density) * float(mass_factor)

    mass_plates = np.append(mass_hull, mass_bhd)
    lcg_plates = np.append(lcg_hull, lcg_bhd)
    tcg_plates = np.append(tcg_hull, tcg_bhd)
    vcg_plates = np.append(vcg_hull, vcg_bhd)
    return np.array([mass_plates, lcg_plates, tcg_plates, vcg_plates], dtype=float)


def ZCG(mass_list, zcg_list):
    """Geef gecombineerd z-zwaartepunt terug uit massa's en z-posities."""
    mass_arr = np.asarray(mass_list, dtype=float)
    zcg_arr = np.asarray(zcg_list, dtype=float)
    total_mass = float(np.sum(mass_arr))
    if total_mass <= 0.0:
        raise InfeasibleLoadCaseError("Totale massa is <= 0 bij ZCG-berekening.")
    return float(np.sum(mass_arr * zcg_arr) / total_mass)


def matrix_add(matrix1, matrix2):
    """Concateneer twee [4 x n]-matrices langs de kolomrichting."""
    matrix1 = np.asarray(matrix1, dtype=float)
    matrix2 = np.asarray(matrix2, dtype=float)
    if matrix1.size == 0:
        return matrix2.copy()
    if matrix2.size == 0:
        return matrix1.copy()
    return np.hstack([matrix1, matrix2])
