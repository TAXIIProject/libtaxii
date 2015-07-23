# Copyright (C) 2014 - The MITRE Corporation
# For license information, see the LICENSE.txt file

"""Backwards compatibility for TAXII 1.0.

All TAXII Message classes used to be in this file. Since TAXII 1.1 support
was added (in messages_11.py), the contents of this file were moved to
messages_10.py. This file allows existing code (referring to libtaxii.messages)
to continue working as before.
"""


from libtaxii.messages_10 import *
