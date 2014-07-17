'''
Created on Dec 2, 2012

@author: teon
'''

import os
import numpy as np
import basic.process as process
import eelbrain.eellab as E

redo = True
e = process.NMG(None, '{db_dir}')
e.set(datatype='behavioral')
e.set(analysis='duration')
e.exclude['subject'].extend(['R0414', 'R0499', 'R0575'])
group_ds = []
# subjects = ['R0095', 'R0224', 'R0338', 'R0370', 'R0494', 'R0498',
#             'R0504', 'R0547', 'R0560', 'R0562', 'R0569', 'R0574',
#             # 'R0575',
#             'R0605']

if not redo and os.path.exists(e.get('agg-file')):
    group_ds = E.load.txt.tsv(e.get('agg-file'))
    group_ds['subject'].random = True
else:
    for _ in e:
        ds = e.get_word_duration(block=1)
        orig_N = ds.n_cases
        ds['duration'] = ds['c1_dur']
#         idx = ds['ortho'] == 'ortho-2'
#         ds[idx]['duration'] = ds[idx]['c2_dur']
        idx = ds['ortho'] == 'ortho-2'
        ds = ds[~idx]

        # outlier rejection
        idx = ds['duration'].x != 0
        ds = ds[idx]

        devs = np.abs(ds['duration'].x - ds['duration'].x.mean())
        criterion = 2 * ds['duration'].x.std().repeat(ds.n_cases)
        good = devs < criterion
        ds = ds[good]

        remainder = ds.n_cases * 100. / orig_N
        e.logger.info('duration: %d' % remainder + r'% ' + 'remain after outlier rejection')
        group_ds.append(ds)

    group_ds = E.combine(group_ds)
#     group_ds = group_ds.compress('condition % wordtype % subject', drop_bad=True)
    group_ds.save_txt(e.get('agg-file'))

# ct = E.Celltable(Y='duration', X='wordtype % condition', match='subject', ds=group_ds)
#
#
# ###########################
# #    constituent anova    #
# ###########################
# e.set(analysis='duration_constituent')
# idx = group_ds['condition'].isany('control_constituent', 'first_constituent')
# a = E.test.anova(Y='duration', X='subject*wordtype*condition', sub=idx, ds=group_ds)
# t = a.table()
# t.save_pdf(e.get('analysis-file') + '.pdf')
# t.save_tex(e.get('analysis-file') + '.tex')
#
# novel = ct.data[('novel', 'control_constituent')] - ct.data[('novel', 'first_constituent')]
# opaque = ct.data[('opaque', 'control_constituent')] - ct.data[('opaque', 'first_constituent')]
# ortho = ct.data[('ortho', 'control_constituent')] - ct.data[('ortho', 'first_constituent')]
# transparent = ct.data[('transparent', 'control_constituent')] - ct.data[('transparent', 'first_constituent')]
#
# Y = E.combine((novel, opaque, ortho, transparent))
# X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
#              rep=len(group_ds['subject'].cells), name='wordtype')
# sub = E.Factor(group_ds['subject'].cells, rep=len(X.cells), name='subject', random=True)
# group_plot = E.Dataset(sub, Y, X)
#
# p = E.plot.uv.barplot(Y, X, match=sub, figsize=(10, 5), corr=False,
#                       ylabel='Duration Priming Difference in ms',
#                       title="Constituent Priming Duration Difference Means")
# p.fig.savefig(e.get('plot-file'))
#
# a = E.test.pairwise(Y, X, match=sub, corr=None)
# a.save_tex(e.get('analysis-file') + '-pairwise.tex')
# a.save_pdf(e.get('analysis-file') + '-pairwise.pdf')
#
# #########################
# #    identity anova     #
# #########################
# e.set(analysis='duration_identity')
# idx = group_ds['condition'].isany('control_identity', 'identity')
# a2 = E.test.anova(Y='duration', X='subject * wordtype * condition',
#                  sub=idx, ds=group_ds)
# t2 = a2.table()
# t2.save_pdf(e.get('analysis-file') + '.pdf')
# t2.save_tex(e.get('analysis-file') + '.tex')
#
# novel = ct.data[('novel', 'control_identity')] - ct.data[('novel', 'identity')]
# opaque = ct.data[('opaque', 'control_identity')] - ct.data[('opaque', 'identity')]
# ortho = ct.data[('ortho', 'control_identity')] - ct.data[('ortho', 'identity')]
# transparent = ct.data[('transparent', 'control_identity')] - ct.data[('transparent', 'identity')]
#
# Y = E.combine((novel, opaque, ortho, transparent))
# X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
#              rep=len(group_ds['subject'].cells), name='wordtype')
# sub = E.Factor(group_ds['subject'].cells, rep=len(X.cells), name='subject', random=True)
# group_plot = E.Dataset(sub, Y, X)
#
# p2 = E.plot.uv.barplot(Y, X, match=sub, figsize=(20, 5), corr=False,
#                        ylabel='Duration Priming Difference in ms',
#                        title="Identity Priming Duration Difference Means")
# p2.fig.savefig(e.get('plot-file'))
#
# a2 = E.test.pairwise(Y, X, match=sub, corr=None)
# a2.save_tex(e.get('analysis-file') + '-pairwise.tex')
# a.save_pdf(e.get('analysis-file') + '-pairwise.pdf')
