'''
Created on Nov 25, 2012

@author: teon
'''

import os
import logging
from subprocess import Popen, PIPE
from collections import defaultdict
import numpy as np
import mne
import mne.fiff.kit as kit
from eelbrain import eellab as E
from eelbrain.vessels import experiment

rois = {}
rois['vmPFC'] = ['lh.vmPFC', 'rh.vmPFC']
rois['cuneus'] = ['lh.cuneus', 'rh.cuneus']

fake_mris = ['R0547', 'R0569', 'R0574', 'R0575', 'R0576', 'R0580']
#exclude = ['R0224', 'R0338a', 'R0338b', 'R0414', 'R0576', 'R0580']
#'R0498','R0569', 'R0575', 'R0576'
class NMG(experiment.mne_experiment):
    _common_brain = 'fsaverage'
    _exp = 'NMG'
    _experiments = ['NMG']

    def __init__(self, subject='{name}', subjects=[], root='~/data'):
        super(NMG, self).__init__(root=root, subjects=subjects)
        self.bad_channels = bad_channels
        self.logger = logging.getLogger('mne')
#        self.exclude['subject'] = exclude
        self.fake_mris = fake_mris
        self.rois = rois
        self.set(subject=subject)
    def get_templates(self):
        t = {

            #experiment
            'experiment': self._experiments[0],
            'mne_bin': os.path.join('/Applications/mne/bin'),
            'exp_db': os.path.join(os.path.expanduser('~'), 'Dropbox',
                                    'Experiments'),
            'results': os.path.join('{exp_db}', 'NMG', 'results'),

            # basic dir
            'exp_dir': os.path.join('{root}', '{experiment}'), #contains subject-name folders for MEG data
            'exp_sdir': os.path.join('{exp_dir}', '{subject}'),
            'fif_sdir': os.path.join('{exp_sdir}', 'myfif'),
            'meg_dir': os.path.join('{root}', '{experiment}'),

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
            'log_sdir': os.path.join('{beh_sdir}', 'logs'),

            # fif files
            'raw': 'raw',
            'raw-base': os.path.join('{fif_sdir}', '{subject}_{experiment}_{raw}'),
            'raw-file': '{raw-base}-raw.fif',
            'trans': os.path.join('{fif_sdir}', '{s_e}_raw-trans.fif'), # mne p. 196

            # fif files derivatives
            'fids': os.path.join('{mri_sdir}', 'bem', '{subject}-fiducials.fif'),
            'fwd': os.path.join('{fif_sdir}', '{s_e}_raw-fwd.fif'),
            'proj': os.path.join('{fif_sdir}', '{s_e}_proj.fif'),
            'inv': os.path.join('{fif_sdir}', '{s_e}_raw-inv.fif'),
            'cov': os.path.join('{fif_sdir}', '{s_e}_{raw}-cov.fif'),
            'proj_plot': os.path.join('{results}', 'visuals', 'pca', '{s_e}' +
                                      '-proj.pdf'),

            # fwd model
            'bem': os.path.join('{mri_sdir}', 'bem',
                                '{mrisubject}-5120-bem-sol.fif'),
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
            # legacy. looks in the fif folder for file pattern
            'raw_raw': os.path.join('{raw_sdir}', '{subject}_{experiment}'),
            's_e': '{subject}_{experiment}',
            'rawtxt': os.path.join('{meg_sdir}', '{s_e}' + '-export*.txt'), #to be deprecated
            'raw-sqd': os.path.join('{meg_sdir}', '{s_e}' + '_calm.sqd'),
            'logfile': os.path.join('{log_sdir}', '{subject}_log.txt'),
            'stims_info': os.path.join('{exp_db}', 'NMG', 'stims', 'stims_info.txt'),
            'plot_png': os.path.join('{results}', 'visuals', 'helmet',
                                     '{name}', '{s_e}' + '_'),
             'analysis': '',

            # eye-tracker
            'edf_sdir': os.path.join('{beh_sdir}', 'eyelink'),
            'edf': os.path.join('{edf_sdir}', '*.edf'),

            # EEG
            'vhdr': os.path.join('{eeg_sdir}', '{s_e}.vhdr'),
            'eegfif': os.path.join('{fif_sdir}', '{s_e}_raw.fif'),

            }

        return t

    #################
    #    process    #
    #################

    def kit2fiff(self, stim='<', mne_raw=False, verbose=False, stimthresh=3.5,
                 overwrite=False, **rawfiles):
        self.set(raw='raw')
        sns = self.get('sns')
        mrk = self.get('mrk')
        elp = self.get('elp')
        hsp = self.get('hsp')
        rawsqd = self.get('raw-sqd')
        rawfif = self.get('raw-file')
        stim = stim
        stimthresh = stimthresh

        if 'mrk' in rawfiles:
            mrk = rawfiles['mrk']
        if 'elp' in rawfiles:
            elp = rawfiles['elp']
        if 'hsp' in rawfiles:
            hsp = rawfiles['hsp']
        if 'raw-sqd' in rawfiles:
            rawsqd = rawfiles['raw-sqd']
        if 'raw-file' in rawfiles:
            rawfif = rawfiles['raw-file']

        if not os.path.lexists(rawfif) or not mne_raw or not overwrite:
            raw = kit.read_raw_kit(input_fname=rawsqd, mrk=mrk,
                               elp=elp, hsp=hsp, sns_fname=sns,
                               stim=stim, verbose=verbose)
            if mne_raw:
                return raw
            else:
                raw.save(rawfif, overwrite=overwrite)
                del raw


    def do_raw(self, lp=40, hp=1, redo=False, n_jobs=3):
        """
        Parameters
        ----------
        lp : int
            Lowpass filter.
        hp : int
            Highpass filter.

        Returns
        -------
        raw : fif-file
            New fif-file with filter settings named with template.
        """
        self.reset()
        raw = 'lp-%dhp-%d' % (lp, hp)
        self.make_filter(raw, hp=hp, lp=lp, n_jobs=n_jobs, src='raw',
                             redo=redo)
        self.reset()

    def make_fiducials(self):
        mne.gui.fiducials(self.get('subject'),
                          subjects_dir=self.get('mri_dir'),
                          fid_file=self.get('fids'))

    def make_coreg(self):
        mne.gui.coregistration(raw=self.get('raw-file'),
                               trans_fname=self.get('trans'),
                               subjects_dir=self.get('mri_dir'))

    def load_events(self, subject=None, experiment=None,
                    remove_bad_chs=True, proj=False, edf=True, treject=25):
        """

        Loads events from the corresponding raw file, adds the raw to the info
        dict.

        proj : True | False | str
            load a projection file and add it to the raw
        edf : bool
            Loads edf and add it to the info dict.

        """
        self.set(subject=subject, experiment=experiment)
        self.logger.info('subject: %s' % self.get('subject'))
        raw_file = self.get('raw-file')
        if isinstance(proj, str):
            proj = self.get('proj', projname=proj)
        if proj:
            proj = os.path.lexists(self.get('proj'))
        ds = E.load.fiff.events(raw_file, proj=proj)

        #Add subject as a dummy variable to the dataset
        ds['subject'] = E.factor([self.get('subject')], rep=ds.N, random=True)
        ds.info['subject'] = self.get('subject')

        #For the first five subjects in NMG, the voice trigger was mistakenly 
        #overlapped with the prime triggers.
        #Repairs voice trigger value problem, if needed.
        index = range(3, ds.N, 4)
        if all(ds['eventID'][index].x > 128):
            ds['eventID'][index] = ds['eventID'][index] - 128

        #Propagates itemID for all trigger events
        #Since the fixation cross and the voice trigger is the same value, we only need to propagate it by factor of 2.
        index = ds['eventID'] < 64
        scenario = map(int, ds['eventID'][index])
        ds['scenario'] = E.var(np.repeat(scenario, 2))

        raw = ds.info['raw']
        if remove_bad_chs:
            bad_chs = self.bad_channels[self.get('subject')]
            raw.info['bads'].extend(bad_chs)

        self.label_events(ds)

        # add edf
        if edf:
            if os.path.lexists(self.get('edf_sdir')):
                edf = self.load_edf()
                if edf.triggers.size != ds.N:
                    self.logger.info('edf: dimension mismatch, eyelink disabled')
                #For the first five subjects in NMG, the voice trigger was mistakenly overlapped with the prime triggers.
                #Repairs voice trigger value problem, if needed.
                else:
                    index = range(3, edf.triggers.size, 4)
                    for trial, idx in zip(edf.triggers[index], index):
                        a = trial[0]
                        b = trial[1] - 128 if trial[1] > 128 else trial[1]
                        edf.triggers[idx] = (a, b)

                    edf.add_T_to(ds)
                    ds.info['edf'] = edf
                ds = self._reject_blinks(ds, treject=treject)
        return ds


    def label_events(self, ds):

        #Initialize lists    
        eventID_bin = []
        exp = []
        target = []
        cond = []
        wtype = []

        #Decomposes the trigger
        for v in ds['eventID']:
            binary_trig = bin(int(v))[2:]
            eventID_bin.append(binary_trig)

            exp_mask = 2 ** 7; exp_bit = 7
            target_mask = 2 ** 6; target_bit = 6
            wtype_mask = 2 ** 5 + 2 ** 4 + 2 ** 3; wtype_bit = 3
            cond_mask = 2 ** 2 + 2 ** 1 + 2 ** 0; cond_bit = 0

            if (v & exp_mask) >> exp_bit:
                exp.append((v & exp_mask) >> exp_bit)
                target.append((v & target_mask) >> target_bit)
                wtype.append((v & wtype_mask) >> wtype_bit)
                cond.append((v & cond_mask) >> cond_bit)
            else:
                exp.append(None)
                target.append(None)
                wtype.append(None)
                cond.append(None)

        #Labels events    
        ds['experiment'] = E.factor(exp, labels={None: 'fixation',
                                                 1: 'experiment'})
        ds['target'] = E.factor(target, labels={None: 'fixation/voice',
                                                0: 'prime', 1: 'target'})
        ds['wordtype'] = E.factor(wtype, labels={None: 'None', 1: 'transparent',
                                                 2: 'opaque', 3: 'novel',
                                                 4: 'ortho-1', 5:'ortho-2'})
        ds['condition'] = E.factor(cond, labels={None: 'None', 1: 'control_identity',
                                                 2: 'identity', 3: 'control_constituent',
                                                 4: 'first_constituent'})
        ds['eventID_bin'] = E.factor(eventID_bin, 'eventID_bin')

        #Makes a temporary ds
        temp = ds[ds['target'] == 'target']
        #Add itemID to uniquely identify each word
        #There are sixty words in each of the four condition 
        itemID = temp['scenario'].x + (temp['wordtype'].x * 60)
        ds['itemID'] = E.var(np.repeat(itemID, 4))

        #Loads logfile and adds it to the ds
        log_ds = logread(self.get('logfile'))
        ds.update(log_ds)

        #Labels the voice events
        #Since python's indexing start at 0 the voice trigger is the fourth event in the trial, the following index is created.
        index = np.arange(3, ds.N, 4)
        ds['experiment'][index] = 'voice'
        #Add block to the ds. 4 events per trial, 240 trials per block
        ds['block'] = E.var(np.repeat(xrange(ds.N / 960), repeats=960,
                                      axis=None))

        #Loads the stim info from txt file and adds it to the ds
        stim_ds = self._load_stim_info(ds)
        try:
            ds.update(stim_ds)
            idx = ds['wordtype'].isany('ortho-1', 'ortho-2')
            ds['wordtype'][idx] = 'ortho'
        except ValueError:
            self.logger.info('ds: Dimension Mismatch. No Stimuli Info')
        return ds


    def _reject_blinks(self, ds, treject=25):

        if 't_edf' in ds:
            ds.info['edf'].mark(ds, tstart= -0.2, tstop=0.4,
                                good=None, bad=False, use=['EBLINK'],
                                T='t_edf', target='accept')
            dsx = ds.subset('accept')
            rejected = (ds.N - dsx.N) * 100 / ds.N
            remainder = dsx.N * 100 / ds.N
            if rejected > treject:
                self.logger.info('edf: %d' % rejected + r'% ' +
                                 'rejected, eyelink disabled')
            else:
                self.logger.info('edf: %d' % remainder + r'% ' + 'remains')
                ds = dsx
            del ds['t_edf']
            del ds['accept']
        else:
            self.logger.info('edf: has no Eyelink data')
            ds = ds

        return ds


    def _load_stim_info(self, ds):
        stims = self.get('stims_info')
        stim_ds = E.load.txt.tsv(stims)

        temp = ds[ds['target'] == 'target']
        idx = []
        for (scenario, wordtype) in zip(temp['scenario'], temp['wordtype']):
            a = scenario == stim_ds['scenario']
            b = wordtype == stim_ds['wordtype']
            idx.append(np.where(a * b)[0][0])

        stim_ds = stim_ds[idx].repeat(4)
        return stim_ds

    ################
    #    source    #
    ################

    def make_proj(self, write=True, overwrite=False, nprojs=1, verbose=False):
        ds = self.load_events(proj=False, edf=False, remove_bad_chs=False)
        if write and not overwrite:
            if os.path.lexists(self.get('proj')):
                raise IOError("proj file at %r already exists"
                              % self.get('proj'))

        #add the projections to this object by using 

        ds_fix = ds[ds['experiment'] == 'fixation']
        epochs = E.load.fiff.mne_Epochs(ds_fix, tstart= -0.2, tstop=.6,
                                        baseline=(None, 0), reject={'mag':1.5e-11})
        proj = mne.proj.compute_proj_epochs(epochs, n_grad=0, n_mag=nprojs,
                                            n_eeg=0, verbose=verbose)
        proj = [proj[:nprojs]]

        if write == True:
            mne.write_proj(self.get('proj'), proj)
            self.logger.info('proj: Projection written to file')
        else:
            return proj

    def make_cov(self, write=True, overwrite=False, remove_bad_chs=False,
                 verbose=False):
        ds = self.load_events(proj=False, edf=False, remove_bad_chs=remove_bad_chs)
        if write and not overwrite:
            if os.path.lexists(self.get('cov')):
                raise IOError("cov file at %r already exists"
                              % self.get('cov'))

        # create covariance matrix
        index = ds['experiment'] == 'fixation'
        ds_fix = ds[index]

        epochs = E.load.fiff.mne_Epochs(ds_fix, baseline=(None, 0),
                                        reject={'mag':2e-12}, tstart= -.2,
                                        tstop=.2, verbose=verbose)
        cov = mne.cov.compute_covariance(epochs, verbose=verbose)

        if write == True:
            cov.save(self.get('cov'))
            self.logger.info('cov: Covariance Matrix written to file')
        else:
            return cov


    def make_fwd(self, fromfile=True, overwrite=False):
        # create the forward solution
        os.environ['SUBJECTS_DIR'] = self.get('mri_dir')

        src = self.get('src')
        trans = self.get('trans')
        bem = self.get('bem')
        fwd = self.get('fwd')
        rawfif = self.get('raw-file')
        mri_subject = self.get('mrisubject')
        cwd = self.get('mne_bin')

        cmd = ['mne_do_forward_solution',
           '--subject', mri_subject,
           '--src', src,
           '--bem', bem,
           '--mri', trans, # head-MRI coordinate transformation.
           '--meas', rawfif, # provides sensor locations
           '--fwd', fwd, #'--destdir', target_file_dir, # optional 
           '--megonly']

        if overwrite:
            cmd.append('--overwrite')
        elif os.path.exists(fwd):
            raise IOError("fwd file at %r already exists" % fwd)

        sp = Popen(cmd, cwd=cwd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = sp.communicate()

        if stderr:
            print stderr

        if os.path.exists(fwd):
            self.logger.info('fwd: Forward Solution written to file')
            return fwd
        else:
            print '\n> ERROR:'
            err = "fwd-file not created"
            err = os.linesep.join([err, "command out:", stdout])
            raise RuntimeError(err)


    def make_stcs(self, ds, labels=None, force_fixed=True,
                    mne_stc=False, stc_type='epochs', lambda2=1. / 9,
                    verbose=False):

        """Creates an stc object of transformed data from the ds

        Parameters
        ----------
        ds: dataset
            data
        labels: list of tuples
            a list of ROIs
        force_fixed: bool
            True = Fixed orientation, False = Free orientation
        mne_stc: bool
            True = mne.object, False = eelbrain.ndvar
        stc_type: str
            'epochs'
            'evoked'
        """
        cov = mne.read_cov(self.get('cov'))
        #there is currently no solution for creating the fwd as an object directly.
        fwd = mne.read_forward_solution(self.get('fwd'), force_fixed=force_fixed,
                                        verbose=verbose)
        inv = mne.minimum_norm.make_inverse_operator(info=ds['epochs'].info,
                                                     depth=None,
                                                     forward=fwd, noise_cov=cov,
                                                     loose=None, verbose=verbose)

        #for ROI analyses
        if labels:
            rois = []
            for label in labels:
                rois.append(mne.read_label(os.path.join(self.get('label_sdir'),
                                                        label + '.label')))

            if len(rois) > 1:
                roi = rois.pop(0)
                rois = sum(rois, roi)
            elif len(rois) == 1:
                rois = rois[0]
        else:
            rois = None

        #makes stc epochs or evoked
        if stc_type == 'epochs':
        #a list of stcs within label per epoch.
            stcs = mne.minimum_norm.apply_inverse_epochs(ds['epochs'], inv,
                                                         label=rois,
                                                         lambda2=lambda2,
                                                         verbose=verbose)
        elif stc_type == 'evoked':
            evoked = ds['epochs'].average()
            stcs = mne.minimum_norm.apply_inverse(evoked, inv,
                                                  lambda2=lambda2,
                                                  verbose=verbose)
        else:
            error = 'Currently only implemented for epochs and evoked'
            self.logger.info('stc: %s' % error)
            raise TypeError(error)

        #makes stc object or ndvar
        if not mne_stc:
            stcs = E.load.fiff.stc_ndvar(stcs, subject=self.get('mrisubject'))

        return stcs


def logread(logfile):

#Initializes list
    displays = []
    triggers = []
    trigger_times = []

#Reads the logfile and searches for the triggers
    for line in open(logfile):
        if line.startswith('TRIGGER\tUSBBox'):
            items = line.split()
            triggers.append(int(items[2]))
            trigger_times.append(float(items[3]))
        if line.startswith('STIM'):
            items = line.split('\t')
            if any('practice' in item for item in items):
                continue
            elif any('The end.' in item for item in items):
                continue
            elif any('Saving Data...' in item for item in items):
                continue
            elif any('Text' in item for item in items):
                displays.append(items[2])
            elif any('Response_Catcher' in item for item in items):
                displays.append(items[2])

    times = np.array(trigger_times)
    times = np.diff(times)
    latencies = times[2::4]

    latency = E.var(latencies, name='latency').repeat(4)
    latency.properties = 'Time (s)'
    trigger = E.var(triggers, name='trigger')
    trigger_time = E.var(trigger_times, name='trigger_time')
    display = E.factor(displays, name='display')

    ds = E.dataset(display, trigger, latency, trigger_time)
    ds['word_length'] = E.var(map(len, ds['display']))

    return ds



# bad chs
bad_channels = defaultdict(lambda: ['MEG 065'])
bad_channels['R0095'].extend(['MEG 151'])
bad_channels['R0224'].extend(['MEG 030', 'MEG 031', 'MEG 064',
                              'MEG 138'])
bad_channels['R0498'].extend(['MEG 066'])
bad_channels['R0504'].extend(['MEG 030', 'MEG 031', 'MEG 138'])
bad_channels['R0569'].extend(['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084'])
bad_channels['R0576'].extend(['MEG 143'])
bad_channels['R0580'].extend(['MEG 001', 'MEG 084', 'MEG 143',
                              'MEG 160', 'MEG161'])

