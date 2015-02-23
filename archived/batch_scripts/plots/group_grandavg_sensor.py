#'''
#Created on Nov 30, 2012
# 
#@author: teon
#'''
# 
#import eelbrain as E
#import os
#import basic.process as process
#import pickle
# 
## raw data parameters
#raw = 'calm_fft_hp1_lp40'
#tstart = -0.1
#tstop = 0.6
#reject = {'mag': 4e-12}
# 
## analysis parameters
#e_type = 'epochs+proj'
#redo = False
#
#e = process.NMG()
#e.set(datatype='meg')
# 
# 
#root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
#plots_dir = os.path.join(root, 'results', 'meg', 'qualitative')
# 
## experiment parameters
#e = process.NMG(None, '{teon-backup_drive}')
#e.set(raw=raw)
#e.set(analysis='_'.join((e_type, raw, str(tstart), str(tstop))))
# 
#group_ds = []
# 
#for _ in e:
#    if os.path.lexists(e.get('data-file')) and ~redo:
#        print e.get('subject')
#        ds = pickle.load(open(e.get('data-file')))
#    else:
#        ds = e.load_events()
#        index = ds['target'].isany('prime', 'target')
#        ds = ds[index]
# 
#        #add epochs to the dataset after excluding bad channels
#        ds = e.make_epochs(ds, mne_obj=False, reject=reject, name=ds.info['subject'])
#        ds = ds.aggregate(ds['target'], drop_bad=True)
#        E.save.pickle(ds, e.get('data-file', mkdir=True))
# 
#    #Append to group level datasets
#    group_ds.append(ds)
 
# group_ds = E.combine(group_ds)
  
prime = []
target = []
  
#creates indices for prime and target
for i, _ in enumerate(group_ds):
    subject = group_ds[i]['subject'][0]
    if subject in group_ds[i]:
        idx = group_ds[i]['target'] == 'prime'
        prime.append(group_ds[i][idx][subject])
        idx = group_ds[i]['target'] == 'target'
        target.append(group_ds[i][idx][subject])

#prime
p = E.plot.Butterfly(prime)
p.figure.savefig(e.get('plot-file', analysis='sensor-prime+proj')) 
#target
p = E.plot.Butterfly(target)
p.figure.savefig(e.get('plot-file', analysis='sensor-target+proj'))
