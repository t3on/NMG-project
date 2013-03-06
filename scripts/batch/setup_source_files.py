'''
Created on Oct 25, 2012

@author: teon
'''
import basic.process as process

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')


e = process.NMG()
e.exclude = {'subject': ['R0224']}
e.set(raw='lp-40hp-1')
for _ in e.iter_vars(['subject']):
    print e.get('subject')
#    e.make_proj(overwrite=True)
    e.make_cov(remove_bad_chs=True, overwrite=True)
#    e.make_fwd(overwrite=True)
#    e.make_fiducials()
#    e.make_coreg()
#    e.do_raw(redo=False)
