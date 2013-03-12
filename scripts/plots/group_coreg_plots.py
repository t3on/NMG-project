'''
Created on Dec 11, 2012

@author: teon
'''
import basic.process as process
from mayavi import mlab

e = process.NMG()

for _ in e.iter_vars():
    e.makeplt_coreg(redo=True, analysis='coreg')
