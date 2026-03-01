# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 14:07:12 2026

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

class Alleskunner(Ship):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        