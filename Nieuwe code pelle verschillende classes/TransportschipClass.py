# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 16:22:22 2026

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

class TransportSchip(Ship):
    def __init__(self, file, TP_position, TP_mass, TP_amount, **kwargs):
        super().__init__(file=file, TP_position=TP_position, TP_mass=TP_mass, 
                         TP_amount=TP_amount, crane_position=None, 
                         jib_length=None, **kwargs)