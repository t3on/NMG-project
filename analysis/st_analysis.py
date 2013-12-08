'''
Created on Nov 27, 2012

@author: teon
'''

import eelbrain.eellab as E
import basic.process as process
import os
import cPickle as pickle
import numpy as np

# raw data parameters
raw = 'NR_iir_hp1_lp40'
tmin = -0.1
tmax = 0.6
reject = 3e-12
decim = 2
analysis='st'
redo = False

# analysis paramaters
cstart = 0
cstop = None
pmin = .1

roilabels = ['inferior_temporal', 'MTG', 'LPTL']
rois = ['lh.inferiortemporal', 'lh.middletemporal', 'lh.LPTL']

e = process.NMG()
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis='st', orient='free')

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        # Selection Criteria
        ds = e.load_events()
        ds['st'] = E.Var(ds['c1_rating'].x + ds['c2_rating'].x)
        idx = ds['target'] == 'prime'
        idx2 = ds['condition'] == 'identity'
        idx3 = np.isnan(ds['st'].x) == False
        idx4 = ds['st'].x != 0
        idx5 = ds['wordtype'].isany('transparent', 'opaque')
        idx = reduce(np.logical_and, [idx,idx2,idx3,idx4, idx5])
        ds = ds[idx]

        ds = e.make_epochs(ds, evoked=False, raw=raw, decim=decim)
        if ds.info['use']:
            ds = e.analyze_source(ds, rois=rois, roilabels=roilabels, tmin=tmin)
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

analyses = []
for roilabel in roilabels:
    title = 'Correlation of Semantic Transparency in %s' % roilabel
    a = E.testnd.corr(Y=group_ds[roilabel], X='st', norm='subject',
                      tstart=cstart, tstop=cstop, pmin=pmin, ds=group_ds, 
                      samples=1000, tmin=.01, match='subject')
    p = E.plot.UTSClusters(a, title=None, axtitle=title, w=10)
    e.set(analysis='%s_%s' % (analysis, roilabel))
    p.figure.savefig(e.get('plot-file'))
    analyses.append(a)


