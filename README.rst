libtaxii
========

A Python library for handling TAXII Messages and invoking TAXII Services.

:Source: https://github.com/TAXIIProject/libtaxii
:Documentation: http://libtaxii.readthedocs.org
:Information: http://taxii.mitre.org
:PyPI page: https://pypi.python.org/pypi/libtaxii/

|travis badge| |version badge| |downloads badge|

.. |travis badge| image:: https://api.travis-ci.org/TAXIIProject/libtaxii.png?branch=master
   :target: https://travis-ci.org/TAXIIProject/libtaxii
   :alt: Build Status
.. |version badge| image:: https://pypip.in/v/libtaxii/badge.png
   :target: https://pypi.python.org/pypi/libtaxii/
.. |downloads badge| image:: https://pypip.in/d/libtaxii/badge.png
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

You are encouraged to provide feedback by commenting on open issues or signing
up for the `TAXII discussion list
<http://taxii.mitre.org/community/registration.html>`_ and posting your
questions.
