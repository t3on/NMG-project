'''
Created on Nov 7, 2012

@author: teon
'''

import eelbrain.utils.kit as kit
import basic.process as process
import os
import mne

e = process.NMG()

for _ in e.iter_vars(['subject']):
    ant_super = kit.split_label(label=mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.superiortemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[1]
    ant_mid = kit.split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.middletemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[1]
    ant_inf = kit.split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.inferiortemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[1]
    LATL = ant_super + ant_mid + ant_inf

    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.LATL.label'), LATL)
