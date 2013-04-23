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
    post_super = kit.split_label(label=mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.superiortemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[0]
    post_mid = kit.split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.middletemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[0]
    post_inf = kit.split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.inferiortemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[0]
    LPTL = post_super + post_mid + post_inf

    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.LPTL.label'), LPTL)
