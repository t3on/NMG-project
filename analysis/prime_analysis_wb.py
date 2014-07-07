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
reject = {'mag':4e-12}
analysis = 'prime'
orient = 'free'
decim = 10
morph = True

# # analysis paramaters
cstart = 0.15
cstop = .5
pmin = .2

e = process.NMG()
e.set(raw=raw)
e.set(datatype='meg')
e.set(analysis=analysis, orient=orient)

if os.path.lexists(e.get('group-file')) and not redo:
    group_ds = pickle.load(open(e.get('group-file')))
else:
    datasets = []
    for _ in e:
        # Selection Criteria
        ds = e.load_events(edf=False)
        idx = ds['target'] == 'prime'
        idy = ds['condition'] == 'identity'
        ds = ds[idx * idy]

        ds = e.make_epochs(ds, evoked=True, raw=raw, model='wordtype',
                           reject=reject, decim=decim)
        if ds.info['use']:
            ds = e.analyze_source(ds, evoked=True, orient=orient, morph=morph,
                                  tmin=tmin, tmax=tmax)
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

analyses = []
wtypes = group_ds['wordtype'].cells
wtypes.remove('ortho')
for wtype in wtypes:
    idx = group_ds['wordtype'].isany('ortho', wtype)

    a = E.testnd.ttest_rel(Y='stc', X='wordtype', c0='ortho',
                           c1=wtype, match='subject', tstart=cstart,
                           tstop=cstop, pmin=pmin, ds=group_ds, samples=1000,
                           tmin=.05, sub=idx)
    a.clusters.sort('p')
    analyses.append((a))
    a.clusters[a.clusters['p'] < .05]
    for i, v in enumerate(a.clusters[a.clusters['p'] < .05].itercases()):
        p = E.plot.brain.cluster(v['cluster'].sum('time'), surf='inflated')
        p.save_image(e.get('plot-file', analysis='%s_%s_%s_cluster_%s' %
                           (analysis, wtype, orient, i)))
        p.close()


#     p = E.plot.UTSStat(Y='stc', X='wordtype', ds=ds, w=10,  # clusters=a.clusters,
#                        axtitle=title)
#     p.figure.savefig(e.get('plot-file', analysis='%s_%s_%s' %
#                            (analysis, wtype, orient)))
