'''
Created on Sep 4, 2012

@author: teon
'''

import eelbrain.eellab as E
import os
import basic.process as process

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
plots_dir = os.path.join(root, 'results', 'visuals', 'pca')

e = process.NMG(root='~/data')

for _ in e.iter_vars(['subject']):
    ds = e.load_events(proj=False)
    ds = ds[ds['target'] == 'target']
    ds = E.load.fiff.add_mne_epochs(ds, tstart= -0.2, tstop=0.6,
                                    baseline=(-.2, 0))
    e.make_proj_for_epochs(ds['epochs'], save=False, save_plot=e.get('proj_plot'))
