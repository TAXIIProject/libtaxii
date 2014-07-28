#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import libtaxii as t
import libtaxii.messages_10 as tm10
import libtaxii.clients as tc
import libtaxii.scripts as scripts


def main():
    parser = scripts.get_base_parser("Discovery Client", path="/services/discovery/")
    args = parser.parse_args()

    discovery_req = tm10.DiscoveryRequest(message_id=tm10.generate_message_id())
    
    if args.xml_output is False:
        scripts.do_rich_print(discovery_req)
    else:
        print "Discovery Request: \r\n", discovery_req.to_xml(pretty_print=True)
    
    client = scripts.create_client(args)
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, discovery_req,to_xml(pretty_print=True), args.port)
    r = t.get_message_from_http_response(resp, '0')
    
    if args.xml_output is False:
        scripts.do_rich_print(r)
    else:
        print "Response Message: \r\n", r.to_xml(pretty_print=True)

if __name__ == "__main__":
    main()
