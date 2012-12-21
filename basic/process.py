'''
Created on Nov 25, 2012

@author: teon
'''

import os
from eelbrain import eellab as E
from eelbrain.vessels import experiment
import numpy as np
import mne
from subprocess import Popen, PIPE
from collections import defaultdict
import time

#################
#    bad chs    #
################# 
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

rois = {}
rois['lh.fusiform'] = ('lh.fusiform',)
rois['vmPFC'] = ('lh.vmPFC', 'rh.vmPFC')
rois['LATL'] = ('lh.LATL',)
rois['lh.inferiortemporal'] = ('lh.inferiortemporal',)
rois['LPTL'] = ('lh.LPTL',)
rois['cuneus'] = ('lh.cuneus', 'rh.cuneus')
rois['lh.cuneus'] = ('lh.cuneus',)

fake_mris = ['R0547', 'R0569', 'R0574', 'R0575', 'R0576', 'R0580']
exclude = ['R0338a', 'R0338b', 'R0414']
#'R0498','R0569', 'R0575', 'R0576'
class NMG(experiment.mne_experiment):
    _common_brain = 'fsaverage'
    _exp = 'NMG'
    #_experiments = ['NMG']
    _subject_loc = 'exp_dir'  # location of subject folders
    _mri_loc = 'mri_dir'

    def __init__(self, subject='{name}', subjects=[], root='~/data'):
        super(NMG, self).__init__(root=root, subjects=subjects)
#       self.bad_channels = bad_channels
        self.log = defaultdict(list)
        self.exclude['subject'] = exclude
        self.fake_mris = fake_mris
        self.rois = rois
        self.set(subject=subject)
    def get_templates(self):
        t = {

            #experiment
            'experiment': self._exp,
            'mne_bin': os.path.join('/Applications/mne/bin'),
            'exp_db': os.path.join(os.path.expanduser('~'), 'Dropbox',
                                    'Experiments'),
            'results': os.path.join('{exp_db}', 'NMG', 'results'),

            # basic dir
            'exp_dir': os.path.join('{root}', '{experiment}'), #contains subject-name folders for MEG data
            'exp_sdir': os.path.join('{exp_dir}', '{subject}'),
            'fif_sdir': os.path.join('{exp_sdir}', 'myfif'),

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
            'rawfif': os.path.join('{fif_sdir}', '{s_e}_raw.fif'), # for subp.kit2fiff
            'trans': os.path.join('{fif_sdir}', '{s_e}_raw-trans.fif'), # mne p. 196

            # fif files derivatives
            'fwd': os.path.join('{fif_sdir}', '{s_e}_raw-fwd.fif'),
            'proj': os.path.join('{fif_sdir}', '{s_e}_proj.fif'),
            'inv': os.path.join('{fif_sdir}', '{s_e}_raw-inv.fif'),
            'cov': os.path.join('{fif_sdir}', '{s_e}_raw-cov.fif'),
            'proj_plot': os.path.join('{results}', 'meg', 'plots', '{s_e}' +
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
            'elp': os.path.join('{param_sdir}', '{s_e}.elp'),
            'hsp': os.path.join('{param_sdir}', '{s_e}.hsp'),
            'sns': os.path.join('{exp_db}', 'tools', 'parameters', 'sns.txt'),

            # raw files
            'raw_raw': os.path.join('{raw_sdir}', '{subject}_{experiment}'), # legacy. looks in the fif folder for file pattern
            's_e': '{subject}_{experiment}',
            'rawtxt': os.path.join('{meg_sdir}', '{s_e}' + '-export*.txt'),
            'logfile': os.path.join('{log_sdir}', '{subject}_log.txt'),
            'stims_info': os.path.join('{exp_dir}', 'stims', 'stims_info.txt'),
            'plot_png': os.path.join('{results}', 'visuals', 'helmet',
                                     '{name}', '{s_e}' + '_'),

            # eye-tracker
            'edf_sdir': os.path.join('{beh_sdir}', 'eyelink'),
            'edf': os.path.join('{edf_sdir}', '*.edf'),

            # EEG
            'vhdr': os.path.join('{eeg_sdir}', '{s_e}.vhdr'),
            'eegfif': os.path.join('{fif_sdir}', '{s_e}_raw.fif'),

            # BESA
            #'besa_triggers': os.path.join('{exp_sdir}', 'besa', '{s_e}_{analysis}_triggers.txt'),
            #'besa_evt': os.path.join('{exp_sdir}', 'besa', '{s_e}_{analysis}.evt'),
            }

        return t

    #################
    #    process    #
    #################

    def kit2fiff(self, aligntol=25, sfreq=500, lowpass=30, highpass=0, stimthresh=1,
                 stim=xrange(168, 160, -1), add=None, **rawfiles):
        import subprocess
        sns = self.get('sns')
        mrk = self.get('mrk')
        elp = self.get('elp')
        hsp = self.get('hsp')
        rawtxt = self.get('rawtxt')
        rawfif = self.get('rawfif')

        if 'mrk' in rawfiles:
            mrk = rawfiles['mrk']
        if 'elp' in rawfiles:
            elp = rawfiles['elp']
        if 'hsp' in rawfiles:
            hsp = rawfiles['hsp']
        if 'rawtxt' in rawfiles:
            rawtxt = rawfiles['rawtxt']
        if 'rawfif' in rawfiles:
            rawfif = rawfiles['rawfif']

        # convert the marker file  
        mrk_file = E.load.kit.marker_avg_file(mrk)
        hpi = mrk_file.path

        stim = ':'.join(map(str, stim))

        cmd = ['/Applications/mne/bin/mne_kit2fiff',
               '--elp', elp,
               '--hsp', hsp,
               '--sns', sns,
               '--hpi', hpi,
               '--aligntol', aligntol,
               '--raw', rawtxt,
               '--out', rawfif,
               '--sfreq', sfreq,
               '--lowpass', lowpass,
               '--highpass', highpass,
               '--stim', stim,
               '--stimthresh', stimthresh]
        cwd = self.get('mne_bin')

        if add:
            add = ':'.join((add))
            cmd = cmd + '--add %s' % add

        cmd = [unicode(c) for c in cmd]
        sp = subprocess.Popen(cmd, cwd=cwd,
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()

        if stderr:
            print '\n> ERROR: %s\n%s' % (stderr, stdout)



    def load_events(self, subject=None, experiment=None, #load_stim_info = True,
                    remove_bad_chs=True, proj=True, edf=True, treject=25):
        """

        Loads events from the corresponding raw file, adds the raw to the info
        dict.

        proj : True | False | str
            load a projection file and add it to the raw
        edf : bool
            Loads edf and add it to the info dict.

        """
        self.set(subject=subject, experiment=experiment)
        self.logger('subject: ')
        raw_file = self.get('rawfif')
        if isinstance(proj, str):
            proj = self.get('proj', projname=proj)
        if proj:
            proj = os.path.lexists(self.get('proj'))
        ds = E.load.fiff.events(raw_file, proj=proj)

        #Add subject as a redundant variable to the dataset
        ds['subject'] = E.factor([self.get('subject')], rep=ds.N, random=True)
        ds.info['subject'] = self.get('subject')

        #For the first five subjects in NMG, the voice trigger was mistakenly overlapped with the prime triggers.
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
            bad_chs = self.bad_channels[self.state['subject']]
            raw.info['bads'].extend(bad_chs)


        self.label_events(ds)

        # add edf
        if edf:
            if os.path.lexists(self.get('edf_sdir')):
                edf = self.load_edf()
                if edf.triggers.size != ds.N:
                    self.logger('edf: dimension mismatch, eyelink disabled')
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

    def load_edf(self, match=False):
        src = self.get('edf', match=match)
        edf = E.load.eyelink.Edf(src)
        return edf

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

            if v > 128:
                exp.append(int(binary_trig[0], 2))
                target.append(int(binary_trig[1], 2))
                wtype.append(int(binary_trig[2:5], 2))
                cond.append(int(binary_trig[5:8], 2))
            else:
                exp.append(None)
                target.append(None)
                wtype.append(None)
                cond.append(None)

        #Labels events    
        ds['experiment'] = E.factor(exp, labels={None: 'fixation', 1: 'experiment'})
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
        itemID = temp['scenario'].x + (temp['wordtype'].x * 60)
        ds['itemID'] = E.var(np.repeat(itemID, 4))

        #Loads logfile and adds it to the ds
        log_ds = self._logread()
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
            e.log('ds: Dimension Mismatch. No Stimuli Info')
        #Load duration data and adds it to the dataset.
        #  ds = _load_dur_info(ds)


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
                self.logger(log='edf: %d' % rejected + r'% ' +
                            'rejected, eyelink disabled')
            else:
                self.logger(log='edf: %d' % remainder + r'% ' + 'remains')
                ds = dsx
            del ds['t_edf']
            del ds['accept']
        else:
            self.logger(log='edf: has no Eyelink data')
            ds = ds

        return ds

    def _logread(self):
        logfile = self.get('logfile')

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

        ds = E.dataset(display, latency, trigger, trigger_time)
        ds['word_length'] = E.var(map(len, ds['display']))

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

    def make_proj(self, write=True, overwrite=False, proj_object=False):
        ds = self.load_events(proj=False, edf=False)
        if write and not overwrite:
            if os.path.lexists(self.get('proj')):
                raise IOError("proj file at %r already exists"
                              % self.get('proj'))

        #add the projections to this object by using 

        ds_fix = ds[ds['experiment'] == 'fixation']
        epochs = E.load.fiff.mne_Epochs(ds_fix, tstart= -0.2, tstop=.6, baseline=(None, 0), reject={'mag':1.5e-11})
        proj = mne.proj.compute_proj_epochs(epochs, n_grad=0, n_mag=5, n_eeg=0)


        if write == True:
            first_proj = [proj[0]]
            mne.write_proj(self.get('proj'), first_proj)
            self.logger(log='proj: Projection written to file')


        pc = [proj[0]]

        if proj_object:
            return pc

    def make_cov(self, write=True, overwrite=False, cov_object=False):
        ds = self.load_events(proj=True, edf=False)
        if write and not overwrite:
            if os.path.lexists(self.get('cov')):
                raise IOError("cov file at %r already exists"
                              % self.get('cov'))

        # create covariance matrix
        index = ds['experiment'] == 'fixation'
        ds_fix = ds[index]

        epochs = E.load.fiff.mne_Epochs(ds_fix, baseline=(None, 0), reject={'mag':2e-12}, tstart= -.2, tstop=.2)
        cov = mne.cov.compute_covariance(epochs)

        if write == True:
            cov.save(self.get('cov'))
            self.logger('cov: Covariance Matrix written to file')

        if cov_object:
            return cov

    def make_fwd(self, fromfile=True, overwrite=False):
        # create the forward solution
        os.environ['SUBJECTS_DIR'] = self.get('mri_dir')

        src = self.get('src')
        trans = self.get('trans')
        bem = self.get('bem')
        fwd = self.get('fwd')
        rawfif = self.get('rawfif')
        mri_subject = self.get('mrisubject')
        cwd = self.get('mne_bin')

        cmd = ['mne_do_forward_solution',
           '--subject', mri_subject,
           '--src', src,
           '--bem', bem,
           '--mri', trans, # MRI description file containing the MEG/MRI coordinate transformation.
           '--meas', rawfif, # provides sensor locations and coordinate transformation between the MEG device coordinates and MEG head-based coordinates.
           '--fwd', fwd, #'--destdir', target_file_dir, # optional 
           '--megonly']

        if overwrite:
            cmd.append('--overwrite')
        elif os.path.exists(fwd):
            raise IOError("fwd file at %r already exists" % fwd)

        sp = Popen(cmd, cwd=cwd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = sp.communicate()

        if stderr:
            print '\n> ERROR:'
            print stderr

        if os.path.exists(fwd):
            self.logger(log='fwd: Forward Solution written to file')
            return fwd

        else:
            err = "fwd-file not created"
            err = os.linesep.join([err, "command out:", stdout])
            raise RuntimeError(err)

    def make_stcs(self, ds, labels=None, force_fixed=True,
                    stc_object=False, stc_type='epochs', lambda2=1. / 9):

        """Creates an stc object of transformed data from the ds

            Parameters
            ----------
            ds: dataset
                data
            labels: list of tuples
                a list of ROIs
            force_fixed: bool
                True = Fixed orientation, False = Free orientation
            stc_object: bool
                True = mne.object, False = eelbrain.ndvar
            stc_type: str
                'epochs'
                'evoked'

        """
        rois = None
        cov = mne.read_cov(self.get('cov'))
        #there is currently no solution for creating the fwd as an object.
        fwd = mne.read_forward_solution(self.get('fwd'), force_fixed=force_fixed)
        inv = mne.minimum_norm.make_inverse_operator(info=ds['epochs'].info,
                                                    forward=fwd, noise_cov=cov,
                                                    loose=None, verbose=False)

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

        #makes stc epochs or evoked

        if stc_type == 'epochs':
        #a list of stcs within label per epoch.
            stcs = mne.minimum_norm.apply_inverse_epochs(ds['epochs'], inv,
                                                         label=rois,
                                                         lambda2=lambda2,
                                                         verbose=False)

        elif stc_type == 'evoked':
            evoked = ds['epochs'].average()
            stcs = mne.minimum_norm.apply_inverse(evoked, inv,
                                                  lambda2=lambda2,
                                                  verbose=False)
        else:
            error = 'Currently only implemented for epochs and evoked'
            self.logger('stc: %s' % error)
            raise TypeError(error)
        #makes stc object or ndvar
        if not stc_object:
            stcs = E.load.fiff.stc_ndvar(stcs, subject=self.get('mrisubject'))

        return stcs

    def logger(self, log, verbose=True):
        """
        A simple logger for actions done in an experiment session.

        Parameters
        ----------

        log: str
            log entry. takes the syntax, key: message
            e.g. edf: 98% of trials remain

        """

        entry = log.split(':', 1)
        log = '%s: %s: %s' % (entry[0], self.get('subject'), entry[1])
        self.log[entry[0]].append(log)
        if verbose:
            print log

    def print_log(self, dest):
        dest, ext = os.path.splitext(dest)
        date = time.localtime()
        date = '-%d.%d.%d' % (date[1], date[2], date[0])
        if ext:
            dest = dest + date + ext
        else:
            dest = dest + date + '.txt'
        with open(dest, 'w') as FILE:
            for key in self.log.keys():
                for comment in self.log[key]:
                    FILE.write('%s: %s' % (key, comment) + os.linesep)


