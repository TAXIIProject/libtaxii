#!/usr/bin/env python
#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info <(2, 6):
    raise Exception('libtaxii requires Python 2.6 or higher.')

install_requires = ['lxml>=2.3.2', 'M2Crypto>=0.21.1', 'python-dateutil>=1.5']

setup(name='libtaxii',
      description='TAXII Library.',
      author='Mark Davidson',
      author_email='mdavidson@mitre.org',
      url="http://taxii.mitre.org/",
      version='1.0.100',
      py_modules=['libtaxii.clients', 'libtaxii.messages'],
      install_requires=install_requires,
      data_files=[('xsd', ['xsd/TAXII_XMLMessageBinding_Schema.xsd',
                           'xsd/xmldsig-core-schema.xsd'])],
      long_description=open("README").read(),
      keywords="taxii libtaxii",
      )
