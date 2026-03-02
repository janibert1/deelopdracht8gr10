# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 14:54:01 2026

@author: ellin
"""

from scipy.interpolate import interp1d, CubicSpline
from scipy.integrate import trapezoid, simpson
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import random
import math
import os

from Class import Ship
from TransportschipClass import TransportSchip

file = [98,1,0] #[group, version, subversion]

#constants
tank3_initial = 70
hull_thickness = np.array([0.012, 0.012, 0.012]) #[transom, shell, deck]
BHD_thickness = 0.012
mass_factor = 2.1
material_density = 7850
water_density = 1025
crane_position = [11,0,6]
TP_position = [76.0925,0,18]
TP_mass = 2256300.0
TP_amount = 4
jib_length = 40
jib_angle = 45
slewing_angle = 180

#voorbeeld = Ship(file, crane_position, jib_length, TP_position, TP_amount, 
                 #hull_thickness, BHD_thickness, tank3_initial, slewing_angle, 
                # jib_angle, TP_mass, water_density, material_density, 
                # mass_factor)

transportschip2 = TransportSchip(file=file,
    TP_position=TP_position,
    TP_mass=TP_mass,
    TP_amount=TP_amount,
    hull_thickness=hull_thickness,
    BHD_thickness=BHD_thickness,
    tank3_initial=tank3_initial,
    slewing_angle=slewing_angle,
    jib_angle=jib_angle,
    water_density=water_density,
    material_density=material_density,
    mass_factor=mass_factor)
