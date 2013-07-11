'''
Created on Dec 11, 2012

@author: teon
'''
import basic.process as process

e = process.NMG()
e.exclude = {}

for _ in e.iter_vars():
    e.plot_coreg(redo=True)
    