'''
Created on Oct 25, 2012

@author: teon
'''
import basic.process as process

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')


e = process.NMG()
for _ in e.iter_vars(['subject']):
#    e.make_proj(overwrite=True)
    e.make_cov(remove_bad_chs=True, overwrite=True)
#    e.make_fwd(overwrite=True)
