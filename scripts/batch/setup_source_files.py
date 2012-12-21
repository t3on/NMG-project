'''
Created on Oct 25, 2012

@author: teon
'''

import basic.process as process

e = process.NMG()

for _ in e.iter_vars(['subject']):
#    e.make_proj(overwrite = True)
    e.make_cov(overwrite=True)
#    e.make_fwd(overwrite=True)
