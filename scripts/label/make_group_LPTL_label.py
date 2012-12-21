'''
Created on Nov 19, 2012

@author: teon
'''

import eelbrain.utils.kit as kit
import basic.process as process
import os
import mne

e = process.NMG()

for _ in e.iter_vars(['subject']):
    pos_super = kit.split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.superiortemporal.label')),
                e.get('fwd'))[0]
    pos_mid = kit.split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.middletemporal.label')),
                e.get('fwd'))[0]
    pos_inf = kit.split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.inferiortemporal.label')),
                e.get('fwd'))[0]
    LPTL = pos_super + pos_mid + pos_inf

    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.LPTL.label'), LPTL)
