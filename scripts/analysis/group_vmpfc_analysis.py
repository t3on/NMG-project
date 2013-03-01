'''
Created on Feb 25, 2013

@author: teon
'''

import os
import pickle
import eelbrain.eellab as E
import basic.process as process

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'group_ds_stcs.pickled')
plots_dir = os.path.join(root, 'results', 'meg', 'plots', 'anovas', 'prime')
stats_dir = os.path.join(root, 'results', 'meg', 'stats', 'anovas', 'prime')
roilabels = ['vmPFC']

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
    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events(edf=True)
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        orig_N = meg_ds.N
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            baseline=(tstart, 0),
                                            reject={'mag':reject}, preload=True)
        remainder = meg_ds.N * 100 / orig_N
        e.logger.info('epochs: %d' % remainder + r'% ' + 'of trials remain')
        if remainder < 80:
            e.logger.info('subject %s is excluded due to large number '
                          % e.get('subject') + 'of rejections')
            del meg_ds
            continue
        #do source transformation
        for roilabel in roilabels:
            if roilabel in e.rois:
                meg_ds[roilabel] = e.make_stcs(meg_ds, labels=e.rois[roilabel],
                                               force_fixed=False)
            else:
                meg_ds[roilabel] = e.make_stcs(meg_ds, labels=roilabel,
                                               force_fixed=False)
            #mean source activity
            meg_ds[roilabel] = meg_ds[roilabel].summary('source', name='stc')
            #baseline correct source estimates
            meg_ds[roilabel] -= meg_ds[roilabel].summary(time=(tstart, 0))
        del meg_ds['epochs']
        ds = meg_ds.compress(meg_ds['target'] % meg_ds['condition']
                                 % meg_ds['wordtype'], drop_bad=True)
        #Append to group level datasets
        datasets.append(ds)
        del meg_ds, ds
    #combines the datasets for group
    group_ds = E.combine(datasets)
    del datasets
    E.save.pickle(group_ds, saved_data)

#creates index for only the prime only identity conditions
condition = (group_ds['condition'] == 'identity') * (group_ds['target'] == 'prime')
wordtypes = ['opaque', 'transparent', 'novel']

sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.' % sub)

for roilabel in roilabels:
    for wtype in wordtypes:
        # test constituent effect
        title = 'Cluster ANOVA of Wordtype by Constituent Priming in %s' % roilabel
        idx = group_ds['wordtype'].isany('ortho', wtype)
        idx = idx * condition
        a = E.testnd.cluster_anova(Y=group_ds[roilabel],
                                   X=group_ds.eval('wordtype*subject'),
                                   sub=idx, tstart=cstart)
        stat = os.path.join(stats_dir, 'group_%s_vs_ortho_%s.txt' % (wtype, roilabel))
        with open(stat , 'w') as FILE:
            FILE.write(title + os.linesep * 2)
            FILE.write(str(a.as_table()))

        p = E.plot.uts.clusters(a, figtitle=title,
                                t={'color': 'g', 'linestyle': 'dashed'})
        p.figure.savefig(os.path.join(plots_dir,
                            'group_%s_vs_ortho_%s.pdf' % (wtype, roilabel)))
