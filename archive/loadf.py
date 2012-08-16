import os
import fnmatch

from eelbrain import ui
from eelbrain.vessels import data as _data
import eelbrain.eellab as U
import eelbrain.vessels.experiment as _eee






class experiment(_eee.mne_experiment):
    def label_events(self, ds, experiment, subject):
       return ds

    def get_templates(self):
        # path elements
        root = '{root}'
        sub = '{subject}'
        exp = '{experiment}'
        sub_dir = os.path.join(root, sub)
        param_dir = os.path.join(sub_dir, 'parameters')
        raw_dir = os.path.join(sub_dir, 'rawdata')
        meg_dir = os.path.join(raw_dir, 'meg')
        mri_dir = os.path.join(root, '..', 'MRI')
        log_dir = os.path.join(raw_dir, 'behavioral', 'logs')
        

        
        t = dict(
                 
                 # basic dir
                 meg_dir = root, # contains subject-name folders for MEG data
                 mri_dir = mri_dir, # contains subject-name folders for MEG data
                 mri_sdir = os.path.join(mri_dir, sub),
                 raw_sdir = raw_dir,
                 
                 sub = sub,
                 exp = exp,
                 
                 # kit2fiff
                 mrk = os.path.join(param_dir, '*-coregis.txt'),
                 elp = os.path.join(param_dir, '*.elp'),
                 hsp = os.path.join(param_dir, '*.hsp'),
                 rawtxt = os.path.join(raw_dir, 'meg', '_'.join((sub, exp, '*export500.txt'))),
                 rawfif = os.path.join(sub_dir, 'myfif', '_'.join((sub, exp, 'raw.fif'))),
        
                 # eye-tracker
                 edf = os.path.join(raw_dir, 'behavioral', 'eyelink', '*.edf'),
                 
                # fwd model
                 fwd = os.path.join(sub_dir, 'myfif', '_'.join((sub, exp, 'raw')) + '_fwd.fif'),
                 bem = os.path.join(mri_dir, sub, 'bem', sub+'-5120-bem-sol.fif'),
                 src = os.path.join(mri_dir, sub, 'bem', sub+'-ico-4-src.fif'),
                 
                 # these might not be necessary after doing coordinate alignment in mne_analyze!
#                 trans = os.path.join(mri_dir, sub, sub+'-trans.fif'), # mne p. 203
                 trans = os.path.join(sub_dir, 'myfif', '_'.join((sub, exp, 'raw-trans.fif'))), # mne p. 196
#                 cor = os.path.join(mri_dir, sub, 'mri', 'T1-neuromag', 'sets', 'COR.fif'),
                 
                # !! these would invalidate the s_e_* pattern with a third _
                 cov = os.path.join(raw_dir, '_'.join((sub, exp)) + '-cov.fif'),
#                inv = os.path.join(raw_dir, '_'.join((sub, exp)) + '-inv.fif'),
                
                # BESA
#                besa_triggers = os.path.join(meg_dir, sub, 'besa', '_'.join((sub, exp, an, 'triggers.txt'))),
#                besa_edt = os.path.join(meg_dir, sub, 'besa', '_'.join((sub, exp, an + '.edt'))),
                )
        
        return t

	def make_stc(self, subject=None, word='adj', redo=False, blc=False):
		"""

        blc : bool

            baseline correction

        """
		experiment = self.get('exp')
		lambda2 = 1.0 / 9

		if blc: # baseline

            tstart = -0.2

            baseline = (None, 0)
		else:

            tstart = 0

            baseline = None



       for sub, exp in self.iter_se(subject=subject, experiment=experiment):

            ds = load_meg_events(sub,exp)
            

            dsa = ds.subset(ds['condition'].isany('control_identity', 'identity'))

			if exp == 'NMG':

                X = dsa['condition']
		else:

                raise NotImplementedError


            dests = {}


            an = lambda cell: '-'.join((word, cellname(cell, '-')))


            for cell in X.cells:


                dest = self.get('stc_tgt', analysis=an(cell))


                dests[cell] = dest


            


            if not redo and all(os.path.exists(dest) for dest in dests.values()):


                continue


            


            edf = ds.info['edf']


            


            cov = mne.read_cov(self.get('cov', analysis='fixation'))


            fwd = mne.read_forward_solution(self.get('fwd'), force_fixed=False, 


                                            surf_ori=False, include=[], exclude=[])


            


            edf.mark(dsa, tstart=tstart, tstop=0.6, use=self.edf_use[sub])


            


            for cell in X.cells:


                dest = dests[cell]


                if (not redo) and os.path.exists(dest):


                    continue


                


                subds = dsa.subset((X==cell) & dsa['accept'])


                epochs = U.load.fiff.mne_Epochs(subds, 


                                                tstart=-0.1, tstop=0.6, 


                                                baseline=baseline, 


                                                reject={'mag': 2e-12}, 


                                                proj=True)


                evoked = epochs.average()


                self.stc_n[(sub, exp, an(cell))] = evoked.nave


                inv = mn.make_inverse_operator(evoked.info, fwd, cov, 


                                               loose=None, depth=None)#0.8)


                stc = mn.apply_inverse(evoked, inv, lambda2, dSPM=True, pick_normal=False)


                stc.save(dest)


                


                msgs = ["* %r/%r/%r" % (sub, exp, cellname(cell)),


                        "subds.n_cases = %s" % subds.n_cases,


                        "len(epochs.events) = %s" % len(epochs.events),


                        "evoked.nave = %s" % evoked.nave]


                self.log.append(',  '.join(msgs))


        


        pickle.dump(self.stc_n, open(self.stc_n_path, 'w'))
