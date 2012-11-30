'''
Created on Nov 19, 2012

@author: teon
'''

import eelbrain.utils.kit as kit
import basic.process as process
import os
import mne

e = process.NMG()

for _ in e.iter_vars('mrisubject'):
    meg_ds = e.load_events()
    
    pos_super = kit.split_label(mne.read_label(os.path.join(
                meg_ds.info['labeldir'], 'lh.superiortemporal.label')), 
                meg_ds.info['fwd'])[0]
    pos_mid = kit.split_label(mne.read_label(os.path.join(
                meg_ds.info['labeldir'], 'lh.middletemporal.label')), 
                meg_ds.info['fwd'])[0]
    pos_inf = kit.split_label(mne.read_label(os.path.join(
                meg_ds.info['labeldir'], 'lh.inferiortemporal.label')), 
                meg_ds.info['fwd'])[0]
    LPTL = pos_super + pos_mid + pos_inf

    mne.write_label(os.path.join(meg_ds.info['labeldir'], 'lh.LPTL.label'), LPTL)
