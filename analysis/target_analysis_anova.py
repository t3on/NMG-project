#"""
#Created on Nov 27, 2012
#
#@author: teon
#"""
#
#import eelbrain.eellab as E
#import basic.process as process
#import os
#import cPickle as pickle
#import numpy as np
#
#
#redo = False
#
## raw data parameters
#raw = 'calm_fft_hp1_lp40'
#tmin = -0.1
#tmax = 0.4
#reject = {'mag':4e-12}
#orient = 'fixed'
#analysis = 'target-%s-all' % orient
#decim = 2
#title = 'Cluster TTest of Wordtype (Diff in Constituent Priming)'
#
## analysis paramaters
#cstart = 0.1
#cstop = 0.3
#pmin = .05
#morph = True
#
#
#e = process.NMG()
#e.set(raw=raw)
#e.set(datatype='meg')
#e.set(analysis='target', orient=orient)
#
#l1 = 'lh.fusiform.label'
#l2 = 'lh.inferiortemporal.label'
#roi = e.read_label([l1, l2])
#
#if os.path.lexists(e.get('group-file')) and not redo:
#    group_ds = pickle.load(open(e.get('group-file')))
#else:
#    datasets = []
#    for _ in e:
#        ds = e.load_events(edf=True, proj=False)
#        ds = ds[ds['target'] == 'target']
#
#        ds = e.make_epochs(ds, evoked=True, raw=raw, decim=decim,
#                           model='condition % wordtype', reject=reject)
#        if ds.info['use']:
#            ds = e.analyze_source(ds, evoked=True, orient=orient,
#                                  tmin=tmin, morph=morph)
#            # Append to group level datasets
#            datasets.append(ds)
#            del ds
#    # combines the datasets for group
#    group_ds = E.combine(datasets)
#    E.save.pickle(group_ds, e.get('group-file'))
#    del datasets

wtypes = list(group_ds['wordtype'].cells)
n_sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (n_sub, group_ds['subject'].cells))

group_ds['stc'] = group_ds['stc'].sub(source=roi)


# ANOVA
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

a = E.testnd.anova(Y='stc', X='condition', 
                   match='subject', tstart=cstart,
                   tstop=cstop, pmin=pmin, ds=group_ds,
                   samples=10000, sub=idx)

analyses = []

wtypes.remove('ortho')
for wtype in wtypes:
    idx = group_ds['wordtype'].isany('ortho', wtype)
    a = E.testnd.anova(Y='stc', X='wordtype % condition', 
                       match='subject', tstart=cstart,
                       tstop=cstop, pmin=pmin, ds=group_ds,
                       samples=10000, sub=idx)

    analyses.append(a)
    title = '%s vs ortho' % wtype
    p = E.plot.UTSStat(Y='stc', X='wordtype % condition', ds=group_ds, sub=idx,
                       clusters=a.clusters, axtitle=title)
    im = p.image()

    section.add_figure(caption='ANOVA Plots', content=im)


# save the report
report.save_html(e.get('report-file', analysis=analysis + '_'.join(('', raw, 'vwfa'))))

