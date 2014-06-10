#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import sys

import argparse
import dateutil.parser

import libtaxii as t
import libtaxii.messages_10 as tm10
import libtaxii.clients as tc


def main():
    parser = argparse.ArgumentParser(description="Poll Client")
    parser.add_argument("--host", dest="host", default="taxiitest.mitre.org", help="Host where the Poll Service is hosted. Defaults to taxiitest.mitre.org.")
    parser.add_argument("--port", dest="port", default="80", type=int, help="Port where the Poll Service is hosted. Defaults to 80.")
    parser.add_argument("--path", dest="path", default="/services/poll/", help="Path where the Poll Service is hosted. Defaults to /services/poll/.")
    parser.add_argument("--feed", dest="feed", default="default", help="Data Collection to poll. Defaults to 'default'.")
    parser.add_argument("--begin_timestamp", dest="begin_ts", default=None, help="The begin timestamp (format: YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm) for the poll request. Defaults to None.")
    parser.add_argument("--end_timestamp", dest="end_ts", default=None, help="The end timestamp (format: YYYY-MM-DDTHH:MM:SS.ssssss+/-hh:mm) for the poll request. Defaults to None.")
    parser.add_argument("--https", dest="https", default=False, type=bool, help="Whether or not to use HTTPS. Defaults to False")
    parser.add_argument("--cert", dest="cert", default=None, help="The file location of the certificate to use. Defaults to None.")
    parser.add_argument("--key", dest="key", default=None, help="The file location of the private key to use. Defaults to None.")
    parser.add_argument("--username", dest="username", default=None, help="The username to authenticate with. Defaults to None.")
    parser.add_argument("--pass", dest="password", default=None, help="The password to authenticate with. Defaults to None.")
    parser.add_argument("--proxy", dest="proxy", default='noproxy', help="A proxy to use (e.g., http://example.com:80/), or None to not use any proxy. Omit this to use the system proxy.")
    parser.add_argument("--subscription-id", dest="subs_id", default=None, help="The subscription ID to use. Defaults to None")
    args = parser.parse_args()

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

    poll_req_xml = poll_req.to_xml(pretty_print=True)
    print "Poll Request: \r\n", poll_req_xml
    client = tc.HttpClient()
    client.setUseHttps(args.https)
    client.setProxy(args.proxy)
    tls = (args.cert is not None and args.key is not None)
    basic = (args.username is not None and args.password is not None)
    if tls and basic:
        client.setAuthType(tc.HttpClient.AUTH_CERT_BASIC)
        client.setAuthCredentials({'key_file': args.key, 'cert_file': args.cert, 'username': args.username, 'password': args.password})
    elif tls:
        client.setAuthType(tc.HttpClient.AUTH_CERT)
        client.setAuthCredentials({'key_file': args.key, 'cert_file': args.cert})
    elif basic:
        client.setAuthType(tc.HttpClient.AUTH_BASIC)
        client.setAuthCredentials({'username': args.username, 'password': args.password})
        
    resp = client.callTaxiiService2(args.host, args.path, t.VID_TAXII_XML_10, poll_req_xml, args.port)
    response_message = t.get_message_from_http_response(resp, '0')
    print "Response Message: \r\n", response_message.to_xml(pretty_print=True)

if __name__ == "__main__":
    main()
