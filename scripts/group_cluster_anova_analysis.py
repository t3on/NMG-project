import eelbrain.eellab as E
import basic.process as process
import basic.source as source
import os

clusters_dir = os.path.join(os.path.expanduser('~'), 
                        'Dropbox', 'Experiments', 'NMG', 'results', 'clusters')
subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']), 
            ('R0504', ['MEG 031']), ('R0414', []), 
            ('R0547', ['MEG 002']), ('R0574', []), 
            ('R0575', []), ('R0576', ['MEG 143'])]
#('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084'])
rois = ['lh.fusiform', 'lh.vmPFC', 'rh.vmPFC',
          'lh.LATL', 'lh.inferiortemporal', 'lh.LPTL']

labelnames = []
datasets = []

tstart = -0.1
tstop = 0.6
reject = 3e-12

for subject in subjects:
    print subject[0]
    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')
    index = meg_ds['target'].isany('prime', 'target')

#create picks to remove bad channels
    if subject[1]:
        meg_ds.info['raw'].info['bads'].extend(subject[1])

    meg_ds = meg_ds[index]
    
    if 't_edf' in meg_ds:
        del meg_ds['t_edf']
    #meg_ds = process.reject_blinks(meg_ds)

    #add epochs to the dataset after excluding bad channels
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop, 
                                        #baseline=(tstart, 0), reject={'mag':reject}, preload=True)
                                        reject={'mag':reject}, preload=True)

    #do source transformation

    meg_ds['stcs'] = source.make_stcs(meg_ds, labels=rois, force_fixed=False)
    #delete subject epochs from memory
    del meg_ds['epochs']

    #collapsing across sources using a root-mean squared
    meg_ds['stcs'] = meg_ds['stcs'].summary('source',
                        #func=E.statfuncs.RMS, name=lblname)
                        #use of simple mean
                        name='stcs')

    #baseline correct source estimates
    meg_ds['stcs'] -= meg_ds['stcs'].summary(time=(tstart, 0))

    meg_ds = meg_ds.compress(meg_ds['target'] % meg_ds['condition'] 
                             % meg_ds['wordtype'], drop_bad=True)


    #Append to group level datasets
    datasets.append(meg_ds)

#combines the datasets for group
group_ds = E.combine(datasets)

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

constituent_clusters = []
identity_clusters = []
wordtype_clusters = []
for lblname in labelnames:
    a = E.testnd.cluster_anova(Y = group_target_constituent[lblname], 
                               X = group_target_constituent['condition'] * 
                               group_target_constituent['wordtype'] * 
                               group_target_constituent['subject'],
                               tstart = 0)
    E.plot.uts.clusters(a).figure.savefig(os.path.join(clusters_dir, 
                        'group_target_constituent_%s.pdf' % lblname))
    constituent_clusters.append(a)

    b = E.testnd.cluster_anova(Y = group_target_identity[lblname], 
                               X = group_target_identity['condition'] * 
                               group_target_identity['wordtype'] * 
                               group_target_identity['subject'],
                               tstart = 0)
    E.plot.uts.clusters(b).figure.savefig(os.path.join(clusters_dir, 
                            'group_target_identity_%s.pdf' % lblname))
    identity_clusters.append(b)

    c = E.testnd.cluster_anova(Y = group_prime_wordtype[lblname], 
                               X = group_prime_wordtype['wordtype'] * 
                               group_prime_wordtype['subject'],
                               tstart = 0)
    E.plot.uts.clusters(c).figure.savefig(os.path.join(clusters_dir, 
                            'group_prime_wordtype_%s.pdf' % lblname))
    wordtype_clusters.append(c)
