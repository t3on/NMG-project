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
raw = 'NR_iir_hp1_lp40'
tmin = -0.1
tmax = 0.6
reject = 3e-12
analysis='prime'
orient='free'

# analysis paramaters
cstart = 0
cstop = None
pmin = .1

plt_clrs = {'ortho': 'orchid', 'novel': 'steelblue', 'transparent': 'steelblue', 
            'opaque': 'steelblue'}

roilabels = ['anterior_fusiform', 'vmPFC', 'LATL']
rois = ['lh.ant_fusiform', ['lh.VMPFC', 'rh.VMPFC'], 'lh.LATL']

e = process.NMG()
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis='prime', orient='free')

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        # Selection Criteria
        ds = e.load_events(redo=True, edf=False)
        idx = ds['target'] == 'prime'
        idy = ds['condition'] == 'identity'
        ds = ds[idx * idy]
        
        ds = e.make_epochs(ds, evoked=True, raw=raw, model='wordtype')
        if ds.info['use']:
            ds = e.analyze_source(ds,evoked=True, rois=rois, 
                                  roilabels=roilabels, tmin=tmin)
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
    wtypes = group_ds['wordtype'].cells
    wtypes.remove('ortho')
    for wtype in wtypes:
        idx=group_ds['wordtype'].isany('ortho', wtype)
	ds=group_ds[idx]
        title = 'Cluster TTest of %s vs ortho in %s: %s' % (wtype, roilabel, orient)
        a = E.testnd.ttest_rel(Y=roilabel, X='wordtype', match='subject',
                               tstart=cstart, tstop=cstop, pmin=pmin, ds=ds, 
                               samples=10000, tmin=.01)
        p = E.plot.UTSStat(Y=ds[roilabel], X='wordtype', ds=ds, w=10, 
                           clusters=a.clusters, colors=plt_clrs,
                           axtitle=title)	
        e.set(analysis='%s_%s_%s_%s' % (analysis, orient, roilabel, wtype))
        p.figure.savefig(e.get('plot-file'))
        p.close()