import eelbrain.eellab as E
import process
import source
import copy
import os
import mne

tstart = -.1
tstop = .6
reject = 3e-12

subjects = ['R0095', 'R0498', 'R0504', 'R0414', 'R0547', 'R0569', 'R0574', 'R0575', 'R0576']

tables = []

for subject in subjects:
    meg_ds = process.load_meg_events(subject)
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), reject={'mag':reject}, preload=True)

    tables.append(E.table.frequencies(E.factor(sum(meg_ds['epochs'].drop_log, []))))
