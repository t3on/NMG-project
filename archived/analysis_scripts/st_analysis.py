'''
Created on Nov 27, 2012

@author: teon
'''

import eelbrain.eellab as E
import basic.process as process
import os
import cPickle as pickle
import numpy as np
import mne.stats.regression

# raw data parameters
raw = 'calm_fft_hp1_lp40'
tmin = -0.1
tmax = 0.6
reject = 4e-12
decim = 10
analysis = 'st'
orient = 'fixed'
method = "MNE"
redo = True

# analysis paramaters
cstart = 0.2
cstop = .4
pmin = .1

# roilabels = ['inferior_temporal', 'MTG', 'LPTL']
# rois = ['lh.inferiortemporal', 'lh.middletemporal', 'lh.LPTL']

e = process.NMG()
e.set(raw=raw)
e.set(datatype='meg')

e.set(analysis='_'.join((analysis, orient, method)), orient=orient)

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        # Selection Criteria
        ds = e.load_events(edf=False)
        ds['st'] = E.Var(ds['c1_rating'].x + ds['c2_rating'].x)
        idx = ds['target'] == 'prime'
        idx2 = ds['condition'] == 'identity'
        idx3 = np.isnan(ds['st'].x) == False
        idx4 = ds['st'].x != 0
        idx5 = ds['wordtype'].isany('transparent', 'opaque')
        idx = reduce(np.logical_and, [idx, idx2, idx3, idx4, idx5])
        ds = ds[idx]

        ds = e.make_epochs(ds, evoked=False, raw=raw, decim=decim)
        if ds.info['use']:
            design_matrix = np.ones([ds.n_cases, 2])
            design_matrix[:, 1] = ds['st'].x
            names = ['intercept', 'st']
            ols_fit = mne.stats.regression.ols_epochs(ds['epochs'],
                                                      design_matrix, names)
            ds = ds.aggregate('subject', drop_bad=True)
            ds['epochs'] = [ols_fit['t']['st']]
            ds = e.analyze_source(ds, evoked=True, morph=True, method=method)

            # Append to group level datasets
            datasets.append(ds)
            del ds
    # combines the datasets for group
    group_ds = E.combine(datasets)
    del datasets
    E.save.pickle(group_ds, e.get('group-file'))

sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (sub, group_ds['subject'].cells))

# analyses = []
# for roilabel in roilabels:
#     title = 'Correlation of Semantic Transparency in %s' % roilabel
#     a = E.testnd.corr(Y=group_ds[roilabel], X='st', norm='subject',
#                       tstart=cstart, tstop=cstop, pmin=pmin, ds=group_ds,
#                       samples=10000, tmin=.01, match='subject')
#     p = E.plot.UTSClusters(a, title=None, axtitle=title, w=10)
#     e.set(analysis='%s_%s' % (analysis, roilabel))
#     p.figure.savefig(e.get('plot-file'))
#     analyses.append(a)

res = pickle.load(open(e.get('analysis-file',
                             analysis='identity_priming_clusters') + '.pickled'))
idx = res.clusters['cluster'][2].sum('time')
idx = idx != 0
group_ds['st'] = group_ds['stc'].sub(source=idx.x).summary('source')
a = E.testnd.ttest_1samp('stc', match='subject', ds=group_ds, samples=10000,
                         tstart=cstart, tstop=cstop, pmin=pmin, mintime=.01)
