#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq
import libtaxii.clients as tc
import libtaxii.scripts as scripts

def main():
    parser = scripts.get_base_parser("Discovery Client", path="/services/discovery/")
    args = parser.parse_args()

    discovery_req = tm11.DiscoveryRequest(message_id=tm11.generate_message_id())
    discovery_req_xml = discovery_req.to_xml(pretty_print=True)

    print "Discovery Request: \r\n", discovery_req_xml
    client = scripts.create_client(args)
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, discovery_req_xml, args.port)
    response_message = t.get_message_from_http_response(resp, '0')
    print "Response Message: \r\n", response_message.to_xml(pretty_print=True)

if __name__ == "__main__":
    main()
    
