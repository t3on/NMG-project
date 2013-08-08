'''
Created on Apr 24, 2013

@author: teon
'''

import basic.process as process

e = process.NMG()

# analysis
e.set(analysis='prime')

for _ in e.iter_vars():
    ds = e.load_events(remove_bad_chs=False)
    ds = ds[ds['target'] == 'prime']
    e.make_BESA_epochs(ds)
