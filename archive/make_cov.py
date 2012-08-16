import os
import mne
from eelbrain.eellab import *
from eelbrain.utils import subp
import load_events


# create covariance matrix

meg_ds = load_events.load_meg_events('R0095')
index = meg_ds['experiment'] == 'fixation'
fix_meg_ds = meg_ds[index]

epochs = load.fiff.mne_Epochs(fix_meg_ds, baseline=(None, 0), reject={'mag':2e-12}, tstart = -.2, tstop = .2)
cov = mne.cov.compute_covariance(epochs)
cov.save(meg_ds.info['cov'])