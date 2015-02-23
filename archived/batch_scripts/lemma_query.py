'''
Created on Oct 10, 2013

@author: teon
'''

import psycopg2


conn_string = ("host='172.22.70.133' dbname='nellab' user='nellab' "
        "password='jut5yem%'")
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
word = 'avocado'
cursor.execute('select count from coca_unigram_freq ' 
                'where word = %s', (word,))
results = cursor.fetchall()
if len(results) == 0:
    freq = 0
else:
    freq = results[0][0]