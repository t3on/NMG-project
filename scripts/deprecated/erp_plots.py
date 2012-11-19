#Modification of the sensor cluster used in Morris (2007).
##T7/8 > P7/8
##There are no T3/4 sensors. Instead there are three additional midline electrodes:
###FCz, CPz, POz
##with load.fiff.add_epochs, the sensors are indexed starting with 0. May differ if working in mne.

import eelbrain.eellab as E
import process, source
datadir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'results', 'plots', 'eeg', 'erps')

subjects = ['R0095', 'R0224', 'R0498', 'R0504']
group_ds = []

for subject in subjects:
    eeg_ds = process.eeg_align(subject)
    eeg_ds = process.reject_blinks(eeg_ds)
    #eeg_ds = eeg_ds.subset(eeg_ds['target'] == 'target')
  
    eeg_ds.info['sns_clusters'] = dict(
            outer = E.var([0, 1, 8, 9, 10, 11, 12, 13]),
            midlateral = E.var([2, 3, 6, 7, 24, 25, 26, 27]),
            inner = E.var([4, 5, 20, 21, 22, 23]),
            midline = E.var([14, 15, 16, 17, 18, 19]))
        
    load.fiff.add_epochs(eeg_ds, tstart =-.2, tstop = .5, baseline= (-.2,0), mult=1e6, unit='uV',
                         proj=False, data='eeg', target='EEG', i_start = 'i_start_eeg', sensors = eeg_ds.info['sensors'])
    
    eeg_ds['outer'] = eeg_ds['EEG'].subdata(sensor = eeg_ds.info['sns_clusters']['outer'].x)
    eeg_ds['outer'] = eeg_ds['outer'].summary('sensor')
    
    eeg_ds['midlateral'] = eeg_ds['EEG'].subdata(sensor = eeg_ds.info['sns_clusters']['midlateral'].x)
    eeg_ds['midlateral'] = eeg_ds['midlateral'].summary('sensor')
        
    eeg_ds['inner'] = eeg_ds['EEG'].subdata(sensor = eeg_ds.info['sns_clusters']['inner'].x)
    eeg_ds['inner'] = eeg_ds['inner'].summary('sensor')
    
    eeg_ds['midline'] = eeg_ds['EEG'].subdata(sensor = eeg_ds.info['sns_clusters']['midline'].x)
    eeg_ds['midline'] = eeg_ds['midline'].summary('sensor')
 
    del eeg_ds['EEG'], eeg_ds['size'], eeg_ds['channel']
    
    group_ds.append(eeg_ds)

full_group_ds = E.combine(group_ds)
targettype = ['prime', 'target']
clusters = ['outer', 'midlateral', 'inner', 'midline']

for word in targettype:
    group_ds = full_group_ds[full_group_ds['target'] == word]
    for cluster in clusters:
        identity = group_ds[group_ds['condition'].isany('identity', 'control_identity')]
        #a = E.plot.uts.stat(identity[cluster], identity['condition'], invy = True)
        a = E.plot.uts.stat(identity[cluster], identity['wordtype']%identity['condition'], 
                             legend = None, dev = None)
        a.figure.savefig(os.path.join(datadir, '%s_%s_identity.png' %(word, cluster)))
        
        constituent = group_ds[group_ds['condition'].isany('first_constituent', 'control_constituent')]
        #b = E.plot.uts.stat(constituent[cluster], constituent['condition'], invy = True)
        b = E.plot.uts.stat(constituent[cluster], constituent['wordtype']%constituent['condition'], 
                             legend = None, dev = None)
        b.figure.savefig(os.path.join(datadir, '%s_%s_constituent.png' %(word, cluster)))
    
#    #Plots
#    for type in group_ds['wordtype'].cells:
#        a = identity[identity['wordtype'] == type]
#        b = constituent[constituent['wordtype'] == type]
#       
#        a = E.plot.uts.stat(a[cluster], a['condition'], invy = True)
#        a.savefig(os.path.join(datadir, '%s_%s_identity.png' %(cluster, type)))
#        
#        b = E.plot.uts.stat(b[cluster], b['condition'], invy = True)
#        b.savefig(os.path.join(datadir, '%s_%s_constituent.png' %(cluster, type)))