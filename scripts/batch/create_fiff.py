'''
Created on Aug 17, 2012

@author: teon
'''

import basic.process as process

e = process.NMG()
e.exclude = {}
for _ in e.iter_vars('subject'):
    print e.get('subject')
    if not os.path.lexists(e.get('raw-file')):
        e.kit2fiff()
