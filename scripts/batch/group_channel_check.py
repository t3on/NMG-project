'''
Created on Nov 6, 2012

@author: teon
'''

import eelbrain.eellab as E
import basic.process as process
import os

e = process.NMG()
e.set(raw='hp1_lp40')
channel_check = os.path.join(e.get('results'), 'logs', 'group_channel_check.txt')

tstart = -.1
tstop = .6
reject = 3e-12

tables = []

#with open(channel_check, 'w') as FILE:
#    for _ in e.iter_vars(['subject']):
subjects = ['R0370']
for subject in subjects:
        e.set(subject)
        meg_ds = e.load_events(remove_bad_chs=False)
        meg_ds = meg_ds[meg_ds['target'] == 'target']
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart,
                                            tstop=tstop, baseline=(tstart, 0),
                                            reject={'mag':reject}, preload=True)
        t = E.table.frequencies(E.factor(sum(meg_ds['epochs'].drop_log, [])))
#        FILE.write(e.get('subject') + os.linesep)
#        FILE.write(str(t) + os.linesep * 3)
