#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

from libtaxii.scripts import TaxiiScript
import libtaxii.messages_11 as tm11
import libtaxii as t

class PollClient11Script(TaxiiScript):
    parser_description = 'TAXII 1.1 Poll Client'
    path = '/services/poll/'
    
    def get_arg_parser(self, *args, **kwargs):
        parser = super(PollClient11Script, self).get_arg_parser(*args, **kwargs)
        parser.add_argument("--collection", dest="collection", default="default", help="Data Collection to poll. Defaults to 'default'.")
        parser.add_argument("--begin-timestamp", dest="begin_ts", default=None, help="The begin timestamp (format: YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm) for the poll request. Defaults to None.")
        parser.add_argument("--end-timestamp", dest="end_ts", default=None, help="The end timestamp (format: YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm) for the poll request. Defaults to None.")
        parser.add_argument("--subscription-id", dest="subscription_id", default=None, help="The Subscription ID for the poll request. Defaults to None.")
        parser.add_argument("--dest-dir", dest="dest_dir", default="", help="The directory to save Content Blocks to. Defaults to the current directory.")
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
        
        create_kwargs = {'message_id': tm11.generate_message_id(),
                         'collection_name': args.collection,
                         'exclusive_begin_timestamp_label': begin_ts,
                         'inclusive_end_timestamp_label': end_ts}
        
        if args.subscription_id:
            create_kwargs['subscription_id'] = args.subscription_id
        else:
            create_kwargs['poll_parameters'] = tm11.PollRequest.PollParameters()
        poll_req = tm11.PollRequest(**create_kwargs)
        return poll_req
    
    def handle_response(self, response, args):
        super(PollClient11Script, self).handle_response(response, args)
        if response.more:
            print "This response has More=True, to request additional parts, use the following command:"
            print "  fulfillment_client --collection %s --result-id %s --result-part-number %s\r\n" % \
                     (response.collection_name, response.result_id, response.result_part_number + 1)
        if response.message_type == tm11.MSG_POLL_RESPONSE:
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
                else: # Format and extension are unknown
                    format = ''
                    ext = ''
                
                if cb.timestamp_label:
                    date_string = 't' + cb.timestamp_label.isoformat()
                else:
                    date_string = 's' + datetime.datetime.now().isoformat()
                
                filename = (args.dest_dir + response.collection_name + format + date_string + ext).translate(None, '/\\:*?"<>|')
                f = open(filename, 'w')
                f.write(cb.content)
                f.flush()
                f.close()
                print "Wrote Content Block to %s" % filename

def main():
    script = PollClient11Script()
    script()

if __name__ == "__main__":
    main()
