'''
Created on Oct 25, 2012

@author: teon
'''

import basic.process as process
 
e = process.NMG()

for _ in e.iter_vars('subject'):
    meg_ds = e.load_events()
    #source.make_proj(meg_ds, overwrite = True)
    #source.make_cov(meg_ds, overwrite = True)
    e.make_fwd(overwrite=True)
