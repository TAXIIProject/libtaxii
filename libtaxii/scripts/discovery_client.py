
#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

from libtaxii.scripts import TaxiiScript
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq


class DiscoveryClient11Script(TaxiiScript):
    parser_description = 'The TAXII 1.1 Discovery Client sends a Discovery Request message to a TAXII Server and ' \
                         'prints out the Discovery Response message to standard out.'
    path = '/services/discovery/'

    def create_request_message(self, args):
        return tm11.DiscoveryRequest(message_id=tm11.generate_message_id())


def main():
    script = DiscoveryClient11Script()
    script()

if __name__ == "__main__":
    main()
