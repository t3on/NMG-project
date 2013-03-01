'''
Created on Nov 27, 2012

@author: teon
'''

import eelbrain.eellab as E
import basic.process as process
import os

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
corrs_dir = os.path.join(root, 'results', 'meg', 'plots', 'corrs')
stats_dir = os.path.join(root, 'results', 'meg', 'stats', 'corrs')
logs_dir = os.path.join(root, 'results', 'logs')
saved_data = os.path.join(root, 'data', 'group_ds_tp_corr.pickled')
roilabels = ['lh.fusiform', 'lh.inferiortemporal']

e = process.NMG()
if os.path.lexists(saved_data):
    group_ds = pickle.load(open(saved_data))
else:
    datasets = []

    tstart = -0.1
    tstop = 0.6
    reject = 3e-12

    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events()
        index = meg_ds['condition'].isany('identity')
        index2 = meg_ds['target'] == 'target'
        meg_ds = meg_ds[index]

        index = meg_ds['c1_freq'] != 0
        index2 = np.isnan(meg_ds['c1_freq']) == False
        index3 = meg_ds['word_freq'] != 0
        index4 = np.isnan(meg_ds['word_freq']) == False
        meg_ds = meg_ds[index * index2 * index3 * index4]

        meg_ds['tp'] = meg_ds['word_freq'] / meg_ds['c1_freq']

        #add epochs to the dataset after excluding bad channels
        orig_N = meg_ds.N
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            #baseline=(tstart, 0), reject={'mag':reject}, preload=True)
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
                meg_ds[roilabel] = e.make_stcs(meg_ds, labels=[roilabel],
                                               force_fixed=False)
            #collapsing across sources
            meg_ds[roilabel] = meg_ds[roilabel].summary('source', name='stc')
            #baseline correct source estimates
            meg_ds[roilabel] -= meg_ds[roilabel].summary(time=(tstart, 0))
        del meg_ds['epochs']
        #Append to group level datasets
        datasets.append(meg_ds)
        del meg_ds
    #combines the datasets for group
    group_ds = E.combine(datasets)
    del datasets
    E.save.pickle(group_ds, saved_data)

sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.' % sub)

cstart = 0
cstop = None
ctp = .05
for roilabel in roilabels:
    title = 'Correlation of Transition Probability and ' \
            'Brain Activity in %s' % roilabel
    a = E.testnd.cluster_corr(Y=group_ds[roilabel], X=group_ds['tp'],
                              norm=group_ds['subject'], tstart=cstart,
                              tstop=cstop, tp=ctp)
    file = os.path.join(stats_dir, 'group_tp_%s.txt' % roilabel)
    with open(file, 'w') as FILE:
        FILE.write(title + os.linesep * 4)
        FILE.write(str(a.as_table()))
    p = E.plot.uts.clusters(a, figtitle=title, axtitle=False,
                            t={'linestyle': 'dashed', 'color': 'g'})
    p.figure.savefig(os.path.join(corrs_dir, 'group_tp_%s.pdf' % roilabel),
                     orientation='landscape')
