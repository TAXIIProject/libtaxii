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
    parser.add_argument("--port", dest="port", default="80", type=int, help="Port where the Poll Service is hosted. Defaults to 80.")
    parser.add_argument("--path", dest="path", default="/services/query_example/", help="Path where the Poll Service is hosted. Defaults to /services/poll/.")
    parser.add_argument("--collection", dest="collection", default="default_queryable", help="Data Collection that this Fulfillment request applies to. Defaults to 'default_queryable'.")
    parser.add_argument("--result_id", dest="result_id", required=True, help="The result_id being requested.")
    parser.add_argument("--result_part_number", dest="result_part_number", default=1, help="The part number being requested. Defaults to '1'.")
    parser.add_argument("--https", dest="https", default=False, type=bool, help="Whether or not to use HTTPS. Defaults to False")
    parser.add_argument("--cert", dest="cert", default=None, help="The file location of the certificate to use. Defaults to None.")
    parser.add_argument("--key", dest="key", default=None, help="The file location of the private key to use. Defaults to None.")
    parser.add_argument("--proxy", dest="proxy", default='noproxy', help="A proxy to use (e.g., http://example.com:80/), or None to not use any proxy. Omit this to use the system proxy.")

    args = parser.parse_args()

    poll_fulf_req = tm11.PollFulfillmentRequest(message_id=tm11.generate_message_id(),
                              collection_name=args.collection,
                              result_id=args.result_id,
                              result_part_number=args.result_part_number)

    poll_fulf_req_xml = poll_fulf_req.to_xml(pretty_print=True)
    print "Poll Fulfillment Request: \r\n", poll_fulf_req_xml
    client = tc.HttpClient()
    client.setUseHttps(args.https)
    client.setProxy(args.proxy)
    if args.cert is not None and args.key is not None:
        client.setAuthType(tc.HttpClient.AUTH_CERT)
        client.setAuthCredentials({'key_file': args.key, 'cert_file': args.cert})
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, poll_fulf_req_xml, args.port)
    response_message = t.get_message_from_http_response(resp, '0')
    print "Response Message: \r\n", response_message.to_xml(pretty_print=True)

if __name__ == "__main__":
    main()
