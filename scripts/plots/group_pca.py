'''
Created on Sep 4, 2012

@author: teon
'''
import basic.process as process


e = process.NMG(root='~/data')
e.exclude = {}

for _ in e.iter_vars(['subject']):
    projs = e.make_proj(write=False, nprojs=5)
    raw = mne.fiff.Raw(e.get('rawfif'))
    e.ui_select_projs(projs[0], raw, save=False, save_plot=True)
