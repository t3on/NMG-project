
import eelbrain.eellab as E
import process, source
datadir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'talk', 'plots')

subjects = ['R0095', 'R0224', 'R0498', 'R0499', 'R0504']
group_ds = []

labels = ['lh.parstriangularis', 'lh.medialorbitofrontal']

tstart = -0.2
tstop = 0.4
reject = 3e-12

for subject in subjects:
    subject_datasets = []
        
    meg_ds = process.load_meg_events(subname = subject, expname='NMG', voiceproblem=True)
    index = meg_ds['target'] == 'target'
    
    meg_ds = meg_ds[index]
    meg_ds = process.reject_blinks(meg_ds)
    meg_ds = load.fiff.add_epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), threshold = reject)

    group_ds.append(meg_ds)
    
group_ds = E.combine(group_ds)
E.plot.topo.butterfly(group_ds['MEG'])