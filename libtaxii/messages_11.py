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
try:
    import simplejson as json
except ImportError:
    import json
import os
import StringIO

from lxml import etree

import libtaxii.messages_10 as tm10

from .common import (get_xml_parser, parse_datetime_string, set_xml_parser,
        TAXIIBase)
from .validation import do_check, uri_regex, check_timestamp_label


# TAXII 1.0 Message Types

#:Constant identifying a Status Message
MSG_STATUS_MESSAGE = tm10.MSG_STATUS_MESSAGE
#:Constant identifying a Discovery Request Message
MSG_DISCOVERY_REQUEST = tm10.MSG_DISCOVERY_REQUEST
#:Constant identifying a Discovery Response Message
MSG_DISCOVERY_RESPONSE = tm10.MSG_DISCOVERY_RESPONSE
#:Constant identifying a Feed Information Request Message
MSG_FEED_INFORMATION_REQUEST = tm10.MSG_FEED_INFORMATION_REQUEST
#:Constant identifying a Feed Information Response Message
MSG_FEED_INFORMATION_RESPONSE = tm10.MSG_FEED_INFORMATION_RESPONSE
#:Constant identifying a Subscription Management Request Message
MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST = tm10.MSG_MANAGE_FEED_SUBSCRIPTION_REQUEST
#:Constant identifying a Subscription Management Response Message
MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE = tm10.MSG_MANAGE_FEED_SUBSCRIPTION_RESPONSE
#:Constant identifying a Poll Request Message
MSG_POLL_REQUEST = tm10.MSG_POLL_REQUEST
#:Constant identifying a Poll Response Message
MSG_POLL_RESPONSE = tm10.MSG_POLL_RESPONSE
#:Constant identifying a Inbox Message
MSG_INBOX_MESSAGE = tm10.MSG_INBOX_MESSAGE

# New Message Types in TAXII 1.1

#:Constant identifying a Status Message
MSG_POLL_FULFILLMENT_REQUEST = 'Poll_Fulfillment'
#:Constant identifying a Collection Information Request
MSG_COLLECTION_INFORMATION_REQUEST = 'Collection_Information_Request'
#:Constant identifying a Collection Information Response
MSG_COLLECTION_INFORMATION_RESPONSE = 'Collection_Information_Response'
#:Constant identifying a Subscription Request
MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST = 'Subscription_Management_Request'
#:Constant identifying a Subscription Response
MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE = 'Subscription_Management_Response'

#: Tuple of all TAXII 1.1 Message Types
MSG_TYPES = (MSG_STATUS_MESSAGE, MSG_DISCOVERY_REQUEST, MSG_DISCOVERY_RESPONSE,
        MSG_COLLECTION_INFORMATION_REQUEST, MSG_COLLECTION_INFORMATION_RESPONSE,
        MSG_MANAGE_COLLECTION_SUBSCRIPTION_REQUEST,
        MSG_MANAGE_COLLECTION_SUBSCRIPTION_RESPONSE, MSG_POLL_REQUEST,
        MSG_POLL_RESPONSE, MSG_INBOX_MESSAGE, MSG_POLL_FULFILLMENT_REQUEST)


# TAXII 1.0 Status Types

#: Constant identifying a Status Type of Bad Message
ST_BAD_MESSAGE = tm10.ST_BAD_MESSAGE
#: Constant identifying a Status Type of Denied
ST_DENIED = tm10.ST_DENIED
#: Constant identifying a Status Type of Failure
ST_FAILURE = tm10.ST_FAILURE
#: Constant identifying a Status Type of Not Found
ST_NOT_FOUND = tm10.ST_NOT_FOUND
#: Constant identifying a Status Type of Polling Unsupported
ST_POLLING_UNSUPPORTED = tm10.ST_POLLING_UNSUPPORTED
#: Constant identifying a Status Type of Retry
ST_RETRY = tm10.ST_RETRY
#: Constant identifying a Status Type of Success
ST_SUCCESS = tm10.ST_SUCCESS
#: Constant identifying a Status Type of Unauthorized
ST_UNAUTHORIZED = tm10.ST_UNAUTHORIZED
#: Constant identifying a Status Type of Unsupported Message Binding
ST_UNSUPPORTED_MESSAGE_BINDING = tm10.ST_UNSUPPORTED_MESSAGE_BINDING
#: Constant identifying a Status Type of Unsupported Content Binding
ST_UNSUPPORTED_CONTENT_BINDING = tm10.ST_UNSUPPORTED_CONTENT_BINDING
#: Constant identifying a Status Type of Unsupported Protocol Binding
ST_UNSUPPORTED_PROTOCOL = tm10.ST_UNSUPPORTED_PROTOCOL

# New Status Types in TAXII 1.1

#: Constant identifying a Status Type of Asynchronous Poll Error
ST_ASYNCHRONOUS_POLL_ERROR = 'ASYNCHRONOUS_POLL_ERROR'
#: Constant identifying a Status Type of Destination Collection Error
ST_DESTINATION_COLLECTION_ERROR = 'DESTINATION_COLLECTION_ERROR'
#: Constant identifying a Status Type of Invalid Response Part
ST_INVALID_RESPONSE_PART = 'INVALID_RESPONSE_PART'
#: Constant identifying a Status Type of Network Error
ST_NETWORK_ERROR = 'NETWORK_ERROR'
#: Constant identifying a Status Type of Pending
ST_PENDING = 'PENDING'
#: Constant identifying a Status Type of Unsupported Query Format
ST_UNSUPPORTED_QUERY = 'UNSUPPORTED_QUERY'

#: Tuple of all TAXII 1.1 Status types
ST_TYPES = (ST_ASYNCHRONOUS_POLL_ERROR, ST_BAD_MESSAGE, ST_DENIED,
        ST_DESTINATION_COLLECTION_ERROR, ST_FAILURE, ST_INVALID_RESPONSE_PART,
        ST_NETWORK_ERROR, ST_NOT_FOUND, ST_PENDING, ST_POLLING_UNSUPPORTED,
        ST_RETRY, ST_SUCCESS, ST_UNAUTHORIZED, ST_UNSUPPORTED_MESSAGE_BINDING,
        ST_UNSUPPORTED_CONTENT_BINDING, ST_UNSUPPORTED_PROTOCOL,
        ST_UNSUPPORTED_QUERY)


# TAXII 1.0 Action Types

#: Constant identifying an Action of Subscribe
ACT_SUBSCRIBE = tm10.ACT_SUBSCRIBE
#: Constant identifying an Action of Unsubscribe
ACT_UNSUBSCRIBE = tm10.ACT_UNSUBSCRIBE
#: Constant identifying an Action of Status
ACT_STATUS = tm10.ACT_STATUS

# New Action Types in TAXII 1.1

#: Constant identifying an Action of Pause
ACT_PAUSE = 'PAUSE'
#: Constant identifying an Action of Resume
ACT_RESUME = 'RESUME'

#: Tuple of all TAXII 1.1 Action types
ACT_TYPES = (ACT_SUBSCRIBE, ACT_PAUSE, ACT_RESUME, ACT_UNSUBSCRIBE, ACT_STATUS)


# TAXII 1.1 Subscription Statuses

#: Subscription Status of Active
SS_ACTIVE = 'ACTIVE'
#: Subscription Status of Paused
SS_PAUSED = 'PAUSED'
#: Subscription Status of Unsubscribed
SS_UNSUBSCRIBED = 'UNSUBSCRIBED'

#: Tuple of all TAXII 1.1 Subscription Statues
SS_TYPES = (SS_ACTIVE, SS_PAUSED, SS_UNSUBSCRIBED)


# TAXII 1.1 Response Types

#: Constant identifying a response type of Full
RT_FULL = 'FULL'
#: Constant identifying a response type of Count only
RT_COUNT_ONLY = 'COUNT_ONLY'

#: Tuple of all TAXII 1.1 Response Types
RT_TYPES = (RT_FULL, RT_COUNT_ONLY)


# TAXII 1.1 Response Types

#: Constant identifying a collection type of Data Feed
CT_DATA_FEED = 'DATA_FEED'
#: Constant identifying a collection type of Data Set
CT_DATA_SET = 'DATA_SET'

#: Tuple of all TAXII 1.1 Collection Types
CT_TYPES = (CT_DATA_FEED, CT_DATA_SET)


# TAXII 1.0 Service Types

#: Constant identifying a Service Type of Inbox
SVC_INBOX = tm10.SVC_INBOX
#: Constant identifying a Service Type of Poll
SVC_POLL = tm10.SVC_POLL
#: Constant identifying a Service Type of Discovery
SVC_DISCOVERY = tm10.SVC_DISCOVERY

# Renamed Status Types in TAXII 1.1
#: Constant identifying a Service Type of Collection Management.
#: "Feed Management" was renamed to "Collection Management" in TAXII 1.1.
SVC_COLLECTION_MANAGEMENT = 'COLLECTION_MANAGEMENT'

#: Tuple of all TAXII 1.1 Service Types
SVC_TYPES = (SVC_INBOX, SVC_POLL, SVC_COLLECTION_MANAGEMENT, SVC_DISCOVERY)


ns_map = {
            'taxii_11': 'http://taxii.mitre.org/messages/taxii_xml_binding-1.1',
         }


# Import helper methods from libtaxii.messages_10 that are still applicable
from libtaxii.messages_10 import (generate_message_id)


def validate_xml(xml_string):
    """Validate XML with the TAXII XML Schema 1.1.

    Args:
        xml_string (str): The XML to validate.

    Example:
        .. code-block:: python

            is_valid = tm11.validate_xml(message.to_xml())
    """
    if isinstance(xml_string, basestring):
        f = StringIO.StringIO(xml_string)
    else:
        f = xml_string

    etree_xml = etree.parse(f, get_xml_parser())
    package_dir, package_filename = os.path.split(__file__)
    schema_file = os.path.join(package_dir, "xsd", "TAXII_XMLMessageBinding_Schema_11.xsd")
    taxii_schema_doc = etree.parse(schema_file, get_xml_parser())
    xml_schema = etree.XMLSchema(taxii_schema_doc)
    valid = xml_schema.validate(etree_xml)
    # TODO: Additionally, validate the Query stuff
    if not valid:
        return xml_schema.error_log.last_error
    return valid


def get_message_from_xml(xml_string):
    """Create a TAXIIMessage object from an XML string.

    This function automatically detects which type of Message should be created
    based on the XML.

    Args:
        xml_string (str): The XML to parse into a TAXII message.

    Example:
        .. code-block:: python

            message_xml = message.to_xml()
            new_message = tm11.get_message_from_xml(message_xml)
    """
    if isinstance(xml_string, basestring):
        f = StringIO.StringIO(xml_string)
    else:
        f = xml_string

    etree_xml = etree.parse(f, get_xml_parser()).getroot()
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


def get_message_from_json(json_string):
    """Create a TAXIIMessage object from a JSON string.

    This function automatically detects which type of Message should be created
    based on the JSON.

    Args:
        json_string (str): The JSON to parse into a TAXII message.
    """
    return get_message_from_dict(json.loads(json_string))


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
    elif isinstance(binding, basestring):  # Convert it to a ContentBinding
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
        # name (string) - The name of the element
        # namespace (string) - The namespace of the element
        # value (string) - The text value of the element
        # attrs (dict) - A dictionary of attributes
        # parent (Element) - The parent element
    # """
    # if value is None and attrs is None:
        # return

    # if parent is None:
        # elt = etree.Element('{%s}%s' % (namespace, name), nsmap=ns_map)
    # else:
        # elt = etree.SubElement(parent, '{%s}%s' % (namespace, name), nsmap=ns_map)

    # if value is not None:
        # elt.text = value

    # if attrs is not None:
        # for k, v in attrs.items():
            # elt.attrib[k] = v

    # return elt


class SupportedQuery(TAXIIBase):
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

    @staticmethod
    def from_etree(etree_xml):
        format_id = etree_xml.xpath('./@format_id', ns_map=nsmap)[0]
        return SupportedQuery(format_id)

    @staticmethod
    def from_dict(d):
        return SupportedQuery(**d)


class Query(TAXIIBase):
    """
    This class contains an instance of a query. It
    is expected that, generally, messages_11.Query 
    subclasses will be used in place of this class
    to represent a query
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

    @classmethod
    def from_etree(cls, etree_xml, kwargs):
        format_id = etree_xml.xpath('./@format_id', ns_map=nsmap)[0]
        return cls(format_id, **kwargs)

    @classmethod
    def from_dict(cls, d, kwargs):
        return cls(d, **kwargs)


# A value can be one of:
# - a dictionary, where each key is a content_binding_id and each value is a list of subtypes
#   (This is the default representation)
# - a "content_binding_id[>subtype]" structure
# - a list of "content_binding_id[>subtype]" structures


class ContentBinding(TAXIIBase):
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
            s = s+ '>' + ','.join(self.subtype_ids)

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


class RecordCount(TAXIIBase):
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

    @staticmethod
    def from_etree(etree_xml):
        record_count = int(etree_xml.text)
        partial_count = etree_xml.attrib.get('partial_count', 'false') == 'true'

        return RecordCount(record_count, partial_count)

    @staticmethod
    def from_dict(d):
        return RecordCount(**d)


class _GenericParameters(TAXIIBase):
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

    @classmethod
    def from_etree(cls, etree_xml, **kwargs):

        response_type = RT_FULL
        response_type_set = etree_xml.xpath('./taxii_11:Response_Type', namespaces=ns_map)
        if len(response_type_set) > 0:
            response_type = response_type_set[0].text

        content_bindings = []
        content_binding_set = etree_xml.xpath('./taxii_11:Content_Binding', namespaces=ns_map)
        for binding in content_binding_set:
            content_bindings.append(ContentBinding.from_etree(binding))

        query = None
        query_set = etree_xml.xpath('./taxii_11:Query', namespaces=ns_map)
        if len(query_set) > 0:
            format_id = query_set[0].attrib['format_id']
            query = get_deserializer(format_id, 'query').from_etree(query_set[0])

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


class ContentBlock(TAXIIBase):
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
        check_timestamp_label(value, 'timestamp_label', can_be_none=True)
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
                xml = etree.parse(content, get_xml_parser()).getroot()
                return xml, True
            except etree.XMLSyntaxError:  # Content is not well-formed XML; just treat as a string
                return content.read(), False
        else:  # The Content is not file-like
            try:  # Attempt to parse string as XML
                sio_content = StringIO.StringIO(content)
                xml = etree.parse(sio_content, get_xml_parser()).getroot()
                return xml, True
            except etree.XMLSyntaxError:  # Content is not well-formed XML; just treat as a string
                if isinstance(content, basestring):  # It's a string of some kind, unicode or otherwise
                    return content, False
                else:  # It's some other datatype that needs casting to string
                    return str(content), False

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        do_check(value, 'message', type=basestring, can_be_none=True)
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

        if self.padding is not None:
            block['padding'] = self.padding

        return block

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}
        cb = etree_xml.xpath('./taxii_11:Content_Binding', namespaces=ns_map)[0]
        kwargs['content_binding'] = ContentBinding.from_etree(cb)
        padding_set = etree_xml.xpath('./taxii_11:Padding', namespaces=ns_map)
        if len(padding_set) > 0:
            kwargs['padding'] = padding_set[0].text

        ts_set = etree_xml.xpath('./taxii_11:Timestamp_Label', namespaces=ns_map)
        if len(ts_set) > 0:
            ts_string = ts_set[0].text
            kwargs['timestamp_label'] = parse_datetime_string(ts_string)

        content = etree_xml.xpath('./taxii_11:Content', namespaces=ns_map)[0]
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

        is_xml = d.get('content_is_xml', False)
        if is_xml:
            kwargs['content'] = etree.parse(StringIO.StringIO(d['content']), get_xml_parser()).getroot()
        else:
            kwargs['content'] = d['content']

        cb = ContentBlock(**kwargs)
        return cb

    @classmethod
    def from_json(cls, json_string):
        return cls.from_dict(json.loads(json_string))


class PushParameters(TAXIIBase):
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

    @classmethod
    def from_etree(cls, etree_xml):
        inbox_protocol = None
        inbox_protocol_set = etree_xml.xpath('./taxii_11:Protocol_Binding', namespaces=ns_map)
        if len(inbox_protocol_set) > 0:
            inbox_protocol = inbox_protocol_set[0].text

        inbox_address = None
        inbox_address_set = etree_xml.xpath('./taxii_11:Address', namespaces=ns_map)
        if len(inbox_address_set) > 0:
            inbox_address = inbox_address_set[0].text

        delivery_message_binding = None
        delivery_message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        if len(delivery_message_binding_set) > 0:
            delivery_message_binding = delivery_message_binding_set[0].text

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


class TAXIIMessage(TAXIIBase):
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
        do_check(value.keys(), 'extended_headers.keys()', regex_tuple=uri_regex)
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

            for name, value in self.extended_headers.items():
                h = etree.SubElement(eh, '{%s}Extended_Header' % ns_map['taxii_11'], nsmap=ns_map)
                h.attrib['name'] = name
                h.text = value
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
        d['extended_headers'] = self.extended_headers

        return d

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_etree(cls, src_etree, **kwargs):
        """Pulls properties of a TAXII Message from an etree.

        Message-specific constructs must be pulled by each Message class. In
        general, when converting from etree, subclasses should call this method
        first, then parse their specific XML constructs.
        """

        # Get the message type
        message_type = src_etree.tag[55:]
        if message_type != cls.message_type:
            raise ValueError('%s != %s' % (message_type, cls.message_type))

        # Get the message ID
        message_id = src_etree.xpath('/taxii_11:*/@message_id', namespaces=ns_map)[0]

        # Get in response to, if present
        in_response_to = None
        in_response_tos = src_etree.xpath('/taxii_11:*/@in_response_to', namespaces=ns_map)
        if len(in_response_tos) > 0:
            in_response_to = in_response_tos[0]

        # Get the Extended headers
        extended_header_list = src_etree.xpath('/taxii_11:*/taxii_11:Extended_Headers/taxii_11:Extended_Header', namespaces=ns_map)
        extended_headers = {}
        for header in extended_header_list:
            eh_name = header.xpath('./@name')[0]
            eh_value = header.text
            extended_headers[eh_name] = eh_value

        return cls(message_id,
                   in_response_to,
                   extended_headers=extended_headers,
                   **kwargs)

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
        extended_headers = d['extended_headers']
        in_response_to = d.get('in_response_to')

        return cls(message_id,
                   in_response_to,
                   extended_headers=extended_headers,
                   **kwargs)

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


class ServiceInstance(TAXIIBase):
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

    @property
    def service_type(self):
        return self._service_type

    @service_type.setter
    def service_type(self, value):
        do_check(value, 'service_type', value_tuple=SVC_TYPES)
        self._service_type = value

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

    @staticmethod
    def from_etree(etree_xml):  # Expects a taxii_11:Service_Instance element
        service_type = etree_xml.attrib['service_type']
        services_version = etree_xml.attrib['service_version']
        available = None
        if 'available' in etree_xml.attrib:
            tmp_available = etree_xml.attrib['available']
            available = tmp_available == 'true'

        protocol_binding = etree_xml.xpath('./taxii_11:Protocol_Binding', namespaces=ns_map)[0].text
        service_address = etree_xml.xpath('./taxii_11:Address', namespaces=ns_map)[0].text

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

        message = None
        message_set = etree_xml.xpath('./taxii_11:Message', namespaces=ns_map)
        if len(message_set) > 0:
            message = message_set[0].text

        return ServiceInstance(service_type, services_version, protocol_binding, service_address, message_bindings, inbox_service_accepted_content, available, message, supported_query)

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

        return ServiceInstance(service_type, services_version, protocol_binding, service_address, message_bindings, inbox_service_accepted_content, available, message, supported_query)


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


class CollectionInformation(TAXIIBase):
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

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}
        kwargs['collection_name'] = etree_xml.attrib['collection_name']
        kwargs['collection_type'] = etree_xml.attrib.get('collection_type', None)

        kwargs['available'] = None
        if 'available' in etree_xml.attrib:
            tmp = etree_xml.attrib['available']
            kwargs['available'] = tmp.lower() == 'true'

        kwargs['collection_description'] = etree_xml.xpath('./taxii_11:Description', namespaces=ns_map)[0].text

        collection_volume_set = etree_xml.xpath('./taxii_11:Collection_Volume', namespaces=ns_map)
        if len(collection_volume_set) > 0:
            kwargs['collection_volume'] = int(collection_volume_set[0].text)

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
        kwargs['collection_volume'] = d.get('collection_volume', None)

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

        kwargs['receiving_inbox_services'] = []
        receiving_inbox_services_set = d.get('receiving_inbox_services', [])
        for receiving_inbox_service in receiving_inbox_services_set:
            kwargs['receiving_inbox_services'].append(ReceivingInboxService.from_dict(receiving_inbox_service))

        return CollectionInformation(**kwargs)


class PushMethod(TAXIIBase):
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

    @staticmethod
    def from_etree(etree_xml):
        kwargs = {}
        kwargs['push_protocol'] = etree_xml.xpath('./taxii_11:Protocol_Binding', namespaces=ns_map)[0].text
        kwargs['push_message_bindings'] = []
        message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        for message_binding in message_binding_set:
            kwargs['push_message_bindings'].append(message_binding.text)
        return PushMethod(**kwargs)

    @staticmethod
    def from_dict(d):
        return PushMethod(**d)


class PollingServiceInstance(TAXIIBase):
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

    @classmethod
    def from_etree(cls, etree_xml):
        protocol = etree_xml.xpath('./taxii_11:Protocol_Binding', namespaces=ns_map)[0].text
        addr = etree_xml.xpath('./taxii_11:Address', namespaces=ns_map)[0].text
        bindings = []
        message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        for message_binding in message_binding_set:
            bindings.append(message_binding.text)
        return cls(protocol, addr, bindings)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class SubscriptionMethod(TAXIIBase):
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

    @classmethod
    def from_etree(cls, etree_xml):
        protocol = etree_xml.xpath('./taxii_11:Protocol_Binding', namespaces=ns_map)[0].text
        addr = etree_xml.xpath('./taxii_11:Address', namespaces=ns_map)[0].text
        bindings = []
        message_binding_set = etree_xml.xpath('./taxii_11:Message_Binding', namespaces=ns_map)
        for message_binding in message_binding_set:
            bindings.append(message_binding.text)
        return cls(protocol, addr, bindings)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class ReceivingInboxService(TAXIIBase):
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
        do_check(value, 'inbox_protocol', type=basestring, regex_tuple=uri_regex)
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

    @staticmethod
    def from_etree(etree_xml):
        proto = etree_xml.xpath('./taxii_11:Protocol_Binding', namespaces=ns_map)[0].text
        addr = etree_xml.xpath('./taxii_11:Address', namespaces=ns_map)[0].text

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

    def __init__(self, message_id, in_response_to=None, extended_headers=None,
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
        check_timestamp_label(value, 'exclusive_begin_timestamp_label', can_be_none=True)
        self._exclusive_begin_timestamp_label = value

    @property
    def inclusive_end_timestamp_label(self):
        return self._inclusive_end_timestamp_label

    @inclusive_end_timestamp_label.setter
    def inclusive_end_timestamp_label(self, value):
        check_timestamp_label(value, 'inclusive_end_timestamp_label', can_be_none=True)
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

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['collection_name'] = etree_xml.xpath('./@collection_name', namespaces=ns_map)[0]

        kwargs['exclusive_begin_timestamp_label'] = None
        begin_ts_set = etree_xml.xpath('./taxii_11:Exclusive_Begin_Timestamp', namespaces=ns_map)
        if len(begin_ts_set) > 0:
            kwargs['exclusive_begin_timestamp_label'] = parse_datetime_string(begin_ts_set[0].text)

        kwargs['inclusive_end_timestamp_label'] = None
        end_ts_set = etree_xml.xpath('./taxii_11:Inclusive_End_Timestamp', namespaces=ns_map)
        if len(end_ts_set) > 0:
            kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(end_ts_set[0].text)

        kwargs['poll_parameters'] = None
        poll_parameter_set = etree_xml.xpath('./taxii_11:Poll_Parameters', namespaces=ns_map)
        if len(poll_parameter_set) > 0:
            kwargs['poll_parameters'] = PollParameters.from_etree(poll_parameter_set[0])

        kwargs['subscription_id'] = None
        subscription_id_set = etree_xml.xpath('./taxii_11:Subscription_ID', namespaces=ns_map)
        if len(subscription_id_set) > 0:
            kwargs['subscription_id'] = subscription_id_set[0].text

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

    @classmethod
    def from_etree(cls, etree_xml):
        poll_parameters = super(PollParameters, cls).from_etree(etree_xml)
        kwargs = {}

        allow_asynch_set = etree_xml.xpath('./@allow_asynch')
        if len(allow_asynch_set) > 0:
            poll_parameters.allow_asynch = allow_asynch_set[0] == 'true'

        delivery_parameters_set = etree_xml.xpath('./taxii_11:Delivery_Parameters', namespaces=ns_map)
        if len(delivery_parameters_set) > 0:
            poll_parameters.delivery_parameters = DeliveryParameters.from_etree(delivery_parameters_set[0])

        return poll_parameters

    @classmethod
    def from_dict(cls, d):
        poll_parameters = super(PollParameters, cls).from_dict(d)
        kwargs = {}

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
        check_timestamp_label(value, 'inclusive_end_timestamp_label', can_be_none=True)
        self._inclusive_end_timestamp_label = value

    @property
    def inclusive_begin_timestamp_label(self):
        return self._inclusive_begin_timestamp_label

    @inclusive_begin_timestamp_label.setter
    def inclusive_begin_timestamp_label(self, value):
        check_timestamp_label(value, 'inclusive_begin_timestamp_label', can_be_none=True)
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

        if self.subscription_id is not None:
            si = etree.SubElement(xml, '{%s}Subscription_ID' % ns_map['taxii_11'])
            si.text = self.subscription_id

        if self.exclusive_begin_timestamp_label is not None:
            ibt = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii_11'])
            ibt.text = self.exclusive_begin_timestamp_label.isoformat()

        if self.inclusive_end_timestamp_label is not None:
            iet = etree.SubElement(xml, '{%s}Inclusive_End_Timestamp' % ns_map['taxii_11'])
            iet.text = self.inclusive_end_timestamp_label.isoformat()

        if self.record_count is not None:
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

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}

        kwargs['collection_name'] = etree_xml.xpath('./@collection_name', namespaces=ns_map)[0]
        kwargs['more'] = etree_xml.attrib.get('more', 'false') == 'true'
        kwargs['subscription_id'] = None
        kwargs['result_id'] = etree_xml.attrib.get('result_id')
        subs_ids = etree_xml.xpath('./taxii_11:Subscription_ID', namespaces=ns_map)
        if len(subs_ids) > 0:
            kwargs['subscription_id'] = subs_ids[0].text

        kwargs['message'] = None
        messages = etree_xml.xpath('./taxii_11:Message', namespaces=ns_map)
        if len(messages) > 0:
            kwargs['message'] = messages[0].text

        kwargs['exclusive_begin_timestamp_label'] = None
        ebts = etree_xml.xpath('./taxii_11:Exclusive_Begin_Timestamp', namespaces=ns_map)
        if len(ebts) > 0:
            kwargs['exclusive_begin_timestamp_label'] = parse_datetime_string(ebts[0].text)

        kwargs['inclusive_end_timestamp_label'] = None
        iets = etree_xml.xpath('./taxii_11:Inclusive_End_Timestamp', namespaces=ns_map)
        if len(iets) > 0:
            kwargs['inclusive_end_timestamp_label'] = parse_datetime_string(iets[0].text)

        kwargs['content_blocks'] = []
        blocks = etree_xml.xpath('./taxii_11:Content_Block', namespaces=ns_map)
        for block in blocks:
            kwargs['content_blocks'].append(ContentBlock.from_etree(block))

        kwargs['record_count'] = None
        record_counts = etree_xml.xpath('./taxii_11:Record_Count', namespaces=ns_map)
        if len(record_counts) > 0:
            kwargs['record_count'] = RecordCount.from_etree(record_counts[0])

        msg = super(PollResponse, cls).from_etree(etree_xml, **kwargs)
        return msg

    @classmethod
    def from_dict(cls, d):
        kwargs = {}
        kwargs['collection_name'] = d['collection_name']
        kwargs['result_id'] = d.get('result_id')

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
_DCE_AcceptableDestination = _StatusDetail('ACCEPTABLE_DESTINATION', False, str, True)
_IRP_MaxPartNumber =         _StatusDetail('MAX_PART_NUMBER',        True,  int,        False)
_NF_Item =                   _StatusDetail('ITEM',                   False, str, False)
_P_EstimatedWait =           _StatusDetail('ESTIMATED_WAIT',         True,  int, False)
_P_ResultId =                _StatusDetail('RESULT_ID',              True,  str, False)
_P_WillPush =                _StatusDetail('WILL_PUSH',              True,  bool, False)
_R_EstimatedWait =           _StatusDetail('ESTIMATED_WAIT',         False, int, False)
_UM_SupportedBinding =       _StatusDetail('SUPPORTED_BINDING',      False, str, True)
_UC_SupportedContent =       _StatusDetail('SUPPORTED_CONTENT',      False, ContentBinding, True)
_UP_SupportedProtocol =      _StatusDetail('SUPPORTED_PROTOCOL',     False, str, True)
_UQ_SupportedQuery =         _StatusDetail('SUPPORTED_QUERY',        False, str, True)


status_details = {
    ST_ASYNCHRONOUS_POLL_ERROR: {},
    ST_BAD_MESSAGE: {},
    ST_DENIED: {},
    ST_DESTINATION_COLLECTION_ERROR: {'ACCEPTABLE_DESTINATION': _DCE_AcceptableDestination},
    ST_FAILURE: {},
    ST_INVALID_RESPONSE_PART: {'MAX_PART_NUMBER': _IRP_MaxPartNumber},
    ST_NETWORK_ERROR: {},
    ST_NOT_FOUND: {'ITEM': _NF_Item},
    ST_PENDING: {'ESTIMATED_WAIT': _P_EstimatedWait,
                 'RESULT_ID': _P_ResultId,
                 'WILL_PUSH': _P_WillPush},
    ST_POLLING_UNSUPPORTED: {},
    ST_RETRY: {'ESTIMATED_WAIT': _R_EstimatedWait},
    ST_SUCCESS: {},
    ST_UNAUTHORIZED: {},
    ST_UNSUPPORTED_MESSAGE_BINDING: {'SUPPORTED_BINDING': _UM_SupportedBinding},
    ST_UNSUPPORTED_CONTENT_BINDING: {'SUPPORTED_CONTENT': _UC_SupportedContent},
    ST_UNSUPPORTED_PROTOCOL: {'SUPPORTED_PROTOCOL': _UP_SupportedProtocol},
    ST_UNSUPPORTED_QUERY: {'SUPPORTED_QUERY': _UQ_SupportedQuery}
}


class StatusMessage(TAXIIMessage):
    """
    A TAXII Status message.

    Args:
        message_id (str): A value identifying this message. **Required**
        in_response_to (str): Contains the Message ID of the message to
            which this is a response. **Optional**
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
        do_check(value.keys(), 'status_detail.keys()', regex_tuple=uri_regex)
        self._status_detail = value

    def to_etree(self):
        xml = super(StatusMessage, self).to_etree()
        xml.attrib['status_type'] = self.status_type

        if len(self.status_detail) > 0:
            sd = etree.SubElement(xml, '{%s}Status_Detail' % ns_map['taxii_11'])
            for k, v in self.status_detail.iteritems():
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
            d['message'] = self.message
        return d

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
        destination_collection_name (list of str): Each string indicates a
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


class SubscriptionInformation(TAXIIBase):
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
        check_timestamp_label(value, 'exclusive_begin_timestamp_label', can_be_none=True)
        self._exclusive_begin_timestamp_label = value

    @property
    def inclusive_end_timestamp_label(self):
        return self._inclusive_end_timestamp_label

    @inclusive_end_timestamp_label.setter
    def inclusive_end_timestamp_label(self, value):
        check_timestamp_label(value, 'inclusive_end_timestamp_label', can_be_none=True)
        self._inclusive_end_timestamp_label = value

    def to_etree(self):
        xml = etree.Element('{%s}Source_Subscription' % ns_map['taxii_11'])
        xml.attrib['collection_name'] = self.collection_name
        si = etree.SubElement(xml, '{%s}Subscription_ID' % ns_map['taxii_11'])
        si.text = self.subscription_id

        if self.exclusive_begin_timestamp_label is not None:
            ebtl = etree.SubElement(xml, '{%s}Exclusive_Begin_Timestamp' % ns_map['taxii_11'])
            ebtl.text = self.exclusive_begin_timestamp_label.isoformat()

        if self.inclusive_end_timestamp_label is not None:
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

    @staticmethod
    def from_etree(etree_xml):
        collection_name = etree_xml.attrib['collection_name']
        subscription_id = etree_xml.xpath('./taxii_11:Subscription_ID', namespaces=ns_map)[0].text

        begin_ts = etree_xml.xpath('./taxii_11:Exclusive_Begin_Timestamp', namespaces=ns_map)
        if begin_ts:
            ebtl = parse_datetime_string(begin_ts[0].text)
        else:
            ebtl = None

        end_ts = etree_xml.xpath('./taxii_11:Inclusive_End_Timestamp', namespaces=ns_map)
        if end_ts:
            ietl = parse_datetime_string(end_ts[0].text)
        else:
            ietl = None

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

    def __init__(self, message_id, in_response_to=None, extended_headers=None,
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

        if self.action == ACT_SUBSCRIBE and self.push_parameters is not None:
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

        if self.action == ACT_SUBSCRIBE and self.push_parameters is not None:
            d['push_parameters'] = self.push_parameters.to_dict()

        return d

    @classmethod
    def from_etree(cls, etree_xml):

        kwargs = {}
        kwargs['collection_name'] = etree_xml.xpath('./@collection_name', namespaces=ns_map)[0]
        kwargs['action'] = etree_xml.xpath('./@action', namespaces=ns_map)[0]

        kwargs['subscription_id'] = None
        subscription_id_set = etree_xml.xpath('./taxii_11:Subscription_ID', namespaces=ns_map)
        if len(subscription_id_set) > 0:
            kwargs['subscription_id'] = subscription_id_set[0].text

        kwargs['subscription_parameters'] = None
        subscription_parameters_set = etree_xml.xpath('./taxii_11:Subscription_Parameters', namespaces=ns_map)
        if len(subscription_parameters_set) > 0:
            kwargs['subscription_parameters'] = SubscriptionParameters.from_etree(subscription_parameters_set[0])

        kwargs['push_parameters'] = None
        push_parameters_set = etree_xml.xpath('./taxii_11:Push_Parameters', namespaces=ns_map)
        if len(push_parameters_set) > 0:
            kwargs['push_parameters'] = PushParameters.from_etree(push_parameters_set[0])

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

    @classmethod
    def from_etree(cls, etree_xml):
        kwargs = {}
        kwargs['collection_name'] = etree_xml.attrib['collection_name']

        message_set = etree_xml.xpath('./taxii_11:Message', namespaces=ns_map)
        if len(message_set) > 0:
            kwargs['message'] = message_set[0].text

        subscription_instance_set = etree_xml.xpath('./taxii_11:Subscription', namespaces=ns_map)

        kwargs['subscription_instances'] = []
        for si in subscription_instance_set:
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


class SubscriptionInstance(TAXIIBase):
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

    @staticmethod
    def from_etree(etree_xml):

        status = None
        status_set = etree_xml.xpath('./@status')
        if len(status_set) > 0:
            status = status_set[0]

        subscription_id = etree_xml.xpath('./taxii_11:Subscription_ID', namespaces=ns_map)[0].text

        subscription_parameters = None
        subscription_parameters_set = etree_xml.xpath('./taxii_11:Subscription_Parameters', namespaces=ns_map)
        if len(subscription_parameters_set) > 0:
            subscription_parameters = SubscriptionParameters.from_etree(subscription_parameters_set[0])

        push_parameters = None
        push_parameters_set = etree_xml.xpath('./taxii_11:Push_Parameters', namespaces=ns_map)
        if len(push_parameters_set) > 0:
            push_parameters = PushParameters.from_etree(push_parameters_set[0])

        poll_instances = []
        poll_instance_set = etree_xml.xpath('./taxii_11:Poll_Instance', namespaces=ns_map)
        for pi in poll_instance_set:
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


class PollInstance(TAXIIBase):
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

    @staticmethod
    def from_etree(etree_xml):
        poll_protocol = etree_xml.xpath('./taxii_11:Protocol_Binding', namespaces=ns_map)[0].text
        address = etree_xml.xpath('./taxii_11:Address', namespaces=ns_map)[0].text
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

    def __init__(self, message_id, in_response_to=None, extended_headers=None,
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
