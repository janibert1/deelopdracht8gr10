# antwoorden.py
from calculations import maak_config
import os
os.chdir('C:/Delft/Opdrachten INV/test')
cfg = maak_config()

print("Volume:", round(cfg.bouyant_volume, 2), "m3")
print("Drijfvermogen:", round(cfg.bouyant_volume * cfg.rho * cfg.g, 0), "N")