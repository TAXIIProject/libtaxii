# Copyright (C) 2013 - The MITRE Corporation
# For license information, see the LICENSE.txt file

# Contributors:
# * Alex Ciobanu - calex@cert.europa.eu
# * Mark Davidson - mdavidson@mitre.org
# * Bryan Worrell - bworrell@mitre.org
# * Benjamin Yates - byates@dtcc.com

"""
Creating, handling, and parsing TAXII 1.1 messages.
"""


import collections
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
from .validation import do_check, uri_regex, check_timestamp_label
from .constants import *


def validate_xml(xml_string):
    """
    Note that this function has been deprecated. Please see
    libtaxii.validators.SchemaValidator.

    Validate XML with the TAXII XML Schema 1.1.

    Args:
        xml_string (str): The XML to validate.

    Example:
        .. code-block:: python

            is_valid = tm11.validate_xml(message.to_xml())
    """

    warnings.warn('Call to deprecated function: libtaxii.messages_11.validate_xml()',
                  category=DeprecationWarning)

    etree_xml = parse_xml_string(xml_string)
    package_dir, package_filename = os.path.split(__file__)
    schema_file = os.path.join(package_dir, "xsd", "TAXII_XMLMessageBinding_Schema_11.xsd")
    taxii_schema_doc = parse(schema_file)
    xml_schema = etree.XMLSchema(taxii_schema_doc)
    valid = xml_schema.validate(etree_xml)
    # TODO: Additionally, validate the Query stuff
    if not valid:
        return xml_schema.error_log.last_error
    return valid


def get_message_from_xml(xml_string, encoding='utf_8'):
    """Create a TAXIIMessage object from an XML string.

    This function automatically detects which type of Message should be created
    based on the XML.

    Args:
        xml_string (str): The XML to parse into a TAXII message.
        encoding (str): The encoding of the string; defaults to UTF-8

    Example:
        .. code-block:: python

            message_xml = message.to_xml()
            new_message = tm11.get_message_from_xml(message_xml)
    """
    decoded_string = xml_string.decode(encoding, 'replace')
    etree_xml = parse_xml_string(decoded_string)
    qn = etree.QName(etree_xml)
    if qn.namespace != ns_map['taxii_11']:
        raise ValueError('Unsupported namespace: %s' % qn.namespace)

    message_type = qn.localname

    if message_type == MSG_DISCOVERY_REQUEST:
        return DiscoveryRequest.from_etree(etree_xml)
    if message_type == MSG_DISCOVERY_RESPONSE:
        return DiscoveryResponse.from_etree(etree_xml)
    if message_type == MSG_COLLECTION_INFORMATION_REQUEST:
        return CollectionInformationRequest.from_etree(etree_xml)
    if message_type == MSG_COLLECTION_INFORMATION_RESPONSE:
        return CollectionInformationResponse.from_etree(etree_xml)
    if message_type == MSG_POLL_REQUEST:
        return PollRequest.from_etree(etree_xml)
    if message_type == MSG_POLL_RESPONSE:
        return PollResponse.from_etree(etree_xml)
    if message_type == MSG_STATUS_MESSAGE:
        return StatusMessage.from_etree(etree_xml)
    if message_type == MSG_INBOX_MESSAGE:
        return InboxMessage.from_etree(etree_xml)
    if message_type == MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST:
        return ManageCollectionSubscriptionRequest.from_etree(etree_xml)
    if message_type == MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE:
        return ManageCollectionSubscriptionResponse.from_etree(etree_xml)
    if message_type == MSG_POLL_FULFILLMENT_REQUEST:
        return PollFulfillmentRequest.from_etree(etree_xml)

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
            new_message = tm11.get_message_from_dict(message_dict)
    """
    if 'message_type' not in d:
        raise ValueError('message_type is a required field!')

    message_type = d['message_type']
    if message_type == MSG_DISCOVERY_REQUEST:
        return DiscoveryRequest.from_dict(d)
    if message_type == MSG_DISCOVERY_RESPONSE:
        return DiscoveryResponse.from_dict(d)
    if message_type == MSG_COLLECTION_INFORMATION_REQUEST:
        return CollectionInformationRequest.from_dict(d)
    if message_type == MSG_COLLECTION_INFORMATION_RESPONSE:
        return CollectionInformationResponse.from_dict(d)
    if message_type == MSG_POLL_REQUEST:
        return PollRequest.from_dict(d)
    if message_type == MSG_POLL_RESPONSE:
        return PollResponse.from_dict(d)
    if message_type == MSG_STATUS_MESSAGE:
        return StatusMessage.from_dict(d)
    if message_type == MSG_INBOX_MESSAGE:
        return InboxMessage.from_dict(d)
    if message_type == MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST:
        return ManageCollectionSubscriptionRequest.from_dict(d)
    if message_type == MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE:
        return ManageCollectionSubscriptionResponse.from_dict(d)
    if message_type == MSG_POLL_FULFILLMENT_REQUEST:
        return PollFulfillmentRequest.from_dict(d)

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


def _sanitize_content_binding(binding):
    """
    Takes in one of:
    1. ContentBinding object
    2. string
    and returns a ContentBinding object.

    This supports function calls where a string or ContentBinding can be
    used to specify a content binding.
    """
    if isinstance(binding, ContentBinding):  # It's already good to go
        return binding
    elif isinstance(binding, six.string_types):  # Convert it to a ContentBinding
        return ContentBinding.from_string(binding)
    else:  # Don't know what to do with it.
        raise ValueError('Type cannot be converted to ContentBinding: %s' % binding.__class__.__name__)


def _sanitize_content_bindings(binding_list):
    bindings = []
    for item in binding_list:
        bindings.append(_sanitize_content_binding(item))

    return bindings


class UnsupportedQueryException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Start with the 'default' deserializer
query_deserializers = {}


def register_query_format(format_id, query, query_info, schema=None):
    """
    This function registers a query format with libtaxii.messages_11.
    Arguments:
        format_id (string) - The format ID of the query
        query (messages_11.Query subclass) - the Query object associated with the format_id
        query_info (messages_11.SupportedQuery subclass) - the SupportedQuery object associated with the format_id
        schema (xml schema) - The XML schema for validating the query
    """
    query_deserializers[format_id] = {'query': query, 'query_info': query_info, 'schema': schema}


def get_deserializer(format_id, type):
    do_check(type, 'type', value_tuple=('query', 'query_info'))

    if format_id not in query_deserializers:
        raise UnsupportedQueryException('A deserializer for the query format \'%s\' is not registered.' % format_id)

    return query_deserializers[format_id][type]

# TODO: Consider using this
# def _create_element(name, namespace=ns_map['taxii_11'], value=None, attrs=None, parent=None):
    # """
    # Helper method for appending a new element to an existing element.

    # Assumes the namespace is TAXII 1.1

    # Arguments:
    #     name (string) - The name of the element
    #     namespace (string) - The namespace of the element
    #     value (string) - The text value of the element
    #     attrs (dict) - A dictionary of attributes
    #     parent (Element) - The parent element
    # """
    # if value is None and attrs is None:
    #     return

    # if parent is None:
    #     elt = etree.Element('{%s}%s' % (namespace, name), nsmap=ns_map)
    # else:
    #     elt = etree.SubElement(parent, '{%s}%s' % (namespace, name), nsmap=ns_map)

    # if value is not None:
    #     elt.text = value

    # if attrs is not None:
    #     for k, v in attrs.items():
    #         elt.attrib[k] = v

    # return elt


class TAXIIBase11(TAXIIBase):
    version = VID_TAXII_XML_11


class SupportedQuery(TAXIIBase11):

    """
    This class contains an instance of a supported query. It
    is expected that, generally, messages_11.SupportedQuery
    subclasses will be used in place of this class
    to represent a query
    """

    def __init__(self, format_id):
        """
        Arguments:
            format_id (string) - The format_id of this supported query
        """
        self.format_id = format_id

    @property
    def sort_key(self):
        return self.format_id

    @property
    def format_id(self):
        return self._format_id

    @format_id.setter
    def format_id(self, value):
        do_check(value, 'format_id', regex_tuple=uri_regex)
        self._format_id = value

    def to_etree(self):
        q = etree.Element('{%s}Supported_Query' % ns_map['taxii_11'], nsmap=ns_map)
        q.attrib['format_id'] = self.format_id
        return q

    def to_dict(self):
        return {'format_id': self.format_id}

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Supported Query Information ===\n"
        s += line_prepend + "  Query Format: %s\n" % self.format_id
        return s

    @staticmethod
    def from_etree(etree_xml):
        format_id = get_required(etree_xml, './@format_id', ns_map)
        return SupportedQuery(format_id)

    @staticmethod
    def from_dict(d):
        return SupportedQuery(**d)


class Query(TAXIIBase11):

    """This class contains an instance of a query.

    It is expected that, generally, messages_11.Query subclasses will be used
    in place of this class to represent a query.
    """

    def __init__(self, format_id):
        """
        Arguments:
            format_id (string) - The format_id of this query
        """
        self.format_id = format_id

    @property
    def format_id(self):
        return self._format_id

    @format_id.setter
    def format_id(self, value):
        do_check(value, 'format_id', regex_tuple=uri_regex)
        self._format_id = value

    def to_etree(self):
        q = etree.Element('{%s}Query' % ns_map['taxii_11'], nsmap=ns_map)
        q.attrib['format_id'] = self.format_id
        return q

    def to_dict(self):
        return {'format_id': self.format_id}

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Query ===\n"
        s += line_prepend + "  Query Format: %s\n" % self.format_id

        return s

    @classmethod
    def from_etree(cls, etree_xml, kwargs):
        format_id = get_required(etree_xml, './@format_id', ns_map)
        return cls(format_id, **kwargs)

    @classmethod
    def from_dict(cls, d, kwargs):
        return cls(d, **kwargs)


# A value can be one of:
# - a dictionary, where each key is a content_binding_id and each value is a list of subtypes
#   (This is the default representation)
# - a "content_binding_id[>subtype]" structure
# - a list of "content_binding_id[>subtype]" structures


class ContentBinding(TAXIIBase11):

    """TAXII Content Binding component

    Args:
        binding_id (str): The content binding ID. **Required**
        subtype_ids (list of str): the subtype IDs. **Required**
    """

    def __init__(self, binding_id, subtype_ids=None):
        self.binding_id = binding_id
        self.subtype_ids = subtype_ids or []

    def __str__(self):
        s = self.binding_id
        if len(self.subtype_ids) > 0:
            s += '>' + ','.join(self.subtype_ids)

        return s

    @staticmethod
    def from_string(s):
        if '>' not in s:
            return ContentBinding(s)

        parts = s.split('>')
        binding_id = parts[0]
        subtype_ids = parts[1].split(',')
        return ContentBinding(binding_id, subtype_ids)

    @property
    def sort_key(self):
        return str(self)

    @property
    def binding_id(self):
        return self._binding_id

    @binding_id.setter
    def binding_id(self, value):
        do_check(value, 'binding_id', regex_tuple=uri_regex)
        self._binding_id = value

    @property
    def subtype_ids(self):
        return self._subtype_ids

    @subtype_ids.setter
    def subtype_ids(self, value):
        do_check(value, 'subtype_ids', regex_tuple=uri_regex)
        self._subtype_ids = value

    def to_etree(self):
        cb = etree.Element('{%s}Content_Binding' % ns_map['taxii_11'], nsmap=ns_map)
        cb.attrib['binding_id'] = self.binding_id
        for subtype_id in self.subtype_ids:
            s = etree.SubElement(cb, '{%s}Subtype' % ns_map['taxii_11'], nsmap=ns_map)
            s.attrib['subtype_id'] = subtype_id
        return cb

    def to_dict(self):
        return {'binding_id': self.binding_id, 'subtype_ids': self.subtype_ids}

    def to_text(self, line_prepend=''):
        return line_prepend + str(self)

    def __hash__(self):
        return hash(str(self.to_dict()))

    @classmethod
    def from_etree(self, etree_xml):
        binding_id = etree_xml.attrib['binding_id']
        subtype_ids = []
        subtype_elts = etree_xml.xpath('./taxii_11:Subtype', namespaces=ns_map)
        for elt in subtype_elts:
            subtype_ids.append(elt.attrib['subtype_id'])
        return ContentBinding(binding_id, subtype_ids)

    @classmethod
    def from_dict(self, d):
        return ContentBinding(**d)


class RecordCount(TAXIIBase11):

    """
    Information summarizing the number of records.

    Args:
        record_count (int): The number of records
        partial_count (bool): Whether the number of records is a partial count
    """

    def __init__(self, record_count, partial_count=False):
        self.record_count = record_count
        self.partial_count = partial_count

    @property
    def record_count(self):
        return self._record_count

    @record_count.setter
    def record_count(self, value):
        do_check(value, 'record_count', type=int)
        self._record_count = value

    @property
    def partial_count(self):
        return self._partial_count

    @partial_count.setter
    def partial_count(self, value):
        do_check(value, 'partial_count', value_tuple=(True, False), can_be_none=True)
        self._partial_count = value

    def to_etree(self):
        xml = etree.Element('{%s}Record_Count' % ns_map['taxii_11'], nsmap=ns_map)
        xml.text = str(self.record_count)

        if self.partial_count is not None:
            xml.attrib['partial_count'] = str(self.partial_count).lower()

        return xml

    def to_dict(self):
        d = {}
        d['record_count'] = self.record_count
        if self.partial_count is not None:
            d['partial_count'] = self.partial_count

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Record Count ===\n"
        s += line_prepend + "  Record Count: %s\n" % self.record_count
        if self.partial_count:
            s += line_prepend + "  Partial Count: %s\n" % self.partial_count

        return s

    @staticmethod
    def from_etree(etree_xml):
        record_count = int(etree_xml.text)
        partial_count = etree_xml.attrib.get('partial_count', 'false') == 'true'

        return RecordCount(record_count, partial_count)

    @staticmethod
    def from_dict(d):
        return RecordCount(**d)


class _GenericParameters(TAXIIBase11):
    name = 'Generic_Parameters'

    def __init__(self, response_type=RT_FULL, content_bindings=None, query=None):
        self.response_type = response_type
        self.content_bindings = content_bindings or []
        self.query = query

    @property
    def response_type(self):
        return self._response_type

    @response_type.setter
    def response_type(self, value):
        do_check(value, 'response_type', value_tuple=(RT_FULL, RT_COUNT_ONLY), can_be_none=True)
        self._response_type = value

    @property
    def content_bindings(self):
        return self._content_bindings

    @content_bindings.setter
    def content_bindings(self, value):
        value = _sanitize_content_bindings(value)
        do_check(value, 'content_bindings', type=ContentBinding)
        self._content_bindings = value

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        # TODO: Can i do more validation?
        do_check(value, 'query', type=Query, can_be_none=True)
        self._query = value

    def to_etree(self):
        xml = etree.Element('{%s}%s' % (ns_map['taxii_11'], self.name), nsmap=ns_map)
        if self.response_type is not None:
            rt = etree.SubElement(xml, '{%s}Response_Type' % ns_map['taxii_11'], nsmap=ns_map)
            rt.text = self.response_type

        for binding in self.content_bindings:
            xml.append(binding.to_etree())

        if self.query is not None:
            xml.append(self.query.to_etree())

        return xml

    def to_dict(self):
        d = {}
        if self.response_type is not None:
            d['response_type'] = self.response_type

        d['content_bindings'] = []
        for binding in self.content_bindings:
            d['content_bindings'].append(binding.to_dict())

        d['query'] = None
        if self.query is not None:
            d['query'] = self.query.to_dict()

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== %s ===\n" % self.name
        for binding in self.content_bindings:
            s += "  Content Binding: %s\n" % str(binding)

        if self.query:
            s += self.query.to_text(line_prepend + STD_INDENT)

        if self.response_type:
            s += line_prepend + "  Response type: %s\n" % str(self.response_type)

        return s

    @classmethod
    def from_etree(cls, etree_xml, **kwargs):

        response_type = get_optional_text(etree_xml, './taxii_11:Response_Type', ns_map)
        if response_type is None:
            response_type = RT_FULL

        content_bindings = []
        for binding in etree_xml.xpath('./taxii_11:Content_Binding', namespaces=ns_map):
            content_bindings.append(ContentBinding.from_etree(binding))

        query = None
        query_el = get_optional(etree_xml, './taxii_11:Query', ns_map)
        if query_el is not None:
            format_id = query_el.attrib['format_id']
            query = get_deserializer(format_id, 'query').from_etree(query_el)

        return cls(response_type, content_bindings, query, **kwargs)

    @classmethod
    def from_dict(cls, d, **kwargs):
        response_type = d.get('response_type', RT_FULL)
        content_bindings = []
        for binding in d['content_bindings']:
            content_bindings.append(ContentBinding.from_dict(binding))

        query = None
        if 'query' in d and d['query'] is not None:
            format_id = d['query']['format_id']
            query = get_deserializer(format_id, 'query').from_dict(d['query'])

        return cls(response_type, content_bindings, query, **kwargs)


class SubscriptionParameters(_GenericParameters):

    """
    TAXII Subscription Parameters.

    Args:
        response_type (str): The requested response type. Must be either
            :py:data:`RT_FULL` or :py:data:`RT_COUNT_ONLY`. **Optional**,
            defaults to :py:data:`RT_FULL`
        content_bindings (list of ContentBinding objects): A list of Content
            Bindings acceptable in response. **Optional**
        query (Query): The query for this poll parameters. **Optional**
    """
    name = 'Subscription_Parameters'


class ContentBlock(TAXIIBase11):

    """A TAXII Content Block.

    Args:
        content_binding (ContentBinding): a Content Binding ID or nesting expression
            indicating the type of content contained in the Content field of this
            Content Block. **Required**
        content (string or etree): a piece of content of the type specified
            by the Content Binding. **Required**
        timestamp_label (datetime): the Timestamp Label associated with this
            Content Block. **Optional**
        padding (string): an arbitrary amount of padding for this Content
            Block. **Optional**
        message (string): a message associated with this ContentBlock. **Optional**
    """
    NAME = 'Content_Block'

    def __init__(self, content_binding, content, timestamp_label=None,
                 padding=None, message=None):
        self.content_binding = content_binding
        self.content, self.content_is_xml = self._stringify_content(content)
        self.timestamp_label = timestamp_label
        self.message = message
        self.padding = padding

    @property
    def sort_key(self):
        return self.content[:25]

    @property
    def content_binding(self):
        return self._content_binding

    @content_binding.setter
    def content_binding(self, value):
        value = _sanitize_content_binding(value)
        do_check(value, 'content_binding', type=ContentBinding)
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
                sio_content = six.StringIO(content)
                xml = parse(sio_content)
                return xml, True
            except etree.XMLSyntaxError:  # Content is not well-formed XML; just treat as a string
                if isinstance(content, six.string_types):  # It's a string of some kind, unicode or otherwise
                    return content, False
                else:  # It's some other datatype that needs casting to string
                    return str(content), False

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        do_check(value, 'message', type=six.string_types, can_be_none=True)
        self._message = value

    def to_etree(self):
        block = etree.Element('{%s}Content_Block' % ns_map['taxii_11'], nsmap=ns_map)
        block.append(self.content_binding.to_etree())
        c = etree.SubElement(block, '{%s}Content' % ns_map['taxii_11'])

        if self.content_is_xml:
            c.append(self._content)
        else:
            c.text = self._content

        if self.timestamp_label is not None:
            tl = etree.SubElement(block, '{%s}Timestamp_Label' % ns_map['taxii_11'])
            tl.text = self.timestamp_label.isoformat()

        if self.message is not None:
            m = etree.SubElement(block, '{%s}Message' % ns_map['taxii_11'])
            m.text = self.message

        if self.padding is not None:
            p = etree.SubElement(block, '{%s}Padding' % ns_map['taxii_11'])
            p.text = self.padding

        return block

    def to_dict(self):
        block = {}
        block['content_binding'] = self.content_binding.to_dict()

        if self.content_is_xml:
            block['content'] = etree.tostring(self._content)
        else:
            block['content'] = self._content
        block['content_is_xml'] = self.content_is_xml

        if self.timestamp_label is not None:
            block['timestamp_label'] = self.timestamp_label.isoformat()

        if self.message is not None:
            block['message'] = self.message

        if self.padding is not None:
            block['padding'] = self.padding

        return block

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Content Block ===\n"
        s += line_prepend + "  Content Binding: %s\n" % str(self.content_binding)
        s += line_prepend + "  Content length: %s\n" % len(self.content)
        s += line_prepend + "  (Content not printed for brevity)\n"
        if self.timestamp_label:
            s += line_prepend + "  Timestamp Label: %s\n" % self.timestamp_label
        s += line_prepend + "  Message: %s\n" % self.message
        s += line_prepend + "  Padding: %s\n" % self.padding
        return s

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}

        kwargs['content_binding'] = ContentBinding.from_etree(
                get_required(etree_xml, './taxii_11:Content_Binding', ns_map))

        kwargs['padding'] = get_optional_text(etree_xml, './taxii_11:Padding', ns_map)

        ts_text = get_optional_text(etree_xml, './taxii_11:Timestamp_Label', ns_map)
        if ts_text:
            kwargs['timestamp_label'] = parse_datetime_string(ts_text)

        kwargs['message'] = get_optional_text(etree_xml, './taxii_11:Message', ns_map)

        content = get_required(etree_xml, './taxii_11:Content', ns_map)
        if len(content) == 0:  # This has string content
            kwargs['content'] = content.text
        else:  # This has XML content
            kwargs['content'] = content[0]

        return ContentBlock(**kwargs)

    @staticmethod
    def from_dict(d):
        kwargs = {}
        kwargs['content_binding'] = ContentBinding.from_dict(d['content_binding'])
        kwargs['padding'] = d.get('padding')
        if 'timestamp_label' in d:
            kwargs['timestamp_label'] = parse_datetime_string(d['timestamp_label'])
        kwargs['message'] = d.get('message')
        is_xml = d.get('content_is_xml', False)
        if is_xml:
            kwargs['content'] = parse(d['content'])
        else:
            kwargs['content'] = d['content']

        cb = ContentBlock(**kwargs)
        return cb

    @classmethod
    def from_json(cls, json_string):
        return cls.from_dict(json.loads(json_string))


class PushParameters(TAXIIBase11):

    """Set up Push Parameters.

    Args:
        inbox_protocol (str): identifies the protocol to be used when pushing
            TAXII Data Collection content to a Consumer's TAXII Inbox Service
            implementation. **Required**
        inbox_address (str): identifies the address of the TAXII Daemon hosting
            the Inbox Service to which the Consumer requests content for this
            TAXII Data Collection to be delivered. **Required**
        delivery_message_binding (str): identifies the message binding to be
             used to send pushed content for this subscription. **Required**
    """

    name = 'Push_Parameters'

    def __init__(self, inbox_protocol, inbox_address, delivery_message_binding):
        self.inbox_protocol = inbox_protocol
        self.inbox_address = inbox_address
        self.delivery_message_binding = delivery_message_binding

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
        self._inbox_address = value

    @property
    def delivery_message_binding(self):
        return self._delivery_message_binding

    @delivery_message_binding.setter
    def delivery_message_binding(self, value):
        do_check(value, 'delivery_message_binding', regex_tuple=uri_regex)
        self._delivery_message_binding = value

    def to_etree(self):
        xml = etree.Element('{%s}%s' % (ns_map['taxii_11'], self.name))

        pb = etree.SubElement(xml, '{%s}Protocol_Binding' % ns_map['taxii_11'])
        pb.text = self.inbox_protocol

        a = etree.SubElement(xml, '{%s}Address' % ns_map['taxii_11'])
        a.text = self.inbox_address

        mb = etree.SubElement(xml, '{%s}Message_Binding' % ns_map['taxii_11'])
        mb.text = self.delivery_message_binding

        return xml

    def to_dict(self):
        d = {}

        if self.inbox_protocol is not None:
            d['inbox_protocol'] = self.inbox_protocol

        if self.inbox_address is not None:
            d['inbox_address'] = self.inbox_address

        if self.delivery_message_binding is not None:
            d['delivery_message_binding'] = self.delivery_message_binding

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Push Parameters ===\n"
        s += line_prepend + "  Protocol Binding: %s\n" % self.inbox_protocol
        s += line_prepend + "  Inbox Address: %s\n" % self.inbox_address
        s += line_prepend + "  Message Binding: %s\n" % self.delivery_message_binding
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        inbox_protocol = get_optional_text(etree_xml, './taxii_11:Protocol_Binding', ns_map)
        inbox_address = get_optional_text(etree_xml, './taxii_11:Address', ns_map)
        delivery_message_binding = get_optional_text(etree_xml, './taxii_11:Message_Binding', ns_map)

        return cls(inbox_protocol, inbox_address, delivery_message_binding)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


# TODO: Check docstring
class DeliveryParameters(PushParameters):

    """Set up Delivery Parameters.

    Args:
        inbox_protocol (str): identifies the protocol to be used when pushing
            TAXII Data Collection content to a Consumer's TAXII Inbox Service
            implementation. **Required**
        inbox_address (str): identifies the address of the TAXII Daemon hosting
            the Inbox Service to which the Consumer requests content for this
            TAXII Data Collection to be delivered. **Required**
        delivery_message_binding (str): identifies the message binding to be
             used to send pushed content for this subscription. **Required**
    """

    name = 'Delivery_Parameters'


class TAXIIMessage(TAXIIBase11):

    """Encapsulate properties common to all TAXII Messages (such as headers).

    This class is extended by each Message Type (e.g., DiscoveryRequest), with
    each subclass containing subclass-specific information
    """

    message_type = 'TAXIIMessage'

    def __init__(self, message_id, in_response_to=None, extended_headers=None):
        """Create a new TAXIIMessage

        Args:
            message_id (str): A value identifying this message.
            in_response_to (str): Contains the Message ID of the message to
                which this is a response.
            extended_headers (dict): A dictionary of name/value pairs for
                use as Extended Headers
        """
        self.message_id = message_id
        self.in_response_to = in_response_to
        self.extended_headers = extended_headers or {}

    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, value):
        do_check(value, 'message_id', regex_tuple=uri_regex)
        self._message_id = value

    @property
    def in_response_to(self):
        return self._in_response_to

    @in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=uri_regex)
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
        root_elt = etree.Element('{%s}%s' % (ns_map['taxii_11'], self.message_type), nsmap=ns_map)
        root_elt.attrib['message_id'] = str(self.message_id)

        if self.in_response_to is not None:
            root_elt.attrib['in_response_to'] = str(self.in_response_to)

        if len(self.extended_headers) > 0:
            eh = etree.SubElement(root_elt, '{%s}Extended_Headers' % ns_map['taxii_11'], nsmap=ns_map)

            for name, value in list(self.extended_headers.items()):
                h = etree.SubElement(eh, '{%s}Extended_Header' % ns_map['taxii_11'], nsmap=ns_map)
                h.attrib['name'] = name
                append_any_content_etree(h, value)
                # h.text = value
        return root_elt

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
            s += line_prepend + "Extended Header: %s = %s\n" % (k, v)

        return s

    @classmethod
    def from_etree(cls, src_etree, **kwargs):
        """Pulls properties of a TAXII Message from an etree.

        Message-specific constructs must be pulled by each Message class. In
        general, when converting from etree, subclasses should call this method
        first, then parse their specific XML constructs.
        """

        # Check namespace and element name of the root element
        expected_tag = '{%s}%s' % (ns_map['taxii_11'], cls.message_type)
        tag = src_etree.tag
        if tag != expected_tag:
            raise ValueError('%s != %s' % (tag, expected_tag))

        # Get the message ID
        message_id = get_required(src_etree, '/taxii_11:*/@message_id', ns_map)

        # Get in response to, if present
        in_response_to = get_optional(src_etree, '/taxii_11:*/@in_response_to', ns_map)
        if in_response_to:
            kwargs['in_response_to'] = in_response_to

        # Get the Extended headers
        extended_header_list = src_etree.xpath('/taxii_11:*/taxii_11:Extended_Headers/taxii_11:Extended_Header', namespaces=ns_map)
        extended_headers = {}
        for header in extended_header_list:
            eh_name = header.xpath('./@name')[0]
            if len(header) == 0:  # This has string content
                eh_value = header.text
            else:  # This has XML content
                eh_value = header[0]

            extended_headers[eh_name] = eh_value

        return cls(message_id, extended_headers=extended_headers, **kwargs)


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


class TAXIIRequestMessage(TAXIIMessage):

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value


class DiscoveryRequest(TAXIIRequestMessage):

    """
    A TAXII Discovery Request message.

    Args:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
    """

    message_type = MSG_DISCOVERY_REQUEST


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
        s = super(DiscoveryResponse, self).to_text()
        for si in self.service_instances:
            s += si.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['service_instances'] = []
        service_instance_set = etree_xml.xpath('./taxii_11:Service_Instance', namespaces=ns_map)
        for service_instance in service_instance_set:
            si = ServiceInstance.from_etree(service_instance)
            kwargs['service_instances'].append(si)

        return super(DiscoveryResponse, cls).from_etree(etree_xml, **kwargs)

    @classmethod
    def from_dict(cls, d):
        msg = super(DiscoveryResponse, cls).from_dict(d)
        msg.service_instances = []
        service_instance_set = d['service_instances']
        for service_instance in service_instance_set:
            si = ServiceInstance.from_dict(service_instance)
            msg.service_instances.append(si)
        return msg


class ServiceInstance(TAXIIBase11):

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
        inbox_service_accepted_content (list of ContentBinding objects): identifies
            content bindings that this Inbox Service is willing to accept.
            **Optional**
        available (boolean): indicates whether the identity of the
            requester (authenticated or otherwise) is allowed to access this
            TAXII Service. **Optional**
        message (string): contains a message regarding this Service
            instance. **Optional**
        supported_query (SupportedQuery): contains a structure indicating a
            supported query. **Optional**

    The ``message_bindings`` list must contain at least one value. The
    ``supported_query`` parameter is optional when
    ``service_type`` is :py:data:`SVC_POLL`.
    """

    def __init__(self, service_type, services_version, protocol_binding,
                 service_address, message_bindings,
                 inbox_service_accepted_content=None, available=None,
                 message=None, supported_query=None):
        self.service_type = service_type
        self.services_version = services_version
        self.protocol_binding = protocol_binding
        self.service_address = service_address
        self.message_bindings = message_bindings
        self.inbox_service_accepted_content = inbox_service_accepted_content or []
        self.available = available
        self.message = message
        self.supported_query = supported_query or []

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
    def supported_query(self):
        return self._supported_query

    @supported_query.setter
    def supported_query(self, value):
        do_check(value, 'supported_query', type=SupportedQuery)
        self._supported_query = value

    @property
    def inbox_service_accepted_content(self):
        return self._inbox_service_accepted_content

    @inbox_service_accepted_content.setter
    def inbox_service_accepted_content(self, value):
        value = _sanitize_content_bindings(value)
        do_check(value, 'inbox_service_accepted_content', type=ContentBinding)
        self._inbox_service_accepted_content = value

    @property
    def available(self):
        return self._available

    @available.setter
    def available(self, value):
        do_check(value, 'available', value_tuple=(True, False), can_be_none=True)
        self._available = value

    def to_etree(self):
        si = etree.Element('{%s}Service_Instance' % ns_map['taxii_11'], nsmap=ns_map)
        si.attrib['service_type'] = self.service_type
        si.attrib['service_version'] = self.services_version
        if self.available is not None:
            si.attrib['available'] = str(self.available).lower()

        protocol_binding = etree.SubElement(si, '{%s}Protocol_Binding' % ns_map['taxii_11'], nsmap=ns_map)
        protocol_binding.text = self.protocol_binding

        service_address = etree.SubElement(si, '{%s}Address' % ns_map['taxii_11'], nsmap=ns_map)
        service_address.text = self.service_address

        for mb in self.message_bindings:
            message_binding = etree.SubElement(si, '{%s}Message_Binding' % ns_map['taxii_11'], nsmap=ns_map)
            message_binding.text = mb

        for sq in self.supported_query:
            si.append(sq.to_etree())

        for cb in self.inbox_service_accepted_content:
            content_binding = cb.to_etree()
            si.append(content_binding)

        if self.message is not None:
            message = etree.SubElement(si, '{%s}Message' % ns_map['taxii_11'], nsmap=ns_map)
            message.text = self.message

        return si

    def to_dict(self):
        d = {}
        d['service_type'] = self.service_type
        d['services_version'] = self.services_version
        d['protocol_binding'] = self.protocol_binding
        d['service_address'] = self.service_address
        d['message_bindings'] = self.message_bindings
        d['supported_query'] = []
        for sq in self.supported_query:
            d['supported_query'].append(sq.to_dict())
        d['inbox_service_accepted_content'] = self.inbox_service_accepted_content
        d['available'] = self.available
        d['message'] = self.message
        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Service Instance ===\n"
        s += line_prepend + "  Service Type: %s\n" % self.service_type
        s += line_prepend + "  Service Version: %s\n" % self.services_version
        s += line_prepend + "  Protocol Binding: %s\n" % self.protocol_binding
        s += line_prepend + "  Service Address: %s\n" % self.service_address
        for mb in self.message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % mb
        if self.service_type == SVC_INBOX:
            s += line_prepend + "  Inbox Service AC: %s\n" % [ac.to_text() for ac in self.inbox_service_accepted_content]
        s += line_prepend + "  Available: %s\n" % self.available
        s += line_prepend + "  Message: %s\n" % self.message
        for q in self.supported_query:
            s += q.to_text(line_prepend + STD_INDENT)

        return s

    @staticmethod
    def from_etree(etree_xml):  # Expects a taxii_11:Service_Instance element
        service_type = etree_xml.attrib['service_type']
        services_version = etree_xml.attrib['service_version']
        available = None
        if etree_xml.attrib.get('available'):
            tmp_available = etree_xml.attrib['available']
            available = tmp_available == 'true'

        protocol_binding = get_required(etree_xml, './taxii_11:Protocol_Binding', ns_map).text
        service_address = get_required(etree_xml, './taxii_11:Address', ns_map).text

        message_bindings = []
        message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        for mb in message_binding_set:
            message_bindings.append(mb.text)

        inbox_service_accepted_content = []
        inbox_service_accepted_content_set = etree_xml.xpath('./taxii_11:Content_Binding', namespaces=ns_map)
        for cb in inbox_service_accepted_content_set:
            inbox_service_accepted_content.append(ContentBinding.from_etree(cb))

        supported_query = []
        supported_query_set = etree_xml.xpath('./taxii_11:Supported_Query', namespaces=ns_map)
        for sq in supported_query_set:
            format_id = sq.xpath('./@format_id')[0]
            query_obj = get_deserializer(format_id, 'query_info').from_etree(sq)
            supported_query.append(query_obj)

        message = get_optional_text(etree_xml, './taxii_11:Message', ns_map)

        return ServiceInstance(service_type,
                               services_version,
                               protocol_binding,
                               service_address,
                               message_bindings,
                               inbox_service_accepted_content,
                               available,
                               message,
                               supported_query)

    @staticmethod
    def from_dict(d):
        service_type = d['service_type']
        services_version = d['services_version']
        protocol_binding = d['protocol_binding']
        service_address = d['service_address']
        message_bindings = d['message_bindings']
        supported_query = []
        sq_list = d.get('supported_query')
        if sq_list is not None:
            for sq in sq_list:
                format_id = sq['format_id']
                query_obj = get_deserializer(format_id, 'query_info').from_dict(sq)
                supported_query.append(query_obj)
        inbox_service_accepted_content = d.get('inbox_service_accepted_content')
        available = d.get('available')
        message = d.get('message')

        return ServiceInstance(service_type,
                               services_version,
                               protocol_binding,
                               service_address,
                               message_bindings,
                               inbox_service_accepted_content,
                               available,
                               message,
                               supported_query)


class CollectionInformationRequest(TAXIIRequestMessage):

    """
    A TAXII Collection Information Request message.

    Args:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
    """

    message_type = MSG_COLLECTION_INFORMATION_REQUEST


class CollectionInformationResponse(TAXIIMessage):

    """
    A TAXII Collection Information Response message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Optional**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        collection_informations (list of CollectionInformation objects): A list
            of CollectionInformation objects to be contained in this response.
            **Optional**
    """
    message_type = MSG_COLLECTION_INFORMATION_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None, collection_informations=None):
        super(CollectionInformationResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.collection_informations = collection_informations or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=uri_regex)
        self._in_response_to = value

    @property
    def collection_informations(self):
        return self._collection_informations

    @collection_informations.setter
    def collection_informations(self, value):
        do_check(value, 'collection_informations', type=CollectionInformation)
        self._collection_informations = value

    def to_etree(self):
        xml = super(CollectionInformationResponse, self).to_etree()
        for collection in self.collection_informations:
            xml.append(collection.to_etree())
        return xml

    def to_dict(self):
        d = super(CollectionInformationResponse, self).to_dict()
        d['collection_informations'] = []
        for collection in self.collection_informations:
            d['collection_informations'].append(collection.to_dict())
        return d

    def to_text(self, line_prepend=''):
        s = super(CollectionInformationResponse, self).to_text(line_prepend)
        s += line_prepend + "Contains %s Collection Informations\n" % len(self.collection_informations)
        for collection in self.collection_informations:
            s += collection.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        msg = super(CollectionInformationResponse, cls).from_etree(etree_xml)
        msg.collection_informations = []
        collection_informations = etree_xml.xpath('./taxii_11:Collection', namespaces=ns_map)
        for collection in collection_informations:
            msg.collection_informations.append(CollectionInformation.from_etree(collection))
        return msg

    @classmethod
    def from_dict(cls, d):
        msg = super(CollectionInformationResponse, cls).from_dict(d)
        msg.collection_informations = []
        for collection in d['collection_informations']:
            msg.collection_informations.append(CollectionInformation.from_dict(collection))
        return msg


class CollectionInformation(TAXIIBase11):

    """
    The Collection Information component of a TAXII Collection Information
    Response Message.

    Arguments:
        collection_name (str): the name by which this TAXII Data Collection is
            identified. **Required**
        collection_description (str): a prose description of this TAXII
            Data Collection. **Required**
        supported_contents (list of str): Content Binding IDs
            indicating which types of content are currently expressed in this
            TAXII Data Collection. **Optional**
        available (boolean): whether the identity of the requester
            (authenticated or otherwise) is allowed to access this TAXII
            Service. **Optional** Default: ``None``, indicating "unknown"
        push_methods (list of PushMethod objects): the protocols that
            can be used to push content via a subscription. **Optional**
        polling_service_instances (list of PollingServiceInstance objects):
            the bindings and address a Consumer can use to interact with a
            Poll Service instance that supports this TAXII Data Collection.
            **Optional**
        subscription_methods (list of SubscriptionMethod objects): the
            protocol and address of the TAXII Daemon hosting the Collection
            Management Service that can process subscriptions for this TAXII
            Data Collection. **Optional**
        collection_volume (int): the typical number of messages per day.
            **Optional**
        collection_type (str): the type ofo this collection. **Optional**,
            defaults to :py:data:`CT_DATA_FEED`.
        receiving_inbox_services (list of ReceivingInboxService objects):
            TODO: FILL THIS IN. **Optional**

    If ``supported_contents`` is omitted, then the collection supports all
    content bindings.  The absense of ``push_methods`` indicates no push
    methods.  The absense of ``polling_service_instances`` indicates no
    polling services.  The absense of ``subscription_methods`` indicates no
    subscription services.  The absense of ``receiving_inbox_services``
    indicates no receiving inbox services.
    """

    def __init__(self, collection_name, collection_description,
                 supported_contents=None, available=None, push_methods=None,
                 polling_service_instances=None, subscription_methods=None,
                 collection_volume=None, collection_type=CT_DATA_FEED,
                 receiving_inbox_services=None):
        self.collection_name = collection_name
        self.available = available
        self.collection_description = collection_description
        self.supported_contents = supported_contents or []
        self.push_methods = push_methods or []
        self.polling_service_instances = polling_service_instances or []
        self.subscription_methods = subscription_methods or []
        self.receiving_inbox_services = receiving_inbox_services or []
        self.collection_volume = collection_volume
        self.collection_type = collection_type

    @property
    def sort_key(self):
        return self.collection_name

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        do_check(value, 'collection_name', regex_tuple=uri_regex)
        self._collection_name = value

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
        value = _sanitize_content_bindings(value)
        do_check(value, 'supported_contents', type=ContentBinding)
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

    @property
    def receiving_inbox_services(self):
        return self._receiving_inbox_services

    @receiving_inbox_services.setter
    def receiving_inbox_services(self, value):
        do_check(value, 'receiving_inbox_services', type=ReceivingInboxService)
        self._receiving_inbox_services = value

    @property
    def collection_volume(self):
        return self._collection_volume

    @collection_volume.setter
    def collection_volume(self, value):
        do_check(value, 'collection_volume', type=int, can_be_none=True)
        self._collection_volume = value

    @property
    def collection_type(self):
        return self._collection_type

    @collection_type.setter
    def collection_type(self, value):
        do_check(value, 'collection_type', value_tuple=CT_TYPES, can_be_none=True)
        self._collection_type = value

    def to_etree(self):
        c = etree.Element('{%s}Collection' % ns_map['taxii_11'], nsmap=ns_map)
        c.attrib['collection_name'] = self.collection_name
        if self.collection_type is not None:
            c.attrib['collection_type'] = self.collection_type
        if self.available is not None:
            c.attrib['available'] = str(self.available).lower()
        collection_description = etree.SubElement(c, '{%s}Description' % ns_map['taxii_11'], nsmap=ns_map)
        collection_description.text = self.collection_description

        if self.collection_volume is not None:
            collection_volume = etree.SubElement(c, '{%s}Collection_Volume' % ns_map['taxii_11'], nsmap=ns_map)
            collection_volume.text = str(self.collection_volume)

        for binding in self.supported_contents:
            c.append(binding.to_etree())

        for push_method in self.push_methods:
            c.append(push_method.to_etree())

        for polling_service in self.polling_service_instances:
            c.append(polling_service.to_etree())

        for subscription_method in self.subscription_methods:
            c.append(subscription_method.to_etree())

        for receiving_inbox_service in self.receiving_inbox_services:
            c.append(receiving_inbox_service.to_etree())

        return c

    def to_dict(self):
        d = {}
        d['collection_name'] = self.collection_name
        if self.collection_type is not None:
            d['collection_type'] = self.collection_type
        if self.available is not None:
            d['available'] = self.available
        d['collection_description'] = self.collection_description
        if self.collection_volume is not None:
            d['collection_volume'] = self.collection_volume
        # TODO: I think this isn't a good serialization, I think a for loop is necessary
        # This is probably a bug
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

        d['receiving_inbox_services'] = []
        for receiving_inbox_service in self.receiving_inbox_services:
            d['receiving_inbox_services'].append(receiving_inbox_service.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Data Collection Information ===\n"
        s += line_prepend + "  Collection Name: %s\n" % self.collection_name
        s += line_prepend + "  Collection Type: %s\n" % (self.collection_type if (None != self.collection_type) else CT_DATA_FEED)
        s += line_prepend + "  Available: %s\n" % self.available
        s += line_prepend + "  Collection Description: %s\n" % self.collection_description
        if self.collection_volume:
            s += line_prepend + "  Volume: %s\n" % self.collection_volume
        if len(self.supported_contents) == 0:  # All contents supported:
            s += line_prepend + "  Supported Content: %s\n" % "All"
        for contents in self.supported_contents:
            s += line_prepend + "  Supported Content: %s\n" % contents.to_text(line_prepend + STD_INDENT)
        for psi in self.polling_service_instances:
            s += psi.to_text(line_prepend + STD_INDENT)
        for sm in self.subscription_methods:
            s += sm.to_text(line_prepend + STD_INDENT)
        for ris in self.receiving_inbox_services:
            s += ris.to_text(line_prepend + STD_INDENT)
        s += line_prepend + "==================================\n\n"
        return s

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}
        kwargs['collection_name'] = etree_xml.attrib['collection_name']
        kwargs['collection_type'] = etree_xml.attrib.get('collection_type', None)

        kwargs['available'] = None
        if 'available' in etree_xml.attrib:
            tmp = etree_xml.attrib['available']
            kwargs['available'] = tmp.lower() == 'true'

        kwargs['collection_description'] = get_required(etree_xml, './taxii_11:Description', ns_map).text

        collection_volume_text = get_optional_text(etree_xml, './taxii_11:Collection_Volume', ns_map)
        if collection_volume_text:
            kwargs['collection_volume'] = int(collection_volume_text)

        kwargs['supported_contents'] = []
        supported_content_set = etree_xml.xpath('./taxii_11:Content_Binding', namespaces=ns_map)
        for binding_elt in supported_content_set:
            kwargs['supported_contents'].append(ContentBinding.from_etree(binding_elt))

        kwargs['push_methods'] = []
        push_method_set = etree_xml.xpath('./taxii_11:Push_Method', namespaces=ns_map)
        for push_method_elt in push_method_set:
            kwargs['push_methods'].append(PushMethod.from_etree(push_method_elt))

        kwargs['polling_service_instances'] = []
        polling_service_set = etree_xml.xpath('./taxii_11:Polling_Service', namespaces=ns_map)
        for polling_elt in polling_service_set:
            kwargs['polling_service_instances'].append(PollingServiceInstance.from_etree(polling_elt))

        kwargs['subscription_methods'] = []
        subscription_method_set = etree_xml.xpath('./taxii_11:Subscription_Service', namespaces=ns_map)
        for subscription_elt in subscription_method_set:
            kwargs['subscription_methods'].append(SubscriptionMethod.from_etree(subscription_elt))

        kwargs['receiving_inbox_services'] = []
        receiving_inbox_services_set = etree_xml.xpath('./taxii_11:Receiving_Inbox_Service', namespaces=ns_map)
        for receiving_inbox_service in receiving_inbox_services_set:
            kwargs['receiving_inbox_services'].append(ReceivingInboxService.from_etree(receiving_inbox_service))

        return CollectionInformation(**kwargs)


    @staticmethod
    def from_dict(d):
        kwargs = {}
        kwargs['collection_name'] = d['collection_name']
        kwargs['collection_type'] = d.get('collection_type')
        kwargs['available'] = d.get('available')
        kwargs['collection_description'] = d['collection_description']
        kwargs['collection_volume'] = d.get('collection_volume')

        kwargs['supported_contents'] = d.get('supported_contents', [])

        kwargs['push_methods'] = []
        for push_method in d.get('push_methods', []):
            kwargs['push_methods'].append(PushMethod.from_dict(push_method))

        kwargs['polling_service_instances'] = []
        for polling in d.get('polling_service_instances', []):
            kwargs['polling_service_instances'].append(PollingServiceInstance.from_dict(polling))

        kwargs['subscription_methods'] = []
        for subscription_method in d.get('subscription_methods', []):
            kwargs['subscription_methods'].append(SubscriptionMethod.from_dict(subscription_method))

        kwargs['receiving_inbox_services'] = []
        receiving_inbox_services_set = d.get('receiving_inbox_services', [])
        for receiving_inbox_service in receiving_inbox_services_set:
            kwargs['receiving_inbox_services'].append(ReceivingInboxService.from_dict(receiving_inbox_service))

        return CollectionInformation(**kwargs)


class PushMethod(TAXIIBase11):

    """
    The Push Method component of a TAXII Collection Information
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
        x = etree.Element('{%s}Push_Method' % ns_map['taxii_11'], nsmap=ns_map)
        proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii_11'], nsmap=ns_map)
        proto_bind.text = self.push_protocol
        for binding in self.push_message_bindings:
            b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii_11'], nsmap=ns_map)
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
        kwargs['push_protocol'] = get_required(etree_xml, './taxii_11:Protocol_Binding', ns_map).text

        kwargs['push_message_bindings'] = []
        message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        for message_binding in message_binding_set:
            kwargs['push_message_bindings'].append(message_binding.text)
        return PushMethod(**kwargs)

    @staticmethod
    def from_dict(d):
        return PushMethod(**d)


class PollingServiceInstance(TAXIIBase11):

    """
    The Polling Service Instance component of a TAXII Collection
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
        x = etree.Element('{%s}Polling_Service' % ns_map['taxii_11'], nsmap=ns_map)
        proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii_11'], nsmap=ns_map)
        proto_bind.text = self.poll_protocol
        address = etree.SubElement(x, '{%s}Address' % ns_map['taxii_11'], nsmap=ns_map)
        address.text = self.poll_address
        for binding in self.poll_message_bindings:
            b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii_11'], nsmap=ns_map)
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
        s = line_prepend + "=== Polling Service Instance ===\n"
        s += line_prepend + "  Poll Protocol: %s\n" % self.poll_protocol
        s += line_prepend + "  Poll Address: %s\n" % self.poll_address
        for binding in self.poll_message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % binding
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        protocol = get_required(etree_xml, './taxii_11:Protocol_Binding', ns_map).text
        addr = get_required(etree_xml, './taxii_11:Address', ns_map).text

        bindings = []
        message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        for message_binding in message_binding_set:
            bindings.append(message_binding.text)
        return cls(protocol, addr, bindings)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class SubscriptionMethod(TAXIIBase11):

    """
    The Subscription Method component of a TAXII Collection Information
    component.

    Args:
        subscription_protocol (str): the protocol binding supported by
            this Collection Management Service instance. **Required**
        subscription_address (str): the address of the TAXII Daemon
            hosting this Collection Management Service instance.
            **Required**.
        subscription_message_bindings (list of str): the message
            bindings supported by this Collection Management Service
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
        x = etree.Element('{%s}%s' % (ns_map['taxii_11'], self.NAME))
        proto_bind = etree.SubElement(x, '{%s}Protocol_Binding' % ns_map['taxii_11'], nsmap=ns_map)
        proto_bind.text = self.subscription_protocol
        address = etree.SubElement(x, '{%s}Address' % ns_map['taxii_11'], nsmap=ns_map)
        address.text = self.subscription_address
        for binding in self.subscription_message_bindings:
            b = etree.SubElement(x, '{%s}Message_Binding' % ns_map['taxii_11'], nsmap=ns_map)
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
        s = line_prepend + "=== Subscription Service ===\n"
        s += line_prepend + "  Protocol Binding: %s\n" % self.subscription_protocol
        s += line_prepend + "  Address: %s\n" % self.subscription_address
        for mb in self.subscription_message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % mb
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        protocol = get_required(etree_xml, './taxii_11:Protocol_Binding', ns_map).text
        addr = get_required(etree_xml, './taxii_11:Address', ns_map).text
        bindings = []
        message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        for message_binding in message_binding_set:
            bindings.append(message_binding.text)
        return cls(protocol, addr, bindings)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class ReceivingInboxService(TAXIIBase11):

    """
    The Receiving Inbox Service component of a TAXII Collection
    Information component.

    Args:
        inbox_protocol (str): Indicates the protocol this Inbox Service
            uses. **Required**
        inbox address (str): Indicates the address of this Inbox Service.
            **Required**
        inbox_message_bindings (list of str): Each string indicates a
            message binding that this inbox service uses. **Required**
        supported_contents (list of ContentBinding objects): Each object
            indicates a Content Binding this inbox service can receive.
            **Optional**.  Setting to ``None`` means that all Content
            Bindings are supported.
    """

    def __init__(self, inbox_protocol, inbox_address,
                 inbox_message_bindings, supported_contents=None):
        self.inbox_protocol = inbox_protocol
        self.inbox_address = inbox_address
        self.inbox_message_bindings = inbox_message_bindings
        self.supported_contents = supported_contents or []

    @property
    def sort_key(self):
        return self.inbox_address

    @property
    def inbox_protocol(self):
        return self._inbox_protocol

    @inbox_protocol.setter
    def inbox_protocol(self, value):
        do_check(value, 'inbox_protocol', type=six.string_types, regex_tuple=uri_regex)
        self._inbox_protocol = value

    @property
    def inbox_address(self):
        return self._inbox_address

    @inbox_address.setter
    def inbox_address(self, value):
        self._inbox_address = value

    @property
    def inbox_message_bindings(self):
        return self._inbox_message_bindings

    @inbox_message_bindings.setter
    def inbox_message_bindings(self, value):
        do_check(value, 'inbox_message_bindings', regex_tuple=uri_regex)
        self._inbox_message_bindings = value

    @property
    def supported_contents(self):
        return self._supported_contents

    @supported_contents.setter
    def supported_contents(self, value):
        value = _sanitize_content_bindings(value)
        do_check(value, 'supported_contents', type=ContentBinding)
        self._supported_contents = value

    def to_etree(self):
        xml = etree.Element('{%s}Receiving_Inbox_Service' % ns_map['taxii_11'], nsmap=ns_map)

        pb = etree.SubElement(xml, '{%s}Protocol_Binding' % ns_map['taxii_11'])
        pb.text = self.inbox_protocol

        a = etree.SubElement(xml, '{%s}Address' % ns_map['taxii_11'])
        a.text = self.inbox_address

        for binding in self.inbox_message_bindings:
            mb = etree.SubElement(xml, '{%s}Message_Binding' % ns_map['taxii_11'])
            mb.text = binding

        for binding in self.supported_contents:
            xml.append(binding.to_etree())

        return xml

    def to_dict(self):
        d = {}

        d['inbox_protocol'] = self.inbox_protocol
        d['inbox_address'] = self.inbox_address
        d['inbox_message_bindings'] = self.inbox_message_bindings
        d['supported_contents'] = []
        for supported_content in self.supported_contents:
            d['supported_contents'].append(supported_content.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Receiving Inbox Service ===\n"
        s += line_prepend + "  Protocol Binding: %s\n" % self.inbox_protocol
        s += line_prepend + "  Address: %s\n" % self.inbox_address
        for mb in self.inbox_message_bindings:
            s += line_prepend + "  Message Binding: %s\n" % mb
        if len(self.supported_contents) == 0:
            s += line_prepend + "  Supported Contents: All\n"
        for sc in self.supported_contents:
            s += line_prepend + "  Supported Content: %s\n" % str(sc)

        return s

    @staticmethod
    def from_etree(etree_xml):
        proto = get_required(etree_xml, './taxii_11:Protocol_Binding', ns_map).text
        addr = get_required(etree_xml, './taxii_11:Address', ns_map).text

        message_bindings = []
        message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        for mb in message_binding_set:
            message_bindings.append(mb.text)

        supported_contents = []
        supported_contents_set = etree_xml.xpath('./taxii_11:Content_Binding', namespaces=ns_map)
        for cb in supported_contents_set:
            supported_contents.append(ContentBinding.from_etree(cb))

        return ReceivingInboxService(proto, addr, message_bindings, supported_contents)

    @staticmethod
    def from_dict(d):
        kwargs = {}
        kwargs['inbox_protocol'] = d['inbox_protocol']
        kwargs['inbox_address'] = d['inbox_address']
        kwargs['inbox_message_bindings'] = d['inbox_message_bindings']
        kwargs['supported_contents'] = []
        for binding in d['supported_contents']:
            kwargs['supported_contents'].append(ContentBinding.from_dict(binding))

        return ReceivingInboxService(**kwargs)


class PollRequest(TAXIIRequestMessage):

    """
    A TAXII Poll Request message.

    Arguments:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        collection_name (str): the name of the TAXII Data Collection that is being
            polled. **Required**
        exclusive_begin_timestamp_label (datetime): a Timestamp Label
            indicating the beginning of the range of TAXII Data Feed content the
            requester wishes to receive. **Optional for a Data Feed, Prohibited
            for a Data Set**
        inclusive_end_timestamp_label (datetime): a Timestamp Label
            indicating the end of the range of TAXII Data Feed content the
            requester wishes to receive. **Optional for a Data Feed, Probited
            for a Data Set**
        subscription_id (str): the existing subscription the Consumer
            wishes to poll. **Optional**
        poll_parameters (list of PollParameters objects): the poll parameters
            for this request. **Optional**

    Exactly one of ``subscription_id`` and ``poll_parameters`` is **Required**.
    """
    message_type = MSG_POLL_REQUEST

    def __init__(self, message_id, extended_headers=None,
                 collection_name=None, exclusive_begin_timestamp_label=None,
                 inclusive_end_timestamp_label=None, subscription_id=None,
                 poll_parameters=None):
        super(PollRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.collection_name = collection_name
        self.exclusive_begin_timestamp_label = exclusive_begin_timestamp_label
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.subscription_id = subscription_id
        self.poll_parameters = poll_parameters

        if subscription_id is None and poll_parameters is None:
            raise ValueError('One of subscription_id or poll_parameters must not be None')
        if subscription_id is not None and poll_parameters is not None:
            raise ValueError('Only one of subscription_id and poll_parameters can be present')

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', value_tuple=(None, None), can_be_none=True)
        self._in_response_to = value

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        do_check(value, 'collection_name', regex_tuple=uri_regex)
        self._collection_name = value

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
    def poll_parameters(self):
        return self._poll_parameters

    @poll_parameters.setter
    def poll_parameters(self, value):
        do_check(value, 'poll_parameters', type=PollParameters, can_be_none=True)
        self._poll_parameters = value

    def to_etree(self):
        xml = super(PollRequest, self).to_etree()
        xml.attrib['collection_name'] = self.collection_name

        if self.exclusive_begin_timestamp_label is not None:
            ebt = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii_11'], nsmap=ns_map)
            # TODO: Add TZ Info
            ebt.text = self.exclusive_begin_timestamp_label.isoformat()

        if self.inclusive_end_timestamp_label is not None:
            iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii_11'], nsmap=ns_map)
            # TODO: Add TZ Info
            iet.text = self.inclusive_end_timestamp_label.isoformat()

        if self.subscription_id is not None:
            si = etree.SubElement(xml, '{%s}Subscription_ID' % ns_map['taxii_11'], nsmap=ns_map)
            si.text = self.subscription_id

        if self.poll_parameters is not None:
            xml.append(self.poll_parameters.to_etree())

        return xml

    def to_dict(self):
        d = super(PollRequest, self).to_dict()
        d['collection_name'] = self.collection_name
        if self.subscription_id is not None:
            d['subscription_id'] = self.subscription_id
        if self.exclusive_begin_timestamp_label is not None:  # TODO: Add TZ Info
            d['exclusive_begin_timestamp_label'] = self.exclusive_begin_timestamp_label.isoformat()
        if self.inclusive_end_timestamp_label is not None:  # TODO: Add TZ Info
            d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        d['poll_parameters'] = None
        if self.poll_parameters is not None:
            d['poll_parameters'] = self.poll_parameters.to_dict()
        return d

    def to_text(self, line_prepend=''):
        s = super(PollRequest, self).to_text(line_prepend)
        s += line_prepend + "  Collection Name: %s\n" % self.collection_name
        if self.subscription_id:
            s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id
        s += line_prepend + "  Excl. Begin TS Label: %s\n" % self.exclusive_begin_timestamp_label
        s += line_prepend + "  Incl. End TS Label: %s\n" % self.inclusive_end_timestamp_label
        if self.poll_parameters:
            s += self.poll_parameters.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['collection_name'] = get_required(etree_xml, './@collection_name', ns_map)

        kwargs['exclusive_begin_timestamp_label'] = None

        begin_ts_text = get_optional_text(etree_xml, './taxii_11:Exclusive_Begin_Timestamp', ns_map)
        if begin_ts_text:
            kwargs['exclusive_begin_timestamp_label'] = parse_datetime_string(begin_ts_text)

        end_ts_text = get_optional_text(etree_xml, './taxii_11:Inclusive_End_Timestamp', ns_map)
        if end_ts_text:
            kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(end_ts_text)

        poll_parameter_el = get_optional(etree_xml, './taxii_11:Poll_Parameters', ns_map)
        if poll_parameter_el is not None:
            kwargs['poll_parameters'] = PollParameters.from_etree(poll_parameter_el)

        kwargs['subscription_id'] = get_optional_text(etree_xml, './taxii_11:Subscription_ID', ns_map)

        msg = super(PollRequest, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['collection_name'] = d['collection_name']

        kwargs['subscription_id'] = d.get('subscription_id')

        kwargs['exclusive_begin_timestamp_label'] = None
        if 'exclusive_begin_timestamp_label' in d:
            kwargs['exclusive_begin_timestamp_label'] = parse_datetime_string(d['exclusive_begin_timestamp_label'])

        kwargs['inclusive_end_timestamp_label'] = None
        if 'inclusive_end_timestamp_label' in d:
            kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(d['inclusive_end_timestamp_label'])

        kwargs['poll_parameters'] = None
        if 'poll_parameters' in d and d['poll_parameters'] is not None:
            kwargs['poll_parameters'] = PollParameters.from_dict(d['poll_parameters'])

        msg = super(PollRequest, cls).from_dict(d, **kwargs)
        return msg


class PollParameters(_GenericParameters):

    """
    The Poll Parameters component of a TAXII Poll Request message.

    Args:
        response_type (str): The requested response type. Must be either
            :py:data:`RT_FULL` or :py:data:`RT_COUNT_ONLY`. **Optional**,
            defaults to :py:data:`RT_FULL`
        content_bindings (list of ContentBinding objects): A list of Content
            Bindings acceptable in response. **Optional**
        query (Query): The query for this poll parameters. **Optional**
        allow_asynch (bool): Indicates whether the client supports
            asynchronous polling. **Optional**, defaults to ``False``
        delivery_parameters (DeliveryParameters): The requested delivery
            parameters for this object. **Optional**

    If ``content_bindings`` in not provided, this indicates that all
    bindings are accepted as a response.
    """
    name = 'Poll_Parameters'

    def __init__(self, response_type=RT_FULL, content_bindings=None,
                 query=None, allow_asynch=False, delivery_parameters=None):
        super(PollParameters, self).__init__(response_type, content_bindings, query)
        self.allow_asynch = allow_asynch
        self.delivery_parameters = delivery_parameters

    @property
    def delivery_parameters(self):
        return self._delivery_parameters

    @delivery_parameters.setter
    def delivery_parameters(self, value):
        do_check(value, 'delivery_parameters', type=DeliveryParameters, can_be_none=True)
        self._delivery_parameters = value

    @property
    def allow_asynch(self):
        return self._allow_asynch

    @allow_asynch.setter
    def allow_asynch(self, value):
        do_check(value, 'allow_asynch', value_tuple=(True, False), can_be_none=True)
        self._allow_asynch = value

    def to_etree(self):
        xml = super(PollParameters, self).to_etree()

        if self.allow_asynch is not None:
            xml.attrib['allow_asynch'] = str(self.allow_asynch).lower()

        if self.delivery_parameters is not None:
            xml.append(self.delivery_parameters.to_etree())
        return xml

    def to_dict(self):
        d = super(PollParameters, self).to_dict()
        if self.allow_asynch is not None:
            d['allow_asynch'] = str(self.allow_asynch).lower()
        d['delivery_parameters'] = None
        if self.delivery_parameters is not None:
            d['delivery_parameters'] = self.delivery_parameters.to_dict()
        return d

    def to_text(self, line_prepend=''):
        s = super(PollParameters, self).to_text(line_prepend)
        if self.allow_asynch:
            s += line_prepend + "  Allow Asynch: %s\n" % self.allow_asynch
        if self.delivery_parameters:
            s += self.delivery_parameters.to_text(line_prepend + STD_INDENT)
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        poll_parameters = super(PollParameters, cls).from_etree(etree_xml)

        allow_asynch_el = get_optional(etree_xml, './@allow_asynch', ns_map)
        poll_parameters.allow_asynch = allow_asynch_el == 'true'

        delivery_parameters_el = get_optional(etree_xml, './taxii_11:Delivery_Parameters', ns_map)
        if delivery_parameters_el is not None:
            poll_parameters.delivery_parameters = DeliveryParameters.from_etree(delivery_parameters_el)

        return poll_parameters

    @classmethod
    def from_dict(cls, d):
        poll_parameters = super(PollParameters, cls).from_dict(d)

        aa = d.get('allow_asynch')
        if aa is not None:
            poll_parameters.allow_asynch = aa == 'true'

        delivery_parameters = d.get('delivery_parameters')
        if delivery_parameters is not None:
            poll_parameters.delivery_parameters = DeliveryParameters.from_dict(delivery_parameters)

        return poll_parameters


class PollResponse(TAXIIMessage):

    """
    A TAXII Poll Response message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Optional**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        collection_name (str): the name of the TAXII Data Collection that was
            polled. **Required**
        exclusive_begin_timestamp_label (datetime): a Timestamp Label
            indicating the beginning of the range this response covers.
            **Optional for a Data Feed, Prohibited for a Data Set**
        inclusive_end_timestamp_label (datetime): a Timestamp Label
            indicating the end of the range this response covers. **Optional
            for a Data Feed, Prohibited for a Data Set**
        subscription_id (str): the Subscription ID for which this content
            is being provided. **Optional**
        message (str): additional information for the message recipient.
            **Optional**
        content_blocks (list of ContentBlock): piece of content
            and additional information related to the content. **Optional**
        more (bool): Whether there are more result parts. **Optional**, defaults
            to ``False``
        result_id (str): The ID of this result. **Optional**
        result_part_number (int): The result part number of this response.
             **Optional**
        record_count (RecordCount): The number of records and whether
             the count is a lower bound. **Optional**
    """
    message_type = MSG_POLL_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None,
                 collection_name=None, exclusive_begin_timestamp_label=None,
                 inclusive_end_timestamp_label=None, subscription_id=None,
                 message=None, content_blocks=None, more=False, result_id=None,
                 result_part_number=1, record_count=None):
        super(PollResponse, self).__init__(message_id, in_response_to, extended_headers)
        self.collection_name = collection_name
        self.exclusive_begin_timestamp_label = exclusive_begin_timestamp_label
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label
        self.subscription_id = subscription_id
        self.message = message
        self.content_blocks = content_blocks or []
        self.more = more
        self.result_part_number = result_part_number
        self.result_id = result_id
        self.record_count = record_count

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=uri_regex)
        self._in_response_to = value

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        do_check(value, 'collection_name', regex_tuple=uri_regex)
        self._collection_name = value

    @property
    def inclusive_end_timestamp_label(self):
        return self._inclusive_end_timestamp_label

    @inclusive_end_timestamp_label.setter
    def inclusive_end_timestamp_label(self, value):
        value = check_timestamp_label(value, 'inclusive_end_timestamp_label', can_be_none=True)
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

    @property
    def more(self):
        return self._more

    @more.setter
    def more(self, value):
        do_check(value, 'more', value_tuple=(True, False))
        self._more = value

    @property
    def result_id(self):
        return self._result_id

    @result_id.setter
    def result_id(self, value):
        do_check(value, 'result_id', regex_tuple=uri_regex, can_be_none=True)
        self._result_id = value

    @property
    def result_part_number(self):
        return self._result_part_number

    @result_part_number.setter
    def result_part_number(self, value):
        do_check(value, 'result_part_number', type=int, can_be_none=True)
        self._result_part_number = value

    @property
    def record_count(self):
        return self._record_count

    @record_count.setter
    def record_count(self, value):
        do_check(value, 'record_count', type=RecordCount, can_be_none=True)
        self._record_count = value

    def to_etree(self):
        xml = super(PollResponse, self).to_etree()
        xml.attrib['collection_name'] = self.collection_name
        if self.result_id is not None:
            xml.attrib['result_id'] = self.result_id

        if self.more is not None:
            xml.attrib['more'] = str(self.more).lower()

        if self.result_part_number is not None:
            xml.attrib['result_part_number'] = str(self.result_part_number)

        if self.subscription_id is not None:
            si = etree.SubElement(xml, '{%s}Subscription_ID' % ns_map['taxii_11'])
            si.text = self.subscription_id

        if self.exclusive_begin_timestamp_label:
            ibt = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii_11'])
            ibt.text = self.exclusive_begin_timestamp_label.isoformat()

        if self.inclusive_end_timestamp_label:
            iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii_11'])
            iet.text = self.inclusive_end_timestamp_label.isoformat()

        if self.record_count:
            xml.append(self.record_count.to_etree())

        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii_11'])
            m.text = self.message

        for block in self.content_blocks:
            xml.append(block.to_etree())

        return xml

    def to_dict(self):
        d = super(PollResponse, self).to_dict()

        d['collection_name'] = self.collection_name
        d['more'] = self.more
        d['result_id'] = self.result_id
        d['result_part_number'] = self.result_part_number
        if self.record_count is not None:
            d['record_count'] = self.record_count.to_dict()
        if self.subscription_id is not None:
            d['subscription_id'] = self.subscription_id
        if self.message is not None:
            d['message'] = self.message
        if self.exclusive_begin_timestamp_label is not None:
            d['exclusive_begin_timestamp_label'] = self.exclusive_begin_timestamp_label.isoformat()
        if self.inclusive_end_timestamp_label is not None:
            d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        d['content_blocks'] = []
        for block in self.content_blocks:
            d['content_blocks'].append(block.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = super(PollResponse, self).to_text(line_prepend)
        s += line_prepend + "  Collection Name: %s\n" % self.collection_name
        s += line_prepend + "  More: %s\n" % self.more
        s += line_prepend + "  Result ID: %s\n" % self.result_id
        if self.result_part_number:
            s += line_prepend + "  Result Part Num: %s\n" % self.result_part_number
        if self.record_count:
            s += self.record_count.to_text(line_prepend + STD_INDENT)
        if self.subscription_id:
            s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id
        if self.message:
            s += line_prepend + "  Message: %s\n" % self.message
        if self.exclusive_begin_timestamp_label:
            s += line_prepend + "  Excl. Begin TS Label: %s\n" % self.exclusive_begin_timestamp_label.isoformat()
        if self.inclusive_end_timestamp_label:
            s += line_prepend + "  Incl. End TS Label: %s\n" % self.inclusive_end_timestamp_label.isoformat()
        for cb in self.content_blocks:
            s += cb.to_text(line_prepend + STD_INDENT)
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}

        kwargs['collection_name'] = get_required(etree_xml, './@collection_name', ns_map)
        kwargs['more'] = etree_xml.attrib.get('more', 'false') == 'true'
        kwargs['subscription_id'] = None
        kwargs['result_id'] = etree_xml.attrib.get('result_id')
        rpn = etree_xml.attrib.get('result_part_number', None)
        if rpn:
            kwargs['result_part_number'] = int(rpn)

        kwargs['subscription_id'] = get_optional_text(etree_xml, './taxii_11:Subscription_ID', ns_map)
        kwargs['message'] = get_optional_text(etree_xml, './taxii_11:Message', ns_map)

        ebts_text = get_optional_text(etree_xml, './taxii_11:Exclusive_Begin_Timestamp', ns_map)
        if ebts_text:
            kwargs['exclusive_begin_timestamp_label'] = parse_datetime_string(ebts_text)

        iets_text = get_optional_text(etree_xml, './taxii_11:Inclusive_End_Timestamp', ns_map)
        if iets_text:
            kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(iets_text)

        kwargs['content_blocks'] = []
        for block in etree_xml.xpath('./taxii_11:Content_Block', namespaces=ns_map):
            kwargs['content_blocks'].append(ContentBlock.from_etree(block))

        record_count_el = get_optional(etree_xml, './taxii_11:Record_Count', ns_map)
        if record_count_el is not None:
            kwargs['record_count'] = RecordCount.from_etree(record_count_el)

        msg = super(PollResponse, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['collection_name'] = d['collection_name']
        kwargs['result_id'] = d.get('result_id')
        kwargs['result_part_number'] = d.get('result_part_number')
        kwargs['message'] = None
        if 'message' in d:
            kwargs['message'] = d['message']

        kwargs['subscription_id'] = d.get('subscription_id')
        kwargs['more'] = d.get('more', False)

        kwargs['exclusive_begin_timestamp_label'] = None
        if 'exclusive_begin_timestamp_label' in d:
            kwargs['exclusive_begin_timestamp_label'] = parse_datetime_string(d['exclusive_begin_timestamp_label'])

        kwargs['record_count'] = None
        if 'record_count' in d:
            kwargs['record_count'] = RecordCount.from_dict(d['record_count'])

        kwargs['inclusive_end_timestamp_label'] = None
        if 'inclusive_end_timestamp_label' in d:
            kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(d['inclusive_end_timestamp_label'])

        kwargs['content_blocks'] = []
        for block in d['content_blocks']:
            kwargs['content_blocks'].append(ContentBlock.from_dict(block))
        msg = super(PollResponse, cls).from_dict(d, **kwargs)
        return msg


_StatusDetail = collections.namedtuple('_StatusDetail', ['name', 'required', 'type', 'multiple'])
_DCE_AcceptableDestination = _StatusDetail(SD_ACCEPTABLE_DESTINATION, False, str, True)
_IRP_MaxPartNumber = _StatusDetail(SD_MAX_PART_NUMBER, True, int, False)
_NF_Item = _StatusDetail(SD_ITEM, False, str, False)
_P_EstimatedWait = _StatusDetail(SD_ESTIMATED_WAIT, True, int, False)
_P_ResultId = _StatusDetail(SD_RESULT_ID, True, str, False)
_P_WillPush = _StatusDetail(SD_WILL_PUSH, True, bool, False)
_R_EstimatedWait = _StatusDetail(SD_ESTIMATED_WAIT, False, int, False)
_UM_SupportedBinding = _StatusDetail(SD_SUPPORTED_BINDING, False, str, True)
_UC_SupportedContent = _StatusDetail(SD_SUPPORTED_CONTENT, False, ContentBinding, True)
_UP_SupportedProtocol = _StatusDetail(SD_SUPPORTED_PROTOCOL, False, str, True)
_UQ_SupportedQuery = _StatusDetail(SD_SUPPORTED_QUERY, False, str, True)


status_details = {
    ST_ASYNCHRONOUS_POLL_ERROR: {},
    ST_BAD_MESSAGE: {},
    ST_DENIED: {},
    ST_DESTINATION_COLLECTION_ERROR: {SD_ACCEPTABLE_DESTINATION: _DCE_AcceptableDestination},
    ST_FAILURE: {},
    ST_INVALID_RESPONSE_PART: {SD_MAX_PART_NUMBER: _IRP_MaxPartNumber},
    ST_NETWORK_ERROR: {},
    ST_NOT_FOUND: {SD_ITEM: _NF_Item},
    ST_PENDING: {SD_ESTIMATED_WAIT: _P_EstimatedWait,
                 SD_RESULT_ID: _P_ResultId,
                 SD_WILL_PUSH: _P_WillPush},
    ST_POLLING_UNSUPPORTED: {},
    ST_RETRY: {SD_ESTIMATED_WAIT: _R_EstimatedWait},
    ST_SUCCESS: {},
    ST_UNAUTHORIZED: {},
    ST_UNSUPPORTED_MESSAGE_BINDING: {SD_SUPPORTED_BINDING: _UM_SupportedBinding},
    ST_UNSUPPORTED_CONTENT_BINDING: {SD_SUPPORTED_CONTENT: _UC_SupportedContent},
    ST_UNSUPPORTED_PROTOCOL: {SD_SUPPORTED_PROTOCOL: _UP_SupportedProtocol},
    ST_UNSUPPORTED_QUERY: {SD_SUPPORTED_QUERY: _UQ_SupportedQuery}
}


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
        status_detail (dict): A field for additional information about
            this status in a machine-readable format. **Required or Optional**
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
        self.status_detail = status_detail or {}
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

    @property
    def status_detail(self):
        return self._status_detail

    @status_detail.setter
    def status_detail(self, value):
        do_check(list(value.keys()), 'status_detail.keys()', regex_tuple=uri_regex)
        detail_rules = status_details.get(self.status_type, {})
        # Check defined status types for conformance
        for sd_name, rules in six.iteritems(detail_rules):
            do_check(value.get(sd_name, None),
                     'status_detail[\'%s\']' % sd_name,
                     type=rules.type,
                     can_be_none=(not rules.required))

        self._status_detail = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        do_check(value, 'message', type=six.string_types, can_be_none=True)
        self._message = value

    def to_etree(self):
        xml = super(StatusMessage, self).to_etree()
        xml.attrib['status_type'] = self.status_type

        if len(self.status_detail) > 0:
            sd = etree.SubElement(xml, '{%s}Status_Detail' % ns_map['taxii_11'])
            for k, v in six.iteritems(self.status_detail):
                if not isinstance(v, list):
                    v = [v]
                for item in v:
                    d = etree.SubElement(sd, '{%s}Detail' % ns_map['taxii_11'])
                    d.attrib['name'] = k
                    if item in (True, False):
                        d.text = str(item).lower()
                    else:
                        d.text = str(item)

        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii_11'])
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
        s += line_prepend + "Status Type: %s\n" % self.status_type
        for k, v in six.iteritems(self.status_detail):
            s += line_prepend + "Status Detail: %s = %s\n" % (k, v)
        if self.message:
            s += line_prepend + "Message: %s\n" % self.message
        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}

        status_type = etree_xml.attrib['status_type']
        kwargs['status_type'] = status_type

        kwargs['status_detail'] = {}
        detail_set = etree_xml.xpath('./taxii_11:Status_Detail/taxii_11:Detail', namespaces=ns_map)
        for detail in detail_set:
            # TODO: This seems kind of hacky and should probably be improved
            name = detail.attrib['name']

            if status_type in status_details and name in status_details[status_type]:  # We have information for this status detail
                detail_info = status_details[status_type][name]
            else:  # We don't have information, so make something up
                detail_info = _StatusDetail('PlaceholderDetail', False, str, True)

            if detail_info.type == bool:
                v = detail.text.lower() == 'true'
            else:
                v = detail_info.type(detail.text)
            if detail_info.multiple:  # There can be multiple instances of this item
                if name not in kwargs['status_detail']:
                    kwargs['status_detail'][name] = v
                else:  # It already exists
                    if not isinstance(kwargs['status_detail'], list):
                        kwargs['status_detail'][name] = [kwargs['status_detail'][name]]  # Make it a list
                    kwargs['status_detail'][name].append(v)
            else:
                kwargs['status_detail'][name] = v

        kwargs['message'] = None
        m_set = etree_xml.xpath('./taxii_11:Message', namespaces=ns_map)
        if len(m_set) > 0:
            kwargs['message'] = m_set[0].text

        msg = super(StatusMessage, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['status_type'] = d['status_type']
        kwargs['status_detail'] = d.get('status_detail')
        kwargs['message'] = d.get('message')

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
        result_id (str): the result id. **Optional**
        destination_collection_names (list of str): Each string indicates a
             destination collection name. **Optional**
        subscription_information (SubscriptionInformation): This
            field is only present if this message is being sent to provide
            content in accordance with an existing TAXII Data Collection
            subscription. **Optional**
        record_count (RecordCount): The number of records and whether
             the count is a lower bound. **Optional**
        content_blocks (list of ContentBlock): Inbox content. **Optional**
    """
    message_type = MSG_INBOX_MESSAGE

    def __init__(self, message_id, in_response_to=None, extended_headers=None,
                 message=None, result_id=None, destination_collection_names=None,
                 subscription_information=None, record_count=None,
                 content_blocks=None):

        super(InboxMessage, self).__init__(message_id, extended_headers=extended_headers)
        self.subscription_information = subscription_information
        self.message = message
        self.result_id = result_id
        self.destination_collection_names = destination_collection_names or []
        self.subscription_information = subscription_information
        self.record_count = record_count
        self.content_blocks = content_blocks or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
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

    @property
    def result_id(self):
        return self._result_id

    @result_id.setter
    def result_id(self, value):
        do_check(value, 'result_id', regex_tuple=uri_regex, can_be_none=True)
        self._result_id = value

    @property
    def destination_collection_names(self):
        return self._destination_collection_names

    @destination_collection_names.setter
    def destination_collection_names(self, value):
        do_check(value, 'destination_collection_names', regex_tuple=uri_regex)
        self._destination_collection_names = value

    @property
    def record_count(self):
        return self._record_count

    @record_count.setter
    def record_count(self, value):
        do_check(value, 'record_count', type=RecordCount, can_be_none=True)
        self._record_count = value

    def to_etree(self):
        xml = super(InboxMessage, self).to_etree()

        if self.result_id is not None:
            xml.attrib['result_id'] = self.result_id

        for dcn in self.destination_collection_names:
            d = etree.SubElement(xml, '{%s}Destination_Collection_Name' % ns_map['taxii_11'], nsmap=ns_map)
            d.text = dcn

        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii_11'])
            m.text = self.message

        if self.subscription_information is not None:
            xml.append(self.subscription_information.to_etree())

        if self.record_count is not None:
            xml.append(self.record_count.to_etree())

        for block in self.content_blocks:
            xml.append(block.to_etree())

        return xml

    def to_dict(self):
        d = super(InboxMessage, self).to_dict()

        if self.result_id is not None:
            d['result_id'] = self.result_id

        d['destination_collection_names'] = []
        for dcn in self.destination_collection_names:
            d['destination_collection_names'].append(dcn)

        if self.message is not None:
            d['message'] = self.message

        if self.subscription_information is not None:
            d['subscription_information'] = self.subscription_information.to_dict()

        if self.record_count is not None:
            d['record_count'] = self.record_count.to_dict()

        d['content_blocks'] = []
        for block in self.content_blocks:
            d['content_blocks'].append(block.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = super(InboxMessage, self).to_text(line_prepend)
        if self.result_id:
            s += line_prepend + "  Result ID: %s\n" % self.result_id
        for dcn in self.destination_collection_names:
            s += line_prepend + "  Destination Collection Name: %s\n" % dcn
        s += line_prepend + "  Message: %s\n" % self.message
        if self.subscription_information:
            s += self.subscription_information.to_text(line_prepend + STD_INDENT)
        if self.record_count:
            s += self.record_count.to_text(line_prepend + STD_INDENT)
        s += line_prepend + "  Message has %s Content Blocks\n" % len(self.content_blocks)
        for cb in self.content_blocks:
            s += cb.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}

        result_id_set = etree_xml.xpath('./@result_id')
        if len(result_id_set) > 0:
            kwargs['result_id'] = result_id_set[0]

        kwargs['destination_collection_names'] = []
        dcn_set = etree_xml.xpath('./taxii_11:Destination_Collection_Name', namespaces=ns_map)
        for dcn in dcn_set:
            kwargs['destination_collection_names'].append(dcn.text)

        msg_set = etree_xml.xpath('./taxii_11:Message', namespaces=ns_map)
        if len(msg_set) > 0:
            kwargs['message'] = msg_set[0].text

        subs_infos = etree_xml.xpath('./taxii_11:Source_Subscription', namespaces=ns_map)
        if len(subs_infos) > 0:
            kwargs['subscription_information'] = SubscriptionInformation.from_etree(subs_infos[0])

        record_count_set = etree_xml.xpath('./taxii_11:Record_Count', namespaces=ns_map)
        if len(record_count_set) > 0:
            kwargs['record_count'] = RecordCount.from_etree(record_count_set[0])

        content_blocks = etree_xml.xpath('./taxii_11:Content_Block', namespaces=ns_map)
        kwargs['content_blocks'] = []
        for block in content_blocks:
            kwargs['content_blocks'].append(ContentBlock.from_etree(block))

        msg = super(InboxMessage, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):

        kwargs = {}

        kwargs['result_id'] = d.get('result_id')

        kwargs['destination_collection_names'] = []
        if 'destination_collection_names' in d:
            for dcn in d['destination_collection_names']:
                kwargs['destination_collection_names'].append(dcn)

        kwargs['message'] = d.get('message')

        kwargs['subscription_information'] = None
        if 'subscription_information' in d:
            kwargs['subscription_information'] = SubscriptionInformation.from_dict(d['subscription_information'])

        if 'record_count' in d:
            kwargs['record_count'] = RecordCount.from_dict(d['record_count'])

        kwargs['content_blocks'] = []
        for block in d['content_blocks']:
            kwargs['content_blocks'].append(ContentBlock.from_dict(block))

        msg = super(InboxMessage, cls).from_dict(d, **kwargs)
        return msg


class SubscriptionInformation(TAXIIBase11):

    """
    The Subscription Information component of a TAXII Inbox message.

    Arguments:
        collection_name (str): the name of the TAXII Data Collection from
            which this content is being provided. **Required**
        subscription_id (str): the Subscription ID for which this
            content is being provided. **Required**
        exclusive_begin_timestamp_label (datetime): a Timestamp Label
            indicating the beginning of the time range this Inbox Message
            covers. **Optional for a Data Feed, Prohibited for a Data Set**
        inclusive_end_timestamp_label (datetime): a Timestamp Label
            indicating the end of the time range this Inbox Message covers.
            **Optional for a Data Feed, Prohibited for a Data Set**
    """

    def __init__(self, collection_name, subscription_id, exclusive_begin_timestamp_label=None, inclusive_end_timestamp_label=None):
        self.collection_name = collection_name
        self.subscription_id = subscription_id
        self.exclusive_begin_timestamp_label = exclusive_begin_timestamp_label
        self.inclusive_end_timestamp_label = inclusive_end_timestamp_label

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        do_check(value, 'collection_name', regex_tuple=uri_regex)
        self._collection_name = value

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        do_check(value, 'subscription_id', regex_tuple=uri_regex)
        self._subscription_id = value

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

    def to_etree(self):
        xml = etree.Element('{%s}Source_Subscription' % ns_map['taxii_11'])
        xml.attrib['collection_name'] = self.collection_name
        si = etree.SubElement(xml, '{%s}Subscription_ID' % ns_map['taxii_11'])
        si.text = self.subscription_id

        if self.exclusive_begin_timestamp_label:
            ebtl = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii_11'])
            ebtl.text = self.exclusive_begin_timestamp_label.isoformat()

        if self.inclusive_end_timestamp_label:
            ietl = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii_11'])
            ietl.text = self.inclusive_end_timestamp_label.isoformat()

        return xml

    def to_dict(self):
        d = {}
        d['collection_name'] = self.collection_name
        d['subscription_id'] = self.subscription_id
        if self.exclusive_begin_timestamp_label:
            d['exclusive_begin_timestamp_label'] = self.exclusive_begin_timestamp_label.isoformat()
        if self.inclusive_end_timestamp_label:
            d['inclusive_end_timestamp_label'] = self.inclusive_end_timestamp_label.isoformat()
        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Source Subscription ===\n"
        s += line_prepend + "  Collection Name: %s\n" % self.collection_name
        s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id

        if self.exclusive_begin_timestamp_label:
            s += line_prepend + "  Excl. Begin TS Label: %s\n" % self.exclusive_begin_timestamp_label.isoformat()
        else:
            s += line_prepend + "  Excl. Begin TS Label: %s\n" % None

        if self.inclusive_end_timestamp_label:
            s += line_prepend + "  Incl. End TS Label: %s\n" % self.inclusive_end_timestamp_label.isoformat()
        else:
            s += line_prepend + "  Incl. End TS Label: %s\n" % None
        return s

    @staticmethod
    def from_etree(etree_xml):
        collection_name = etree_xml.attrib['collection_name']
        subscription_id = get_required(etree_xml, './taxii_11:Subscription_ID', ns_map).text

        begin_ts_text = get_optional_text(etree_xml, './taxii_11:Exclusive_Begin_Timestamp', ns_map)
        ebtl = parse_datetime_string(begin_ts_text) if begin_ts_text else None

        end_ts_text = get_optional_text(etree_xml, './taxii_11:Inclusive_End_Timestamp', ns_map)
        ietl = parse_datetime_string(end_ts_text) if end_ts_text else None

        return SubscriptionInformation(collection_name, subscription_id, ebtl, ietl)

    @staticmethod
    def from_dict(d):
        collection_name = d['collection_name']
        subscription_id = d['subscription_id']

        ebtl = parse_datetime_string(d.get('exclusive_begin_timestamp_label'))
        ietl = parse_datetime_string(d.get('inclusive_end_timestamp_label'))

        return SubscriptionInformation(collection_name, subscription_id, ebtl, ietl)


class ManageCollectionSubscriptionRequest(TAXIIRequestMessage):

    """
    A TAXII Manage Collection Subscription Request message.

    Args:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        collection_name (str): the name of the TAXII Data Collection to which the
            action applies. **Required**
        action (str): the requested action to take. **Required**
        subscription_id (str): the ID of a previously created subscription.
            **Probibited** if ``action==``:py:data:`ACT_SUBSCRIBE`, else
            **Required**
        subscription_parameters (SubscriptionParameters): The parameters for
            this subscription. **Optional**
        push_parameters (list of PushParameter): the push parameters for this
            request. **Optional** Absence means push is not requested.
    """

    message_type = MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST

    def __init__(self, message_id, extended_headers=None,
                 collection_name=None, action=None, subscription_id=None,
                 subscription_parameters=None, push_parameters=None):

        super(ManageCollectionSubscriptionRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.collection_name = collection_name
        self.action = action
        self.subscription_id = subscription_id
        self.subscription_parameters = subscription_parameters or SubscriptionParameters()
        self.push_parameters = push_parameters

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        if value is not None:
            raise ValueError('in_response_to must be None')
        self._in_response_to = value

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        do_check(value, 'collection_name', regex_tuple=uri_regex)
        self._collection_name = value

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
    def subscription_parameters(self):
        return self._subscription_parameters

    @subscription_parameters.setter
    def subscription_parameters(self, value):
        do_check(value, 'subscription_parameters', type=SubscriptionParameters, can_be_none=True)
        self._subscription_parameters = value

    @property
    def push_parameters(self):
        return self._push_parameters

    @push_parameters.setter
    def push_parameters(self, value):
        do_check(value, 'push_parameters', type=PushParameters, can_be_none=True)
        self._push_parameters = value

    def to_etree(self):
        xml = super(ManageCollectionSubscriptionRequest, self).to_etree()
        xml.attrib['collection_name'] = self.collection_name
        xml.attrib['action'] = self.action
        if self.subscription_id is not None:
            si = etree.SubElement(xml, '{%s}Subscription_ID' % ns_map['taxii_11'])
            si.text = self.subscription_id

        if self.action == ACT_SUBSCRIBE:
            xml.append(self.subscription_parameters.to_etree())

        if self.action == ACT_SUBSCRIBE and self.push_parameters:
            xml.append(self.push_parameters.to_etree())
        return xml

    def to_dict(self):
        d = super(ManageCollectionSubscriptionRequest, self).to_dict()
        d['collection_name'] = self.collection_name
        d['action'] = self.action

        if self.subscription_id is not None:
            d['subscription_id'] = self.subscription_id

        if self.action == ACT_SUBSCRIBE:
            d['subscription_parameters'] = self.subscription_parameters.to_dict()

        if self.action == ACT_SUBSCRIBE and self.push_parameters:
            d['push_parameters'] = self.push_parameters.to_dict()

        return d

    def to_text(self, line_prepend=''):
        s = super(ManageCollectionSubscriptionRequest, self).to_text(line_prepend)
        s += line_prepend + "  Collection Name: %s\n" % self.collection_name
        s += line_prepend + "  Action: %s\n" % self.action
        s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id

        if self.action == ACT_SUBSCRIBE:
            s += self.subscription_parameters.to_text(line_prepend + STD_INDENT)

        if self.action == ACT_SUBSCRIBE and self.push_parameters:
            s += self.push_parameters.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):

        kwargs = {}
        kwargs['collection_name'] = get_required(etree_xml, './@collection_name', ns_map)
        kwargs['action'] = get_required(etree_xml, './@action', ns_map)

        kwargs['subscription_id'] = get_optional_text(etree_xml, './taxii_11:Subscription_ID', ns_map)

        subscription_parameters_el = get_optional(etree_xml, './taxii_11:Subscription_Parameters', ns_map)
        if subscription_parameters_el is not None:
            kwargs['subscription_parameters'] = SubscriptionParameters.from_etree(subscription_parameters_el)

        push_parameters_el = get_optional(etree_xml, './taxii_11:Push_Parameters', ns_map)
        if push_parameters_el is not None:
            kwargs['push_parameters'] = PushParameters.from_etree(push_parameters_el)

        msg = super(ManageCollectionSubscriptionRequest, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['collection_name'] = d['collection_name']
        kwargs['action'] = d['action']
        kwargs['subscription_id'] = d.get('subscription_id')

        kwargs['subscription_parameters'] = None
        if 'subscription_parameters' in d:
            kwargs['subscription_parameters'] = SubscriptionParameters.from_dict(d['subscription_parameters'])

        kwargs['push_parameters'] = None
        if 'push_parameters' in d:
            kwargs['push_parameters'] = PushParameters.from_dict(d['push_parameters'])

        msg = super(ManageCollectionSubscriptionRequest, cls).from_dict(d, **kwargs)
        return msg


class ManageCollectionSubscriptionResponse(TAXIIMessage):

    """
    A TAXII Manage Collection Subscription Response message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        collection_name (str): the name of the TAXII Data Collection to which
            the action applies. **Required**
        message (str): additional information for the message recipient.
            **Optional**
        subscription_instances (list of SubscriptionInstance): **Optional**
    """
    message_type = MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE

    def __init__(self, message_id, in_response_to, extended_headers=None, collection_name=None, message=None, subscription_instances=None):
        super(ManageCollectionSubscriptionResponse, self).__init__(message_id, in_response_to, extended_headers=extended_headers)
        self.collection_name = collection_name
        self.message = message
        self.subscription_instances = subscription_instances or []

    @TAXIIMessage.in_response_to.setter
    def in_response_to(self, value):
        do_check(value, 'in_response_to', regex_tuple=uri_regex)
        self._in_response_to = value

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        do_check(value, 'collection_name', regex_tuple=uri_regex)
        self._collection_name = value

    @property
    def subscription_instances(self):
        return self._subscription_instances

    @subscription_instances.setter
    def subscription_instances(self, value):
        do_check(value, 'subscription_instances', type=SubscriptionInstance)
        self._subscription_instances = value

    def to_etree(self):
        xml = super(ManageCollectionSubscriptionResponse, self).to_etree()
        xml.attrib['collection_name'] = self.collection_name
        if self.message is not None:
            m = etree.SubElement(xml, '{%s}Message' % ns_map['taxii_11'])
            m.text = self.message

        for subscription_instance in self.subscription_instances:
            xml.append(subscription_instance.to_etree())

        return xml

    def to_dict(self):
        d = super(ManageCollectionSubscriptionResponse, self).to_dict()
        d['collection_name'] = self.collection_name
        if self.message is not None:
            d['message'] = self.message
        d['subscription_instances'] = []
        for subscription_instance in self.subscription_instances:
            d['subscription_instances'].append(subscription_instance.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = super(ManageCollectionSubscriptionResponse, self).to_text(line_prepend)
        s += line_prepend + "  Collection Name: %s\n" % self.collection_name
        s += line_prepend + "  Message: %s\n" % self.message
        for si in self.subscription_instances:
            s += si.to_text(line_prepend + STD_INDENT)

        return s

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['collection_name'] = etree_xml.attrib['collection_name']

        kwargs['message'] = get_optional_text(etree_xml, './taxii_11:Message', ns_map)

        kwargs['subscription_instances'] = []
        for si in etree_xml.xpath('./taxii_11:Subscription', namespaces=ns_map):
            kwargs['subscription_instances'].append(SubscriptionInstance.from_etree(si))

        msg = super(ManageCollectionSubscriptionResponse, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['collection_name'] = d['collection_name']

        kwargs['message'] = d.get('message')

        kwargs['subscription_instances'] = []
        for instance in d['subscription_instances']:
            kwargs['subscription_instances'].append(SubscriptionInstance.from_dict(instance))

        msg = super(ManageCollectionSubscriptionResponse, cls).from_dict(d, **kwargs)
        return msg


class SubscriptionInstance(TAXIIBase11):

    """
    The Subscription Instance component of the Manage Collection Subscription
    Response message.

    Args:
        subscription_id (str): the id of the subscription. **Required**
        status (str): One of :py:data:`SS_ACTIVE`, :py:data:`SS_PAUSED`, or
                :py:data:`SS_UNSUBSCRIBED`. **Optional**, defaults to "ACTIVE"
        subscription_parameters (SubscriptionParameters): the parameters
            for this subscription. **Optional** If provided, should match
            the request.
        push_parameters (PushParameters): the push parameters for this
            subscription. **Optional** If provided, should match the request.
        poll_instances (list of PollInstance): The Poll Services that can be
                polled to fulfill this subscription. **Optional**
    """

    def __init__(self, subscription_id, status=SS_ACTIVE,
                 subscription_parameters=None, push_parameters=None,
                 poll_instances=None):
        self.subscription_id = subscription_id
        self.status = status
        self.subscription_parameters = subscription_parameters
        self.push_parameters = push_parameters
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
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        do_check(value, 'status', value_tuple=SS_TYPES, can_be_none=True)
        self._status = value

    @property
    def subscription_parameters(self):
        return self._subscription_parameters

    @subscription_parameters.setter
    def subscription_parameters(self, value):
        do_check(value, 'subscription_parameters', type=SubscriptionParameters, can_be_none=True)
        self._subscription_parameters = value

    @property
    def push_parameters(self):
        return self._push_parameters

    @push_parameters.setter
    def push_parameters(self, value):
        do_check(value, 'push_parameters', type=PushParameters, can_be_none=True)
        self._push_parameters = value

    @property
    def poll_instances(self):
        return self._poll_instances

    @poll_instances.setter
    def poll_instances(self, value):
        do_check(value, 'poll_instances', type=PollInstance)
        self._poll_instances = value

    def to_etree(self):
        si = etree.Element('{%s}Subscription' % ns_map['taxii_11'], nsmap=ns_map)
        if self.status is not None:
            si.attrib['status'] = self.status

        subs_id = etree.SubElement(si, '{%s}Subscription_ID' % ns_map['taxii_11'])
        subs_id.text = self.subscription_id

        if self.subscription_parameters is not None:
            si.append(self.subscription_parameters.to_etree())

        if self.push_parameters is not None:
            si.append(self.push_parameters.to_etree())

        for pi in self.poll_instances:
            si.append(pi.to_etree())

        return si

    def to_dict(self):
        d = {}
        d['status'] = self.status
        d['subscription_id'] = self.subscription_id
        d['subscription_parameters'] = None
        if self.subscription_parameters is not None:
            d['subscription_parameters'] = self.subscription_parameters.to_dict()

        d['push_parameters'] = None
        if self.push_parameters is not None:
            d['push_parameters'] = self.push_parameters.to_dict()

        d['poll_instances'] = []
        for pi in self.poll_instances:
            d['poll_instances'].append(pi.to_dict())

        return d

    def to_text(self, line_prepend=''):
        s = line_prepend + "=== Subscription Instance ===\n"
        s += line_prepend + "  Status: %s\n" % self.status
        s += line_prepend + "  Subscription ID: %s\n" % self.subscription_id
        if self.subscription_parameters:
            s += self.subscription_parameters.to_text(line_prepend + STD_INDENT)
        if self.push_parameters:
            s += self.push_parameters.to_text(line_prepend + STD_INDENT)
        for pi in self.poll_instances:
            s += pi.to_text(line_prepend + STD_INDENT)

        return s

    @staticmethod
    def from_etree(etree_xml):

        status = get_optional(etree_xml, './@status', ns_map)

        subscription_id = get_required(etree_xml, './taxii_11:Subscription_ID', ns_map).text

        subscription_parameters = None
        subscription_parameters_el = get_optional(etree_xml, './taxii_11:Subscription_Parameters', ns_map)
        if subscription_parameters_el is not None:
            subscription_parameters = SubscriptionParameters.from_etree(subscription_parameters_el)

        push_parameters = None
        push_parameters_el = get_optional(etree_xml, './taxii_11:Push_Parameters', ns_map)
        if push_parameters_el is not None:
            push_parameters = PushParameters.from_etree(push_parameters_el)

        poll_instances = []
        for pi in etree_xml.xpath('./taxii_11:Poll_Instance', namespaces=ns_map):
            poll_instances.append(PollInstance.from_etree(pi))

        return SubscriptionInstance(subscription_id, status, subscription_parameters, push_parameters, poll_instances)

    @staticmethod
    def from_dict(d):
        subscription_id = d['subscription_id']
        status = d.get('status')

        subscription_parameters = None
        if d.get('subscription_parameters') is not None:
            subscription_parameters = SubscriptionParameters.from_dict(d['subscription_parameters'])

        push_parameters = None
        if d.get('push_parameters') is not None:
            push_parameters = PushParameters.from_dict(d['push_parameters'])

        poll_instances = []
        if 'poll_instances' in d:
            for pi in d['poll_instances']:
                poll_instances.append(PollInstance.from_dict(pi))

        return SubscriptionInstance(subscription_id, status, subscription_parameters, push_parameters, poll_instances)


class PollInstance(TAXIIBase11):

    """
    The Poll Instance component of the Manage Collection Subscription
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
        self.poll_message_bindings = poll_message_bindings or []

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
        xml = etree.Element('{%s}Poll_Instance' % ns_map['taxii_11'])

        pb = etree.SubElement(xml, '{%s}Protocol_Binding' % ns_map['taxii_11'])
        pb.text = self.poll_protocol

        a = etree.SubElement(xml, '{%s}Address' % ns_map['taxii_11'])
        a.text = self.poll_address

        for binding in self.poll_message_bindings:
            b = etree.SubElement(xml, '{%s}Message_Binding' % ns_map['taxii_11'])
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
        poll_protocol = get_required(etree_xml, './taxii_11:Protocol_Binding', ns_map).text
        address = get_required(etree_xml, './taxii_11:Address', ns_map).text

        poll_message_bindings = []
        for b in etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map):
            poll_message_bindings.append(b.text)

        return PollInstance(poll_protocol, address, poll_message_bindings)

    @staticmethod
    def from_dict(d):
        return PollInstance(**d)


class PollFulfillmentRequest(TAXIIRequestMessage):

    """
    A TAXII Poll Fulfillment Request message.

    Args:
        message_id (str): A value identifying this message. **Required**
        extended_headers (dict): A dictionary of name/value pairs for
            use as Extended Headers. **Optional**
        collection_name (str): the name of the TAXII Data Collection to which the
            action applies. **Required**
        result_id (str): The result id of the requested result. **Required**
        result_part_number (int): The part number being requested. **Required**
    """
    message_type = MSG_POLL_FULFILLMENT_REQUEST

    def __init__(self, message_id, extended_headers=None,
                 collection_name=None, result_id=None, result_part_number=None):
        super(PollFulfillmentRequest, self).__init__(message_id, extended_headers=extended_headers)
        self.collection_name = collection_name
        self.result_id = result_id
        self.result_part_number = result_part_number

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        do_check(value, 'collection_name', regex_tuple=uri_regex)
        self._collection_name = value

    @property
    def result_id(self):
        return self._result_id

    @result_id.setter
    def result_id(self, value):
        do_check(value, 'result_id', regex_tuple=uri_regex)
        self._result_id = value

    @property
    def result_part_number(self):
        return self._result_part_number

    @result_part_number.setter
    def result_part_number(self, value):
        do_check(value, 'result_part_number', type=int)
        self._result_part_number = value

    def to_etree(self):
        xml = super(PollFulfillmentRequest, self).to_etree()
        xml.attrib['collection_name'] = self.collection_name
        xml.attrib['result_id'] = self.result_id
        xml.attrib['result_part_number'] = str(self.result_part_number)
        return xml

    def to_dict(self):
        d = super(PollFulfillmentRequest, self).to_dict()
        d['collection_name'] = self.collection_name
        d['result_id'] = self.result_id
        d['result_part_number'] = self.result_part_number
        return d

    def to_text(self, line_prepend=''):
        s = super(PollFulfillmentRequest, self).to_text(line_prepend)
        s += line_prepend + "  Collection Name: %s\n" % self.collection_name
        s += line_prepend + "  Result ID: %s\n" % self.result_id
        s += line_prepend + "  Result Part Number: %s\n" % self.result_part_number
        return s

    @classmethod
    def from_etree(cls, etree_xml):

        kwargs = {}
        kwargs['collection_name'] = etree_xml.attrib['collection_name']
        kwargs['result_id'] = etree_xml.attrib['result_id']
        kwargs['result_part_number'] = int(etree_xml.attrib['result_part_number'])

        return super(PollFulfillmentRequest, cls).from_etree(etree_xml, **kwargs)

    @classmethod
    def from_dict(cls, d):

        kwargs = {}
        kwargs['collection_name'] = d['collection_name']
        kwargs['result_id'] = d['result_id']
        kwargs['result_part_number'] = int(d['result_part_number'])

        return super(PollFulfillmentRequest, cls).from_dict(d, **kwargs)


########################################################
# EVERYTHING BELOW HERE IS FOR BACKWARDS COMPATIBILITY #
########################################################

# Add top-level classes as nested classes for backwards compatibility
DiscoveryResponse.ServiceInstance = ServiceInstance
CollectionInformationResponse.CollectionInformation = CollectionInformation
CollectionInformation.PushMethod = PushMethod
CollectionInformation.PollingServiceInstance = PollingServiceInstance
CollectionInformation.SubscriptionMethod = SubscriptionMethod
CollectionInformation.ReceivingInboxService = ReceivingInboxService
ManageCollectionSubscriptionResponse.PollInstance = PollInstance
ManageCollectionSubscriptionResponse.SubscriptionInstance = SubscriptionInstance
PollRequest.PollParameters = PollParameters
InboxMessage.SubscriptionInformation = SubscriptionInformation

# Constants not imported in `from constants import *`

MSG_TYPES = MSG_TYPES_11
ST_TYPES = ST_TYPES_11
ACT_TYPES = ACT_TYPES_11
SS_TYPES = SS_TYPES_11
RT_TYPES = RT_TYPES_11
CT_TYPES = CT_TYPES_11
SVC_TYPES = SVC_TYPES_11
SD_TYPES = SD_TYPES_11

from .common import (generate_message_id)
