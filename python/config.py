# config.py
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.integrate import simpson

@dataclass
class Alleskunnerconfig:
    name: str
    lengte: float
    breedte: float
    diepgang: float
    vullingsgraad_tank_3: float
    vrijboord: float = 3.0
    rho: float = 1025
    g: float = 9.81

    @property
    def bouyant_volume(self):
        df = pd.read_csv('Buoyant_CSA_Gr98_V1.csv', skiprows=1)
        x = df.iloc[:, 0].values.astype(float)
        A = df.iloc[:, 1].values.astype(float)
        return simpson(A, x)
    