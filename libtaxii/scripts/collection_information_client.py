#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq
from libtaxii.scripts import TaxiiScript


class CollectionInformationClient11Script(TaxiiScript):
    parser_description = 'TAXII 1.1 Collection Information Client'
    path = '/services/collection-management/'

    def create_request_message(self, args):
        return tm11.CollectionInformationRequest(message_id=tm11.generate_message_id())


def main():
    script = CollectionInformationClient11Script()
    script()

if __name__ == "__main__":
    main()
