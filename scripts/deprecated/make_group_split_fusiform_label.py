'''
Created on Nov 7, 2012

@author: teon
'''

import eelbrain.utils.kit as kit
import basic.process as process
import os
import mne

e = process.NMG()
e.set(raw='hp1_lp40')
for _ in e.iter_vars(['subject']):
    label = mne.read_label(os.path.join(e.get('label_sdir'),
                                        'lh.fusiform.label'))
    ant_fusiform = kit.split_label(label=label,
                source_space=e.get('src'),
                axis=1, pieces=2)[1]
    post_fusiform = kit.split_label(label=label,
                source_space=e.get('src'),
                axis=1, pieces=2)[0]

    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.ant_fusiform.label'),
                    ant_fusiform)
    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.post_fusiform.label'),
                    post_fusiform)
