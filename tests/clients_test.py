#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import libtaxii.clients as tc
import libtaxii.messages as tm
import libtaxii as t

import datetime

#Create the TAXII HTTPS Client
client = tc.HttpClient()
client.setUseHttps(True)
client.setAuthType(tc.HttpClient.AUTH_BASIC)
client.setAuthCredentials({'username':'some_username', 'password':'some_password'})

#Create the poll request
poll_request_kwargs = {}
poll_request_kwargs['message_id'] = tm.generate_message_id()
poll_request_kwargs['feed_name'] = 'TheFeedToPoll'
poll_request_kwargs['subscription_id'] = 'SomeID'
poll_request_kwargs['exclusive_begin_timestamp'] = datetime.datetime.now()
poll_request_kwargs['inclusive_end_timestamp'] = datetime.datetime.now()
poll_request_kwargs['content_bindings'] = []

poll_request1 = tm.PollRequest(**poll_request_kwargs)

#Call the poll service
http_response = client.callTaxiiService('tspdev01.mitre.org', '/PathToService/', t.VID_TAXII_XML_10, poll_request1.to_xml())
taxii_response = get_message_from_http_response(http_response)
print http_response