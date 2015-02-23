"""
Created on Nov 27, 2012

@author: teon
"""

import eelbrain as E
import basic.process as process
import os
import cPickle as pickle
import numpy as np


redo = False

# raw data parameters
raw = 'calm_iir_hp1_lp40'
tmin = -0.1
tmax = 0.6
reject = {'mag':4e-12}
orient = 'fixed'
analysis = 'target-%s-all' % orient
decim = 2

# analysis paramaters
cstart = 0.1
cstop = None
pmin = .05
morph = True
hemi = 'lh'

e = process.NMG(None, '{home}')
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis='target', orient=orient, plot_ext='jpg')
e.exclude['subject'] = ['R0414']
e.set(cov = os.path.join('{fif_sdir}', '{s_e}_{raw}_auto-cov.fif'))

l1 = 'lh.fusiform.label'
labels = [l1]
roi = e.read_label([l1])

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        ds = e.load_events(edf=True, proj=False)
        ds = ds[ds['target'] == 'target']
        ds = ds[ds['condition'].isany('control_constituent', 'first_constituent')]

        ds = e.make_epochs(ds, evoked=True, raw=raw, decim=decim,
                           model='condition % wordtype', reject=reject)
        if ds.info['use']:
            ds = e.analyze_source(ds, evoked=True, orient=orient,
                                  tmin=tmin, morph=morph)
            # Append to group level datasets
            datasets.append(ds)
            del ds
    # combines the datasets for group
    group_ds = E.combine(datasets)
    group_ds['stc'] = group_ds['stc'].sub(source=roi)
    E.save.pickle(group_ds, e.get('group-file'))
    del datasets

n_sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (n_sub, group_ds['subject'].cells))

# Create a report
report = E.Report("Target Analyses", author="Teon")
section = report.add_section("Info")
section.append('%d subjects entered into stats.\n\n %s\n\n'
              % (n_sub, group_ds['subject'].cells))
section.append('Rejection: %s. Cluster start: %s. Decim: %s' % (reject, cstart,
                                                       decim))


wtypes = list(group_ds['wordtype'].cells)
wtypes.remove('ortho')

# interaction = c_timecourse.summary(time=(c_tstart, c_tstop))
ct = E.Celltable(Y='stc', X='wordtype % condition', match='subject',
                 ds=group_ds)
novel = (ct.data[('novel', 'first_constituent')] -
         ct.data[('novel', 'control_constituent')])
opaque = (ct.data[('opaque', 'first_constituent')] -
          ct.data[('opaque', 'control_constituent')])
ortho = (ct.data[('ortho', 'first_constituent')] -
         ct.data[('ortho', 'control_constituent')])
transparent = (ct.data[('transparent', 'first_constituent')] -
               ct.data[('transparent', 'control_constituent')])
Y = E.combine((novel, opaque, ortho, transparent), name='diffs')
X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
             rep=len(group_ds['subject'].cells), name='wordtype')
subjects = E.Factor(group_ds['subject'].cells, tile=len(X.cells),
                    name='subject', random=True)
diffs = E.Dataset(subjects, Y, X)

analyses = []
for wtype in wtypes:
    idx = group_ds['wordtype'].isany('ortho', wtype)
    a = E.testnd.ttest_rel(Y=group_ds['stc'].sub(source=roi), X='wordtype',
                           c0='ortho', c1=wtype, match='subject', tstart=cstart,
                           tstop=cstop, ds=group_ds, tail=1, sub=idx, samples=10000,
                           pmin=pmin)

    analyses.append(a)
    title = 'Spatiotemporal Cluster TTest of %s vs ortho in Inferior Temporal: %s' % (wtype, orient)
    if a.clusters.n_cases > 0:
        for i, cluster in enumerate(a.clusters[a.clusters['p'] < .1].itercases()):
            c_0 = cluster['cluster']
            p = cluster['p']
            section = report.add_section("Cluster %s, p=%s" % (i, p))
            c_extent = c_0.sum('time')
            plt_extent = E.plot.brain.cluster(c_extent)
            image = E.plot.brain.image(plt_extent, "cluster %s extent.png" % i,
                                       alt=None, close=True)
            section.add_image_figure(image, "Extent of the largest "
                                     "cluster, p=%s" % p)
            plt_extent.close()

            # extract and analyze the value in the cluster in each trial
            index = c_0 != 0
            c_value = group_ds['stc'].sum(index)
            # index is a boolean NDVar over space and time, so here we are summing in the
            # whole spatio-temporal cluster
            plt_box = E.plot.Boxplot(c_value, 'wordtype', ds=group_ds, match='subject', run=False)

            image = plt_box.image('image.png')
            figure = section.add_figure("Cluster value")
            figure.append(image)

            index = c_extent != 0
            c_timecourse = group_ds['stc'].sub(source=roi).mean(index)
            plt_tc = E.plot.UTSStat(c_timecourse, X='wordtype', ds=group_ds,
                                    sub=idx, axtitle=title, run=False)
            # plot the cluster
            c_tstart = cluster['tstart']
            c_tstop = cluster['tstop']
            for ax in plt_tc._axes:
                ax.axvspan(c_tstart, c_tstop, color='r', alpha=0.2, zorder=-2)
            plt_tc.figure.savefig(e.get('plot-file', analysis=wtype), run=False)
            im = plt_tc.image()
            plt_tc.close()
            section.add_figure(caption='Difference Plots', content=im)

# save the report
report.save_html(e.get('report-file', analysis='target_constituent_priming_iir_auto_2p'))

