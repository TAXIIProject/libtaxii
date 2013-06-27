#!/usr/bin/env python
#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file
import os
import sys

from setuptools import setup, find_packages

if sys.version_info < (2, 6):
    raise Exception('libtaxii requires Python 2.6 or higher.')

install_requires = ['lxml>=2.3.2', 'python-dateutil>=1.5']

with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    long_description = f.read()

setup(name='libtaxii',
      description='TAXII Library.',
      author='Mark Davidson',
      author_email='mdavidson@mitre.org',
      url="http://taxii.mitre.org/",
      version='1.0.103',
      packages=find_packages(),
      install_requires=install_requires,
      package_data={'libtaxii': ['xsd/*.xsd']},
      long_description=long_description,
      keywords="taxii libtaxii",
      )
