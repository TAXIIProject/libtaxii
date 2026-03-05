from http.client import HTTPResponse
from urllib.error import HTTPError

import pytest

import libtaxii
from libtaxii.constants import VID_TAXII_XML_10, VID_TAXII_XML_11, VID_CERT_EU_JSON_10
import libtaxii.clients
import libtaxii.messages


IN_RESPONSE_TO = "test in_response_to value"
TAXII_CONTENT_TYPE = libtaxii.constants.VID_TAXII_XML_11
TEST_MESSAGE_ID = "test message id"

MESSAGES = {
    VID_TAXII_XML_10: (
        '<taxii:Discovery_Request xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1" message_id="1"/>',
        libtaxii.messages_10.DiscoveryRequest(message_id='1')
    ),
    VID_TAXII_XML_11: (
        '<taxii_11:Discovery_Request xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" message_id="non-ascii message id Ħ"/>',
        libtaxii.messages_11.DiscoveryRequest(message_id='non-ascii message id Ħ'),
    ),
    VID_CERT_EU_JSON_10: (
        '{"extended_headers": {}, "message_type": "Discovery_Request", "message_id": "1"}',
        libtaxii.messages_10.DiscoveryRequest(message_id='1')
    )
}


@pytest.mark.parametrize('taxii_content_type', MESSAGES.keys())
def test_httplib_http_response(taxii_content_type, httpserver):
    content, expected_message = MESSAGES[taxii_content_type]

    httpserver.expect_request("/poll_service_path/").respond_with_data(
        content.encode('ISO-8859-3'),
        content_type="application/xml; charset=ISO-8859-3",
        headers={"X-TAXII-Content-Type": taxii_content_type}
    )

    client = libtaxii.clients.HttpClient()
    http_response = client.call_taxii_service2(httpserver.host, '/poll_service_path/', libtaxii.constants.VID_TAXII_XML_10, b"", port=httpserver.port)
    assert isinstance(http_response, HTTPResponse)

    message = libtaxii.get_message_from_http_response(http_response, IN_RESPONSE_TO)
    print(message.message_id)
    assert message == expected_message


@pytest.mark.parametrize('taxii_content_type', MESSAGES.keys())
def test_httplib_http_response_error(taxii_content_type, httpserver):
    content, expected_message = MESSAGES[taxii_content_type]

    httpserver.expect_request("/poll_service_path/").respond_with_data(
        content.encode('ISO-8859-3'),
        status=500,
        content_type="application/xml; charset=ISO-8859-3",
        headers={"X-TAXII-Content-Type": taxii_content_type}
    )

    client = libtaxii.clients.HttpClient()
    http_response = client.call_taxii_service2(httpserver.host, '/poll_service_path/', libtaxii.constants.VID_TAXII_XML_10, b"", port=httpserver.port)
    assert isinstance(http_response, HTTPError)

    message = libtaxii.get_message_from_http_response(http_response, IN_RESPONSE_TO)
    assert message == expected_message


def test_httplib_http_response_no_taxii_content_type(httpserver):
    httpserver.expect_request("/poll_service_path/").respond_with_data(
        "some content".encode('ISO-8859-3'),
        content_type="application/xml; charset=ISO-8859-3",
    )

    client = libtaxii.clients.HttpClient()
    http_response = client.call_taxii_service2(httpserver.host, '/poll_service_path/', libtaxii.constants.VID_TAXII_XML_10, b"", port=httpserver.port)
    message = libtaxii.get_message_from_http_response(http_response, IN_RESPONSE_TO)

    assert isinstance(message, libtaxii.messages_11.StatusMessage)
    assert message.in_response_to == IN_RESPONSE_TO
    assert message.message_id == '0'

    server = http_response.headers.get("Server")
    date = http_response.headers.get("Date")
    assert message.message == (
        f'''Server: {server}\r\n'''
        f'''Date: {date}\r\n'''
        '''Content-Type: application/xml; charset=ISO-8859-3\r\n'''
        '''Content-Length: 12\r\n'''
        '''Connection: close\r\n'''
        '''\r\n'''
        '''some content'''
    )


def test_httplib_http_response_error_no_taxii_content_type(httpserver):
    httpserver.expect_request("/poll_service_path/").respond_with_data(
        "some content".encode('ISO-8859-3'),
        status=500,
        content_type="application/xml; charset=ISO-8859-3",
    )

    client = libtaxii.clients.HttpClient()
    http_response = client.call_taxii_service2(httpserver.host, '/poll_service_path/', libtaxii.constants.VID_TAXII_XML_10, b"", port=httpserver.port)
    assert isinstance(http_response, HTTPError)

    message = libtaxii.get_message_from_http_response(http_response, IN_RESPONSE_TO)
    assert isinstance(message, libtaxii.messages_11.StatusMessage)
    assert message.in_response_to == IN_RESPONSE_TO
    assert message.message_id == '0'

    server = http_response.headers.get("Server")
    date = http_response.headers.get("Date")
    assert message.message == (
        f'''HTTP Error 500: INTERNAL SERVER ERROR\r\n'''
        f'''Server: {server}\r\n'''
        f'''Date: {date}\r\n'''
        '''Content-Type: application/xml; charset=ISO-8859-3\r\n'''
        '''Content-Length: 12\r\n'''
        '''Connection: close\r\n'''
        '''\r\n'''
        '''some content'''
    )


