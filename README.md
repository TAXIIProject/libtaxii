libtaxii
--------

Python module for TAXII. libtaxii provides Python object access to 
TAXII Messages and HTTP/HTTPS clients for invoking TAXII Services.

Update 5/15 - This module is being modified to conform to TAXII 1.0. The following changes have been made:

1. libtaxii/messages.py contains the new interface for TAXII Messages (This is very different than taxii_message_converter.py)
2. libtaxii/clients.py contains the new interface for TAXII Clients (This is somewhat different than taxii_client.py)
3. tests/ contains tests for libtaxii. These may be informative examples as well.
4. libtaxii/taxii_message_converter.py is now deprecated
5. libtaxii/taxii_client.py is not deprecated

In the future, the following will happen:

1. There will be a version of libtaxii that contains both the new interfaces and the old interfaces. This 
version is intended to be used by implementers who want to migrate from the deprecated interfaces 
(taxii_message_converter.py and taxii_client.py) to the new interfaces (messages.py and clients.py).
2. After #1, the old interfaces will be removed, and a 1.0.1 version will be released.

Update 4/30 - This module is currently out of date. TAXII 1.0 Final will be released later today (4/30/2013), 
and this library is not conformant with TAXII 1.0 Final. Providing developer support is a priority, and libtaxii 
will be updated in the near future. The concepts in this library are expected to 
(for the most part) remain unchanged as the library is updated to conform to TAXII 1.0 Final.

More information can be found at https://github.com/TAXIIProject.

For license information, see the LICENSE.txt file.
