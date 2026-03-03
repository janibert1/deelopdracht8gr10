"""Main entry point for the class-based ship calculation project.

This script does three things:
1. Defines one input scenario.
2. Runs all three ship-type models for that scenario.
3. Stores results to JSON and a graph in the local `output/` folder.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from AlleskunnerClass import Alleskunner
from KraanschipClass import KraanSchip
from TransportschipClass import TransportSchip


def print_result(name, ship):
    """Print compact summary of the most relevant output values.

    Parameters
    ----------
    name : str
        Display name for the ship type.
    ship : Ship
        Instantiated ship object with computed results.
    """
    result = ship.to_dict()
    print(f"\n{name}")
    print(f"  Tank 1 fill [%]: {result['tank1_percentage']:.4f}")
    print(f"  Tank 2 fill [%]: {result['tank2_percentage']:.4f}")
    print(f"  Tank 2 lcg [m]: {result['tank2_lcg']:.4f}")
    print(f"  GM [m]: {result['GM']:.4f}")


def build_result_payload(file_id, constants, ship_results):
    """Build a JSON-serializable payload for storage in `output/results.json`."""
    payload = {
        "scenario": {
            "file_id": file_id,
            "constants": constants,
        },
        "results": ship_results,
    }
    return payload


def write_results_json(output_dir, payload):
    """Write model outputs to JSON for traceability and comparison."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ship_results.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=4)
    return output_path


def write_results_graph(output_dir, ship_results):
    """Create and save a PNG graph for the computed ship metrics.

    The graph shows:
    - GM per ship type
    - Tank 1 and Tank 2 fill percentage per ship type
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    names = list(ship_results.keys())
    gm_values = [ship_results[name]["GM"] for name in names]
    tank1_values = [ship_results[name]["tank1_percentage"] for name in names]
    tank2_values = [ship_results[name]["tank2_percentage"] for name in names]

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    axes[0].bar(names, gm_values, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    axes[0].set_title("Initial Stability (GM) per Ship Type")
    axes[0].set_ylabel("GM [m]")
    axes[0].axhline(0.0, color="black", linewidth=1)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)

    x = np.arange(len(names))
    width = 0.35
    axes[1].bar(x - width / 2, tank1_values, width=width, label="Tank 1 fill [%]")
    axes[1].bar(x + width / 2, tank2_values, width=width, label="Tank 2 fill [%]")
    axes[1].set_title("Calculated Tank Fill Percentages")
    axes[1].set_ylabel("Fill [% of h_tank]")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)
    axes[1].legend()

    plt.tight_layout()
    output_path = output_dir / "ship_results_graph.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def main():
    """Build and run the three ship-type calculations for one scenario.

    Returns
    -------
    tuple[pathlib.Path, pathlib.Path]
        Paths to the generated JSON file and PNG graph.
    """
    file_id = [98, 1, 0]  # [group, version, subversion]
    data_dir = Path(__file__).resolve().parent / "data"
    output_dir = Path(__file__).resolve().parent / "output"

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

    # Shared model inputs used by each ship type.
    shared_kwargs = dict(
        hull_thickness=hull_thickness,
        BHD_thickness=BHD_thickness,
        tank3_initial=tank3_initial,
        water_density=water_density,
        material_density=material_density,
        mass_factor=mass_factor,
        data_dir=data_dir,
    )

    # Build ship-type specific objects while reusing the same core `Ship` logic.
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

    # Print a quick terminal summary.
    print_result("TransportSchip", transport)
    print_result("KraanSchip", kraanschip)
    print_result("Alleskunner", alleskunner)

    ship_results = {
        "TransportSchip": transport.to_dict(),
        "KraanSchip": kraanschip.to_dict(),
        "Alleskunner": alleskunner.to_dict(),
    }
    constants = {
        "tank3_initial": tank3_initial,
        "hull_thickness": hull_thickness.tolist(),
        "BHD_thickness": BHD_thickness,
        "mass_factor": mass_factor,
        "material_density": material_density,
        "water_density": water_density,
        "crane_position": crane_position,
        "TP_position": TP_position,
        "TP_mass": TP_mass,
        "TP_amount": TP_amount,
        "jib_length": jib_length,
        "jib_angle": jib_angle,
        "slewing_angle": slewing_angle,
        "pivot_height": pivot_height,
    }
    payload = build_result_payload(file_id, constants, ship_results)
    json_path = write_results_json(output_dir, payload)
    graph_path = write_results_graph(output_dir, ship_results)

    print(f"\nSaved JSON results to: {json_path}")
    print(f"Saved graph PNG to:   {graph_path}")
    return json_path, graph_path


if __name__ == "__main__":
    main()
