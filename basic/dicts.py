'''
Created on May 30, 2013

@author: teon
'''

import os
from collections import defaultdict


t = {
    # experiment
    'experiment': 'NMG',
    'mne_bin': os.path.join('/Applications/mne/bin'),
    'root': os.path.join(os.path.expanduser('~'), 'Experiments'),
    'server': os.path.join('/Volumes', 'server', 'MORPHLAB', 'Teon'),

    # keywords
    'common_brain': 'fsaverage',
    'raw_raw': os.path.join('{raw_sdir}', '{subject}_{experiment}'),
    's_e': '{subject}_{experiment}',
    'denoise': 'calm',
    'filter': 'iir_hp1_lp40',
    'raw': '{denoise}_{filter}',
    'analysis': '',
    'orient': 'free',
    'test': '',
    'datatype': '',
    'stat': '',

    # db dirs
    'db_dir': os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments'),
    'results': os.path.join('{db_dir}', '{experiment}', 'results'),
    'plots_dir': os.path.join('{results}', '{datatype}', 'plots'),
    'stats_dir': os.path.join('{results}', '{datatype}', 'stats'),


    # basic dir
    'exp_dir': os.path.join('{root}', '{experiment}', 'data'),
    'exp_sdir': os.path.join('{exp_dir}', '{subject}'),
    'data_sdir': os.path.join('{exp_sdir}', 'data'),
    'meg_dir': os.path.join('{root}', '{experiment}', 'data'),
    'group_dir': os.path.join('{meg_dir}', 'group'),
    'server_dir': os.path.join('{server}', 'data', '{experiment}'),

    # MNE dir
    'fif_sdir': os.path.join('{exp_sdir}', 'mne'),

    # BESA dir
    'BESA_dir': os.path.join('{meg_dir}', 'BESA'),
    'BESA_sdir': os.path.join('{exp_sdir}', 'BESA'),
    'BESA_Averages': os.path.join('{BESA_dir}', 'BESA_Averages'),
    'BESA_MN': os.path.join('{BESA_dir}', 'BESA_MN'),

    # mri dir
    'mri_dir': os.path.join('{root}', 'MRI'),
    'mri_sdir': os.path.join('{mri_dir}', '{subject}'),
    'label_sdir': os.path.join('{mri_sdir}', 'label'),

    # raw folders
    'raw_sdir': os.path.join('{exp_sdir}', 'raw'),
    'eeg_sdir': os.path.join('{exp_sdir}', 'eeg'),
    'beh_sdir': os.path.join('{exp_sdir}', 'behavioral'),
    'script_dir': os.path.join('{db_dir}', '{experiment}', 'stims',
                               'transcripts'),
    'audio_sdir': os.path.join('{beh_sdir}', 'audio'),
    'log_sdir': os.path.join('{beh_sdir}', 'logs'),

    # saved data
    'ds-file': os.path.join('{data_sdir}', '{s_e}_ds.txt'),
    'bads-file': os.path.join('{data_sdir}', '{s_e}_{raw}_bads.txt'),
    'agg-file': os.path.join('{group_dir}', '{analysis}_ds.txt'),
    'data-file': os.path.join('{data_sdir}', '{s_e}_{analysis}.pickled'),
    'group-file': os.path.join('{group_dir}', 'group_{analysis}.pickled'),

    'helmet_png': os.path.join('{plots_dir}', 'coreg', '{s_e}' + '.png'),
    'analysis-file': os.path.join('{stats_dir}', '{analysis}_analysis'),
    'plot-file': os.path.join('{plots_dir}', '{analysis}_analysis.pdf'),

    # mne files
    'raw-file': os.path.join('{fif_sdir}', '{s_e}_{raw}-raw.fif'),
    'trans': os.path.join('{fif_sdir}', '{s_e}_{raw}-trans.fif'),  # mne p.196
    'fwd': os.path.join('{fif_sdir}', '{s_e}_{raw}-fwd.fif'),

    'cov': os.path.join('{fif_sdir}', '{s_e}_{raw}-cov.fif'),
    'fids': os.path.join('{mri_sdir}', 'bem', '{subject}-fiducials.fif'),
    'proj': os.path.join('{fif_sdir}', '{s_e}_proj.fif'),
    'proj_plot': os.path.join('{results}', 'visuals', 'pca', '{s_e}' +
                              '-proj.pdf'),

    # fwd model
    'bem_head': os.path.join('{mri_sdir}', 'bem', '{subject}-head.fif'),
    'bem': os.path.join('{mri_sdir}', 'bem', '{subject}-*-bem.fif'),
    'src': os.path.join('{mri_sdir}', 'bem', '{subject}-ico-4-src.fif'),

    # raw files
    'raw-sqd': os.path.join('{raw_sdir}', '{s_e}' + '_{denoise}.sqd'),
    'log-file': os.path.join('{log_sdir}', '{subject}_log.txt'),
    'stim_info': os.path.join('{db_dir}', '{experiment}',
                              'exp', 'stims', 'stims_info.mat'),
    'mrk': os.path.join('{raw_sdir}', '{s_e}_marker.txt'),
    'elp': os.path.join('{raw_sdir}', '{s_e}_elp.txt'),
    'hsp': os.path.join('{raw_sdir}', '{s_e}_hsp.txt'),
    'fsn': os.path.join('{raw_sdir}', '{subject}*.fsn'),

    # eye-tracker
    'edf_sdir': os.path.join('{beh_sdir}', 'eyelink'),
    'edf-file': os.path.join('{edf_sdir}', '*.edf'),

    # EEG
    'vhdr': os.path.join('{eeg_sdir}', '{s_e}.vhdr'),
    'eegfif': os.path.join('{fif_sdir}', '{s_e}_raw.fif'),

    # BESA raw files
    'besa_ascii': os.path.join('{BESA_sdir}', '{s_e}_{analysis}-epochs.asc'),
    'besa_cot': os.path.join('{BESA_sdir}', '{s_e}_{analysis}-epochs.cot'),
    'besa_ela': os.path.join('{BESA_sdir}', '{s_e}_{analysis}-epochs.ela'),
    'besa_pos': os.path.join('{BESA_sdir}', '{s_e}_{analysis}-epochs.pos'),
    'besa_sfp': os.path.join('{BESA_sdir}', '{s_e}_{analysis}-epochs.sfp'),
    'besa_evt': os.path.join('{BESA_sdir}', '{s_e}_{analysis}-epochs.evt'),
    'elp_legacy': os.path.join('{BESA_sdir}', '{s_e}.elp'),
    'hsp_legacy': os.path.join('{BESA_sdir}', '{s_e}.hsp'),

    # BESA files
    'besa_pdg': os.path.join('{BESA_dir}', '{experiment}.PDG'),
    'besa_cfg': os.path.join('{BESA_dir}', 'BESA_MN.cfg'),
    'besa_fsg': os.path.join('{BESA_Averages}', '{s_e}_epochs_av.fsg'),
    'besa_elv': os.path.join('{BESA_Averages}', '{s_e}_epochs_av.elv'),
    'besa_dat': os.path.join('{BESA_MN}', '{s_e}_*-*.dat'),

    # audio dir
    'textgrid': os.path.join('{data_sdir}', '*.TextGrid'),
    'sound-file': os.path.join('{data_sdir}', '*.wav'),
    }

###############################
# Experiment class attributes #
###############################

# subject to exclude
exclude = ['R0224',  # large noise artifacts
           'R0414']  # lost 3/4 of trials by accident

# color palette
cm = dict()
cm['ortho'] = 'b'
cm['transparent'] = 'g'
cm['opaque'] = 'r'
cm['novel'] = 'm'

cm['control_identity'] = cm['control_constituent'] = 'b'
cm['identity'] = cm['first_constituent'] = 'g'

cm[('control_identity', 'novel')] = cm[('control_constituent', 'novel')] = (0.137, 0.07, 0.906)
cm[('control_identity', 'transparent')] = cm[('control_constituent', 'transparent')] = (0.055, 0.25, 0.906)
cm[('control_identity', 'opaque')] = cm[('control_constituent', 'opaque')] = (0.078, 0.594, 0.906)
cm[('control_identity', 'ortho')] = cm[('control_constituent', 'ortho')] = (0.055, 0.832, 0.906)

cm[('identity', 'novel')] = cm[('first_constituent', 'novel')] = (0.906, 0.0, 0.309)
cm[('identity', 'transparent')] = cm[('first_constituent', 'transparent')] = (0.906, 0.031, 0.133)
cm[('identity', 'opaque')] = cm[('first_constituent', 'opaque')] = (0.906, 0.23, 0.035)
cm[('identity', 'ortho')] = cm[('first_constituent', 'ortho')] = (0.906, 0.453, 0.047)
