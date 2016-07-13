libtaxii
========

A Python library for handling TAXII Messages and invoking TAXII Services.

:Source: https://github.com/TAXIIProject/libtaxii
:Documentation: http://libtaxii.readthedocs.org
:Information: http://taxiiproject.github.io/
:Download: https://pypi.python.org/pypi/libtaxii/

|travis badge| |landscape.io badge| |version badge| |downloads badge|

.. |travis badge| image:: https://api.travis-ci.org/TAXIIProject/libtaxii.png?branch=master
   :target: https://travis-ci.org/TAXIIProject/libtaxii
   :alt: Build Status
.. |landscape.io badge| image:: https://landscape.io/github/TAXIIProject/libtaxii/master/landscape.png
   :target: https://landscape.io/github/TAXIIProject/libtaxii/master
   :alt: Code Health
.. |version badge| image:: https://img.shields.io/pypi/v/libtaxii.png?maxAge=2592000
   :target: https://pypi.python.org/pypi/libtaxii/
.. |downloads badge| image:: https://img.shields.io/pypi/dm/libtaxii.png?maxAge=2592000
   :target: https://pypi.python.org/pypi/libtaxii/

Overview
--------

A primary goal of libtaxii is to remain faithful to both the TAXII
specifications and to customary Python practices. libtaxii is designed to be
intuitive both to Python developers and XML developers.


Installation
------------

Use pip to install or upgrade libtaxii::

    $ pip install libtaxii [--upgrade]

For more information, see the `Installation instructions
<http://libtaxii.readthedocs.org/en/latest/installation.html>`_.


Getting Started
---------------

Read the `Getting Started guide
<http://libtaxii.readthedocs.org/en/latest/getting_started.html>`_.


Layout
------

The libtaxii repository has the following layout:

* ``docs/`` - Used to build the `documentation
  <http://libtaxii.readthedocs.org>`_.
* ``libtaxii/`` - The main libtaxii source.
* ``libtaxii/tests/`` - libtaxii tests.
* ``xsd/`` - A copy of the TAXII XML Schemas, used by libtaxii for validation.


Versioning
----------

Releases of libtaxii are given ``major.minor.revision`` version numbers, where
``major`` and ``minor`` correspond to the TAXII version being supported.  The
``revision``` number is used to indicate new versions of libtaxii.


Feedback
--------

Please provide feedback and/or comments on open issues to taxii@mitre.org.
