#!/usr/bin/env python

# Copyright (c) 2015 - The MITRE Corporation
# For license information, see the LICENSE.txt file

from os.path import abspath, dirname, join
import sys

from setuptools import setup, find_packages

BASE_DIR = dirname(abspath(__file__))
VERSION_FILE = join(BASE_DIR, 'libtaxii', 'version.py')


def get_version():
    with open(VERSION_FILE) as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                version = line.split()[-1].strip('"')
                return version
        raise AttributeError("Package does not have a __version__")


py_maj, py_minor = sys.version_info[:2]
if (py_maj, py_minor) < (2, 6) or (py_maj == 3 and py_minor < 3):
    raise Exception('libtaxii requires Python 2.6, 2.7 or 3.3+')

install_requires = [
    'lxml>=2.2.3',
    'python-dateutil>=1.4.1',
    'six>=1.9.0',
]

try:
    import argparse
except ImportError:
    install_requires.append('argparse')

with open("README.rst") as f:
    long_description = f.read()

setup(
    name='libtaxii',
    description='TAXII Library.',
    author='Mark Davidson',
    author_email='mdavidson@mitre.org',
    url="http://taxii.mitre.org/",
    version=get_version(),
    packages=find_packages(),
    install_requires=install_requires,
    scripts=[
        'libtaxii/scripts/collection_information_client.py',
        'libtaxii/scripts/discovery_client.py',
        'libtaxii/scripts/fulfillment_client.py',
        'libtaxii/scripts/inbox_client.py',
        'libtaxii/scripts/inbox_client_10.py',
        'libtaxii/scripts/poll_client.py',
        'libtaxii/scripts/query_client.py',
        'libtaxii/scripts/discovery_client_10.py',
        'libtaxii/scripts/feed_information_client_10.py',
        'libtaxii/scripts/poll_client_10.py',
    ],
    entry_points={
        'console_scripts': [
            'collection_information_client = libtaxii.scripts.collection_information_client:main',
            'discovery_client = libtaxii.scripts.discovery_client:main',
            'fulfillment_client = libtaxii.scripts.fulfillment_client:main',
            'inbox_client = libtaxii.scripts.inbox_client:main',
            'inbox_client_10 = libtaxii.scripts.inbox_client_10:main',
            'poll_client = libtaxii.scripts.poll_client:main',
            'query_client = libtaxii.scripts.query_client:main',
            'discovery_client_10 = libtaxii.scripts.discovery_client_10:main',
            'feed_information_client_10 = libtaxii.scripts.feed_information_client_10:main',
            'poll_client_10 = libtaxii.scripts.poll_client_10:main',
        ],
    },
    package_data={'libtaxii': ['xsd/*.xsd']},
    long_description=long_description,
    keywords="taxii libtaxii",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
