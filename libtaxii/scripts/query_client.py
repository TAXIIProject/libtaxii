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
    parser = scripts.get_base_parser("Poll Query Client", path="/services/poll/")
    parser.add_argument("--collection", dest="collection", default="default_queryable", help="Data Collection to poll. Defaults to 'default_queryable'.")
    parser.add_argument("--allow-asynch", dest="allow_asynch", default=True, help="Indicate whether or not the client support Asynchronous Polling. Defaults to True")
    parser.add_argument("--tev", dest="tev", default=t.CB_STIX_XML_111, help="Indicate which Targeting Expression Vocabulary is being used. Defaults to STIX XML 1.1.1")
    parser.add_argument("--target", dest="target", default="**/@id", help="The targeting expression to use. Defaults to **/@id (Any id, anywhere).")
    parser.add_argument("--rel", dest="relationship", default="equals", help="The relationship to use (e.g., equals). Defaults to equals.")
    parser.add_argument("--cm", dest="capability_module", default=None, help="The capability module being used. If not specified, the script will attempt to infer the correct capability module")
    # Parameters - optional depending on what relationship is chosen
    parser.add_argument("--value", dest=tdq.P_VALUE, default=None, help="The value to look for. Required (or not) and allowed values depend on the relationship.")
    parser.add_argument("--match-type", dest=tdq.P_MATCH_TYPE, default=None, choices=['case_sensitive_string', 'case_insensitive_string', 'number'], help="The match type. Required (or not) and allowed values depend on the relationship.")
    parser.add_argument("--case-sensitive", dest=tdq.P_CASE_SENSITIVE, default=None, choices=[True, False], help="Whether the match is case sensitive. Required (or not) and allowed values depend on the relationship.")

    args = parser.parse_args()

    capability_module = None
    relationship = None
    for cm_id, cm in tdq.capability_modules.iteritems():
        relationship = cm.relationships.get(args.relationship.lower(), None)

        if args.capability_module:  # The user specified a value - try to match on that
            if cm_id == args.capability_module:
                if not relationship:  # If the specified relationship is not in the capability module, that's an error
                    raise ValueError('Relationship (%s) not found in capability module (%s). Valid relationships are: %s' %
                                     (args.relationship, args.capability_module, cm.relationships.keys()))
                capability_module = cm
        elif relationship:  # User did not specify a value for capability_module, attempt to infer
            capability_module = cm

        if capability_module:
            break

    if not capability_module:
        raise ValueError("Unable to map relationship to Capability Module: %s" % args.relationship)

    # Make sure all required params are set and
    # no unused params are set

    tdq_params = {}

    for parameter in tdq.P_NAMES:
        param_obj = relationship.parameters.get(parameter, None)  # Will either be a parameter object or None
        param_value = getattr(args, parameter)  # Will either be a value or None

        if param_obj and not param_value:
            raise ValueError('The parameter "%s" is needed and was not specified. Specify using --%s <value>' % (parameter, parameter.replace('_', '-')))
        if param_value and not param_obj:
            raise ValueError('The parameter %s was specified and is not needed' % parameter)

        if param_obj:
            param_obj.verify(param_value)
            tdq_params[parameter] = param_value

    test = tdq.Test(capability_id=capability_module.capability_module_id,
                    relationship=relationship.name,
                    parameters=tdq_params)

    criterion = tdq.Criterion(target=args.target, test=test)

    criteria = tdq.Criteria(operator=tdq.OP_AND, criterion=[criterion])

    q = tdq.DefaultQuery(args.tev, criteria)

    poll_req = tm11.PollRequest(message_id=tm11.generate_message_id(),
                                collection_name=args.collection,
                                poll_parameters=tm11.PollRequest.PollParameters(allow_asynch=args.allow_asynch, query=q))

    print "Request:\n"
    if args.xml_output is False:
        print poll_req.to_text()
    else:
        print poll_req.to_xml(pretty_print=True)

    client = scripts.create_client(args)
    resp = client.call_taxii_service2(args.host, args.path, t.VID_TAXII_XML_11, poll_req.to_xml(pretty_print=True), args.port)
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
            else:  # Format and extension are unknown
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
