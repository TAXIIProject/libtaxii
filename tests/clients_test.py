#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import libtaxii as t
import libtaxii.clients as tc
import libtaxii.messages as tm

import datetime

#Create the TAXII HTTPS Client
client = tc.HttpClient()

#Uncomment to use HTTPS
#client.setUseHttps(True)

#Uncomment to use basic authentication
#client.setAuthType(tc.HttpClient.AUTH_BASIC)
#client.setAuthCredentials({'username':'some_username', 'password':'some_password'})

#Uncomment to use certificate-based authentication
#client.setAuthType(tc.HttpClient.AUTH_CERT)
#client.setAuthCredentials({'key_file': 'key_filename', 'cert_file': 'cert_filename'})

#Create the poll request
poll_request1 = tm.PollRequest(message_id = tm.generate_message_id(),
                               feed_name = 'TheFeedToPoll',
                               subscription_id = 'SubsId012',
                               exclusive_begin_timestamp_label = datetime.datetime.now(),
                               inclusive_end_timestamp_label = datetime.datetime.now(),
                               content_bindings = [])

#Call through a proxy:
proxy_host = 'proxyname'
proxy_port = 80
service_url = 'http://example.iana.org/servicepath/'
http_response = client.callTaxiiService(proxy_host, service_url, t.VID_TAXII_XML_10, poll_request1.to_xml(), port=proxy_port)

#Call without a proxy
#http_response = client.callTaxiiService('example.com', '/servicepath/', t.VID_TAXII_XML_10, poll_request1.to_xml())

taxii_message = t.get_message_from_http_response(http_response,
                                                 poll_request1.message_id)
print(taxii_message.to_xml())