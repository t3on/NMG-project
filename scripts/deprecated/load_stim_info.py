import scipy.io
import eelbrain.eellab as E


allstims_info='/Users/teon/Dropbox/Experiments/NMG/stims/allstims_info.mat'
stims = scipy.io.loadmat(allstims_info)['stims'].T

stim_ds = E.dataset()
stim_ds['c1_rating'] = E.var(np.hstack(np.hstack(np.hstack(stims[0]))))
stim_ds['c1_sd'] = E.var(np.hstack(np.hstack(np.hstack(stims[1]))))
stim_ds['c1'] = E.factor(np.hstack(np.hstack(stims[2])))
stim_ds['c1_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims[3]))))
stim_ds['c1_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims[4]))))
stim_ds['word'] = E.factor(np.hstack(np.hstack(stims[5])))
stim_ds['word_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims[6]))))
stim_ds['word_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims[7]))))
stim_ds['wordtype'] = E.factor(np.hstack(np.hstack(np.hstack(stims[8]))), labels={0: 'opaque', 1: 'transparent', 2: 'novel',
                                                                                           3: 'ortho', 4: 'ortho'})
stim_ds['c2_rating'] = E.var(np.hstack(np.hstack(np.hstack(stims[-9]))))
stim_ds['c2_sd'] = E.var(np.hstack(np.hstack(np.hstack(stims[-8]))))
stim_ds['c2'] = E.factor(np.hstack(np.hstack(stims[-7])))
stim_ds['c2_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims[-6]))))
stim_ds['c2_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims[-5]))))
stim_ds['word2'] = E.factor(np.hstack(np.hstack(stims[-4])))
stim_ds['word2_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims[-3]))))
stim_ds['word2_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims[-2]))))
stim_ds['wordtype'] = E.factor(np.hstack(np.hstack(np.hstack(stims[-1]))), labels={0: 'opaque', 1: 'transparent', 2: 'novel',
                                                                                   3: 'ortho', 4: 'ortho'})
idx = stim_ds['word2'] != 'NaW'
idy = stim_ds['word'] == 'NaW'
stim_ds['word'][stim_ds['word'] == 'NaW'] = stim_ds[idx*idy]['word2']
idx = ~np.isnan(stim_ds['word2_freq'])
idy = np.isnan(stim_ds['word_freq'])
stim_ds['word_freq'][np.isnan(stim_ds['word_freq'])] = stim_ds[idx*idy]['word2_freq']
idx = ~np.isnan(stim_ds['word2_nmg'])
idy = np.isnan(stim_ds['word_nmg'])
stim_ds['word_nmg'][np.isnan(stim_ds['word_nmg'])] = stim_ds[idx*idy]['word2_nmg']

del stim_ds['word2'], stim_ds['word2_freq'], stim_ds['word2_nmg'], stim_ds['wordtype']

