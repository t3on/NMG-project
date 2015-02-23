'''
Created on Dec 2, 2012
Modified February 16, 2015

@author: teon
'''

import os
import numpy as np
import basic.process as process
import eelbrain.eellab as E


group_ds = []
e = process.NMG(None, '{db_dir}')
e.exclude = {}
e.set(datatype='behavioral')
e.set(analysis='latency_revision')


if os.path.exists(e.get('agg-file')):
    group_ds = E.load.tsv(e.get('agg-file'))
    group_ds['subject'].random = True
else:
    for _ in e:
        ds = e.load_events(proj=False)
        ds = ds[ds['target'] == 'target']
        orig_N = ds.n_cases
        ds['latency'].x = ds['latency'].x * 1e3

        # outlier rejection
        devs = np.abs(ds['latency'].x - ds['latency'].x.mean())
        criterion = 2 * ds['latency'].x.std().repeat(ds.n_cases)
        good = devs < criterion
        ds = ds[good]

        remainder = ds.n_cases * 100. / orig_N
        e.logger.info('latency: %d' % remainder + r'% ' + 'remain after outlier rejection')
        group_ds.append(ds)

    group_ds = E.combine(group_ds)
    group_ds = group_ds.compress('condition % wordtype % subject', drop_bad=True)
    group_ds.save_txt(e.get('agg-file'))

# exclude novel
group_ds = group_ds[group_ds['wordtype'].isany('transparent', 'opaque', 'ortho')]
ct = E.Celltable(Y='latency', X='wordtype % condition', match='subject', ds=group_ds)

###########################
#    constituent anova    #
###########################
e.set(analysis='latency_constituent')
idx = group_ds['condition'].isany('control_constituent', 'first_constituent')
a = E.test.anova(Y='latency', X='subject*wordtype*condition', sub=idx, ds=group_ds)
t = a.table()
t.save_pdf(e.get('analysis-file') + '.pdf')
t.save_tex(e.get('analysis-file') + '.tex')

novel = ct.data[('novel', 'control_constituent')] - ct.data[('novel', 'first_constituent')]
opaque = ct.data[('opaque', 'control_constituent')] - ct.data[('opaque', 'first_constituent')]
ortho = ct.data[('ortho', 'control_constituent')] - ct.data[('ortho', 'first_constituent')]
transparent = ct.data[('transparent', 'control_constituent')] - ct.data[('transparent', 'first_constituent')]

Y = E.combine((novel, opaque, ortho, transparent))
X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
             rep=len(group_ds['subject'].cells), name='wordtype')
sub = E.Factor(group_ds['subject'].cells, rep=len(X.cells), name='subject', random=True)
group_plot = E.Dataset(sub, Y, X)

p = E.plot.uv.barplot(Y, X, match=sub, figsize=(10, 5), corr=False,
                      ylabel='Latency Priming Difference in ms',
                      title="Constituent Priming Latency Difference Means")
p.fig.savefig(e.get('plot-file'))

a = E.test.pairwise(Y,X, match=sub, corr=None)
a.save_tex(e.get('analysis-file') + '-pairwise.tex')
a.save_pdf(e.get('analysis-file') + '-pairwise.pdf')

p = E.plot.uv.barplot(Y, X, match=sub, figsize=(10, 5), corr=False, test=0,
                      ylabel='Latency Priming Difference in ms',
                      title="Constituent Priming Latency Difference Means")
e.set(analysis='latency_constituent_zero')
p.fig.savefig(e.get('plot-file'))
#a = E.test.ttests(Y,X, against=0, match=sub)

#########################
#    identity anova     #
#########################
e.set(analysis='latency_identity')
idx = group_ds['condition'].isany('control_identity', 'identity')
a2 = E.test.anova(Y=group_ds['latency'], X='subject * wordtype * condition',
                 sub=idx, ds=group_ds)
t2 = a2.table()
t2.save_pdf(e.get('analysis-file') + '.pdf')
t2.save_tex(e.get('analysis-file') + '.tex')

novel = ct.data[('novel', 'control_identity')] - ct.data[('novel', 'identity')]
opaque = ct.data[('opaque', 'control_identity')] - ct.data[('opaque', 'identity')]
ortho = ct.data[('ortho', 'control_identity')] - ct.data[('ortho', 'identity')]
transparent = ct.data[('transparent', 'control_identity')] - ct.data[('transparent', 'identity')]

Y = E.combine((novel, opaque, ortho, transparent))
X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
             rep=len(group_ds['subject'].cells), name='wordtype')
sub = E.Factor(group_ds['subject'].cells, rep=len(X.cells), name='subject', random=True)
group_plot = E.Dataset(sub, Y, X)

p2 = E.plot.uv.barplot(Y, X, match=sub, figsize=(10, 5), corr=False,
                       ylabel='Latency Priming Difference in ms', test=0,
                       title="Identity Priming Latency Difference Means")
p2.fig.savefig(e.get('plot-file'))

a2 = E.test.pairwise(Y,X, match=sub, corr=None)
a2.save_tex(e.get('analysis-file') + '-pairwise.tex')
a2.save_pdf(e.get('analysis-file') + '-pairwise.pdf')