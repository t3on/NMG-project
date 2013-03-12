'''
Created on Nov 26, 2012

@author: teon
'''

import os
import pickle
import eelbrain.eellab as E
import basic.process as process

orient = 'free'
root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'target_stcs_%s.pickled' % orient)
plots_dir = os.path.join(root, 'results', 'meg', 'anovas', 'targets', orient)
stats_dir = os.path.join(root, 'results', 'meg', 'anovas', 'targets', orient, 'stats')
wf_dir = os.path.join(root, 'results', 'meg', 'waveforms', 'targets', orient)
roilabels = ['lh.fusiform', 'vmPFC', 'lh.LATL', 'lh.inferiortemporal', 'lh.LPTL']
conditions = ['constituent', 'identity']

datasets = []

e = process.NMG()
e.set(raw='hp1_lp40')

tstart = -0.1
tstop = 0.6
reject = 3e-12


if orient == 'free':
    fixed = False
elif orient == 'fixed':
    fixed = True
else:
    raise ValueError

if os.path.lexists(saved_data):
    group_ds = pickle.load(open(saved_data))
else:
    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events(edf=True)
        index = meg_ds['target'] == 'target'
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        orig_N = meg_ds.N
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            reject={'mag':reject},
                                            baseline=None,
                                            preload=True, verbose=False)
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
                                               force_fixed=fixed)
            else:
                meg_ds[roilabel] = e.make_stcs(meg_ds, labels=[roilabel],
                               force_fixed=fixed)
            #mean source activity
            meg_ds[roilabel] = meg_ds[roilabel].summary('source', name='stc')
            #baseline correct source estimates
            meg_ds[roilabel] -= meg_ds[roilabel].summary(time=(tstart, 0))
        del meg_ds['epochs']
        ds = meg_ds.compress(meg_ds['condition'] % meg_ds['wordtype'], drop_bad=True)
        #Append to group level datasets
        datasets.append(ds)
        del meg_ds, ds
    #combines the datasets for group
    group_ds = E.combine(datasets)
    del datasets
    E.save.pickle(group_ds, saved_data)

#create index for only the constituent conditions
constituent = group_ds['condition'].isany('control_constituent', 'first_constituent')
#creates index for only the identity conditions
identity = group_ds['condition'].isany('control_identity', 'identity')

sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.' % sub)

for roilabel in roilabels:
    for condition in conditions:
        if condition == 'identity':
            sub = identity; tname = 'Identity'
        elif condition == 'constituent':
            sub = constituent; tname = 'Constituent'
        else:
            raise ValueError
        # test constituent effect
        title = 'Cluster ANOVA of Wordtype by %s Priming in %s: %s' % (tname, roilabel,
                                                                       orient)
        a = E.testnd.cluster_anova(Y=group_ds[roilabel],
                                   X=group_ds.eval('condition*wordtype*subject'),
                                   sub=sub)
        stat = os.path.join(stats_dir, 'group_%s_%s.txt' % (condition, roilabel))
        with open(stat , 'w') as FILE:
            FILE.write(title + os.linesep * 2)
            FILE.write(str(a.as_table()))
        p = E.plot.uts.clusters(a, figtitle=title,
                                t={'color': 'g', 'linestyle': 'dashed'})
        p.figure.savefig(os.path.join(plots_dir,
                            'group_%s_%s.pdf' % (condition, roilabel)))
        # subject plot
        p = E.plot.uts.stat(Y=group_ds[roilabel], X=group_ds['condition'],
                            sub=sub, Xax=group_ds['subject'], dev=None,
                            figtitle=title, ylabel='dSPM', legend='upper left',
                             width=15, height=9)
        p.figure.savefig(os.path.join(wf_dir, 'subject_%s_%s.pdf'
                                      % (condition, roilabel)))
        # group plot
        p = E.plot.uts.stat(Y=group_ds[roilabel], X=group_ds['condition'],
                            sub=sub,
                            figtitle=title, ylabel='dSPM', legend='upper left',
                             width=15, height=9)
        p.figure.savefig(os.path.join(wf_dir, 'group_%s_%s.pdf'
                                      % (condition, roilabel)))
