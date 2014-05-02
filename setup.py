#!/usr/bin/env python
#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

from os.path import abspath, dirname, join
from setuptools import setup, find_packages
import sys

INIT_FILE = join(dirname(abspath(__file__)), 'libtaxii', '__init__.py')

def get_version():
    with open(INIT_FILE) as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                version = line.split()[-1].strip('"')
                return version
        raise AttributeError("Package does not have a __version__")
if sys.version_info < (2, 6):
    raise Exception('libtaxii requires Python 2.6 or higher.')

install_requires = ['lxml>=2.3.2', 'python-dateutil>=1.5']

with open("README.md") as f:
    long_description = f.read()

extras_require = {
    'docs': [
        'Sphinx==1.2.1',
        # TODO: remove when updating to Sphinx 1.3, since napoleon will be
        # included as sphinx.ext.napoleon
        'sphinxcontrib-napoleon==0.2.4',
    ],
}

setup(name='libtaxii',
      description='TAXII Library.',
      author='Mark Davidson',
      author_email='mdavidson@mitre.org',
      url="http://taxii.mitre.org/",
      version=get_version(),
      packages=find_packages(),
      install_requires=install_requires,
      extras_require=extras_require,
      package_data={'libtaxii': ['xsd/*.xsd']},
      long_description=long_description,
      keywords="taxii libtaxii",
      )
