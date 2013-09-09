'''
Created on Nov 25, 2012

@author: teon

Collection of functions used on an experiment class.
'''

import re
import os
import logging
from glob import glob
from subprocess import Popen, PIPE
import cPickle as pickle
import numpy as np
from numpy import hstack as nphs
import scipy.io as sio
import mne
import mne.fiff.kit as KIT
from eelbrain import eellab as E
from eelbrain.experiment import FileTree
from pyphon import pyphon as pyp
import dicts
import custom_labels



class NMG(FileTree):
    _subject_loc = '{meg_dir}'
    _templates = _defaults = dicts.t
    exclude = dicts.exclude
    def __init__(self, subject=None,
                 root=dicts.t['root'], **kwargs):
        super(NMG, self).__init__(root=root, subject=subject, **kwargs)
        self.bad_channels = dicts.bad_channels
        self.logger = logging.getLogger('mne')
        self.cm = dicts.cm

    def _register_field(self, key, values=None, default=None, set_handler=None,
                        eval_handler=None, post_set_handler=None):
        folders = os.listdir(self.get('exp_dir'))
        pat = re.compile('R[0-9]{4}')
        subjects = []
        for subject in folders:
            if re.match(pat, subject):
                subjects.append(subject)
                subjects.sort()

        return FileTree._register_field(self, 'subject', subjects)

    def __iter__(self):
        "Iterate state through subjects and yield each subject name."
        for subject in self.iter('subject'):
            if subject in self.exclude:
                continue
            else:
                yield subject

    def set(self, subject=None, **state):
        """
        Set variable values.

        Parameters
        ----------
        subject : str
            Set the `subject` value.
        add : bool
            If the template name does not exist, add a new key. If False
            (default), a non-existent key will raise a KeyError.
        other : str
            All other keywords can be used to set templates.
        """
        if subject is not None:
            state['subject'] = subject

        FileTree.set(self, **state)

    #################
    #    process    #
    #################

    def kit2fiff(self, stim='>', slope='-', mne_raw=False, verbose=False,
                 stimthresh=3.5, overwrite=False, denoise='calm', **rawfiles):
        self.set(raw=denoise, denoise=denoise)
        mrk = self.get('mrk')
        elp = self.get('elp')
        hsp = self.get('hsp')
        rawsqd = self.get('raw-sqd')
        rawfif = self.get('raw-file')

        if 'mrk' in rawfiles:
            mrk = rawfiles['mrk']
        if 'elp' in rawfiles:
            elp = rawfiles['elp']
        if 'hsp' in rawfiles:
            hsp = rawfiles['hsp']
        if 'rawsqd' in rawfiles:
            rawsqd = rawfiles['rawsqd']
        if 'rawfif' in rawfiles:
            rawfif = rawfiles['rawfif']
        fifdir = os.path.dirname(rawfif)

        if os.path.lexists(mrk) or os.path.lexists(elp) or os.path.lexists(hsp):
            mrk = elp = hsp = None

        if not os.path.lexists(rawfif) or not mne_raw or not overwrite:
            if not os.path.lexists(fifdir):
                os.mkdir(fifdir)
            raw = KIT.read_raw_kit(input_fname=rawsqd, mrk=mrk,
                                   elp=elp, hsp=hsp,
                                   stim=stim, slope=slope, verbose=verbose)
            if mne_raw:
                return raw
            else:
                raw.save(rawfif, overwrite=overwrite)
                del raw
        self.reset()


    def make_bpf_raw(self, hp=1, lp=40, redo=False, n_jobs=2, **kwargs):
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
#         self.reset()
        if isinstance(hp, int) and isinstance(lp, int):
            raw = 'hp%d_lp%d' % (hp, lp)
        elif isinstance(hp, float) and isinstance(lp, int):
            raw = 'hp%.1f_lp%d' % (hp, lp)
        elif isinstance(hp, int) and isinstance(lp, float):
            raw = 'hp%d_lp%.1f' % (hp, lp)
        elif isinstance(hp, float) and isinstance(lp, float):
            raw = 'hp%.1f_lp%.1f' % (hp, lp)
        else:
            TypeError('Must be int or float')

        src_file = self.get('raw-file', raw='calm')
        dest_file = self.get('raw-file', raw=raw)
        if (not redo) and os.path.exists(dest_file):
            return

        raw = mne.fiff.Raw(src_file, preload=True)
        raw.filter(hp, lp, n_jobs=n_jobs, **kwargs)
        raw.verbose = False
        raw.save(dest_file, overwrite=True)

#         self.reset()

    def make_fiducials(self):
        mne.gui.fiducials(self.get('subject'),
                          subjects_dir=self.get('mri_dir'),
                          fid_file=self.get('fids'))

    def make_coreg(self):
        mne.gui.coregistration(raw=self.get('raw-file'),
                               trans_fname=self.get('trans'),
                               subjects_dir=self.get('mri_dir'))

    def load_events(self, subject=None, redo=False, remove_bad_chs=True,
                    proj=False, edf=True, treject=25):
        """

        Loads events from the corresponding raw file, adds the raw to the info
        dict.

        proj : True | False | str
            load a projection file and add it to the raw
        edf : bool
            Loads edf and add it to the info dict.

        """
        edf_path = self.get('edf_sdir')
        if subject:
            self.set(subject=subject)

        if redo or not os.path.lexists(self.get('ds-file')):
            self.logger.info('subject: %s' % self.get('subject'))
            raw_file = self.get('raw-file')
            if isinstance(proj, str):
                proj = self.get('proj', projname=proj)
            if proj:
                proj = os.path.lexists(self.get('proj'))
            ds = E.load.fiff.events(raw_file, proj=proj)

            # Add subject as a dummy variable to the dataset
            ds['subject'] = E.Factor([self.get('subject')], rep=ds.n_cases, random=True)

            # Loads logfile and adds it to the ds
            log_ds = read_log(self.get('log-file'))
            ds.update(log_ds)

            self.label_events(ds)

            if edf and os.path.lexists(edf_path):
                edf_path = os.path.join(edf_path, '*.edf')
                edf = E.load.eyelink.Edf(path=edf_path)
                if edf.triggers.size != ds.n_cases:
                    self.logger.info('edf: dimension mismatch, eyelink disabled')
                # For the first five subjects in NMG, the voice trigger was mistakenly overlapped with the prime triggers.
                # Repairs voice trigger value problem, if needed.
                else:
                    index = range(3, edf.triggers.size, 4)
                    for trial, idx in zip(edf.triggers[index], index):
                        a = trial[0]
                        b = trial[1] - 128 if trial[1] > 128 else trial[1]
                        edf.triggers[idx] = (a, b)

                    try:
                        edf.add_T_to(ds)
                        edf.mark(ds, tstart= -0.2, tstop=0.4, good=None, bad=False,
                                 use=['EBLINK'], T='t_edf', target='accept')
                    except ValueError:
                        edf = False
                        pass

            ds.save_txt(self.get('ds-file'))

        else:
            ds = E.load.txt.tsv(self.get('ds-file'))
            ds['subject'].random = True

        ds.info['subject'] = self.get('subject')
        try:
            ds.info['raw'] = raw = mne.fiff.Raw(self.get('raw-file'), verbose=False)
            if remove_bad_chs:
                bad_chs = self.bad_channels[self.get('subject')]
                raw.info['bads'].extend(bad_chs)
            else:
                self.bad_channels = {}
                raw.info['bads'] = []
        except IOError:
            print 'No Raw fif found. Loading dataset without raw...'
            pass

        # add edf
        if edf and os.path.lexists(edf_path):
            ds = self._reject_blinks(ds, treject=treject)
        if 't_edf' in ds:
            del ds['t_edf']
        if 'accept' in ds:
            del ds['accept']
        return ds

    def _reject_blinks(self, ds, treject=25):
        if 'accept' in ds:
            ds['accept'] = E.Var(np.array(ds['accept'].x, bool))
            dsx = ds.subset('accept')
            rejected = (ds.n_cases - dsx.n_cases) * 100 / ds.n_cases
            remainder = dsx.n_cases * 100 / ds.n_cases
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

    def label_events(self, ds):

        # Initialize lists
        eventID_bin = []
        exp = []
        target = []
        cond = []
        wtype = []

        if not 'eventID' in ds:
            ds['eventID'] = ds['trigger']

        # For the first five subjects in NMG, the voice trigger was mistakenly
        # overlapped with the prime triggers.
        # Repairs voice trigger value problem, if needed.
        index = range(3, ds.n_cases, 4)
        if all(ds['eventID'][index].x > 128):
            ds['eventID'][index] = ds['eventID'][index] - 128

        # Decomposes the trigger
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

        # Labels events
        ds['experiment'] = E.Factor(exp, labels={None: 'fixation',
                                                 1: 'experiment'})
        ds['target'] = E.Factor(target, labels={None: 'fixation/voice',
                                                0: 'prime', 1: 'target'})
        ds['wordtype'] = E.Factor(wtype, labels={None: 'None', 1: 'transparent',
                                                 2: 'opaque', 3: 'novel',
                                                 4: 'ortho', 5:'ortho'})
        ds['orthotype'] = E.Factor(wtype, labels={None: 'compound', 1: 'compound',
                                                 2: 'compound', 3: 'compound',
                                                 4: 'ortho-1', 5:'ortho-2'})
        ds['condition'] = E.Factor(cond, labels={None: 'None', 1: 'control_identity',
                                                 2: 'identity', 3: 'control_constituent',
                                                 4: 'first_constituent'})
        ds['eventID_bin'] = E.Factor(eventID_bin, 'eventID_bin')

        ds['opaque'] = E.Var(np.array((ds['wordtype'] == 'opaque'), float))
        ds['transparent'] = E.Var(np.array((ds['wordtype'] == 'transparent'), float))
        ds['novel'] = E.Var(np.array((ds['wordtype'] == 'novel'), float))

        # Propagates itemID for all trigger events
        # Since the fixation cross and the voice trigger is the same value, we only need to propagate it by Factor of 2.
        index = ds['eventID'] < 64
        scenario = map(int, ds['eventID'][index])
        ds['scenario'] = E.Var(np.repeat(scenario, 2))


        # Makes a temporary ds
        temp = ds[ds['target'] == 'target']
        # Add itemID to uniquely identify each word
        # There are sixty words in each of the four condition
        itemID = temp['scenario'].x + (temp['wordtype'].x * 60)
        ds['itemID'] = E.Var(np.repeat(itemID, 4))

        # Labels the voice events
        # Since python's indexing start at 0 the voice trigger is the fourth event in the trial, the following index is created.
        index = np.arange(3, ds.n_cases, 4)
        ds['experiment'][index] = 'voice'
        # Add block to the ds. 4 events per trial, 240 trials per block
        ds['block'] = E.Var(np.repeat(xrange(ds.n_cases / 960), repeats=960,
                                      axis=None))

        # Loads the stim info from txt file and adds it to the ds
        stim_ds = load_stim_info(self.get('stim_info'), ds)
        try:
            ds.update(stim_ds)
            freq = ds['word_freq'].x
            freq[np.where(freq == 0)[0]] = 1
            ds['log_freq'] = E.Var(np.log(freq))
        except ValueError:
            self.logger.info('ds: Dimension Mismatch. No Stimuli Info')
        return ds

    def push_mne_files(self, overwrite=False, **kwargs):
        if 'raw' in kwargs:
            self.set(raw=kwargs['raw'])
        self.push(dst_root=self.get('server_dir'),
                  names=['raw-file', 'trans', 'cov', 'fwd'],
                  overwrite=overwrite)

    def push_BESA_files(self,
                        names=['besa_ascii', 'besa_cot', 'besa_ela',
                               'besa_pos', 'besa_sfp', 'besa_evt'],
                        overwrite=False, **kwargs):
        if 'raw' in kwargs:
            self.set(raw=kwargs['raw'])
        self.push(dst_root=self.get('server_dir'),
                  names=names, overwrite=overwrite)

    ################
    #    source    #
    ################

    def make_proj(self, write=True, overwrite=False, nprojs=1, verbose=False):
        ds = self.load_events(proj=False, edf=False, remove_bad_chs=False)
        if write and not overwrite:
            if os.path.lexists(self.get('proj')):
                raise IOError("proj file at %r already exists"
                              % self.get('proj'))

        # add the projections to this object by using

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

        epochs = E.load.fiff.mne_Epochs(ds_fix, baseline=(-.2, 0),
                                        reject={'mag':2e-12}, tstart= -.2,
                                        tstop=0, verbose=verbose)
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
        mri_subject = self.get('subject')
        cwd = self.get('mne_bin')

        cmd = ['mne_do_forward_solution',
           '--subject', mri_subject,
           '--src', src,
           '--bem', bem,
           '--mri', trans,  # head-MRI coordinate transformation.
           '--meas', rawfif,  # provides sensor locations
           '--fwd', fwd,  # '--destdir', target_file_dir, # optional
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
        else:
            print '\n> ERROR:'
            err = "fwd-file not created"
            err = os.linesep.join([err, "command out:", stdout])
            raise RuntimeError(err)


    def make_stcs(self, ds, labels=None, stc_type='evoked', verbose=False,
                  **kwargs):

        """Creates an stc object of transformed data from the ds

        Parameters
        ----------
        ds: Dataset
            data
        labels: list of tuples
            a list of ROIs
        orient: 'fixed' | 'free'
            'fixed' = Fixed orientation, 'free' = Free orientation
        stc_type: 'epochs' | 'evoked'
        """
        cov = mne.read_cov(self.get('cov'))

        if 'orient' in kwargs:
            orient = kwargs['orient']
        else:
            orient = self.get('orient')

        if orient == 'free':
            fixed = False
        elif orient == 'fixed':
            fixed = True
        else:
            raise ValueError

        fwd = mne.read_forward_solution(self.get('fwd'), force_fixed=fixed,
                                        verbose=verbose)
        inv = mne.minimum_norm.make_inverse_operator(info=ds['epochs'].info,
                                                     depth=None, fixed=fixed,
                                                     forward=fwd, noise_cov=cov,
                                                     loose=None, verbose=verbose)
        # makes stc epochs or evoked
        if stc_type == 'epochs':
            # for ROI analyses
            rois = self.read_label(labels)
            # a list of stcs within label per epoch.
            stcs = mne.minimum_norm.apply_inverse_epochs(ds['epochs'], inv,
                                                         label=rois,
                                                         lambda2=1. / 2 ** 2,
                                                         verbose=verbose)
            return stcs
        elif stc_type == 'evoked':
            stcs = mne.minimum_norm.apply_inverse(ds['epochs'], inv,
                                                  lambda2=1. / 3 ** 2,
                                                  verbose=verbose)
            return stcs
        else:
            error = 'Currently only implemented for epochs and evoked'
            self.logger.info('stc: %s' % error)
            raise TypeError(error)

    def make_BESA_files(self, asc=False):
        tstart = -.1
        tstop = .6
        epoch = int((tstop - tstart) * 1e3)

        ds = self.load_events(remove_bad_chs=False)
        ds = ds[ds['target'] == 'prime']
        d = E.Dataset()
        d['Tms'] = E.Var(range(0, epoch * ds.n_cases, epoch))
        d['Code'] = E.Var(np.ones(ds.n_cases))
        d['TriNo'] = ds['eventID']
        d.save_txt(self.get('besa_evt'))

        if asc:
            # loads a epoch x sensor x time
            ds = E.load.fiff.add_epochs(ds, tstart=tstart, tstop=tstop)
            # makes a time x sensor x epoch
            epochs = ds['MEG'].x.T
            epochs = [epochs[:, :, i] for i in xrange(epochs.shape[2])]
            epochs = np.vstack(epochs) * 1e15
            np.savetxt(self.get('besa_ascii', mkdir=True), epochs)

    def make_custom_labels(self):
        "makes custom fs labels for subjects"
        custom_labels.make_LATL_label(self)
        custom_labels.make_LPTL_label(self)
        custom_labels.make_split_fusiform(self)
        custom_labels.make_vmPFC_label(self)

    def plot_coreg(self, redo=False):
        fname = self.get('helmet_png')
        if not redo and os.path.exists(fname):
            return

        from mayavi import mlab
        import eelbrain.data.plot.coreg as coreg

        raw = mne.fiff.Raw(self.get('raw-file'))
        p = coreg.dev_mri(raw)
        p.save_views(fname, overwrite=True)
        mlab.close()

    def read_label(self, labels):
        "label: list"
        rois = []
        if not isinstance(labels, list):
            labels = [labels]
        for label in labels:
            rois.append(mne.read_label(os.path.join(self.get('label_sdir'),
                                                    label + '.label')))

        if len(rois) > 1:
            roi = rois.pop(0)
            rois = sum(rois, roi)
        elif len(rois) == 1:
            rois = rois[0]
        return rois

    def process_evoked(self, model='condition % wordtype % target',
                       raw='hp1_lp40', e_type='evoked', tstart= -0.1,
                       tstop=0.6, reject={'mag': 3e-12}, redo=False):
        if e_type != 'evoked':
            raise ValueError('This method only works for evoked data.')
        self.set(raw=raw)
        self.set(analysis='_'.join((e_type, raw, str(tstart), str(tstop))))
        data = self.get('data-file')
        if os.path.lexists(data) and ~redo:
            print self.get('subject')
            ds = pickle.load(open(data))
        else:
            ds = self.load_events(edf=True)
            index = ds['experiment'] == 'experiment'
            ds = ds[index]

            # add epochs to the Dataset after excluding bad channels
            orig_N = ds.n_cases
            ds = E.load.fiff.add_mne_epochs(ds, tstart=tstart, tstop=tstop,
                                            reject=reject)
            remainder = ds.n_cases * 100 / orig_N
            self.logger.info('epochs: %d' % remainder + r'% ' +
                             'of trials remain')
            if remainder < 50:
                self.logger.info('subject %s is excluded due to large number '
                                 % self.get('subject') + 'of rejections')
                return
            # do compression
            ds = ds.compress(model, drop_bad=True)
            E.save.pickle(ds, self.get('data-file', mkdir=True))
        return ds

    def source_evoked(self, ds, rois=None, roilabels=None,
                      tstart= -0.1, tstop=0.6, **kwargs):

        e_type = 'evoked'

        if 'orient' in kwargs:
            orient = kwargs['orient']
        else:
            orient = self.get('orient')

        stcs = []
        for d in ds.itercases():
            stcs.append(self.make_stcs(d, orient=orient, stc_type=e_type))
        del ds['epochs']

        if rois == None:
            ds['stcs'] = stcs
            return ds
        else:
            for fs_roi, roilabel in zip(rois, roilabels):
                stc_rois = []
                for stc in stcs:
                    roi = self.read_label(fs_roi)
                    roi = stc.in_label(roi)
                    mri = self.get('subject')
                    roi = E.load.fiff.stc_ndvar(roi, subject=mri)
                    roi = roi.summary('source', name='stc')
                    roi.x -= roi.summary(time=(tstart, 0))
                    stc_rois.append(roi)
                ds[roilabel] = E.combine(stc_rois)
        return ds

    ###############
    #    audio    #
    ###############

    def load_soundfiles(self):
        from audio import load_soundfiles
        load_soundfiles(audio_sdir=self.get('audio_sdir'),
                        script_dir=self.get('script_dir'))

    def do_force_alignment(self, redo=False):
        fmatch = os.path.join(self.get('data_sdir'), '*.TextGrid')
        if len(glob(fmatch)) > 0 and not redo:
            return

        from audio import make_transcripts
        make_transcripts(audio_sdir=self.get('audio_sdir'),
                        script_dir=self.get('script_dir'),
                        data_sdir=self.get('data_sdir'),
                        name=self.get('s_e'))
        from audio import cat_soundfiles
        cat_soundfiles(audio_sdir=self.get('audio_sdir'),
                       script_dir=self.get('script_dir'),
                       data_sdir=self.get('data_sdir'),
                       name=self.get('s_e'))
        from audio import force_align
        force_align(data_sdir=self.get('data_sdir'))

    def get_word_duration(self, block=1, **kwargs):
        dataset = self.load_events(edf=False, remove_bad_chs=False, **kwargs)
        dataset = dataset[dataset['target'] == 'target']
        ds = []
        fmatch = self.format('{textgrid}')
        textgrids = glob(fmatch)
        textgrids.sort()
        for grid in textgrids[:block]:
            grid = pyp.Textgrid(grid)
            ds.append(grid.export_durs())
        ds = E.combine(ds)
        if all(ds['words'] == dataset['word'][:ds.n_cases]):
            c1_dur = np.zeros((dataset.n_cases))
            c1_dur[:ds.n_cases] = ds['c1_dur'].x
            c1_dur = E.Var(c1_dur, 'c1_dur')
            c2_dur = np.zeros((dataset.n_cases))
            c2_dur[:ds.n_cases] = ds['c2_dur'].x
            c2_dur = E.Var(c2_dur, 'c2_dur')

            dataset.update(E.Dataset(c1_dur, c2_dur))
        else:
            raise ValueError('Words do not match up.')

        return dataset

def read_log(logfile, **kwargs):

# Initializes list
    displays = []
    triggers = []
    trigger_times = []

# Reads the logfile and searches for the triggers
    for line in open(logfile):
        if (line.startswith('TRIGGER\tUSBBox') or
            line.startswith('TRIGGER\tStimTracker')):
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

    latency = E.Var(latencies, name='latency').repeat(4)
    latency.properties = 'Time (s)'
    trigger = E.Var(triggers, name='trigger')
    trigger_time = E.Var(trigger_times, name='trigger_time')
    display = E.Factor(displays, name='display')

    if 'subject' in kwargs:
        subject = E.Factor([kwargs['subject']], rep=len(latency), name='subject')
        ds = E.Dataset(subject, display, trigger, latency, trigger_time)
    else:
        ds = E.Dataset(display, trigger, latency, trigger_time)
    ds['word_length'] = E.Var(map(len, ds['display']))

    return ds

def read_stim_info(stim_info):
    stims = sio.loadmat(stim_info)['stims'].T
    stim_ds = E.Dataset()

    stim_ds['c1_rating'] = E.Var(nphs(nphs(nphs(stims[0]))))
    stim_ds['c1_sd'] = E.Var(nphs(nphs(nphs(stims[1]))))
    stim_ds['c1'] = E.Factor(nphs(nphs(stims[2])))
    stim_ds['c1_freq'] = E.Var(nphs(nphs(nphs(stims[3]))))
    stim_ds['c1_nmg'] = E.Var(nphs(nphs(nphs(stims[4]))))

    stim_ds['word'] = E.Factor(nphs(nphs(stims[5])))
    stim_ds['word_freq'] = E.Var(nphs(nphs(nphs(stims[6]))))
    stim_ds['word_nmg'] = E.Var(nphs(nphs(nphs(stims[7]))))

    stim_ds['c2_rating'] = E.Var(nphs(nphs(nphs(stims[-9]))))
    stim_ds['c2_sd'] = E.Var(nphs(nphs(nphs(stims[-8]))))
    stim_ds['c2'] = E.Factor(nphs(nphs(stims[-7])))
    stim_ds['c2_freq'] = E.Var(nphs(nphs(nphs(stims[-6]))))
    stim_ds['c2_nmg'] = E.Var(nphs(nphs(nphs(stims[-5]))))

    stim_ds['word2'] = E.Factor(nphs(nphs(stims[-4])))
    stim_ds['word2_freq'] = E.Var(nphs(nphs(nphs(stims[-3]))))
    stim_ds['word2_nmg'] = E.Var(nphs(nphs(nphs(stims[-2]))))

    idx = stim_ds['word2'] != 'NaW'
    idy = stim_ds['word'] == 'NaW'
    stim_ds['word'][stim_ds['word'] == 'NaW'] = stim_ds[idx * idy]['word2']

    idx = ~np.isnan(stim_ds['word2_freq'])
    idy = np.isnan(stim_ds['word_freq'])
    stim_ds['word_freq'][idx * idy] = stim_ds[idx * idy]['word2_freq']

    idx = ~np.isnan(stim_ds['word2_nmg'])
    idy = np.isnan(stim_ds['word_nmg'])

    stim_ds['word_nmg'][idx * idy] = stim_ds[idx * idy]['word2_nmg']
    del stim_ds['word2'], stim_ds['word2_freq'], stim_ds['word2_nmg']

    return stim_ds


def load_stim_info(stim_info, ds):
    stim_ds = read_stim_info(stim_info)

    c1 = E.Factor(stim_ds['c1'], name='word')
    freq = E.Var(stim_ds['c1_freq'], name='word_freq')
    nmg = E.Var(stim_ds['c1_nmg'], name='word_nmg')
    c1 = E.Dataset(c1, freq, nmg)

    c2 = E.Factor(stim_ds['c2'], name='word')
    freq = E.Var(stim_ds['c2_freq'], name='word_freq')
    nmg = E.Var(stim_ds['c2_nmg'], name='word_nmg')
    c2 = E.Dataset(c2, freq, nmg)

    word = stim_ds['word', 'word_freq', 'word_nmg',
                   'c1_rating', 'c1_sd', 'c1_freq',
                   'c2_rating', 'c2_sd', 'c2_freq']
    words = E.combine((c1, c2, word))
    word_dict = {word: i for i, word in enumerate(words['word'])}
    word_idx = [word_dict[word.lower()] for word in ds['display']]

    return words[word_idx]


