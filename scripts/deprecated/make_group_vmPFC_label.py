'''
Created on Nov 28, 2012

@author: teon
'''

import basic.process as process
import os
import mne

e = process.NMG()

for _ in e.iter_vars(['subject']):
    lmedial = mne.read_label(os.path.join(e.get('label_sdir'),
                                          'lh.lateralorbitofrontal.label'))
    llateral = mne.read_label(os.path.join(e.get('label_sdir'),
                                           'lh.medialorbitofrontal.label'))
    lvmPFC = lmedial + llateral

    rmedial = mne.read_label(os.path.join(e.get('label_sdir'),
                                          'rh.lateralorbitofrontal.label'))
    rlateral = mne.read_label(os.path.join(e.get('label_sdir'),
                                           'rh.medialorbitofrontal.label'))
    rvmPFC = rmedial + rlateral


    mne.write_label(os.path.join(e.get('label_sdir'),
                                 'lh.vmPFC.label'), lvmPFC)
    mne.write_label(os.path.join(e.get('label_sdir'),
                                 'rh.vmPFC.label'), rvmPFC)
