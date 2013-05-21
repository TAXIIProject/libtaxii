libtaxii
--------

libtaxii is a Python library for handling TAXII Messages as Python objects and invoking TAXII Services.

## Overview

A primary goal of libtaxii is to remain faithful to both the TAXII specifications 
and to customary Python practices. In places where these conflict, and the goal is 
to make libtaxii intuitive both to Python developers and XML developers.

## Getting Started
Documentation is not currently well supported. New users should start by looking in the /tests
directory for examples on how to use messages.py and clients.py. If your questions is not answered there (and they very well may not be),
you are encouraged to post your question to the TAXII discussion list (http://taxii.mitre.org/community/registration.html).

## Versioning

Releases of libtaxii will be given 'major.minor.revision'
version numbers, where 'major' and 'minor' correspond to the TAXII version
being supported. The 'revision' number is used to indicate new versions of
libtaxii.

## Feedback 
You are encouraged to provide feedback by commenting on open issues
or signing up for the TAXII discussion list and posting your questions 
(http://taxii.mitre.org/community/registration.html).

## News / Updates

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
