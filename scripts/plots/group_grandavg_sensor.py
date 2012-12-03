'''
Created on Nov 30, 2012

@author: teon
'''

import eelbrain.eellab as E
import os
import basic.process as process
import pickle

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'group_ds_epochs.pickled')
plots_dir = os.path.join(root, 'results', 'plots', 'meg', 'sensor')

e = process.NMG(root='~/data')

tstart = -0.1
tstop = 0.6
reject = 3e-12

if os.path.lexists(saved_data):
    group_ds = pickle.load(open(saved_data))
else:
    group_ds = []
    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events(edf=True, remove_bad_chs=False)
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]

        #meg_ds = process.reject_blinks(meg_ds)
        if 't_edf' in meg_ds:
            del meg_ds['t_edf']

        #add epochs to the dataset after excluding bad channels
        meg_ds = E.load.fiff.add_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                        baseline=(tstart, 0), reject=reject,
                                        mult=1e12, unit='pT')

        meg_ds = meg_ds.compress(meg_ds['target'], drop_bad=True)

        #Append to group level datasets
        group_ds.append(meg_ds)
    group_ds = E.combine(group_ds)
    E.save.pickle(group_ds, saved_data)


#creates indices for prime and target
prime = group_ds[group_ds['target'] == 'prime']
target = group_ds[group_ds['target'] == 'target']

#prime
E.plot.utsnd.butterfly(E.plot.unpack(prime['MEG'],
    prime['subject'])).figure.savefig(os.path.join(plots_dir, 'primes_grandavg_epochs.pdf'))
#target
E.plot.utsnd.butterfly(E.plot.unpack(target['MEG'],
    target['subject'])).figure.savefig(os.path.join(plots_dir, 'target_grandavg_epochs.pdf'))
