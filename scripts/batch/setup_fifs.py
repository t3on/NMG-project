'''
Created on Oct 25, 2012

@author: teon
'''
import basic.process as process
import os
import mne

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')


e = process.NMG()
e.exclude = {}
e.set(raw='calm')
e._state['name'] = ''

for _ in e.iter_vars(['subject']):
    print e.get('subject')

#    e.reset()
    e.make_bpf_raw(hp=.3, lp=40, redo=True, l_trans_bandwidth=.2,
                   h_trans_bandwidth=.5)
    e.set('hp0.3_lp40')
#    if not os.path.lexists(e.get('raw-file')):
#        e.kit2fiff()
    e.make_cov(remove_bad_chs=True, overwrite=True)
#
    e.make_fwd(overwrite=True)

#    e.make_fiducials()

#    e.make_coreg()

#    e.makeplt_coreg(redo=False)

