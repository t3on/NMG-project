'''
Created on Feb 25, 2013

@author: teon
'''

import os
import eelbrain.eellab as E
import basic.process as process

# raw data parameters
raw = 'hp1_lp40'
tstart = -0.1
tstop = 0.6
reject = {'mag': 3e-12}

# analysis parameter
orient = 'free'
e_type = 'evoked'
test = 'prime_analysis'

# initialize experiment
e = process.NMG()
datasets = []

# directory info
plots_dir = e.get('plots_dir', dtype='meg', stat='anovas', orient=orient, mkdir=True)
wf_dir = e.get('wf_dir', dtype='meg', stat='waveforms', orient=orient, mkdir=True)
stats_dir = e.get('stats_dir', dtype='meg', stat='anovas', orient=orient, mkdir=True)

# rois
rois = [['lh.vmPFC', 'rh.vmPFC'], 'lh.LATL', 'lh.fusiform']
roilabels = ['vmPFC', 'LATL', 'fusiform']

for _ in e.iter_vars(['subject']):
    meg_ds = e.process_evoked(raw=raw, e_type=e_type, tstart=tstart,
                              tstop=tstop, reject=reject)
    if meg_ds is None:
        continue
    # filter
    idx = meg_ds['target'] == 'prime'
    idy = meg_ds['condition'] == 'identity'
    meg_ds = meg_ds[idx * idy]
    # source computation
    meg_ds = e.source_evoked(meg_ds, rois, roilabels, tstart, tstop)
    # append to group level datasets
    datasets.append(meg_ds)

#combines the datasets for group
group_ds = E.combine(datasets)
E.save.pickle(group_ds, e.get('group-file', test=test, orient=orient))
del datasets

sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (sub, group_ds['subject'].cells))

# creates index for only the prime only identity conditions
wordtypes = ['opaque', 'transparent', 'novel']

for roilabel in roilabels:
    for wtype in wordtypes:
        title = 'Cluster ANOVA of %s vs ortho in %s: %s' % (wtype, roilabel, orient)
        idx = group_ds['wordtype'].isany('ortho', wtype)
        ds = group_ds[idx]
        ds = ds.compress(ds['wordtype'] % ds['subject'], drop_bad=True)
        a = E.testnd.cluster_anova(Y=ds[roilabel],
                                   X=ds.eval('wordtype*subject'))
        stat = os.path.join(stats_dir, '%s_%s_%s_vs_ortho.txt' % (test, roilabel, wtype))
        with open(stat , 'w') as FILE:
            FILE.write(title + os.linesep * 2)
            FILE.write(str(a.as_table()))
        # analysis plot
        p = E.plot.uts.clusters(a, figtitle=title, axtitle=None,
                                t={'color': 'g', 'linestyle': 'dashed'})
        p.figure.savefig(os.path.join(plots_dir,
                            '%s_%s_%s_vs_ortho.pdf' % (test, roilabel, wtype)))
        # subject plots
        p = E.plot.uts.stat(Y=ds[roilabel], X=ds['wordtype'],
                            Xax=ds['subject'], dev=None,
                            figtitle=title, ylabel='dSPM', legend='upper left',
                            width=15, height=9)
        p.figure.savefig(os.path.join(wf_dir, 'subjects',
                                      'subject_%s_%s_%s_vs_ortho.pdf'
                                      % (test, roilabel, wtype)))
        # group plot
        p = E.plot.uts.stat(Y=ds[roilabel], X=ds['wordtype'],
                            figtitle=title, ylabel='dSPM', legend='upper left',
                            width=15, height=9)
        p.figure.savefig(os.path.join(wf_dir, '%s_%s_%s_vs_ortho.pdf'
                                      % (test, roilabel, wtype)))
