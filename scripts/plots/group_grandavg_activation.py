'''
Created on Nov 30, 2012

@author: teon
'''

import eelbrain.eellab as E
import os
import basic.process as process
import pickle

e = process.NMG()

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'group_stcs_activation.pickled')
plots_dir = os.path.join(root, 'results', 'plots', 'meg', 'activation')

if os.path.lexists(saved_data):
    group_stcs = pickle.load(open(saved_data))
else:
    tstart = -0.1
    tstop = 0.6
    reject = 3e-12


    stcs = []
    subs = []
    group_stcs = []

    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events()
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]


        #add epochs to the dataset after excluding bad channels
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            #baseline=(tstart, 0), reject={'mag':reject}, preload=True)
                                            reject={'mag':reject}, preload=True)

        #do source transformation
        stcs.append(e.make_stcs(meg_ds, stc_type='evoked', force_fixed=False))
        del meg_ds['epochs']
        subs.append(e.get('subject'))

    #combines the datasets for group
    for stc, sub in zip(stcs, subs):
        stc = stc.summary('source', name='stc')
        group_stcs.append(stc)
    stcs = E.combine(group_stcs)
    subjects = E.factor(subs, name = 'subject')
    group_stcs = E.dataset(stcs, subjects)
    E.save.pickle(group_stcs, saved_data)

p = E.plot.uts.uts(E.plot.unpack(group_stcs['stc'], group_stcs['subject']))
p.figure.savefig(os.path.join(plots_dir, 'group_grandavg_activation.pdf'))
