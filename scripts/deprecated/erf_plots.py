#Modification of the sensor cluster used in Morris (2007).
##T7/8 > P7/8
##There are no T3/4 sensors. Instead there are three additional midline electrodes:
###FCz, CPz, POz
##with load.fiff.add_epochs, the sensors are indexed starting with 0. May differ if working in mne.

import eelbrain.eellab as E
import process, source
datadir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'results', 'plots', 'meg', 'erfs')

subjects = ['R0095', 'R0498', 'R0504', 'R0414', 'R0547', 'R0569', 'R0574', 'R0575', 'R0576']
labels = ['lh.fusiform', 'lh.medialorbitofrontal', 'lh.temporalpole']
group_ds = []

tstart = -0.2
tstop = 0.4
reject = 3e-12

for subject in subjects:
    subject_datasets = []
        
    meg_ds = process.load_meg_events(subname = subject, expname='NMG', voiceproblem=True)
    index = meg_ds['target'] == 'target'

    meg_ds = meg_ds[index]
    meg_ds = process.reject_blinks(meg_ds)
    meg_ds = load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), reject={'mag':reject}, preload=True)

    for lbl in labels:
        ds = source.make_stc_epochs(meg_ds, tstart = tstart, tstop = tstop, reject = reject, label = lbl, force_fixed = True, from_file = True, method = 'rms')
#Append to subject level datasets        
        subject_datasets.append(ds)

#Combines label into one dataset   
    subject_ds = E.combine(subject_datasets)
    group_ds.append(subject_ds)

group_ds = E.combine(group_ds)

#[('identity', 'opaque'), ('identity', 'transparent'), ('identity', 'novel'), ('identity', 'ortho'), ('control_constituent', 'opaque'), ('control_constituent', 'transparent'), ('control_constituent', 'novel'), ('control_constituent', 'ortho'), ('control_identity', 'opaque'), ('control_identity', 'transparent'), ('control_identity', 'novel'), ('control_identity', 'ortho'), ('first_constituent', 'opaque'), ('first_constituent', 'transparent'), ('first_constituent', 'novel'), ('first_constituent', 'ortho')]

graph_colors = dict({'control_identity': 'blue', 'control_constituent': 'blue', 'identity': 'green', 
                     'first_constituent': 'green'})


for lbl in labels:
    identity = group_ds[group_ds['condition'].isany('identity', 'control_identity')]
    identity = identity[identity['label'] == lbl]
    a = E.plot.uts.stat(identity['stc'], identity['condition'], legend = 'lower center', dev = None, colors = graph_colors)
    a.figure.savefig(os.path.join(datadir, 'priming_%s_identity.png' %lbl))
    
    constituent = group_ds[group_ds['condition'].isany('first_constituent', 'control_constituent')]
    constituent = constituent[constituent['label'] == lbl]
    b = E.plot.uts.stat(constituent['stc'], constituent['condition'], legend = 'lower center', dev = None, colors = graph_colors)
    b.figure.savefig(os.path.join(datadir, 'priming_%s_constituent.png' %lbl))
    
    b2 = E.plot.uts.stat(constituent['stc'], constituent['wordtype']%constituent['condition'], 
                         legend = 'lower center', dev = None)
    b2.figure.savefig(os.path.join(datadir, 'wt_priming_%s_constituent.png' %lbl))
    
    #Plots
    for type in group_ds['wordtype'].cells:
        a = identity[identity['wordtype'] == type]
        b = constituent[constituent['wordtype'] == type]
       
        a = E.plot.uts.stat(a['stc'], a['condition'], legend = 'lower center', dev = None, colors = graph_colors)
        #a.figure.legend(prop={'size':6})
        a.figure.savefig(os.path.join(datadir, '%s_%s_identity.png' %(lbl, type)))
        
        b = E.plot.uts.stat(b['stc'], b['condition'], legend = 'lower center', dev = None, colors = graph_colors)
        b.figure.savefig(os.path.join(datadir, '%s_%s_constituent.png' %(lbl, type)))
