
#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

from libtaxii.scripts import TaxiiScript
import libtaxii.messages_10 as tm10
from libtaxii.common import generate_message_id
from libtaxii.constants import *

class DiscoveryClient10Script(TaxiiScript):
    taxii_version = VID_TAXII_XML_10
    parser_description = 'The TAXII 1.0 Discovery Client sends a Discovery Request message to a TAXII Server and ' \
                         'prints out the Discovery Response message to standard out.'
    path = '/services/discovery/'

    def create_request_message(self, args):
        return tm10.DiscoveryRequest(message_id=generate_message_id())


def main():
    script = DiscoveryClient10Script()
    script()

if __name__ == "__main__":
    main()
