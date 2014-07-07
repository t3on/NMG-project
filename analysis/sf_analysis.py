'''
Created on Nov 27, 2012

@author: teon
'''

import eelbrain.eellab as E
import basic.process as process
import os
import cPickle as pickle
import numpy as np


redo = True

# raw data parameters
raw = 'calm_fft_hp1_lp40'
tmin = -0.1
tmax = 0.6
reject = 4e-12
decim = 10
analysis = 'sf'
orient = 'free'
morph = True
method = 'dSPM'

# analysis paramaters
cstart = .1
cstop = .3
pmin = .05

# rois = roilabels = ['lh.fusiform', 'lh.inferiortemporal', 'lh.middletemporal',
#                     'lh.cuneus', 'lh.LPTL']

e = process.NMG()
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis='_'.join((analysis, orient, method)), orient=orient)

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
#     for _ in e:
    for subject in ['R0095']:
        e.set(subject)
        ds = e.load_events(edf=False)
        idx = (ds['word_freq'] != 0) * (~np.isnan(ds['word_freq']))
        ds = ds[idx]
        ds['log_freq'] = E.Var(np.log(ds['word_freq'].x))
        ds = e.make_epochs(ds, evoked=False, raw=raw, decim=decim)
        if ds.info['use']:
            design_matrix = np.ones([ds.n_cases, 2])
            design_matrix[:, 1] = ds['log_freq'].x
            names = ['intercept', 'log_freq']
            ds = e.analyze_source(ds, evoked=False, morph=True, method=method)
            ols_fit = mne.stats.ols_source_estimate(ds['stc'], design_matrix, names)
            ds = ds.aggregate('subject', drop_bad=True)
            ds['stc'] = [ols_fit['b']['log_freq']]
            # Append to group level datasets
#             datasets.append(ds)
#             del ds
#     # combines the datasets for group
#     group_ds = E.combine(datasets)
#     del datasets
#     E.save.pickle(group_ds, e.get('group-file'))
#
# sub = len(group_ds['subject'].cells)
# e.logger.info('%d subjects entered into stats.\n %s'
#               % (sub, group_ds['subject'].cells))
# #
# # for roilabel in roilabels:
# #     title = 'Correlation of Surface Frequency in %s' % roilabel
# #     a = E.testnd.corr(Y=group_ds[roilabel], X='log_freq', norm='subject',
# #                       tstart=cstart, tstop=cstop, pmin=pmin, ds=group_ds,
# #                       samples=100, tmin=.01, match='subject')
# #     p = E.plot.UTSClusters(a, title=title, axtitle=None, w=10)
# #     e.set(analysis='%s_%s' % (analysis, roilabel))
# #     p.figure.savefig(e.get('plot-file'))
#
# a = E.testnd.ttest_1samp('stc', match='subject', ds=group_ds, samples=1000,
#                          tstart=cstart, tstop=None, pmin=pmin, tmin=.01)
