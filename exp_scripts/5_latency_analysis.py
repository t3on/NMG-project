'''
Created on Dec 2, 2012
Modified February 16, 2015

@author: teon
'''

import os
import numpy as np
import basic.process as process
import eelbrain as E


redo = False
e = process.NMG(None, '{dropbox}')
e.exclude['subject'] = ['R0414']
e.set(datatype='behavioral')
e.set(analysis='latency_revision')


if not redo and os.path.exists(e.get('agg-file')):
    group_ds = E.load.tsv(e.get('agg-file'))
    group_ds['subject'].random = True
else:
    for _ in e:
        ds = e.load_events(proj=False)
        ds = ds[ds['target'] == 'target']
        ds = ds[ds['wordtype'] != 'novel']
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
    group_ds.save_txt(e.get('agg-file'))

group_ds = group_ds.aggregate('condition % wordtype % subject', drop_bad=True)
ct = E.Celltable(Y='latency', X='wordtype % condition', match='subject', ds=group_ds)

###########################
#    constituent anova    #
###########################
e.set(analysis='latency_revision_constituent')
idx = group_ds['condition'].isany('control_constituent', 'first_constituent')
a = E.test.anova(Y='latency', X='subject*wordtype*condition', sub=idx, ds=group_ds)
t = a.table()
# t.save_pdf(e.get('analysis-file') + '.pdf')
# t.save_tex(e.get('analysis-file') + '.tex')

opaque = ct.data[('opaque', 'first_constituent')] - ct.data[('opaque', 'control_constituent')]
simplex = ct.data[('simplex', 'first_constituent')] - ct.data[('simplex', 'control_constituent')]
transparent = ct.data[('transparent', 'first_constituent')] - ct.data[('transparent', 'control_constituent')]

Y = E.combine((opaque, simplex, transparent))
X = E.Factor(('opaque', 'simplex', 'transparent'),
             repeat=len(group_ds['subject'].cells), name='wordtype')
sub = E.Factor(group_ds['subject'].cells, tile=len(X.cells), name='subject', random=True)
group_int = E.Dataset()
group_int['subject'] = sub
group_int['latency'] = Y
group_int['wordtype'] = X

# p = E.plot.Barplot('latency', 'wordtype', match='subject', corr=False,
#                    ylabel='Priming Difference (ms)', xlabel='Word Type',
#                    title="Partial-Repetition Priming Onset Latency Difference Means",
#                    show=False, test=False, ds=group_int)
# p.figure.savefig(e.get('plot-file'))
#
# p = E.plot.Barplot('latency', 'wordtype', match='subject', corr=False, test=0,
#                    ylabel='Priming Difference (ms)', xlabel='Word Type',
#                    title="Partial-Repetition Priming Onset Latency Difference Means",
#                    show=False, ds=group_int)
# e.set(analysis='latency_revision_constituent_zero')
# p.figure.savefig(e.get('plot-file'))

wtypes = list(group_int['wordtype'].cells)
wtypes.remove('simplex')
planned_comparisons = []
for wtype in wtypes:
    idx = group_int['wordtype'].isany('simplex', wtype)
    ds = group_int[idx]
    a = E.test.anova(Y='latency', X='subject*wordtype', ds=ds)
    planned_comparisons.append((wtype, a))

idx = group_int['wordtype'].isany('transparent', 'opaque')
ds = group_int[idx]
a = E.test.anova(Y='latency', X='subject*wordtype', ds=ds)
planned_comparisons.append(('compounds', a))

