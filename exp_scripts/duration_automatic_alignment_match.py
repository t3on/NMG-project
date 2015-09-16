'''
Created on March 10, 2015

@author: teon
'''
import os
import numpy as np
import basic.process as process
from basic import audio
import eelbrain.eellab as E
from glob import glob


e = process.NMG(None, '{home}')
# e.exclude['subject'] = ['R0414']
e.exclude['subject'] = ['R0414', 'R0499', 'R0547', 'R0560', 'R0569',
                        'R0574', 'R0575', 'R0576', 'R0580', 'R0605']
e.set(datatype='behavioral')
e.set(analysis='duration_automatic_alignment_match')

group_ds = []
for _ in e:
    ds = audio.order_textgrids(e.subject, e, e.get('audio_sdir'))
    ds = audio.get_word_duration(ds)
    orig_N = ds.n_cases
    ds['latency'].x = ds['latency'].x * 1e3
    ds['constituent_duration'] = E.Var(ds['c1_dur'].x.copy())
    ds['constituent_freq'] = E.Var(ds['c1_freq'].x.copy())
    idx = ds['orthotype'] == 'ortho-2'
    ds[idx, 'constituent_duration'] = E.Var(ds[idx, 'c2_dur'].x.copy())
    ds[idx, 'constituent_freq'] = E.Var(ds[idx, 'c2_freq'].x.copy())
    ds = ds[ds['target'] == 'target']
    ds = ds[ds['block'] == 0]

    ds['duration'] = E.Var(ds['c1_dur'].x + ds['c2_dur'].x)

    remainder = ds.n_cases * 100. / orig_N
    e.logger.info('duration: %d' % remainder + r'% ' + 'remain after outlier rejection')
    group_ds.append(ds)

group_ds = E.combine(group_ds)
group_ds.save_txt(e.get('agg-file'))
