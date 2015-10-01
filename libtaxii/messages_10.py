# Copyright (C) 2013 - The MITRE Corporation
# For license information, see the LICENSE.txt file

# Contributors:
# * Alex Ciobanu - calex@cert.europa.eu
# * Mark Davidson - mdavidson@mitre.org
# * Bryan Worrell - bworrell@mitre.org
# * Benjamin Yates - byates@dtcc.com

"""
Creating, handling, and parsing TAXII 1.0 messages.
"""

import six

try:
    import simplejson as json
except ImportError:
    import json
import os
import warnings

from lxml import etree

from .common import (parse, parse_datetime_string, append_any_content_etree, TAXIIBase,
                     get_required, get_optional, get_optional_text, parse_xml_string)
from .validation import do_check, uri_regex, check_timestamp_label, message_id_regex_10
from .constants import *


def validate_xml(xml_string):
    """
    Note that this function has been deprecated. Please see
    libtaxii.validators.SchemaValidator.

    Validate XML with the TAXII XML Schema 1.0.

    Args:
        xml_string (str): The XML to validate.

    Example:
        .. code-block:: python

            is_valid = tm10.validate_xml(message.to_xml())
    """

    warnings.warn('Call to deprecated function: libtaxii.messages_10.validate_xml()',
                  category=DeprecationWarning)

    etree_xml = parse_xml_string(xml_string)
    package_dir, package_filename = os.path.split(__file__)
    schema_file = os.path.join(package_dir, "xsd", "TAXII_XMLMessageBinding_Schema.xsd")
    taxii_schema_doc = parse(schema_file)
    xml_schema = etree.XMLSchema(taxii_schema_doc)
    valid = xml_schema.validate(etree_xml)
    if not valid:
        return xml_schema.error_log.last_error
    return valid


def get_message_from_xml(xml_string, encoding='utf_8'):
    """Create a TAXIIMessage object from an XML string.

    This function automatically detects which type of Message should be created
    based on the XML.

    Args:
        xml_string (str): The XML to parse into a TAXII message.

    Example:
        .. code-block:: python

            message_xml = message.to_xml()
            new_message = tm10.get_message_from_xml(message_xml)
    """
    decoded_string = xml_string.decode(encoding, 'replace')
    etree_xml = parse_xml_string(decoded_string)
    qn = etree.QName(etree_xml)
    if qn.namespace != ns_map['taxii']:
        raise ValueError('Unsupported namespace: %s' % qn.namespace)

    message_type = qn.localname

    if message_type == MSG_DISCOVERY_REQUEST:
        return DiscoveryRequest.from_etree(etree_xml)
    if message_type == MSG_DISCOVERY_RESPONSE:
        return DiscoveryResponse.from_etree(etree_xml)
    if message_type == MSG_FEED_INFORMATION_REQUEST:
        return FeedInformationRequest.from_etree(etree_xml)
    if message_type == MSG_FEED_INFORMATION_RESPONSE:
        return FeedInformationResponse.from_etree(etree_xml)
    if message_type == MSG_POLL_REQUEST:
        return PollRequest.from_etree(etree_xml)
    if message_type == MSG_POLL_RESPONSE:
        return PollResponse.from_etree(etree_xml)
    if message_type == MSG_STATUS_MESSAGE:
        return StatusMessage.from_etree(etree_xml)
    if message_type == MSG_INBOX_MESSAGE:
        return InboxMessage.from_etree(etree_xml)
    if message_type == MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST:
        return ManageFeedSubscriptionRequest.from_etree(etree_xml)
    if message_type == MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE:
        return ManageFeedSubscriptionResponse.from_etree(etree_xml)

    raise ValueError('Unknown message_type: %s' % message_type)


def get_message_from_dict(d):
    """Create a TAXIIMessage object from a dictonary.

    This function automatically detects which type of Message should be created
    based on the 'message_type' key in the dictionary.

    Args:
        d (dict): The dictionary to build the TAXII message from.

    Example:
        .. code-block:: python

            message_dict = message.to_dict()
            new_message = tm10.get_message_from_dict(message_dict)
    """
    if 'message_type' not in d:
        raise ValueError('message_type is a required field!')

    message_type = d['message_type']
    if message_type == MSG_DISCOVERY_REQUEST:
        return DiscoveryRequest.from_dict(d)
    if message_type == MSG_DISCOVERY_RESPONSE:
        return DiscoveryResponse.from_dict(d)
    if message_type == MSG_FEED_INFORMATION_REQUEST:
        return FeedInformationRequest.from_dict(d)
    if message_type == MSG_FEED_INFORMATION_RESPONSE:
        return FeedInformationResponse.from_dict(d)
    if message_type == MSG_POLL_REQUEST:
        return PollRequest.from_dict(d)
    if message_type == MSG_POLL_RESPONSE:
        return PollResponse.from_dict(d)
    if message_type == MSG_STATUS_MESSAGE:
        return StatusMessage.from_dict(d)
    if message_type == MSG_INBOX_MESSAGE:
        return InboxMessage.from_dict(d)
    if message_type == MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST:
        return ManageFeedSubscriptionRequest.from_dict(d)
    if message_type == MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE:
        return ManageFeedSubscriptionResponse.from_dict(d)

    raise ValueError('Unknown message_type: %s' % message_type)


def get_message_from_json(json_string, encoding='utf_8'):
    """Create a TAXIIMessage object from a JSON string.

    This function automatically detects which type of Message should be created
    based on the JSON.

    Args:
        json_string (str): The JSON to parse into a TAXII message.
    """
    decoded_string = json_string.decode(encoding, 'replace')
    return get_message_from_dict(json.loads(decoded_string))


class TAXIIBase10(TAXIIBase):
    version = VID_TAXII_XML_10


class DeliveryParameters(TAXIIBase10):

    """Delivery Parameters.

    Args:
        inbox_protocol (str): identifies the protocol to be used when pushing
            TAXII Data Feed content to a Consumer's TAXII Inbox Service
            implementation. **Required**
        inbox_address (str): identifies the address of the TAXII Daemon hosting
            the Inbox Service to which the Consumer requests content for this
            TAXII Data Feed to be delivered. **Required**
        delivery_message_binding (str): identifies the message binding to be
             used to send pushed content for this subscription. **Required**
        content_bindings (list of str): contains Content Binding IDs
            indicating which types of contents the Consumer requests to
            receive for this TAXII Data Feed. **Optional**
    """

    # TODO: Should the default arguments of these change? I'm not sure these are
    # actually optional

    def __init__(self, inbox_protocol=None, inbox_address=None,
                 delivery_message_binding=None, content_bindings=None):
        self.inbox_protocol = inbox_protocol
        self.inbox_address = inbox_address
        self.delivery_message_binding = delivery_message_binding
        self.content_bindings = content_bindings or []

    @property
    def sort_key(self):
        return self.inbox_address

    @property
    def inbox_protocol(self):
        return self._inbox_protocol

    @inbox_protocol.setter
    def inbox_protocol(self, value):
        do_check(value, 'inbox_protocol', regex_tuple=uri_regex)
        self._inbox_protocol = value

    @property
    def inbox_address(self):
        return self._inbox_address

    @inbox_address.setter
    def inbox_address(self, value):
        # TODO: Can inbox_address be validated?
        self._inbox_address = value

    @property
    def delivery_message_binding(self):
        return self._delivery_message_binding

    @delivery_message_binding.setter
    def delivery_message_binding(self, value):
        do_check(value, 'delivery_message_binding', regex_tuple=uri_regex)
        self._delivery_message_binding = value

    @property
    def content_bindings(self):
        return self._content_bindings

    @content_bindings.setter
    def content_bindings(self, value):
        do_check(value, 'content_bindings', regex_tuple=uri_regex)
        self._content_bindings = value

    def to_etree(self):
        xml = etree.Element('{%s}Push_Parameters' % ns_map['taxii'])

        if self.inbox_protocol is not None:
            pb = etree.SubElement(xml, '{%s}Protocol_Binding' % ns_map['taxii'])
            pb.text = self.inbox_protocol

        if self.inbox_address is not None:
            a = etree.SubElement(xml, '{%s}Address' % ns_map['taxii'])
            a.text = self.inbox_address

        if self.delivery_message_binding is not None:
            mb = etree.SubElement(xml, '{%s}Message_Binding' % ns_map['taxii'])
            mb.text = self.delivery_message_binding

        for binding in self.content_bindings:
            cb = etree.SubElement(xml, '{%s}Content_Binding' % ns_map['taxii'])
            cb.text = binding

        return xml

    def to_dict(self):
        d = {}

        if self.inbox_protocol is not None:
            d['inbox_protocol'] = self.inbox_protocol

        if self.inbox_address is not None:
            d['inbox_address'] = self.inbox_address

        if self.delivery_message_binding is not None:
            d['delivery_message_binding'] = self.delivery_message_binding

        d['content_bindings'] = []
        for binding in self.content_bindings:
            d['content_bindings'].append(binding)

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Push Parameters ===\n"
        s += line_prepend + "  Inbox Protocol: %s\n" % self.inbox_protocol
        s += line_prepend + "  Address: %s\n" % self.inbox_address
        s += line_prepend + "  Message Binding: %s\n" % self.delivery_message_binding
        if len(self.content_bindings) > 0:
            s += line_prepend + "  Content Bindings: Any Content\n"
        for cb in self.content_bindings:
            s += line_prepend + "  Content Binding: %s\n" % str(cb)

        return s

    @staticmethod
    def from_etree(etree_xml):

        inbox_protocol = get_optional_text(etree_xml, './taxii:Protocol_Binding', ns_map)
        inbox_address = get_optional_text(etree_xml, './taxii:Address', ns_map)
        delivery_message_binding = get_optional_text(etree_xml, './taxii:Message_Binding', ns_map)

        content_bindings = []
        for binding in etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map):
            content_bindings.append(binding.text)

        return DeliveryParameters(inbox_protocol, inbox_address, delivery_message_binding, content_bindings)

    @staticmethod
    def from_dict(d):
        return DeliveryParameters(**d)


class TAXIIMessage(TAXIIBase10):

    """Encapsulate properties common to all TAXII Messages (such as headers).

    This class is extended by each Message Type (e.g., DiscoveryRequest), with
    each subclass containing subclass-specific information
    """

    message_type = 'TAXIIMessage'

    def __init__(self, message_id, in_response_to=None, extended_headers=None):
        """Create a new TAXIIMessage

        Arguments:
        - message_id (string) - A value identifying this message.
        - in_response_to (string) - Contains the Message ID of the message to
          which this is a response.
        - extended_headers (dictionary) - A dictionary of name/value pairs for
          use as Extended Headers
        """
        self.message_id = message_id
        self.in_response_to = in_response_to
        if extended_headers is None:
            self.extended_headers = {}
        else:
            self.extended_headers = extended_headers

    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, value):
        do_check(value, 'message_id', regex_tuple=message_id_regex_10)
        self._message_id = value

    @property
    def in_response_to(self):
        return self._in_response_to

    @in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=message_id_regex_10, can_be_none=True)
        self._in_response_to = value

    @property
    def extended_headers(self):
        return self._extended_headers

    @extended_headers.setter
    def extended_headers(self, value):
        do_check(list(value.keys()), 'extended_headers.keys()', regex_tuple=uri_regex)
        self._extended_headers = value

    def to_etree(self):
        """Creates the base etree for the TAXII Message.

        Message-specific constructs must be added by each Message class. In
        general, when converting to XML, subclasses should call this method
        first, then create their specific XML constructs.
        """
        root_elt = etree.Element('{%s}%s' % (ns_map['taxii'], self.message_type), nsmap=ns_map)
        root_elt.attrib['message_id'] = str(self.message_id)

        if self.in_response_to is not None:
            root_elt.attrib['in_response_to'] = str(self.in_response_to)

        if len(self.extended_headers) > 0:
            eh = etree.SubElement(root_elt, '{%s}Extended_Headers' % ns_map['taxii'])

            for name, value in list(self.extended_headers.items()):
                h = etree.SubElement(eh, '{%s}Extended_Header' % ns_map['taxii'])
                h.attrib['name'] = name
                append_any_content_etree(h, value)
                # h.text = value
        return root_elt

    def to_xml(self, pretty_print=False):
        """Convert a message to XML.

        Subclasses shouldn't implement this method, as it is mainly a wrapper
        for cls.to_etree.
        """
        return etree.tostring(self.to_etree(), pretty_print=pretty_print)

    def to_dict(self):
        """Create the base dictionary for the TAXII Message.

        Message-specific constructs must be added by each Message class. In
        general, when converting to dictionary, subclasses should call this
        method first, then create their specific dictionary constructs.
        """
        d = {}
        d['message_type'] = self.message_type
        d['message_id'] = self.message_id
        if self.in_response_to is not None:
            d['in_response_to'] = self.in_response_to
        d['extended_headers'] = {}
        for k, v in six.iteritems(self.extended_headers):
            if isinstance(v, etree._Element) or isinstance(v, etree._ElementTree):
                v = etree.tostring(v)
            elif not isinstance(v, six.string_types):
                v = str(v)
            d['extended_headers'][k] = v

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "Message Type: %s\n" % self.message_type
        s += line_prepend + "Message ID: %s" % self.message_id
        if self.in_response_to:
            s += "; In Response To: %s" % self.in_response_to
        s += "\n"
        for k, v in six.iteritems(self.extended_headers):
            s += line_prepend + "Extended Header: %s = %s" % (k, v)

        return s

    @classmethod
    def from_etree(cls, src_etree, **kwargs):
        """Pulls properties of a TAXII Message from an etree.

        Message-specific constructs must be pulled by each Message class. In
        general, when converting from etree, subclasses should call this method
        first, then parse their specific XML constructs.
        """

        # Check namespace and element name of the root element
        expected_tag = '{%s}%s' % (ns_map['taxii'], cls.message_type)
        tag = src_etree.tag
        if tag != expected_tag:
            raise ValueError('%s != %s' % (tag, expected_tag))

        # Get the message ID
        message_id = get_required(src_etree, '/taxii:*/@message_id', ns_map)

        # Get in response to, if present
        in_response_to = get_optional(src_etree, '/taxii:*/@in_response_to', ns_map)
        if in_response_to:
            kwargs['in_response_to'] = in_response_to

        # Get the Extended headers
        extended_header_list = src_etree.xpath('/taxii:*/taxii:Extended_Headers/taxii:Extended_Header', namespaces=ns_map)
        extended_headers = {}
        for header in extended_header_list:
            eh_name = header.xpath('./@name')[0]
            # eh_value = header.text
            if len(header) == 0:  # This has string content
                eh_value = header.text
            else:  # This has XML content
                eh_value = header[0]

            extended_headers[eh_name] = eh_value

        return cls(message_id, extended_headers=extended_headers, **kwargs)


    @classmethod
    def from_xml(cls, xml):
        """Parse a Message from XML.

        Subclasses shouldn't implemnet this method, as it is mainly a wrapper
        for cls.from_etree.
        """
        etree_xml = parse_xml_string(xml)
        return cls.from_etree(etree_xml)

    @classmethod
    def from_dict(cls, d, **kwargs):
        """Pulls properties of a TAXII Message from a dictionary.

        Message-specific constructs must be pulled by each Message class. In
        general, when converting from dictionary, subclasses should call this
        method first, then parse their specific dictionary constructs.
        """
        message_type = d['message_type']
        if message_type != cls.message_type:
            raise ValueError('%s != %s' % (message_type, cls.message_type))
        message_id = d['message_id']
        extended_headers = {}
        for k, v in six.iteritems(d['extended_headers']):
            try:
                v = parse(v)
            except etree.XMLSyntaxError:
                pass
            extended_headers[k] = v

        in_response_to = d.get('in_response_to')
        if in_response_to:
            kwargs['in_response_to'] = in_response_to

        return cls(message_id, extended_headers=extended_headers, **kwargs)

    @classmethod
    def from_json(cls, json_string):
        return cls.from_dict(json.loads(json_string))


class ContentBlock(TAXIIBase10):

    """A TAXII Content Block.

    Args:
        content_binding (str): a Content Binding ID or nesting expression
            indicating the type of content contained in the Content field of this
            Content Block. **Required**
        content (string or etree): a piece of content of the type specified
            by the Content Binding. **Required**
        timestamp_label (datetime): the Timestamp Label associated with this
            Content Block. **Optional**
        padding (string): an arbitrary amount of padding for this Content
            Block. **Optional**
    """

    NAME = 'Content_Block'

    def __init__(self, content_binding, content, timestamp_label=None, padding=None):
        self.content_binding = content_binding
        self.content, self.content_is_xml = self._stringify_content(content)
        self.timestamp_label = timestamp_label
        self.padding = padding

    @property
    def sort_key(self):
        return self.content[:25]

    @property
    def content_binding(self):
        return self._content_binding

    @content_binding.setter
    def content_binding(self, value):
        do_check(value, 'content_binding', regex_tuple=uri_regex)
        self._content_binding = value

    @property
    def content(self):
        if self.content_is_xml:
            return etree.tostring(self._content)
        else:
            return self._content

    @content.setter
    def content(self, value):
        do_check(value, 'content')  # Just check for not None
        self._content, self.content_is_xml = self._stringify_content(value)

    @property
    def content_is_xml(self):
        return self._content_is_xml

    @content_is_xml.setter
    def content_is_xml(self, value):
        do_check(value, 'content_is_xml', value_tuple=(True, False))
        self._content_is_xml = value

    @property
    def timestamp_label(self):
        return self._timestamp_label

    @timestamp_label.setter
    def timestamp_label(self, value):
        value = check_timestamp_label(value, 'timestamp_label', can_be_none=True)
        self._timestamp_label = value

    def _stringify_content(self, content):
        """Always a string or raises an error.
        Returns the string representation and whether the data is XML.
        """
        # If it's an etree, it's definitely XML
        if isinstance(content, etree._ElementTree):
            return content.getroot(), True

        if isinstance(content, etree._Element):
            return content, True

        if hasattr(content, 'read'):  # The content is file-like
            try:  # Try to parse as XML
                xml = parse(content)
                return xml, True
            except etree.XMLSyntaxError:  # Content is not well-formed XML; just treat as a string
                return content.read(), False
        else:  # The Content is not file-like
            try:  # Attempt to parse string as XML
                xml = parse_xml_string(content)
                return xml, True
            except etree.XMLSyntaxError:  # Content is not well-formed XML; just treat as a string
                if isinstance(content, six.string_types):  # It's a string of some kind, unicode or otherwise
                    return content, False
                else:  # It's some other datatype that needs casting to string
                    return str(content), False

    def to_etree(self):
        block = etree.Element('{%s}Content_Block' % ns_map['taxii'], nsmap=ns_map)
        cb = etree.SubElement(block, '{%s}Content_Binding' % ns_map['taxii'])
        cb.text = self.content_binding
        c = etree.SubElement(block, '{%s}Content' % ns_map['taxii'])

        if self.content_is_xml:
            c.append(self._content)
        else:
            c.text = self._content

        if self.timestamp_label:
            tl = etree.SubElement(block, '{%s}Timestamp_Label' % ns_map['taxii'])
            tl.text = self.timestamp_label.isoformat()

        if self.padding is not None:
            p = etree.SubElement(block, '{%s}Padding' % ns_map['taxii'])
            p.text = self.padding

        return block

    def to_dict(self):
        block = {}
        block['content_binding'] = self.content_binding

        if self.content_is_xml:
            block['content'] = etree.tostring(self._content)
        else:
            block['content'] = self._content
        block['content_is_xml'] = self.content_is_xml

        if self.timestamp_label:
            block['timestamp_label'] = self.timestamp_label.isoformat()

        if self.padding is not None:
            block['padding'] = self.padding

        return block

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Content Block ===\n"
        s += line_prepend + "  Content Binding: %s\n" % self.content_binding
        s += line_prepend + "  Content Length: %s\n" % len(self.content)
        s += line_prepend + "  (Only content length is shown for brevity)\n"
        if self.timestamp_label:
            s += line_prepend + "  Timestamp Label: %s\n" % self.timestamp_label.isoformat()
        s += line_prepend + "  Padding: %s\n" % self.padding

        return s

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}

        kwargs['content_binding'] = get_required(etree_xml, './taxii:Content_Binding', ns_map).text

        kwargs['padding'] = get_optional_text(etree_xml, './taxii:Padding', ns_map)

        ts_text = get_optional_text(etree_xml, './taxii:Timestamp_Label', ns_map)
        if ts_text:
            kwargs['timestamp_label'] = parse_datetime_string(ts_text)

        content = get_required(etree_xml, './taxii:Content', ns_map)

        if len(content) == 0:  # This has string content
            kwargs['content'] = content.text
        else:  # This has XML content
            kwargs['content'] = content[0]

        return ContentBlock(**kwargs)


    @staticmethod
    def from_dict(d):
        kwargs = {}
        kwargs['content_binding'] = d['content_binding']
        kwargs['padding'] = d.get('padding')

        if d.get('timestamp_label'):
            kwargs['timestamp_label'] = parse_datetime_string(d['timestamp_label'])

        is_xml = d.get('content_is_xml', False)
        if is_xml:
            #FIXME: to parse or not to parse the content - this should be configurable
            kwargs['content'] = parse(d['content'])
        else:
            kwargs['content'] = d['content']

        cb = ContentBlock(**kwargs)
        return cb

    @classmethod
    def from_json(cls, json_string):
        return cls.from_dict(json.loads(json_string))


# TAXII Message Classes #

class DiscoveryRequest(TAXIIMessage):

    """
    A TAXII Discovery Request message.

    Args:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
    """

    message_type = MSG_DISCOVERY_REQUEST

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value


class DiscoveryResponse(TAXIIMessage):

    """
    A TAXII Discovery Response message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Optional**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        service_instances (list of `ServiceInstance`): a list of
            service instances that this response contains. **Optional**
    """
    message_type = MSG_DISCOVERY_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None, service_instances=None):
        super(DiscoveryResponse, self).__init__(message_id, in_response_to, extended_headers)
        self.service_instances = service_instances or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=uri_regex)
        self._in_response_to = value

    @property
    def service_instances(self):
        return self._service_instances

    @service_instances.setter
    def service_instances(self, value):
        do_check(value, 'service_instances', type=ServiceInstance)
        self._service_instances = value

    def to_etree(self):
        xml = super(DiscoveryResponse, self).to_etree()
        for service_instance in self.service_instances:
            xml.append(service_instance.to_etree())
        return xml

    def to_dict(self):
        d = super(DiscoveryResponse, self).to_dict()
        d['service_instances'] = []
        for service_instance in self.service_instances:
            d['service_instances'].append(service_instance.to_dict())
        return d

    def to_text(self, line_prepend=''):
        s = super(DiscoveryResponse, self).to_text(line_prepend)
        for si in self.service_instances:
            s += si.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(DiscoveryResponse, cls).from_etree(etree_xml)
        msg.service_instances = []
        for service_instance in etree_xml.xpath('./taxii:Service_Instance', namespaces=ns_map):
            si = ServiceInstance.from_etree(service_instance)
            msg.service_instances.append(si)
        return msg

    @classmethod
    def from_dict(cls, d):
        msg = super(DiscoveryResponse, cls).from_dict(d)
        msg.service_instances = []
        for service_instance in d['service_instances']:
            si = ServiceInstance.from_dict(service_instance)
            msg.service_instances.append(si)
        return msg


class ServiceInstance(TAXIIBase10):

    """
    The Service Instance component of a TAXII Discovery Response Message.

    Args:
        service_type (string): identifies the Service Type of this
            Service Instance. **Required**
        services_version (string): identifies the TAXII Services
            Specification to which this Service conforms. **Required**
        protocol_binding (string): identifies the protocol binding
            supported by this Service. **Required**
        service_address (string): identifies the network address of the
            TAXII Daemon that hosts this Service. **Required**
        message_bindings (list of strings): identifies the message
            bindings supported by this Service instance. **Required**
        inbox_service_accepted_content (list of strings): identifies
            content bindings that this Inbox Service is willing to accept.
            **Optional**
        available (boolean): indicates whether the identity of the
            requester (authenticated or otherwise) is allowed to access this
            TAXII Service. **Optional**
        message (string): contains a message regarding this Service
            instance. **Optional**

    The ``message_bindings`` list must contain at least one value.
    """

    def __init__(self, service_type, services_version, protocol_binding,
                 service_address, message_bindings,
                 inbox_service_accepted_content=None, available=None,
                 message=None):
        self.service_type = service_type
        self.services_version = services_version
        self.protocol_binding = protocol_binding
        self.service_address = service_address
        self.message_bindings = message_bindings
        self.inbox_service_accepted_content = inbox_service_accepted_content or []
        self.available = available
        self.message = message

    @property
    def sort_key(self):
        return self.service_address

    @property
    def service_type(self):
        return self._service_type

    @service_type.setter
    def service_type(self, value):
        do_check(value, 'service_type', value_tuple=SVC_TYPES)
        self._service_type = value

    @property
    def services_version(self):
        return self._services_version

    @services_version.setter
    def services_version(self, value):
        do_check(value, 'services_version', regex_tuple=uri_regex)
        self._services_version = value

    @property
    def protocol_binding(self):
        return self._protocol_binding

    @protocol_binding.setter
    def protocol_binding(self, value):
        do_check(value, 'protocol_binding', regex_tuple=uri_regex)
        self._protocol_binding = value

    @property
    def service_address(self):
        return self._service_address

    @service_address.setter
    def service_address(self, value):
        self._service_address = value

    @property
    def message_bindings(self):
        return self._message_bindings

    @message_bindings.setter
    def message_bindings(self, value):
        do_check(value, 'message_bindings', regex_tuple=uri_regex)
        self._message_bindings = value

    @property
    def inbox_service_accepted_content(self):
        return self._inbox_service_accepted_content

    @inbox_service_accepted_content.setter
    def inbox_service_accepted_content(self, value):
        do_check(value, 'inbox_service_accepted_content', regex_tuple=uri_regex)
        self._inbox_service_accepted_content = value

    @property
    def available(self):
        return self._available

    @available.setter
    def available(self, value):
        do_check(value, 'available', value_tuple=(True, False), can_be_none=True)
        self._available = value

    def to_etree(self):
        si = etree.Element('{%s}Service_Instance' % ns_map['taxii'])
        si.attrib['service_type'] = self.service_type
        si.attrib['service_version'] = self.services_version
        if self.available:
            si.attrib['available'] = str(self.available).lower()

        protocol_binding = etree.SubElement(si, '{%s}Protocol_Binding' % ns_map['taxii'])
        protocol_binding.text = self.protocol_binding

        service_address = etree.SubElement(si, '{%s}Address' % ns_map['taxii'])
        service_address.text = self.service_address

        for mb in self.message_bindings:
            message_binding = etree.SubElement(si, '{%s}Message_Binding' % ns_map['taxii'])
            message_binding.text = mb

        for cb in self.inbox_service_accepted_content:
            content_binding = etree.SubElement(si, '{%s}Content_Binding' % ns_map['taxii'])
            content_binding.text = cb

        if self.message is not None:
            message = etree.SubElement(si, '{%s}Message' % ns_map['taxii'])
            message.text = self.message

        return si

    def to_dict(self):
        d = {}
        d['service_type'] = self.service_type
        d['services_version'] = self.services_version
        d['protocol_binding'] = self.protocol_binding
        d['service_address'] = self.service_address
        d['message_bindings'] = self.message_bindings
        d['inbox_service_accepted_content'] = self.inbox_service_accepted_content
        d['available'] = self.available
        d['message'] = self.message
        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Service Instance===\n"
        s += line_prepend + "  Service Type: %s\n" % self.service_type
        s += line_prepend + "  Services Version: %s\n" % self.services_version
        s += line_prepend + "  Protocol Binding: %s\n" % self.protocol_binding
        s += line_prepend + "  Address: %s\n" % self.service_address
        for mb in self.message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % mb
        if len(self.inbox_service_accepted_content) == 0:
            s += line_prepend + "  Inbox Service Accepts: %s\n" % None
        for isac in self.inbox_service_accepted_content:
            s += line_prepend + "  Inbox Service Accepts: %s\n" % isac
        s += line_prepend + "  Available: %s\n" % self.available
        s += line_prepend + "  Message: %s\n" % self.message

        return s

    @classmethod
    def from_etree(cls, etree_xml):  # Expects a taxii:Service_Instance element
        service_type = etree_xml.attrib['service_type']
        services_version = etree_xml.attrib['service_version']
        available = None
        if etree_xml.attrib.get('available'):
            tmp_available = etree_xml.attrib['available']
            available = tmp_available.lower() == 'true'

        protocol_binding = get_required(etree_xml, './taxii:Protocol_Binding', ns_map).text
        service_address = get_required(etree_xml, './taxii:Address', ns_map).text

        message_bindings = []
        for mb in etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map):
            message_bindings.append(mb.text)

        inbox_service_accepted_contents = []
        for cb in etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map):
            inbox_service_accepted_contents.append(cb.text)

        message = get_optional_text(etree_xml, './taxii:Message', ns_map)

        return ServiceInstance(service_type, services_version, protocol_binding,
                service_address, message_bindings, inbox_service_accepted_contents,
                available, message)

    @staticmethod
    def from_dict(d):
        return ServiceInstance(**d)


class FeedInformationRequest(TAXIIMessage):

    """
    A TAXII Feed Information Request message.

    Args:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
    """

    message_type = MSG_FEED_INFORMATION_REQUEST

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value


class FeedInformationResponse(TAXIIMessage):

    """
    A TAXII Feed Information Response message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        feed_informations (list of FeedInformation): A list
            of FeedInformation objects to be contained in this response.
            **Optional**
    """
    message_type = MSG_FEED_INFORMATION_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None, feed_informations=None):
        super(FeedInformationResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.feed_informations = feed_informations or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=message_id_regex_10)
        self._in_response_to = value

    @property
    def feed_informations(self):
        return self._feed_informations

    @feed_informations.setter
    def feed_informations(self, value):
        do_check(value, 'feed_informations', type=FeedInformation)
        self._feed_informations = value

    def to_etree(self):
        xml = super(FeedInformationResponse, self).to_etree()
        for feed in self.feed_informations:
            xml.append(feed.to_etree())
        return xml

    def to_dict(self):
        d = super(FeedInformationResponse, self).to_dict()
        d['feed_informations'] = []
        for feed in self.feed_informations:
            d['feed_informations'].append(feed.to_dict())
        return d

    def to_text(self, line_prepend=''):
        s = super(FeedInformationResponse, self).to_text(line_prepend)
        for feed in self.feed_informations:
            s += feed.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(FeedInformationResponse, cls).from_etree(etree_xml)
        msg.feed_informations = []
        feed_informations = etree_xml.xpath('./taxii:Feed', namespaces=ns_map)
        for feed in feed_informations:
            msg.feed_informations.append(FeedInformation.from_etree(feed))
        return msg

    @classmethod
    def from_dict(cls, d):
        msg = super(FeedInformationResponse, cls).from_dict(d)
        msg.feed_informations = []
        for feed in d['feed_informations']:
            msg.feed_informations.append(FeedInformation.from_dict(feed))
        return msg


class FeedInformation(TAXIIBase10):

    """
    The Feed Information component of a TAXII Feed Information Response
    Message.

    Arguments:
        feed_name (str): the name by which this TAXII Data Feed is
            identified. **Required**
        feed_description (str): a prose description of this TAXII
            Data Feed. **Required**
        supported_contents (list of str): Content Binding IDs
            indicating which types of content are currently expressed in this
            TAXII Data Feed. **Required**
        available (boolean): whether the identity of the requester
            (authenticated or otherwise) is allowed to access this TAXII
            Service. **Optional** Default: ``None``, indicating "unknown"
        push_methods (list of PushMethod objects): the protocols that
            can be used to push content via a subscription. **Optional**
        polling_service_instances (list of PollingServiceInstance objects):
            the bindings and address a Consumer can use to interact with a
            Poll Service instance that supports this TAXII Data Feed.
            **Optional**
        subscription_methods (list of SubscriptionMethod objects): the
            protocol and address of the TAXII Daemon hosting the Feed
            Management Service that can process subscriptions for this TAXII
            Data Feed. **Optional**

    The absense of ``push_methods`` indicates no push methods.  The absense
    of ``polling_service_instances`` indicates no polling services.  At
    least one of ``push_methods`` and ``polling_service_instances`` must not
    be empty. The absense of ``subscription_methods`` indicates no
    subscription services.
    """

    def __init__(self, feed_name, feed_description, supported_contents,
                 available=None, push_methods=None,
                 polling_service_instances=None, subscription_methods=None):

        self.feed_name = feed_name
        self.available = available
        self.feed_description = feed_description
        self.supported_contents = supported_contents
        self.push_methods = push_methods or []
        self.polling_service_instances = polling_service_instances or []
        self.subscription_methods = subscription_methods or []

    @property
    def sort_key(self):
        return self.feed_name

    @property
    def feed_name(self):
        return self._feed_name

    @feed_name.setter
    def feed_name(self, value):
        do_check(value, 'feed_name', regex_tuple=uri_regex)
        self._feed_name = value

    @property
    def available(self):
        return self._available

    @available.setter
    def available(self, value):
        do_check(value, 'available', value_tuple=(True, False), can_be_none=True)
        self._available = value

    @property
    def supported_contents(self):
        return self._supported_contents

    @supported_contents.setter
    def supported_contents(self, value):
        do_check(value, 'supported_contents', regex_tuple=uri_regex)
        self._supported_contents = value

    @property
    def push_methods(self):
        return self._push_methods

    @push_methods.setter
    def push_methods(self, value):
        do_check(value, 'push_methods', type=PushMethod)
        self._push_methods = value

    @property
    def polling_service_instances(self):
        return self._polling_service_instances

    @polling_service_instances.setter
    def polling_service_instances(self, value):
        do_check(value, 'polling_service_instances', type=PollingServiceInstance)
        self._polling_service_instances = value

    @property
    def subscription_methods(self):
        return self._subscription_methods

    @subscription_methods.setter
    def subscription_methods(self, value):
        do_check(value, 'subscription_methods', type=SubscriptionMethod)
        self._subscription_methods = value

    def to_etree(self):
        f = etree.Element('{%s}Feed' % ns_map['taxii'])
        f.attrib['feed_name'] = self.feed_name
        if self.available:
            f.attrib['available'] = str(self.available).lower()
        feed_description = etree.SubElement(f, '{%s}Description' % ns_map['taxii'])
        feed_description.text = self.feed_description

        for binding in self.supported_contents:
            cb = etree.SubElement(f, '{%s}Content_Binding' % ns_map['taxii'])
            cb.text = binding

        for push_method in self.push_methods:
            f.append(push_method.to_etree())

        for polling_service in self.polling_service_instances:
            f.append(polling_service.to_etree())

        for subscription_method in self.subscription_methods:
            f.append(subscription_method.to_etree())

        return f

    def to_dict(self):
        d = {}
        d['feed_name'] = self.feed_name
        if self.available:
            d['available'] = self.available
        d['feed_description'] = self.feed_description
        d['supported_contents'] = self.supported_contents
        d['push_methods'] = []
        for push_method in self.push_methods:
            d['push_methods'].append(push_method.to_dict())
        d['polling_service_instances'] = []
        for polling_service in self.polling_service_instances:
            d['polling_service_instances'].append(polling_service.to_dict())
        d['subscription_methods'] = []
        for subscription_method in self.subscription_methods:
            d['subscription_methods'].append(subscription_method.to_dict())
        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Data Feed ===\n"
        s += line_prepend + "  Feed Name: %s\n" % self.feed_name
        if self.available:
            s += line_prepend + "  Available: %s\n" % self.available
        s += line_prepend + "  Feed Description: %s\n" % self.feed_description
        for sc in self.supported_contents:
            s += line_prepend + "  Supported Content: %s\n" % sc
        for pm in self.push_methods:
            s += pm.to_text(line_prepend + STD_INDENT)
        for ps in self.polling_service_instances:
            s += ps.to_text(line_prepend + STD_INDENT)
        for sm in self.subscription_methods:
            s += sm.to_text(line_prepend + STD_INDENT)

        return s

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}
        kwargs['feed_name'] = etree_xml.attrib['feed_name']
        kwargs['available'] = None
        if 'available' in etree_xml.attrib:
            tmp = etree_xml.attrib['available']
            kwargs['available'] = tmp.lower() == 'true'

        kwargs['feed_description'] = get_required(etree_xml, './taxii:Description', ns_map).text

        kwargs['supported_contents'] = []
        for binding_elt in etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map):
            kwargs['supported_contents'].append(binding_elt.text)

        kwargs['push_methods'] = []
        for push_method_elt in etree_xml.xpath('./taxii:Push_Method', namespaces=ns_map):
            kwargs['push_methods'].append(PushMethod.from_etree(push_method_elt))

        kwargs['polling_service_instances'] = []
        for polling_elt in etree_xml.xpath('./taxii:Polling_Service', namespaces=ns_map):
            kwargs['polling_service_instances'].append(PollingServiceInstance.from_etree(polling_elt))

        kwargs['subscription_methods'] = []
        for subscription_elt in etree_xml.xpath('./taxii:Subscription_Service', namespaces=ns_map):
            kwargs['subscription_methods'].append(SubscriptionMethod.from_etree(subscription_elt))

        return FeedInformation(**kwargs)

    @staticmethod
    def from_dict(d):
        kwargs = {}
        kwargs['feed_name'] = d['feed_name']
        kwargs['available'] = d.get('available')

        kwargs['feed_description'] = d['feed_description']
        kwargs['supported_contents'] = []
        for binding in d.get('supported_contents', []):
            kwargs['supported_contents'].append(binding)

        kwargs['push_methods'] = []
        for push_method in d.get('push_methods', []):
            kwargs['push_methods'].append(PushMethod.from_dict(push_method))

        kwargs['polling_service_instances'] = []
        for polling in d.get('polling_service_instances', []):
            kwargs['polling_service_instances'].append(PollingServiceInstance.from_dict(polling))

        kwargs['subscription_methods'] = []
        for subscription_method in d.get('subscription_methods', []):
            kwargs['subscription_methods'].append(SubscriptionMethod.from_dict(subscription_method))

        return FeedInformation(**kwargs)


class PushMethod(TAXIIBase10):

    """
    The Push Method component of a TAXII Feed Information
    component.

    Args:
        push_protocol (str): a protocol binding that can be used
            to push content to an Inbox Service instance. **Required**
        push_message_bindings (list of str): the message bindings that
            can be used to push content to an Inbox Service instance
            using the protocol identified in the Push Protocol field.
            **Required**
    """

    def __init__(self, push_protocol, push_message_bindings):
        self.push_protocol = push_protocol
        self.push_message_bindings = push_message_bindings

    @property
    def sort_key(self):
        return self.push_protocol

    @property
    def push_protocol(self):
        return self._push_protocol

    @push_protocol.setter
    def push_protocol(self, value):
        do_check(value, 'push_protocol', regex_tuple=uri_regex)
        self._push_protocol = value

    @property
    def push_message_bindings(self):
        return self._push_message_bindings

    @push_message_bindings.setter
    def push_message_bindings(self, value):
        do_check(value, 'push_message_bindings', regex_tuple=uri_regex)
        self._push_message_bindings = value

    def to_etree(self):
        x = etree.Element('{%s}Push_Method' % ns_map['taxii'])
        proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
        proto_bind.text = self.push_protocol
        for binding in self.push_message_bindings:
            b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii'])
            b.text = binding
        return x

    def to_dict(self):
        d = {}
        d['push_protocol'] = self.push_protocol
        d['push_message_bindings'] = []
        for binding in self.push_message_bindings:
            d['push_message_bindings'].append(binding)
        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Push Method ===\n"
        s += line_prepend + "  Protocol Binding: %s\n" % self.push_protocol
        for mb in self.push_message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % mb

        return s

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}
        kwargs['push_protocol'] = get_required(etree_xml, './taxii:Protocol_Binding', ns_map).text
        kwargs['push_message_bindings'] = []
        for message_binding in etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map):
            kwargs['push_message_bindings'].append(message_binding.text)
        return PushMethod(**kwargs)

    @staticmethod
    def from_dict(d):
        return PushMethod(**d)


class PollingServiceInstance(TAXIIBase10):

    """
    The Polling Service Instance component of a TAXII Feed
    Information component.

    Args:
        poll_protocol (str): the protocol binding supported by
            this Poll Service instance. **Required**
        poll_address (str): the address of the TAXII Daemon
            hosting this Poll Service instance. **Required**
        poll_message_bindings (list of str): the message bindings
            supported by this Poll Service instance. **Required**
    """
    NAME = 'Polling_Service'

    def __init__(self, poll_protocol, poll_address, poll_message_bindings):
        self.poll_protocol = poll_protocol
        self.poll_address = poll_address
        self.poll_message_bindings = poll_message_bindings

    @property
    def sort_key(self):
        return self.poll_address

    @property
    def poll_protocol(self):
        return self._poll_protocol

    @poll_protocol.setter
    def poll_protocol(self, value):
        do_check(value, 'poll_protocol', regex_tuple=uri_regex)
        self._poll_protocol = value

    @property
    def poll_message_bindings(self):
        return self._poll_message_bindings

    @poll_message_bindings.setter
    def poll_message_bindings(self, value):
        do_check(value, 'poll_message_bindings', regex_tuple=uri_regex)
        self._poll_message_bindings = value

    def to_etree(self):
        x = etree.Element('{%s}Polling_Service' % ns_map['taxii'])
        proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
        proto_bind.text = self.poll_protocol
        address = etree.SubElement(x, '{%s}Address' % ns_map['taxii'])
        address.text = self.poll_address
        for binding in self.poll_message_bindings:
            b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii'])
            b.text = binding
        return x

    def to_dict(self):
        d = {}
        d['poll_protocol'] = self.poll_protocol
        d['poll_address'] = self.poll_address
        d['poll_message_bindings'] = []
        for binding in self.poll_message_bindings:
            d['poll_message_bindings'].append(binding)
        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Poll Service Instance ===\n"
        s += line_prepend + "  Protocol Binding: %s\n" % self.poll_protocol
        s += line_prepend + "  Address: %s\n" % self.poll_address
        for mb in self.poll_message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % mb

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        protocol = get_required(etree_xml, './taxii:Protocol_Binding', ns_map).text
        addr = get_required(etree_xml, './taxii:Address', ns_map).text

        bindings = []
        for message_binding in etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map):
            bindings.append(message_binding.text)
        return cls(protocol, addr, bindings)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class SubscriptionMethod(TAXIIBase10):

    """
    The Subscription Method component of a TAXII Feed Information
    component.

    Args:
        subscription_protocol (str): the protocol binding supported by
            this Feed Management Service instance. **Required**
        subscription_address (str): the address of the TAXII Daemon
            hosting this Feed Management Service instance.
            **Required**.
        subscription_message_bindings (list of str): the message
            bindings supported by this Feed Management Service
            Instance. **Required**
    """
    NAME = 'Subscription_Service'

    def __init__(self, subscription_protocol, subscription_address,
                 subscription_message_bindings):
        self.subscription_protocol = subscription_protocol
        self.subscription_address = subscription_address
        self.subscription_message_bindings = subscription_message_bindings

    @property
    def sort_key(self):
        return self.subscription_address

    @property
    def subscription_protocol(self):
        return self._subscription_protocol

    @subscription_protocol.setter
    def subscription_protocol(self, value):
        do_check(value, 'subscription_protocol', regex_tuple=uri_regex)
        self._subscription_protocol = value

    @property
    def subscription_message_bindings(self):
        return self._subscription_message_bindings

    @subscription_message_bindings.setter
    def subscription_message_bindings(self, value):
        do_check(value, 'subscription_message_bindings', regex_tuple=uri_regex)
        self._subscription_message_bindings = value

    def to_etree(self):
        x = etree.Element('{%s}%s' % (ns_map['taxii'], self.NAME))
        proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii'])
        proto_bind.text = self.subscription_protocol
        address = etree.SubElement(x, '{%s}Address' % ns_map['taxii'])
        address.text = self.subscription_address
        for binding in self.subscription_message_bindings:
            b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii'])
            b.text = binding
        return x

    def to_dict(self):
        d = {}
        d['subscription_protocol'] = self.subscription_protocol
        d['subscription_address'] = self.subscription_address
        d['subscription_message_bindings'] = []
        for binding in self.subscription_message_bindings:
            d['subscription_message_bindings'].append(binding)
        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Subscription Method ===\n"
        s += line_prepend + "  Protocol Binding: %s\n" % self.subscription_protocol
        s += line_prepend + "  Address: %s\n" % self.subscription_address
        for mb in self.subscription_message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % mb

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        protocol = get_required(etree_xml, './taxii:Protocol_Binding', ns_map).text
        addr = get_required(etree_xml, './taxii:Address', ns_map).text
        bindings = []
        for message_binding in etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map):
            bindings.append(message_binding.text)
        return cls(protocol, addr, bindings)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class PollRequest(TAXIIMessage):

    """
    A TAXII Poll Request message.

    Arguments:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        feed_name (str): the name of the TAXII Data Feed that is being
            polled. **Required**
        exclusive_begin_timestamp_label (datetime): a Timestamp Label
            indicating the beginning of the range of TAXII Data Feed content the
            requester wishes to receive. **Optional**
        inclusive_end_timestamp_label (datetime): a Timestamp Label
            indicating the end of the range of TAXII Data Feed content the
            requester wishes to receive. **Optional**
        subscription_id (str): the existing subscription the Consumer
            wishes to poll. **Optional**
        content_bindings (list of str): the type of content that is
            requested in the response to this poll. **Optional**, defaults to
            accepting all content bindings.
    """
    message_type = MSG_POLL_REQUEST

    def __init__(self, message_id, extended_headers=None,
                 feed_name=None, exclusive_begin_timestamp_label=None,
                 inclusive_end_timestamp_label=None, subscription_id=None,
                 content_bindings=None):
        super(PollRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.exclusive_begin_timestamp_label = exclusive_begin_timestamp_label
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.subscription_id = subscription_id
        self.content_bindings = content_bindings or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value

    @property
    def feed_name(self):
        return self._feed_name

    @feed_name.setter
    def feed_name(self, value):
        do_check(value, 'feed_name', regex_tuple=uri_regex)
        self._feed_name = value

    @property
    def exclusive_begin_timestamp_label(self):
        return self._exclusive_begin_timestamp_label

    @exclusive_begin_timestamp_label.setter
    def exclusive_begin_timestamp_label(self, value):
        value = check_timestamp_label(value, 'exclusive_begin_timestamp_label', can_be_none=True)
        self._exclusive_begin_timestamp_label = value

    @property
    def inclusive_end_timestamp_label(self):
        return self._inclusive_end_timestamp_label

    @inclusive_end_timestamp_label.setter
    def inclusive_end_timestamp_label(self, value):
        value = check_timestamp_label(value, 'inclusive_end_timestamp_label', can_be_none=True)
        self._inclusive_end_timestamp_label = value

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        do_check(value, 'subscription_id', regex_tuple=uri_regex, can_be_none=True)
        self._subscription_id = value

    @property
    def content_bindings(self):
        return self._content_bindings

    @content_bindings.setter
    def content_bindings(self, value):
        do_check(value, 'content_bindings', regex_tuple=uri_regex)
        self._content_bindings = value

    def to_etree(self):
        xml = super(PollRequest, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            xml.attrib['subscription_id'] = self.subscription_id

        if self.exclusive_begin_timestamp_label:
            ebt = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii'])
            # TODO: Add TZ Info
            ebt.text = self.exclusive_begin_timestamp_label.isoformat()

        if self.inclusive_end_timestamp_label:
            iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
            # TODO: Add TZ Info
            iet.text = self.inclusive_end_timestamp_label.isoformat()

        for binding in self.content_bindings:
            b = etree.SubElement(xml, '{%s}Content_Binding' % ns_map['taxii'])
            b.text = binding

        return xml

    def to_dict(self):
        d = super(PollRequest, self).to_dict()
        d['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            d['subscription_id'] = self.subscription_id
        if self.exclusive_begin_timestamp_label:  # TODO: Add TZ Info
            d['exclusive_begin_timestamp_label'] = self.exclusive_begin_timestamp_label.isoformat()
        if self.inclusive_end_timestamp_label:  # TODO: Add TZ Info
            d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        d['content_bindings'] = []
        for bind in self.content_bindings:
            d['content_bindings'].append(bind)
        return d

    def to_text(self, line_prepend=''):
        s = super(PollRequest, self).to_text(line_prepend)
        s += line_prepend + "  Feed Name: %s\n" % self.feed_name
        if self.subscription_id:
            s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id

        if self.exclusive_begin_timestamp_label:
            s += line_prepend + "  Excl. Begin Timestamp Label: %s\n" % self.exclusive_begin_timestamp_label.isoformat()
        else:
            s += line_prepend + "  Excl. Begin Timestamp Label: %s\n" % None

        if self.inclusive_end_timestamp_label:
            s += line_prepend + "  Incl. End Timestamp Label: %s\n" % self.inclusive_end_timestamp_label.isoformat()
        else:
            s += line_prepend + "  Incl. End Timestamp Label: %s\n" % None

        if len(self.content_bindings) == 0:
            s += line_prepend + "  Content Binding: Any Content\n"

        for cb in self.content_bindings:
            s += line_prepend + "  Content Binding: %s\n" % cb

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['feed_name'] = get_required(etree_xml, './@feed_name', ns_map)
        kwargs['subscription_id'] = get_optional(etree_xml, './@subscription_id', ns_map)

        ebt_text = get_optional_text(etree_xml, './taxii:Exclusive_Begin_Timestamp', ns_map)
        if ebt_text:
            kwargs['exclusive_begin_timestamp_label'] = parse_datetime_string(ebt_text)

        iet_text = get_optional_text(etree_xml, './taxii:Inclusive_End_Timestamp', ns_map)
        if iet_text:
            kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(iet_text)

        kwargs['content_bindings'] = []
        for binding in etree_xml.xpath('./taxii:Content_Binding', namespaces=ns_map):
            kwargs['content_bindings'].append(binding.text)

        msg = super(PollRequest, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['feed_name'] = d['feed_name']

        kwargs['subscription_id'] = d.get('subscription_id')

        kwargs['exclusive_begin_timestamp_label'] = None
        if d.get('exclusive_begin_timestamp_label'):
            kwargs['exclusive_begin_timestamp_label'] = parse_datetime_string(d['exclusive_begin_timestamp_label'])

        kwargs['inclusive_end_timestamp_label'] = None
        if d.get('inclusive_end_timestamp_label'):
            kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(d['inclusive_end_timestamp_label'])

        kwargs['content_bindings'] = d.get('content_bindings', [])

        msg = super(PollRequest, cls).from_dict(d, **kwargs)
        return msg


class PollResponse(TAXIIMessage):

    """
    A TAXII Poll Response message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        feed_name (str): the name of the TAXII Data Feed that was polled.
            **Required**
        inclusive_begin_timestamp_label (datetime): a Timestamp Label
            indicating the beginning of the range this response covers.
            **Optional**
        inclusive_end_timestamp_label (datetime): a Timestamp Label
            indicating the end of the range this response covers. **Required**
        subscription_id (str): the Subscription ID for which this content
            is being provided. **Optional**
        message (str): additional information for the message recipient.
            **Optional**
        content_blocks (list of ContentBlock): piece of content
            and additional information related to the content. **Optional**
    """
    message_type = MSG_POLL_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None,
                 feed_name=None, inclusive_begin_timestamp_label=None,
                 inclusive_end_timestamp_label=None, subscription_id=None,
                 message=None, content_blocks=None):
        super(PollResponse, self).__init__(message_id, in_response_to, extended_headers)
        self.feed_name = feed_name
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.inclusive_begin_timestamp_label = inclusive_begin_timestamp_label
        self.subscription_id = subscription_id
        self.message = message
        self.content_blocks = content_blocks or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=uri_regex)
        self._in_response_to = value

    @property
    def feed_name(self):
        return self._feed_name

    @feed_name.setter
    def feed_name(self, value):
        do_check(value, 'feed_name', regex_tuple=uri_regex)
        self._feed_name = value

    @property
    def inclusive_end_timestamp_label(self):
        return self._inclusive_end_timestamp_label

    @inclusive_end_timestamp_label.setter
    def inclusive_end_timestamp_label(self, value):
        value = check_timestamp_label(value, 'inclusive_end_timestamp_label')
        self._inclusive_end_timestamp_label = value

    @property
    def inclusive_begin_timestamp_label(self):
        return self._inclusive_begin_timestamp_label

    @inclusive_begin_timestamp_label.setter
    def inclusive_begin_timestamp_label(self, value):
        value = check_timestamp_label(value, 'inclusive_begin_timestamp_label', can_be_none=True)
        self._inclusive_begin_timestamp_label = value

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        do_check(value, 'subscription_id', regex_tuple=uri_regex, can_be_none=True)
        self._subscription_id = value

    @property
    def content_blocks(self):
        return self._content_blocks

    @content_blocks.setter
    def content_blocks(self, value):
        do_check(value, 'content_blocks', type=ContentBlock)
        self._content_blocks = value

    def to_etree(self):
        xml = super(PollResponse, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            xml.attrib['subscription_id'] = self.subscription_id

        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message

        if self.inclusive_begin_timestamp_label:
            ibt = etree.SubElement(xml, '{%s}Inclusive_Begin_Timestamp' % ns_map['taxii'])
            ibt.text = self.inclusive_begin_timestamp_label.isoformat()

        iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
        iet.text = self.inclusive_end_timestamp_label.isoformat()

        for block in self.content_blocks:
            xml.append(block.to_etree())

        return xml

    def to_dict(self):
        d = super(PollResponse, self).to_dict()

        d['feed_name'] = self.feed_name
        if self.subscription_id is not None:
            d['subscription_id'] = self.subscription_id
        if self.message is not None:
            d['message'] = self.message
        if self.inclusive_begin_timestamp_label:
            d['inclusive_begin_timestamp_label'] = self.inclusive_begin_timestamp_label.isoformat()
        d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        d['content_blocks'] = []
        for block in self.content_blocks:
            d['content_blocks'].append(block.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = super(PollResponse, self).to_text(line_prepend)
        s += line_prepend + "  Feed Name: %s\n" % self.feed_name
        if self.subscription_id:
            s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id
        s += line_prepend + "  Message: %s\n" % self.message

        if self.inclusive_begin_timestamp_label:
            s += line_prepend + "  Incl. Begin Timestamp Label: %s\n" % self.inclusive_begin_timestamp_label.isoformat()
        else:
            s += line_prepend + "  Incl. Begin Timestamp Label: %s\n" % None

        s += line_prepend + "  Incl. End Timestamp Label: %s\n" % self.inclusive_end_timestamp_label.isoformat()

        for cb in self.content_blocks:
            s += cb.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}

        kwargs['feed_name'] = get_required(etree_xml, './@feed_name', ns_map)
        kwargs['subscription_id'] = get_optional(etree_xml, './@subscription_id', ns_map)
        kwargs['message'] = get_optional_text(etree_xml, './taxii:Message', ns_map)

        ibts_text = get_optional_text(etree_xml, './taxii:Inclusive_Begin_Timestamp', ns_map)
        if ibts_text:
            kwargs['inclusive_begin_timestamp_label'] = parse_datetime_string(ibts_text)

        iets_text = get_required(etree_xml, './taxii:Inclusive_End_Timestamp', ns_map).text
        kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(iets_text)

        kwargs['content_blocks'] = []
        blocks = etree_xml.xpath('./taxii:Content_Block', namespaces=ns_map)
        for block in blocks:
            kwargs['content_blocks'].append(ContentBlock.from_etree(block))

        msg = super(PollResponse, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['feed_name'] = d['feed_name']

        kwargs['message'] = d.get('message')
        kwargs['subscription_id'] = d.get('subscription_id')

        kwargs['inclusive_begin_timestamp_label'] = None
        if d.get('inclusive_begin_timestamp_label'):
            kwargs['inclusive_begin_timestamp_label'] = parse_datetime_string(d['inclusive_begin_timestamp_label'])

        kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(d['inclusive_end_timestamp_label'])

        kwargs['content_blocks'] = []
        for block in d['content_blocks']:
            kwargs['content_blocks'].append(ContentBlock.from_dict(block))
        msg = super(PollResponse, cls).from_dict(d, **kwargs)
        return msg


class StatusMessage(TAXIIMessage):

    """
    A TAXII Status message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        status_type (str): One of the defined Status Types or a third-party-
            defined Status Type. **Required**
        status_detail (str): A field for additional information about
            this status in a machine-readable format. **Optional or Prohibited**
            depending on ``status_type``. See TAXII Specification for details.
        message (str): Additional information for the status. There is no
            expectation that this field be interpretable by a machine; it is
            instead targeted to a human operator. **Optional**
    """
    message_type = MSG_STATUS_MESSAGE

    def __init__(self, message_id, in_response_to, extended_headers=None,
                 status_type=None, status_detail=None, message=None):
        super(StatusMessage, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.status_type = status_type
        self.status_detail = status_detail
        self.message = message

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=uri_regex)
        self._in_response_to = value

    @property
    def status_type(self):
        return self._status_type

    @status_type.setter
    def status_type(self, value):
        do_check(value, 'status_type')
        self._status_type = value

    # TODO: is it possible to check the status detail?

    def to_etree(self):
        xml = super(StatusMessage, self).to_etree()
        xml.attrib['status_type'] = self.status_type

        if self.status_detail is not None:
            sd = etree.SubElement(xml, '{%s}Status_Detail' % ns_map['taxii'])
            sd.text = self.status_detail

        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message

        return xml

    def to_dict(self):
        d = super(StatusMessage, self).to_dict()
        d['status_type'] = self.status_type
        if self.status_detail is not None:
            d['status_detail'] = self.status_detail
        if self.message is not None:
            d['message'] = self.message

        return d

    def to_text(self, line_prepend=''):
        s = super(StatusMessage, self).to_text(line_prepend)
        s += line_prepend + "  Status Type: %s\n" % self.status_type
        if self.status_detail:
            s += line_prepend + "  Status Detail: %s\n" % self.status_detail
        s += line_prepend + "  Status Message: %s\n" % self.message
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = dict(
            status_type = etree_xml.attrib['status_type'],
            status_detail = get_optional_text(etree_xml, './taxii:Status_Detail', ns_map),
            message = get_optional_text(etree_xml, './taxii:Message', ns_map),
        )

        msg = super(StatusMessage, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = dict(
            status_type = d['status_type'],
            status_detail = d.get('status_detail'),
            message = d.get('message')
        )

        msg = super(StatusMessage, cls).from_dict(d, **kwargs)
        return msg


class InboxMessage(TAXIIMessage):

    """
    A TAXII Inbox message.

    Args:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        message (str): prose information for the message recipient. **Optional**
        subscription_information (SubscriptionInformation): This
            field is only present if this message is being sent to provide
            content in accordance with an existing TAXII Data Feed
            subscription. **Optional**
        content_blocks (list of ContentBlock): Inbox content. **Optional**
    """

    message_type = MSG_INBOX_MESSAGE

    def __init__(self, message_id, in_response_to=None, extended_headers=None,
                 message=None, subscription_information=None,
                 content_blocks=None):

        super(InboxMessage, self).__init__(message_id, extended_headers=extended_headers)
        self.subscription_information = subscription_information
        self.message = message
        self.content_blocks = content_blocks or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value

    @property
    def subscription_information(self):
        return self._subscription_information

    @subscription_information.setter
    def subscription_information(self, value):
        do_check(value, 'subscription_information', type=SubscriptionInformation, can_be_none=True)
        self._subscription_information = value

    @property
    def content_blocks(self):
        return self._content_blocks

    @content_blocks.setter
    def content_blocks(self, value):
        do_check(value, 'content_blocks', type=ContentBlock)
        self._content_blocks = value

    def to_etree(self):
        xml = super(InboxMessage, self).to_etree()
        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message

        if self.subscription_information:
            xml.append(self.subscription_information.to_etree())

        for block in self.content_blocks:
            xml.append(block.to_etree())

        return xml

    def to_dict(self):
        d = super(InboxMessage, self).to_dict()
        if self.message is not None:
            d['message'] = self.message

        if self.subscription_information:
            d['subscription_information'] = self.subscription_information.to_dict()

        d['content_blocks'] = []
        for block in self.content_blocks:
            d['content_blocks'].append(block.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = super(InboxMessage, self).to_text(line_prepend)
        s += line_prepend + "  Message: %s\n" % self.message
        if self.subscription_information:
            s += self.subscription_information.to_text(line_prepend + STD_INDENT)
        s += line_prepend + "  Message has %s Content Blocks\n" % len(self.content_blocks)
        for cb in self.content_blocks:
            s += cb.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(InboxMessage, cls).from_etree(etree_xml)

        msg.message = get_optional_text(etree_xml, './taxii:Message', ns_map)

        subs_info = get_optional(etree_xml, './taxii:Source_Subscription', ns_map)
        if subs_info is not None:
            msg.subscription_information = SubscriptionInformation.from_etree(subs_info)

        content_blocks = etree_xml.xpath('./taxii:Content_Block', namespaces=ns_map)
        msg.content_blocks = []
        for block in content_blocks:
            msg.content_blocks.append(ContentBlock.from_etree(block))

        return msg

    @classmethod
    def from_dict(cls, d):
        msg = super(InboxMessage, cls).from_dict(d)

        msg.message = d.get('message')

        msg.subscription_information = None
        if 'subscription_information' in d:
            msg.subscription_information = SubscriptionInformation.from_dict(d['subscription_information'])

        msg.content_blocks = []
        for block in d['content_blocks']:
            msg.content_blocks.append(ContentBlock.from_dict(block))

        return msg


class SubscriptionInformation(TAXIIBase10):

    """
    The Subscription Information component of a TAXII Inbox message.

    Arguments:
        feed_name (str): the name of the TAXII Data Feed from
            which this content is being provided. **Required**
        subscription_id (str): the Subscription ID for which this
            content is being provided. **Required**
        inclusive_begin_timestamp_label (datetime): a Timestamp Label
            indicating the beginning of the time range this Inbox Message
            covers. **Optional**
        inclusive_end_timestamp_label (datetime): a Timestamp Label
            indicating the end of the time range this Inbox Message covers.
            **Optional**
    """

    def __init__(self, feed_name, subscription_id,
                 inclusive_begin_timestamp_label,
                 inclusive_end_timestamp_label):
        self.feed_name = feed_name
        self.subscription_id = subscription_id
        self.inclusive_begin_timestamp_label = inclusive_begin_timestamp_label
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label

    @property
    def feed_name(self):
        return self._feed_name

    @feed_name.setter
    def feed_name(self, value):
        do_check(value, 'feed_name', regex_tuple=uri_regex)
        self._feed_name = value

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        do_check(value, 'subscription_id', regex_tuple=uri_regex)
        self._subscription_id = value

    @property
    def inclusive_begin_timestamp_label(self):
        return self._inclusive_begin_timestamp_label

    @inclusive_begin_timestamp_label.setter
    def inclusive_begin_timestamp_label(self, value):
        value = check_timestamp_label(value, 'inclusive_begin_timestamp_label')
        self._inclusive_begin_timestamp_label = value

    @property
    def inclusive_end_timestamp_label(self):
        return self._inclusive_end_timestamp_label

    @inclusive_end_timestamp_label.setter
    def inclusive_end_timestamp_label(self, value):
        value = check_timestamp_label(value, 'inclusive_end_timestamp_label')
        self._inclusive_end_timestamp_label = value

    def to_etree(self):
        xml = etree.Element('{%s}Source_Subscription' % ns_map['taxii'])
        xml.attrib['feed_name'] = self.feed_name
        xml.attrib['subscription_id'] = self.subscription_id

        ibtl = etree.SubElement(xml, '{%s}Inclusive_Begin_Timestamp' % ns_map['taxii'])
        ibtl.text = self.inclusive_begin_timestamp_label.isoformat()

        ietl = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii'])
        ietl.text = self.inclusive_end_timestamp_label.isoformat()

        return xml

    def to_dict(self):
        d = {}
        d['feed_name'] = self.feed_name
        d['subscription_id'] = self.subscription_id
        d['inclusive_begin_timestamp_label'] = self.inclusive_begin_timestamp_label.isoformat()
        d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Subscription Information ===\n"
        s += line_prepend + "  Feed Name: %s\n" % self.feed_name
        s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id
        s += line_prepend + "  Incl. Begin TS Label: %s\n" % self.inclusive_begin_timestamp_label.isoformat()
        s += line_prepend + "  Incl. End TS Label: %s\n" % self.inclusive_end_timestamp_label.isoformat()
        return s

    @staticmethod
    def from_etree(etree_xml):
        feed_name = etree_xml.attrib['feed_name']
        subscription_id = etree_xml.attrib['subscription_id']

        ibtl = parse_datetime_string(get_required(etree_xml, './taxii:Inclusive_Begin_Timestamp', ns_map).text)
        ietl = parse_datetime_string(get_required(etree_xml, './taxii:Inclusive_End_Timestamp', ns_map).text)

        return SubscriptionInformation(feed_name, subscription_id, ibtl, ietl)

    @staticmethod
    def from_dict(d):
        feed_name = d['feed_name']
        subscription_id = d['subscription_id']

        ibtl = parse_datetime_string(d['inclusive_begin_timestamp_label'])
        ietl = parse_datetime_string(d['inclusive_end_timestamp_label'])

        return SubscriptionInformation(feed_name, subscription_id, ibtl, ietl)


class ManageFeedSubscriptionRequest(TAXIIMessage):

    """
    A TAXII Manage Feed Subscription Request message.

    Args:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        feed_name (str): the name of the TAXII Data Feed to which the
            action applies. **Required**
        action (str): the requested action to take. **Required**
        subscription_id (str): the ID of a previously created subscription.
            **Required** if ``action==``:py:data:`ACT_UNSUBSCRIBE`, else
            **Prohibited**.
        delivery_parameters (list of DeliveryParameters): the delivery parameters
            for this request. **Optional** Absence means delivery is not requested.
    """

    message_type = MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST

    def __init__(self, message_id, extended_headers=None,
                 feed_name=None, action=None, subscription_id=None,
                 delivery_parameters=None):
        super(ManageFeedSubscriptionRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.action = action
        self.subscription_id = subscription_id
        self.delivery_parameters = delivery_parameters

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value

    @property
    def feed_name(self):
        return self._feed_name

    @feed_name.setter
    def feed_name(self, value):
        do_check(value, 'feed_name', regex_tuple=uri_regex)
        self._feed_name = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        do_check(value, 'action', value_tuple=ACT_TYPES)
        self._action = value

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        do_check(value, 'subscription_id', regex_tuple=uri_regex, can_be_none=True)
        self._subscription_id = value

    @property
    def delivery_parameters(self):
        return self._delivery_parameters

    @delivery_parameters.setter
    def delivery_parameters(self, value):
        do_check(value, 'delivery_parameters', type=DeliveryParameters, can_be_none=True)
        self._delivery_parameters = value

    def to_etree(self):
        xml = super(ManageFeedSubscriptionRequest, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        xml.attrib['action'] = self.action
        if self.subscription_id is not None:
            xml.attrib['subscription_id'] = self.subscription_id

        if self.delivery_parameters:
            xml.append(self.delivery_parameters.to_etree())
        return xml

    def to_dict(self):
        d = super(ManageFeedSubscriptionRequest, self).to_dict()
        d['feed_name'] = self.feed_name
        d['action'] = self.action
        d['subscription_id'] = self.subscription_id
        d['delivery_parameters'] = None
        if self.delivery_parameters:
            d['delivery_parameters'] = self.delivery_parameters.to_dict()
        return d

    def to_text(self, line_prepend=''):
        s = super(ManageFeedSubscriptionRequest, self).to_text(line_prepend)
        s += line_prepend + "  Feed Name: %s\n" % self.feed_name
        s += line_prepend + "  Action: %s\n" % self.action
        s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id
        if self.delivery_parameters:
            s += self.delivery_parameters.to_text(line_prepend + STD_INDENT)
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = dict(
            feed_name = get_required(etree_xml, './@feed_name', ns_map),
            action = get_required(etree_xml, './@action', ns_map),

            # subscription_id is not required for action 'SUBSCRIBE'
            subscription_id = get_optional(etree_xml, './@subscription_id', ns_map),
        )

        # marked as required in spec but as optional is XSD
        delivery = get_optional(etree_xml, './taxii:Push_Parameters', ns_map)
        if delivery is not None:
            kwargs['delivery_parameters'] = DeliveryParameters.from_etree(delivery)

        msg = super(ManageFeedSubscriptionRequest, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = dict(
            feed_name = d['feed_name'],
            action = d['action'],
            subscription_id = d['subscription_id'],
            delivery_parameters = DeliveryParameters.from_dict(d['delivery_parameters'])
        )

        msg = super(ManageFeedSubscriptionRequest, cls).from_dict(d, **kwargs)
        return msg


class ManageFeedSubscriptionResponse(TAXIIMessage):

    """
    A TAXII Manage Feed Subscription Response message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        feed_name (str): the name of the TAXII Data Feed to which
            the action applies. **Required**
        message (str): additional information for the message recipient.
            **Optional**
        subscription_instances (list of SubscriptionInstance): **Optional**
    """

    message_type = MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None,
                 feed_name=None, message=None, subscription_instances=None):
        super(ManageFeedSubscriptionResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.feed_name = feed_name
        self.message = message
        self.subscription_instances = subscription_instances or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=uri_regex)
        self._in_response_to = value

    @property
    def feed_name(self):
        return self._feed_name

    @feed_name.setter
    def feed_name(self, value):
        do_check(value, 'feed_name', regex_tuple=uri_regex)
        self._feed_name = value

    @property
    def subscription_instances(self):
        return self._subscription_instances

    @subscription_instances.setter
    def subscription_instances(self, value):
        do_check(value, 'subscription_instances', type=SubscriptionInstance)
        self._subscription_instances = value

    def to_etree(self):
        xml = super(ManageFeedSubscriptionResponse, self).to_etree()
        xml.attrib['feed_name'] = self.feed_name
        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii'])
            m.text = self.message

        for subscription_instance in self.subscription_instances:
            xml.append(subscription_instance.to_etree())

        return xml

    def to_dict(self):
        d = super(ManageFeedSubscriptionResponse, self).to_dict()
        d['feed_name'] = self.feed_name
        if self.message is not None:
            d['message'] = self.message
        d['subscription_instances'] = []
        for subscription_instance in self.subscription_instances:
            d['subscription_instances'].append(subscription_instance.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = super(ManageFeedSubscriptionResponse, self).to_text(line_prepend)
        s += line_prepend + "  Feed Name: %s\n" % self.feed_name
        s += line_prepend + "  Message: %s\n" % self.message
        for si in self.subscription_instances:
            s += si.to_text(line_prepend + STD_INDENT)
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['feed_name'] = etree_xml.attrib['feed_name']

        kwargs['message'] = get_optional_text(etree_xml, './taxii:Message', ns_map)

        kwargs['subscription_instances'] = []
        for si in etree_xml.xpath('./taxii:Subscription', namespaces=ns_map):
            kwargs['subscription_instances'].append(SubscriptionInstance.from_etree(si))

        msg = super(ManageFeedSubscriptionResponse, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['feed_name'] = d['feed_name']
        kwargs['message'] = d.get('message')

        kwargs['subscription_instances'] = []
        for instance in d['subscription_instances']:
            kwargs['subscription_instances'].append(SubscriptionInstance.from_dict(instance))

        msg = super(ManageFeedSubscriptionResponse, cls).from_dict(d, **kwargs)
        return msg


class SubscriptionInstance(TAXIIBase10):

    """
    The Subscription Instance component of the Manage Feed Subscription
    Response message.

    Args:
        subscription_id (str): the id of the subscription. **Required**
        delivery_parameters (DeliveryParameters): the parameters
            for this subscription. **Required** if responding to message
            with ``action==``:py:data:`ACT_STATUS`, otherwise **Prohibited**
        poll_instances (list of PollInstance): Each Poll
            Instance represents an instance of a Poll Service that can be
            contacted to retrieve content associated with the new
            Subscription. **Optional**
    """

    def __init__(self, subscription_id, delivery_parameters=None,
                 poll_instances=None):
        self.subscription_id = subscription_id
        self.delivery_parameters = delivery_parameters
        self.poll_instances = poll_instances or []

    @property
    def sort_key(self):
        return self.subscription_id

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        do_check(value, 'subscription_id', regex_tuple=uri_regex)
        self._subscription_id = value

    @property
    def delivery_parameters(self):
        return self._delivery_parameters

    @delivery_parameters.setter
    def delivery_parameters(self, value):
        do_check(value, 'delivery_parameters', type=DeliveryParameters, can_be_none=True)
        self._delivery_parameters = value

    @property
    def poll_instances(self):
        return self._poll_instances

    @poll_instances.setter
    def poll_instances(self, value):
        do_check(value, 'poll_instances', type=PollInstance, can_be_none=False)
        self._poll_instances = value

    def to_etree(self):
        xml = etree.Element('{%s}Subscription' % ns_map['taxii'])
        xml.attrib['subscription_id'] = self.subscription_id

        if self.delivery_parameters:
            xml.append(self.delivery_parameters.to_etree())

        for poll_instance in self.poll_instances:
            xml.append(poll_instance.to_etree())

        return xml

    def to_dict(self):
        d = {}
        d['subscription_id'] = self.subscription_id

        if self.delivery_parameters:
            d['delivery_parameters'] = self.delivery_parameters.to_dict()
        else:
            d['delivery_parameters'] = None

        d['poll_instances'] = []
        for poll_instance in self.poll_instances:
            d['poll_instances'].append(poll_instance.to_dict())

        return d

    def to_text(self, line_indent=''):
        s = line_indent + "=== Subscription Instance ===\n"
        s += line_indent + "  Subscription ID: %s\n" % self.subscription_id
        if self.delivery_parameters:
            s += self.delivery_parameters.to_text(line_indent + STD_INDENT)
        for pi in self.poll_instances:
            s += pi.to_text(line_indent + STD_INDENT)
        return s

    @staticmethod
    def from_etree(etree_xml):
        subscription_id = etree_xml.attrib['subscription_id']

        _delivery_parameters = get_optional(etree_xml, './taxii:Push_Parameters', ns_map)
        if _delivery_parameters:
            delivery_parameters = DeliveryParameters.from_etree(_delivery_parameters)
        else:
            delivery_parameters = None

        poll_instances = []
        for poll_instance in etree_xml.xpath('./taxii:Poll_Instance', namespaces=ns_map):
            poll_instances.append(PollInstance.from_etree(poll_instance))

        return SubscriptionInstance(subscription_id, delivery_parameters, poll_instances)

    @staticmethod
    def from_dict(d):
        subscription_id = d['subscription_id']

        if d.get('delivery_parameters'):
            delivery_parameters = DeliveryParameters.from_dict(d['delivery_parameters'])
        else:
            delivery_parameters = None

        poll_instances = []
        for poll_instance in d['poll_instances']:
            poll_instances.append(PollInstance.from_dict(poll_instance))

        return SubscriptionInstance(subscription_id, delivery_parameters, poll_instances)


class PollInstance(TAXIIBase10):

    """
    The Poll Instance component of the Manage Feed Subscription
    Response message.

    Args:
        poll_protocol (str): The protocol binding supported by this
            instance of a Polling Service. **Required**
        poll_address (str): the address of the TAXII Daemon hosting
            this Poll Service. **Required**
        poll_message_bindings (list of str): one or more message bindings
            that can be used when interacting with this Poll Service
            instance. **Required**
    """

    def __init__(self, poll_protocol, poll_address, poll_message_bindings=None):
        self.poll_protocol = poll_protocol
        self.poll_address = poll_address
        self._poll_message_bindings = poll_message_bindings or []

    @property
    def sort_key(self):
        return self.poll_address

    @property
    def poll_protocol(self):
        return self._poll_protocol

    @poll_protocol.setter
    def poll_protocol(self, value):
        do_check(value, 'poll_protocol', regex_tuple=uri_regex)
        self._poll_protocol = value

    @property
    def poll_message_bindings(self):
        return self._poll_message_bindings

    @poll_message_bindings.setter
    def poll_message_bindings(self, value):
        do_check(value, 'poll_message_bindings', regex_tuple=uri_regex)
        self._poll_message_bindings = value

    def to_etree(self):
        xml = etree.Element('{%s}Poll_Instance' % ns_map['taxii'])

        pb = etree.SubElement(xml, '{%s}Protocol_Binding' % ns_map['taxii'])
        pb.text = self.poll_protocol

        a = etree.SubElement(xml, '{%s}Address' % ns_map['taxii'])
        a.text = self.poll_address

        for binding in self.poll_message_bindings:
            b = etree.SubElement(xml, '{%s}Message_Binding' % ns_map['taxii'])
            b.text = binding

        return xml

    def to_dict(self):
        d = {}

        d['poll_protocol'] = self.poll_protocol
        d['poll_address'] = self.poll_address
        d['poll_message_bindings'] = []
        for binding in self.poll_message_bindings:
            d['poll_message_bindings'].append(binding)

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Poll Instance ===\n"
        s += line_prepend + "  Protocol Binding: %s\n" % self.poll_protocol
        s += line_prepend + "  Address: %s\n" % self.poll_address
        for mb in self.poll_message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % mb
        return s

    @staticmethod
    def from_etree(etree_xml):
        poll_protocol = get_required(etree_xml, './taxii:Protocol_Binding', ns_map).text
        address = get_required(etree_xml, './taxii:Address', ns_map).text

        poll_message_bindings = []
        for b in etree_xml.xpath('./taxii:Message_Binding', namespaces=ns_map):
            poll_message_bindings.append(b.text)

        return PollInstance(poll_protocol, address, poll_message_bindings)

    @staticmethod
    def from_dict(d):
        return PollInstance(**d)

########################################################
# EVERYTHING BELOW HERE IS FOR BACKWARDS COMPATIBILITY #
########################################################

# Add top-level classes as nested classes for backwards compatibility
DiscoveryResponse.ServiceInstance = ServiceInstance
FeedInformationResponse.FeedInformation = FeedInformation
FeedInformation.PushMethod = PushMethod
FeedInformation.PollingServiceInstance = PollingServiceInstance
FeedInformation.SubscriptionMethod = SubscriptionMethod
ManageFeedSubscriptionResponse.PollInstance = PollInstance
ManageFeedSubscriptionResponse.SubscriptionInstance = SubscriptionInstance
InboxMessage.SubscriptionInformation = SubscriptionInformation

# Constants not imported in `from constants import *`
MSG_TYPES = MSG_TYPES_10
ST_TYPES = ST_TYPES_10
ACT_TYPES = ACT_TYPES_10
SVC_TYPES = SVC_TYPES_10

from .common import (generate_message_id)
