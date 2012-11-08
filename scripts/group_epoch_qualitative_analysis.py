import eelbrain.eellab as E
import basic.process as process
import basic.source as source
import copy
import os
import mne

clusters_dir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'results', 'clusters')
subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']), ('R0504', ['MEG 031']),
            ('R0414', []), ('R0547', ['MEG 002']), ('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084']),
            ('R0574', []), ('R0575', []), ('R0576', ['MEG 143'])]

datasets = []

tstart = -0.1
tstop = 0.4
reject = 3e-12

for subject in [subjects[0]]:

    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')
    index = meg_ds['target'].isany('prime', 'target')

#create picks to remove bad channels
    if subject[1]:
        meg_ds.info['raw'].info['bads'].extend(subject[1])

    meg_ds = meg_ds[index]
    #meg_ds = process.reject_blinks(meg_ds)

    #add epochs to the dataset after excluding bad channels
    meg_ds = E.load.fiff.add_epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), threshold=reject)
    meg_ds = meg_ds.compress(meg_ds['target'] % meg_ds['condition'] % meg_ds['wordtype'], drop_bad=True)

    #Append to group level datasets
    datasets.append(meg_ds)

#combines the datasets for group
group_ds = E.combine(datasets)
group_ds = group_ds.compress(group_ds['target'], drop_bad=True)

#creates indices for prime and target
prime = group_ds[group_ds['target'] == 'prime']
target = group_ds[group_ds['target'] == 'target']

#prime
E.plot.topo.butterfly(prime['MEG']).figure.save
#target
E.plot.topo.butterfly(target['MEG'])
