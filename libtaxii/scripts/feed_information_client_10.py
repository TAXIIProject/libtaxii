#!/usr/bin/env python

# Copyright (c) 2017, The MITRE Corporation
# For license information, see the LICENSE.txt file

import libtaxii.messages_10 as tm10
from libtaxii.scripts import TaxiiScript
from libtaxii.constants import VID_TAXII_XML_10


class FeedInformationClient10Script(TaxiiScript):
    """Feed Information Request Client"""
    taxii_version = VID_TAXII_XML_10
    parser_description = \
        'The TAXII 1.0 Feed Information Client sends a Feed Information ' \
        'Request message to a TAXII Server and prints the Feed Information ' \
        'Response message to standard out.'

    path = '/taxii-data'

    def create_request_message(self, args):
        message_id = tm10.generate_message_id()
        return tm10.FeedInformationRequest(message_id)


def main():
    """Send a Feed Information Request to a Taxii 1.0 Service"""
    script = FeedInformationClient10Script()
    script()

if __name__ == "__main__":
    main()
