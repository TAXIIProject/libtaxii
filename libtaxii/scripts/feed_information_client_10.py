#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import libtaxii as t
import libtaxii.messages_10 as tm10
from libtaxii.scripts import TaxiiScript

class FeedInformationClient10Script(TaxiiScript):
    taxii_version = t.VID_TAXII_XML_10
    parser_description = 'TAXII 1.0 Feed Information Client'
    path = '/services/feed-management/'
    def create_request_message(self, args):
        return tm10.FeedInformationRequest(message_id = tm10.generate_message_id())

def main():
    script = FeedInformationClient10Script()
    script()

if __name__ == "__main__":
    main()
