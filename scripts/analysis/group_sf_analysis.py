'''
Created on Nov 27, 2012

@author: teon
'''

import eelbrain.eellab as E
import basic.process as process
import os

# raw data parameters
filter = 'hp1_lp40'
tstart = -0.1
tstop = 0.6
reject = 3e-12

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
corrs_dir = os.path.join(root, 'results', 'meg', 'corrs')
stats_dir = os.path.join(root, 'results', 'meg', 'corrs', 'stats')
logs_dir = os.path.join(root, 'results', 'logs')
saved_data = os.path.join(root, 'data', 'sf_corr_%s.pickled' % filter)
roilabels = ['lh.fusiform', 'lh.inferiortemporal', 'lh.middletemporal']

e = process.NMG()
e.set(raw=filter)

if os.path.lexists(saved_data):
    group_ds = pickle.load(open(saved_data))
else:

    datasets = []

    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events()
        #eliminate certain trials
        idx = (meg_ds['word_freq'] != 0) * (~np.isnan(meg_ds['word_freq']))
        meg_ds = meg_ds[idx]

        #add epochs to the dataset after excluding bad channels
        orig_N = meg_ds.n_cases
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            baseline=(tstart, 0),
                                            reject={'mag':reject}, preload=True)
        remainder = meg_ds.n_cases * 100 / orig_N
        e.logger.info('epochs: %d' % remainder + r'% ' + 'of trials remain')
        if remainder < 50:
            e.logger.info('subject %s is excluded due to large number '
                          % e.get('subject') + 'of rejections')
            del meg_ds
            continue
        #do source transformation
        for roilabel in roilabels:
            stc = e.make_stcs(meg_ds, labels=[roilabel], stc_type='epochs',
                              force_fixed=False)
#            stc.data = t_map
#            stc = mne.morph_data(subject_from=e.get('mrisubject'),
#                                 subject_to=e._common_brain, stc_from=stc,
#                                 grade=5, n_jobs=2)
            meg_ds[roilabel] = E.load.fiff.stc_ndvar(stc, subject=e.get('mrisubject'))
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
e.logger.info('%d subjects entered into stats.\n %s'
              % (sub, group_ds['subject'].cells))

#cstart = .2
#cstop = None
#ctp = .05
#for roilabel in roilabels:
#    title = 'Correlation of Surface Frequency in %s' % roilabel
#    a = E.testnd.cluster_corr(Y=group_ds[roilabel], X=group_ds['word_freq'],
#                              norm=group_ds['subject'], tstart=cstart,
#                              tstop=cstop, tp=ctp)
#    file = os.path.join(stats_dir, 'group_sf_%s.txt' % roilabel)
#    with open(file, 'w') as FILE:
#        FILE.write(title + os.linesep * 4)
#        FILE.write(str(a.as_table()))
#    p = E.plot.uts.clusters(a, figtitle=title, axtitle=False,
#                            t={'linestyle': 'dashed', 'color': 'g'})
#    p.figure.savefig(os.path.join(corrs_dir, 'group_sf_%s.pdf' % roilabel),
#                     orientation='landscape')
