'''
Created on Dec 2, 2012

@author: teon
'''

import os
import numpy as np
import basic.process as process
import eelbrain.eellab as E

e = process.NMG(None, '{db_dir}')
group_ds = []
subjects = ['R0095', 'R0224', 'R0338', 'R0370', 'R0494', 'R0498']

for subject in subjects:
    e.set(subject)
    ds = e.get_word_duration(block=1)
    orig_N = ds.n_cases
    ds['duration'] = ds['c1_dur']
    idx = ds['ortho'] == 'ortho-2'
    ds[idx]['duration'] = ds[idx]['c2_dur']
    
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
group_ds = group_ds.compress('condition % wordtype % subject', drop_bad=True)
group_ds['opaque'] = E.Var(np.array((group_ds['wordtype'] == 'opaque'), float))
group_ds['transparent'] = E.Var(np.array((group_ds['wordtype'] == 'transparent'), float))
group_ds['novel'] = E.Var(np.array((group_ds['wordtype'] == 'novel'), float))

group_ds.save_txt(e.get('group_ds-file', analysis='duration'))
#   
# idx = group_ds['condition'].isany('control_constituent', 'first_constituent')
# a = E.test.anova(Y=group_ds['duration'], X= 'subject * wordtype * condition', 
#                  ds=group_ds, sub=idx)
# t = E.table.rm_table(Y=group_ds['duration'], X=group_ds['wordtype'] %
#                      group_ds['condition'], match=group_ds['wordtype'] %
#                      group_ds['condition'], fmt='%0.3f', sub=idx)
# # relabeling conditions
# idy = group_ds['condition'] == 'control_constituent'
# group_ds['condition'][idy] = 'c_c'
# idz = group_ds['condition'] == 'first_constituent'
# group_ds['condition'][idz] = 'f_c'
 
# 
# # plot constituent conditions
# ct = E.Celltable(group_ds['duration'],
#                  group_ds['wordtype'] % group_ds['condition'],
#                  match=group_ds['subject'])
# novel = ct.data[('novel', 'f_c')] - ct.data[('novel', 'c_c')]
# opaque = ct.data[('opaque', 'f_c')] - ct.data[('opaque', 'c_c')]
# ortho = ct.data[('ortho', 'f_c')] - ct.data[('ortho', 'c_c')]
# transparent = ct.data[('transparent', 'f_c')] - ct.data[('transparent', 'c_c')]
# Y = E.combine((novel, opaque, ortho, transparent))*1e3
# X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
#              rep=len(group_ds['subject'].cells), name='wordtype')
# sub = E.Factor(group_ds['subject'].cells, rep=len(X.cells), name='subject', random=True)
# group_plot = E.Dataset(sub, Y, X)
# 
# p = E.plot.uv.barplot(Y, X, match=sub, figsize=(20, 5),
#                       ylabel='Duration Difference in ms',
#                       title="Constituent Condition Group Latency Means")
# p.fig.savefig(os.path.join(plots_dir, 'group_bar_latency_constituent.pdf'))
# 
# #########################
# ##    identity anova    #
# #########################
# 
# ## write out stats
# #idx = group_ds['condition'].isany('control_identity', 'identity')
# #a2 = E.test.anova(Y=group_ds['latency'], X=group_ds['subject'] *
# #                  group_ds['wordtype'] * group_ds['condition'])
# #t2 = E.table.rm_table(Y=group_ds['latency'], X=group_ds['wordtype'] %
# #                      group_ds['condition'], match=group_ds['wordtype'] %
# #                      group_ds['condition'], fmt='%0.3f', sub=idx)
# #with open(identity_stats, 'w') as FILE:
# #    FILE.write(str(a2) + '\r\n')
# #    FILE.write(str(t2))
# #
# #
# ## relabeling conditions
# #idy = group_ds['condition'] == 'control_identity'
# #group_ds['condition'][idy] = 'c_i'
# #idz = group_ds['condition'] == 'identity'
# #group_ds['condition'][idz] = 'i'
# #
# ## plot identity conditions
# #identity_cells = (group_ds['wordtype'] % group_ds['condition'])
# #p2 = E.plot.uv.boxplot(Y=group_ds['latency'], X=identity_cells, sub=idx,
# #                       match=group_ds['subject'], figsize=(10, 5),
# #                       bottom=.4, title="Identity Condtition Group Latency Means")
# #p2.fig.savefig(os.path.join(plots_dir, 'group_box_latency_identity.pdf'))
# #p2a = E.plot.uv.barplot(Y=group_ds['latency'], X=identity_cells, sub=idx,
# #                        match=group_ds['subject'], figsize=(10, 5),
# #                        bottom=.4, title="Identity Condtition Group Latency Means")
# #p2a.fig.savefig(os.path.join(plots_dir, 'group_bar_latency_identity.pdf'))
# 
# # Marginal Means
# t
# 
# 
# # ANOVA
# a.F_tests
# 
# # Plotting
# 
# # plot constituent conditions
# ct = E.Celltable('duration', 'wordtype % condition',
#                  match='subject', ds=group_ds)
# novel = ct.data[('novel', 'c_c')] - ct.data[('novel', 'f_c')]
# opaque = ct.data[('opaque', 'c_c')] - ct.data[('opaque', 'f_c')]
# ortho = ct.data[('ortho', 'c_c')] - ct.data[('ortho', 'f_c')]
# transparent = ct.data[('transparent', 'c_c')] - ct.data[('transparent', 'f_c')]
# Y = E.Var(E.combine((novel, opaque, ortho, transparent))*1e3, 'duration')
# X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
#              rep=len(group_ds['subject'].cells), name='wordtype')
# subject = E.Factor(group_ds['subject'].cells, tile=len(X.cells), name='subject', random=True)
# group_plot = E.Dataset(subject, Y, X)
# 
# ds = group_plot.compress('wordtype', drop_bad=True)
# 
# plt.bar(ds['wordtype'].x, ds['duration'].x)
# plt.xticks(ds['wordtype'].x+.5, ds['wordtype'].as_labels())
