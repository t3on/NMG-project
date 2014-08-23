'''
Created on May 31, 2013

@author: teon
'''


import os
import mne
from mne.label import split_label


def make_LATL_label(e):
    ant_super = split_label(label=mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.superiortemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[1]
    ant_mid = split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.middletemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[1]
    ant_inf = split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.inferiortemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[1]
    LATL = ant_super + ant_mid + ant_inf
    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.LATL.label'), LATL)

def make_LPTL_label(e):
    post_super = split_label(label=mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.superiortemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[0]
    post_mid = split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.middletemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[0]
    post_inf = split_label(mne.read_label(os.path.join(
                e.get('label_sdir'), 'lh.inferiortemporal.label')),
                source_space=e.get('src'), axis=1, pieces=2)[0]
    LPTL = post_super + post_mid + post_inf
    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.LPTL.label'), LPTL)

def make_split_fusiform(e):
    label = mne.read_label(os.path.join(e.get('label_sdir'), 'lh.fusiform.label'))
    ant_fusiform = split_label(label=label,
                source_space=e.get('src'),
                axis=1, pieces=2)[1]
    post_fusiform = split_label(label=label,
                source_space=e.get('src'),
                axis=1, pieces=2)[0]
    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.ant_fusiform.label'),
                    ant_fusiform)
    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.post_fusiform.label'),
                    post_fusiform)

def make_vmPFC_label(e):
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
    mne.write_label(os.path.join(e.get('label_sdir'), 'lh.vmPFC.label'), lvmPFC)
    mne.write_label(os.path.join(e.get('label_sdir'), 'rh.vmPFC.label'), rvmPFC)
