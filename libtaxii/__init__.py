#Copyright (C) 2013 - The MITRE Corporation
#For license information, see the LICENSE.txt file

### Contributors ###
#Contributors: If you would like, add your name to the list, alphabetically by last name
#
# Mark Davidson - mdavidson@mitre.org
#

import libtaxii.messages as tm
import libtaxii.clients as tc

import httplib, urllib

#TAXII Version IDs
VID_TAXII_SERVICES_10 = 'urn:taxii.mitre.org:services:1.0'
VID_TAXII_XML_10 = 'urn:taxii.mitre.org:message:xml:1.0'
VID_TAXII_HTTP_10 = 'urn:taxii.mitre.org:protocol:http:1.0'
VID_TAXII_HTTPS_10 = 'urn:taxii.mitre.org:protocol:https:1.0'

#TAXII Content Bindings
CB_STIX_XML_10 = 'urn:stix.mitre.org:xml:1.0'
CB_CAP_11 = 'urn:oasis:names:tc:emergency:cap:1.1'
CB_XENC_122002 = 'http://www.w3.org/2001/04/xmlenc#'

#http_response - an httplib http_response object
#in_response_to - a string containing the default value for in_response_to
#
# This function parses the HTTP Response by reading the X-TAXII-Content-Type
# HTTP header to determine if the message binding is supported. If the 
# X-TAXII-Content-Type header is present and the value indicates a supported 
# Message Binidng, this function will attempt to parse the HTTP Response body.
# 
# If the X-TAXII-Content-Type header is not present, this function will attempt
# to build a Failure Status Message per the HTTP Binding 1.0 specification.
#
# If the X-TAXII-Content-Type header is present, but indicates an unsupported 
# Message Binding, this function will raise a ValueError.
def get_message_from_http_response(http_response, in_response_to):
    if isinstance(http_response, httplib.HTTPResponse):
        return get_message_from_httplib_http_response(http_response, in_response_to)
    elif isinstance(http_response, urllib.addinfourl):
        return get_message_from_urllib_addinfourl(http_response, in_response_to)
    else:
        raise ValueError('Unsupported response type: %s.' % http_response.__class__.__name__)


def get_message_from_urllib_addinfourl(http_response, in_response_to):
    taxii_content_type = http_response.info().getheader('X-TAXII-Content-Type')
    response_message = http_response.read()
    
    if taxii_content_type is None:#Treat it as a Failure Status Message, per the spec
        
        message = []
        header_tuples = http_response.getheaders()
        for k, v in header_tuples:
            message.append(k + ': ' + v + '\r\n')
        message.append('\r\n')
        message.append(response_message)
        
        m = ''.join(message)
        
        return tm.StatusMessage(message_id = '0', in_response_to = in_response_to, status_type = tm.ST_FAILURE, message = m)
    
    elif taxii_content_type == VID_TAXII_XML_10:#It's a TAXII XML 1.0 message
        return tm.get_message_from_xml(response_message)
    else:
        raise ValueError('Unsupported X-TAXII-Content-Type: %s' % taxii_content_type) 
        
    return None

def get_message_from_httplib_http_response(http_response, in_response_to):
    taxii_content_type = http_response.getheader('X-TAXII-Content-Type')
    response_message = http_response.read()
    
    if taxii_content_type is None:#Treat it as a Failure Status Message, per the spec
        
        message = []        
        header_tuples = http_response.getheaders()
        for k, v in header_tuples:
            message.append(k + ': ' + v + '\r\n')
        message.append('\r\n')
        message.append(response_message)
        
        m = ''.join(message)
        
        return tm.StatusMessage(message_id = '0', in_response_to = in_response_to, status_type = tm.ST_FAILURE, message = m)
        
    elif taxii_content_type == VID_TAXII_XML_10:#It's a TAXII XML 1.0 message
        return tm.get_message_from_xml(response_message)
    else:
        raise ValueError('Unsupported X-TAXII-Content-Type: %s' % taxii_content_type)
    
    return None
