'''
Created on Jan 10, 2013

@author: teon
pattern matching for coreg is from Tal Linzen
coreg methods are adapted from Christian Brodbeck's eelbrain.plot.coreg
'''

import re
import numpy as np
from numpy import sin, cos
from scipy.optimize import leastsq
from mne.fiff.constants import FIFF

class coreg:

    """
    Attributes
    ----------

    mrk_fname : str
        Path to marker avg file (saved as text form MEG160).

    elp_fname : str
        Path to elp digitizer file.

    """
    def __init__(self, mrk_fname, elp_fname):
        """
        points : np.array
        array with shape point by coordinate (x, y, z)

        """
        # marker point extraction
        self.mrk_src_path = mrk_fname

        # pattern by Tal:
        p = re.compile(r'Marker \d:   MEG:x= *([\.\-0-9]+), y= *([\.\-0-9]+), z= *([\.\-0-9]+)')
        str_points = p.findall(open(mrk_fname).read())
        self.mrk_points = np.array(str_points, dtype=float)

        # elp point extraction
        self.elp_src_path = elp_fname

        # pattern modified from Tal's mrk pattern:
        p = re.compile('%N\t\d-[A-Z]+\s+([\.\-0-9]+)\t([\.\-0-9]+)\t([\.\-0-9]+)')
        str_points = p.findall(open(elp_fname).read())
        self.elp_points = np.array(str_points, dtype=float)



    def fit(self, include=range(5)):
            """
            Fit the marker points to the digitizer points.

            include : index (numpy compatible)
                Which points to include in the fit. Index should select among
                points [0, 1, 2, 3, 4].
            """
            def err(params):
                T = trans(*params[:3]) * rot(*params[3:])
                est = T * self.elp_points[include]
                tgt = self.mrk_points()[include]
                return (tgt - est).ravel()

            # initial guess
            params = (0, 0, 0, 0, 0, 0)
            params, _ = leastsq(err, params)
            self.est_params = params

            # head-to-device
            T = trans(*params[:3]) * rot(*params[3:])
            # returns dev2head by applying the inverse
            return np.array(T.I)

def trans(x=0, y=0, z=0):
    "MNE manual p. 95"
    m = np.matrix([[1, 0, 0, x],
                   [0, 1, 0, y],
                   [0, 0, 1, z],
                   [0, 0, 0, 1]], dtype=float)
    return m

def rot(x=0, y=0, z=0):
    "From eelbrain.plot.coreg"
    r = np.matrix([[cos(y) * cos(z), -cos(x) * sin(z) + sin(x) * sin(y) * cos(z), sin(x) * sin(z) + cos(x) * sin(y) * cos(z), 0],
                  [cos(y) * sin(z), cos(x) * cos(z) + sin(x) * sin(y) * sin(z), -sin(x) * cos(z) + cos(x) * sin(y) * sin(z), 0],
                  [-sin(y), sin(x) * cos(y), cos(x) * cos(y), 0],
                  [0, 0, 0, 1]], dtype=float)
    return r

class dig:
    def __init__(self, hsp_fname):
        self.hsp_src_path = hsp_fname
        # pattern modified from Tal's mrk pattern:
        p = re.compile('//No of rows, no of columns; position of digitized points\s(\d*)\t(\d)\s*')
        v = re.split(p, open(hsp_fname).read())[1:]
        hsp_points = np.fromstring(v[-1], sep='\t').reshape(int(v[0]), int(v[1]))
        self.hsp_points = []
        for idx, point in enumerate(hsp_points):
            point_dict = {}
            point_dict['coord_frame'] = FIFF.FIFFV_COORD_HEAD
            point_dict['ident'] = idx + 1
            point_dict['kind'] = FIFF.FIFFV_POINT_CARDINAL # equivalent in value but may not be the proper constant
            point_dict['r'] = point
            self.hsp_points.append(point_dict)


