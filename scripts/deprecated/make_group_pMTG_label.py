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
    pMTG = kit.split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.middletemporal.label')),
                source_space=e.get('fwd'), axis=1, pieces=2)[0]


    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.pMTG.label'), pMTG)
