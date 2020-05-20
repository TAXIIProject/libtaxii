from __future__ import unicode_literals

from lxml import etree

from libtaxii.common import parse_xml_string
from libtaxii.constants import CB_STIX_XML_111
from libtaxii.messages_10 import ContentBlock as ContentBlock10
from libtaxii.messages_11 import get_message_from_xml, ContentBlock as ContentBlock11


discovery_request_with_encoding_bytes = b"""<?xml version="1.0" encoding="UTF-8" ?>
<taxii_11:Discovery_Request xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1"
    xsi:schemaLocation="http://taxii.mitre.org/messages/taxii_xml_binding-1.1 http://taxii.mitre.org/messages/taxii_xml_binding-1.1"
    message_id="331bf15a-76a0-4e29-8444-6e986e514e29" />
"""

discovery_request_with_encoding_unicode = """<?xml version="1.0" encoding="UTF-8" ?>
<taxii_11:Discovery_Request xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1"
    xsi:schemaLocation="http://taxii.mitre.org/messages/taxii_xml_binding-1.1 http://taxii.mitre.org/messages/taxii_xml_binding-1.1"
    message_id="331bf15a-76a0-4e29-8444-6e986e514e29" />
"""

stix_package_bytes = b"""<?xml version="1.0" encoding="UTF-8"?>
<stix:STIX_Package xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:stix="http://stix.mitre.org/stix-1" xmlns:example="http://example.com/"
  id="example:Indicator-ba1d406e-937c-414f-9231-6e1dbe64fe8b" version="1.1.1">
  <stix:STIX_Header>
    <stix:Description>Test Package</stix:Description>
  </stix:STIX_Header>
</stix:STIX_Package>
"""

stix_package_unicode = """<?xml version="1.0" encoding="UTF-8"?>
<stix:STIX_Package xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:stix="http://stix.mitre.org/stix-1" xmlns:example="http://example.com/"
  id="example:Indicator-ba1d406e-937c-414f-9231-6e1dbe64fe8b" version="1.1.1">
  <stix:STIX_Header>
    <stix:Description>Test Package</stix:Description>
  </stix:STIX_Header>
</stix:STIX_Package>
"""


def test_parsing_byte_string_with_encoding():
    x = parse_xml_string(b"""<?xml version="1.0" encoding="UTF-8" ?><foo />""")
    assert x.tag == "foo"


def test_parsing_byte_string_without_encoding():
    x = parse_xml_string(b"""<?xml version="1.0" ?><bar />""")
    assert x.tag == "bar"


def test_parsing_unicode_string_with_encoding():
    x = parse_xml_string("""<?xml version="1.0" encoding="UTF-8" ?><baz />""")
    assert x.tag == "baz"


def test_parsing_unicode_string_without_encoding():
    x = parse_xml_string("""<?xml version="1.0" ?><quz />""")
    assert x.tag == "quz"


def test_get_xml_from_byte_string():
    req = get_message_from_xml(discovery_request_with_encoding_bytes)

    assert req is not None
    assert req.message_id == "331bf15a-76a0-4e29-8444-6e986e514e29"


def test_get_xml_from_unicode_string():
    req = get_message_from_xml(discovery_request_with_encoding_unicode)

    assert req is not None
    assert req.message_id == "331bf15a-76a0-4e29-8444-6e986e514e29"


def test_content_block_11_bytes():
    content_block = ContentBlock11(CB_STIX_XML_111, stix_package_bytes)

    assert content_block.content_is_xml is True
    assert b"Indicator-ba1d406e-937c-414f-9231-6e1dbe64fe8b" in content_block.content


def test_content_block_11_unicode():
    content_block = ContentBlock11(CB_STIX_XML_111, stix_package_unicode)

    assert content_block.content_is_xml is True
    # Content is always in bytes
    assert b"Indicator-ba1d406e-937c-414f-9231-6e1dbe64fe8b" in content_block.content


def test_content_block_10_bytes():
    content_block = ContentBlock10(CB_STIX_XML_111, stix_package_bytes)

    assert content_block.content_is_xml is True
    assert isinstance(content_block._content, etree._Element)
    assert b"Indicator-ba1d406e-937c-414f-9231-6e1dbe64fe8b" in content_block.content


def test_content_block_10_unicode():
    content_block = ContentBlock10(CB_STIX_XML_111, stix_package_unicode)

    assert content_block.content_is_xml is True
    # Content is always in bytes
    assert isinstance(content_block._content, etree._Element)
    assert b"Indicator-ba1d406e-937c-414f-9231-6e1dbe64fe8b" in content_block.content
