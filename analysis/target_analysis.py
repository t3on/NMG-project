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


# e = process.NMG()
e = process.NMG(None, '{glyph_drive}')
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis='target', orient=orient, plot_ext='jpg')
#
l1 = 'lh.fusiform.label'
l2 = 'lh.inferiortemporal.label'
l3 = 'lh.LATL.label'
l4 = 'lh.LPTL.label'
labels = [l1,l2,l3,l4]

roi = e.read_label([l1, l2, l3, l4])

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        ds = e.load_events(edf=True, proj=False)
        ds = ds[ds['target'] == 'target']
        # ds = ds[ds['condition'].isany('control_constituent', 'first_constituent')]

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


analyses = []
wtypes = list(group_ds['wordtype'].cells)
wtypes.remove('ortho')

for label in labels:
    roi = e.read_label(label)
    idx = group_ds['condition'].isany('first_constituent', 'control_constituent')
    ds = group_ds[idx]
    ds['stc'] = ds['stc'].sub(source=roi)
    a = E.testnd.anova(Y='stc', X='condition*wordtype', match='subject', tstart=cstart,
                       tstop=cstop, pmin=pmin, ds=ds, samples=10000)
    analyses.append(a)

labels = [l1, l2, [l3,l4]]
for a, label in zip(analyses, labels):
    # added
    roi = e.read_label(label)
    idx = group_ds['condition'].isany('first_constituent', 'control_constituent')
    ds = group_ds[idx]
    ds['stc'] = ds['stc'].sub(source=roi)
    # delete

    for i, cluster in enumerate(a.clusters[a.clusters['p'] < .1].itercases()):
        effect = cluster['effect']
        c_0 = cluster['cluster']
        p = cluster['p']
        c_tstart = cluster['tstart']
        c_tstop = cluster['tstop']

        section = report.add_section("Cluster %s, p=%s" % (effect, p))
        report.add_section('Cluster start: %s, Cluster stop: %s' %(c_tstart,
                                                                   c_tstop))

        c_extent = c_0.sum('time')
        plt_extent = E.plot.brain.cluster(c_extent, surf='inflated')
        plt_extent.show_view('ventral')
        image = E.plot.brain.image(plt_extent, "cluster %s extent.png" % i,
                                   alt=None, close=True)
        image.save_image(e.get('plot-file', analysis='target_brain_%s_%s_%s' %(effect,label, i)))
        section.add_image_figure(image, "Extent of the largest "
                                 "cluster, p=%s" % p)
        plt_extent.close()

        # Time course
        index = c_extent != 0
        c_timecourse = ds['stc'].sub(source=roi).mean(index)

        title = 'Cluster ANOVA: %s' %effect
        if ' x ' in effect:
            for wtype in wtypes:
                idx = ds['wordtype'].isany('ortho', wtype)
                p = E.plot.UTSStat(Y=c_timecourse, X='condition % wordtype', ds=ds, sub=idx,
                                   axtitle=title, ylabel='dSPM')
                # plot the cluster
                for ax in p._axes:
                    ax.axvspan(c_tstart, c_tstop, color='r', alpha=0.15, zorder=-2)

                p.figure.savefig((e.get('plot-file',
                                 analysis='target_anova_%s_%s_%s_%s' %(effect,label,i,wtype))))

        else:
            p = E.plot.UTSStat(Y=c_timecourse, X=effect, ds=ds,
                               axtitle=title, ylabel='dSPM')
            # plot the cluster
            for ax in p._axes:
                ax.axvspan(c_tstart, c_tstop, color='r', alpha=0.15, zorder=-2)

            p.figure.savefig((e.get('plot-file', analysis='target_anova_%s_%s_%s' %(effect,
                                                                       label, i))))
        im = p.image()

        section.add_figure(caption='ANOVA Plots', content=im)
        plt.close('all')

# save the report
report.save_html(e.get('report-file', analysis='target_constituent_priming'))

# # for interaction
# analyses = pickle.load(open('/Users/teon/Dropbox/analyses.pickled'))
# idx = analyses[-1].clusters['id'] == 3
# idx2 = analyses[-1].clusters['effect'] == 'condition x wordtype'
# cluster = analyses[-1].clusters[idx*idx2][0]
# effect = cluster['effect']
# c_0 = cluster['cluster']
# p = cluster['p']
# c_tstart = cluster['tstart']
# c_tstop = cluster['tstop']
# c_extent = c_0.sum('time')
# index = c_extent != 0
#
# label = [l3,l4]
# roi = e.read_label(label)
# idx = group_ds['condition'].isany('first_constituent', 'control_constituent')
# ds = group_ds[idx]
# ds['stc'] = ds['stc'].sub(source=roi)
#
# c_timecourse = ds['stc'].sub(source=roi).mean(index)
#
# # interaction = c_timecourse.summary(time=(c_tstart, c_tstop))
# ct = E.Celltable(Y=c_timecourse, X='wordtype % condition', match='subject',
#                  ds=ds)
# novel = (ct.data[('novel', 'first_constituent')] -
#          ct.data[('novel', 'control_constituent')])
# opaque = (ct.data[('opaque', 'first_constituent')] -
#           ct.data[('opaque', 'control_constituent')])
# ortho = (ct.data[('ortho', 'first_constituent')] -
#          ct.data[('ortho', 'control_constituent')])
# transparent = (ct.data[('transparent', 'first_constituent')] -
#                ct.data[('transparent', 'control_constituent')])
# Y = E.combine((novel, opaque, ortho, transparent), name='diffs')
# X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
#              rep=len(ds['subject'].cells), name='wordtype')
# subjects = E.Factor(ds['subject'].cells, tile=len(X.cells),
#                     name='subject', random=True)
# diffs = E.Dataset(subjects, Y, X)
#
# title = 'Cluster ANOVA: interaction'
# p = E.plot.UTSStat(Y='diffs', X='wordtype', ds=diffs,
#                    axtitle=title, ylabel='dSPM', legend='lower left')
# # plot the cluster
# for ax in p._axes:
#     ax.axvspan(c_tstart, c_tstop, color='r', alpha=0.15, zorder=-2)
#
# p.figure.savefig((e.get('plot-file', analysis='target_anova_inter')))
