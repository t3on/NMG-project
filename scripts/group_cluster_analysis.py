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
labels = ['lh.fusiform', ('lh.vmPFC', 'rh.vmPFC'), 'lh.LATL']

labelnames = []
datasets = []

tstart = -0.1
tstop = 0.4
reject = 3e-12

for subject in subjects:

    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')
    index = meg_ds['target'].isany('prime', 'target')

#create picks to remove bad channels
    if subject[1]:
        meg_ds.info['raw'].info['bads'].extend(subject[1])

    meg_ds = meg_ds[index]
    #meg_ds = process.reject_blinks(meg_ds)

    #add epochs to the dataset after excluding bad channels
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), reject={'mag':reject}, preload=True)

    #do source transformation
    for lbl in labels:
        if type(lbl) == tuple:
            lbl2 = lbl[1]
            lbl = lbl[0]
            lblname = '%s+%s' % (lbl, lbl2)
        else:
            lbl2 = None
            lblname = lbl
        labelnames.append(lblname)

        meg_ds = source.make_stc_epochs(meg_ds, tstart=tstart, tstop=tstop, reject=reject, label=lbl, label2=lbl2, force_fixed=True, from_file=True)

    #collapsing across sources using a root-mean squared
        meg_ds[lblname] = meg_ds[lblname].summary('source_space', func=E.statfuncs.RMS, name=lblname)

    #delete subject epochs from memory
    del meg_ds['epochs']

    meg_ds = meg_ds.compress(meg_ds['condition'] % meg_ds['wordtype'], drop_bad=True)


    #Append to group level datasets
    datasets.append(meg_ds)

#combines the datasets for group
group_ds = E.combine(datasets)

#creates indices for prime and target
prime = group_ds['target'] == 'prime'
target = group_ds['target'] == 'target'

#create index for only the constituent conditions
constituent_condition = group_ds['condition'].isany('control_constituent', 'first_constituent')

#creates index for only the identity conditions
identity_condition = group_ds['condition'].isany('control_identity', 'identity')

#creates index for only the prime only identity conditions
wordtype_condition = group_ds['condition'] == 'identity'


#creates the comparisons
group_target_constituent = group_ds[target * constituent_condition]
group_target_identity = group_ds[target * identity_condition]
group_prime_wordtype = group_ds[prime * wordtype_condition]

constituent_clusters = []
identity_clusters = []
wordtype_clusters = []for lblname in labelnames:
    a = E.testnd.cluster_anova(lblname, 'condition' * 'wordtype' * 'subject', ds=group_target_constituent)
    a.figure.savefig(os.path.join(clusters_dir, 'group_target_constituent_%s.png' % lbl))
    constituent_clusters.append(a)

    b = E.testnd.cluster_anova(lblname, 'condition' * 'wordtype' * 'subject', ds=group_target_identity)
    b.figure.savefig(os.path.join(clusters_dir, 'group_target_identity_%s.png' % lbl))
    identity_clusters.append(b)

    c = E.testnd.cluster_anova(lblname, 'wordtype' * 'subject', ds=group_prime_wordtype)
    c.figure.savefig(os.path.join(clusters_dir, 'group_prime_wordtype_%s.png' % lbl))
    wordtype_clusters.append(c)

