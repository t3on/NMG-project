#'''
#Created on Nov 27, 2012
#
#@author: teon
#'''
#
#import datetime
#import eelbrain as E
#import basic.process as process
#import os
#import cPickle as pickle
#import numpy as np
#
#timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#redo = False
#
## raw data parameters
#raw = 'calm_fft_hp1_lp40'
#tmin = -0.1
#tmax = 0.6
#reject = {'mag':4e-12}
#orient = 'fixed'
#decim = 2
#morph = True
#analysis = 'prime-%s-all-%s' % (orient, raw)
#proj_val = ''
## e.exclude['subject'] = []
#
## analysis paramaters
#cstart = 0.4
#cstop = None
#pmin = .05
#
#l1 = mne.read_label(u'/Volumes/teon-backup/Experiments/MRI/fsaverage/label/lh.LATL.label')
#l2 = mne.read_label(u'/Volumes/teon-backup/Experiments/MRI/fsaverage/label/lh.LPTL.label')
#
#roi = l1 + l2
#
#e = process.NMG(None, '{teon-backup_drive}')
#e.set(raw=raw)
#e.set(datatype='meg')
#e.set(analysis=analysis, orient=orient, proj_val=proj_val)
#
#if os.path.lexists(e.get('group-file')) and not redo:
#    group_ds = pickle.load(open(e.get('group-file')))
#else:
#    datasets = []
#    for _ in e:
#        print e.subject
#        # Selection Criteria
#        ds = e.load_events(edf=True, proj=False)
#        idx = ds['target'] == 'prime'
#        idy = ds['condition'] == 'identity'
#        ds = ds[idx * idy]
#        ds = e.make_epochs(ds, evoked=True, raw=raw, model='wordtype',
#                           reject=reject, decim=decim)
#        if ds.info['use']:
#            ds = e.analyze_source(ds, evoked=True, orient=orient, tmin=tmin,
#                                  morph=morph)
#            # Append to group level datasets
#            datasets.append(ds)
#            del ds
#    # combines the datasets for group
#    group_ds = E.combine(datasets)
#    del datasets
#    E.save.pickle(group_ds, e.get('group-file', analysis=analysis))

n_sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (n_sub, group_ds['subject'].cells))

# Create a report
report = E.Report("Prime Analyses", author="Teon")
section = report.add_section("Info")
section.append('%d subjects entered into stats.\n\n %s\n\n'
              % (n_sub, group_ds['subject'].cells))
section = report.add_section("Planned Comparison of Word Type "
                             "Differences in Temporal Lobe.")
section.append('Rejection: %s. Cluster start: %s. Decim: %s' % (reject, cstart,
                                                                decim))

idx = group_ds['wordtype'].isany('transparent', 'opaque', 'ortho')
a = E.testnd.t_contrast_rel(Y=group_ds['stc'].sub(source=roi), X='wordtype',
                            contrast='+min( transparent > ortho, opaque > ortho)', 
                            match='subject', tstart=cstart, tstop=cstop, pmin=pmin,
                            ds=group_ds, samples=10000)
title = 'Spatiotemporal Cluster TTest of %s vs ortho in Temporal Lobe: %s' % (wtype, orient)
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
    plt_box = E.plot.uv.boxplot(c_value, 'wordtype', ds=group_ds, match='subject')
    pw_table = E.test.pairwise(c_value, 'wordtype', ds=group_ds, match='subject')
    print pw_table

    image = plt_box.image('image.png')
    figure = section.add_figure("Cluster value")
    figure.append(image)
    figure.append(pw_table)

    index = c_extent != 0
    c_timecourse = group_ds['stc'].sub(source=roi).mean(index)
    plt_tc = E.plot.UTSStat(c_timecourse, X='wordtype', ds=group_ds,
                            sub=idx, axtitle=title)
    # plot the cluster
    c_tstart = cluster['tstart']
    c_tstop = cluster['tstop']
    for ax in plt_tc._axes:
        ax.axvspan(c_tstart, c_tstop, color='r', alpha=0.2, zorder=-2)
    plt_tc.figure.savefig(e.get('plot-file', analysis='contrast'))
    im = plt_tc.image()
    plt_tc.close()
    section.add_figure(caption='Difference Plots', content=im)

# save the report
report.save_html(e.get('report-file', analysis=analysis + '_temporal-contrast_full'))




# add the contrast to this test: '+min( transparent > ortho, opaque > ortho)'
