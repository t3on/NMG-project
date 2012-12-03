'''
Created on Nov 26, 2012

@author: teon
'''

import os
import pickle
import eelbrain.eellab as E
import basic.process as process

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'group_ds_stcs.pickled')
plots_dir = os.path.join(root, 'results', 'meg', 'plots', 'clusters')

datasets = []

tstart = -0.1
tstop = 0.6
reject = 3e-12

cstart = .2
wcstart = 0

e = process.NMG()

if os.path.lexists(saved_data):
    group_ds = pickle.load(open(saved_data))
else:
    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events(edf=True)
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            reject={'mag':reject}, preload=True)

        #do source transformation
        for roi, roilabel in e.rois:
            meg_ds[roilabel] = e.make_stcs(meg_ds, labels=tuple(roi), 
                                           force_fixed=False)

            #mean source activity
            meg_ds[roilabel] = meg_ds[roilabel].summary('source', name='stc')
            #baseline correct source estimates
            meg_ds[roilabel] -= meg_ds[roilabel].summary(time=(tstart, 0))

        del meg_ds['epochs']
        meg_ds = meg_ds.compress(meg_ds['target'] % meg_ds['condition']
                                 % meg_ds['wordtype'], drop_bad=True)

        #Append to group level datasets
        datasets.append(meg_ds)

    #combines the datasets for group
    group_ds = E.combine(datasets)
    E.save.pickle(group_ds, saved_data)

#creates indices for prime and target
prime = group_ds['target'] == 'prime'
target = group_ds['target'] == 'target'

#create index for only the constituent conditions
constituent_condition = group_ds['condition'].isany('control_constituent',
                                                    'first_constituent')

#creates index for only the identity conditions
identity_condition = group_ds['condition'].isany('control_identity',
                                                 'identity')

#creates index for only the prime only identity conditions
wordtype_condition = group_ds['condition'] == 'identity'


#creates the comparisons
group_target_constituent = group_ds[target * constituent_condition]
group_target_identity = group_ds[target * identity_condition]
group_prime_wordtype = group_ds[prime * wordtype_condition]

constituent_clusters = {}
identity_clusters = {}
wordtype_clusters = {}
for _, roilabel in e.rois:
    # test constituent effect
    a = E.testnd.cluster_anova(Y=group_target_constituent[roilabel],
                               X=group_target_constituent['condition'] *
                               group_target_constituent['wordtype'] *
                               group_target_constituent['subject'],
                               tstart=cstart)
    E.plot.uts.clusters(a).figure.savefig(os.path.join(plots_dir,
                        'group_target_constituent_%s.pdf' % roilabel))
    constituent_clusters[roilabel] = a   

    # test identity effect
    b = E.testnd.cluster_anova(Y=group_target_identity[roilabel],
                               X=group_target_identity['condition'] *
                               group_target_identity['wordtype'] *
                               group_target_identity['subject'],
                               tstart=cstart)
    E.plot.uts.clusters(b).figure.savefig(os.path.join(plots_dir,
                            'group_target_identity_%s.pdf' % roilabel))
    identity_clusters[roilabel] = b

    # test wordtype effect
    c = E.testnd.cluster_anova(Y=group_prime_wordtype[roilabel],
                               X=group_prime_wordtype['wordtype'] *
                               group_prime_wordtype['subject'],
                               tstart=wcstart)
    E.plot.uts.clusters(c).figure.savefig(os.path.join(plots_dir,
                            'group_prime_wordtype_%s.pdf' % roilabel))
    wordtype_clusters[roilabel] = c
