'''
Created on Nov 15, 2012

@author: teon
'''
import eelbrain.eellab as E
import os
import mne
import scipy.stats as stats
import basic.process as process

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'group_visual_response_morphed_stcs.pickled')

e = process.NMG(root='~/data')

movie_dir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments',
                          'NMG', 'results', 'visuals', 'movies')

tstart = -0.1
tstop = 0.6
reject = 3e-12

morphed_stcs = []
subjects_list = []
condition = []

if os.path.lexists(saved_data):
    stcs = pickle.load(open(saved_data))
else:
    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events()
        index = meg_ds['target'] == 'prime'
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        meg = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                            reject={'mag':reject}, preload=True, decim=4)
        stc = e.make_stcs(meg, force_fixed=False,
                               mne_stc=True, stc_type='evoked')

        morphed = mne.morph_data(subject_from=e.get('mrisubject'),
                                 subject_to=e._common_brain, stc_from=stc,
                                 grade=4, n_jobs=10)

        orig = E.load.fiff.stc_ndvar(stc, e.get('mrisubject'), 'orig')
        orig -= orig.summary(time=(tstart, 0))
        # Individual subjects plots    
        a = E.plot.brain.activation(orig, hemi='lh')
        tt = E.testnd.ttest(Y=orig)
        a = E.plot.brain.stat(tt.p, hemi='lh')
        a.lh.show_view('medial')
        a.animate(save_mov=os.path.join(movie_dir, 'orig',
                    '%s-orig-medial.mov' % e.get('subject')))

        morphed = E.load.fiff.stc_ndvar(morphed, e._common_brain, 'morphed')
        morphed -= morphed.summary(time=(tstart, 0))
        morphed_stcs.append(morphed)
        subjects_list.append(e.get('subject'))

    subjects_list = E.factor(subjects_list, name='subject', random=True)
    stcs = E.combine(morphed_stcs)
    group_ds = E.dataset(subjects_list, stcs)
    E.save.pickle(group_ds, saved_data)

group_ds['stcs'] -= group_ds['stcs'].summary(time=(tstart, 0))
tt = E.testnd.ttest(Y=group_ds['morphed'])

a = E.plot.brain.stat(tt.p, hemi='lh')#, p0=.01, p1=.001)
a.lh.show_view('lateral')
a.animate(save_mov=os.path.join(movie_dir, 'group-lateral.mov'))

a.lh.show_view('caudal')
a.animate(save_mov=os.path.join(movie_dir, 'group-caudal.mov'))

a.lh.show_view('ventral')
a.animate(save_mov=os.path.join(movie_dir, 'group-ventral.mov'))

a.lh.show_view('medial')
a.animate(save_mov=os.path.join(movie_dir, 'group-medial.mov'))
