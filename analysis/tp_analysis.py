'''
Created on Nov 27, 2012

@author: teon
'''

import eelbrain.eellab as E
import basic.process as process
import os
import cPickle as pickle
import numpy as np


redo=True

# raw data parameters
raw = 'iir_hp1_lp40'
tmin = -0.1
tmax = 0.6
reject = 3e-12
analysis='tp'

# analysis paramaters
cstart = 0
cstop = None
pmin = .1

rois = roilabels = ['lh.fusiform', 'lh.ant_fusiform', 'lh.inferiortemporal', 'lh.middletemporal']

e = process.NMG()
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis='tp', orient='free')

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        # Selection Criteria
        ds = e.load_events()
        idx = ds['wordtype'].isany('transparent', 'opaque')
        idx2 = ds['condition'].isany('control_identity')
        idx3 = ds['target'] == 'prime'
        idx = reduce(np.logical_and, [idx,idx2,idx3])

        idy = ds['c1_freq'] != 0
        idy2 = ~np.isnan(ds['c1_freq'])
        idy3 = ds['word_freq'] != 0
        idy4 = ~np.isnan(ds['word_freq'])
        idy = reduce(np.logical_and, [idy,idy2,idy3,idy4])
        
        idx = reduce(np.logical_and, [idx,idy])
        ds = ds[idx]
        
        ds['log_freq'] = E.Var(np.log(ds['word_freq'].x))
        ds['log_c1_freq'] = E.Var(np.log(ds['c1_freq'].x))        
        ds['tp'] = E.Var(ds['log_freq'].x - ds['log_c1_freq'].x)

        ds = e.make_epochs(ds, evoked=False, raw=raw)
        if ds.info['use']:
            ds = e.analyze_source(ds, rois=rois, roilabels=roilabels, tmin=tmin)
            # Append to group level datasets
            datasets.append(ds)
            del ds
    # combines the datasets for group
    group_ds = E.combine(datasets)
    del datasets
    E.save.pickle(group_ds, e.get('group-file', analysis=analysis))

sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (sub, group_ds['subject'].cells))

for roilabel in roilabels:
    title = 'Correlation of Transition Probability in %s' % roilabel
    a = E.testnd.corr(Y=group_ds[roilabel], X='tp', norm='subject',
                      tstart=cstart, tstop=cstop, pmin=pmin, ds=group_ds, 
                      samples=1000, tmin=.01, match='subject')
    p = E.plot.UTSClusters(a, title=title, axtitle=None, w=10)
    e.set(analysis='%s_%s' % (analysis, roilabel))
    p.figure.savefig(e.get('plot-file'))


