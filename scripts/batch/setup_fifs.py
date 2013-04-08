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
e.set(raw='hp0.1_lp40')
e._state['name'] = ''

for _ in e.iter_vars(['subject']):
    print e.get('subject')

#    e.reset()
#    if not os.path.lexists(e.get('raw-file')):
#        e.kit2fiff()


    e.make_cov(remove_bad_chs=True, overwrite=True)

    e.make_fwd(overwrite=True)

#    e.make_fiducials()

#    e.make_coreg()

#    e.makeplt_coreg(redo=False)

#    e.make_bpf_raw(hp=1, lp=40, redo=True, l_trans_bandwidth=.5,
#             h_trans_bandwidth=.5)
