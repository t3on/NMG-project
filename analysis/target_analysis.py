'''
Created on Nov 26, 2012
  
@author: teon
'''
  
import os
import eelbrain.eellab as E
import basic.process as process
  
# raw data parameters
raw = 'hp1_lp40'
tstart = -0.1
tstop = 0.6
reject = {'mag': 3e-12}
  
# initialize experiment
e = process.NMG()
e.set(orient='fixed')
e.set(datatype='meg')
e.set(stat='anovas')
e.set(analysis='target')
e_type = 'evoked'
datasets = []
  
# experimental conditions
conditions = ['constituent', 'identity']
  
# rois
rois = [['lh.vmPFC', 'rh.vmPFC'], 'lh.ant_fusiform', 'lh.post_fusiform',
        'lh.LATL', 'lh.LPTL']
roilabels = ['vmPFC', 'ant_fusiform', 'post_fusiform', 'LATL', 'LPTL']
roititles = ['vmPFC', 'anterior Fusiform', 'posterior Fusiform', 'LATL',
             'Posterior Temporal Gyrii']
  
  
if os.path.lexists(e.get('group-file')):
    group_ds = pickle.load(open(e.get('group-file')))
else:
    for _ in e:
        meg_ds = e.process_evoked(raw=raw, e_type=e_type, tstart=tstart,
                                  tstop=tstop, reject=reject)
        if meg_ds is None:
            continue
        # filter
        meg_ds = meg_ds[meg_ds['target'] == 'target']
        # source computation
        meg_ds = e.source_evoked(meg_ds, rois, roilabels, tstart, tstop)
        # append to group level datasets
        datasets.append(meg_ds)
        # combines the datasets for group
    group_ds = E.combine(datasets)
    E.save.pickle(group_ds, e.get('group-file'))
    del datasets
  
#create index for only the constituent conditions
constituent = group_ds['condition'].isany('control_constituent',
                                          'first_constituent')
#creates index for only the identity conditions
identity = group_ds['condition'].isany('control_identity', 'identity')
  
sub = len(group_ds['subject'].cells)
e.logger.info('%d subjects entered into stats.\n %s'
              % (sub, group_ds['subject'].cells))

for roilabel, roititle in zip(roilabels, roititles):
    for condition in conditions:
        if condition == 'identity':
            sub = identity; tname = 'Identity'
        elif condition == 'constituent':
            sub = constituent; tname = 'Constituent'
        else:
            raise ValueError
        # test constituent effect
        title = ('%s Priming Effects in %s: %s orientation'
                 % (tname, roititle, e.get('orient')))
        a = E.testnd.anova(Y=group_ds[roilabel], X='condition*wordtype*subject',
                           ds=group_ds, sub=sub)
        p = E.plot.uts.UTSClusters(a, title=title)
        p.figure.savefig(os.path.join(e.get('plots_dir'), e.get('orient'),
                        '%s_anova_%s_%s.pdf' % (e.get('analysis'), condition, roilabel)))

        p = E.plot.uts.UTSStat(Y=group_ds[roilabel], X=group_ds['condition'],
                               sub=sub, title=title, ylabel='dSPM', 
                               legend='upper left',  w=16, h=16, axtitle=None)
        p.figure.savefig(os.path.join(e.get('plots_dir'), e.get('orient'), 
                                      '%s_%s_%s.pdf' % (e.get('analysis'), 
                                                        condition, roilabel)))

#        # subject plots
#        p = E.plot.uts.stat(Y=group_ds[roilabel], X=group_ds['condition'],
#                            sub=sub, Xax=group_ds['subject'], dev=None,
#                            figtitle=title, ylabel='dSPM', legend='upper left',
#                             width=15, height=9)
#        p.figure.savefig(os.path.join(wf_dir, 'subject_%s_%s.pdf'
#                                      % (condition, roilabel)))
#        # group plot (all)
#        p = E.plot.uts.stat(Y=group_ds[roilabel],
#                            X=group_ds['condition'] % group_ds['wordtype'],
#                            sub=sub, figtitle=title, ylabel='dSPM',
#                            colors=e.cm, dev=None,
#                            legend='upper left', width=15, height=9)
#        p.figure.savefig(os.path.join(wf_dir, 'group_%s_by_wordtype_%s.pdf'
#                                      % (condition, roilabel)))
