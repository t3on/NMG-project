'''
Created on Oct 24, 2012

@author: teon
'''
import eelbrain.eellab as E
import process
import source

#subjects = ['R0414', 'R0547', 'R0569', 'R0574', 'R0575', 'R0576']
#subjects = ['R0338a', 'R0338b']
for subject in subjects:
    meg_ds = process.load_meg_events(subject)
    #source.make_proj(meg_ds)
    #source.make_cov(meg_ds)
    source.make_fwd(meg_ds, overwrite=True)
