#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import libtaxii as t
import libtaxii.messages_11 as tm11
#import libtaxii.taxii_default_query as tdq
import libtaxii.clients as tc
import libtaxii.scripts as scripts


def main():
    parser = scripts.get_base_parser("Collection Information Client", path="/services/discovery/")
    args = parser.parse_args()

    collection_information_req = tm11.CollectionInformationRequest(message_id=tm11.generate_message_id())
    
    print "Request:\n"
    if args.xml_output is False:
        print collection_information_req.to_text()
    else:
        print collection_information_req.to_xml(pretty_print=True)
    
    client = scripts.create_client(args)
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, collection_information_req.to_xml(pretty_print=True), args.port)
    r = t.get_message_from_http_response(resp, '0')
    
    print "Response:\n"
    if args.xml_output is False:
        print r.to_text()
    else:
        print r.to_xml(pretty_print=True)

if __name__ == "__main__":
    main()
