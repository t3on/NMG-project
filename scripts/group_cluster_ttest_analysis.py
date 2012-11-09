import eelbrain.eellab as E
import basic.process as process
import basic.source as source
import os


clusters_dir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'results', 'clusters')
subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']), ('R0504', ['MEG 031']),
            ('R0414', []), ('R0547', ['MEG 002']), ('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084']),
            ('R0574', []), ('R0575', []), ('R0576', ['MEG 143'])]
#labels = ['lh.fusiform', ('lh.vmPFC', 'rh.vmPFC'), 'lh.LATL']
labels = [('lh.vmPFC', 'rh.vmPFC')]
labelnames = []
datasets = []

tstart = -0.1
tstop = 0.5
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
        if type(lbl) == tuple:
            lbl2 = lbl[1]
            lbl = lbl[0]
            lblname = '%s+%s' % (lbl, lbl2)
        else:
            lbl2 = None
            lblname = lbl
        labelnames.append(lblname)

        source.make_stc_epochs(meg_ds, tstart=tstart, tstop=tstop, reject=reject, label=lbl, label2=lbl2, force_fixed=True)

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

#creates index for only the prime only identity conditions
wordtype_condition = group_ds['condition'] == 'identity'


#creates the comparisons
group_prime_wordtype = group_ds[prime * wordtype_condition]

wordtypes = ['transparent', 'opaque', 'novel']
wordtype_clusters = []
for lblname in labelnames:
    for wordtype in wordtypes:
        test = group_prime_wordtype[group_prime_wordtype['wordtype'].isany(wordtype, 'ortho')]
        a = E.testnd.cluster_anova(test[lblname], test['wordtype'] * test['subject'])
        E.plot.uts.clusters(a).figure.savefig(os.path.join(clusters_dir, 'group_prime_ttest_%s_%s.png' % (wordtype, lblname)))
        wordtype_clusters.append(a)
