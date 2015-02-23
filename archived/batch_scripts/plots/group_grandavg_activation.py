'''
Created on Nov 30, 2012

@author: teon
'''

import eelbrain.eellab as E
import os
import basic.process as process
import pickle

# raw data parameters
filter = 'hp1_lp40'
tstart = -0.1
tstop = 0.6
reject = 3e-12

# analysis parameters
orient = 'free'
e_type = 'evoked'

# experiment parameters
e = process.NMG()
e.set(raw='hp1_lp40')
e.set(analysis='_'.join((e_type, filter, str(tstart), str(tstop))))

# directory info
plots_dir = os.path.join(e.get('exp_db'), 'results', 'meg', 'qualitative')

# roi
roi = ['lh.cuneus', 'rh.cuneus']
group_stcs = []

for _ in e.iter_vars(['subject']):
    stcs = []
    subs = []
    if os.path.lexists('data-file'):
        meg_ds = pickle.load(open(e.get('data-file')))
else:
    meg_ds = e.load_events()
    index = meg_ds['target'].isany('prime', 'target')
    meg_ds = meg_ds[index]

    #add epochs to the dataset after excluding bad channels
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                        baseline=None, reject={'mag':reject},
                                        preload=True)
#do source transformation
stc = e.make_stcs(meg_ds, stc_type=e_type, force_fixed=False)
roi = e.read_label(labels=roi)
roi = stc.in_label(roi)
mri = e.get('mrisubject')
roi = E.load.fiff.stc_ndvar(roi, subject=mri)
roi = roi.summary('source', name='stc')
roi.x -= roi.summary(time=(tstart, 0))
del meg_ds['epochs'], stc
stcs.append(roi)
subs.append(e.get('subject'))

#combines the datasets for group
stcs = E.combine(stcs)
subjects = E.factor(subs, name='subject')
group_stcs = E.dataset(stcs, subjects)

p = E.plot.uts.uts(E.plot.unpack(group_stcs['stc'], group_stcs['subject']))
p.figure.savefig(os.path.join(plots_dir, 'group_grandavg_activation.pdf'))
