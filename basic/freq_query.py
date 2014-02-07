'''
Created on Oct 10, 2013

@author: teon
'''

import psycopg2
from basic import process
import numpy as np

conn_string = ("host='172.22.70.133' dbname='nellab' user='nellab' "
        "password='jut5yem%'")
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
stim_info = '/Users/teon/Dropbox/Experiments/NMG/exp/stims/stims_info.mat'

ds = process.read_stim_info(stim_info)
freqs = []
words = []

for word in np.unique(ds['c1']):
    cursor.execute('select count from coca_unigram_freq ' 
                   'where word = %s', (word,))
    results = cursor.fetchall()
    words.append(word)
    if len(results) == 0:
        freqs.append(0)
    else:
        freqs.append(results[0][0])
        
ds = E.Dataset()
ds['c1'] = E.Factor(words)
ds['lemma_freq']

