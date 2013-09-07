'''
Created on Dec 2, 2012
 
@author: teon
'''
 
import os
import numpy as np
import basic.process as process
import eelbrain.eellab as E
 
 
group_ds = []
e = process.NMG()
e.exclude = {}
e.set(datatype='behavioral')
e.set(stat='anovas')
e.set(analysis='latency')
 
 
for _ in e:
    ds = e.load_events(proj=False)
    ds = ds[ds['target'] == 'target']
    orig_N = ds.n_cases
 
    # outlier rejection
    devs = np.abs(ds['latency'].x - ds['latency'].x.mean())
    criterion = 2 * ds['latency'].x.std().repeat(ds.n_cases)
    good = devs < criterion
    ds = ds[good]
 
    remainder = ds.n_cases * 100. / orig_N
    e.logger.info('latency: %d' % remainder + r'% ' + 'remain after outlier rejection')
    group_ds.append(ds)
 
group_ds = E.combine(group_ds)
group_ds = group_ds.compress(group_ds['condition'] % group_ds['wordtype'] %
                             group_ds['subject'], drop_bad=True)
group_ds.save_txt(e.get('analysis-file'))

###########################
#    constituent anova    #
###########################

idx = group_ds['condition'].isany('control_constituent', 'first_constituent')
a = E.test.anova(Y= group_ds['latency'], X='subject * wordtype * condition', 
                 sub=idx, ds=group_ds)

###########################
#     identity anova      #
###########################

idx = group_ds['condition'].isany('control_identity', 'identity')
a2 = E.test.anova(Y= group_ds['latency'], X='subject * wordtype * condition', 
                 sub=idx, ds=group_ds)

 
# relabeling conditions
idy = group_ds['condition'] == 'control_constituent'
group_ds['c'] = group_ds['condition']
group_ds['c'][idy] = 'c_c'
idz = group_ds['c'] == 'first_constituent'
group_ds['c'][idz] = 'f_c'
 
# plot constituent conditions
ct = E.Celltable(group_ds['latency'],
                 group_ds['wordtype'] % group_ds['c'],
                 match=group_ds['subject'])
novel = ct.data[('novel', 'f_c')] - ct.data[('novel', 'c_c')]
opaque = ct.data[('opaque', 'f_c')] - ct.data[('opaque', 'c_c')]
ortho = ct.data[('ortho', 'f_c')] - ct.data[('ortho', 'c_c')]
transparent = ct.data[('transparent', 'f_c')] - ct.data[('transparent', 'c_c')]

Y = E.combine((novel, opaque, ortho, transparent))
X = E.Factor(('novel', 'opaque', 'ortho', 'transparent'),
             rep=len(group_ds['subject'].cells), name='wordtype')
sub = E.Factor(group_ds['subject'].cells, rep=len(X.cells), name='subject', random=True)
group_plot = E.Dataset(sub, Y, X)
p = E.plot.uv.boxplot(Y, X, match=sub, figsize=(20, 5),
                       title="Constituent Condition Group Latency Means")
# #p.fig.savefig(os.path.join(plots_dir, 'group_box_latency_constituent.pdf'))
# p = E.plot.uv.barplot(Y, X, match=sub, figsize=(20, 5),
#                       ylabel='Latency Difference in s',
#                       title="Constituent Condition Group Latency Means")
# p.fig.savefig(os.path.join(e.get('plots_dir'), 'group_bar_latency_constituent.pdf'))

#
#########################
##    identity anova    #
#########################
#
## write out stats
#idx = group_ds['condition'].isany('control_identity', 'identity')
#a2 = E.test.anova(Y=group_ds['latency'], X=group_ds['subject'] *
#                  group_ds['wordtype'] * group_ds['condition'])
#t2 = E.table.rm_table(Y=group_ds['latency'], X=group_ds['wordtype'] %
#                      group_ds['condition'], match=group_ds['wordtype'] %
#                      group_ds['condition'], fmt='%0.3f', sub=idx)
#with open(identity_stats, 'w') as FILE:
#    FILE.write(str(a2) + '\r\n')
#    FILE.write(str(t2))
#
#
## relabeling conditions
#idy = group_ds['condition'] == 'control_identity'
#group_ds['condition'][idy] = 'c_i'
#idz = group_ds['condition'] == 'identity'
#group_ds['condition'][idz] = 'i'
#
## plot identity conditions
#identity_cells = (group_ds['wordtype'] % group_ds['condition'])
#p2 = E.plot.uv.boxplot(Y=group_ds['latency'], X=identity_cells, sub=idx,
#                       match=group_ds['subject'], figsize=(10, 5),
#                       bottom=.4, title="Identity Condtition Group Latency Means")
#p2.fig.savefig(os.path.join(plots_dir, 'group_box_latency_identity.pdf'))
#p2a = E.plot.uv.barplot(Y=group_ds['latency'], X=identity_cells, sub=idx,
#                        match=group_ds['subject'], figsize=(10, 5),
#                        bottom=.4, title="Identity Condtition Group Latency Means")
#p2a.fig.savefig(os.path.join(plots_dir, 'group_bar_latency_identity.pdf'))
