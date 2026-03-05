# Copyright (c) 2017, The MITRE Corporation
# For license information, see the LICENSE.txt file

"""
The main libtaxii module
"""

from urllib.error import HTTPError

import libtaxii.messages_10 as tm10
import libtaxii.messages_11 as tm11
from .constants import *

from .version import __version__  # noqa


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
        in_response_to (str): the default value for in_response_to
    """

    taxii_content_type = http_response.getheader('X-TAXII-Content-Type')
    encoding = http_response.headers.get_content_charset() or 'utf-8'

    response_message = http_response.read()

    if taxii_content_type is None:
        if isinstance(http_response, HTTPError):
            m = str(http_response) + '\r\n'
        else:
            m = ''
        for header, value in http_response.headers.items():
            m += f'{header}: {value}\r\n'
        m += '\r\n'
        m += response_message.decode(encoding, 'replace')

        return tm11.StatusMessage(message_id='0', in_response_to=in_response_to, status_type=ST_FAILURE, message=m)
    elif taxii_content_type == VID_TAXII_XML_10:  # It's a TAXII XML 1.0 message
        return tm10.get_message_from_xml(response_message, encoding)
    elif taxii_content_type == VID_TAXII_XML_11:  # It's a TAXII XML 1.1 message
        return tm11.get_message_from_xml(response_message, encoding)
    elif taxii_content_type == VID_CERT_EU_JSON_10:
        return tm10.get_message_from_json(response_message, encoding)
    else:
        raise ValueError('Unsupported X-TAXII-Content-Type: %s' % taxii_content_type)
