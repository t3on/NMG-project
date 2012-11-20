'''
Created on Nov 15, 2012

@author: teon
'''
import eelbrain.eellab as E
import basic.process as process
import basic.source as source
import os
import mne
import scipy.stats as stats

movie_dir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'results', 'movies')
subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']), ('R0504', ['MEG 031']),
            ('R0414', []), ('R0547', ['MEG 002']), ('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084']),
            ('R0574', []), ('R0575', []), ('R0576', ['MEG 143'])]


tstart = -0.1
tstop = 0.6
reject = 3e-12

morphed_stcs = []
subjects_list = []
condition = []
target = 'prime'

for subject in subjects:
    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')
    index = meg_ds['target'] == target

    #create picks to remove bad channels
    if subject[1]:
        meg_ds.info['raw'].info['bads'].extend(subject[1])

    meg_ds = meg_ds[index]
    #meg_ds = process.reject_blinks(meg_ds)

    #add epochs to the dataset after excluding bad channels
    idx = meg_ds['target'] == 'prime'
    meg = E.load.fiff.add_mne_epochs(meg_ds[idx], tstart=tstart, tstop=tstop,
                        reject={'mag':reject}, preload=True, downsample=4)
    stc = source.make_stcs(meg, force_fixed=False,
                           stc_object=True, stc_type='evoked')

    morphed = mne.morph_data(subject_from=meg_ds.info['mri_subname'],
                             subject_to='00', stc_from=stc, grade=4, n_jobs=10)

    orig = E.load.fiff.stc_ndvar(stc, meg.info['mri_subname'], 'orig')
    orig -= orig.summary(time=(tstart, 0))


    morphed = E.load.fiff.stc_ndvar(morphed, '00', 'morphed')
    morphed -= morphed.summary(time=(tstart, 0))

    #Individual subjects plots    
#    a = E.plot.brain.activation(orig, hemi='lh')
#    a.lh.show_view('lateral')
#    a.animate(save_mov=os.path.join(movie_dir,
#                '%s-orig.mov' % meg.info['subname']))

    b = E.plot.brain.activation(morphed, hemi='lh')
    b.lh.show_view('lateral')
    b.animate(save_mov=os.path.join(movie_dir,
                '%s-morphed-lateral.mov' % meg.info['subname']))
    b.lh.show_view('medial')
    b.animate(save_mov=os.path.join(movie_dir,
                '%s-morphed-medial.mov' % meg.info['subname']))

    morphed_stcs.append(morphed)
    subjects_list.append(meg_ds.info['subname'])
    condition.append(target)


subjects_list = E.factor(subjects_list, name='subject', random=True)
condition = E.factor(condition, name='condition')
stcs = E.combine(morphed_stcs)
for i in xrange(len(stcs.x)):
    stcs.x[i] = stats.mstats.zscore(stcs.x[i], axis=None)

stcs -= stcs.summary(time=(tstart, 0))

group_ds = E.dataset(subjects_list, condition, stcs)
tt = E.testnd.ttest(Y=group_ds['morphed'], X=group_ds['condition'], c1='prime')

a = E.plot.brain.stat(tt.p, hemi='lh')
a.lh.show_view('lateral')
a.animate(save_mov=os.path.join(movie_dir, 'group-lateral.mov'))

a.lh.show_view('caudal')
a.animate(save_mov=os.path.join(movie_dir, 'group-caudal.mov'))

a.lh.show_view('ventral')
a.animate(save_mov=os.path.join(movie_dir, 'group-ventral.mov'))

a.lh.show_view('medial')
a.animate(save_mov=os.path.join(movie_dir, 'group-medial.mov'))
