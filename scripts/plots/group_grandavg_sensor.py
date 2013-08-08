'''
Created on Nov 30, 2012
 
@author: teon
'''
 
import eelbrain.eellab as E
import os
import basic.process as process
import pickle
 
# raw data parameters
filter = 'hp1_lp40'
tstart = -0.1
tstop = 0.6
reject = 3e-12
 
# analysis parameters
e_type = 'epochs'
redo = True
 
 
root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
plots_dir = os.path.join(root, 'results', 'meg', 'qualitative')
 
# experiment parameters
e = process.NMG(root='~/data')
e.set(raw=filter)
e.set(analysis='_'.join((e_type, filter, str(tstart), str(tstop))))
 
group_ds = []
 
for _ in e.iter():
    if os.path.lexists(e.get('data-file')) and ~redo:
        print e.get('subject')
        meg_ds = pickle.load(open(e.get('data-file')))
    else:
        meg_ds = e.load_events()
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]
 
        #add epochs to the dataset after excluding bad channels
        meg_ds = E.load.fiff.add_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                        baseline=(tstart, 0), reject=reject,
                                        mult=1e12, unit='pT',
                                        target = e.get('subject'))
        meg_ds = meg_ds.compress(meg_ds['target'], drop_bad=True)
        E.save.pickle(meg_ds, e.get('data-file', mkdir=True))
 
    #Append to group level datasets
    group_ds.append(meg_ds)
 
# group_ds = E.combine(group_ds)
  
prime = []
target = []
  
#creates indices for prime and target
for i, _ in enumerate(group_ds):
    subject = group_ds[i]['subject'][0]
    idx = group_ds[i]['target'] == 'prime'
    prime.append(group_ds[i][idx][subject])
    idx = group_ds[i]['target'] == 'target'
    target.append(group_ds[i][idx][subject])

#prime
p = E.plot.utsnd.butterfly(prime)
p.figure.savefig(os.path.join(plots_dir, '%s_primes_grandavg_epochs.pdf' % filter))
#target
p = E.plot.utsnd.butterfly(target)
p.figure.savefig(os.path.join(plots_dir, '%s_targets_grandavg_epochs.pdf' % filter))
