#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import sys

import argparse
import dateutil.parser

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.taxii_default_query as tdq
import libtaxii.clients as tc


def main():
    parser = argparse.ArgumentParser(description="Poll Query Client")
    parser.add_argument("--host", dest="host", default="taxiitest.mitre.org", help="Host where the Poll Service is hosted. Defaults to taxiitest.mitre.org.")
    parser.add_argument("--port", dest="port", default="80", type=int, help="Port where the Poll Service is hosted. Defaults to 80.")
    parser.add_argument("--path", dest="path", default="/services/query_example/", help="Path where the Poll Service is hosted. Defaults to /services/query_example/.")
    parser.add_argument("--collection", dest="collection", default="default_queryable", help="Data Collection to poll. Defaults to 'default_queryable'.")
    parser.add_argument("--allow_asynch", dest="allow_asynch", default=True, help="Indicate whether or not the client support Asynchronous Polling. Defaults to True")
    parser.add_argument("--ip", dest="ip", default=None, help="The IP address to query")
    parser.add_argument("--hash", dest="hash", default=None, help="The file hash to query")
    parser.add_argument("--https", dest="https", default=False, type=bool, help="Whether or not to use HTTPS. Defaults to False")
    parser.add_argument("--cert", dest="cert", default=None, help="The file location of the certificate to use. Defaults to None.")
    parser.add_argument("--key", dest="key", default=None, help="The file location of the private key to use. Defaults to None.")
    parser.add_argument("--proxy", dest="proxy", default='noproxy', help="A proxy to use (e.g., http://example.com:80/), or None to not use any proxy. Omit this to use the system proxy.")
    
    args = parser.parse_args()
    
    if args.ip is None and args.hash is None:
        print "At least one of --ip or --hash must be specified!"
        sys.exit()
    
    criterion = []
    
    if args.ip is not None:
        tmp = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_CORE,
                                              relationship='equals',
                                              parameters={'value': args.ip, 'match_type': 'case_insensitive_string'})
        criterion.append(tdq.DefaultQuery.Criterion(target='//Address_Value', test=tmp))
    
    if args.hash is not None:
        tmp = tdq.DefaultQuery.Criterion.Test(capability_id=tdq.CM_CORE,
                                              relationship='equals',
                                              parameters={'value': args.hash, 'match_type': 'case_insensitive_string'})
        criterion.append(tdq.DefaultQuery.Criterion(target='//Hash/Simple_Hash_Value', test=tmp))
    
    criteria = tdq.DefaultQuery.Criteria(operator=tdq.OP_AND, criterion=criterion)
    
    q = tdq.DefaultQuery(t.CB_STIX_XML_11, criteria)

    poll_req = tm11.PollRequest(message_id=tm11.generate_message_id(),
                              collection_name=args.collection,
                              poll_parameters=tm11.PollRequest.PollParameters(allow_asynch=args.allow_asynch, query=q))

    poll_req_xml = poll_req.to_xml(pretty_print=True)
    print "Poll Request: \r\n", poll_req_xml
    client = tc.HttpClient()
    client.setUseHttps(args.https)
    client.setProxy(args.proxy)
    if args.cert is not None and args.key is not None:
        client.setAuthType(tc.HttpClient.AUTH_CERT)
        client.setAuthCredentials({'key_file': args.key, 'cert_file': args.cert})
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, poll_req_xml, args.port)
    response_message = t.get_message_from_http_response(resp, '0')
    print "Response Message: \r\n", response_message.to_xml(pretty_print=True)

if __name__ == "__main__":
    main()
