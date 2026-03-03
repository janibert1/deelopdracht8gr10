"""Main entry point for the class-based ship calculation project."""

from pathlib import Path

import numpy as np

from AlleskunnerClass import Alleskunner
from KraanschipClass import KraanSchip
from TransportschipClass import TransportSchip


def print_result(name, ship):
    """Print compact summary of the most relevant output values."""
    result = ship.to_dict()
    print(f"\n{name}")
    print(f"  Tank 1 fill [%]: {result['tank1_percentage']:.4f}")
    print(f"  Tank 2 fill [%]: {result['tank2_percentage']:.4f}")
    print(f"  Tank 2 lcg [m]: {result['tank2_lcg']:.4f}")
    print(f"  GM [m]: {result['GM']:.4f}")


def main():
    """Build and run the three ship-type calculations for one scenario."""
    file_id = [98, 1, 0]  # [group, version, subversion]
    data_dir = Path(__file__).resolve().parent / "data"

    # Constants
    tank3_initial = 70
    hull_thickness = np.array([0.012, 0.012, 0.012])  # [transom, shell, deck]
    BHD_thickness = 0.012
    mass_factor = 2.1
    material_density = 7850
    water_density = 1025

    crane_position = [11, 0, 6]
    TP_position = [76.0925, 0, 18]
    TP_mass = 2256300.0
    TP_amount = 4
    jib_length = 40
    jib_angle = 45
    slewing_angle = 180
    pivot_height = 1.0

    shared_kwargs = dict(
        hull_thickness=hull_thickness,
        BHD_thickness=BHD_thickness,
        tank3_initial=tank3_initial,
        water_density=water_density,
        material_density=material_density,
        mass_factor=mass_factor,
        data_dir=data_dir,
    )

    transport = TransportSchip(
        file=file_id,
        TP_position=TP_position,
        TP_mass=TP_mass,
        TP_amount=TP_amount,
        **shared_kwargs,
    )

    kraanschip = KraanSchip(
        file=file_id,
        crane_position=crane_position,
        jib_length=jib_length,
        slewing_angle=slewing_angle,
        jib_angle=jib_angle,
        TP_mass=TP_mass,
        TP_position=TP_position,
        pivot_height=pivot_height,
        **shared_kwargs,
    )

    alleskunner = Alleskunner(
        file=file_id,
        crane_position=crane_position,
        jib_length=jib_length,
        slewing_angle=slewing_angle,
        jib_angle=jib_angle,
        TP_position=TP_position,
        TP_mass=TP_mass,
        TP_amount=TP_amount,
        pivot_height=pivot_height,
        **shared_kwargs,
    )

    print_result("TransportSchip", transport)
    print_result("KraanSchip", kraanschip)
    print_result("Alleskunner", alleskunner)


if __name__ == "__main__":
    main()
