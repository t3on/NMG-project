'''
Created on Feb 26, 2013

@author: teon
'''

from MySQLdb import connect, cursors

stimlist = '/Users/teon/data/NMG/stims/stims_info.txt'
ds = E.load.txt.tsv(stimlist)
freqs = []

db = connect(db='pling', host='localhost', port=3306, user='querier', passwd='dipole5%', cursorclass=cursors.DictCursor)
cur = db.cursor()

for word in ds['c2']:
    if word == 'burns':
        word = 'burn'
    if word == 'legger':
        word = 'leg'
    cur.execute('select lemma, CobPPM from celex_efl where lemma = %s', word)
    result = cur.fetchall()
    freqs.append(result[0]['CobPPM'])

ds['c2_lemma_freq'] = E.var(freqs, name='c2 lemma frequency')
