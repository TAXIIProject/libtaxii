#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

from libtaxii.scripts import TaxiiScript
import libtaxii as t
import libtaxii.messages_10 as tm10
import os
from re import sub as resub


class PollClient10Script(TaxiiScript):
    taxii_version = t.VID_TAXII_XML_10
    parser_description = 'TAXII 1.0 Poll Client'
    path = '/services/poll/'

    def get_arg_parser(self, *args, **kwargs):
        parser = super(PollClient10Script, self).get_arg_parser(*args, **kwargs)
        parser.add_argument("--feed", dest="feed", default="default", help="Data Collection to poll. Defaults to 'default'.")
        parser.add_argument("--begin-timestamp", dest="begin_ts", default=None, help="The begin timestamp (format: YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm) for the poll request. Defaults to None.")
        parser.add_argument("--end-timestamp", dest="end_ts", default=None, help="The end timestamp (format: YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm) for the poll request. Defaults to None.")
        parser.add_argument("--subscription-id", dest="subs_id", default=None, help="The subscription ID to use. Defaults to None")
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
            print "Unable to parse timestamp value. Timestamp should include both date and time information along with a timezone or UTC offset (e.g., YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm). Aborting poll."
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
            for cb in response.content_blocks:
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

                filename = (    response.collection_name.lstrip(".") +
                                format +
                                resub(r"[^a-zA-Z0-9]", "_", date_string) + ext
                                ).translate(None, '/\\:*?"<>|')
                filename = os.path.join(args.dest_dir, filename)

                f = open(filename, 'w')
                f.write(cb.content)
                f.flush()
                f.close()
                print "Wrote Content Block to %s" % filename


def main():
    script = PollClient10Script()
    script()

if __name__ == "__main__":
    main()
