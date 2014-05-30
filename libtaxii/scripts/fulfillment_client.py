#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import sys

import argparse
import dateutil.parser

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.clients as tc


def main():
    parser = argparse.ArgumentParser(description="Poll Client")
    parser.add_argument("--host", dest="host", default="taxiitest.mitre.org", help="Host where the Poll Service is hosted. Defaults to taxiitest.mitre.org.")
    parser.add_argument("--port", dest="port", default="80", help="Port where the Poll Service is hosted. Defaults to 80.")
    parser.add_argument("--path", dest="path", default="/services/query_example/", help="Path where the Poll Service is hosted. Defaults to /services/poll/.")
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
    client = tc.HttpClient()
    client.setProxy(None) 
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, poll_fulf_req_xml, args.port)
    response_message = t.get_message_from_http_response(resp, '0')
    print "Response Message: \r\n", response_message.to_xml(pretty_print=True)

if __name__ == "__main__":
    main()
