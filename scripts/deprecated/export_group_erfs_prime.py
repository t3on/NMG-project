import eelbrain.eellab as E
import process
import source

subjects = ['R0095', 'R0498', 'R0504']
labels = ['lh.fusiform', 'lh.temporalpole', 'lh.parstriangularis', 'lh.superiortemporal', 'lh.medialorbitofrontal', 'lh.lateralorbitofrontal']
#maybe AMF
datasets = []

tstart = -0.2
tstop = 0.4
reject = 3e-12

for subject in subjects:
    subject_datasets = []
        
    meg_ds = process.load_meg_events(subname = subject, expname='NMG', voiceproblem=True)
    index = meg_ds['target'] == 'prime'

    meg_ds = meg_ds[index]
    meg_ds = process.reject_blinks(meg_ds)
    meg_ds.info['epochs'] = load.fiff.mne_Epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), reject={'mag':reject}, preload=True)

    for lbl in labels:
        ds = source.make_stc_epochs(meg_ds, tstart = tstart, tstop = tstop, reject = reject, label = lbl, force_fixed = True, from_file = True, method = 'rms')

        ds['m170'] = ds['stc'].summary(time = (.12, .22))
        ds['m250'] = ds['stc'].summary(time = (.2, .3))
        ds['m350'] = ds['stc'].summary(time = (.3, .4))

        del ds['stc']

#Append to subject level datasets        
        subject_datasets.append(ds)

#Combines label into one dataset   
    subject_ds = E.combine(subject_datasets)
    subject_ds.info = subject_datasets[0].info
#Append to group level datasets
    datasets.append(subject_ds)
#Exports the source estimate epochs and ERFs 
    #source.export_stcs(subject_ds)
    subject_ds.export(fn = ds.info['erfs'])

#combines the datasets for group
group_ds = E.combine(datasets)
#Defines filepaths
group_ds.info['datadir'] = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'data')
group_ds.info['erfs'] = os.path.join(group_ds.info['datadir'], '%s_%s_erfs.txt' %('NMG', 'group'))
#group_ds.info['stc_ds'] = os.path.join(group_ds.info['datadir'], '%s_%s_stc_ds.txt' %('NMG', 'group'))
#group_ds.info['stc'] = os.path.join(group_ds.info['datadir'], '%s_%s_stc.txt' %('NMG', 'group'))
#Exports the epochs and ERFs
#source.export_stcs(group_ds)
group_ds.export(fn = group_ds.info['erfs'])