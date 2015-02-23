'''
Completed on Feb 14, 2015

@author: teon
'''

import datetime
import eelbrain as E
import basic.process as process
import os
import cPickle as pickle
import numpy as np


redo = False

# raw data parameters
raw = 'calm_iir_hp1_lp40'
tmin = -0.2
tmax = 0.6
reject = {'mag':4e-12}
orient = 'fixed'
decim = 1
morph = True
analysis = 'prime-%s-all-%s' % (orient, raw)
proj_val = ''

# analysis paramaters
cstart = 0.1
cstop = None
pmin = .05

e = process.NMG(None, '{home}')
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis=analysis, orient=orient, proj_val=proj_val)
e.exclude['subject'] = ['R0414']
e.set(cov = os.path.join('{fif_sdir}', '{s_e}_{raw}_auto-cov.fif'))

l1 = e.read_label('lh.LATL.label')
l2 = e.read_label('lh.LPTL+sts.label')
l3 = e.read_label('lh.transversetemporal.label')
l4 = e.read_label('lh.temporalpole.label')
roi = l1 + l2 + l3 + l4

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        print e.subject
        print e.get('cov')
        # Selection Criteria
        ds = e.load_events(edf=False, proj=False, redo=True)
        idx = ds['target'] == 'prime'
        idy = ds['condition'] == 'identity'
        ds = ds[idx * idy]
        ds = e.make_epochs(ds, evoked=True, raw=raw, model='wordtype',
                           reject=reject, decim=decim, tmin=tmin, tmax=tmax,
                           baseline=(None,0))
        if ds.info['use']:
            ds = e.analyze_source(ds, evoked=True, orient=orient, tmin=tmin,
                                  morph=morph)
            # Append to group level datasets
            del ds.info['raw']
            datasets.append(ds)
            del ds
    # combines the datasets for group
    group_ds = E.combine(datasets)
    del datasets
    E.save.pickle(group_ds, e.get('group-file', analysis=analysis))

n_sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (n_sub, group_ds['subject'].cells))


analyses = []
ts = []
wtypes = list(group_ds['wordtype'].cells)
wtypes.remove('simplex')
for wtype in wtypes:
    idx = group_ds['wordtype'].isany('simplex', wtype)
    a = E.testnd.ttest_rel(Y=group_ds['stc'].sub(source=roi), X='wordtype',
                           c0='simplex', c1=wtype, match='subject', tstart=cstart,
                           tstop=cstop, ds=group_ds, sub=idx, tail=1, samples=10000,
                           pmin=pmin)
    analyses.append(a)

# Create a report
report = E.Report("Prime Analyses", author="Teon")
section = report.add_section("Info")
section.append('%d subjects entered into stats.\n\n %s\n\n'
              % (n_sub, group_ds['subject'].cells))
section.append('Rejection Threshold: %s. Cluster start: %s. Decim: %s'
               % (reject, cstart, decim))
section = report.add_section("Planned Comparisons of Word Type "
                             "Differences in Temporal Lobe.")


ylabel = 'Brain Activation (dSPM)'
for wtype, a in zip(wtypes, analyses):
    idx = group_ds['wordtype'].isany('simplex', wtype)
    if a.clusters.n_cases > 0:
        if a.clusters[a.clusters['p'] < .05].n_cases == 0:
            alpha = 0
            clusters = [a.clusters.sorted('p')[0]]
        else:
            alpha = 1
            clusters = a.clusters[a.clusters['p'] < .05].itercases()
        for i, cluster in enumerate(clusters):
            c_0 = cluster['cluster']
            p = cluster['p']
            section = report.add_section("%s cluster %s" % (wtype, i))
            c_extent = c_0.mean('time')
            c_extent.x[c_extent.x > 0] = 1
            plt_extent = E.plot.brain.cluster(c_extent, surf='inflated',
                                              views='lateral')
            b_image = E.plot.brain.image(plt_extent, "cluster %s extent.png" % i,
                                         alt=None, close=True)
            b_image.save_image(e.get('plot-file', analysis='brain_%d_' %i + wtype,
                                     plot_ext='png'))
            section.add_image_figure(b_image, "Extent of the largest "
                                     "cluster, p=%s" % p)
            plt_extent.close()
            del b_image, plt_extent

            # # color map
            # vmax = c_extent.max()
            # lut = E.plot._brain._dspm_lut(0, vmax / 2, vmax)
            # cmap = mpl.colors.ListedColormap(lut / 255., "Average dSPM")
            # p = E.plot.ColorBar(cmap, -vmax, vmax, h=0.5, w=1.5, show=False)
            # p.figure.save_fig(e.get('plot-file', analysis='cmap_%d_' %i + wtype,
            #                         plot_ext='pdf'))


            # extract and analyze the value in the cluster in each trial
            index = c_0 != 0
            c_value = group_ds['stc'].mean(index)
            # index is a boolean NDVar over space and time, so here we are averaging in the
            # whole spatio-temporal cluster
            title = 'Average dSPM of Cluster'
            plt_box = E.plot.Barplot(c_value, 'wordtype', ds=group_ds, match='subject',
                                     ylabel=ylabel, xlabel='Word Type', sub=idx,
                                     run=False, title=title)
            image = plt_box.image('image.png')
            plt_box.figure.savefig(e.get('plot-file', analysis='bp_%d_' %i + wtype,
                                   plot_ext='pdf'))
            figure = section.add_figure("Cluster value")
            figure.append(image)

            index = c_extent != 0
            c_timecourse = group_ds['stc'].sub(source=roi).mean(index)
            ts.append((a, E.table.stats(c_value, 'wordtype',
                      ds=group_ds, funcs=[np.mean, np.std])))
            title = 'Spatiotemporal t-Test of %s vs Simplex' % (wtype[0].upper() + wtype[1:])
            plt_tc = E.plot.UTSStat(c_timecourse, X='wordtype', ds=group_ds,
                                    sub=idx, title=title, run=False,
                                    ylabel=ylabel, match='subject')
            # plot the cluster
            if alpha:
                c_tstart = cluster['tstart']
                c_tstop = cluster['tstop']
                for ax in plt_tc._axes:
                    ax.axvspan(c_tstart, c_tstop, color='r', alpha=0.2*alpha, zorder=-2)
            plt_tc.figure.savefig(e.get('plot-file',
                                        analysis='ts_%d_' %i + wtype,
                                        plot_ext='pdf'))
            im = plt_tc.image()
            plt_tc.close()
            section.add_figure(caption='Difference Plots', content=im)
            plt.close('all')

# save the report
report.save_html(e.get('report-file', analysis=analysis + '_temporal-revision_final'))




# # add the contrast to this test: '+min( transparent > ortho, opaque > ortho)'
