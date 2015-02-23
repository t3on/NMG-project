'''
Created on Feb 26, 2013

@author: teon
'''


from MySQLdb import connect, cursors
 
list = ['apple', 'orange', 'banana']
freqs = []
lemmas = []
 
db = connect(db='nellab', host='172.22.70.133', port=3306, user='nellab', passwd='jut5yem%', 
             cursorclass=cursors.DictCursor)
cur = db.cursor()
 
for word in list:
    cur.execute('select lemma, CobPPM from celex_efl where lemma = %s', word)
    result = cur.fetchall()
    lemmas.append(result[0]['lemma'])
    freqs.append(result[0]['CobPPM'])