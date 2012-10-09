from __future__ import division

import sys
import os
import cPickle as pickle

import numpy as np
import scipy as sp
import matplotlib as mpl
from matplotlib import pyplot as plt

# Eelbrain
from eelbrain import plot
from eelbrain import vessels as V
from eelbrain import analyze as A
import eelbrain.eellab as E
from eelbrain import load as load

# GUI
from eelbrain.wxgui import MEG as gui
import eelbrain.utils.subp as subp


import mne
import eelbrain.eellab as E
import process