import eelbrain.eellab as E
import process
import source
import copy
import os


subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']), ('R0504', ['MEG 031']),
            ('R0414', []), ('R0547', ['MEG 002']), ('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084']),
            ('R0574', []), ('R0575', []), ('R0576', ['MEG 0143', 'MEG 046'])]
labels = ['lh.fusiform', 'lh.medialorbitofrontal', 'lh.temporalpole']
#'lh.parstriangularis', 'lh.superiortemporal', 'lh.lateralorbitofrontal'
#maybe AMF
datasets = []

tstart = -0.1
tstop = 0.4
reject = 3e-12

for subject in subjects:
    subject_datasets = []
        
    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')
    index = meg_ds['target'] == 'target'

#create picks to remove bad channels
    if subject[1]:
        meg_ds.info['raw'].info['bads'].extend(subject[1])

    meg_ds = meg_ds[index]
    #meg_ds = process.reject_blinks(meg_ds)
    
    #add epochs to the dataset after excluding bad channels
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), reject={'mag':reject}, preload=True)

    for lbl in labels:
        ds = copy.copy(source.make_stc_epochs(meg_ds, tstart=tstart, tstop=tstop, reject=reject, label=lbl, force_fixed=True, from_file=True, method='rms'))

        ds['m170'] = ds['stc'].summary(time = (.12, .22))
        ds['m250'] = ds['stc'].summary(time = (.2, .3))
        ds['m350'] = ds['stc'].summary(time = (.3, .4))

        del ds['stc']

        del ds['epochs']

        #Append to subject level datasets        
        subject_datasets.append(ds)

    #Combines label into one dataset   
    subject_ds = E.combine(subject_datasets)
    subject_ds.info = subject_datasets[0].info

    #Append to group level datasets
    datasets.append(subject_ds)

#Exports the source estimate ERFs 

#combines the datasets for group
group_ds = E.combine(datasets)
#Defines filepaths
datadir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'data')
group_ds.info['erfs'] = os.path.join(datadir, '%s_%s_erfs.txt' % ('NMG', 'group'))

group_ds.export(fn = group_ds.info['erfs'])
