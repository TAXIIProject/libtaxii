#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import datetime

from dateutil.tz import tzutc

import libtaxii as t
import libtaxii.clients as tc
import libtaxii.messages as tm


#Create the TAXII HTTPS Client
client = tc.HttpClient()

#Uncomment to use HTTPS
client.setUseHttps(True)

#Uncomment to use basic authentication
#client.setAuthType(tc.HttpClient.AUTH_BASIC)
#client.setAuthCredentials({'username':'some_username', 'password':'some_password'})

#Uncomment to use certificate-based authentication
client.setAuthType(tc.HttpClient.AUTH_CERT)
client.setAuthCredentials({'key_file': 'keyfile',
                           'cert_file': 'certfile'})

#Uncomment to set a proxy
#client.setProxy(tc.HttpClient.PROXY_HTTP, 'http://proxy.company.com:80')

#Create the poll request
poll_request1 = tm.PollRequest(message_id=tm.generate_message_id(), feed_name='TheFeedToPoll')

#Call without a proxy
http_response = client.callTaxiiService2('hostname', '/poll_service_path/', t.VID_TAXII_XML_10, poll_request1.to_xml())

print http_response.__class__.__name__

taxii_message = t.get_message_from_http_response(http_response,
                                                 poll_request1.message_id)
print(taxii_message.to_xml())
