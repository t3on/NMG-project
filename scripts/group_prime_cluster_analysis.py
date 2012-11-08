import eelbrain.eellab as E
import process
import source
import copy
import os
import mne


subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']), ('R0504', ['MEG 031']),
            ('R0414', []), ('R0547', ['MEG 002']), ('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084']),
            ('R0574', []), ('R0575', []), ('R0576', ['MEG 143'])]

E.utils.kit.split_label(mne.read_label('lh.superiortemporal'))[1] +
E.utils.kit.split_label(mne.read_label('lh.middletemporal'))[1] +
mne.read_label('lh.temporalpole')


labels = ['lh.fusiform', 'lh.medialorbitofrontal', 'lh.temporalpole']
#'lh.parstriangularis', 'lh.superiortemporal', 'lh.lateralorbitofrontal'
#maybe AMF
datasets = []

tstart = -0.1
tstop = 0.4
reject = 3e-12

for subject in subjects:

    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')
    index = meg_ds['target'] == 'prime'

#create picks to remove bad channels
    if subject[1]:
        meg_ds.info['raw'].info['bads'].extend(subject[1])

    meg_ds = meg_ds[index]
    #meg_ds = process.reject_blinks(meg_ds)

    #add epochs to the dataset after excluding bad channels
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), reject={'mag':reject}, preload=True)

    #do source transformation
    for lbl in labels:
        meg_ds = source.make_stc_epochs(meg_ds, tstart=tstart, tstop=tstop, reject=reject, label=lbl, force_fixed=True, from_file=True)

    #collapsing across sources using a root-mean squared
        meg_ds[lbl] = meg_ds[lbl].summary('source_space', func=E.statfuncs.RMS, name=lbl)

    #delete subject epochs from memory
    del meg_ds['epochs']

    meg_ds = meg_ds.compress(meg_ds['condition'] % meg_ds['wordtype'], drop_bad=True)


    #Append to group level datasets
    datasets.append(meg_ds)


#Exports the source estimate ERFs 

#combines the datasets for group
group_ds = E.combine(datasets)

#select only the identity conditions
group_identity = group_ds[group_ds['condition'] == 'identity']


identity_clusters = []for lbl in labels:
    a = E.testnd.cluster_anova(group_identity[lbl], group_identity['wordtype'] * group_identity['subject'])
    a.figure.savefig('/Users/teon/Dropbox/Experiments/NMG/results/clusters/prime_%s.png' % lbl)
    identity_clusters.append(a)
