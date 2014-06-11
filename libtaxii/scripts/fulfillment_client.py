#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import sys

import dateutil.parser

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.clients as tc


def main():
    parser = t.scripts.get_base_parser("Poll Fulfillment Client", path="/services/query_example/")
    parser.add_argument("--collection", dest="collection", default="default_queryable", help="Data Collection that this Fulfillment request applies to. Defaults to 'default_queryable'.")
    parser.add_argument("--result_id", dest="result_id", required=True, help="The result_id being requested.")
    parser.add_argument("--result_part_number", dest="result_part_number", default=1, help="The part number being requested. Defaults to '1'.")

    args = parser.parse_args()

    poll_fulf_req = tm11.PollFulfillmentRequest(message_id=tm11.generate_message_id(),
                              collection_name=args.collection,
                              result_id=args.result_id,
                              result_part_number=args.result_part_number)

    poll_fulf_req_xml = poll_fulf_req.to_xml(pretty_print=True)
    print "Poll Fulfillment Request: \r\n", poll_fulf_req_xml
    client = t.scripts.create_client(args)
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, poll_fulf_req_xml, args.port)
    response_message = t.get_message_from_http_response(resp, '0')
    print "Response Message: \r\n", response_message.to_xml(pretty_print=True)

if __name__ == "__main__":
    main()
