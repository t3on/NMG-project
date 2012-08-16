import os
import mne
from eelbrain.eellab import *
from eelbrain.utils import subp
import load_events


meg_ds = load_events.load_meg_events('R0095')


#currently you can only make a single stc per condition. modify for each condition
cl = ['control_identity', 'identity', 'control_constituent', 'first_constituent']
wt = ['opaque', 'transparent', 'novel', 'ortho']


stc_data = []

condition = []

wordtype = []


for type in wt: 
    for cond in cl:
        # load the events of interest
        index1 = meg_ds['condition'] == cond
        index2 = meg_ds['category'] == type
        meg = meg_ds.subset(index1 & index2)

        fwd = mne.read_forward_solution(meg.info['fwd'])
        cov = mne.read_cov(meg.info['cov'])
		
		# create the inverse solution
        ds = load.fiff.mne_Epochs(meg, tstart=-0.2, tstop=0.6, baseline=(-.2, 0), reject=None)
        inv = mne.minimum_norm.make_inverse_operator(ds.info, fwd, cov, loose = None)
		
	
		#average ds
	
		#ds = ds.average()
	
	
        #make this general at some point
        label = mne.read_label('/Users/teon/data/MRI/R0095/label/fusiform-rh.label')


        stcs = mne.minimum_norm.apply_inverse_epochs(ds, inv, lambda2 = 1./9, label = label)

        stc_data.extend(stc.data.mean(0) for stc in stcs)
        condition.extend([cond] * len(stcs))

        wordtype.extend([type] * len(stcs))

        #stc.save(os.path.join(meg.info['fifdir'], 'stc', '_'.join((meg_ds.info['subname'], type, cond))))







ds = dataset()

ds['condition'] = factor(condition)

ds['wordtype'] = factor(wordtype)



T = var(stcs[0].times, name='time')

ds['stc'] = ndvar(np.vstack(stc_data), dims=('case', T))



