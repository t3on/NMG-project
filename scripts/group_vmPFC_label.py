import eelbrain.utils.kit as kit
import process
import copy
import os
import mne


subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']), ('R0504', ['MEG 031']),
            ('R0414', []), ('R0547', ['MEG 002']), ('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084']),
            ('R0574', []), ('R0575', []), ('R0576', ['MEG 143'])]

for subject in subjects:
    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')

    lmedial = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'], 'lh.lateralorbitofrontal.label')), meg_ds.info['fwd'])[1]
    llateral = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'], 'lh.medialorbitofrontal.label')), meg_ds.info['fwd'])[1]
    lvmPFC = lmedial + llateral

    rmedial = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'], 'rh.lateralorbitofrontal.label')), meg_ds.info['fwd'])[1]
    rlateral = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'], 'rh.medialorbitofrontal.label')), meg_ds.info['fwd'])[1]
    rvmPFC = rmedial + rlateral


    mne.write_label(os.path.join(meg_ds.info['labeldir'], 'lh.vmPFC.label'), lvmPFC)
    mne.write_label(os.path.join(meg_ds.info['labeldir'], 'rh.vmPFC.label'), rvmPFC)
