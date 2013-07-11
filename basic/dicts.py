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

    # keywords
    'common_brain': 'fsaverage',
    'raw_raw': os.path.join('{raw_sdir}', '{subject}_{experiment}'),
    's_e': '{subject}_{experiment}',
    'denoise': 'calm',
    'raw': 'hp1_lp40',
    'analysis': '',
    'orient': '',
    'test': '',
    'dtype': '',
    'stat': '',

    # db dirs
    'exp_db': os.path.join(os.path.expanduser('~'), 'Dropbox',
                            'Experiments', '{experiment}'),
    'results': os.path.join('{exp_db}', 'results'),
    'plots_dir': os.path.join('{results}', '{dtype}', '{stat}',
                              '{orient}', ''),
    'stats_dir': os.path.join('{results}', '{dtype}', '{stat}',
                              '{orient}', 'stats', ''),
    'wf_dir': os.path.join('{results}', '{dtype}', '{stat}',
                           '{orient}', ''),

    # basic dir
    'exp_dir': os.path.join('{root}', '{experiment}'),
    'exp_sdir': os.path.join('{exp_dir}', '{subject}'),
    'data_sdir': os.path.join('{exp_sdir}', 'data'),
    'meg_dir': os.path.join('{root}', '{experiment}'),
    'group_dir': os.path.join('{meg_dir}', 'group'),

    # MNE dir
    'fif_sdir': os.path.join('{exp_sdir}', 'fifs'),

    # BESA dir
    'BESA_dir': os.path.join('{meg_dir}', 'BESA'),
    'BESA_sdir': os.path.join('{exp_sdir}', 'BESA', ''),
    'BESA_Averages': os.path.join('{BESA_dir}', 'BESA_Averages'),
    'BESA_MN': os.path.join('{BESA_dir}', 'BESA_MN'),
    
    # audio dir
    'script_dir': os.path.join('{exp_db}', 'stims', 'transcripts'),

    # mri dir
    'mri_dir': os.path.join('{root}', 'MRI'), # contains subject-name folders for MRI data
    'mri_sdir': os.path.join('{mri_dir}', '{mrisubject}'),
    'label_sdir': os.path.join('{mri_sdir}', 'label'),

    # raw folders
    'param_sdir': os.path.join('{exp_sdir}', 'parameters'),
    'raw_sdir': os.path.join('{exp_sdir}', 'rawdata', 'meg'),
    'meg_sdir': os.path.join('{exp_sdir}', 'rawdata', 'meg'),
    'eeg_sdir': os.path.join('{exp_sdir}', 'rawdata', 'eeg'),
    'beh_sdir': os.path.join('{exp_sdir}', 'rawdata', 'behavioral'),
    'audio_sdir': os.path.join('{beh_sdir}', 'audio'),
    'log_sdir': os.path.join('{beh_sdir}', 'logs'),

    # fif files
    'raw-base': os.path.join('{fif_sdir}', '{s_e}_{raw}'),
    'raw-file': '{raw-base}-raw.fif',
    'trans': os.path.join('{fif_sdir}', '{subject}-trans.fif'), # mne p. 196

    # saved data
    'data-file': os.path.join('{data_sdir}', '{s_e}_{analysis}.pickled'),
    'group-file': os.path.join('{group_dir}', 'group_{test}-{orient}.pydat'),

    # fif files derivatives
    'fids': os.path.join('{mri_sdir}', 'bem', '{subject}-fiducials.fif'),
    'fwd': os.path.join('{fif_sdir}', '{s_e}_{raw}-fwd.fif'),
    'proj': os.path.join('{fif_sdir}', '{s_e}_proj.fif'),
    'cov': os.path.join('{fif_sdir}', '{s_e}_{raw}-cov.fif'),
    'proj_plot': os.path.join('{results}', 'visuals', 'pca', '{s_e}' +
                              '-proj.pdf'),

    # fwd model
    # replaces 5120-bem-sol.fif
    'bem': os.path.join('{mri_sdir}', 'bem',
                        '{mrisubject}-*-bem.fif'),
    'src': os.path.join('{mri_sdir}', 'bem',
                        '{mrisubject}-ico-4-src.fif'),
    'bem_head': os.path.join('{mri_sdir}', 'bem',
                             '{mrisubject}-head.fif'),

    # parameter files
    'mrk': os.path.join('{param_sdir}', '{s_e}_marker.txt'),
    'elp': os.path.join('{param_sdir}', '{s_e}_elp.txt'),
    'hsp': os.path.join('{param_sdir}', '{s_e}_hsp.txt'),
    'sns': os.path.join('{exp_db}', 'tools', 'parameters', 'sns.txt'),

    # raw files
    'raw-sqd': os.path.join('{meg_sdir}', '{s_e}' + '_{denoise}.sqd'),
    'log-file': os.path.join('{log_sdir}', '{subject}_log.txt'),
    'stim_info': os.path.join('{exp_db}', 'stims', 'stims_info.mat'),
    'helmet_png': os.path.join('{results}', 'visuals', 'helmet',
                             '{s_e}' + '.png'),

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

    # BESA files
    'besa_pdg': os.path.join('{BESA_dir}', '{exp}.PDG'),
    'besa_cfg': os.path.join('{BESA_dir}', 'BESA_MN.cfg'),
    'besa_fsg': os.path.join('{BESA_Averages}', '{s_e}_epochs_av.fsg'),
    'besa_elv': os.path.join('{BESA_Averages}', '{s_e}_epochs_av.elv'),
    'besa_dat': os.path.join('{BESA_MN}', '{s_e}_*-*.dat'),
    }


# bad chs
bad_channels = defaultdict(lambda: [])
bad_channels['R0498'].extend(['MEG 065', 'MEG 066'])
bad_channels['R0504'].extend(['MEG 030', 'MEG 031', 'MEG 065', 'MEG 138'])
bad_channels['R0576'].extend(['MEG 065', 'MEG 143'])
bad_channels['R0580'].extend(['MEG 001', 'MEG 065', 'MEG 084', 'MEG 143',
                              'MEG 160', 'MEG161'])
bad_channels['R0605'].extend(['MEG 041', 'MEG 065', 'MEG 114'])

###############################
# Experiment class attributes #
###############################

# subject to exclude
exclude = ['R0224', # large noise artifacts 
           'R0414', # lost 3/4 of trials by accident
           'R0576', # noise issues
           'R0580', # noise issues
           'R0605'] # noise issues

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
