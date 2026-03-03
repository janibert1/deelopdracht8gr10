## Project structure

This class-based variant is organized around one generic ship class and three
specialized ship-type classes.

- `Main_pelle.py`: main entry point and scenario setup.
- `Ship_pelle.py`: generic `Ship` class with equilibrium and stability logic.
- `Functions_pelle.py`: reusable tank/deck/plate helper logic.
- `TransportschipClass.py`: `TransportSchip` (deck cargo, no crane).
- `KraanschipClass.py`: `KraanSchip` (crane condition, no deck cargo).
- `AlleskunnerClass.py`: `Alleskunner` (crane + deck cargo).
- `data/`: generated CSV/JSON input files.

## Run

From this folder:

```bash
python Main_pelle.py
```

## Notes

- Existing formulas and data flow were preserved as much as possible.
- Imports and formatting were cleaned up to match the structuring guidelines.
- If local `data/MainShipParticulars_*.json` is unusable (zero buoyant volume),
  the code automatically falls back to the repository example data folder.
