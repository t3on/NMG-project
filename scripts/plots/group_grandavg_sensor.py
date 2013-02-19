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
log_file = os.path.join(root, 'results', 'logs', 'group_ds_epochs')
plots_dir = os.path.join(root, 'results', 'meg', 'plots', 'sensor')

e = process.NMG(root='~/data')
e.exclude = {}

tstart = -0.1
tstop = 0.6
reject = 3e-12

if os.path.lexists(saved_data):
    group_ds = pickle.load(open(saved_data))
else:
    group_ds = []
    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events()
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        meg_ds = E.load.fiff.add_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                        baseline=(tstart, 0), reject=reject,
                                        mult=1e12, unit='pT',
                                        target=e.get('subject'))
        meg_ds = meg_ds.compress(meg_ds['target'], drop_bad=True)
        #Append to group level datasets
        group_ds.append(meg_ds)
#    group_ds = E.combine(group_ds)
    E.save.pickle(group_ds, saved_data)

prime = []
target = []

#creates indices for prime and target
for i, _ in enumerate(group_ds):
    subject = group_ds[i][0]['subject']
    idx = group_ds[i]['target'] == 'prime'
    prime.append(group_ds[i][idx][subject])
    idx = group_ds[i]['target'] == 'target'
    target.append(group_ds[i][idx][subject])

#prime
E.plot.utsnd.butterfly(prime).figure.savefig(os.path.join(plots_dir, 'primes_grandavg_epochs.pdf'))
#target
E.plot.utsnd.butterfly(target).figure.savefig(os.path.join(plots_dir, 'target_grandavg_epochs.pdf'))
