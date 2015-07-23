
#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import libtaxii.taxii_default_query as tdq
from libtaxii.constants import *
from .poll_client import PollClient11Script


class QueryClient11Script(PollClient11Script):
    parser_description = "The TAXII 1.1 Query Client sends a Poll Request message to a TAXII Server (queries are " \
                         "contained in Poll Request messages) and prints out the resulting Poll Response message" \
                         "to standard out. The Content Blocks are saved to disk (depending on the command line" \
                         "options)."
    path = '/services/poll/'

    def get_arg_parser(self, *args, **kwargs):
        parser = super(QueryClient11Script, self).get_arg_parser(*args, **kwargs)
        parser.add_argument("--tev",
                            dest="tev",
                            default=CB_STIX_XML_111,
                            help="Indicate which Targeting Expression Vocabulary is being used. Defaults to "
                                 "STIX XML 1.1.1")
        parser.add_argument("--target",
                            dest="target",
                            default="**/@id",
                            help="The targeting expression to use. Defaults to **/@id (Any id, anywhere).")
        parser.add_argument("--rel",
                            dest="relationship",
                            default="equals",
                            help="The relationship to use (e.g., equals). Defaults to equals.")
        parser.add_argument("--cm",
                            dest="capability_module",
                            default=CM_CORE,
                            help="The capability module to use. Defaults to CORE.")
        # Parameters - optional depending on what relationship is chosen
        parser.add_argument("--value",
                            dest=tdq.P_VALUE,
                            default=None,
                            help="The value to look for. Required (or not) and allowed values depend "
                                 "on the relationship.")
        parser.add_argument("--match-type",
                            dest=tdq.P_MATCH_TYPE,
                            default='case_insensitive_string',
                            choices=['case_sensitive_string', 'case_insensitive_string', 'number'],
                            help="The match type. Required (or not) and allowed values depend on the relationship. "
                                 "Defaults to \'case_insensitive_string\'")
        parser.add_argument("--case-sensitive",
                            dest=tdq.P_CASE_SENSITIVE,
                            default=None,
                            choices=[True, False],
                            help="Whether the match is case sensitive. Required (or not) and allowed values "
                                 "depend on the relationship. Defaults to \'None\'")
        return parser

    def create_request_message(self, args):
        msg = super(QueryClient11Script, self).create_request_message(args)
        if args.subscription_id is not None:
            return msg  # Query goes in Poll Parameters, which can't be specified with a subscription

        capability_module = tdq.capability_modules.get(args.capability_module, None)
        if capability_module is None:
            raise ValueError("Unknown Capability Module specified: %s" % args.capability_module)

        relationship = capability_module.relationships.get(args.relationship, None)
        if relationship is None:
            raise ValueError("Unknown Relationship: %s" % args.relationship)

        params = {}

        for parameter in tdq.P_NAMES:
            param_obj = relationship.parameters.get(parameter, None)  # Will either be a parameter object or None
            param_value = getattr(args, parameter)  # Will either be a value or None

            if param_obj and not param_value:
                raise ValueError('The parameter "%s" is needed and was not specified. Specify using --%s <value>' %
                                 (parameter, parameter.replace('_', '-')))
            if param_value and not param_obj:
                raise ValueError('The parameter %s was specified and is not needed' % parameter)

            if param_obj:
                param_obj.verify(param_value)
                params[parameter] = param_value

        test = tdq.Test(capability_id=capability_module.capability_module_id,
                        relationship=relationship.name,
                        parameters=params)

        criterion = tdq.Criterion(target=args.target, test=test)
        criteria = tdq.Criteria(operator=OP_AND, criterion=[criterion])
        q = tdq.DefaultQuery(args.tev, criteria)
        msg.poll_parameters.query = q

        return msg



def main():
    script = QueryClient11Script()
    script()

if __name__ == "__main__":
    main()
