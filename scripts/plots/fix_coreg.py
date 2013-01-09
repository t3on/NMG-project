'''
Created on Dec 15, 2012

@author: teon
'''

import basic.process as process
import eelbrain.eellab.plot.coreg as coreg
from mayavi import mlab

e = process.NMG('R0580')
p = coreg.dev_head_fitter(raw = e.get('rawfif'), mrk = e.get('mrk'))
#p.plot()
##p.set_hs_opacity(0)
##p.set_hs_opacity(1)
p.fit(include=[0, 1, 2, 3, 4])
fixed_data = os.path.join(e.get('fif_sdir'), 
                e.get('subject') + '_NMG_raw_fix.fif')
p.save(fixed_data)

##os.rename(fixed_data, e.get('rawfif'))