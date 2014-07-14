# Copyright (C) 2014 - The MITRE Corporation
# For license information, see the LICENSE.txt file

# Contributors:
# * Alex Ciobanu - calex@cert.europa.eu
# * Mark Davidson - mdavidson@mitre.org

"""
The main libtaxii module
"""

__version__ = "1.1.102"

import httplib
import urllib
import urllib2

import libtaxii.messages_10 as tm10
import libtaxii.messages_11 as tm11
import libtaxii.clients as tc

### TAXII Version IDs ###

#: Version ID for the TAXII Services Specification 1.0
VID_TAXII_SERVICES_10 = 'urn:taxii.mitre.org:services:1.0'
#: Version ID for the TAXII Services Specification 1.1
VID_TAXII_SERVICES_11 = 'urn:taxii.mitre.org:services:1.1'
#: Version ID for the TAXII XML Message Binding Specification 1.0
VID_TAXII_XML_10 = 'urn:taxii.mitre.org:message:xml:1.0'
#: Version ID for the TAXII XML Message Binding Specification 1.1
VID_TAXII_XML_11 = 'urn:taxii.mitre.org:message:xml:1.1'
#: Version ID for the TAXII HTTP Protocol Binding Specification 1.0
VID_TAXII_HTTP_10 = 'urn:taxii.mitre.org:protocol:http:1.0'
#: Version ID for the TAXII HTTPS Protocol Binding Specification 1.0
VID_TAXII_HTTPS_10 = 'urn:taxii.mitre.org:protocol:https:1.0'

# Third Party Version IDs
#: Version ID for the CERT EU JSON Message Binding
VID_CERT_EU_JSON_10 = 'urn:cert.europa.eu:message:json:1.0'


### TAXII Content Bindings ###

#: Content Binding ID for STIX XML 1.0
CB_STIX_XML_10 = 'urn:stix.mitre.org:xml:1.0'
#: Content Binding ID for STIX XML 1.0.1
CB_STIX_XML_101 = 'urn:stix.mitre.org:xml:1.0.1'
#: Content Binding ID for STIX XML 1.1
CB_STIX_XML_11 = 'urn:stix.mitre.org:xml:1.1'
#: Content Binding ID for STIX XML 1.1.1
CB_STIX_XML_111 = 'urn:stix.mitre.org:xml:1.1.1'
#: Content Binding ID for CAP 1.1
CB_CAP_11 = 'urn:oasis:names:tc:emergency:cap:1.1'
#: Content Binding ID for XML Encryption
CB_XENC_122002 = 'http://www.w3.org/2001/04/xmlenc#'
#: Content Binding ID for SMIME
CB_SMIME = 'application/x-pks7-mime'


def get_message_from_http_response(http_response, in_response_to):
    """Create a TAXII message from an HTTPResponse object.

    This function parses the :py:class:`httplib.HTTPResponse` by reading the
    X-TAXII-Content-Type HTTP header to determine if the message binding is
    supported. If the X-TAXII-Content-Type header is present and the value
    indicates a supported Message Binding, this function will attempt to parse
    the HTTP Response body.

    If the X-TAXII-Content-Type header is not present, this function will
    attempt to build a Failure Status Message per the HTTP Binding 1.0
    specification.

    If the X-TAXII-Content-Type header is present and indicates an unsupported
    Message Binding, this function will raise a ValueError.

    Args:
        http_response (httplib.HTTPResponse): the HTTP response to
            parse
        in_reponse_to (str): the default value for in_response_to
    """
    if isinstance(http_response, httplib.HTTPResponse):
        return get_message_from_httplib_http_response(http_response, in_response_to)
    elif isinstance(http_response, urllib2.HTTPError):
        return get_message_from_urllib2_httperror(http_response, in_response_to)
    elif isinstance(http_response, urllib.addinfourl):
        return get_message_from_urllib_addinfourl(http_response, in_response_to)
    else:
        raise ValueError('Unsupported response type: %s.' % http_response.__class__.__name__)


def get_message_from_urllib2_httperror(http_response, in_response_to):
    """ This function should not be called by libtaxii users directly. """
    taxii_content_type = http_response.info().getheader('X-TAXII-Content-Type')
    response_message = http_response.read()

    if taxii_content_type is None:
        m = str(http_response.info()) + '\r\n' + response_message
        return tm11.StatusMessage(message_id='0', in_response_to=in_response_to, status_type=tm11.ST_FAILURE, message=m)
    elif taxii_content_type == VID_TAXII_XML_10:  # It's a TAXII XML 1.0 message
        return tm10.get_message_from_xml(response_message)
    elif taxii_content_type == VID_TAXII_XML_11:  # It's a TAXII XML 1.1 message
        return tm11.get_message_from_xml(response_message)
    elif taxii_content_type == VID_CERT_EU_JSON_10:
        return tm10.get_message_from_json(response_message)
    else:
        raise ValueError('Unsupported X-TAXII-Content-Type: %s' % taxii_content_type)

    return None


def get_message_from_urllib_addinfourl(http_response, in_response_to):
    """ This function should not be called by libtaxii users directly. """
    taxii_content_type = http_response.info().getheader('X-TAXII-Content-Type')
    response_message = http_response.read()

    if taxii_content_type is None:  # Treat it as a Failure Status Message, per the spec

        message = []
        #header_tuples = http_response.getheaders()
        header_dict = http_response.info().dict.iteritems()
        for k, v in header_dict:  # header_tuples:
            message.append(k + ': ' + v + '\r\n')
        message.append('\r\n')
        message.append(response_message)

        m = ''.join(message)

        return tm11.StatusMessage(message_id='0', in_response_to=in_response_to, status_type=tm11.ST_FAILURE, message=m)

    elif taxii_content_type == VID_TAXII_XML_10:  # It's a TAXII XML 1.0 message
        return tm10.get_message_from_xml(response_message)
    elif taxii_content_type == VID_TAXII_XML_11:  # It's a TAXII XML 1.1 message
        return tm11.get_message_from_xml(response_message)
    elif taxii_content_type == VID_CERT_EU_JSON_10:
        return tm10.get_message_from_json(response_message)
    else:
        raise ValueError('Unsupported X-TAXII-Content-Type: %s' % taxii_content_type)

    return None


def get_message_from_httplib_http_response(http_response, in_response_to):
    """ This function should not be called by libtaxii users directly. """
    taxii_content_type = http_response.getheader('X-TAXII-Content-Type')
    response_message = http_response.read()

    if taxii_content_type is None:  # Treat it as a Failure Status Message, per the spec

        message = []
        header_tuples = http_response.getheaders()
        for k, v in header_tuples:
            message.append(k + ': ' + v + '\r\n')
        message.append('\r\n')
        message.append(response_message)

        m = ''.join(message)

        return tm11.StatusMessage(message_id='0', in_response_to=in_response_to, status_type=tm11.ST_FAILURE, message=m)

    elif taxii_content_type == VID_TAXII_XML_10:  # It's a TAXII XML 1.0 message
        return tm10.get_message_from_xml(response_message)
    elif taxii_content_type == VID_TAXII_XML_11:  # It's a TAXII XML 1.1 message
        return tm11.get_message_from_xml(response_message)
    else:
        raise ValueError('Unsupported X-TAXII-Content-Type: %s' % taxii_content_type)

    return None
