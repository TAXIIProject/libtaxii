

#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

from libtaxii.scripts import TaxiiScript, add_poll_response_args
import libtaxii.messages_10 as tm10
import dateutil.parser
import datetime
import sys
import os
from libtaxii.common import gen_filename
from libtaxii.constants import *

class PollClient10Script(TaxiiScript):
    taxii_version = VID_TAXII_XML_10
    parser_description = 'The TAXII 1.0 Poll Client sends a Poll Request message to a TAXII Server and then' \
                         'prints the Poll Response message to standard out, saving the Content Blocks to disk (' \
                         'depending on the command line arguments).'
    path = '/services/poll/'

    def get_arg_parser(self, *args, **kwargs):
        parser = super(PollClient10Script, self).get_arg_parser(*args, **kwargs)
        parser.add_argument("--feed",
                            dest="feed",
                            default="default",
                            help="Data Collection to poll. Defaults to 'default'.")
        parser.add_argument("--begin-timestamp",
                            dest="begin_ts",
                            default=None,
                            help="The begin timestamp (format: YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm) for the poll "
                                 "request. Defaults to None.")
        parser.add_argument("--end-timestamp",
                            dest="end_ts",
                            default=None,
                            help="The end timestamp (format: YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm) for the poll request. "
                                 "Defaults to None.")
        parser.add_argument("--subscription-id",
                            dest="subs_id",
                            default=None,
                            help="The subscription ID to use. Defaults to None")
        add_poll_response_args(parser)
        return parser

    def create_request_message(self, args):
        try:
            if args.begin_ts:
                begin_ts = dateutil.parser.parse(args.begin_ts)
                if not begin_ts.tzinfo:
                    raise ValueError
            else:
                begin_ts = None

            if args.end_ts:
                end_ts = dateutil.parser.parse(args.end_ts)
                if not end_ts.tzinfo:
                    raise ValueError
            else:
                end_ts = None
        except ValueError:
            print("Unable to parse timestamp value. Timestamp should include both date and time information along " \
                  "with a timezone or UTC offset (e.g., YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm). Aborting poll.")
            sys.exit()

        poll_req = tm10.PollRequest(message_id=tm10.generate_message_id(),
                                    feed_name=args.feed,
                                    exclusive_begin_timestamp_label=begin_ts,
                                    inclusive_end_timestamp_label=end_ts,
                                    subscription_id=args.subs_id)
        return poll_req

    def handle_response(self, response, args):
        super(PollClient10Script, self).handle_response(response, args)
        if response.message_type == tm10.MSG_POLL_RESPONSE:
            self.write_cbs_from_poll_response_10(response, dest_dir=args.dest_dir, write_type_=args.write_type)


def main():
    script = PollClient10Script()
    script()

if __name__ == "__main__":
    main()
