'''
Created on Nov 28, 2012

@author: teon
'''

import basic.process as process
import os
import mne

e = process.NMG()

for _ in e.iter_vars('mrisubject'):
    meg_ds = e.load_events()
    
    lmedial = mne.read_label(os.path.join(meg_ds.info['labeldir'], 
                                          'lh.lateralorbitofrontal.label'))
    llateral = mne.read_label(os.path.join(meg_ds.info['labeldir'], 
                                           'lh.medialorbitofrontal.label'))
    lvmPFC = lmedial + llateral

    rmedial = mne.read_label(os.path.join(meg_ds.info['labeldir'], 
                                          'rh.lateralorbitofrontal.label'))
    rlateral = mne.read_label(os.path.join(meg_ds.info['labeldir'], 
                                           'rh.medialorbitofrontal.label'))
    rvmPFC = rmedial + rlateral


    mne.write_label(os.path.join(meg_ds.info['labeldir'], 
                                 'lh.vmPFC.label'), lvmPFC)
    mne.write_label(os.path.join(meg_ds.info['labeldir'], 
                                 'rh.vmPFC.label'), rvmPFC)
