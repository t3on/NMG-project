'''
Created on Nov 26, 2012

@author: teon
'''

import os
import pickle
import eelbrain.eellab as E
import basic.process as process

# raw data parameters
raw = 'hp1_lp40'
tstart = -0.1
tstop = 0.6
reject = {'mag': 3e-12}

# analysis parameters
orient = 'fixed'
e_type = 'evoked'
test = 'target_analysis'
conditions = ['constituent', 'identity']

# initialize experiment
e = process.NMG()
datasets = []

# directory info
plots_dir = e.get('plots_dir', dtype='meg', stat='anovas', orient=orient, mkdir=True)
wf_dir = e.get('wf_dir', dtype='meg', stat='waveforms', orient=orient, mkdir=True)
stats_dir = e.get('stats_dir', dtype='meg', stat='anovas', orient=orient, mkdir=True)

# rois
rois = [['lh.vmPFC', 'rh.vmPFC'], 'lh.ant_fusiform', 'lh.post_fusiform',
        'lh.LATL', 'lh.LPTL']
roilabels = ['vmPFC', 'ant_fusiform', 'post_fusiform', 'LATL', 'LPTL']
roititles = ['vmPFC', 'anterior Fusiform', 'posterior Fusiform', 'LATL',
             'Posterior Temporal Gyrii']

for _ in e.iter_vars(['subject']):
    meg_ds = e.process_evoked(raw=raw, e_type=e_type, tstart=tstart,
                              tstop=tstop, reject=reject)
    if meg_ds is None:
        continue
    # filter
    meg_ds = meg_ds[meg_ds['target'] == 'target']
    # source computation
    meg_ds = e.source_evoked(meg_ds, rois, roilabels, tstart, tstop)
    # append to group level datasets
    datasets.append(meg_ds)
# combines the datasets for group
group_ds = E.combine(datasets)
E.save.pickle(group_ds, e.get('group-file', test=test, orient=orient))
del datasets

#create index for only the constituent conditions
constituent = group_ds['condition'].isany('control_constituent',
                                          'first_constituent')
#creates index for only the identity conditions
identity = group_ds['condition'].isany('control_identity', 'identity')

sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (sub, group_ds['subject'].cells))

for roilabel, roititle in zip(roilabels, roititles):
    for condition in conditions:
        if condition == 'identity':
            sub = identity; tname = 'Identity'
        elif condition == 'constituent':
            sub = constituent; tname = 'Constituent'
        else:
            raise ValueError
        # test constituent effect
        title = ('%s Priming Effects in %s: %s orientation'
                 % (tname, roititle, orient))
        a = E.testnd.cluster_anova(Y=group_ds[roilabel],
                                   X=group_ds.eval('condition*wordtype*subject'),
                                   sub=sub)
        stat = os.path.join(stats_dir, '%s_%s_%s.txt' % (test, condition, roilabel))
        with open(stat , 'w') as FILE:
            FILE.write(title + os.linesep * 2)
            FILE.write(str(a.as_table()))
        # group plots
        p = E.plot.uts.clusters(a, figtitle=title,
                                t={'color': 'g', 'linestyle': 'dashed'})
        p.figure.savefig(os.path.join(plots_dir,
                            '%s_%s_%s.pdf' % (test, condition, roilabel)))

        p = E.plot.uts.stat(Y=group_ds[roilabel], X=group_ds['condition'],
                            sub=sub,
                            figtitle=title, ylabel='dSPM', legend='upper left',
                             width=15, height=9)
        p.figure.savefig(os.path.join(wf_dir, '%s_%s_%s.pdf'
                                      % (test, condition, roilabel)))

#        # subject plots
#        p = E.plot.uts.stat(Y=group_ds[roilabel], X=group_ds['condition'],
#                            sub=sub, Xax=group_ds['subject'], dev=None,
#                            figtitle=title, ylabel='dSPM', legend='upper left',
#                             width=15, height=9)
#        p.figure.savefig(os.path.join(wf_dir, 'subject_%s_%s.pdf'
#                                      % (condition, roilabel)))
#        # group plot (all)
#        p = E.plot.uts.stat(Y=group_ds[roilabel],
#                            X=group_ds['condition'] % group_ds['wordtype'],
#                            sub=sub, figtitle=title, ylabel='dSPM',
#                            colors=e.cm, dev=None,
#                            legend='upper left', width=15, height=9)
#        p.figure.savefig(os.path.join(wf_dir, 'group_%s_by_wordtype_%s.pdf'
#                                      % (condition, roilabel)))
