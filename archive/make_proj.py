#make_proj.py
##Teon Brooks
##July 26, 2012

import os
import mne
from eelbrain.eellab import *
from eelbrain.utils import subp


def make_proj(ds):

#add the projections to this object by using 
	ds_fix = ds[ds['experiment'] == 'fixation']
	epochs = load.fiff.mne_Epochs(ds_fix, tstart=-0.2, tstop=.6, baseline=(None, 0), reject={'mag':1.5e-11})
	sensor = load.fiff.sensors(epochs)
	proj = mne.proj.compute_proj_epochs(epochs, n_grad=0, n_mag=5, n_eeg=0)
	
	#for our data, the iron-cross noise is the first principal component
	#first_proj = proj[0]['data']['data']
	#name = proj[0]['desc'][-5:]
	#PCA = ndvar(first_proj, (sensor,), name=name)
	
	#problem with the write proj command
	#mne.write_proj(ds.info['proj'], proj[0])
	
	#PCA = mne.read_proj(ds.info['proj'])    
	ds.info['raw'].info['projs'] += proj[0]
	
	return ds  