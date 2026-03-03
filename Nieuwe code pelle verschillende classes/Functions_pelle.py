"""Core utility functions and tank helper class for ship calculations."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline


class Tank:
    """Ballast tank interpolation helper based on volume and waterplane diagrams."""

    def __init__(self, volume_file, waterplane_file, water_density, buoyant_volume, cov):
        self.volume_data = pd.read_csv(volume_file, delimiter=",", skiprows=1)
        self.waterplane_data = pd.read_csv(waterplane_file, delimiter=",", skiprows=1)

        self.meter = self.volume_data["Tankfilling [m]"].to_numpy()
        self.percentage = self.volume_data[" Tankfilling [% of h_tank]"].to_numpy()
        self.volume = self.volume_data[" Tankvolume [m3]"].to_numpy()
        self.lcg = self.volume_data[" lcg [m]"].to_numpy()
        self.tcg = self.volume_data[" tcg [m]"].to_numpy()
        self.vcg = self.volume_data[" vcg [m]"].to_numpy()

        self.mass = self.volume * water_density
        self.lM = self.mass * (self.lcg - cov[0])
        self.tM = self.mass * self.tcg

        self.volume_data[" mass [kg]"] = self.mass
        self.volume_data[" lM [kgm]"] = self.lM
        self.volume_data[" tM [kgm]"] = self.tM

        self.Ix = self.waterplane_data[" Inertia_x [m4]"].to_numpy()
        self.GG = self.Ix / buoyant_volume
        self.waterplane_data[" GG [m]"] = self.GG

    def percentage_filled(self, percentage):
        """Interpolate tank properties for a given fill percentage."""
        self.exact_lM = CubicSpline(self.percentage, self.lM)(percentage)
        self.exact_tM = CubicSpline(self.percentage, self.tM)(percentage)
        self.exact_lcg = CubicSpline(self.percentage, self.lcg)(percentage)
        self.exact_tcg = CubicSpline(self.percentage, self.tcg)(percentage)
        self.exact_vcg = CubicSpline(self.percentage, self.vcg)(percentage)
        self.exact_mass = CubicSpline(self.percentage, self.mass)(percentage)
        self.exact_Ix = CubicSpline(self.percentage, self.Ix)(percentage)
        self.exact_GG = CubicSpline(self.percentage, self.GG)(percentage)


def deck(
    crane_position=None,
    TP_position=None,
    TP_mass=0.0,
    TP_amount=0,
    jib_length=None,
    jib_angle=0.0,
    slewing_angle=0.0,
    pivot_height=0.0,
):
    """Build deck load matrix [mass, lcg, tcg, vcg] for cargo and optional crane."""
    if crane_position is None or jib_length is None:
        if TP_position is None or TP_amount == 0:
            return np.zeros((4, 0))
        cargo_mass = TP_amount * TP_mass
        return np.array(
            [
                [cargo_mass],
                [TP_position[0]],
                [TP_position[1]],
                [TP_position[2]],
            ],
            dtype=float,
        )

    jib_angle_rad = math.radians(jib_angle)
    slewing_angle_rad = math.radians(slewing_angle)

    crane_housing_lcg = crane_position[0]
    crane_housing_tcg = crane_position[1]
    crane_housing_vcg = crane_position[2] + pivot_height

    crane_swl = TP_mass / 0.94 if TP_mass else 0.0
    crane_housing_mass = 0.34 * crane_swl
    jib_mass = 0.17 * crane_swl

    jib_lcg = crane_housing_lcg + ((jib_length / 2) * math.cos(jib_angle_rad)) * math.cos(
        slewing_angle_rad
    )
    jib_tcg = crane_housing_tcg + ((jib_length / 2) * math.cos(jib_angle_rad)) * math.sin(
        slewing_angle_rad
    )
    jib_vcg = crane_housing_vcg + (jib_length / 2) * math.sin(jib_angle_rad)

    load_mass = crane_swl
    load_lcg = crane_housing_lcg + jib_length * math.cos(jib_angle_rad) * math.cos(
        slewing_angle_rad
    )
    load_tcg = crane_housing_tcg + jib_length * math.cos(jib_angle_rad) * math.sin(
        slewing_angle_rad
    )
    load_vcg = crane_housing_vcg + jib_length * math.sin(jib_angle_rad)

    if TP_position is None:
        cargo_lcg, cargo_tcg, cargo_vcg = load_lcg, load_tcg, load_vcg
    else:
        cargo_lcg, cargo_tcg, cargo_vcg = TP_position

    cargo_mass = TP_amount * TP_mass

    mass_deck = np.array([crane_housing_mass, jib_mass, load_mass, cargo_mass], dtype=float)
    lcg_deck = np.array([crane_housing_lcg, jib_lcg, load_lcg, cargo_lcg], dtype=float)
    tcg_deck = np.array([crane_housing_tcg, jib_tcg, load_tcg, cargo_tcg], dtype=float)
    vcg_deck = np.array([crane_housing_vcg, jib_vcg, load_vcg, cargo_vcg], dtype=float)

    return np.array([mass_deck, lcg_deck, tcg_deck, vcg_deck], dtype=float)


def plates(file_id, hull_thickness, BHD_thickness, material_density, mass_factor, data_dir="data"):
    """Calculate hull and bulkhead steel masses and centers of gravity."""
    data_dir = Path(data_dir)
    hull_path = data_dir / f"HullAreaData_Gr{file_id[0]}_V{file_id[1]}.{file_id[2]}.csv"
    bhd_path = data_dir / f"TankBHD_Data_Gr{file_id[0]}_V{file_id[1]}.{file_id[2]}.csv"

    hull_data = pd.read_csv(hull_path, delimiter=",", skiprows=1)
    bhd_data = pd.read_csv(bhd_path, delimiter=",", skiprows=1)

    area_hull = hull_data[" Area [m2]"].to_numpy()
    lcg_hull = hull_data[" lca [m]"].to_numpy()
    tcg_hull = hull_data[" tca [m]"].to_numpy()
    vcg_hull = hull_data[" vca [m]"].to_numpy()

    hull_thickness_arr = np.asarray(hull_thickness, dtype=float)
    if hull_thickness_arr.size == 1:
        hull_thickness_arr = np.full_like(area_hull, float(hull_thickness_arr), dtype=float)

    volume_hull = area_hull * hull_thickness_arr
    mass_hull = volume_hull * material_density * mass_factor

    area_bhd = bhd_data["BHD Area [m2]"].to_numpy()
    lcg_bhd = bhd_data[" lcg [m]"].to_numpy()
    tcg_bhd = bhd_data[" tcg [m]"].to_numpy()
    vcg_bhd = bhd_data[" vcg [m]"].to_numpy()

    volume_bhd = area_bhd * BHD_thickness
    mass_bhd = volume_bhd * material_density * mass_factor

    mass_plates = np.append(mass_hull, mass_bhd)
    lcg_plates = np.append(lcg_hull, lcg_bhd)
    tcg_plates = np.append(tcg_hull, tcg_bhd)
    vcg_plates = np.append(vcg_hull, vcg_bhd)

    return np.array([mass_plates, lcg_plates, tcg_plates, vcg_plates], dtype=float)


def ZCG(mass_list, zcg_list):
    """Return combined z-center of gravity from masses and z-locations."""
    moment = np.sum(mass_list * zcg_list)
    total_mass = np.sum(mass_list)
    return moment / total_mass


def array_add(arr1, arr2, arr3):
    """Concatenate three vectors."""
    return np.append(np.append(arr1, arr2), arr3)


def matrix_add(matrix1, matrix2):
    """Concatenate two [4 x n] matrices along columns."""
    matrix1 = np.asarray(matrix1, dtype=float)
    matrix2 = np.asarray(matrix2, dtype=float)

    if matrix1.size == 0:
        return matrix2.copy()
    if matrix2.size == 0:
        return matrix1.copy()
    return np.hstack([matrix1, matrix2])
