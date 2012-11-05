'''
Basic ``setup.py``, intended for::

    $ python setup.py develop

Incomplete, does not specify dependencies etc.

After: 
http://packages.python.org/distribute/setuptools.html#basic-use


Created on Jul 28, 2012

@author: Christian M Brodbeck
'''
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "NMG",
    version = "0.1dev",
    packages = find_packages(),
)