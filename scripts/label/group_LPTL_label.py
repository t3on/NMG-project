import eelbrain.utils.kit as kit
import basic.process as process
import os
import mne


subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']), ('R0504', ['MEG 031']),
            ('R0414', []), ('R0547', ['MEG 002']), ('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084']),
            ('R0574', []), ('R0575', []), ('R0576', ['MEG 143'])]

for subject in subjects:
    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')

    pos_super = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'], 'lh.superiortemporal.label')), meg_ds.info['fwd'])[0]
    pos_mid = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'], 'lh.middletemporal.label')), meg_ds.info['fwd'])[0]
    pos_inf = kit.split_label(mne.read_label(os.path.join(meg_ds.info['labeldir'], 'lh.inferiortemporal.label')), meg_ds.info['fwd'])[0]
    LATL = pos_super + pos_mid + pos_inf

    mne.write_label(os.path.join(meg_ds.info['labeldir'], 'lh.LPTL.label'), LATL)
