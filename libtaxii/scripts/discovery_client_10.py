#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

from libtaxii.scripts import TaxiiScript
import libtaxii as t
import libtaxii.messages_10 as tm10
from common import generate_message_id

class DiscoveryClient10Script(TaxiiScript):
    taxii_version = t.VID_TAXII_XML_10
    parser_description = 'TAXII 1.0 Discovery Client'
    path = '/services/discovery/'
    def create_request_message(self, args):
        return tm10.DiscoveryRequest(message_id = generate_message_id())

def main():
    script = DiscoveryClient10Script()
    script()

if __name__ == "__main__":
    main()
