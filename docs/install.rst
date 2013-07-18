Installation instructions for libtaxii  
======================================

Step 1: Install libtaxii's dependencies
---------------------------------------

These libraries may have their own dependencies (for example, lxml requires libxml2). Look in setup.py for the minimum required version of each library.

1. lxml - Home page: http://lxml.de/
2. dateutil - Home page: http://labix.org/python-dateutil
3. M2Crypto **(only required for libtaxii 1.0.101 and lower)** - Home page: http://chandlerproject.org/Projects/MeTooCrypto

Step 2: Install libtaxii
------------------------

1. On the tags section (https://github.com/TAXIIProject/libtaxii/tags) of libtaxii's GitHub page, identify the version of libtaxii you would like to install.
2. Download the zip (Windows) or tarball (Unix/Linux) to the computer you want to install libtaxii on.
3. Extract the contents of the zip/tarball
4. Navigate into the directory where the extracted contents are
5. Run the following command ``python setup.py install``
  
Step 3: Test the installation  
-----------------------------
  
1. At a command prompt, type ``python`` to enter the python interpreter  
2. Type the following command: ``import libtaxii``
3. If you do not get an ImportError, the install succeeded.  