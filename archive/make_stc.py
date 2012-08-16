import os
import mne
from eelbrain.eellab import *
from eelbrain.utils import subp
import load_events


meg_ds = load_events.load_meg_events('R0095')


#currently you can only make a single stc per condition. modify for each condition
cl = ['control_identity', 'identity', 'control_constituent', 'first_constituent']
wt = ['opaque', 'transparent', 'novel', 'ortho']


for type in wt: 
	for cond in cl:
	
		# load the events of interest
		index1 = meg_ds['condition'] == cond
		index2 = meg_ds['category'] == type
		meg = meg_ds.subset(index1*index2)
		
		fwd = mne.read_forward_solution(meg.info['fwd'])
		cov = mne.read_cov(meg.info['cov'])
		
		# create the inverse solution
		ds = load.fiff.mne_Epochs(meg, tstart=-0.2, tstop=0.6, baseline=(-.2, 0), reject={'mag':3e-12})
		inv = mne.minimum_norm.make_inverse_operator(ds.info, fwd, cov, loose = None)
		
	
		#average ds
	
		ds = ds.average()

	
		stc = mne.minimum_norm.apply_inverse(ds, inv, lambda2 = 1./9)
		stc.save(os.path.join(meg.info['fifdir'], 'stc', '_'.join((meg_ds.info['subname'], type, cond))))