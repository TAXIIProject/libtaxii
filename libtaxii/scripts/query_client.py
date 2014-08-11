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
import libtaxii.scripts as scripts


def main():
    parser = scripts.get_base_parser("Poll Query Client", path="/services/query_example/")
    parser.add_argument("--collection", dest="collection", default="default_queryable", help="Data Collection to poll. Defaults to 'default_queryable'.")
    parser.add_argument("--allow-asynch", dest="allow_asynch", default=True, help="Indicate whether or not the client support Asynchronous Polling. Defaults to True")
    parser.add_argument("--ip", dest="ip", default=None, help="The IP address to query")
    parser.add_argument("--hash", dest="hash", default=None, help="The file hash to query")

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

    q = tdq.DefaultQuery(t.CB_STIX_XML_111, criteria)

    poll_req = tm11.PollRequest(message_id=tm11.generate_message_id(),
                              collection_name=args.collection,
                              poll_parameters=tm11.PollRequest.PollParameters(allow_asynch=args.allow_asynch, query=q))

    print "Request:\n"
    if args.xml_output is False:
        print poll_req.to_text()
    else:
        print poll_req.to_xml(pretty_print=True)
    
    client = scripts.create_client(args)
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_11, poll_req.to_xml(pretty_print=True), args.port)
    r = t.get_message_from_http_response(resp, '0')
    
    print "Response:\n"
    if args.xml_output is False:
        print r.to_text()
    else:
        print r.to_xml(pretty_print=True)
    
    if r.message_type == tm11.MSG_POLL_RESPONSE:
        for cb in r.content_blocks:
            if cb.content_binding.binding_id == t.CB_STIX_XML_10:
                format = '_STIX10_'
                ext = '.xml'
            elif cb.content_binding.binding_id == t.CB_STIX_XML_101:
                format = '_STIX101_'
                ext = '.xml'
            elif cb.content_binding.binding_id == t.CB_STIX_XML_11:
                format = '_STIX11_'
                ext = '.xml'
            elif cb.content_binding.binding_id == t.CB_STIX_XML_111:
                format = '_STIX111_'
                ext = '.xml'
            else: # Format and extension are unknown
                format = ''
                ext = ''
            
            if cb.timestamp_label:
                date_string = 't' + cb.timestamp_label.isoformat()
            else:
                date_string = 's' + datetime.datetime.now().isoformat()
            
            filename = (args.dest_dir + r.collection_name + format + date_string + ext).translate(None, '/\\:*?"<>|')
            f = open(filename, 'w')
            f.write(cb.content)
            f.flush()
            f.close()
            print "Wrote Content Block to %s" % filename

if __name__ == "__main__":
    main()
