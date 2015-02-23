'''
Created on Sep 17, 2014

@author: teon
'''

import eelbrain as E
import basic.process as process
import os
import cPickle as pickle
import numpy as np


# raw data parameters
raw = 'calm_fft_hp1_lp40'
tmin = -0.1
tmax = 0.6
baseline = None
reject = {'mag':4e-12}
orient = 'fixed'
decim = 2
morph = True
analysis = 'prime-decode'
proj_val = ''
plot_ext='jpg'

event_id = ['transparent', 'opaque']


e = process.NMG(None, '{teon-backup_drive}')
# e = process.NMG(None, '{glyph_drive}')
e.set(raw=raw, datatype='meg')
e.set(analysis=analysis, orient=orient, proj_val=proj_val, plot_ext=plot_ext)

# datasets = []
# for _ in e:
#     print e.subject
#     # Selection Criteria
#     ds = e.load_events(edf=True, proj=False)
#     idx = ds['target'] == 'prime'
#     idy = ds['condition'] == 'identity'
#     idz = ds['wordtype'].isany('transparent', 'opaque')
#     ds = ds[idx * idy * idz]
#     ds = e.make_epochs(ds, evoked=False, raw=raw, reject=reject, decim=decim)
#     if ds.n_cases < 60:
#         ds.info['use'] = False
#     if ds.info['use']:
#         # Append to group level datasets
#         datasets.append(ds)
#         del ds
#
# # combines the datasets for group
# E.save.pickle(datasets, e.get('group-file', analysis=analysis))

# test for one subject first
ds = e.load_events('R0095', edf=True, proj=True)

idx = ds['word_length'] < 5
idy = ds['word_length'] > 7
ds = ds[np.logical_or(idx,idy)]

idx = ds['target'] == 'prime'
ds = ds[idx]
# idy = ds['condition'] == 'identity'
# idz = ds['wordtype'].isany('transparent', 'opaque')
# ds = ds[idx * idy * idz]
ds = e.make_epochs(ds, evoked=False, raw=raw, reject=reject, decim=decim, baseline=baseline)

epochs = ds['epochs']

# reindex
idx = ds['word_length'] < 5
idy = ds['word_length'] > 7
# epochs_list = [ds[ds['wordtype'] == k]['epochs'] for k in event_id]
epochs_list = []
epochs_list.append(ds[idx]['epochs'])
epochs_list.append(ds[idy]['epochs'])

# mne.epochs.equalize_epoch_counts(epochs_list)

# copied directly from decode example
###############################################################################
# Decoding in sensor space using a linear SVM
n_times = len(epochs_list[0].times)
# Make arrays X and y such that :
# X is 3d with X.shape[0] is the total number of epochs to classify
# y is filled with integers coding for the class to predict
# We must have X.shape[0] equal to y.shape[0]
data_picks = mne.pick_types(epochs.info, meg=True, exclude='bads')
X = [epoch.get_data()[:,data_picks,:] for epoch in epochs_list]
y = [k * np.ones(len(this_X)) for k, this_X in enumerate(X)]
X = np.concatenate(X)
y = np.concatenate(y)

from sklearn.svm import SVC
from sklearn.cross_validation import cross_val_score, ShuffleSplit

clf = SVC(C=1, kernel='linear')
# # Define a monte-carlo cross-validation generator (reduce variance):
cv = ShuffleSplit(len(X), 10, test_size=0.2)

scores = np.empty(n_times)
std_scores = np.empty(n_times)

for t in xrange(n_times):
    Xt = X[:, :, t]
    # Standardize features
    Xt -= Xt.mean(axis=0)
    Xt /= Xt.std(axis=0)
    # Run cross-validation
    # Note : for sklearn the Xt matrix should be 2d (n_samples x n_features)
    scores_t = cross_val_score(clf, Xt, y, cv=cv, n_jobs=1)
    scores[t] = scores_t.mean()
    std_scores[t] = scores_t.std()

times = 1e3 * epochs.times
scores *= 100  # make it percentage
std_scores *= 100
plt.plot(times, scores, label="Classif. score")
plt.axhline(50, color='k', linestyle='--', label="Chance level")
plt.axvline(0, color='r', label='stim onset')
plt.legend()
hyp_limits = (scores - std_scores, scores + std_scores)
plt.fill_between(times, hyp_limits[0], y2=hyp_limits[1], color='b', alpha=0.5)
plt.xlabel('Times (ms)')
plt.ylabel('CV classification score (% correct)')
plt.ylim([30, 100])
plt.title('Sensor space decoding')
plt.show()