'''
Created on Aug 17, 2012

@author: teon
'''

import basic.process as process

e = process.NMG()

for _ in e.iter_vars('subject'):
    print e.get('subject')
    e.kit2fiff()
