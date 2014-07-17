"""
Created on Nov 27, 2012

@author: teon
"""

import eelbrain.eellab as E
import basic.process as process
import os
import cPickle as pickle
import numpy as np


redo = False

# raw data parameters
raw = 'calm_fft_hp1_lp40'
tmin = -0.1
tmax = 0.4
reject = {'mag':4e-12}
orient = 'fixed'
analysis = 'target-%s-all' % orient
decim = 2
title = 'Cluster TTest of Wordtype (Diff in Constituent Priming)'

# analysis paramaters
cstart = 0.1
cstop = None
pmin = .05
morph = True


e = process.NMG()
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis='target', orient=orient)

l1 = mne.read_label(u'/Users/teon/Experiments/MRI/fsaverage/label/lh.fusiform.label')
l2 = mne.read_label(u'/Users/teon/Experiments/MRI/fsaverage/label/lh.inferiortemporal.label')
roi = l1 + l2
# l1 = mne.read_label(u'/Users/teon/Experiments/MRI/fsaverage/label/lh.LATL.label')
# l2 = mne.read_label(u'/Users/teon/Experiments/MRI/fsaverage/label/lh.LPTL.label')
# roi = l1 + l2

e.exclude['subject'] = []

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        ds = e.load_events(edf=True)
        ds = ds[ds['target'] == 'target']

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
    E.save.pickle(group_ds, e.get('group-file'))
    del datasets

n_sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (n_sub, group_ds['subject'].cells))

# group_ds['stc'] = group_ds['stc'].sub(source=roi)


# Identity Priming
sub_idx = group_ds['condition'].isany('identity', 'control_identity')
res = E.testnd.ttest_rel(Y='stc', X='condition', c0='control_identity',
                         c1='identity', match='subject', tstart=cstart,
                         tstop=cstop, pmin=pmin, ds=group_ds, samples=10000)
res.clusters.sort("p")
# Create a report
report = E.Report("Target Analyses", author="Teon")
section = report.add_section("Info")
section.append('%d subjects entered into stats.\n\n %s\n\n'
              % (n_sub, group_ds['subject'].cells))
section = report.add_section("Analysis of the location of "
                             "the identity priming effects.")
section.append('Rejection: %s. Cluster start: %s. Decim: %s' % (reject, cstart,
                                                                decim))

from surfer import Brain
brain = Brain('fsaverage', 'lh', 'inflated')
brain.add_label(roi)
# brain.show_view('ventral')
im = E.plot.brain.image(brain, 'temp.png')

section.add_figure(caption='Selected Subsection of Cortex associated with WF',
                   content=im)

sections = []
for i, cluster in enumerate(res.clusters[res.clusters['p'] < .05].itercases()):
    c_0 = cluster['cluster']
    p = cluster['p']
    section = report.add_section("Cluster %s, p=%s" % (i, p))

    c_extent = c_0.mean('time')
    plt_extent = E.plot.brain.cluster(c_extent)  # , surf='inflated', views='ventral')
    image = E.plot.brain.image(plt_extent, "cluster %s extent.png" % i, alt=None,
                               close=True)
    section.add_image_figure(image, "Extent of the largest cluster, p=%s" % p)
    plt_extent.close()

    # extract and analyze the value in the cluster in each trial
    index = c_0 != 0
    c_value = group_ds['stc'].sum(index)
    # index is a boolean NDVar over space and time, so here we are summing in the
    # whole spatio-temporal cluster
    plt_box = E.plot.uv.boxplot(c_value, 'condition', ds=group_ds, sub=sub_idx)
    pw_table = E.test.pairwise(c_value, 'condition', ds=group_ds, sub=sub_idx)
    print pw_table

    image = plt_box.image('image.png')
    figure = section.add_figure("Cluster value")
    figure.append(image)
    figure.append(pw_table)

    index = c_extent != 0
    c_timecourse = group_ds['stc'].mean(index)
    # c_extent is a boolean NDVar over space only, so here we are summing over the
    # spatial extent of the cluster for every time point but keep the time dimension
    plt_tc = E.plot.UTSStat(c_timecourse, 'condition', ds=group_ds, sub=sub_idx)
    # plot the cluster
    c_tstart = cluster['tstart']
    c_tstop = cluster['tstop']
    for ax in plt_tc._axes:
        ax.axvspan(c_tstart, c_tstop, color='r', alpha=0.2, zorder=-2)
    # add to report
    image = plt_tc.image()
    section.add_image_figure(image, "Time course of the average in the largest "
                             "cluster extent")
    sections.append(section)
    plt.close('all')

# Priming differences
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
Y = E.combine((novel, opaque, ortho, transparent), name='stc')
X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
             rep=len(group_ds['subject'].cells), name='wordtype')
subjects = E.Factor(group_ds['subject'].cells, tile=len(X.cells),
                    name='subject', random=True)
group_diffs = E.Dataset(subjects, Y, X)

analyses = []

for i, cluster in enumerate(res.clusters[res.clusters['p'] < .05].itercases()):
    sections[i].append("Analysis of the priming effects in "
                       "functionally-defined ROI.")

    r = cluster['cluster'].sum('time')
    r = r != 0

    wtypes = list(group_ds['wordtype'].cells)
    wtypes.remove('ortho')
    for wtype in wtypes:
        idx = group_diffs['wordtype'].isany('ortho', wtype)

        stc = group_diffs['stc'][r].mean('source')

        a = E.testnd.ttest_rel(Y=stc, X='wordtype', c0='ortho',
                               c1=wtype, match='subject', tstart=cstart,
                               tstop=cstop, pmin=pmin, ds=group_diffs,
                               samples=10000, sub=idx)

        analyses.append(a)
        title = '%s vs ortho' % wtype
        p = E.plot.UTSStat(Y=stc, X='wordtype', ds=group_diffs, sub=idx,
                           clusters=a.clusters, axtitle=title)
        im = p.image()

        sections[i].add_figure(caption='Difference Plots', content=im)


# save the report
report.save_html(e.get('report-file', analysis=analysis + '_'.join(('', raw, 'vwfa'))))

