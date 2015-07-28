#!/usr/bin/env python
"""
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file
"""


import libtaxii.messages_11 as tm11
from libtaxii.scripts import TaxiiScript


class CollectionInformationClient11Script(TaxiiScript):
    """Collection Information Request Client"""

    parser_description = \
        'The TAXII 1.1 Collection Information Client sends a Collection Information Request ' \
        'to a TAXII Server and then prints the resulting Collection Information Response to ' \
        'standard out.'

    path = '/services/collection-management/'

    def create_request_message(self, args):
        message_id = tm11.generate_message_id()
        return tm11.CollectionInformationRequest(message_id)


def main():
    """Send a Collection Information Request to a Taxii 1.0 Service"""
    script = CollectionInformationClient11Script()
    script()

if __name__ == "__main__":
    main()
