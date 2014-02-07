'''
Created on Dec 2, 2012

@author: teon
'''

import os
import numpy as np
import basic.process as process
import eelbrain.eellab as E

e = process.NMG(None, '{db_dir}')
e.set(datatype='behavioral')
e.set(analysis='duration_predicted')

Y = E.Var((20, 20, 4, 20,19,19,5,19), name='duration')
X = E.Factor(('novel', 'opaque', 'ortho', 'transparent',
              'novel', 'opaque', 'ortho', 'transparent'),
             name='wordtype')
Z = E.Factor(('a','a','a','a', 'b','b','b','b'), random=True)

p = E.plot.uv.barplot(Y, X, figsize=(10, 5), corr=False, match=Z,
                      ylabel='Duration Priming Difference in ms',
                      test=True,
                      title="Predicted Constituent Priming Duration Difference Means")
p.fig.savefig(e.get('plot-file'))