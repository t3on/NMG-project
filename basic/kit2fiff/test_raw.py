'''
Created on Jan 9, 2013

@author: teon
'''

from numpy.testing import assert_array_almost_equal, assert_array_equal
import scipy.io
import basic.kit2fiff as kit2fiff


g = kit2fiff.sqd_params('/Users/teon/Dropbox/test.sqd')
g.get_data()

h = scipy.io.loadmat('/Users/teon/Dropbox/test_Ykgw.mat')

assert_array_almost_equal(g.x, h['data'])
