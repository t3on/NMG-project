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
stats_dir = os.path.join(root, 'results', 'meg', 'stats')
roilabels = ['lh.fusiform', 'vmPFC', 'LATL', 'lh.inferiortemporal', 'LPTL']
log_file = os.path.join(root, 'results', 'logs', 'group_cluster_anova_log.txt')

datasets = []

tstart = -0.1
tstop = 0.6
reject = 3e-12

cstart = .2
wcstart = 0

if os.path.lexists(saved_data):
    group_ds = pickle.load(open(saved_data))
else:
    e = process.NMG()
    e.exclude = {'subject': ['R0580']}
    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events(edf=True)
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        orig_N = meg_ds.N
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            reject={'mag':reject}, preload=True)
        remainder = meg_ds.N*100/orig_N
        e.logger('epochs: %d' % remainder + r'% ' + 'of trials remain' )

        #do source transformation
        for roilabel in roilabels:
            meg_ds[roilabel] = e.make_stcs(meg_ds, 
                                           labels=tuple(e.rois[roilabel]), 
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
    e.print_log(log_file)

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


for roilabel in roilabels:
    # test constituent effect
    title = 'Cluster ANOVA of Wordtype by Constituent Priming in %s' % roilabel
    a = E.testnd.cluster_anova(Y=group_target_constituent[roilabel],
                               X=group_target_constituent['condition'] *
                               group_target_constituent['wordtype'] *
                               group_target_constituent['subject'],
                               tstart=cstart)
    stat = os.path.join(stats_dir, 'group_target_constituent_%s.txt' %roilabel)
    with open(stat ,'w') as FILE:
        FILE.write(title + os.linesep*2)
        FILE.write(str(a.as_table()))
    constituent_clusters[roilabel] = a   
        
    p = E.plot.uts.clusters(a, figtitle = title,
                            t = {'color': 'g', 'linestyle': 'dashed'})
    p.figure.savefig(os.path.join(plots_dir,
                        'group_target_constituent_%s.pdf' % roilabel))

    # test identity effect
    title = 'Cluster ANOVA of Wordtype by Identity Priming in %s' % roilabel
    b = E.testnd.cluster_anova(Y=group_target_identity[roilabel],
                               X=group_target_identity['condition'] *
                               group_target_identity['wordtype'] *
                               group_target_identity['subject'],
                               tstart=cstart)
    stat = os.path.join(stats_dir, 'group_target_identity_%s.txt' %roilabel)
    with open(stat ,'w') as FILE:
        FILE.write(title + os.linesep*2)
        FILE.write(str(b.as_table()))
    identity_clusters[roilabel] = b
    
    p = E.plot.uts.clusters(b, figtitle = title,
                            t = {'color': 'g', 'linestyle': 'dashed'})
    p.figure.savefig(os.path.join(plots_dir,
                            'group_target_identity_%s.pdf' % roilabel))

    # test wordtype effect
    title = 'Cluster ANOVA of Wordtype in %s' % roilabel
    c = E.testnd.cluster_anova(Y=group_prime_wordtype[roilabel],
                               X=group_prime_wordtype['wordtype'] *
                               group_prime_wordtype['subject'],
                               tstart=wcstart)
    stat = os.path.join(stats_dir, 'group_prime_wordtype_%s.txt' %roilabel)
    with open(stat ,'w') as FILE:
        FILE.write(title + os.linesep*2)
        FILE.write(str(c.as_table()))
    wordtype_clusters[roilabel] = c
        
    p = E.plot.uts.clusters(c, figtitle = title,
                            t = {'color': 'g', 'linestyle': 'dashed'})
    p.figure.savefig(os.path.join(plots_dir,
                            'group_prime_wordtype_%s.pdf' % roilabel))
