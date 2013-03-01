'''
Created on Feb 26, 2013

@author: teon
'''

from MySQLdb import connect, cursors

list = ['apple', 'orange', 'banana']
freqs = []
lemmas = []

db = connect(db='pling', host='localhost', port=3306, user='querier', passwd='dipole5%', cursorclass=cursors.DictCursor)
cur = db.cursor()

for word in list:
    cur.execute('select lemma, CobPPM from celex_efl where lemma = %s', word)
    result = cur.fetchall()
    lemmas.append(result[0]['lemma'])
    freqs.append(result[0]['CobPPM'])


