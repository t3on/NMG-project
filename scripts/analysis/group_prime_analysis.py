'''
Created on Feb 25, 2013

@author: teon
'''

import os
import pickle
import eelbrain.eellab as E
import basic.process as process

orient = 'fixed'
root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'prime_stcs_%s.pickled' % orient)
plots_dir = os.path.join(root, 'results', 'meg', 'anovas', 'primes', orient)
wf_dir = os.path.join(root, 'results', 'meg', 'waveforms', 'primes', orient)
stats_dir = os.path.join(root, 'results', 'meg', 'anovas', 'primes', orient, 'stats')
roilabels = ['vmPFC', 'lh.LATL', 'lh.fusiform']

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
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        orig_N = meg_ds.N
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            baseline=None,
                                            reject={'mag':reject},
                                            preload=True)
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
        ds = meg_ds.compress(meg_ds['target'] % meg_ds['condition']
                                 % meg_ds['wordtype'], drop_bad=True)
        #Append to group level datasets
        datasets.append(ds)
        del meg_ds, ds
    #combines the datasets for group
    group_ds = E.combine(datasets)
    del datasets
    E.save.pickle(group_ds, saved_data)

sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (sub, group_ds['subject'].cells))

#creates index for only the prime only identity conditions
wordtypes = ['opaque', 'transparent', 'novel']

for roilabel in roilabels:
    for wtype in wordtypes:
        title = 'Cluster ANOVA of %s vs ortho in %s: %s' % (wtype, roilabel, orient)
        idx = (group_ds['condition'] == 'identity') * (group_ds['target'] == 'prime')
        idy = (group_ds['condition']).isany('control_constituent', 'control_identity')
        idy *= (group_ds['target'] == 'target')
        idz = group_ds['wordtype'].isany('ortho', wtype)
        idx = (idx | idy) * idz
        ds = group_ds[idx]
        ds = ds.compress(ds['wordtype'] % ds['subject'], drop_bad=True)
        a = E.testnd.cluster_anova(Y=ds[roilabel],
                                   X=ds.eval('wordtype*subject'))
        stat = os.path.join(stats_dir, 'group_%s_%s_vs_ortho.txt' % (roilabel, wtype))
        with open(stat , 'w') as FILE:
            FILE.write(title + os.linesep * 2)
            FILE.write(str(a.as_table()))
        # analysis plot
        p = E.plot.uts.clusters(a, figtitle=title, axtitle=None,
                                t={'color': 'g', 'linestyle': 'dashed'})
        p.figure.savefig(os.path.join(plots_dir,
                            'group_%s_%s_vs_ortho.pdf' % (roilabel, wtype)))
        # subject plots
        p = E.plot.uts.stat(Y=ds[roilabel], X=ds['wordtype'],
                            Xax=ds['subject'], dev=None,
                            figtitle=title, ylabel='dSPM', legend='upper left',
                            width=15, height=9)
        p.figure.savefig(os.path.join(wf_dir, 'subject_prime_%s_%s_vs_ortho.pdf'
                                      % (roilabel, wtype)))
        # group plot
        p = E.plot.uts.stat(Y=ds[roilabel], X=ds['wordtype'],
                            figtitle=title, ylabel='dSPM', legend='upper left',
                            width=15, height=9)
        p.figure.savefig(os.path.join(wf_dir, 'group_prime_%s_%s_vs_ortho.pdf'
                                      % (roilabel, wtype)))
