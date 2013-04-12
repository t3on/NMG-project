'''
Created on Nov 26, 2012

@author: teon
'''

import os
import pickle
import eelbrain.eellab as E
import basic.process as process

# raw data parameters
filter = 'hp1_lp40'
tstart = -0.1
tstop = 0.6
reject = 3e-12

# analysis parameter
orient = 'fixed'
e_type = 'evoked'
conditions = ['constituent', 'identity']

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
plots_dir = os.path.join(root, 'results', 'meg', 'anovas', 'targets', orient)
stats_dir = os.path.join(root, 'results', 'meg', 'anovas', 'targets', orient, 'stats')
wf_dir = os.path.join(root, 'results', 'meg', 'waveforms', 'targets', orient)

# rois
vmPFC = ['lh.vmPFC', 'rh.vmPFC']
#roilabels = ['lh.ant_fusiform', 'lh.post_fusiform']
#roilabels = ['lh.inferiortemporal', vmPFC, 'lh.LATL', 'lh.LPTL']
roilabels = ['lh.LPTL']
roititles = ['Posterior Temporal Gyrii']

datasets = []

e = process.NMG()
e.set(raw=filter)
e.set(analysis='_'.join((e_type, filter, str(tstart), str(tstop))))

if orient == 'free':
    fixed = False
elif orient == 'fixed':
    fixed = True
else:
    raise ValueError

for _ in e.iter_vars(['subject']):
    if os.path.lexists(e.get('data-file')):
        print e.get('subject')
        meg_ds = pickle.load(open(e.get('data-file')))
    else:
        meg_ds = e.load_events(edf=True)
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        orig_N = meg_ds.n_cases
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            reject={'mag':reject},
                                            baseline=None,
                                            preload=True, verbose=False)
        remainder = meg_ds.n_cases * 100 / orig_N
        e.logger.info('epochs: %d' % remainder + r'% ' + 'of trials remain')
        if remainder < 50:
            e.logger.info('subject %s is excluded due to large number '
                          % e.get('subject') + 'of rejections')
            del meg_ds
            continue
        #do source transformation
        meg_ds = meg_ds.compress(meg_ds['condition'] % meg_ds['wordtype'] %
                                 meg_ds['target'], drop_bad=True)
        E.save.pickle(meg_ds, e.get('data-file', mkdir=True))

    # filter
    meg_ds = meg_ds[meg_ds['target'] == 'target']
    # source computation
    stcs = []
    for ds in meg_ds.itercases():
        stcs.append(e.make_stcs(ds, force_fixed=fixed, stc_type=e_type))
    del meg_ds['epochs']
    # extract rois
    for roilabel in roilabels:
        stc_rois = []
        for stc in stcs:
            if roilabel in e.rois:
                roi = e.read_label(e.rois[roilabel])
                roi = stc.in_label(roi)
                mri = e.get('mrisubject')
                roi = E.load.fiff.stc_ndvar(roi, subject=mri)
                roi = roi.summary('source', name='stc')
                roi.x -= roi.summary(time=(tstart, 0))
                stc_rois.append(roi)
            else:
                roi = e.read_label([roilabel])
                roi = stc.in_label(roi)
                mri = e.get('mrisubject')
                roi = E.load.fiff.stc_ndvar(roi, subject=mri)
                roi = roi.summary('source', name='stc')
                roi.x -= roi.summary(time=(tstart, 0))
                stc_rois.append(roi)
        meg_ds[roilabel] = E.combine(stc_rois)
    # append to group level datasets
    datasets.append(meg_ds)

# combines the datasets for group
group_ds = E.combine(datasets)
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
        stat = os.path.join(stats_dir, 'group_%s_%s.txt' % (condition, roilabel))
        with open(stat , 'w') as FILE:
            FILE.write(title + os.linesep * 2)
            FILE.write(str(a.as_table()))
        # group plots
        p = E.plot.uts.clusters(a, figtitle=title,
                                t={'color': 'g', 'linestyle': 'dashed'})
        p.figure.savefig(os.path.join(plots_dir,
                            'group_%s_%s.pdf' % (condition, roilabel)))

        p = E.plot.uts.stat(Y=group_ds[roilabel], X=group_ds['condition'],
                            sub=sub,
                            figtitle=title, ylabel='dSPM', legend='upper left',
                             width=15, height=9)
        p.figure.savefig(os.path.join(wf_dir, 'group_%s_%s.pdf'
                                      % (condition, roilabel)))

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
