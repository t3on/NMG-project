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
from mne.io.kit import read_raw_kit
import eelbrain as E
from eelbrain.experiment import FileTree
from pyphon import pyphon as pyp
import dicts
from collections import defaultdict
import custom_labels



class NMG(FileTree):
    _subject_loc = '{meg_dir}'
    _templates = _defaults = dicts.t
    def __init__(self, subject=None, root=dicts.t['root'], exclude=True,
                 **kwargs):
        super(NMG, self).__init__(root=root, subject=subject, **kwargs)
        self.bad_channels = defaultdict(list)
        self.scaled_subjects = list()
        if exclude:
            self._exclude()
        self.logger = logging.getLogger('mne')
        self.old = dicts.old
        self.new = dicts.new
        self.store_state()
        os.environ['SUBJECTS_DIR'] = self.get('mri_dir')

    @property
    def subject(self):
        return self.get('subject')

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

    def _exclude(self):
        subjects = set()
        for subject in self.iter('subject', exclude=False):
            drop, bad_chs = load_bad_chs_info(self.get('bads-file'))
            if drop:
                subjects.add(subject)
            self.bad_channels[subject] = bad_chs
            if os.path.exists(self.get('scaling-file')):
                self.scaled_subjects.append(subject)
        self.exclude['subject'] = list(subjects)

    #################
    #    process    #
    #################

    def kit2fiff(self, stim='>', slope='-', mne_raw=False, verbose=False,
                 stimthresh=3, overwrite=False, denoise='calm', **rawfiles):
        self.set(raw=denoise, denoise=denoise)
        mrk = self.get('mrk', fmatch=False)
        elp = self.get('elp')
        hsp = self.get('hsp')
        rawsqd = self.get('raw-sqd')
        rawfif = self.get('raw-file')

        if 'mrk' in rawfiles:
            mrk = rawfiles['mrk']
        if 'mrk2' in rawfiles:
            mrk2 = rawfiles['mrk2']
        if 'elp' in rawfiles:
            elp = rawfiles['elp']
        if 'hsp' in rawfiles:
            hsp = rawfiles['hsp']
        if 'rawsqd' in rawfiles:
            rawsqd = rawfiles['rawsqd']
        if 'rawfif' in rawfiles:
            rawfif = rawfiles['rawfif']
        fifdir = os.path.dirname(rawfif)

        if '*' in mrk:
            mrk = glob(mrk)
            if mrk is None:
                ValueError('No markers found.')
        elif not os.path.lexists(mrk):
            raise ValueError('No marker found.')

        if not os.path.lexists(elp):
                raise ValueError('No elp file found.')
        if not os.path.lexists(hsp):
                raise ValueError('No hsp file found.')
#             mrk = elp = hsp = None

        if not os.path.lexists(rawfif) or not mne_raw or not overwrite:
            if not os.path.lexists(fifdir):
                os.mkdir(fifdir)
            raw = read_raw_kit(input_fname=rawsqd, mrk=mrk, elp=elp, hsp=hsp,
                               stim=stim, slope=slope, verbose=verbose)
            if mne_raw:
                return raw
            else:
                raw.save(rawfif, overwrite=overwrite, verbose=verbose)
                del raw

    def push_mne_files(self, overwrite=False, **kwargs):
        if 'raw' in kwargs:
            self.set(raw=kwargs['raw'])
        self.push(dst_root=self.get('server_dir'),
                  names=['raw-file', 'trans', 'cov', 'fwd'],
                  overwrite=overwrite)

    def push_BESA_files(self, overwrite=False, **kwargs):
        names = ['besa_ascii', 'besa_cot', 'besa_ela',
                 'besa_pos', 'besa_sfp', 'besa_evt']
        if 'raw' in kwargs:
            self.set(raw=kwargs['raw'])
        self.push(dst_root=self.get('server_dir'),
                  names=names, overwrite=overwrite)

    def load_events(self, subject=None, redo=False, drop_bad_chs=True,
                    proj='group_proj', edf=True, treject=25):
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
        else:
            subject = self.get('subject')
        self.logger.info('Loading Subject: %s' % subject)


        if redo or not os.path.lexists(self.get('ds-file')):
            raw_file = self.get('raw-file')
            raw = mne.io.Raw(raw_file, verbose=False)
            evts = mne.find_stim_steps(raw, merge=-1)
            idx = np.nonzero(evts[:, 2])
            evts = evts[idx]

            if len(evts) == 0:
                raise ValueError("No events found!")

            i_start = E.Var(evts[:, 0], name='i_start')
            trigger = E.Var(evts[:, 2], name='trigger')
            info = {'raw': raw}
            ds = E.Dataset(trigger, i_start, info=info)

            # Add subject as a dummy variable to the dataset
            ds['subject'] = E.Factor([subject], rep=ds.n_cases, random=True)

            # Loads logfile and adds it to the ds
            log_ds = read_log(self.get('log-file'))
            ds.update(log_ds)

            self.label_events(ds)
            ds.save_txt(self.get('ds-file'))
        else:
            ds = E.load.txt.tsv(self.get('ds-file'), delimiter='\t')
            ds['subject'].random = True

        ds.info['subject'] = subject
        try:
            raw = mne.io.Raw(self.get('raw-file'), verbose=False)
            ds.info['raw'] = raw
            if drop_bad_chs:
                ds.info['raw'].info['bads'].extend(self.bad_channels[subject])
            else:
                ds.info['raw'].info['bads'] = []
        except IOError:
            print 'No Raw fif found. Loading dataset without raw...'
            pass
        
        # add proj
        if isinstance(proj, str):
            if proj == 'group_proj':
                proj = self.get('group_proj')
            else:
                proj = self.get('proj', projname=proj)
            proj = mne.read_proj(proj)
            raw.add_proj(proj, remove_existing=True)
        elif proj is True:
            proj = mne.read_proj(self.get('proj'))
            raw.add_proj(proj, remove_existing=True)

        # add edf
        if edf and os.path.lexists(edf_path):
            ds = self._reject_blinks(ds, treject=treject)

        return ds

    def _reject_blinks(self, ds, treject=25):

        edf_path = self.get('edf-file', match=False)
        edf = E.load.eyelink.Edf(path=edf_path)

        if edf.triggers.size != ds.n_cases:
            self.logger.info('edf: dimension mismatch, '
                             'eyelink disabled')
        # For the first five subjects in NMG, the voice trigger was
        # mistakenly overlapped with the prime triggers.
        # Repairs voice trigger value problem, if needed.
        else:
            index = range(3, edf.triggers.size, 4)
            for trial, idx in zip(edf.triggers[index], index):
                a = trial[0]
                b = trial[1] - 128 if trial[1] > 128 else trial[1]
                edf.triggers[idx] = (a, b)

            try:
                edf.add_t_to(ds)
                edf.mark(ds, tstart=-0.2, tstop=0.4, good=None,
                         bad=False, use=['EBLINK'], T='t_edf',
                         target='accept')
            except ValueError:
                edf = False
                pass

        if 'accept' in ds:
            ds['accept'] = E.Var(np.array(ds['accept'].x, bool))
            dsx = ds.sub('accept')
            rejected = (ds.n_cases - dsx.n_cases) * 100 / ds.n_cases
            remainder = dsx.n_cases * 100 / ds.n_cases
            if rejected > treject:
                self.logger.info('edf: %d' % rejected + r'% ' +
                                 'rejected, eyelink disabled')
            else:
                self.logger.info('edf: %d' % remainder + r'% ' + 'remains')
                ds = dsx
            del ds['t_edf'], ds['accept']
        else:
            self.logger.info('edf: has no Eyelink data')
            ds = ds

        return ds

    def label_events(self, ds):

        # Initialize lists
        trigger_bin = []
        exp = []
        target = []
        cond = []
        wtype = []

        if not 'trigger' in ds:
            ds['trigger'] = ds['ptb_trigger']

        # For the first five subjects in NMG, the voice trigger was mistakenly
        # overlapped with the prime triggers.
        # Repairs voice trigger value problem, if needed.
        index = range(3, ds.n_cases, 4)
        if all(ds['trigger'][index].x > 128):
            ds['trigger'][index] = ds['trigger'][index] - 128

        # Decomposes the trigger
        for v in ds['trigger']:
            binary_trig = bin(int(v))[2:]
            trigger_bin.append(binary_trig)

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
        ds['trigger_bin'] = E.Factor(trigger_bin, 'trigger_bin')

        ds['opaque'] = E.Var(np.array((ds['wordtype'] == 'opaque'), float))
        ds['transparent'] = E.Var(np.array((ds['wordtype'] == 'transparent'), float))
        ds['novel'] = E.Var(np.array((ds['wordtype'] == 'novel'), float))

        # Propagates itemID for all trigger events
        # Since the fixation cross and the voice trigger is the same value, we only need to propagate it by Factor of 2.
        index = ds['trigger'] < 64
        scenario = map(int, ds['trigger'][index])
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


    def check_bad_chs(self, threshold=0.1, reject=4e-12, n_chan=5):
        """
        Check for flat-line channels or channels that repeatedly exceeded
        threshold.
        """
        ds = self.load_events(drop_bad_chs=False)
        ds = ds[ds['experiment'] == 'fixation']
        threshold = ds.n_cases * threshold
        epochs = E.load.fiff.mne_epochs(ds, tmin=-.2, tmax=.6,
                                        drop_bad_chs=False, verbose=False,
                                        baseline=(None, 0), preload=True,
                                        reject={'mag': reject})
        if epochs.drop_log:
            bads = E.Factor(sum(epochs.drop_log, []))
            bads = E.table.frequencies(bads)
            bads = bads[bads['n'] > threshold]['cell'].as_labels()
        else:
            bads = []
        picks = mne.pick_types(epochs.info, exclude=[])
        data = epochs.get_data()[:, picks, :]
        flats = []
        diffs = np.diff(data) == 0
        for epoch in diffs:
            # channels flat > 50% time period
            flats.append(np.where(np.mean(epoch, 1) >= .5)[0])
        flats = np.unique(np.hstack(flats))
        flats = ['MEG %03d' % (x + 1) for x in flats]

        bad_chs = np.unique(np.hstack((bads, flats)).ravel())
        if len(bad_chs) > n_chan:
            drop = 1
        else:
            drop = 0

        with open(self.get('bads-file'), 'w') as FILE:
            import datetime
            date = datetime.datetime.now().ctime()
            FILE.write('# Log of bad channels for %s written on %s\n\n'
                       % (self.get('subject'), date))
            FILE.write('bads=%s\n' % bad_chs)
            FILE.write('drop=%s' % drop)
        return bad_chs

    def make_bpf_raw(self, denoise='calm', hp=1, lp=40, redo=False,
                     method='fft', n_jobs=2, **kwargs):
        """
        Parameters
        ----------
        denoise : str
            Denoising method.
        lp : int
            Lowpass filter.
        hp : int
            Highpass filter.

        Returns
        -------
        raw : fif-file
            New fif-file with filter settings named with template.
        """

        self.set(raw=denoise)
        if isinstance(hp, int) and isinstance(lp, int):
            newraw = '%s_%s_hp%d_lp%d' % (denoise, method, hp, lp)
        elif isinstance(hp, float) and isinstance(lp, int):
            newraw = '%s_%s_hp%.1f_lp%d' % (denoise, method, hp, lp)
        elif isinstance(hp, int) and isinstance(lp, float):
            newraw = '%s_%s_hp%d_lp%.1f' % (denoise, method, hp, lp)
        elif isinstance(hp, float) and isinstance(lp, float):
            newraw = '%s_%s_hp%.1f_lp%.1f' % (denoise, method, hp, lp)
        else:
            TypeError('Must be int or float')

        src_file = self.get('raw-file', raw=denoise)
        dest_file = self.get('raw-file', raw=newraw)
        if (not redo) and os.path.exists(dest_file):
            return

        raw = mne.io.Raw(src_file, preload=True)
        raw.filter(hp, lp, n_jobs=n_jobs, method=method, **kwargs)
        raw.verbose = False
        raw.save(dest_file, overwrite=True, verbose=False)

    def do_ica(self):
        ds = self.load_events(edf=False)
        ds = ds[ds['experiment'] == 'experiment']
        ds = self.make_epochs(ds, reject=None, redo=True)
        picks = mne.io.pick_types(ds.info['raw'].info, meg=True, eeg=False,
                                    eog=False, stim=False, exclude='bads')
        rs = np.random.RandomState(42)
        ica = mne.preprocessing.ICA(n_components=0.90, n_pca_components=64,
                                    max_pca_components=100, noise_cov=None,
                                    random_state=rs)
        ica.decompose_epochs(ds['epochs'], decim=None, picks=picks)
        ds.info['ica'] = ica
        ica.plot_topomap(range(0, ica.n_components_), ch_type='mag');

        return ds

    def make_ica_epochs(self, ds, exclude):
        ds.info['ica'].exclude = exclude
        ds['epochs'] = ds.info['ica'].pick_sources_epochs(ds['epochs'])
        E.save.pickle(ds, self.get('ica-epochs'))
        return ds

    def make_epochs(self, ds, evoked=False, tmin=-0.2, tmax=0.6, decim=2,
                    baseline=(None, 0), reject={'mag': 3e-12},
                    model=None, redo=True, mne_obj=True, name='epochs',
                    **kwargs):

        if evoked and not model:
                raise ValueError('No aggregation model specified.')
        if redo:
            if 'raw' in kwargs:
                self.set(raw=kwargs['raw'])
            lp = ds.info['raw'].info['lowpass']
            nyq = lp * 2  # nyquist rate requires at least twice the sampling.
            sfreq = ds.info['raw'].info['sfreq']
            if decim > sfreq / nyq:
                raise NotImplementedError('Decimated value will cause '
                                          'aliasing.')

            # add epochs to the Dataset after excluding bad channels
            orig_N = ds.n_cases
            
            events = np.zeros((orig_N, 3), int)
            events[:, 0] = ds['i_start'].x
            events[:, 1] = np.arange(orig_N)
            events[:, 2] = ds['trigger'].x
            
            raw = ds.info['raw']
            
            epochs = mne.Epochs(raw=raw, events=events, event_id=None, 
                                tmin=tmin, tmax=tmax, decim=decim, 
                                baseline=baseline, reject=reject, 
                                preload=True, verbose=False)
            
            # trim to match events in epochs
            if len(epochs) < ds.n_cases:
                index = epochs.events[:, 1]
                ds = ds.sub(index)
            ds[name] = epochs

            remainder = ds.n_cases * 100 / orig_N
            self.logger.info('epochs: %d' % remainder + r'% ' +
                             'of trials remain')
            if remainder < 75:
                self.logger.info('subject %s is excluded due to large number '
                                 % self.get('subject') + 'of rejections')
                del ds[name]
                ds.info['use'] = False
            else:
                ds.info['use'] = True
                # do compression
                if evoked:
                    ds = ds.aggregate(model, drop_bad=True)
                    ds.info['use'] = True
        else:
            ds = pickle.load(open(self.get('ica-epochs')))
            self.set(raw=self.get('raw') + '-ica')
            if reject:
                ds, idx = self.reject_epochs(ds, threshold=reject['mag'])
                reject = sum(idx) * 100 / len(idx)
                if reject < 75:
                    self.logger.info('subject %s is excluded due to large '
                                     % self.get('subject') +
                                     'number of rejections')
                    del ds['epochs']
                    ds.info['use'] = False
                else:
                    ds.info['use'] = True
                    if evoked:
                        ds = ds.aggregate(model, drop_bad=True)
        return ds

    def reject_epochs(self, ds, threshold=3e-12):
        picks = mne.io.pick_types(ds['epochs'].info)
        epochs = ds['epochs'].get_data()
        idx = threshold >= np.max(np.max(epochs[:, picks, :], 2) -
                                  np.min(epochs[:, picks, :], 2), 1)
        ds = ds[idx]

        print E.table.frequencies(idx)
        return ds, idx

    def make_BESA_files(self, asc=False):
        tstart = -.1
        tstop = .6
        epoch = int((tstop - tstart) * 1e3)

        ds = self.load_events(remove_bad_chs=False)
        ds = ds[ds['target'] == 'prime']
        d = E.Dataset()
        d['Tms'] = E.Var(range(0, epoch * ds.n_cases, epoch))
        d['Code'] = E.Var(np.ones(ds.n_cases))
        d['TriNo'] = ds['trigger']
        d.save_txt(self.get('besa_evt'))

        if asc:
            # loads a epoch x sensor x time
            ds = E.load.fiff.add_epochs(ds, tstart=tstart, tstop=tstop)
            # makes a time x sensor x epoch
            epochs = ds['MEG'].x.T
            epochs = [epochs[:, :, i] for i in xrange(epochs.shape[2])]
            epochs = np.vstack(epochs) * 1e15
            np.savetxt(self.get('besa_ascii', mkdir=True), epochs)

    ################
    #    source    #
    ################

    def make_fiducials(self):
        mne.gui.fiducials(self.get('subject'),
                          subjects_dir=self.get('mri_dir'),
                          fid_file=self.get('fids'))

    def make_coreg(self):
        mne.gui.coregistration(raw=self.get('raw-file'),
                               trans_fname=self.get('trans'),
                               subjects_dir=self.get('mri_dir'))

    def make_proj(self, write=True, overwrite=False, nprojs=5, verbose=False):
        ds = self.load_events(proj=False, edf=False, drop_bad_chs=True)
        if write and not overwrite:
            if os.path.lexists(self.get('proj')):
                raise IOError("proj file at %r already exists"
                              % self.get('proj'))
        ds_fix = ds[ds['experiment'] == 'fixation']
        epochs = E.load.fiff.mne_epochs(ds_fix, tmin=-0.2, tmax=.6,
                                        baseline=(None, 0),
                                        reject={'mag':3e-12})


        # add the projections to this object by using
        proj = mne.proj.compute_proj_epochs(epochs, n_grad=0, n_mag=nprojs,
                                            n_eeg=0, verbose=verbose)
        if write == True:
            mne.write_proj(self.get('proj'), proj)
            self.logger.info('proj: Projection written to file')
        else:
            return proj

    def make_cov(self, write=True, raw='calm_fft_hp1_lp40', proj=False, 
                 reject={'mag':4e-12}, overwrite=False):
        ds = self.load_events(proj=proj, edf=True)
        if proj:
            proj_val = '_+proj'
        else:
            proj_val = ''
        if write and not overwrite:
            if os.path.lexists(self.get('cov', proj_val=proj_val)):
                raise IOError("cov file at %r already exists"
                              % self.get('cov'))

        # create covariance matrix
        index = ds['experiment'] == 'fixation'
        ds_fix = ds[index]

        epochs = E.load.fiff.mne_epochs(ds_fix, baseline=(-.2, 0),
                                        reject=reject, tmin=-.2,
                                        tmax=0, verbose=False)
        cov = mne.cov.compute_covariance(epochs, verbose=False)

        if write == True:
            cov.save(self.get('cov'))
            self.logger.info('cov: Covariance Matrix written to file')
        else:
                return cov

    def make_fwd(self, overwrite=False):
        # create the forward solution
        os.environ['SUBJECTS_DIR'] = self.get('mri_dir')

        src = self.get('src')
        trans = self.get('trans')
        bem = self.get('bem-sol', fmatch=True)
        fwd = self.get('fwd')
        rawfif = self.get('raw-file')

        mne.forward.make_forward_solution(rawfif, trans, src, bem, fwd,
                                          eeg=False, ignore_ref=True,
                                          overwrite=overwrite)

        if os.path.exists(fwd):
            self.logger.info('fwd: Forward Solution written to file')
        else:
            print '\n> ERROR:'
            err = "fwd-file not created"
            raise RuntimeError(err)

    def make_fwd_c(self, fromfile=True, overwrite=False):
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


    def make_stcs(self, ds, roi=None, evoked=True, verbose=False, method='dSPM',
                  **kwargs):

        """Creates an stc object of transformed data from the ds

        Parameters
        ----------
        ds: Dataset
            data
        roi: str instance of ROI
        orient: 'fixed' | 'free'
            'fixed' = Fixed orientation, 'free' = Free orientation
        evoked: bool
            True: evoked
            False: epochs
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
        # for ROI analyses
        if roi:
            roi = self.read_label(roi)

        # makes stc epochs or evoked
        if evoked == True:
            stcs = mne.minimum_norm.apply_inverse(ds['epochs'], inv,
                                                  lambda2=1. / 2 ** 2,
                                                  method=method, verbose=verbose)
            if roi:
                stcs = stcs.in_label(roi)
            return stcs
        else:
            if roi:
                # a list of stcs within label per epoch.
                stcs = mne.minimum_norm.apply_inverse_epochs(ds['epochs'], inv,
                                                             label=roi,
                                                             lambda2=1. / 2 ** 2,
                                                             method=method,
                                                             verbose=verbose)
            else:
                stcs = mne.minimum_norm.apply_inverse_epochs(ds['epochs'], inv,
                                                             lambda2=1. / 2 ** 2,
                                                             method=method,
                                                             verbose=verbose)

            return stcs

    def make_custom_labels(self):
        "makes custom fs labels for subjects"
        custom_labels.make_LATL_label(self)
        custom_labels.make_LPTL_label(self)
        custom_labels.make_split_fusiform(self)
        custom_labels.make_vmPFC_label(self)

    def plot_coreg(self, redo=False):
        s_e = self.get('{s_e}')
        fname = self.get('plot-file', datatype='meg', analysis='%s-helmet' %s_e)
        if not redo and os.path.exists(fname):
            return

        from mayavi import mlab
        import eelbrain.data.plot.coreg as coreg

        raw = mne.io.Raw(self.get('raw-file'))
        p = coreg.dev_mri(raw, head_mri_t=self.get('trans'))
        p.save_views(fname, overwrite=True)
        mlab.close()

    def read_label(self, labels, subject=None):
        "label: list"

        if subject is None:
            self.set(subject='fsaverage', match=False)
        else:
            self.set(subject=subject)
        rois = []
        if not isinstance(labels, list):
            labels = [labels]
        for label in labels:
            label = os.path.join(self.get('label_sdir'), label)
            if os.path.splitext(label)[-1] != '.label':
                label = label + '.label'
            rois.append(mne.read_label(label))

        if len(rois) > 1:
            roi = rois.pop(0)
            rois = sum(rois, roi)
        elif len(rois) == 1:
            rois = rois[0]
        return rois

    def make_morph_matrix(self, hemi=None):
        from mne.source_estimate import compute_morph_matrix as cmm

        ss = mne.source_space.read_source_spaces(self.get('src'))
        common_ss = mne.source_space.read_source_spaces(self.get('common_src'))
        if hemi == 'lh':
            ss = [ss[0]['vertno'], np.array([])]
            common_ss = [common_ss[0]['vertno'], np.array([])]
        elif hemi == 'rh':
            ss = [np.array([]), ss[1]['vertno']]
            common_ss = [np.array([]), common_ss[1]['vertno']]
        else:
            ss = [ss[0]['vertno'], ss[1]['vertno']]
            common_ss = [common_ss[0]['vertno'], common_ss[1]['vertno']]

        morph = cmm(subject_from=self.subject,
                    subject_to=self.get('common_brain'),
                    vertices_from=ss, vertices_to=common_ss)
        return morph, common_ss

    def analyze_source(self, ds, evoked=False, rois=None, morph=False,
                       mne_obj=False, method='dSPM', **kwargs):
        """
        """
        orient = self.get('orient')
        if 'orient' in kwargs:
            orient = kwargs['orient']
        if 'hemi' in kwargs:
            hemi = kwargs['hemi']
        else:
            hemi = None
        common_brain = self.get('common_brain')
        subject = self.get('subject')

        if morph:
            morph_mat, verts = self.make_morph_matrix(hemi)

        if rois:
            if 'roilabels' in kwargs:
                roilabels = kwargs['roilabels']
                rois = zip(rois, roilabels)
            else:
                rois = zip(rois, rois)

        if evoked:
            stcs = []
            if rois:
                for roi, roilabel in rois:
                    # do source transformation
                    for d in ds.itercases():
                        stc = self.make_stcs(d, roi=roi, evoked=evoked,
                                             orient=orient, method=method)
                        stc = E.load.fiff.stc_ndvar(stc, subject=subject,
                                                    src='ico-4')
                        stc = stc.summary('source', name='stc')
                        stcs.append(stc)
                    ds[roilabel] = E.combine(stcs)
            # whole brain
            else:
                for d in ds.itercases():
                    stc = self.make_stcs(d, evoked=evoked, orient=orient,
                                         method=method)
                    # temporary fix
                    if stc.subject == common_brain:
                        morph = False
                    if morph:
                        stc = mne.morph_data_precomputed(subject, common_brain,
                                                         stc, verts, morph_mat)
                    stcs.append(stc)
                ds['stc'] = E.load.fiff.stc_ndvar(stcs, subject=common_brain,
                                                  src='ico-4')


        else:
            if rois:
                for roi, roilabel in rois:
                    stcs = self.make_stcs(ds, roi, evoked=evoked, orient=orient)
                    if morph:
                        stcs = mne.morph_data_precomputed(subject, common_brain,
                                                          stcs, verts, morph_mat)
                    ds[roilabel] = E.load.fiff.stc_ndvar(stcs, subject=subject,
                                                         src='ico-4')
                    ds[roilabel] = ds[roilabel].summary('source', name=roilabel)
            else:
                stcs = self.make_stcs(ds, evoked=evoked, orient=orient)
                if morph:
                    stcs = mne.morph_data_precomputed(subject, common_brain,
                                                      stcs, verts, morph_mat)
                ds['stc'] = E.load.fiff.stc_ndvar(stcs, subject=subject,
                                                  src='ico-4')


        del stcs, ds['epochs']
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
        dataset = self.load_events(edf=False, drop_bad_chs=False, **kwargs)
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
#             idx = np.setdiff1d(range(dataset.n_cases), ds.info['reject'])
            dataset = dataset[ds['accept'] == True]
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
    ptb_trigger = E.Var(triggers, name='ptb_trigger')
    trigger_time = E.Var(trigger_times, name='trigger_time')
    display = E.Factor(displays, name='display')

    if 'subject' in kwargs:
        subject = E.Factor([kwargs['subject']], rep=len(latency), name='subject')
        ds = E.Dataset(subject, display, ptb_trigger, latency, trigger_time)
    else:
        ds = E.Dataset(display, ptb_trigger, latency, trigger_time)
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
                   'c1', 'c1_rating', 'c1_sd', 'c1_freq',
                   'c2', 'c2_rating', 'c2_sd', 'c2_freq']
    words = E.combine((c1, c2, word))
    word_dict = {word: i for i, word in enumerate(words['word'])}
    word_idx = [word_dict[word.lower()] for word in ds['display']]

    return words[word_idx]


def load_bad_chs_info(bads_file):
    bad_chs = drop = []
    if os.path.lexists(bads_file):
        bads = open(bads_file).readlines()
        for line in bads:
            if line.startswith('bads='):
                bad_chs = re.findall('(MEG \d+)', line)
            if line.startswith('drop='):
                drop = int(re.findall('(\d)', line)[0])
    return drop, bad_chs


def load_coca_freq_info(freq_info):
#     E.load.tsv
    words = E.combine((c1, c2, word))
    word_dict = {word: i for i, word in enumerate(words['word'])}
    word_idx = [word_dict[word.lower()] for word in ds['display']]

    words[word_idx]


