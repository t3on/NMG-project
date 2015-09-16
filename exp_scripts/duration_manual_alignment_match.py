'''
Created on Dec 2, 2012

@author: teon
'''

import os
import numpy as np
import basic.process as process
import eelbrain.eellab as E


e = process.NMG(None, '{home}')
e.exclude['subject'] = ['R0414', 'R0499', 'R0547', 'R0560', 'R0569',
                        'R0574', 'R0575', 'R0576', 'R0580', 'R0605']
e.set(datatype='behavioral')
e.set(analysis='duration_manual_alignment_match')

group_ds = []
for _ in e:
    ds = e.get_word_duration(block=1)
    orig_N = ds.n_cases
    ds['duration'] = ds['c1_dur']
    idx = ds['orthotype'] == 'ortho-2'
    ds[idx]['duration'] = ds[idx]['c2_dur']
    idx = ds['ortho'] == 'ortho-2'

    remainder = ds.n_cases * 100. / orig_N
    e.logger.info('duration: %d' % remainder + r'% ' + 'remain after outlier rejection')
    group_ds.append(ds)

group_ds = E.combine(group_ds)
group_ds.save_txt(e.get('agg-file'))
