"""Eenvoudige regressiecheck voor Gr98 V1.0 voorbeelddata.

Deze script draait de hoofdcode en controleert of de belangrijkste
referentiewaarden binnen tolerantie liggen.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def main():
    basis_map = Path(__file__).resolve().parent
    main_script = basis_map / "Main_pelle.py"

    # Lokale data bevat soms onvolledige hoofdgegevens; fallback expliciet toegestaan.
    cmd = [sys.executable, str(main_script), "--allow-fallback"]
    subprocess.run(cmd, check=True)

    resultaat_pad = basis_map / "output" / "ship_results.json"
    with open(resultaat_pad, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    alles = data["results"]["Alleskunner"]
    tank1_pct = float(alles["tank1_percentage"])
    tank2_pct = float(alles["tank2_percentage"])
    gm = float(alles["GM"])

    expected_tank1_pct = 59.322
    expected_tank2_pct = 85.1747
    expected_gm = 1.0585

    assert abs(tank1_pct - expected_tank1_pct) <= 1.5, (
        f"Tank1 buiten tolerantie: {tank1_pct:.4f} vs {expected_tank1_pct:.4f}"
    )
    assert abs(tank2_pct - expected_tank2_pct) <= 1.5, (
        f"Tank2 buiten tolerantie: {tank2_pct:.4f} vs {expected_tank2_pct:.4f}"
    )
    assert abs(gm - expected_gm) <= 0.15, f"GM buiten tolerantie: {gm:.4f} vs {expected_gm:.4f}"

    print("Regressiecheck Gr98 V1.0: geslaagd.")


if __name__ == "__main__":
    main()
