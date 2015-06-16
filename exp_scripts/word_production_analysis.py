'''
Created on March 10, 2015

@author: teon
'''

import os
import numpy as np
from basic import process, audio
import eelbrain as E
from glob import glob


redo = False
e = process.NMG(None, '{dropbox}')
e.exclude['subject'] = ['R0414']
e.set(datatype='behavioral')
e.set(analysis='duration')


if not redo and os.path.exists(e.get('agg-file')):
    group_ds = E.load.txt.tsv(e.get('agg-file'))
    group_ds['subject'].random = True
    group_ds = group_ds.aggregate('condition % wordtype % subject', drop_bad=True)
else:
    group_ds = []
    for _ in e:
        ds = audio.order_textgrids(e.subject, e.get('audio_sdir'))
        ds = audio.get_word_duration(ds)
        orig_N = ds.n_cases
        ds['latency'].x = ds['latency'].x * 1e3
        ds['constituent_duration'] = E.Var(ds['c1_dur'].x.copy())
        ds['constituent_freq'] = E.Var(ds['c1_freq'].x.copy())
        idx = ds['orthotype'] == 'ortho-2'
        ds[idx, 'constituent_duration'] = E.Var(ds[idx, 'c2_dur'].x.copy())
        ds[idx, 'constituent_freq'] = E.Var(ds[idx, 'c2_freq'].x.copy())
        ds = ds[ds['target'] == 'target']

        ds['duration'] = E.Var(ds['c1_dur'].x + ds['c2_dur'].x)

        # outlier rejection
        idx = ds['duration'].x != 0
        ds = ds[idx]

        devs = np.abs(ds['duration'].x - ds['duration'].x.mean())
        criterion = 2 * ds['duration'].x.std().repeat(ds.n_cases)
        good = devs < criterion
        ds = ds[good]

        idx = ds['word'] == 'phonetic'
        idy = ds['word'] == 'plush'
        idz = ds['word'] == 'starwart'
        idx = idx + idy + idz
        ds = ds[~idx]

        remainder = ds.n_cases * 100. / orig_N
        e.logger.info('duration: %d' % remainder + r'% ' + 'remain after outlier rejection')
        group_ds.append(ds)

    group_ds = E.combine(group_ds)
    group_ds.save_txt(e.get('agg-file'))
