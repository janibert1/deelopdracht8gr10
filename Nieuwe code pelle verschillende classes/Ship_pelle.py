"""Ship model used by the class-based project variant."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline

from Functions_pelle import Tank, ZCG, deck, matrix_add, plates


class Ship:
    """Generic ship class for equilibrium and initial stability calculations."""

    def __init__(
        self,
        file,
        crane_position,
        jib_length,
        TP_position,
        TP_amount,
        hull_thickness,
        BHD_thickness,
        tank3_initial,
        slewing_angle,
        jib_angle,
        TP_mass=230000.0,
        water_density=1025.0,
        material_density=7850.0,
        mass_factor=2.1,
        data_dir=None,
        pivot_height=0.0,
    ):
        self.file = file
        self.crane_position = crane_position
        self.jib_length = jib_length
        self.TP_position = TP_position
        self.TP_amount = TP_amount
        self.hull_thickness = hull_thickness
        self.BHD_thickness = BHD_thickness
        self.tank3_initial = tank3_initial
        self.slewing_angle = slewing_angle
        self.jib_angle = jib_angle
        self.TP_mass = TP_mass
        self.water_density = water_density
        self.material_density = material_density
        self.mass_factor = mass_factor
        self.pivot_height = pivot_height

        self.data_dir = self._resolve_data_dir(data_dir)
        self.main_data = self._load_main_data()
        self._read_main_dimensions()
        self._build_tanks()
        self._calculate_mass_balance()
        self._calculate_stability()

    def _resolve_data_dir(self, data_dir):
        """Pick a usable data folder; fallback to repository example data if needed."""
        module_dir = Path(__file__).resolve().parent
        candidates = []
        if data_dir is not None:
            candidates.append(Path(data_dir))
        candidates.append(module_dir / "data")
        candidates.append(module_dir.parent / "Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps")

        checked = []
        for candidate in candidates:
            candidate = candidate.resolve()
            if candidate in checked:
                continue
            checked.append(candidate)
            if self._has_usable_main_particulars(candidate):
                return candidate

        raise FileNotFoundError(
            "No usable data folder found for MainShipParticulars and tank files."
        )

    def _has_usable_main_particulars(self, data_dir):
        """Return True when main particulars exist and contain non-zero buoyant volume."""
        main_path = data_dir / f"MainShipParticulars_Gr{self.file[0]}_V{self.file[1]}.{self.file[2]}.json"
        if not main_path.exists():
            return False

        with open(main_path, "r", encoding="utf-8") as handle:
            main_data = json.load(handle)
        buoyant_volume = main_data["VOLUME RELATED DATA (MOULDED)"].get("Buoyant_Volume_m3", 0)
        return isinstance(buoyant_volume, (int, float)) and buoyant_volume > 0

    def _data_file(self, stem):
        """Build full path for a data file with group/version formatting."""
        return self.data_dir / f"{stem}_Gr{self.file[0]}_V{self.file[1]}.{self.file[2]}.csv"

    def _load_main_data(self):
        """Read main hydrostatic particulars JSON."""
        path = self.data_dir / f"MainShipParticulars_Gr{self.file[0]}_V{self.file[1]}.{self.file[2]}.json"
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _read_main_dimensions(self):
        """Read commonly used dimensions and hydrostatics into attributes."""
        dimensions = self.main_data["MAIN DIMENSIONS"]
        volume_data = self.main_data["VOLUME RELATED DATA (MOULDED)"]
        underwater_data = self.main_data["DATA OF UNDERWATER AREAS (MOULDED)"]

        self.LOA = dimensions["Loa_m"]
        self.width = dimensions["B_m"]
        self.height = dimensions["H_m"]
        self.LPP = dimensions["Lpp_m"]

        self.COB = np.asarray(volume_data["COB_m"], dtype=float)
        self.COV = np.asarray(volume_data["COV_Total_m"], dtype=float)
        self.buoyant_volume = float(volume_data["Buoyant_Volume_m3"])
        self.I = np.asarray(underwater_data["Inertia_WPA_around_COF_m4"], dtype=float)

    def _build_tanks(self):
        """Create tank objects and set initial fill for tank 3."""
        self.tank1 = Tank(
            self._data_file("Tank1_Diagram_Volume"),
            self._data_file("Tank1_Diagram_Waterplane"),
            self.water_density,
            self.buoyant_volume,
            self.COV,
        )
        self.tank2 = Tank(
            self._data_file("Tank2_Diagram_Volume"),
            self._data_file("Tank2_Diagram_Waterplane"),
            self.water_density,
            self.buoyant_volume,
            self.COV,
        )
        self.tank3 = Tank(
            self._data_file("Tank3_Diagram_Volume"),
            self._data_file("Tank3_Diagram_Waterplane"),
            self.water_density,
            self.buoyant_volume,
            self.COV,
        )
        self.tank3.percentage_filled(self.tank3_initial)

    def _calculate_mass_balance(self):
        """Calculate deck/steel contributions and solve tank 1 and tank 2 equilibrium."""
        self.deck_data = deck(
            self.crane_position,
            self.TP_position,
            self.TP_mass,
            self.TP_amount,
            self.jib_length,
            self.jib_angle,
            self.slewing_angle,
            pivot_height=self.pivot_height,
        )
        self.plates_data = plates(
            self.file,
            self.hull_thickness,
            self.BHD_thickness,
            self.material_density,
            self.mass_factor,
            data_dir=self.data_dir,
        )
        self.dry_data = matrix_add(self.deck_data, self.plates_data)

        self.lM_dry = self.dry_data[0] * (self.dry_data[1] - self.COV[0])
        self.tM_dry = self.dry_data[0] * self.dry_data[2]
        self.dry_mass = np.sum(self.dry_data[0])
        self.dry_lM = np.sum(self.lM_dry)
        self.dry_tM = np.sum(self.tM_dry)

        self.initial_tM = self.dry_tM + self.tank3.exact_tM
        self.tank1_tM = -self.initial_tM
        self.tank1_percentage = CubicSpline(self.tank1.tM, self.tank1.percentage)(self.tank1_tM)
        self.tank1.percentage_filled(self.tank1_percentage)

        self.buoyant_mass = self.buoyant_volume * self.water_density
        self.tank2_mass = self.buoyant_mass - (
            self.dry_mass + self.tank1.exact_mass + self.tank3.exact_mass
        )
        self.tank2_percentage = CubicSpline(self.tank2.mass, self.tank2.percentage)(self.tank2_mass)
        self.tank2.percentage_filled(self.tank2_percentage)

        self.buoyant_lM = self.buoyant_mass * (self.COV[0] - self.COB[0])
        self.initial_lM = (
            self.dry_lM + self.buoyant_lM + self.tank1.exact_lM + self.tank3.exact_lM
        )
        self.tank2_lM = -self.initial_lM
        self.tank2_lcg = (self.tank2_lM / self.tank2_mass) + self.COV[0]

        self.tank_data = np.array(
            [
                [self.tank1.exact_mass, self.tank2.exact_mass, self.tank3.exact_mass],
                [self.tank1.exact_lcg, self.tank2.exact_lcg, self.tank3.exact_lcg],
                [self.tank1.exact_tcg, self.tank2.exact_tcg, self.tank3.exact_tcg],
                [self.tank1.exact_vcg, self.tank2.exact_vcg, self.tank3.exact_vcg],
            ],
            dtype=float,
        )
        self.ship_data = matrix_add(self.dry_data, self.tank_data)

    def _calculate_stability(self):
        """Compute KB, KG, BM and GM values."""
        self.KB = self.COB[2]
        self.KG = ZCG(self.ship_data[0], self.ship_data[3])
        self.BM = self.I[0] / self.buoyant_volume - (
            self.tank1.exact_GG + self.tank2.exact_GG + self.tank3.exact_GG
        )
        self.GM = self.KB - self.KG + self.BM

    def to_dict(self):
        """Return a compact result dictionary for reporting/comparison lists."""
        return {
            "file": self.file,
            "tank1_percentage": float(self.tank1_percentage),
            "tank2_percentage": float(self.tank2_percentage),
            "tank2_lcg": float(self.tank2_lcg),
            "KB": float(self.KB),
            "KG": float(self.KG),
            "BM": float(self.BM),
            "GM": float(self.GM),
        }
