from __future__ import unicode_literals

from lxml import etree

from libtaxii.clients import VerifiableHTTPSConnection


def test_connection():
    # This is a basic test just to confirm that we pass the right arguments
    # in the right order to a (non-TAXII) HTTPS server

    conn = VerifiableHTTPSConnection("https://httpbin.org/", 443)
