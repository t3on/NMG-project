'''
Created on Dec 2, 2012

@author: teon
'''

import basic.process as process
import eelbrain.eellab as E
from eelbrain.vessels.structure import celltable

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
plots_dir = os.path.join(root, 'results', 'behavioral',  'stats')
stats_dir = os.path.join(root, 'results', 'behavioral', 'stats')
constituent_stats = os.path.join(stats_dir, 'group_latency_constituent.txt')
identity_stats = os.path.join(stats_dir, 'group_latency_identity.txt')
log_file = os.path.join(root, 'results', 'logs', 'group_latency_log.txt')

group_ds = []
e = process.NMG()

for _ in e.iter_vars(['subject']):
    ds = e.load_events(proj = False)
    ds = ds[ds['target'] == 'target']
    orig_N = ds.N
    
    # outlier rejection
    devs = np.abs(ds['latency'].x - ds['latency'].x.mean())
    criterion = 2*ds['latency'].x.std().repeat(ds.N)
    good = devs < criterion
    ds = ds[good]
    
    remainder = ds.N*100./orig_N
    e.logger('latency: %d' %remainder + r'% ' + 'remain after outlier rejection') 
    group_ds.append(ds)

e.print_log(log_file)
group_ds = E.combine(group_ds)
group_ds = group_ds.compress(group_ds['condition'] % group_ds['wordtype'] %
                             group_ds['subject'], drop_bad=True)


############################
##    constituent anova    #
############################
#
#group = group_ds.compress(group_ds['wordtype'] % group_ds['subject'], drop_bad=True)
#idx = group_ds['condition'].isany('control_constituent', 'first_constituent')
#
#table = celltable(Y='latency', X='condition', match='subject', sub=idx,
#          match_func=np.mean, ds=group_ds)
#priming = table.data['first_constituent'] - table.data['control_constituent']
#wordtype = table.groups
#subject = table.match
###a1 = E.test.anova(Y=group_ds['first_constituent']['latency'], X=group_ds['subject'] *
###                  group_ds['wordtype'] * group_ds['condition'], sub = idx)




###########################
#    constituent anova    #
###########################

idx = group_ds['condition'].isany('control_constituent', 'first_constituent')
a1 = E.test.anova(Y = group_ds['latency'], X = group_ds['subject'] *
                  group_ds['wordtype'] * group_ds['condition'], sub = idx)
t1 = E.table.rm_table(Y = group_ds['latency'], X=group_ds['wordtype'] % 
                      group_ds['condition'], match=group_ds['wordtype'] % 
                      group_ds['condition'], fmt = '%0.3f', sub = idx)
with open(constituent_stats,'w') as FILE:
    FILE.write(str(a1) + '\r\n')
    FILE.write(str(t1))
    

# relabeling conditions
idy = group_ds['condition'] == 'control_constituent'
group_ds['condition'][idy] = 'c_c'
idz = group_ds['condition'] == 'first_constituent'
group_ds['condition'][idz] = 'f_c'

# plot constituent conditions
constituent_cells = (group_ds['wordtype'] % group_ds['condition'])
p1 = E.plot.uv.boxplot(Y = group_ds['latency'], X = constituent_cells, 
                       match = group_ds['subject'], figsize=(10,5), sub = idx,
                  bottom=.4, title="Constituent Condition Group Latency Means")
p1.fig.savefig(os.path.join(plots_dir, 'group_box_latency_constituent.pdf'))
p1a = E.plot.uv.barplot(Y = group_ds['latency'], X = constituent_cells, 
                       match = group_ds['subject'], figsize=(10,5), sub = idx,
                  bottom=.4, title="Constituent Condition Group Latency Means")
p1a.fig.savefig(os.path.join(plots_dir, 'group_bar_latency_constituent.pdf'))


# plot constituent conditions
constituent_cells = (group_ds['wordtype'] % group_ds['condition'])
p1 = E.plot.uv.boxplot(Y = group_ds['latency'], X = constituent_cells, 
                       match = group_ds['subject'], figsize=(10,5), sub = idx,
                  bottom=.4, title="Constituent Condition Group Latency Means")
p1.fig.savefig(os.path.join(plots_dir, 'group_box_latency_constituent.pdf'))
p1a = E.plot.uv.barplot(Y = group_ds['latency'], X = constituent_cells, 
                       match = group_ds['subject'], figsize=(10,5), sub = idx,
                  bottom=.4, title="Constituent Condition Group Latency Means")
p1a.fig.savefig(os.path.join(plots_dir, 'group_bar_latency_constituent.pdf'))


########################
#    identity anova    #
########################

# write out stats
idx = group_ds['condition'].isany('control_identity', 'identity')
a2 = E.test.anova(Y = group_ds['latency'], X = group_ds['subject'] *
                  group_ds['wordtype'] * group_ds['condition'])
t2 = E.table.rm_table(Y = group_ds['latency'], X=group_ds['wordtype'] % 
                      group_ds['condition'], match=group_ds['wordtype'] % 
                      group_ds['condition'], fmt = '%0.3f', sub = idx)
with open(identity_stats,'w') as FILE:
    FILE.write(str(a2) + '\r\n')
    FILE.write(str(t2))


# relabeling conditions
idy = group_ds['condition'] == 'control_identity'
group_ds['condition'][idy] = 'c_i'
idz = group_ds['condition'] == 'identity'
group_ds['condition'][idz] = 'i'

# plot identity conditions
identity_cells = (group_ds['wordtype'] % group_ds['condition'])
p2 = E.plot.uv.boxplot(Y = group_ds['latency'], X = identity_cells, sub = idx,
                       match = group_ds['subject'], figsize=(10,5),
                       bottom=.4, title="Identity Condtition Group Latency Means")
p2.fig.savefig(os.path.join(plots_dir, 'group_box_latency_identity.pdf'))
p2a = E.plot.uv.barplot(Y = group_ds['latency'], X = identity_cells, sub = idx,
                        match = group_ds['subject'], figsize=(10,5), 
                        bottom=.4, title="Identity Condtition Group Latency Means")
p2a.fig.savefig(os.path.join(plots_dir, 'group_bar_latency_identity.pdf'))
