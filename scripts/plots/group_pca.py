'''
Created on Sep 4, 2012

@author: teon
'''

import eelbrain.eellab as E
import os
import basic.process as process
from eelbrain.wxgui import MEG as gui

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
plots_dir = os.path.join(root, 'results', 'visuals', 'pca')

e = process.NMG(root='~/data')

for _ in e.iter_vars(['subject']):
    meg_ds = e.load_events(proj = False)
    meg_ds = meg_ds[meg_ds['target'] == 'target']
    meg_ds = E.load.fiff.add_epochs(meg_ds, tstart=-0.2, tstop=0.6, 
                                    baseline=(-.2,0))
    p = gui.pca(meg_ds, Y='MEG', nplots=(1, 1), dpi=50, figsize=(10, 6))
    p.figure.savefig(os.path.join(plots_dir, '%s_pca.pdf' % e.get('subject')))
