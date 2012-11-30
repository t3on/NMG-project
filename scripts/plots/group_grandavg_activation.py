import eelbrain.eellab as E
import os
import basic.process as process

e = process.NMG()

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'group_ds_epochs.pickled')
plots_dir = os.path.join(root, 'results', 'plots', 'meg', 'activation')



tstart = -0.1
tstop = 0.6
reject = 3e-12


stcs = []
subs = []
group_stcs = []

for _ in e.iter_vars(['subject']):
    meg_ds = e.load_events()
    index = meg_ds['target'].isany('prime', 'target')
    meg_ds = meg_ds[index]

#    #meg_ds = process.reject_blinks(meg_ds)
#    if 't_edf' in meg_ds:
#        del meg_ds['t_edf']

    #add epochs to the dataset after excluding bad channels
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                        #baseline=(tstart, 0), reject={'mag':reject}, preload=True)
                                        reject={'mag':reject}, preload=True)

    #do source transformation
    stcs.append(e.make_stcs(meg_ds, stc_type = 'evoked', force_fixed=False))
    del meg_ds['epochs']
    subs.append(e.get('subject'))

#combines the datasets for group
for stc, sub in zip(stcs,subs):
    stc = stc.summary('source', name = sub)
    group_stcs.append(stc)

#group_stcs = E.combine(group_stcs)
p = E.plot.uts.uts(group_stcs) 
#                   title = '%s Average Source Activation' %subject)
p.figure.savefig(os.path.join(plots_dir, 'group_grandavg_activation.pdf'))
