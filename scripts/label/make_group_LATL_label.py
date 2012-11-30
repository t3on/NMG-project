'''
Created on Nov 7, 2012

@author: teon
'''

import eelbrain.utils.kit as kit
import basic.process as process
import os
import mne

e = process.NMG()

for _ in e.iter_vars('mrisubject'):
    meg_ds = e.load_events()

    ant_super = kit.split_label(mne.read_label(os.path.join
                (meg_ds.info['labeldir'], 'lh.superiortemporal.label')), 
                meg_ds.info['fwd'])[1]
    ant_mid = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'],
                'lh.middletemporal.label')), meg_ds.info['fwd'])[1]
    ant_inf = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'],
                'lh.inferiortemporal.label')), meg_ds.info['fwd'])[1]
    pole = mne.read_label(os.path.join(meg_ds.info['labeldir'],
                                       'lh.temporalpole.label'))
    LATL = ant_super + ant_mid + ant_inf + pole

    mne.write_label(os.path.join(meg_ds.info['labeldir'], 'lh.LATL.label'), LATL)
