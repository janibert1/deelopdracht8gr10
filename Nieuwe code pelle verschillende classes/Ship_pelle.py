"""Generieke scheepsklasse voor evenwicht en aanvangsstabiliteit.

Interne eenheden:
- massa: kilogram [kg]
- lengte: meter [m]
- moment: kilogrammeter [kgm]
"""

from __future__ import annotations

import json
from pathlib import Path
import warnings

import numpy as np

from Functions_pelle import (
    DataValidatieFout,
    InfeasibleLoadCaseError,
    Tank,
    ZCG,
    deck,
    matrix_add,
    plates,
)


class Ship:
    """Generieke scheepsklasse voor alle load cases."""

    def __init__(
        self,
        file,
        crane_position,
        jib_length,
        deck_tp_position,
        deck_tp_amount,
        hull_thickness,
        BHD_thickness,
        tank3_initial,
        slewing_angle,
        jib_angle,
        deck_tp_mass_kg=0.0,
        hook_tp_mass_kg=0.0,
        crane_swl_mass_kg=0.0,
        water_density=1025.0,
        material_density=7850.0,
        mass_factor=2.1,
        data_dir=None,
        fallback_data_dir=None,
        allow_fallback=False,
        pivot_height=0.0,
        hook_position=None,
        tank2_is_movable=False,
        strict_residuen=False,
    ):
        self.file = file
        self.crane_position = crane_position
        self.jib_length = jib_length
        self.deck_tp_position = deck_tp_position
        self.deck_tp_amount = deck_tp_amount
        self.hull_thickness = hull_thickness
        self.BHD_thickness = BHD_thickness
        self.tank3_initial = float(tank3_initial)
        self.slewing_angle = slewing_angle
        self.jib_angle = jib_angle
        self.deck_tp_mass_kg = float(deck_tp_mass_kg)
        self.hook_tp_mass_kg = float(hook_tp_mass_kg)
        self.crane_swl_mass_kg = float(crane_swl_mass_kg)
        self.water_density = float(water_density)
        self.material_density = float(material_density)
        self.mass_factor = float(mass_factor)
        self.allow_fallback = bool(allow_fallback)
        self.pivot_height = float(pivot_height)
        self.hook_position = hook_position
        self.tank2_is_movable = bool(tank2_is_movable)
        self.strict_residuen = bool(strict_residuen)

        self.data_dir = self._resolve_data_dir(data_dir, fallback_data_dir)
        self.main_data = self._load_main_data()
        self._read_main_dimensions()
        self._build_tanks()
        self._calculate_mass_balance()
        self._calculate_stability()
        self._validate_solution()

    def _resolve_data_dir(self, data_dir, fallback_data_dir):
        """Gebruik primaire map, en alleen expliciete fallback als toegestaan."""
        module_dir = Path(__file__).resolve().parent
        primary = Path(data_dir) if data_dir is not None else module_dir / "data"
        fallback = (
            Path(fallback_data_dir)
            if fallback_data_dir is not None
            else module_dir.parent / "Data voorbeeld ship 1 alleskunner met kraan dwarsscheeps"
        )

        if self._is_usable_data_dir(primary):
            return primary.resolve()

        if not self.allow_fallback:
            raise DataValidatieFout(
                f"Datamap ongeldig: {primary}. "
                "Gebruik geldige data of run met allow_fallback=True."
            )

        if self._is_usable_data_dir(fallback):
            warnings.warn(
                f"Lokale data ongeldig ({primary}); fallback wordt gebruikt: {fallback}",
                RuntimeWarning,
            )
            return fallback.resolve()

        raise DataValidatieFout(
            f"Zowel primaire ({primary}) als fallback ({fallback}) data zijn ongeldig."
        )

    def _is_usable_data_dir(self, data_dir):
        """Controleer of vereiste bestanden bestaan en hoofdvelden geldig zijn."""
        data_dir = Path(data_dir)
        main_path = data_dir / f"MainShipParticulars_Gr{self.file[0]}_V{self.file[1]}.{self.file[2]}.json"
        if not main_path.exists():
            return False

        try:
            with open(main_path, "r", encoding="utf-8") as handle:
                main_data = json.load(handle)
            volume_data = main_data["VOLUME RELATED DATA (MOULDED)"]
            buoyant_volume = float(volume_data["Buoyant_Volume_m3"])
            cob = volume_data["COB_m"]
            cov = volume_data["COV_Total_m"]
            if buoyant_volume <= 0.0:
                return False
            if not isinstance(cob, list) or not isinstance(cov, list):
                return False
            if len(cob) < 3 or len(cov) < 3:
                return False
        except Exception:
            return False
        return True

    def _load_main_data(self):
        """Lees hoofd-hydrostatische JSON."""
        path = self.data_dir / f"MainShipParticulars_Gr{self.file[0]}_V{self.file[1]}.{self.file[2]}.json"
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _data_file(self, stem):
        """Maak pad naar versie-afhankelijk databestand."""
        path = self.data_dir / f"{stem}_Gr{self.file[0]}_V{self.file[1]}.{self.file[2]}.csv"
        if not path.exists():
            raise DataValidatieFout(f"Bestand ontbreekt: {path}")
        return path

    def _read_main_dimensions(self):
        """Lees hoofdafmetingen en hydrostatische kenmerken."""
        dimensions = self.main_data["MAIN DIMENSIONS"]
        volume_data = self.main_data["VOLUME RELATED DATA (MOULDED)"]
        underwater_data = self.main_data["DATA OF UNDERWATER AREAS (MOULDED)"]

        self.LOA = float(dimensions["Loa_m"])
        self.width = float(dimensions["B_m"])
        self.height = float(dimensions["H_m"])
        self.LPP = float(dimensions["Lpp_m"])

        self.COB = np.asarray(volume_data["COB_m"], dtype=float)
        self.COV = np.asarray(volume_data["COV_Total_m"], dtype=float)
        self.buoyant_volume = float(volume_data["Buoyant_Volume_m3"])
        self.I = np.asarray(underwater_data["Inertia_WPA_around_COF_m4"], dtype=float)
        if self.buoyant_volume <= 0.0:
            raise DataValidatieFout("Buoyant_Volume_m3 moet > 0 zijn.")

    def _build_tanks(self):
        """Maak tankobjecten en zet initiële tank-3 vulling."""
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
        """Bereken massa-evenwicht en los tank1/tank2 op binnen fysische grenzen."""
        self.deck_data = deck(
            crane_position=self.crane_position,
            deck_tp_position=self.deck_tp_position,
            deck_tp_mass_kg=self.deck_tp_mass_kg,
            deck_tp_amount=self.deck_tp_amount,
            jib_length=self.jib_length,
            jib_angle=self.jib_angle,
            slewing_angle=self.slewing_angle,
            pivot_height=self.pivot_height,
            hook_tp_mass_kg=self.hook_tp_mass_kg,
            crane_swl_mass_kg=self.crane_swl_mass_kg,
            hook_position=self.hook_position,
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
        self.tM_dry = self.dry_data[0] * (self.dry_data[2] - self.COV[1])
        self.dry_mass = float(np.sum(self.dry_data[0]))
        self.dry_lM = float(np.sum(self.lM_dry))
        self.dry_tM = float(np.sum(self.tM_dry))

        # Tank 1 uit dwarsscheeps momentevenwicht.
        self.initial_tM = self.dry_tM + self.tank3.exact_tM
        self.tank1_tM = -self.initial_tM
        self.tank1_percentage = self.tank1.percentage_uit_tM(self.tank1_tM)
        self.tank1.percentage_filled(self.tank1_percentage)

        # Tank 2 uit verticaal krachtevenwicht.
        self.buoyant_mass = self.buoyant_volume * self.water_density
        self.tank2_mass = self.buoyant_mass - (
            self.dry_mass + self.tank1.exact_mass + self.tank3.exact_mass
        )
        self.tank2_percentage = self.tank2.percentage_uit_massa(self.tank2_mass)
        self.tank2.percentage_filled(self.tank2_percentage)

        # Tank 2 langsscheepse positie uit momentevenwicht.
        self.buoyant_lM = self.buoyant_mass * (self.COV[0] - self.COB[0])
        self.initial_lM = (
            self.dry_lM + self.buoyant_lM + self.tank1.exact_lM + self.tank3.exact_lM
        )
        self.tank2_lM = -self.initial_lM
        self.tank2_lcg_solved = (self.tank2_lM / self.tank2_mass) + self.COV[0]
        if self.tank2_is_movable:
            if self.tank2_lcg_solved < self.tank2.lcg_min or self.tank2_lcg_solved > self.tank2.lcg_max:
                raise InfeasibleLoadCaseError(
                    "Berekende tank2_lcg valt buiten geometrisch bereik: "
                    f"lcg={self.tank2_lcg_solved:.4f}, toegestaan=[{self.tank2.lcg_min:.4f}, {self.tank2.lcg_max:.4f}]."
                )
            self.tank2_lcg = self.tank2_lcg_solved
        else:
            self.tank2_lcg = float(self.tank2.exact_lcg)
            if self.tank2_lcg_solved < self.tank2.lcg_min or self.tank2_lcg_solved > self.tank2.lcg_max:
                warnings.warn(
                    "tank2_is_movable=False: opgeloste tank2_lcg valt buiten bereik en wordt niet toegepast.",
                    RuntimeWarning,
                )

        # Gebruik ofwel opgeloste (movable) of vaste (non-movable) tank2_lcg.
        self.tank_data = np.array(
            [
                [self.tank1.exact_mass, self.tank2.exact_mass, self.tank3.exact_mass],
                [self.tank1.exact_lcg, self.tank2_lcg, self.tank3.exact_lcg],
                [self.tank1.exact_tcg, self.tank2.exact_tcg, self.tank3.exact_tcg],
                [self.tank1.exact_vcg, self.tank2.exact_vcg, self.tank3.exact_vcg],
            ],
            dtype=float,
        )
        self.ship_data = matrix_add(self.dry_data, self.tank_data)

    def _calculate_stability(self):
        """Bereken KB, KG, BM en GM."""
        self.KB = float(self.COB[2])
        self.KG = ZCG(self.ship_data[0], self.ship_data[3])
        self.BM = float(
            self.I[0] / self.buoyant_volume
            - (self.tank1.exact_GG + self.tank2.exact_GG + self.tank3.exact_GG)
        )
        self.GM = float(self.KB - self.KG + self.BM)

    def _bereken_residuen(self):
        """Bereken resterende balansfouten in kg en kgm."""
        massa = np.asarray(self.ship_data[0], dtype=float)
        lcg = np.asarray(self.ship_data[1], dtype=float)
        tcg = np.asarray(self.ship_data[2], dtype=float)

        force_residual_kg = float(self.buoyant_mass - np.sum(massa))
        long_m_residual_kgm = float(
            np.sum(massa * (lcg - self.COV[0])) + self.buoyant_mass * (self.COV[0] - self.COB[0])
        )
        trans_m_residual_kgm = float(
            np.sum(massa * (tcg - self.COV[1])) + self.buoyant_mass * (self.COV[1] - self.COB[1])
        )
        return force_residual_kg, long_m_residual_kgm, trans_m_residual_kgm

    def _validate_solution(self):
        """Controleer fysische grenzen en numerieke residuen."""
        for naam, pct in [
            ("tank1", self.tank1_percentage),
            ("tank2", self.tank2_percentage),
            ("tank3", self.tank3_initial),
        ]:
            if pct < 0.0 or pct > 100.0:
                raise InfeasibleLoadCaseError(
                    f"Vullingspercentage buiten [0,100] voor {naam}: {pct:.4f}%."
                )

        force_residual_kg, long_m_residual_kgm, trans_m_residual_kgm = self._bereken_residuen()
        self.force_residual_kg = force_residual_kg
        self.long_m_residual_kgm = long_m_residual_kgm
        self.trans_m_residual_kgm = trans_m_residual_kgm

        force_tol = max(0.001 * self.buoyant_mass, 25.0)
        long_tol = max(0.001 * self.buoyant_mass * max(self.LOA, 1.0), 250.0)
        trans_tol = max(0.001 * self.buoyant_mass * max(self.width, 1.0), 250.0)

        fouten = []
        if abs(force_residual_kg) > force_tol:
            fouten.append(
                f"Verticaal residu te groot: {force_residual_kg:.3f} kg, tolerantie {force_tol:.3f} kg."
            )
        if abs(long_m_residual_kgm) > long_tol:
            fouten.append(
                f"Langsscheeps residu te groot: {long_m_residual_kgm:.3f} kgm, tolerantie {long_tol:.3f} kgm."
            )
        if abs(trans_m_residual_kgm) > trans_tol:
            fouten.append(
                f"Dwarsscheeps residu te groot: {trans_m_residual_kgm:.3f} kgm, tolerantie {trans_tol:.3f} kgm."
            )

        self.residuen_ok = True
        self.residu_melding = None
        if fouten:
            msg = " | ".join(fouten)
            self.residuen_ok = False
            self.residu_melding = msg
            if self.strict_residuen:
                raise InfeasibleLoadCaseError(msg)
            warnings.warn(f"Residuwaarschuwing: {msg}", RuntimeWarning)

    def to_dict(self):
        """Geef compacte resultaatset terug voor output en vergelijking."""
        return {
            "file": self.file,
            "tank1_percentage": float(self.tank1_percentage),
            "tank2_percentage": float(self.tank2_percentage),
            "tank2_lcg": float(self.tank2_lcg),
            "tank2_lcg_solved": float(self.tank2_lcg_solved),
            "KB": float(self.KB),
            "KG": float(self.KG),
            "BM": float(self.BM),
            "GM": float(self.GM),
            "force_residual_kg": float(self.force_residual_kg),
            "long_m_residual_kgm": float(self.long_m_residual_kgm),
            "trans_m_residual_kgm": float(self.trans_m_residual_kgm),
            "residuen_ok": bool(self.residuen_ok),
            "residu_melding": self.residu_melding,
        }
