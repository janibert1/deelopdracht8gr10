# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 16:16:45 2026

@author: ellin
"""

from scipy.interpolate import interp1d, CubicSpline
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import random
import math
import os

from Class import Ship
from Functions import Tank, deck, plates, ZCG, matrix_add

class KraanSchip(Ship):
    def __init__(self, file, crane_position, jib_length, slewing_angle, jib_angle, **kwargs):
        super().__init__(file=file, TP_position=None, TP_mass=0, 
                         TP_amount=0, crane_position=craneposition, 
                         jib_length=jib_length, **kwargs)