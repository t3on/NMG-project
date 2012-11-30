'''
Created on Nov 6, 2012

@author: teon
'''

import eelbrain.eellab as E
import basic.process as process

tstart = -.1
tstop = .6
reject = 3e-12

e = process.NMG()
tables = []

for _ in e.iter_vars('subject'):
    meg_ds = e.load_events()
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, 
                                        tstop=tstop, baseline=(tstart, 0), 
                                        reject={'mag':reject}, preload=True)

    tables.append(E.table.frequencies(
                    E.factor(sum(meg_ds['epochs'].drop_log, []))))
